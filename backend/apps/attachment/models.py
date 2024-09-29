from django.db import models


class Attachment(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True)
    type = models.CharField(max_length=50, default='file')
    description = models.TextField(null=True, blank=True)
    file_path = models.CharField(max_length=300)
    file_name = models.CharField(max_length=300)
    file_original_name = models.CharField(max_length=300)
    file_ext = models.CharField(max_length=10)
    file_mime_type = models.CharField(max_length=200)
    file_size = models.DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by_username = models.CharField(max_length=300)
    update_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'attachment'

    def __str__(self):
        return self.file_original_name

    @staticmethod
    def create(
            attachment_type,
            file_path,
            file_name,
            file_original_name,
            file_ext,
            file_mime_type,
            created_by_username,
            name=None,
            description=None,
            file_size=None
    ):
        return Attachment.objects.create(
            name=name,
            type=attachment_type,
            description=description,
            file_path=file_path,
            file_name=file_name,
            file_original_name=file_original_name,
            file_ext=file_ext,
            file_mime_type=file_mime_type,
            file_size=file_size,
            created_by_username=created_by_username
        )
