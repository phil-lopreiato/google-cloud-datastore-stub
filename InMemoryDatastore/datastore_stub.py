import grpc
import google.cloud.datastore.helpers as ds_helpers
from google.cloud import ndb
from google.cloud.datastore_v1 import types
from google.cloud.datastore_v1.proto import datastore_pb2_grpc
from typing import Dict, List, Optional, NamedTuple

from .futures import InstantFuture


class _StoredObject(NamedTuple):
    version: int
    entity: types.Entity


class _RequestWrapper(grpc.UnaryUnaryMultiCallable):
    def __init__(self, func):
        self.func = func

    def __call__(self, request, *args, **kwargs):
        return self.func(request, *args, **kwargs)

    def with_call(self, request, *args, **kwargs):
        return self(request, *args, **kwargs)

    def future(self, request, *args, **kwargs):
        resp = self(request, *args, **kwargs)
        return InstantFuture(resp)


class LocalDatastoreStub(datastore_pb2_grpc.DatastoreStub):

    _OPERATOR_TO_CMP_METHOD_NAME = {
        types.PropertyFilter.Operator.LESS_THAN: "__lt__",
        types.PropertyFilter.Operator.LESS_THAN_OR_EQUAL: "__le__",
        types.PropertyFilter.Operator.GREATER_THAN: "__gt__",
        types.PropertyFilter.Operator.GREATER_THAN_OR_EQUAL: "__ge__",
        types.PropertyFilter.Operator.EQUAL: "__eq__",
        # TODO missing HAS_ANCESTOR
    }

    seqid: int
    store: Dict[str, _StoredObject]

    Lookup: _RequestWrapper
    Commit: _RequestWrapper
    RunQuery: _RequestWrapper
    # BeginTransaction: _RequestWrapper
    # Rollback: _RequestWrapper
    # AllocateIds: _RequestWrapper
    # ReserveIds: _RequestWrapper

    def __init__(self) -> None:
        # don't call super, we want to do other stuff
        # also we can ignore the channel, since we're doing it all in memory
        self.seqid = 0
        self.store = {}

        self.Lookup = _RequestWrapper(self._lookup)
        self.Commit = _RequestWrapper(self._commit)
        self.RunQuery = _RequestWrapper(self._run_query)

    def _insert_model(self, model: ndb.Model) -> None:
        ds_key = model.key._key.to_protobuf()
        assert self._get_stored_data(ds_key) is None
        entity_proto = ndb.model._entity_to_protobuf(model)
        self._put_entity(entity_proto, 0)

    def _lookup(
        self, request: types.LookupRequest, *args, **kwargs
    ) -> types.LookupResponse:
        found: List[types.EntityResult] = []
        missing: List[types.EntityResult] = []

        for key in request.keys:
            stored_data = self._get_stored_data(key)
            if stored_data:
                found.append(
                    types.EntityResult(
                        entity=stored_data.entity, version=stored_data.version
                    )
                )
            else:
                missing.append(
                    types.EntityResult(
                        entity=types.Entity(key=key), version=self.seqid,
                    )
                )

        return types.LookupResponse(found=found, missing=missing,)

    def _commit(
        self, request: types.CommitRequest, *args, **kwargs
    ) -> types.CommitResponse:
        results: List[types.MutationResult] = []
        for mutation in request.mutations:
            result = self._apply_mutation(mutation)
            results.append(result)
        return types.CommitResponse(mutation_results=results, index_updates=0,)

    def _run_query(
        self, request: types.RunQueryRequest, *args, **kwargs
    ) -> types.RunQueryResponse:
        # Don't support cloud sql
        # TODO also figire out error handling
        assert request.query

        # Query processing will be very naive.
        query: types.Query = request.query
        resp_data: List[_StoredObject] = []
        for _, stored in self.store.items():
            if query.kind and stored.entity.key.path[-1].kind != query.kind[0].name:
                # this doesn't account for ancestor keys
                continue

            if self._matches_filter(stored, query.filter):
                resp_data.append(stored)

        if query.order:
            # TODO
            assert len(query.order) == 1
            order = query.order[0]
            assert order.direction in [
                types.PropertyOrder.Direction.DESCENDING,
                types.PropertyOrder.Direction.ASCENDING,
            ]
            resp_data.sort(
                key=lambda d: ds_helpers._get_value_from_value_pb(
                    d.entity.properties.get(order.property.name)
                ),
                reverse=order.direction == types.PropertyOrder.Direction.DESCENDING,
            )

        if query.limit:
            resp_data = resp_data[: query.limit.value]

        return types.RunQueryResponse(
            batch=types.QueryResultBatch(
                entity_result_type=types.EntityResult.ResultType.FULL,  # TODO projection
                entity_results=[
                    types.EntityResult(entity=resp.entity, version=resp.version,)
                    for resp in resp_data
                ],
                snapshot_version=self.seqid,
            )
        )

    def _put_entity(self, ds_entity: types.Entity, entity_version: int) -> None:
        self.seqid += 1
        key_str = ds_entity.key.SerializeToString()
        self.store[key_str] = _StoredObject(entity=ds_entity, version=entity_version)

    def _get_stored_data(self, key: types.Key) -> Optional[_StoredObject]:
        key_str = key.SerializeToString()
        return self.store.get(key_str)

    def _delete_entity(self, key: types.Key) -> None:
        key_str = key.SerializeToString()
        if key_str in self.store:
            del self.store[key_str]

    def _matches_filter(
        self, stored_obj: _StoredObject, query_filter: types.Filter
    ) -> bool:
        filter_type = query_filter.WhichOneof("filter_type")
        assert filter_type in ["property_filter", "composite_filter"]
        if filter_type == "property_filter":
            return self._matches_property_filter(
                stored_obj, query_filter.property_filter
            )
        elif filter_type == "composite_filter":
            return self._matches_composite_filter(
                stored_obj, query_filter.composite_filter
            )
        return False

    def _matches_composite_filter(
        self, stored_obj: _StoredObject, comp_filter: types.CompositeFilter
    ) -> bool:
        assert comp_filter.op == types.CompositeFilter.Operator.AND
        results = [self._matches_filter(stored_obj, f) for f in comp_filter.filters]
        return all(results)

    def _matches_property_filter(
        self, stored_obj: _StoredObject, prop_filter: types.PropertyFilter
    ) -> bool:
        for prop_name, prop_val_pb in stored_obj.entity.properties.items():
            prop_val = ds_helpers._get_value_from_value_pb(prop_val_pb)
            if prop_name == prop_filter.property.name:
                op = prop_filter.op
                filter_val = ds_helpers._get_value_from_value_pb(prop_filter.value)
                method_name = self._OPERATOR_TO_CMP_METHOD_NAME.get(op)
                assert method_name
                return getattr(prop_val, method_name)(filter_val)
        return False

    def _apply_mutation(self, mutation: types.Mutation) -> types.MutationResult:
        # TODO will need to potentially do key assignment for insert/upsert
        mutation_key = self._mutation_key(mutation)
        existing_data = self._get_stored_data(mutation_key)
        if mutation.insert:
            # TODO figure out how to properly express error handling
            assert existing_data is None
            self._put_entity(mutation.insert, 0)
            return types.MutationResult(key=mutation_key, version=0)
        elif mutation.update:
            # TODO figure out better error handling
            assert existing_data is not None
            if existing_data.version != mutation.base_version:
                return self._mutation_conflict(mutation_key, existing_data.version)
            new_version = existing_data.version + 1
            self._put_entity(mutation.upsert, new_version)
            return types.MutationResult(key=mutation_key, version=new_version)
        elif mutation.upsert:
            if existing_data and existing_data.version != mutation.base_version:
                return self._mutation_conflict(mutation_key, existing_data.version)
            new_version = existing_data.version + 1 if existing_data else 0
            self._put_entity(mutation.upsert, new_version)
            return types.MutationResult(key=mutation_key, version=new_version)
        elif mutation.delete:
            new_version = existing_data.version + 1 if existing_data else 0
            self._delete_entity(mutation_key)
            return types.MutationResult(key=mutation_key, version=new_version)

    def _mutation_key(self, mutation: types.Mutation) -> types.Key:
        if mutation.insert:
            return mutation.insert.key
        elif mutation.update:
            return mutation.update.key
        elif mutation.upsert:
            return mutation.upsert.key
        elif mutation.delete:
            return mutation.delete.key

    def _mutation_conflict(
        self, key: types.Key, old_version: int
    ) -> types.MutationResult:
        return types.MutationResult(
            key=key, version=old_version, conflict_detected=True,
        )
