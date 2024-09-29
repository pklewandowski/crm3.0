from rest_framework import serializers

from apps.address.models import Address
from apps.user.models import User


class HistoryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class AddressHistorySerializer(serializers.ModelSerializer):
    history_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    history_user = HistoryUserSerializer()

    class Meta:
        model = Address.history.model
        fields = '__all__'
