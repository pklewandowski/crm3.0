from django.forms import IntegerField, DecimalField, FloatField
from django.forms.widgets import Input
from django.forms.utils import ValidationError
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class PercentageInput(Input):
    """ A simple form input for a percentage """
    input_type = 'text'

    def _format_value(self, value):
        if value is None:
            return ''
        return str(value * 100)

    def render(self, name, value, attrs=None, renderer=None):
        value = self._format_value(value)
        return super(PercentageInput, self).render(name, value, attrs)

    # def _has_changed(self, initial, data):
    #     return super(PercentageInput, self)._has_changed(self._format_value(initial), data)


def is_float(s):
    if s is None:
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


class PercentageField(DecimalField):
    """ A field that gets a value between 0 and 1 and displays as a value between 0 and 100"""
    # widget = PercentageInput(attrs={"class": "percentInput", "size": 4})
    widget = Input(attrs={"class": "percentInput"})

    default_error_messages = {
        'positive': _('Wartość musi być >= 0'),
    }

    # def has_changed(self, initial, data):
    #     dt = data.replace(',', '.')
    #     if not is_float(initial) or not is_float(dt):
    #         return True
    #     print(round(Decimal(initial) * 100, 4), round(Decimal(dt), 4), round(Decimal(initial) * 100, 4) != round(Decimal(dt), 4))
    #
    #     # changed = round(Decimal(initial) * 100, 4) != round(dt, 4)
    #
    #     print(type(initial))
    #     ch = super(PercentageField, self).has_changed(initial, data)
    #     print('initial, data, to_python data, changed?', initial, data, self.to_python(data.replace(',', '.')), ch)
    #
    #     return ch

    def validate(self, value):
        super(PercentageField, self).validate(value)

    def to_python(self, value):
        val = value.replace(',', '.').replace(' ', '')
        val = super(PercentageField, self).to_python(val)
        if is_float(val):
            return round(val / 100, 4)
        return val

    def prepare_value(self, value):
        val = super(PercentageField, self).prepare_value(value)
        if is_float(val) and not isinstance(val, str):
            return str(round((float(val) * 100), 2))
        return val

    def clean(self, value):
        """
        Validates that the input can be converted to a value between 0 and 1.
        Returns a Decimal
        """
        value = value.replace(' ', '').replace(',', '.')
        value = super(PercentageField, self).clean(value)

        if value is None:
            return None
        if value < 0:
            raise ValidationError(self.error_messages['positive'])
        return value

    def __str__(self):
        return 'PercentageField'

#
#
# class PercentageField(FloatField):
#     def to_python(self, value):
#         val = super(PercentageField, self).to_python(value)
#         if is_float(val):
#             return val / 100
#         return val
#
#     def prepare_value(self, value):
#         val = super(PercentageField, self).prepare_value(value)
#         if is_float(val) and not isinstance(val, str):
#             return str((float(val) * 100))
#         return val
