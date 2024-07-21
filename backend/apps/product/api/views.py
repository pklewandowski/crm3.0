import traceback

from django.conf import settings
from django.db import transaction
from django.db.models import Sum, Q, Count
from rest_framework import status as http_status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.document.models import DocumentTypeAccountingType, DocumentTypeStatus, DocumentStatusCourse
from apps.product.api.serializers import ProductCalculationSerializer, ProductCashFlowSerializer, DocumentTypeAccountingTypeSerializer, ProductSerializer, ProductScheduleSerializer, \
    ProductInterestSerializer, ProductInterestGlobalSerializer
from apps.product.models import Product, ProductCalculation, ProductCashFlow as ProductCashFlowModel, ProductInterestGlobal
from apps.product.utils.utils import ProductUtils

from .services import calc_table_services, interest_services
from ..calculation import Calculation
from ...document.api.utils import DocumentApiUtils
from ...financial_accounting.batch_processing.loaders.loaderMT940 import LoaderMT940
from ...financial_accounting.transaction.models import Transaction


class ProductApi(APIView):
    def get(self, request):
        response_status = http_status.HTTP_200_OK

        try:
            product = Product.objects.get(pk=request.query_params.get('productId'))
            response_data = {
                'product': ProductSerializer(product).data,
                'schedule': ProductScheduleSerializer(product.schedule_set.all().order_by('maturity_date'), many=True).data,
                'cashflow': ProductCashFlowSerializer(product.cashflow_set.all().order_by('cash_flow_date'), many=True).data,
                'calculation_last': ProductCalculationSerializer(product.calculation.all().order_by('calc_date').last()).data,
                'interest': ProductInterestSerializer(product.interest_set.all().order_by('start_date'), many=True).data
            }

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = http_status.HTTP_422_UNPROCESSABLE_ENTITY

        return Response(data=response_data, status=response_status)

    def delete(self, request):
        response_status = http_status.HTTP_200_OK
        response_data = {}

        try:
            product = Product.objects.get(pk=request.data.get('productId'))
            if product.document.annexed_by:
                # remove annex relations
                product.document.annexed_by.annex = None
                product.document.annexed_by.save()

                product.document.annexed_by = None
                product.document.save()

            DocumentApiUtils.change_status(document=product.document,
                                           status=DocumentTypeStatus.objects.get(type=product.document.type, is_initial=True),
                                           reason='[Product deletion]: ',
                                           user=request.user)

            for i in DocumentStatusCourse.objects.filter(document=product.document).order_by('creation_date')[1:]:
                i.delete()

            # delete references to product from transaction (batch bank transaction files upload like MT940)
            Transaction.objects.filter(destination_id=product.pk).update(destination_id=None)

            product.delete()

        except Exception as ex:
            response_status = http_status.HTTP_400_BAD_REQUEST
            response_data['errmsg'] = str(ex)
            response_data['traceback'] = traceback.format_exc()
        return Response(data=response_data, status=response_status)


class ProductCalcTable(APIView):
    DEFAULT_FORMATTER = {"titleFormatter": "textarea", "variableHeight": True}
    CURRENCY_FORMATTER = {
        "hozAlign": "right",
        "formatter": "money", "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2}
    }

    @staticmethod
    def get_calc_table_columns(document_type):
        return calc_table_services.get_calc_table_columns(document_type=document_type)

    @staticmethod
    def get_data(product, add_query=None):
        q = Q(product=product)
        if add_query:
            q &= add_query

        return ProductCalculationSerializer(ProductCalculation.objects.filter(q).order_by('calc_date'), many=True).data

    def get(self, request):
        product_id = request.query_params.get('productId')
        calc_date = request.query_params.get('calcDate', None)
        no_header = request.query_params.get('noHeader', False)

        product = Product.objects.get(pk=product_id)

        if calc_date:
            if calc_date == '__MAX_DATE__':
                data = ProductCalcTable.get_data(product)[-1]
            else:
                data = ProductCalcTable.get_data(product, Q(calc_date=calc_date))
        else:
            data = ProductCalcTable.get_data(product)

        if no_header:
            return Response(data=data)
        return Response(data={"header": ProductCalcTable.get_calc_table_columns(product.document.type), "data": data})


