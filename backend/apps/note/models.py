from django.db import models
from django.utils.translation import gettext_lazy as _

from application.models import AuditMixin


class Note(AuditMixin):
    PRIORITIES = [(_('high_priority'), 'HIGH'), (_('normal_priority'), 'NORMAL'), (_('low_priority'), 'LOW')]
    DEFAULT_PRIORITY = 'NORMAL'

    header = models.CharField(max_length=200, null=True, blank=True, verbose_name=_('note.header'))
    text = models.TextField(verbose_name=_('note.text'))
    importance = models.CharField(max_length=50, choices=PRIORITIES, default=DEFAULT_PRIORITY)


    class Meta:
        db_table = 'note'
