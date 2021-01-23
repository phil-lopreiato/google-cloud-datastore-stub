# An In-Memory Stub for Google Cloud Datastore

This project is a pure python implementation of the Google Cloud Datastore [RPC Spec](https://cloud.google.com/datastore/docs/reference/data/rpc). This allows projects using the [python-ndb](https://github.com/googleapis/python-ndb) lirary to write unit tests without needing to depend on/manage the full datastore emulator.

## Installing

`InMemoryCloudDatatoreStub` can be installed [from PyPi](https://pypi.org/project/InMemoryCloudDatastoreStub/):
```bash
$ pip install InMemoryCloudDatastoreStub
```

## Using

The stub can be inserted into your unit tests as a pytest fixture using [monkeypatch](https://docs.pytest.org/en/stable/monkeypatch.html):
```python
from unittest.mock import magicMock

import pytest
from InMemoryCloudDatastoreStub.datastore_stub import LocalDatastoreStub

@pytest.fixture()
def ndb_stub(monkeypatch):
    stub = LocalDatastoreStub()
    monkeypatch.setattr(_datastore_api, "stub", MagicMock(return_value=stub))
    return stub
```
