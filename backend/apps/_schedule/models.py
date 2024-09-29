from django.utils.translation import gettext_lazy as _
from django.db import models

from apps.document.models import DocumentType
from apps.meeting_room.models import MeetingRoom
from apps.address.models import Address
from apps.message.models import MessageTemplate
from apps.user.models import User
from simple_history.models import HistoricalRecords


class Schedule(models.Model):
    type = models.ForeignKey('ScheduleType', db_column="id_type", on_delete=models.CASCADE)
    host_user = models.ForeignKey(User, verbose_name=_('schedule.host_user'), db_column="id_host_user", related_name='host_user', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, db_column="id_created_by", related_name='created_by', on_delete=models.CASCADE)
    custom_location_address = models.ForeignKey(Address, db_column="id_custom_loc_address", null=True, blank=True, on_delete=models.CASCADE)
    meeting_room = models.ForeignKey(MeetingRoom, verbose_name=_('schedule.meeting_room'), db_column='id_meeting_room', null=True, blank=True,
                                     related_name="meeting_room", on_delete=models.CASCADE)
    service = models.ForeignKey(DocumentType, db_column='id_service', null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(verbose_name=_('schedule.title'), max_length=200)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(verbose_name=_('schedule.start_date'), db_index=True)
    end_date = models.DateTimeField(verbose_name=_('schedule.end_date'))
    participant_confirmed = models.BooleanField(verbose_name=_('schedule.participant_confirmed'), default=False)
    superior_confirmed = models.BooleanField(verbose_name=_('schedule.superior_confirmed'), default=False)
    superior_confirmed_by = models.ForeignKey(User, db_column='id_superior_confirmed_by', null=True, blank=True, on_delete=models.CASCADE)
    host_user_confirmed = models.BooleanField(verbose_name=_('schedule.host_user_confirmed'), default=False)
    invited_users = models.ManyToManyField(User, through='ScheduleUser', blank=True, related_name="invited")
    status = models.CharField(verbose_name=_('schedule.status'), max_length=200, default='NW', blank=True)
    history = HistoricalRecords(verbose_name=_('schedule.history'), table_name='h_schedule')

    def __str__(self):
        return self.title

    class Meta:
        db_table = "schedule"
        default_permissions = ()
        permissions = (
            ('add_schedule', _('schedule.permissions.add_schedule')),
            ('list_schedule', _('schedule.permissions.list_schedule')),
            ('view_schedule', _('schedule.permissions.view_schedule')),
            ('change_schedule', _('schedule.permissions.change_schedule')),
            ('close_schedule', _('schedule.permissions.close_schedule')),
            ('cancel_schedule', _('schedule.permissions.cancel_schedule')),
            ('delete_schedule', _('schedule.permissions.delete_schedule')),
            ('add_all_schedule', _('schedule.permissions.add_all_schedule')),
            ('list_all_schedule', _('schedule.permissions.list_all_schedule')),
            ('view_all_schedule', _('schedule.permissions.view_all_schedule')),
            ('change_all_schedule', _('schedule.permissions.change_all_schedule')),
            ('close_all_schedule', _('schedule.permissions.close_all_schedule')),
            ('cancel_all_schedule', _('schedule.permissions.cancel_all_schedule')),
            ('delete_all_schedule', _('schedule.permissions.delete_all_schedule')),
        )


class ScheduleType(models.Model):
    name = models.CharField(verbose_name=_('schedule.type.name'), max_length=200)
    description = models.TextField(verbose_name=_('schedule.type.description'), null=True, blank=True)
    work_break = models.BooleanField(verbose_name=_('schedule.type.work_break'), default=False)

    superior_confirmation = models.BooleanField(verbose_name=_('schedule.type.superior_confirmation'), default=False)
    participant_confirmation = models.BooleanField(verbose_name=_('schedule.type.participant_confirmation'), default=False)
    host_user_confirmation = models.BooleanField(verbose_name=_('schedule.type.host_user_confirmation'), default=False)
    host_user_editable = models.BooleanField(verbose_name=_('schedule.type.host_user_editable'), default=True)

    location_required = models.BooleanField(verbose_name=_('schedule.type.location_required'), blank=True, default=False)
    title_required = models.BooleanField(verbose_name=_('schedule.type.title_required'), blank=True, default=False)

    single_person = models.BooleanField(verbose_name=_('schedule.type.single_person'), default=False)
    whole_day_event = models.BooleanField(verbose_name=_('schedule.type.whole_day_event'), default=False)
    auto_close = models.BooleanField(verbose_name=_('schedule.type.auto_close'), default=False)

    min_time = models.PositiveIntegerField(verbose_name=_('schedule.type.min_time'), null=True, blank=True)
    max_time = models.PositiveIntegerField(verbose_name=_('schedule.type.max_time'), null=True, blank=True)
    # Minimalna przerwa dla właściciela spotkania. Podczas zatwierdzania zdarzenia Wybór ostatniego odbytego zdarzenia
    # W przypadku, gdy zdarzenie występuje i posiada poniższy argument ustawiony to kontrola, czy jest on spełniony
    # Czas przerwy podany w minutach
    min_host_break = models.PositiveIntegerField(verbose_name=_('schedule.type.min_host_break'), null=True, blank=True)
    # To samo dla uczestnika spotkania
    min_participant_break = models.IntegerField(verbose_name=_('schedule.type.min_participant_break'), null=True, blank=True)

    event_kind = models.CharField(verbose_name=_('schedule.type.event_kind'), max_length=3, default='E')
    cyclic = models.BooleanField(verbose_name=_('schedule.type.cyclic'), default=False)
    default_title = models.CharField(verbose_name=_('schedule.type.default_title'), max_length=200, null=True, blank=True)
    color = models.CharField(verbose_name=_('schedule.type.color'), max_length=7, null=True, blank=True)
    sq = models.IntegerField(default=0)
    exclusive_participant_mode = models.BooleanField(verbose_name=_('schedule.type.exclusive_participant_mode'), default=False)
    is_default_event = models.BooleanField(default=False)
    send_message = models.BooleanField(verbose_name=_('schedule.type.send_message'), default=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "schedule_type"


class ScheduleTypeReminder(models.Model):
    unit_number = models.CharField(verbose_name='schedule.type.reminder.unit_number', max_length=5)
    unit_type = models.CharField(verbose_name='schedule.type.reminder.unit_type', max_length=3)
    type = models.CharField(verbose_name='schedule.type.reminder.type', max_length=3)  # mail telefon

    class Meta:
        db_table = 'schedule_type_reminder'


class ScheduleUser(models.Model):
    schedule = models.ForeignKey(Schedule, db_column="id_schedule", related_name="membership", on_delete=models.CASCADE)
    user = models.ForeignKey(User, db_column="id_user", related_name='user_set', on_delete=models.CASCADE)
    confirmed = models.BooleanField(default=False)
    participant_type = models.CharField(max_length=1)
    exclusive_participant_mode = models.BooleanField(default=False)
    token = models.CharField(verbose_name=_('schedule.user.token'), max_length=500, null=True, blank=True)
    token_valid = models.BooleanField(verbose_name=_('schedule.user.token_valid'), default=False)
    history = HistoricalRecords(verbose_name=_('schedule.history'), table_name='h_schedule_user')

    def __str__(self):
        return str(self.user.id) + '_' + str(self.schedule.id)

    class Meta:
        db_table = "schedule_user"


class ScheduleMessage(models.Model):
    schedule = models.ForeignKey(Schedule, db_column='id_schedule', related_name='message_set', on_delete=models.CASCADE)
    user = models.ForeignKey(User, db_column='id_user', on_delete=models.CASCADE)
    created_date = models.DateTimeField(verbose_name='schedule.message.date_created')

    text = models.TextField(verbose_name='schedule.message.text')

    class Meta:
        db_table = 'schedule_message'


