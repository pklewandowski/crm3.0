import datetime

from django.db.models import Max, F, Sum, Count, OuterRef, Subquery, Window, IntegerField, DecimalField, Min, DateField
from django.shortcuts import render
from django.views.generic import ListView

from apps.document.models import Document
from apps.product.models import Product, ProductCashFlow, ProductSchedule


def report_list(request):
    return render(request, 'table_report/table_report_list_template.html')


class TableReportView(ListView):
    paginate_by = 30
    ordering = 'creation_date'

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.title = ''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title  # _('Pożyczki w procesie')
        context['style'] = {'template_pack': 'rest_framework/vertical/'}
        return context

    def get_queryset(self):
        if self.kwargs.get('code') == 'wnstatustimeline':
            self.template_name = 'table_report/documents_status_timeline_template.html'
            self.title = 'Wnioski w osi czasu'
            return Document.objects.filter(type_id=self.kwargs.get('id')).prefetch_related()

        if self.kwargs.get('code') == 'winpr':
            self.template_name = 'table_report/documents_in_process_template.html'
            self.title = 'Wnioski w procesie'
            return Document.objects.filter(type_id=self.kwargs.get('id'),
                                           status__is_closing_process=False
                                           )

        if self.kwargs.get('code') == 'prinpr':
            self.title = 'Pożyczki w procesie'
            self.template_name = 'table_report/products_in_statuses_template.html'
            return Product.objects.filter(type_id=self.kwargs.get('id'),
                                          status__is_closing_process=False
                                          )

        if self.kwargs.get('code') == 'prinwdk':
            self.title = 'Pożyczki w windykacji'
            self.template_name = 'table_report/products_in_statuses_template.html'
            return Product.objects.filter(type_id=self.kwargs.get('id'),
                                          status__code__startswith='WDK'
                                          )

        if self.kwargs.get('code') == 'agrenddays':
            self.title = 'Produkty umowy raty'
            self.template_name = 'table_report/client_product_data.html'

            total_instalment_paid_subquery = ProductCashFlow.objects.filter(
                product=OuterRef('pk'), type__code='PAYMENT'
            ).annotate(total_instalment_paid=Window(expression=Sum('value'))).values('total_instalment_paid')[:1]

            total_instalment_count_subquery = ProductCashFlow.objects.filter(
                product=OuterRef('pk'), type__code='PAYMENT'
            ).annotate(total_instalment_count=Window(expression=Count('pk'), partition_by=['type'])).values('total_instalment_count')[:1]

            next_instalment_date_subquery = ProductSchedule.objects.filter(
                product=OuterRef('pk'), maturity_date__gte=datetime.date.today()
            ).annotate(next_instalment_date=Window(expression=Min('maturity_date'), partition_by=['product'])).values('next_instalment_date')[:1]

            return Product.objects.filter(status__is_closing_process=False). \
                annotate(agreement_end_date=Max('schedule_set__maturity_date')). \
                annotate(days_to_last_instalment=F('agreement_end_date') - datetime.date.today()).prefetch_related('schedule_set'). \
                annotate(total_instalment_paid=Subquery(total_instalment_paid_subquery, output_field=DecimalField())). \
                annotate(total_instalment_count=Subquery(total_instalment_count_subquery, output_field=IntegerField())). \
                annotate(next_instalment_date=Subquery(next_instalment_date_subquery, output_field=DateField())). \
                annotate(days_to_next_instalment=F('next_instalment_date') - datetime.date.today()). \
                order_by('client')

        return None
