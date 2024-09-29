from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DocumentConfig(AppConfig):
    name = 'apps.document'
    verbose_name = _('Dokument')
    verbose_name_plural = _('Dokumenty')
