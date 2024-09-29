from rest_framework import serializers

from apps.file_repository.models import FileRepository


class FileRepositorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FileRepository
        fields = '__all__'
