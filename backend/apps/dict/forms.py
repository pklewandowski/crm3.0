from django.utils.translation import gettext_lazy as _
from django.forms import ModelForm
from .models import DictionaryEntry


class DictionaryEntryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(DictionaryEntryForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control input-sm'

    class Meta:
        model = DictionaryEntry
        fields = 'label'
        labels = {'label': _("dictionary.entry.form.label.label")}
