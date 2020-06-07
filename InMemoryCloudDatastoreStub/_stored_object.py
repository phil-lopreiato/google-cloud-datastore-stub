from google.cloud.datastore_v1 import types
from typing import NamedTuple


class _StoredObject(NamedTuple):
    version: int
    entity: types.Entity
