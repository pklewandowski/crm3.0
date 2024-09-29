from itertools import chain
from django import forms

from django.forms.widgets import CheckboxInput

# from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe


class MultiCheckboxRenderedList(forms.models.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj


class MultiCheckboxRenderedListWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs)
        output = []
        # Normalize to strings
        checkbox_array = []
        str_values = set([str(v) for v in value])

        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: str(value) in str_values)
            option_value = option_value
            rendered_cb = cb.render(name, option_value)
            option_label2 = conditional_escape(option_label)

            output.append(u'<tr><td><i class="fa fa-arrows-v sortable-handle" aria-hidden="true"></i></td><td>%s</td><td>%s</td></tr>' % (rendered_cb, option_label2))

        return mark_safe(u'\n'.join(output))

# class MultiCheckboxRenderedListWidget(forms.CheckboxSelectMultiple):
# def render(self, name, value, attrs=None, choices=()):
#         if value is None: value = []
#         has_id = attrs and 'id' in attrs
#         final_attrs = self.build_attrs(attrs)
#         output = [u'<ul>']
#         # Normalize to strings
#         str_values = set([v for v in value])
#         for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
#             # If an ID attribute was given, add a numeric index as a suffix,
#             # so that the checkboxes don't all have the same ID attribute.
#             if has_id:
#                 final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
#                 label_for = u' for="%s"' % final_attrs['id']
#             else:
#                 label_for = ''
#
#             print(value)
#             print(option_value)
#
#             cb = CheckboxInput(final_attrs, check_test=lambda value: str(option_value) in value)
#             option_value = option_value
#             rendered_cb = cb.render(name, option_value)
#             option_label2 = conditional_escape(option_label)
#             output.append(u'<li><label%s>%s %s %d</label></li>' % (label_for, rendered_cb, option_label2,0))
#         output.append(u'</ul>')
#         return mark_safe(u'\n'.join(output))

# class TestForm(forms.ModelForm):
# groups = CustomZever(Group.objects.all(), widget=MultiCheckboxRenderedListWidget())
#
# class Meta:
#         model = User
#         fields = ['groups']
#
#
# def test(request):
#     return render_to_response('ambassador-tools/test.html', {'form': TestForm()})
