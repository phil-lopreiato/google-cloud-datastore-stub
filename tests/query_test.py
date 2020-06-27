import pytest
from InMemoryCloudDatastoreStub import datastore_stub
from google.cloud import ndb
from tests.models import RepeatedPropertyModel, SimpleModel, KeyPropertyModel


def test_get_nonexistent_key() -> None:
    model = SimpleModel.get_by_id("notfound")
    assert model is None


def test_get_existing_by_id(ndb_stub: datastore_stub.LocalDatastoreStub) -> None:
    model = SimpleModel(id="test", str_prop="asdf",)
    ndb_stub._insert_model(model)

    model_res = SimpleModel.get_by_id("test")
    assert model_res == model


def test_get_existing_by_field(ndb_stub: datastore_stub.LocalDatastoreStub) -> None:
    model = SimpleModel(id="test", str_prop="asdf",)
    ndb_stub._insert_model(model)

    query_res = SimpleModel.query(SimpleModel.str_prop == "asdf").get()
    assert query_res == model


def test_get_existing_by_multi_field(
    ndb_stub: datastore_stub.LocalDatastoreStub,
) -> None:
    model = SimpleModel(id="test", str_prop="asdf", int_prop=42)
    ndb_stub._insert_model(model)

    query_res = SimpleModel.query(
        SimpleModel.str_prop == "asdf", SimpleModel.int_prop == 42
    ).get()
    assert query_res == model


def test_get_existing_by_field_not_found(
    ndb_stub: datastore_stub.LocalDatastoreStub,
) -> None:
    model = SimpleModel(id="test", str_prop="asdf",)
    ndb_stub._insert_model(model)

    query_res = SimpleModel.query(SimpleModel.str_prop == "foo").get()
    assert query_res is None


def test_fetch_existing_by_field_multiple(
    ndb_stub: datastore_stub.LocalDatastoreStub,
) -> None:
    model1 = SimpleModel(id="test", str_prop="asdf",)
    model2 = SimpleModel(id="test2", str_prop="asdf",)
    ndb_stub._insert_model(model1)
    ndb_stub._insert_model(model2)

    # We don't pass an ordering here, so the order is not deterministic
    query_res = SimpleModel.query(SimpleModel.str_prop == "asdf").fetch(limit=2)
    assert len(query_res) == 2
    query_res.sort(key=lambda m: m.key.id())
    assert query_res == [model1, model2]


def test_fetch_existing_by_field_multiple_with_order(
    ndb_stub: datastore_stub.LocalDatastoreStub,
) -> None:
    model1 = SimpleModel(id="test", str_prop="asdf", int_prop=10)
    model2 = SimpleModel(id="test2", str_prop="asdf", int_prop=20)
    ndb_stub._insert_model(model1)
    ndb_stub._insert_model(model2)

    # We don't pass an ordering here, so the order is not deterministic
    query_res = (
        SimpleModel.query(SimpleModel.str_prop == "asdf")
        .order(SimpleModel.int_prop)
        .fetch(limit=2)
    )
    assert len(query_res) == 2
    assert query_res == [model1, model2]


def test_fetch_existing_by_field_with_limit(
    ndb_stub: datastore_stub.LocalDatastoreStub,
) -> None:
    model1 = SimpleModel(id="test", str_prop="asdf",)
    model2 = SimpleModel(id="test2", str_prop="asdf",)
    ndb_stub._insert_model(model1)
    ndb_stub._insert_model(model2)

    # Since we don't pass an order by, it's non deterministic which we get
    query_res = SimpleModel.query(SimpleModel.str_prop == "asdf").fetch(limit=1)
    assert len(query_res) == 1
    assert query_res[0].str_prop == "asdf"


def test_fetch_existing_by_field_with_limit_not_hit(
    ndb_stub: datastore_stub.LocalDatastoreStub,
) -> None:
    model1 = SimpleModel(id="test", str_prop="asdf",)
    model2 = SimpleModel(id="test2", str_prop="asdfz",)
    ndb_stub._insert_model(model1)
    ndb_stub._insert_model(model2)

    # Since we don't pass an order by, it's non deterministic which we get
    query_res = SimpleModel.query(SimpleModel.str_prop == "asdf").fetch(limit=2)
    assert len(query_res) == 1
    assert query_res[0].str_prop == "asdf"


def test_fetch_existing_by_gt(ndb_stub: datastore_stub.LocalDatastoreStub) -> None:
    model1 = SimpleModel(id="test", int_prop=42,)
    model2 = SimpleModel(id="test2", int_prop=43,)
    ndb_stub._insert_model(model1)
    ndb_stub._insert_model(model2)

    query_res = SimpleModel.query(SimpleModel.int_prop > 42).fetch(limit=5)
    assert query_res == [model2]


def test_fetch_existing_by_ge(ndb_stub: datastore_stub.LocalDatastoreStub) -> None:
    model1 = SimpleModel(id="test", int_prop=42,)
    model2 = SimpleModel(id="test2", int_prop=43,)
    ndb_stub._insert_model(model1)
    ndb_stub._insert_model(model2)

    query_res = SimpleModel.query(SimpleModel.int_prop >= 42).fetch(limit=5)
    assert len(query_res) == 2


