# coding: utf-8
import fields


def make_field(type, **kwargs):
    Field = fields.fields.get_field(type)
    return Field(**kwargs)
