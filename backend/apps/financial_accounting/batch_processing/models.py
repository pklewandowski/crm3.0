from django.utils.translation import gettext_lazy as _
from django.db import models


class File(models.Model):
    type = models.CharField(max_length=100)
    name = models.CharField(max_length=300)
    records = models.IntegerField(default=-1)
    load_date = models.DateTimeField(auto_now_add=True)
    subsidiary_company_code = models.CharField(max_length=30)

    class Meta:
        db_table = 'fa_file'
        unique_together = ('name', 'subsidiary_company_code')