def test_fetch_existing_by_lt(ndb_stub: datastore_stub.LocalDatastoreStub) -> None:
    model1 = SimpleModel(id="test", int_prop=42,)
    model2 = SimpleModel(id="test2", int_prop=43,)
    ndb_stub._insert_model(model1)
    ndb_stub._insert_model(model2)

    query_res = SimpleModel.query(SimpleModel.int_prop < 43).fetch(limit=5)
    assert query_res == [model1]


def test_fetch_existing_by_le(ndb_stub: datastore_stub.LocalDatastoreStub) -> None:
    model1 = SimpleModel(id="test", int_prop=42,)
    model2 = SimpleModel(id="test2", int_prop=43,)
    ndb_stub._insert_model(model1)
    ndb_stub._insert_model(model2)

    query_res = SimpleModel.query(SimpleModel.int_prop <= 43).fetch(limit=5)
    assert len(query_res) == 2


def test_put_model() -> None:
    model = SimpleModel(id="test", str_prop="asdf")
    key = model.put()

    assert key == model.key


def test_put_model_matches_key_get() -> None:
    model = SimpleModel(id="test", str_prop="asdf")
    key = model.put()

    get_resp = key.get()
    assert get_resp == model


def test_put_model_matches_point_query() -> None:
    model = SimpleModel(id="test", str_prop="asdf")
    key = model.put()

    get_resp = SimpleModel.get_by_id("test")
    assert get_resp == model
    assert model.key == key


def test_put_model_with_repeated_property() -> None:
    model = RepeatedPropertyModel(id="test", int_props=[1, 2, 3])
    key = model.put()

    get_resp = RepeatedPropertyModel.get_by_id("test")
    assert get_resp == model
    assert get_resp.int_props == [1, 2, 3]
    assert model.key == key


def test_query_all() -> None:
    stored_keys = ndb.put_multi(
        [SimpleModel(id=f"test{i}", int_prop=i) for i in range(10)]
    )
    assert len(stored_keys) == 10

    query_all = SimpleModel.query().order(SimpleModel.int_prop).fetch()
    assert len(query_all) == 10
    for i, model in enumerate(query_all):
        assert model.int_prop == i


def test_query_in_range() -> None:
    stored_keys = ndb.put_multi(
        [SimpleModel(id=f"test{i}", int_prop=i) for i in range(10)]
    )
    assert len(stored_keys) == 10

    resp = (
        SimpleModel.query(SimpleModel.int_prop >= 1, SimpleModel.int_prop < 5)
        .order(SimpleModel.int_prop)
        .fetch()
    )
    assert len(resp) == 4
    for i, model in enumerate(resp):
        assert model.int_prop == i + 1


def test_query_keys_only() -> None:
    stored_keys = ndb.put_multi(
        [SimpleModel(id=f"test{i}", int_prop=i) for i in range(10)]
    )
    assert len(stored_keys) == 10

    resp = SimpleModel.query().fetch(keys_only=True)
    assert len(resp) == 10
    assert all(isinstance(i, ndb.Key) for i in resp)


def test_query_projection() -> None:
    stored_keys = ndb.put_multi(
        [SimpleModel(id=f"test{i}", int_prop=i, str_prop=f"{i}") for i in range(10)]
    )
    assert len(stored_keys) == 10

    resp = SimpleModel.query().fetch(projection=[SimpleModel.int_prop])
    assert len(resp) == 10
    assert all(i.int_prop is not None for i in resp)
    with pytest.raises(ndb.model.UnprojectedPropertyError):
        assert all(i.str_prop is None for i in resp)


def test_query_for_key_prop_none() -> None:
    resp = KeyPropertyModel.query(
        KeyPropertyModel.model_ref == ndb.Key(SimpleModel, "test")
    ).fetch()
    assert resp == []


def test_query_for_key_prop_filter() -> None:
    SimpleModel(id="test").put()
    SimpleModel(id="test1").put()
    SimpleModel(id="test2").put()
    KeyPropertyModel(id="test", model_ref=ndb.Key(SimpleModel, "test")).put()

    resp = KeyPropertyModel.query(
        KeyPropertyModel.model_ref == ndb.Key(SimpleModel, "test")
    ).fetch()
    assert len(resp) == 1
    assert resp[0] == KeyPropertyModel.get_by_id("test")
    assert resp[0].model_ref.get() == SimpleModel.get_by_id("test")


def test_query_for_key_prop_unset() -> None:
    KeyPropertyModel(id="test", model_ref=None).put()

    resp = KeyPropertyModel.query(
        KeyPropertyModel.model_ref == ndb.Key(SimpleModel, "test")
    ).fetch()
    assert len(resp) == 0


def test_query_for_key_prop_unset_in_query() -> None:
    KeyPropertyModel(id="test", model_ref=None).put()

    resp = KeyPropertyModel.query(KeyPropertyModel.model_ref == None).fetch()
    assert len(resp) == 1
    assert resp[0] == KeyPropertyModel.get_by_id("test")
