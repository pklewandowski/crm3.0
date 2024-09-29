from rest_framework import serializers

from apps.attachment.models import Attachment
from apps.attachment.utils import get_mime_type


class AttachmentSerializer(serializers.ModelSerializer):
    mime = serializers.SerializerMethodField('get_mime')

    def get_mime(self, obj):
        return get_mime_type(obj.file_ext)

    class Meta:
        model = Attachment
        fields = '__all__'
