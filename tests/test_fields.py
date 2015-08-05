import fields


def test_blank_field():
    simple_field = fields.Field()
    simple_field.clean()
    assert simple_field.is_valid()


def test_required_field():
    simple_field = fields.Field(required=True)
    simple_field.clean()
    assert not simple_field.is_valid()

    simple_field.set_value('foo bar')
    simple_field.clean()
    assert simple_field.is_valid()


def test_charfield():
    charfield = fields.CharField(blank=True)
    charfield.clean()
    assert charfield.is_valid()

    charfield = fields.CharField(blank=False)
    charfield.set_value('')
    charfield.clean()
    assert not charfield.is_valid()


def test_charfield_limits():
    charfield = fields.CharField(min_length=3, max_length=6)
    charfield.set_value('abc')
    charfield.clean()
    assert charfield.is_valid()

    charfield.set_value('abcdef')
    charfield.clean()
    assert charfield.is_valid()

    charfield.set_value('ab')
    charfield.clean()
    assert not charfield.is_valid()

    charfield.set_value('abcdefg')
    charfield.clean()
    assert not charfield.is_valid()


def test_integerfield():
    integerfield = fields.IntegerField()
    integerfield.clean()
    assert integerfield.is_valid()

    integerfield.set_value(4.2)
    value = integerfield.clean()
    assert integerfield.is_valid()
    assert value == 4

    integerfield.set_value('3.14')
    value = integerfield.clean()
    assert integerfield.is_valid()
    assert value == 3

    integerfield.set_value('aimpim')
    value = integerfield.clean()
    assert not integerfield.is_valid()


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


def test_integer_limits():
    num_limits(fields.IntegerField, 3, 6)


def test_floatfield():
    floatfield = fields.FloatField()
    floatfield.clean()
    assert floatfield.is_valid()

    floatfield.set_value(4.2)
    value = floatfield.clean()
    assert floatfield.is_valid()

    floatfield.set_value('3.14')
    value = floatfield.clean()
    assert floatfield.is_valid()
    assert value == 3.14

    floatfield.set_value('aimpim')
    value = floatfield.clean()
    assert not floatfield.is_valid()


def test_floatfield_limits():
    num_limits(fields.FloatField, 3.14, 42)
