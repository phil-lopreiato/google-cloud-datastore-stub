import grpc
import logging
from google.cloud import ndb
from google.cloud.datastore_v1 import types
from google.cloud.datastore_v1.proto import datastore_pb2_grpc
from typing import Dict, List


class InstantFuture(grpc.Future):
    def __init__(self, resp):
        self.resp = resp

    def cancel(self):
        return False

    def cancelled(self):
        return False

    def running(self):
        return False

    def done(self):
        return True

    def result(self, timeout=None):
        return self.resp

    def exception(self, timeout=None):
        return None

    def traceback(self, timeout=None):
        return None

    def add_done_callback(self, fn):
        fn(self)


class RequestWrapper(grpc.UnaryUnaryMultiCallable):
    def __init__(self, func):
        self.func = func

    def __call__(self, request, *args, **kwargs):
        logging.warning(f"REQUEST {request}")
        return self.func(request, *args, **kwargs)

    def with_call(self, request, *args, **kwargs):
        return self(request, *args, **kwargs)

    def future(self, request, *args, **kwargs):
        resp = self(request, *args, **kwargs)
        return InstantFuture(resp)


class LocalDatastoreStub(datastore_pb2_grpc.DatastoreStub):

    seqid: int
    store: Dict[str, types.Entity]

    Lookup: RequestWrapper

    def __init__(self) -> None:
        # don't call super, we want to do other stuff
        # also we can ignore the channel, since we're doing it all in memory
        self.seqid = 0
        self.store = {}

        self.Lookup = RequestWrapper(self._lookup)

    def _insert_model(self, model: ndb.Model) -> None:
        key_str = model.key._key.to_protobuf().SerializeToString()
        entity_proto = ndb.model._entity_to_protobuf(model)
        logging.warning(f"ENTITY {entity_proto}")
        self.store[key_str] = entity_proto
        self.seqid += 1

    def _lookup(
        self, request: types.LookupRequest, *args, **kwargs
    ) -> types.LookupResponse:
        found: List[types.EntityResult] = []
        missing: List[types.EntityResult] = []

        for key in request.keys:
            key_str = key.SerializeToString()
            entity = self.store.get(key_str)
            if entity:
                found.append(types.EntityResult(entity=entity, version=self.seqid,))
            else:
                missing.append(
                    types.EntityResult(
                        entity=types.Entity(key=key), version=self.seqid,
                    )
                )

        return types.LookupResponse(found=found, missing=missing,)

    """
    def RunQuery(request, **kwargs) -> grpc.UnaryUnaryMultiCallable:
        logging.warning(f"RunQuery {request}")
        return RequestWrapper()

    def BeginTransaction(request, **kwargs) -> grpc.UnaryUnaryMultiCallable:
        return RequestWrapper()

    def Commit(request, **kwargs) -> grpc.UnaryUnaryMultiCallable:
        logging.warning(f"CALLING COMMIT {request}")
        return RequestWrapper()

    def Rollback(request, **kwargs) -> grpc.UnaryUnaryMultiCallable:
        return RequestWrapper()

    def AllocateIds(request, **kwargs) -> grpc.UnaryUnaryMultiCallable:
        return RequestWrapper()

    def ReserveIds(request, **kwargs) -> grpc.UnaryUnaryMultiCallable:
        return RequestWrapper()
    """
