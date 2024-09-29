from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from apps.address.models import Address
from apps.hierarchy.models import Hierarchy


class MeetingRoomAttribute(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=10, null=True, blank=True)
    code = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "meeting_room_attribute"


class MeetingRoomRoomAttribute(models.Model):
    meeting_room = models.ForeignKey('MeetingRoom', db_column='id_room', on_delete=models.CASCADE)
    meeting_room_attribute = models.ForeignKey(MeetingRoomAttribute, db_column='id_attribute', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.pk)

    class Meta:
        db_table = "meeting_room_room_attribute"


class MeetingRoom(models.Model):
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.CASCADE)
    headquarter = models.ForeignKey(Hierarchy, db_column='id_headquarter', verbose_name=_('meeting_room.hierarchy'), null=True, blank=True, on_delete=models.SET_NULL)
    is_local = models.BooleanField(default=True)
    name = models.CharField(max_length=200)
    seats = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    max_seats = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    av_hour_from = models.TimeField(null=True, blank=True)
    av_hour_to = models.TimeField(null=True, blank=True)
    # Maksymalna liczba zdarzeń ciągłych po któej musi nastąpić przerwa min_break określona w minutach
    # Liczba zdarzeń ciągłych to liczba zdarzeń odległych od siebie o wartość < min_break
    max_continous_events = models.PositiveIntegerField(verbose_name=_('meeting_room.max_continous_events'), null=True, blank=True)
    # Minimalna przerwa po max_continous_events. Jeśli ustawione, to pobranie max_continous_events ostatnich zdarzeń dla sali i sprawdzenie, czy
    # spełniony jest warunek minimalnej przerwy
    min_break = models.PositiveIntegerField(verbose_name=_('meeting_room.min_break'), null=True, blank=True)
    color = models.CharField(verbose_name=_('meeting_room.color'), max_length=7, null=True, blank=True)
    attributes = models.ManyToManyField(MeetingRoomAttribute, through=MeetingRoomRoomAttribute, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "meeting_room"
