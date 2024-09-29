from django import forms
from py3ws.forms import utils
from django.db import models


class LvTxt(forms.CharField):
    def __init__(self, dictname=None, multi=False, *args, **kwargs):
        self.multi = multi
        self.dictname = dictname
        if dictname:
            self.choices = utils.get_dictionary_entries(dictname, 'pk')
        else:
            self.choices = None
        super(LvTxt, self).__init__(*args, **kwargs)
        if 'class' not in self.widget.attrs:
            self.widget.attrs['class'] = 'lvm-txt-json'
        else:
            self.widget.attrs['class'] += ' lvm-txt-json'


class DictChoiceField(forms.ChoiceField):
    def __init__(self, dictname=None, *args, **kwargs):
        self.dictname = dictname
        super(DictChoiceField, self).__init__(*args, **kwargs)
        if dictname:
            self.choices = utils.get_dictionary_entries(dictname=dictname)


class CalendarDateTimeField(forms.CharField):
    pass


# class ColorField(forms.CharField):
#     def __init__(self, *args, **kwargs):
#         kwargs['max_length'] = 10
#         super(ColorField, self).__init__(*args, **kwargs)
#
#     def formfield(self, **kwargs):
#         kwargs['widget'] = ColorWidget
#         return super(ColorField, self).formfield(**kwargs)



# class PercentField(forms.FloatField):
#     def to_python(self, value):
#         val = super(PercentField, self).to_python(value)
#         if is_float(val):
#             return val / 100
#         return val
#
#     def prepare_value(self, value):
#         val = super(PercentField, self).prepare_value(value)
#         if is_float(val) and not isinstance(val, str):
#             return str((float(val) * 100))
#         return val
