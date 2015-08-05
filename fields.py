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
