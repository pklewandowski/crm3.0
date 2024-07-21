from django.utils.translation import gettext_lazy as _
from django import forms
from .models import MeetingRoom, MeetingRoomAttribute
from py3ws.forms import p3form


class MeetingRoomForm(p3form.ModelForm):
    class Meta:
        model = MeetingRoom
        fields = ['is_local', 'name', 'seats', 'max_seats', 'av_hour_from', 'av_hour_to', 'color', 'max_continous_events', 'min_break']
        labels = {
            "is_local": _("meeting_room.form.label.is_local"),
            "name": _("meeting_room.form.label.name"),
            "seats": _("meeting_room.form.label.seats"),
            "max_seats": _("meeting_room.form.label.max_seats"),
            "av_hour_from": _("meeting_room.form.label.av_hour_from"),
            "av_hour_to": _("meeting_room.form.label.av_hour_to")
        }
        # widgets = {
        #     "max_seats": forms.TextInput
        # }


class MeetingRoomAttributeForm(p3form.ModelForm):
    class Meta:
        model = MeetingRoomAttribute
        fields = ['name', 'description']
        labels = {
            "name": _("meeting_room_attribute.form.label.name"),
            "description": _("meeting_room_attribute.form.label.description"),
        }
