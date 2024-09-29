from django.utils.translation import gettext_lazy as _
from django.db import models
from apps.user.models import User
from apps.user_func.adviser.models import Adviser
from apps.document.models import DocumentType


class Broker(models.Model):
    user = models.OneToOneField(User, primary_key=True, db_column='id', related_name='broker_set', on_delete=models.CASCADE)
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', on_delete=models.CASCADE)
    adviser = models.ForeignKey(Adviser, verbose_name=_('broker.adviser'), db_column='id_adviser', related_name='broker_set', on_delete=models.CASCADE, null=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    multi = models.BooleanField(default=False)

    def __str__(self):
        return (self.user.first_name or '') + ' ' + (self.user.last_name or '')

    class Meta:
        db_table = "user_broker"
        permissions = (
            ('view:all', _('permissions.app.broker.view.all')),
            ('view:own', _('permissions.app.broker.view.own')),
            ('list:all', _('permissions.app.broker.list.all')),
            ('list:own', _('permissions.app.broker.list.own')),
        )
