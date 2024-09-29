import datetime

from django.db.models import JSONField
from django.db import models
from django.utils import timezone

from apps.user.models import User


class NotificationTemplate(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, null=True, blank=True)
    text = models.TextField()
    params = JSONField(null=True, blank=True)

    class Meta:
        db_table = 'notification_template'


class Notification(models.Model):
    # Nie zawsze alert będzie na podstawie template-a
    template = models.ForeignKey(to=NotificationTemplate, db_column='id_template', null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=20, default='INFO')
    users = models.ManyToManyField(User, through='NotificationUser')
    creation_date = models.DateTimeField(auto_now_add=True)
    effective_date = models.DateField(default=timezone.now)

    class Meta:
        db_table = 'notification'
        ordering = ('-effective_date',)


class NotificationUser(models.Model):
    priorities = [('STD', 'standard'), ('URG', 'urgent'), ('INFO', 'info')]
    notification = models.ForeignKey(to=Notification, db_column='id_notification', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, db_column='id_user', related_name='notification_user_set', on_delete=models.CASCADE, db_index=True)
    # NW - nowy, RD - przeczytany, CL - usunięty
    status = models.CharField(max_length=10)
    priority = models.CharField(max_length=10, default='STD')
    close_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notification_user'
        ordering = ('-notification__creation_date', '-notification__pk')
