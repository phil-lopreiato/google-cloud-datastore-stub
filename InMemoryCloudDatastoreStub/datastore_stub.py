import google.cloud.datastore.helpers as ds_helpers
from google.cloud import ndb
from google.cloud.datastore_v1 import types
from google.cloud.datastore_v1.proto import datastore_pb2_grpc
from typing import List

from ._in_memory_store import _InMemoryStore
from ._request_wrapper import _RequestWrapper
from ._stored_object import _StoredObject
from ._transactions import _TransactionType


class LocalDatastoreStub(datastore_pb2_grpc.DatastoreStub):

    _OPERATOR_TO_CMP_METHOD_NAME = {
        types.PropertyFilter.Operator.LESS_THAN: "__lt__",
        types.PropertyFilter.Operator.LESS_THAN_OR_EQUAL: "__le__",
        types.PropertyFilter.Operator.GREATER_THAN: "__gt__",
        types.PropertyFilter.Operator.GREATER_THAN_OR_EQUAL: "__ge__",
        types.PropertyFilter.Operator.EQUAL: "__eq__",
        # TODO missing HAS_ANCESTOR
    }

    store: _InMemoryStore

    Lookup: _RequestWrapper
    Commit: _RequestWrapper
    RunQuery: _RequestWrapper
    BeginTransaction: _RequestWrapper
    Rollback: _RequestWrapper
    # AllocateIds: _RequestWrapper
    # ReserveIds: _RequestWrapper

    def __init__(self) -> None:
        self.store = _InMemoryStore()

        self.Lookup = _RequestWrapper(self._lookup)
        self.Commit = _RequestWrapper(self._commit)
        self.RunQuery = _RequestWrapper(self._run_query)
        self.BeginTransaction = _RequestWrapper(self._begin_transaction)
        self.Rollback = _RequestWrapper(self._rollback)

    def _insert_model(self, model: ndb.Model) -> None:
        ds_key = model.key._key.to_protobuf()
        assert self.store.get(ds_key, None) is None
        entity_proto = ndb.model._entity_to_protobuf(model)
        self.store.put(entity_proto, 0, None)

    def _lookup(
        self, request: types.LookupRequest, *args, **kwargs
    ) -> types.LookupResponse:
        found: List[types.EntityResult] = []
        missing: List[types.EntityResult] = []
        transaction_id = request.read_options.transaction

        for key in request.keys:
            stored_data = self.store.get(key, transaction_id)
            if stored_data:
                found.append(
                    types.EntityResult(
                        entity=stored_data.entity, version=stored_data.version
                    )
                )
            else:
                missing.append(
                    types.EntityResult(
                        entity=types.Entity(key=key),
                        version=self.store.seqid(transaction_id),
                    )
                )

        return types.LookupResponse(found=found, missing=missing,)

    def _begin_transaction(
        self, request: types.BeginTransactionRequest, *args, **kwargs
    ) -> types.BeginTransactionResponse:
        transaction_mode = None
        request_type = request.transaction_options.WhichOneof("mode")
        if request_type == "read_write":
            transaction_mode = _TransactionType.READ_WRITE
        elif request_type == "read_only":
            transaction_mode = _TransactionType.READ_ONLY
        assert transaction_mode is not None
        transaction_id = self.store.beginTransaction(transaction_mode)

        return types.BeginTransactionResponse(transaction=transaction_id,)

    def _commit(
        self, request: types.CommitRequest, *args, **kwargs
    ) -> types.CommitResponse:
        results: List[types.MutationResult] = self.store.commitTransaction(
            request.transaction, request.mutations
        )
        return types.CommitResponse(mutation_results=results, index_updates=0,)

    def _rollback(
        self, request: types.RollbackRequest, *args, **kwargs
    ) -> types.RollbackResponse:
        self.store.rollbackTransaction(request.transaction)
        return types.RollbackResponse()

    def _run_query(
        self, request: types.RunQueryRequest, *args, **kwargs
    ) -> types.RunQueryResponse:
        # Don't support cloud sql
        # TODO also figire out error handling
        assert request.query

        # Query processing will be very naive.
        query: types.Query = request.query
        transaction_id: bytes = request.read_options.transaction
        resp_data: List[_StoredObject] = []
        for _, stored in self.store.items(transaction_id):
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

        if query.HasField("limit"):
            resp_data = resp_data[: query.limit.value]

        if query.projection:
            projection_fields = [p.property.name for p in query.projection]
            if projection_fields == ["__key__"]:
                result_type = types.EntityResult.ResultType.KEY_ONLY
                entity_results = [
                    types.EntityResult(
                        entity=types.Entity(key=resp.entity.key), version=resp.version
                    )
                    for resp in resp_data
                ]
            else:
                result_type = types.EntityResult.ResultType.PROJECTION
                entity_results = [
                    types.EntityResult(
                        entity=types.Entity(
                            key=resp.entity.key,
                            properties={
                                k: v
                                for k, v in resp.entity.properties.items()
                                if k in projection_fields
                            },
                        ),
                        version=resp.version,
                    )
                    for resp in resp_data
                ]
        else:
            result_type = types.EntityResult.ResultType.FULL
            entity_results = [
                types.EntityResult(entity=resp.entity, version=resp.version)
                for resp in resp_data
            ]

        return types.RunQueryResponse(
            batch=types.QueryResultBatch(
                entity_result_type=result_type,
                entity_results=entity_results,
                snapshot_version=self.store.seqid(transaction_id),
            )
        )

    def _matches_filter(
        self, stored_obj: _StoredObject, query_filter: types.Filter
    ) -> bool:
        filter_type = query_filter.WhichOneof("filter_type")
        if filter_type is None:
            # If doing a query for all entities, filter will be None
            return True

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
            prop_type = prop_val_pb.WhichOneof("value_type")
            prop_val = ds_helpers._get_value_from_value_pb(prop_val_pb)
            if prop_name == prop_filter.property.name:
                op = prop_filter.op
                filter_val = ds_helpers._get_value_from_value_pb(prop_filter.value)
                method_name = self._OPERATOR_TO_CMP_METHOD_NAME.get(op)
                assert method_name

                if prop_type == "array_value":
                    # For repeated properties, we need to unpack them
                    res = any(
                        getattr(p, method_name)(filter_val) == True for p in prop_val
                    )
                else:
                    res = getattr(prop_val, method_name)(filter_val)

                if res is NotImplemented:
                    return False
                return res
        return False
