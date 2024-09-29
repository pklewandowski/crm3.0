from rest_framework import serializers

from apps.document.models import DocumentTypeAccountingType
from apps.product.models import ProductCalculation, ProductCashFlow, Product, ProductSchedule, ProductInterest, ProductTypeStatus, ProductInterestGlobal


class ProductTypeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTypeStatus
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    status = ProductTypeStatusSerializer()

    class Meta:
        model = Product
        fields = '__all__'


class ProductScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSchedule
        fields = '__all__'


class ProductInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductInterest
        fields = '__all__'


class ProductCalculationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCalculation
        fields = '__all__'


class ProductCashFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCashFlow
        exclude = ('product',)
        depth = 1


class DocumentTypeAccountingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTypeAccountingType
        fields = '__all__'


class ProductInterestGlobalSerializer(serializers.ModelSerializer):

    def create(self, data):
        data['created_by'] = self.context['user']
        return ProductInterestGlobal.objects.create(**data)

    class Meta:
        model = ProductInterestGlobal
        exclude = 'created_by',
