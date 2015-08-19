import re
from datetime import datetime


class FieldRegister(object):
    fields = {}

    def register(self, field_class):
        self.fields[field_class.type] = field_class

    def get_field(self, name):
        return self.fields[name]

fields = FieldRegister()


class ValidationException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message


class Field(object):
    type = None

    def __init__(self, required=False, default=None, messages={}):
        self.required = required
        self.value = default
        self.error = None
        self.messages = messages

    def set_value(self, value):
        self.value = value

    def get_clean_methods(self):
        methods = []
        for attr in dir(self):
            if attr.startswith('clean_'):
                methods.append(getattr(self, attr))
        return methods

    def clean(self):
        self.error = None
        self.cleaned = []
        for method in self.get_clean_methods():
            try:
                self.value = method()
            except ValidationException as e:
                self.error = e.message
                break
        return self.value

    def clean_required(self):
        if self.required and self.value is None:
            raise ValidationException(
                self.messages.get('required', "This field is required")
            )
        return self.value

    def is_valid(self):
        return self.error is None


class CharField(Field):
    type = 'char'

    def __init__(self, min_length=None, max_length=None,
                 blank=True, *args, **kwargs):
        super(CharField, self).__init__(*args, **kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.blank = blank

    def clean(self):
        if self.value is not None:
            self.value = str(self.value).strip()

        return super(CharField, self).clean()

    def clean_min_length(self):
        if self.min_length is not None:
            if len(self.value) < self.min_length:
                raise ValidationException(
                    self.messages.get(
                        'min_length',
                        'At least {} characters'
                    ).format(self.min_length)
                )
        return self.value

    def clean_max_length(self):
        if self.max_length is not None:
            if len(self.value) > self.max_length:
                raise ValidationException(
                    self.messages.get(
                        'min_length',
                        'Maximum {} characters'
                    ).format(self.min_length)
                )
        return self.value

    def clean_blank(self):
        if self.value is None:
            return self.value

        if not self.blank and len(self.value) == 0:
            raise ValidationException(
                self.messages.get('blank', 'This field can\'t be empty')
            )
        return self.value


class IntegerField(Field):
    type = 'int'

    def __init__(self, min=None, max=None, *args, **kwargs):
        super(IntegerField, self).__init__(*args, **kwargs)
        self.min = min
        self.max = max

    def clean(self):
        if self.value is not None:
            try:
                if type(self.value) == str:
                    if '.' in self.value:
                        self.value = self.value.split('.')[0]
                self.value = int(self.value)
            except ValueError:
                self.error = self.messages.get('not_num', 'This isn\'t a num')
                return self.value

        return super(IntegerField, self).clean()

    def clean_min(self, *args, **kwargs):
        if self.value is not None and self.max:
            print(self.value)
            print(self.min)
            if self.value < self.min:
                raise ValidationException(
                    self.messages.get(
                        'min', 'The number must be greater than {}'.format(
                            self.min
                        )
                    )
                )
        return self.value

    def clean_max(self, *args, **kwargs):
        if self.value is not None and self.max:
            if self.value > self.max:
                raise ValidationException(
                    self.messages.get(
                        'min', 'The number must be less than {}'.format(
                            self.min
                        )
                    )
                )
        return self.value


class FloatField(IntegerField):
    type = 'float'

    def clean(self):
        if self.value is not None:
            try:
                self.value = float(self.value)
            except ValueError:
                self.error = self.messages.get('not_num', 'This isn\'t a num')
                return self.value

        return super(IntegerField, self).clean()


class BooleanField(Field):
    type = 'boolean'

    def __init__(self, *args, **kwargs):
        if 'required' in kwargs:
            kwargs.pop('required')
        super(BooleanField, self).__init__(required=True, *args, **kwargs)
        self.value = False

    def set_value(self, value):
        self.value = bool(value)


class ChoiceField(Field):
    type = 'choice'

    def __init__(self, choices, *args, **kwargs):
        self.choices = choices
        super(ChoiceField, self).__init__(*args, **kwargs)

    def clean_choice(self):
        if self.value is not None:
            if self.value not in self.choices:
                raise ValidationException(
                    self.messages.get('choice', '{} isn\'t a valid option.')
                )
        return self.value


class DateTimeField(Field):
    type = 'datetime'

    def __init__(self, format='%Y-%m-%d %H:%M:%S', *args, **kwargs):
        self.format = format
        super(DateTimeField, self).__init__(*args, **kwargs)

    def clean_datetime(self):
        if self.value is not None:
            if type(self.value) is not datetime:
                try:
                    self.value = datetime.strptime(self.value, self.format)
                except ValueError:
                    raise ValidationException(
                        self.messages.get('invalid_date', 'Invalid Datetime')
                    )
        return self.value


class DateField(DateTimeField):
    type = 'date'

    def __init__(self, format='%Y-%m-%d', *args, **kwargs):
        super(DateField, self).__init__(format, *args, **kwargs)


class RegexField(CharField):
    type = 'regex'

    def __init__(self, regex, *args, **kwargs):
        super(RegexField, self).__init__(*args, **kwargs)
        self.regex = regex

    def clean_regex(self):
        if self.value is not None:
            if re.match(self.regex, self.value) is None:
                raise ValidationException(
                    self.messages.get('regex', 'Regex error')
                )
        return self.value


class EmailField(RegexField):
    type = 'email'
    REGEX = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(self.REGEX, *args, **kwargs)


class UrlField(RegexField):
    type = 'url'

    # Django Fork
    # unicode letters range (must be a unicode string, not a raw string)
    ul = '\u00a1-\uffff'

    # IP patterns
    ipv4_re = r'(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)(?:\.(?:25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}'
    ipv6_re = r'\[[0-9a-f:\.]+\]'  # (simple regex, validated later)

    # Host patterns
    hostname_re = r'[a-z' + ul + r'0-9](?:[a-z' + ul + r'0-9-]*[a-z' + ul + r'0-9])?'
    domain_re = r'(?:\.(?!-)[a-z' + ul + r'0-9-]*(?<!-))*'
    tld_re = r'\.(?:[a-z' + ul + r']{2,}|xn--[a-z0-9]+)\.?'
    host_re = '(' + hostname_re + domain_re + tld_re + '|localhost)'

    REGEX = (r'^(?:[a-z0-9\.\-]*)://'  # scheme is validated separately
             r'(?:\S+(?::\S*)?@)?'  # user:pass authentication
             r'(?:' + ipv4_re + '|' + ipv6_re + '|' + host_re + ')'
             r'(?::\d{2,5})?'  # port
             r'(?:[/?#][^\s]*)?'  # resource path
             r'\Z')

    def __init__(self, *args, **kwargs):
        super(UrlField, self).__init__(self.REGEX, *args, **kwargs)


class ListField(Field):
    type = 'list'
    value = []
    fields = []
    array_errors = []

    def __init__(self, field, field_kwargs={}, empty=True, *args, **kwargs):
        self.field_class = fields.get_field(field)
        self.kwargs = field_kwargs
        super(ListField, self).__init__(*args, **kwargs)

    def set_value(self, data):
        self.value = data
        self.fields = []

        for value in data:
            field = self.field_class(**self.kwargs)
            field.set_value(value)
            self.fields.append(field)

    def clean_fields(self):
        self.array_errors = []
        i = 0
        for field in self.fields:
            self.value[i] = field.clean()
            i += 1

    def clean(self):
        value = super(ListField, self).clean()

        i = 0
        for field in self.fields:
            if not field.is_valid():
                self.array_errors.append({
                    'index': i,
                    'error': field.error
                })
            i += 1

        return value

    def is_valid(self):
        valid = super(ListField, self).is_valid()
        return valid and len(self.array_errors) == 0


fields.register(CharField)
fields.register(IntegerField)
fields.register(FloatField)
fields.register(BooleanField)
fields.register(ChoiceField)
fields.register(DateTimeField)
fields.register(DateField)
fields.register(RegexField)
fields.register(EmailField)
fields.register(UrlField)
fields.register(ListField)
