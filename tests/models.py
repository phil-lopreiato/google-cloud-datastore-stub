from google.cloud import ndb


class SimpleModel(ndb.Model):
    str_prop = ndb.StringProperty()
    int_prop = ndb.IntegerProperty()
