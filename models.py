# coding: utf-8
from fields.utils import make_field
import fields
from tornado import gen
from datetime import datetime


class ModelDataMixin(object):
    def set_data(self, data):
        self._id = data.get('_id', None)
        for field in self._fields:
            setattr(self, field, data.get(field, None))

    @property
    def __dict__(self):
        fields = {}

        if self._id:
            fields['_id'] = self._id

        for field in self._fields:
            fields[field] = super(
                ModelValidationMixin, self
            ).__getattribute__(field).value

        return fields

    def __setattr__(self, item, value):
        if hasattr(self, item):
            data = object.__getattribute__(self, item)
            if isinstance(data, fields.Field):
                data.set(value)
                return
        return super(ModelDataMixin, self).__setattr__(item, value)

    def __getattribute__(self, item):
        ret = super(ModelValidationMixin, self).__getattribute__(item)
        if isinstance(ret, fields.Field):
            return ret.get()
        return ret


class ModelValidationMixin(object):
    def __init__(self, fields):
        self._fields = fields
        self._fields.update(self.get_default_fields())
        self.make_fields()

    def make_fields(self):
        for name, kwargs in self._fields.items():
            setattr(self, name, make_field(**kwargs))

    def get_default_fields(self):
        return {}

    def is_valid(self):
        valid = True

        for field in self._fields:
            data = super(ModelValidationMixin, self).__getattribute__(field)
            data.clean()

            if not data.is_valid():
                valid = False
                self.errors[field] = data.error
        return valid


class ModelBase(ModelDataMixin, ModelValidationMixin):
    pass


class ModelList(list):
    def get_data(self):
        return [data.__dict__ for data in self]


class Model(ModelBase):
    errors = {}
    _id = None
    _colection = None

    def __init__(self, db, collection_name, fields):
        super(Model, self).__init__(fields)
        self._db = db
        self._collection_name = collection_name
        self.created_at = datetime.now()

    def get_default_fields(self):
        return {
            'created_at': {'type': 'datetime'},
            'last_updates': {'type': 'list', 'field': 'datetime'}
        }

    def get_collection(self):
        if self._colection is None:
            self._colection = self._db[self._collection_name]
        return self._colection

    @property
    def queryset(self):
        return self.get_collection()

    @gen.coroutine
    def save(self):
        collection = self.get_collection()

        if self._id:
            if self.last_updates is None:
                self.last_updates = []

            self.last_updates.append(datetime.now())
            future = collection.update({'_id': self._id}, self.__dict__)
            result = yield future
        else:
            future = collection.insert(self.__dict__)
            result = yield future
            self._id = result

    @gen.coroutine
    def remove(self):
        collection = self.get_collection()
        yield collection.remove({'_id': self._id})

    @gen.coroutine
    def get(self, **kwargs):
        data = yield self.get_collection().find_one(**kwargs)
        self.set_data(data)
