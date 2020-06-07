from InMemoryCloudDatastoreStub import datastore_stub
from tests.models import SimpleModel


def test_get_or_insert_existing_by_id(
    ndb_stub: datastore_stub.LocalDatastoreStub,
) -> None:
    model = SimpleModel(id="test", str_prop="asdf",)
    ndb_stub._insert_model(model)

    model_res = SimpleModel.get_or_insert("test")
    assert model_res == model


def test_get_or_insert_doesnt_exist() -> None:
    model_res = SimpleModel.get_or_insert("test")
    assert model_res is not None


def test_get_or_insert_then_update() -> None:
    model = SimpleModel.get_or_insert("test", int_prop=10)
    assert model is not None

    model.int_prop = 20
    model.put()

    sanity_check = SimpleModel.get_by_id("test")
    assert sanity_check == model
