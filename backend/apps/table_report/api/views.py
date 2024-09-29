from django.db.models import Sum, Count
from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.document.models import Document
from apps.product.models import Product, ProductCashFlow


class TableReportWidget(APIView):
    @rest_api_wrapper
    def get(self, request):
        return {
            'total_commission': {
                'name': 'Naliczona prowizja ( wszystkie / aktywne )',
                'total': f"{Product.objects.all().aggregate(total_commission=Sum('commission'))['total_commission']}",
                'active': f"{Product.objects.filter(status__is_closing_process=False).aggregate(active_commission=Sum('commission'))['active_commission']}"
            },
            'total_instalment': {
                'name': 'Spłacalność',
                'total': ProductCashFlow.objects.filter(type__code='PAYMENT').aggregate(total=Sum('value'))['total']
            },
            'total_cost': {
                'name': 'Koszty',
                'total': ProductCashFlow.objects.filter(type__code='COST').aggregate(total=Sum('value'))['total']
            },
            'total_balance': {
                'name': 'Saldo',
                'total': Product.objects.filter(status__is_closing_process=False).aggregate(total=Sum('balance'))['total']
            },
            'total_products': {
                'name': 'Wszystkie udzielone pożyczki',
                'total': Product.objects.all().aggregate(total=Sum('value'))['total'],
                'count': Product.objects.all().count()
            }
        }


class TableReportAggregateView(APIView):
    @rest_api_wrapper
    def get(self, request):
        return {
            "winpr": Document.objects.filter(type__id=request.query_params.get('id'),
                                             status__is_closing_process=False
                                             ).count(),
            "prinpr": Product.objects.filter(type_id=request.query_params.get('id'),
                                             status__is_closing_process=False, status__is_alternate=False
                                             ).aggregate(count=Count('id'), total_value=Sum('value')),
            "prinwdk": Product.objects.filter(type_id=request.query_params.get('id'),
                                              status__code__startswith='WDK'
                                              ).aggregate(count=Count('id'), total_value=Sum('value')),
        }
