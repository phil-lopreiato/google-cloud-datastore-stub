from InMemoryDatastore import datastore_stub
from tests.models import SimpleModel


def test_get_nonexistent_key() -> None:
    model = SimpleModel.get_by_id("notfound")
    assert model is None


def test_get_existing(ndb_stub: datastore_stub.LocalDatastoreStub) -> None:
    model = SimpleModel(id="test", str_prop="asdf",)
    ndb_stub._insert_model(model)

    model_res = SimpleModel.get_by_id("test")
    assert model_res == model
