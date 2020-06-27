from google.cloud import ndb


class SimpleModel(ndb.Model):
    str_prop = ndb.StringProperty()
    int_prop = ndb.IntegerProperty()


class RepeatedPropertyModel(ndb.Model):
    int_props = ndb.IntegerProperty(repeated=True)


class KeyPropertyModel(ndb.Model):
    model_ref = ndb.KeyProperty(kind=SimpleModel)
