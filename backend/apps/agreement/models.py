from django.db import models
from apps.user_func.client.models import Client
from apps.attachment.models import Attachment


class Agreement(models.Model):
    # nie można zaimportować ProductType bo występuje tzw. circular import
    client = models.ForeignKey(Client, db_column='id_client', on_delete=models.CASCADE)
    signature = models.CharField(max_length=100, db_column='signature', unique=True)
    attachments = models.ManyToManyField(Attachment, through='AgreementAttachment', blank=True)

    def __str__(self):
        return self.signature

    class Meta:
        db_table = "agreement"


class AgreementAttachment(models.Model):
    agreement = models.ForeignKey(Agreement, db_column='id_agreement', on_delete=models.CASCADE)
    attachment = models.ForeignKey(Attachment, db_column='id_attachment', on_delete=models.CASCADE)

    def __str__(self):
        return self.agreement

    class Meta:
        db_table = "agreement_attachment"