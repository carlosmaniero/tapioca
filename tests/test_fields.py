import fields
from fields.utils import make_field
from datetime import datetime


def test_blank_field():
    field = fields.Field()
    field.clean()
    assert field.is_valid()


def test_required_field():
    field = fields.Field(required=True)
    field.clean()
    assert not field.is_valid()

    field.set('foo bar')
    field.clean()
    assert field.is_valid()


def test_char():
    field = fields.CharField(blank=True)
    field.clean()
    assert field.is_valid()

    field = fields.CharField(blank=False)
    field.set('')
    field.clean()
    assert not field.is_valid()


def test_char_limits():
    field = fields.CharField(min_length=3, max_length=6)
    field.set('abc')
    field.clean()
    assert field.is_valid()

    field.set('abcdef')
    field.clean()
    assert field.is_valid()

    field.set('ab')
    field.clean()
    assert not field.is_valid()

    field.set('abcdefg')
    field.clean()
    assert not field.is_valid()


def test_int():
    field = fields.IntegerField()
    field.clean()
    assert field.is_valid()

    field.set(4.2)
    value = field.clean()
    assert field.is_valid()
    assert value == 4

    field.set('3.14')
    value = field.clean()
    assert field.is_valid()
    assert value == 3

    field.set('aimpim')
    value = field.clean()
    assert not field.is_valid()


def num_limits(fieldclass, min, max):
    field = fieldclass(min=min, max=max)

    field.set(min)
    field.clean()
    assert field.is_valid()

    field.set(min - 1)
    field.clean()
    assert not field.is_valid()

    field.set(max)
    field.clean()
    assert field.is_valid()

    field.set(max + 1)
    field.clean()
    assert not field.is_valid()


def test_int_limits():
    num_limits(fields.IntegerField, 3, 6)


def test_float():
    field = fields.FloatField()
    field.clean()
    assert field.is_valid()

    field.set(4.2)
    value = field.clean()
    assert field.is_valid()

    field.set('3.14')
    value = field.clean()
    assert field.is_valid()
    assert value == 3.14

    field.set('aimpim')
    value = field.clean()
    assert not field.is_valid()


def test_float_limits():
    num_limits(fields.FloatField, 3.14, 42)


def test_boolean():
    field = fields.BooleanField()

    field.set(False)
    value = field.clean()
    assert field.is_valid()
    assert not value

    field.set(True)
    value = field.clean()
    assert field.is_valid()
    assert value

    field.set(None)
    value = field.clean()
    assert field.is_valid()
    assert not value

    field.set("This is love")
    value = field.clean()
    assert field.is_valid()
    assert value


def test_choice():
    field = fields.ChoiceField(
        ('banana', 'tofu'),
        required=True
    )

    field.set('meat')     # :,(
    field.clean()
    assert not field.is_valid()

    field.set('banana')
    field.clean()
    assert field.is_valid()


def test_datetime():
    field = fields.DateTimeField()

    field.set('1993-09-25 05:30:00')
    date = datetime(1993, 9, 25, 5, 30, 00)
    date_field = field.clean()
    assert field.is_valid()
    assert date == date_field

    field.set('1993-09-25 05:30')
    field.clean()
    assert not field.is_valid()


def test_date():
    field = fields.DateField()

    field.set('1993-09-25')
    date = datetime(1993, 9, 25)
    date_field = field.clean()
    assert field.is_valid()
    assert date == date_field

    field.set('1993-09-32')
    field.clean()
    assert not field.is_valid()


def test_regex():
    field = fields.RegexField(r'[abc]+')

    field.set('aabbccccbbaa')
    field.clean()
    assert field.is_valid()

    field.set('foo bar')
    field.clean()
    assert not field.is_valid()


def test_email():
    field = fields.EmailField()

    field.set('carlosmaniero@gmail.com')
    field.clean()
    assert field.is_valid()

    field.set('carlosmaniero@gmail')
    field.clean()
    assert not field.is_valid()


def test_http():
    field = fields.UrlField()

    field.set('https://www.python.org/')
    field.clean()
    assert field.is_valid()

    field.set('https://tapioca.vegan')
    field.clean()
    assert field.is_valid()

    field.set('http://bacon')
    field.clean()
    assert not field.is_valid()


def test_array():
    field = fields.ListField('int', {'required': True})
    field.set([1, 2, 3, 4, 5])
    field.clean()
    assert field.is_valid()

    field = fields.ListField('email', {'required': True})
    field.set(['tapioca@pot.com', 'foobar'])
    field.clean()
    assert not field.is_valid()


def test_register():
    assert fields.fields.get_field('email') == fields.EmailField
    assert fields.fields.get_field('int') == fields.IntegerField
    assert fields.fields.get_field('float') == fields.FloatField


def test_make_field():
    field = make_field(required=True, blank=False, type='char')
    field.set('')
    field.clean()
    assert not field.is_valid()
