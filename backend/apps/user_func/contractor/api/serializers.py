from rest_framework import serializers

from apps.user.api.serializers import UserSerializer
from apps.user_func.contractor.models import Contractor


class ContractorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Contractor
        fields = '__all__'
