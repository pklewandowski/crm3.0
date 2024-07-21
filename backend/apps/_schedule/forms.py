import datetime
import pprint
from django.db.models import Q
from django.forms import modelformset_factory
from django.utils.translation import gettext_lazy as _
from django import forms
from django.forms.forms import NON_FIELD_ERRORS
from django.conf import settings

from apps.document.models import DocumentType, DocumentTypeCategory
from apps.user_func.adviser.models import Adviser
from apps.user_func.employee.models import Employee
from apps.user.models import User

from py3ws.forms.widgets.color.color import ColorInput
from .models import Schedule, ScheduleType, ScheduleUser, ScheduleMessage
from apps.meeting_room.models import MeetingRoom
from py3ws.forms import p3form, fields
from py3ws.utils import utils as py3ws_utils
from apps.user_func.client.models import Client


class ScheduleForm(p3form.ModelForm):
    mode = forms.CharField(max_length=20, widget=forms.HiddenInput())
    employee_ = forms.CharField(label=_('schedule.form.employee'), required=False, widget=forms.Select())
    client_ = forms.CharField(required=False, label=_('schedule.form.client'), widget=forms.Select())
    host_user_ = forms.CharField(required=True, label=_('schedule.host_user'), widget=forms.Select())
    single_person_ = forms.CharField(required=False, label=_('schedule.single_person'), widget=forms.Select())
    type = forms.ModelChoiceField(queryset=ScheduleType.objects.all().order_by('sq'), widget=forms.Select, empty_label=None, required=True)
    meeting_room = forms.ModelChoiceField(queryset=MeetingRoom.objects.all().order_by('name'), widget=forms.RadioSelect, empty_label=None, required=False)
    service = forms.ModelChoiceField(queryset=DocumentType.objects.filter(category=DocumentTypeCategory.objects.get(code='US')).order_by('name'),
                                     empty_label='----', required=False)

    def __init__(self, *args, **kwargs):
        super(ScheduleForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] += ' description-field'
        self.fields['host_user_'].widget.attrs['class'] += ' schedule-select2'
        self.fields['single_person_'].widget.attrs['class'] += ' schedule-select2'
        self.fields['employee_'].widget.attrs['class'] += ' schedule-select2'
        self.fields['client_'].widget.attrs['class'] += ' schedule-select2'

    def is_valid(self):
        mode = self.data[self.prefix + '-mode']
        if mode == 'basic':
            self.fields['employee_'].required = True
            self.fields['client_'].required = True

        valid = super(ScheduleForm, self).is_valid()
        return valid

    class Meta:
        model = Schedule
        fields = ['type', 'title', 'description', 'start_date', 'end_date', 'meeting_room']


class ScheduleTypeForm(p3form.ModelForm):
    event_kind = forms.ChoiceField(choices=[('E', 'Zdarzenie'), ('T', 'Zadanie'), ('U', 'Usługa'), ], label=_('schedule.type.event_kind'))

    class Meta:
        model = ScheduleType
        fields = [
            'name', 'description', 'work_break', 'superior_confirmation', 'participant_confirmation', 'host_user_confirmation',
            'host_user_editable', 'event_kind', 'whole_day_event', 'location_required', 'title_required', 'single_person',
            'default_title', 'color', 'min_time', 'max_time', 'min_host_break', 'send_message'
        ]
        widgets = {'color': ColorInput}


class ScheduleUserForm(p3form.ModelForm):
    class Meta:
        model = ScheduleUser
        fields = '__all__'


ScheduleUserFormset = modelformset_factory(model=ScheduleUserForm.Meta.model, form=ScheduleUserForm, extra=0, can_delete=True)

class ScheduleMessageForm(p3form.ModelForm):
    text = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control input-sm'}))

    class Meta:
        model = ScheduleMessage
        fields = ('text',)


class Select2(forms.ModelChoiceField):
    pass


class CalendarDateTimeField(forms.DateTimeField):
    pass


class ScheduleFilterForm(p3form.Form):
    duration_choices = [
        (15, '0:15'),
        (30, '0:30'),
        (45, '0:45'),
        (60, '1:00'),
        (75, '1:15'),
        (90, '1:30'),
        (105, '1:45'),
        (120, '2:00'),
        (150, '2:30'),
        (180, '3:00'),
        (240, '4:00'),
        (300, '5:00'),
        (360, '6:00'),
        (420, '7:00'),
        (480, '8:00'),
    ]
    # user_q = Q(pk__in=Adviser.objects.all().values('pk'))
    employee = forms.CharField(required=False, label=_('schedule.filter.form.employee'), widget=forms.SelectMultiple())
    user = forms.MultipleChoiceField(required=False, label=_('schedule.filter.form.host_user'), widget=forms.SelectMultiple())
    meeting_room = forms.ModelChoiceField(queryset=MeetingRoom.objects.all().order_by('name'), required=False, label=_('schedule.filter.form.meeting_room'))
    from_date = forms.DateField(required=False, label=_('schedule.filter.form.from_date'))
    from_hour = forms.TimeField(required=False, label=_('schedule.filter.form.from_hour'))
    to_hour = forms.TimeField(required=False, label=_('schedule.filter.form.to_hour'))
    min_duration = forms.ChoiceField(choices=duration_choices, required=False, label=_('schedule.filter.form.min_duration'))

    def __init__(self, *args, **kwargs):
        super(ScheduleFilterForm, self).__init__(*args, **kwargs)
        self.fields['from_date'].widget.attrs['placeholder'] = datetime.date.strftime(datetime.date.today(), '%Y-%m-%d')
        self.fields['from_hour'].widget.attrs['placeholder'] = datetime.time.strftime(settings.SCHEDULE_WORKING_HOURS['start'], '%H:%M')
        self.fields['to_hour'].widget.attrs['placeholder'] = datetime.time.strftime(settings.SCHEDULE_WORKING_HOURS['end'], '%H:%M')
        self.fields['employee'].widget.attrs['class'] += ' select2'
        self.fields['employee'].widget.attrs['data-width'] = '100%'  # ze względu na kontrolkę select2
        self.fields['user'].widget.attrs['class'] += ' select2'
        self.fields['user'].widget.attrs['data-width'] = '100%'

    class Meta:
        fields = '__all__'

