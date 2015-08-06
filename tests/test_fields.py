import fields


def test_blank_field():
    field = fields.Field()
    field.clean()
    assert field.is_valid()


def test_required_field():
    field = fields.Field(required=True)
    field.clean()
    assert not field.is_valid()

    field.set_value('foo bar')
    field.clean()
    assert field.is_valid()


def test_char():
    field = fields.CharField(blank=True)
    field.clean()
    assert field.is_valid()

    field = fields.CharField(blank=False)
    field.set_value('')
    field.clean()
    assert not field.is_valid()


def test_char_limits():
    field = fields.CharField(min_length=3, max_length=6)
    field.set_value('abc')
    field.clean()
    assert field.is_valid()

    field.set_value('abcdef')
    field.clean()
    assert field.is_valid()

    field.set_value('ab')
    field.clean()
    assert not field.is_valid()

    field.set_value('abcdefg')
    field.clean()
    assert not field.is_valid()


def test_int():
    field = fields.IntegerField()
    field.clean()
    assert field.is_valid()

    field.set_value(4.2)
    value = field.clean()
    assert field.is_valid()
    assert value == 4

    field.set_value('3.14')
    value = field.clean()
    assert field.is_valid()
    assert value == 3

    field.set_value('aimpim')
    value = field.clean()
    assert not field.is_valid()


def num_limits(fieldclass, min, max):
    field = fieldclass(min=min, max=max)

    field.set_value(min)
    field.clean()
    assert field.is_valid()

    field.set_value(min - 1)
    field.clean()
    assert not field.is_valid()

    field.set_value(max)
    field.clean()
    assert field.is_valid()

    field.set_value(max + 1)
    field.clean()
    assert not field.is_valid()


def test_int_limits():
    num_limits(fields.IntegerField, 3, 6)


def test_float():
    field = fields.FloatField()
    field.clean()
    assert field.is_valid()

    field.set_value(4.2)
    value = field.clean()
    assert field.is_valid()

    field.set_value('3.14')
    value = field.clean()
    assert field.is_valid()
    assert value == 3.14

    field.set_value('aimpim')
    value = field.clean()
    assert not field.is_valid()


def test_float_limits():
    num_limits(fields.FloatField, 3.14, 42)


def test_boolean():
    field = fields.BooleanField()

    field.set_value(False)
    value = field.clean()
    assert field.is_valid()
    assert not value

    field.set_value(True)
    value = field.clean()
    assert field.is_valid()
    assert value

    field.set_value(None)
    value = field.clean()
    assert field.is_valid()
    assert not value

    field.set_value("This is love")
    value = field.clean()
    assert field.is_valid()
    assert value


def test_choice():
    field = fields.ChoiceField(
        ('banana', 'tofu')
    )

    field.set_value('meat')     # :,(
    field.clean()
    assert not field.is_valid()

    field.set_value('banana')
    field.clean()
    assert field.is_valid()


def test_regex():
    field = fields.RegexField(r'[abc]+')

    field.set_value('aabbccccbbaa')
    field.clean()
    assert field.is_valid()

    field.set_value('foo bar')
    field.clean()
    assert not field.is_valid()


def test_email():
    field = fields.EmailField()

    field.set_value('carlosmaniero@gmail.com')
    field.clean()
    assert field.is_valid()

    field.set_value('carlosmaniero@gmail')
    field.clean()
    assert not field.is_valid()


def test_http():
    field = fields.UrlField()

    field.set_value('https://www.python.org/')
    field.clean()
    assert field.is_valid()

    field.set_value('https://tapioca.vegan')
    field.clean()
    assert field.is_valid()

    field.set_value('http://bacon')
    field.clean()
    assert not field.is_valid()
