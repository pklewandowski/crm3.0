from rest_framework import serializers

from apps.document.models import DocumentTypeAccountingType
from apps.product.models import ProductCalculation, ProductCashFlow, Product, ProductSchedule, ProductInterest, \
    ProductTypeStatus, ProductInterestGlobal


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


class ProductCalculationBalanceSerializer(serializers.ModelSerializer):
    product_start_date = serializers.DateField()
    cost_aggregation = serializers.SerializerMethodField()
    interest_for_delay_date = serializers.SerializerMethodField()
    interest_for_delay_max_date = serializers.SerializerMethodField()
    interest_nominal_end_date = serializers.SerializerMethodField()
    capital_total = serializers.SerializerMethodField()
    current_liabilities = serializers.SerializerMethodField()

    def get_product_start_date(self, obj):
        return obj.product_start_date

    def get_cost_aggregation(self, obj):
        return obj.cost_aggregation

    def get_interest_for_delay_date(self, obj):
        return obj.interest_for_delay_date

    def get_interest_for_delay_max_date(self, obj):
        return obj.interest_for_delay_max_date

    def get_interest_nominal_end_date(self, obj):
        return obj.interest_nominal_end_date

    def get_capital_total(self, obj):
        return obj.capital_total

    def get_current_liabilities(self, obj):
        return obj.current_liabilities

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
