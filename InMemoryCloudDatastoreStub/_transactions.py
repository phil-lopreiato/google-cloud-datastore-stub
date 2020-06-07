import enum
from google.cloud.datastore_v1 import types
from typing import Dict, List, NamedTuple
from ._stored_object import _StoredObject


class _TransactionType(enum.Enum):
    READ_ONLY = 0
    READ_WRITE = 1


class _InFlightTransaction(NamedTuple):
    mode: _TransactionType
    initial_seqid: int
    snapshot: Dict[str, _StoredObject]
    mutations: List[types.Mutation]
