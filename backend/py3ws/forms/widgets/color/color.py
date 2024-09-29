from django.forms.widgets import TextInput


class ColorInput(TextInput):
    input_type = 'color'
