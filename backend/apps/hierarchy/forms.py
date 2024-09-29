from .models import Hierarchy
from py3ws.forms import p3form
from django import forms
from django.contrib.auth.models import Group


class HierarchyForm(p3form.ModelForm):
    HIERARCHY_CHOICES = [
        ('CMP', 'Firma / spółka zależna'),
        ('HDQ', 'Oddział'),
        ('DEP', 'Departament'),
        ('POS', 'Stanowisko')
    ]
    type = forms.ChoiceField(choices=HIERARCHY_CHOICES)
    group = forms.ModelMultipleChoiceField(queryset=Group.objects.all().order_by('name'), widget=forms.CheckboxSelectMultiple())

    class Meta:
        model = Hierarchy
        fields = ['id', 'name', 'description', 'parent', 'group', 'type']