class ProductCashFlowApi(APIView):
    @rest_api_wrapper
    def get(self, request):
        product = request.query_params.get('productId')
        cashflow_type_serializer = DocumentTypeAccountingTypeSerializer(DocumentTypeAccountingType.objects.filter(is_editable=True).order_by('sq'), many=True).data
        serializer = ProductCashFlowSerializer(ProductCashFlowModel.objects.filter(product=product).order_by('cash_flow_date'), many=True)
        data = {'cashflow_types': cashflow_type_serializer, 'data': serializer.data}

        return data

    @rest_api_wrapper
    def put(self, request):
        product = Product.objects.get(pk=request.data.get('id'))
        with transaction.atomic():
            LoaderMT940.account_products(product=product, reset=True)
            ProductCalculation.objects.filter(product=product).delete()
            Calculation(product=product, user=request.user).calculate()


class ProductCashFlowAggregatesApi(APIView):

    @staticmethod
    def get_subtype(type, subtype):
        ac = DocumentTypeAccountingType.objects.get(pk=type)
        for i in ac.subtypes:
            if subtype in i:
                return i[subtype]
        return ''

    def get(self, request):
        status = http_status.HTTP_200_OK
        try:
            product = request.query_params.get('productId')

            data = [{
                '_type': i['type'],
                'type': i['type__name'],
                'subtype': ProductCashFlowAggregatesApi.get_subtype(i['type'], i['subtype']),
                'sum': i['sum']
            }
                for i in ProductCashFlowModel.objects.filter(product=product).select_related('type').values('type', 'type__name', 'type__subtypes', 'subtype').annotate(sum=Sum('value'))]

        except Exception as ex:
            status = http_status.HTTP_400_BAD_REQUEST
            data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}

        return Response(data=data, status=status)


class ProductTypeStatusApi(APIView):
    def get(self, request):
        response_data = []
        response_status = http_status.HTTP_200_OK
        try:
            current_status = request.query_params.get('status', None)
            available_statuses = ProductUtils.get_available_statuses(status=current_status)
            if available_statuses:
                response_data = [(i.available_status.pk, i.available_status.name) for i in available_statuses]

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = http_status.HTTP_400_BAD_REQUEST

        return Response(data=response_data, status=response_status)


class ProductGlobalInterestView(APIView):
    @rest_api_wrapper
    def get(self, request):
        id = request.query_params.get('id', None)

        if id:
            return ProductInterestGlobalSerializer(instance=ProductInterestGlobal.objects.get(pk=id)).data

        return ProductInterestGlobalSerializer(instance=ProductInterestGlobal.objects.all().order_by('start_date'), many=True).data

    @rest_api_wrapper
    def post(self, request):
        product_interest_global = ProductInterestGlobalSerializer(data=request.data, context={"user": request.user})
        product_interest_global.is_valid(raise_exception=True)

        with transaction.atomic():
            product_interest_global = product_interest_global.save()
            interest_services.save_interest_global(product_interest_global, request.user)

        return {'refresh': True}

    @rest_api_wrapper
    def put(self, request):
        product_interest_global = ProductInterestGlobalSerializer(
            instance=ProductInterestGlobal.objects.get(pk=request.data.get('id')),
            data=request.data
        )
        product_interest_global.is_valid(raise_exception=True)

        with transaction.atomic():
            product_interest_global = product_interest_global.save()
            interest_services.save_interest_global(product_interest_global, request.user)

        return {'refresh': True}

    @rest_api_wrapper
    def delete(self, request):
        id = request.data.get('id', None)

        interest_global = ProductInterestGlobal.objects.get(pk=id)
        interest_services.delete_interest_global(interest_global)
        interest_global.delete()

        return {'refresh': True}


    @rest_api_wrapper
    def patch(self, request):
        return self.put(request)


class ProductStatView(APIView):
    @rest_api_wrapper
    def get(self, request):
        data = []
        labels = []

        products = Product.objects.values('status__name').annotate(
            cnt=Count('id'),
            total = Sum('value')
        ).order_by('status__sq')

        for product in products:
            data.append(product['cnt'])
            label = f"{product['total']:,}".replace(',', ' ').replace('.', ',')
            labels.append(f"{product['status__name']} ({product['cnt']}) - {label} {settings.CURRENCY_SHORTCUT}.")

        return {"products": products, "productStatsChart": {"data": [data], "labels": labels}}