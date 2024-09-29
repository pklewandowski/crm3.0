from django.utils.translation import gettext_lazy as _
from django.db import models


class LogUserAction(models.Model):
    username = models.CharField(verbose_name=_('user.action.log.username'), max_length=200, null=True)
    user_id = models.IntegerField(null=True, blank=True)
    action_type = models.CharField(verbose_name=_('user.action.log.action_type'), max_length=20)
    request_path = models.CharField(verbose_name=_('user.action.log.request_path'), max_length=500)
    url_name = models.CharField(verbose_name=_('user.action.log.url_name'), max_length=200)
    parameter_list = models.CharField(verbose_name=_('user.action.log.parameter_list'), max_length=500)
    date_created = models.DateTimeField(verbose_name=_('user.action.log.date_created'))

    class Meta:
        db_table = 'log_user_action'
