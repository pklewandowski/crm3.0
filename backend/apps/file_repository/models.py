from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class FileRepository(models.Model):
    name = models.CharField(verbose_name=_('report.template.repo.name'), max_length=200)
    filename = models.CharField(verbose_name=_('report.template.repo.filename'), max_length=500, unique=True, blank=True)
    original_filename = models.CharField(verbose_name=_('report.template.repo.original_filename'), max_length=500, blank=True)
    mimetype = models.CharField(verbose_name=_('report.template.repo.mimetype'), max_length=100, blank=True)
    description = models.TextField(verbose_name=_('report.template.repo.description'), null=True, blank=True)
    creation_date = models.DateTimeField(verbose_name=_('report.template.repo.creation_date'), auto_now_add=True)
    created_by = models.CharField(max_length=200, verbose_name=_('report.template.repo.created_by'), blank=True)
    version = models.IntegerField(verbose_name=_('report.template.repo.created_by'), default=1)
    history = HistoricalRecords(table_name='h_file_repository')

    class Meta:
        db_table = 'file_repository'


