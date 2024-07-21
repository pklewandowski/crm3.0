import os

from django.conf import settings
from django.core.management import BaseCommand

from apps.attachment.models import Attachment
from apps.document.models import DocumentAttachment, Document


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for i in DocumentAttachment.objects.filter(attachment__file_path='document/attachments/'):
            i.attachment.file_path = 'document/attachments/%s/' % i.document.pk
            i.attachment.save()

