import datetime

from django.db.models import Q, Max, F, Sum, Avg, Count
from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.document.models import Document
from apps.product.models import Product, ProductCashFlow, ProductCalculation
from apps.user_func.client.api.serializers import ClientSerializer
from apps.user_func.client.models import Client

RECORDS_PER_PAGE = 200


class NumberWidget(APIView):
    def _get_registered_number_widgets(self, user):
        """
        returns registered users' number widgets with appropriate data source methods
        todo: to be developed later but sure...
        :param user:
        :return:
        """
        pass

    @staticmethod
    def median(queryset):
        if not queryset:
            return '-'

        cnt = queryset.count()

        if not cnt:
            return '-'

        if cnt == 1:
            return queryset[0].value or '-'

        _cnt = cnt // 2

        return (queryset[_cnt - 1].value + queryset[_cnt].value) / 2 if cnt / 2 == _cnt else queryset[_cnt].value

    @rest_api_wrapper
    def get(self, request):
        return {
            'clients': {
                'name': 'Klienci wszyscy / aktywni',
                'value': f"{Client.objects.all().count()} / {Client.objects.filter(status__in=['IN', 'PROSPECT', 'INVEST']).distinct().count()}"
            },
            'balanceSum': {
                'name': 'Suma bilansowa',
                'value': ProductCalculation.objects.filter(
                    calc_date=datetime.date.today() - datetime.timedelta(days=1)
                ).aggregate(total_value=Sum(F('capital_not_required') + F('capital_required')))['total_value'] or '-'
            },
            'allLoanSum': {
                'name': 'Suma udzielonych pożyczek',
                'value': Product.objects.filter(type__id=26).aggregate(total_value=Sum('value'), )['total_value'] or '-'  # todo: DRUT
            },
            'instalmentIncome': {
                'name': 'Przychody z rat',
                'value': ProductCashFlow.objects.filter(type__code='PAYMENT').aggregate(total_value=Sum('value'))['total_value'] or '-'
            },
            'avgLoanVal': {
                'name': 'Średnia wartość pożyczki',
                'value': Product.objects.filter(type__id=26).aggregate(avg_value=Avg('value'))['avg_value'] or '-' # todo: DRUT
            },
            'median': {
                'name': 'Mediana pożyczek',
                'value': NumberWidget.median(Product.objects.filter(type__id=26).order_by('value')) # todo: DRUT
            }
        }


class ChartWidgetView(APIView):
    @rest_api_wrapper
    def get(self, request):
        data = []
        labels = []

        documents = Document.objects.filter(type__id=26).values('status__name').annotate(
            cnt=Count('id')).order_by('status__is_alternate', 'status__sq')

        for document in documents:
            data.append(document['cnt'])
            labels.append(document['status__name'])

        result = {"documentStatusChart": {"data": [data], "labels": labels}}

        documents = Document.objects.filter(type__id=26).values('created_by__pk', 'created_by__first_name', 'created_by__last_name').annotate(
            cnt=Count('created_by__pk')).order_by('-cnt')[:10]

        data = []
        labels = []

        for document in documents:
            data.append(document['cnt'])
            labels.append(f"{document['created_by__first_name']} {document['created_by__last_name']}")

        result["documentByAdviser"] = {"data": [data], "labels": labels}

        return result


class CurrentContacts(APIView):
    @rest_api_wrapper
    def get(self, request):
        page = int(request.query_params.get('p', 1)) - 1
        q = Q()

        result = Client.objects.filter(q).exclude(status='OUT'). \
            annotate(max_event_date=Max('user__schedule_user_set__schedule__start_date'),
                     date_diff=F('max_event_date') - datetime.date.today()).order_by('-max_event_date')

        count = result.count()

        return {
            'data': ClientSerializer(result[page * RECORDS_PER_PAGE: page * RECORDS_PER_PAGE + RECORDS_PER_PAGE], many=True).data,
            'count': count,
            'pages': count // RECORDS_PER_PAGE
        }
