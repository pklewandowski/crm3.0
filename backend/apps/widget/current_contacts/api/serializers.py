from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.user.api.serializers import UserSerializer
from apps.user_func.client.models import Client


class ClientSerializerForCurrentContacts(ModelSerializer):
    user = UserSerializer()
    date_diff = serializers.IntegerField()
    max_event_date = serializers.DateTimeField()


    class Meta:
        model = Client
        fields = 'user', 'date_diff', 'max_event_date'

