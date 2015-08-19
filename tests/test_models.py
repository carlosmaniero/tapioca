# coding: utf-8
import models
import motor
import pytest
from datetime import datetime


def get_db():
    client = motor.MotorClient()
    return client['test_database']


def get_tapioca():
    db = get_db()

    return models.Model(
        collection_name='tapiocas',
        db=db,
        fields={
            'flavor': {
                'type': 'char'
            },
            'candy': {
                'type': 'boolean',
                'default': True
            },
            'size': {
                'type': 'choice',
                'choices': ['big', 'small', 'medium'],
                'required': True
            }
        }
    )


@pytest.mark.gen_test
def test_drop():
    tapioca = get_tapioca()
    yield tapioca.queryset.drop()


@pytest.mark.gen_test
def test_insert():
    tapioca = get_tapioca()
    flavor = 'Banana'
    size = 'big'

    total = yield tapioca.queryset.count()

    tapioca.flavor = flavor
    tapioca.size = size

    assert tapioca.flavor == flavor
    assert tapioca.size == size
    assert isinstance(tapioca.created_at, datetime)
    assert tapioca.is_valid()

    yield tapioca.save()

    total2 = yield tapioca.queryset.count()

    assert total + 1 == total2

    assert tapioca._id is not None


@pytest.mark.gen_test
def test_all():
    tapioca = get_tapioca()
    tapiocas = yield tapioca.queryset.find().to_list(length=None)
    assert type(tapiocas) == list


@pytest.mark.gen_test
def test_check_order():
    tapioca = get_tapioca()
    tapiocas = yield tapioca.queryset.find().to_list(length=1)
    assert len(tapiocas) > 0
    tapioca0 = tapiocas[0]
    tapiocas = yield tapioca.queryset.find().to_list(length=1)
    tapioca1 = tapiocas[0]

    assert tapioca0['_id'] == tapioca1['_id']


@pytest.mark.gen_test
def test_update():
    tapioca = get_tapioca()
    tapiocas = yield tapioca.queryset.find().to_list(length=1)

    assert len(tapiocas) > 0
    data = tapiocas[0]
    tapioca.set_data(data)
    flavor = 'Mandioqueijo'
    size = 'small'

    tapioca.flavor = flavor
    tapioca.size = size
    tapioca.candy = False

    yield tapioca.save()

    assert tapioca._id == data['_id']

    tapiocas2 = yield tapioca.queryset.find().to_list(length=1)
    assert data['_id'] == tapiocas2[0]['_id']
    assert flavor == tapiocas2[0]['flavor']
    assert size == tapiocas2[0]['size']
    assert not tapiocas2[0]['candy']


@pytest.mark.gen_test
def test_get():
    tapioca = get_tapioca()
    yield tapioca.get(flavor='brigadeiro')
    assert tapioca._id is not None
    assert isinstance(tapioca.created_at, datetime)


@pytest.mark.gen_test
def test_remove():
    tapioca = get_tapioca()
    yield tapioca.get(flavor='brigadeiro')
    total = yield tapioca.queryset.count()
    assert tapioca._id is not None
    yield tapioca.remove()
    total2 = yield tapioca.queryset.count()
    assert total - 1 == total2


@pytest.mark.gen_test
def test_remove_all():
    tapioca = get_tapioca()
    yield tapioca.queryset.remove()
    total = yield tapioca.queryset.count()
    assert total == 0
