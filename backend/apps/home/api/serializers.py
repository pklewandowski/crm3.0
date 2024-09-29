from rest_framework import serializers

from apps.document.models import Document
from apps.product.api.serializers import ProductSerializer


class DocumentSerializerForUserDetails(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Document
        fields = 'id', 'code', 'product', 'status', 'creation_date'
        depth = 1
