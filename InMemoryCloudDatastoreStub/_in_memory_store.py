import copy
import uuid
from google.cloud.datastore_v1 import types
from typing import Dict, Iterable, Optional, Tuple, List
from ._stored_object import _StoredObject
from ._transactions import _InFlightTransaction, _TransactionType


class _InMemoryStore(object):

    _seqid: int
    _store: Dict[str, _StoredObject]
    _transactions: Dict[bytes, _InFlightTransaction]

    def __init__(self) -> None:
        self._seqid = 0
        self._store = {}
        self._transactions = {}

    def seqid(self, transaction_id: Optional[bytes]) -> int:
        if transaction_id and transaction_id in self._transactions:
            return self._transactions[transaction_id].initial_seqid
        return self._seqid

    def put(
        self,
        ds_entity: types.Entity,
        entity_version: int,
        transaction_id: Optional[bytes],
    ) -> None:
        key_str = ds_entity.key.SerializeToString()
        if transaction_id and transaction_id in self._transactions:
            mutation = types.Mutation(upsert=ds_entity,)
            self._transactions[transaction_id].mutations.append(mutation)
        else:
            self._seqid += 1
            self._store[key_str] = _StoredObject(
                entity=ds_entity, version=entity_version
            )

    def get(
        self, key: types.Key, transaction_id: Optional[bytes]
    ) -> Optional[_StoredObject]:
        key_str = key.SerializeToString()
        if transaction_id and transaction_id in self._transactions:
            return self._transactions[transaction_id].snapshot.get(key_str)
        else:
            return self._store.get(key_str)

    def delete(self, key: types.Key, transaction_id: Optional[bytes]) -> None:
        key_str = key.SerializeToString()
        if transaction_id and transaction_id in self._transactions:
            mutation = types.Mutation(delete=key,)
            self._transactions[transaction_id].mutations.append(mutation)
        else:
            if key_str in self._store:
                del self._store[key_str]

    def items(self, transaction_id: bytes) -> Iterable[Tuple[str, _StoredObject]]:
        if transaction_id in self._transactions:
            return self._transactions[transaction_id].snapshot.items()
        else:
            return self._store.items()

    def beginTransaction(self, mode: _TransactionType) -> bytes:
        transaction_id = uuid.uuid1().bytes
        self._transactions[transaction_id] = _InFlightTransaction(
            mode=mode,
            initial_seqid=self._seqid,
            snapshot=copy.deepcopy(self._store),
            mutations=[],
        )
        return transaction_id

    def commitTransaction(
        self, transaction_id: bytes, final_mutations: List[types.Mutation]
    ) -> List[types.MutationResult]:
        if transaction_id != b"" and transaction_id in self._transactions:
            transaction = self._transactions[transaction_id]

            # Apply OCC (make sure no entities touched in the transaction have been modified since it began)
            # For now, just assume that no writes at all are allowed
            assert self._seqid == transaction.initial_seqid

            for mutation in transaction.mutations:
                self._applyMutation(mutation)

            del self._transactions[transaction_id]

        return [self._applyMutation(m) for m in final_mutations]

    def rollbackTransaction(self, transaction_id: bytes) -> None:
        assert transaction_id in self._transactions
        del self._transactions[transaction_id]

    def _applyMutation(self, mutation: types.Mutation) -> types.MutationResult:
        # TODO will need to potentially do key assignment for insert/upsert
        mutation_key = self._mutation_key(mutation)
        existing_data = self.get(mutation_key, None)
        operation = mutation.WhichOneof("operation")
        if operation == "insert":
            # TODO figure out how to properly express error handling
            assert existing_data is None
            self.put(mutation.insert, 0, None)
            return types.MutationResult(key=mutation_key, version=0)
        elif operation == "update":
            # TODO figure out better error handling
            assert existing_data is not None
            if existing_data.version != mutation.base_version:
                return self._mutation_conflict(mutation_key, existing_data.version)
            new_version = existing_data.version + 1
            self.put(mutation.upsert, new_version, None)
            return types.MutationResult(key=mutation_key, version=new_version)
        elif operation == "upsert":
            if existing_data and existing_data.version != mutation.base_version:
                return self._mutation_conflict(mutation_key, existing_data.version)
            new_version = existing_data.version + 1 if existing_data else 0
            self.put(mutation.upsert, new_version, None)
            return types.MutationResult(key=mutation_key, version=new_version)
        elif operation == "delete":
            new_version = existing_data.version + 1 if existing_data else 0
            self.delete(mutation_key, None)
            return types.MutationResult(key=mutation_key, version=new_version)

    def _mutation_key(self, mutation: types.Mutation) -> types.Key:
        operation = mutation.WhichOneof("operation")
        if operation == "insert":
            return mutation.insert.key
        elif operation == "update":
            return mutation.update.key
        elif operation == "upsert":
            return mutation.upsert.key
        elif operation == "delete":
            return mutation.delete.key

    def _mutation_conflict(
        self, key: types.Key, old_version: int
    ) -> types.MutationResult:
        return types.MutationResult(
            key=key, version=old_version, conflict_detected=True,
        )
