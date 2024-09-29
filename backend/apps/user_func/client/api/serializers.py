from rest_framework import serializers

from apps.user_func.client.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
