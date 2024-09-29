from django.db import models

from apps.document.models import DocumentType
from apps.user.models import User


class Contractor(models.Model):
    user = models.OneToOneField(User, primary_key=True, db_column='id', related_name='contractor_set', on_delete=models.CASCADE)
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', on_delete=models.CASCADE)

    def __str__(self):
        return (self.user.first_name or '') + ' ' + (self.user.last_name or '')

    class Meta:
        db_table = "user_contractor"
