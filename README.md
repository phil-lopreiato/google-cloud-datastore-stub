# An In-Memory Stub for Google Cloud Datastore

[![PyPI version](https://badge.fury.io/py/InMemoryCloudDatastoreStub.svg)](https://pypi.python.org/pypi/InMemoryCloudDatastoreStub/)

This project is a pure python implementation of the Google Cloud Datastore [RPC Spec](https://cloud.google.com/datastore/docs/reference/data/rpc). This allows projects using the [python-ndb](https://github.com/googleapis/python-ndb) lirary to write unit tests without needing to depend on/manage the full datastore emulator. It is intended as a replacement for the legacy App Engine runtime's [local datastore testbed](https://cloud.google.com/appengine/docs/standard/python/tools/localunittesting).

## Installing

`InMemoryCloudDatatoreStub` can be installed [from PyPi](https://pypi.org/project/InMemoryCloudDatastoreStub/):
```bash
$ pip install InMemoryCloudDatastoreStub
```

## Using

The stub can be inserted into your unit tests as a pytest fixture using [monkeypatch](https://docs.pytest.org/en/stable/monkeypatch.html):
```python
from unittest.mock import MagicMock

import pytest
from google.cloud.ndb import _datastore_api
from InMemoryCloudDatastoreStub.datastore_stub import LocalDatastoreStub

@pytest.fixture()
def ndb_stub(monkeypatch):
    stub = LocalDatastoreStub()
    monkeypatch.setattr(_datastore_api, "stub", MagicMock(return_value=stub))
    return stub
```

## Contributing

Unit tests, typechecks, and lints can all be run with [`tox`](https://tox.readthedocs.io/en/latest/):

```bash
# Run everything
$ tox

# Run unit tests
$ tox -e py

# Run lint check
$ tox -e lint

# Run type check
$ tox -e typecheck
```
