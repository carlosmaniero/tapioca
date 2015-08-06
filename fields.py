import re


class ValidationException(Exception):
    def __init__(self, message, *args, **kwargs):
        self.message = message


class Field(object):
    def __init__(self, required=False, messages={}):
        self.required = required
        self.value = None
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
    def clean(self):
        if self.value is not None:
            try:
                self.value = float(self.value)
            except ValueError:
                self.error = self.messages.get('not_num', 'This isn\'t a num')
                return self.value

        return super(IntegerField, self).clean()


class BooleanField(Field):
    def __init__(self, *args, **kwargs):
        if 'required' in kwargs:
            kwargs.pop('required')
        super(BooleanField, self).__init__(required=True, *args, **kwargs)
        self.value = False

    def set_value(self, value):
        self.value = bool(value)


class ChoiceField(Field):
    def __init__(self, choices, *args, **kwargs):
        self.choices = choices
        super(ChoiceField, self).__init__(*args, **kwargs)

    def clean_choice(self):
        if self.value is not None:
            if self.value not in self.choices:
                raise ValidationException(
                    self.messages.get('choice', '{} isn\'t a valid option.')
                )


class RegexField(CharField):
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
    REGEX = "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    def __init__(self, *args, **kwargs):
        super(EmailField, self).__init__(self.REGEX, *args, **kwargs)


class UrlField(RegexField):
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
