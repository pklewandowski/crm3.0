import datetime
import json
import logging
import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.db import transaction
from django.db.models import Max, F
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.attachment import utils as atm_utils
from apps.document.models import DocumentTypeAttribute, DocumentType, DocumentTypeSection, DocumentTypeAccountingType
from apps.product import FORCE_CALCULATION
from apps.product.base import ProductActionManager
from apps.product.calculation import CalculationException
from apps.product.forms import ProductTypeAttributeForm, ProductForm, ProductActionForm, TestCopyPasteForm, \
    CashFlowFormset, ProductInterestGlobalForm, ProductTrancheFormset
from apps.product.models import Product, ProductAccounting, ProductCalculation, ProductAction, ProductActionDefinition, \
    ProductInterestGlobal
from apps.product.utils.utils import ProductUtils
from apps.report.datasource_utils import ReportDatasourceUtils
from apps.report.forms import ReportDatasourceForm
from apps.report.models import Report
from py3ws.auth.decorators.decorators import p3permission_required
from py3ws.report.jasper.server import report_server
from py3ws.utils import utils as py3ws_utils

logger = logging.getLogger(__name__)


class InterestNotFoundException(Exception):
    pass


def index(request):
    return HttpResponse("Statysyki produktów")


def list_product(request, id):
    product_type = get_object_or_404(DocumentType, pk=id)
    products = Product.objects.filter(type=product_type).order_by('-creation_date')

    context = {'products': products, 'product_type': product_type}
    return render(request, 'product/list.html', context)


def list_all_products(request):
    products = Product.objects.all().order_by('document__type__name', '-creation_date')

    context = {'products': products}
    return render(request, 'product/list_all_products.html', context)


@login_required()
@p3permission_required('product.add_product')
@transaction.atomic()
def add(request, id):
    return redirect('document.add', type=id)


def recalculate_schedule_interest_instalment(product):
    schedule = product.schedule_set.all().order_by('maturity_date')
    schedule_count = len(schedule)
    interest = product.interest_set.all().order_by('start_date')
    capital_net = product.capital_net

    def get_last_interest(interest_set, date):
        it = iter(interest_set)
        last_interest = None

        try:
            interest = next(it)
            while interest.start_date <= date:
                last_interest = interest
                interest = next(it)
        except StopIteration:
            pass

        return last_interest

    for i in schedule:
        with transaction.atomic():
            try:
                last_interest = get_last_interest(interest, i.maturity_date)
                if last_interest:
                    i.instalment_interest = round(capital_net * last_interest.statutory_rate / 12, 2)
                    i.save()
                    capital_net -= i.instalment_capital
                else:
                    raise InterestNotFoundException()
            except InterestNotFoundException:
                pass


def _count_balance(product):
    calc_max_date = ProductCalculation.objects.filter(product=product).aggregate(max_date=Max('calc_date'))['max_date']

    pc = ProductCalculation.objects.get(
        product=product,
        calc_date=calc_max_date
    )
    return {
        "balance": ProductUtils.calculate_balance(
            {'capital_not_required': pc.capital_not_required,
             'commission_not_required': pc.commission_not_required,
             'interest_for_delay_required': pc.interest_for_delay_required,
             'required_liabilities_sum': pc.required_liabilities_sum,
             'cost': pc.cost,
             'instalment_overpaid': pc.instalment_overpaid
             }),
        "calc_max_date": calc_max_date
    }


@login_required()
@p3permission_required('product.change_product')
@transaction.atomic()
def edit(request, id, iframe=0):
    errors = None
    messages = []
    product = Product.objects.prefetch_related('document', 'document__type').get(pk=id)

    actions = product.action_set.all().order_by('action_date')
    calculation_list = ProductCalculation.objects.filter(product=product).order_by('calc_date')
    atm_root_name = py3ws_utils.replace_special_chars(product.agreement_no)

    form = ProductForm(request.POST or None, instance=product)

    end_date = None
    schedule = None
    schedule_formset = None

    balance = 0
    calc_max_date = None

    if product.type.is_schedule:
        # schedule = product.schedule_set.all().annotate(
        #     instalment_total=F('instalment_capital') + F('instalment_interest')
        # ).order_by('maturity_date')

        schedule = product.schedule_set.all().order_by('maturity_date')

        end_date = product.end_date or datetime.date.today()

    # TODO: docelowo kalkulacja jest aktulana, bo liczona przez proces cron-owy codziennie.
    #  Proces musi być wykonywany tak, aby była aktualność na początek bieżącego dnia.
    # TODO: Do tego czasu trzeba każdorazowo przeliczać, żeby stan był aktualny

    if request.method != 'POST' and product.type.calculation_class:
        if FORCE_CALCULATION:
            py3ws_utils.get_class(product.type.calculation_class)(product, request.user).calculate()
        else:
            try:
                ProductCalculation.objects.get(product=product, calc_date=end_date - datetime.timedelta(days=1))
                logger.debug('Calculation exists!')
            except ProductCalculation.DoesNotExist:
                logger.debug('Calculation does not exist')
                if not product.status.is_closing_process:
                    # calculating
                    try:
                        # TODO: poprawić, żeby działało dla startu od danego dnia
                        # py3ws_utils.get_class(product.type.calculation_class)(product, request.user).calculate(
                        #     start_date=datetime.date.today())
                        py3ws_utils.get_class(product.type.calculation_class)(product, request.user).calculate()
                    except CalculationException as ex:
                        return render(request, 'product/calculation_error.html', {"errmsg": str(ex), "product": product})

                else:
                    print('Product is in closing process status')

    try:
        cb = _count_balance(product=product)
        balance = cb['balance']
        calc_max_date = cb['calc_max_date']

    except Exception:
        pass

    # if schedule:
    #     schedule_formset = ScheduleFormset(data=request.POST or None, queryset=schedule, prefix='product-schedule')

    cashflow_formset = CashFlowFormset(data=request.POST or None,
                                       queryset=product.cashflow_set.all().order_by('cash_flow_date',
                                                                                    'accounting_date'),
                                       prefix='product-cashflow')

    tranche_formset = ProductTrancheFormset(data=request.POST or None,
                                            queryset=product.tranches.all().order_by('launch_date'),
                                            prefix='product-tranche'
                                            )

    # interest_queryset = product.interest_set.all().order_by('start_date')
    # interest_formset = InterestFormset(data=request.POST or None, queryset=interest_queryset, prefix='product-interest')

    if request.method == 'POST':
        min_change_date = settings.INFINITY_DATE
        valid = True

        # if product.type.is_schedule:
        #     valid = not schedule_formset.has_changed() or schedule_formset.is_valid()

        if valid and all([
            not form.has_changed() or form.is_valid(),
            not cashflow_formset.has_changed() or cashflow_formset.is_valid(),
            not tranche_formset.has_changed() or tranche_formset.is_valid()
            # not interest_formset.has_changed() or interest_formset.is_valid()
        ]):
            has_changed = False

            if form.has_changed():
                form.save()
                has_changed = True

            # if schedule_formset and schedule_formset.has_changed():
            #     min_change_date = min(min_change_date,
            #                           min([min(k.initial.get('maturity_date'), k.cleaned_data.get('maturity_date') or settings.INFINITY_DATE)
            #                                for k in schedule_formset if k.changed_data] or settings.INFINITY_DATE))
            #     schedule_formset.save()
            #     has_changed = True

            # if interest_formset.has_changed():
            #     min_change_date = min(min_change_date,
            #                           min([min(k.initial.get('start_date') or settings.INFINITY_DATE,
            #                                    k.cleaned_data.get('start_date') or settings.INFINITY_DATE)
            #                                for k in interest_formset if k.changed_data] or settings.INFINITY_DATE))
            #     interest_formset.save()

            if cashflow_formset.has_changed():
                min_change_date = min(min_change_date,
                                      min([min(k.initial.get('cash_flow_date') or settings.INFINITY_DATE,
                                               k.cleaned_data.get('cash_flow_date') or settings.INFINITY_DATE)
                                           for k in cashflow_formset if k.changed_data] or settings.INFINITY_DATE))
                cashflow_formset.save()
                has_changed = True

            if tranche_formset.has_changed():
                min_change_date = min(min_change_date,
                                      min([min(k.initial.get('launch_date') or settings.INFINITY_DATE,
                                               k.cleaned_data.get('launch_date') or settings.INFINITY_DATE)
                                           for k in tranche_formset if k.changed_data] or settings.INFINITY_DATE))
                tranche_formset.save()
                has_changed = True

            # TODO: do zrobienia accounting na poziomie produktu
            if has_changed:
                # py3ws_utils.get_class(product.type.calculation_class)(product.pk, request.user).calculate(start_date=min_change_date)
                py3ws_utils.get_class(product.type.calculation_class)(product.pk, request.user).calculate()
                messages.append('Pomyślnie zapisano zmiany')
            else:
                messages.append('Brak zmian do zapisania')
                print('no changes detected')

            return redirect('product.edit', product.pk)
        else:
            errors = True

    accounting_ordered = [
        i.accounting_type for i in ProductAccounting.objects.filter(
            product=product,
            accounting_type__is_accounting_order=True).order_by('sq')
    ]

    product_action_definition = ProductActionDefinition.objects.filter(
        document_type=product.document.type).order_by('sq')

    context = {'form': form,
               # 'cashflow_type': {i.code.lower(): {"id": i.pk, 'name': i.name, 'subtypes': i.subtypes} for i in
               #                   DocumentTypeAccountingType.objects.filter(is_editable=True)},
               'cashflow_type': DocumentTypeAccountingType.get_accounting_types(),
               'cashflow_formset': cashflow_formset,
               'schedule': schedule,
               'tranche_formset': tranche_formset,
               'atm_classname': 'apps.product.models.ProductAttachment',
               'atm_owner_classname': 'apps.product.models.Product',
               'atm_root_name': atm_root_name,
               'accounting_ordered': accounting_ordered,
               'calculation_list': calculation_list,
               'product_action_definition': product_action_definition,
               'actions': actions,
               'mode': settings.MODE_EDIT,
               'messages': messages,
               'balance': balance,
               'calc_max_date': calc_max_date,
               'errors': errors
               }
    if iframe:
        context['override_base'] = "%s.html" % iframe
    return render(request, 'product/edit.html', context)


def list_product_type(request):
    product_types = DocumentType.objects.filter(category__attributes__contains={"product": "1"})
    context = {'product_types': product_types}
    return render(request, 'product/type/list.html', context)


def list_product_type_section(request, id):
    product_type = DocumentType.objects.get(pk=id)
    sections = DocumentTypeSection.objects.filter(product_type=product_type)
    context = {'sections': sections, 'product_type': product_type}
    return render(request, 'product/type/section/list.html', context)


@transaction.atomic
def add_product_type_attribute(request, id):
    product_type = DocumentType.objects.get(pk=id)
    form = ProductTypeAttributeForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            attr = form.save(commit=False)
            attr.product_type = product_type
            attr.sq = 0
            attr.save()
            return redirect('product.type.attribute.list', attr.product_type.pk)

    context = {'form': form, 'product_type': product_type}
    return render(request, 'product/type/attribute/add.html', context)


@transaction.atomic
def edit_product_type_attribute(request, id):
    attr = get_object_or_404(DocumentTypeAttribute, pk=id)
    form = ProductTypeAttributeForm(request.POST or None, instance=attr)

    if request.method == 'POST':
        if form.is_valid():
            attr = form.save()
            return redirect('product.type.attribute.list', attr.product_type.pk)

    context = {'form': form}
    return render(request, 'product/type/attribute/add.html', context)


def list_product_type_attribute(request, id):
    product_type = DocumentType.objects.get(pk=id)
    attributes = DocumentTypeAttribute.objects.filter(product_type=id).order_by('section', 'sq')
    context = {'attributes': attributes, 'product_type': product_type}
    return render(request, 'product/type/attribute/list.html', context)


@csrf_exempt
def day_calculation(request):
    response_data = {'data': None, 'message': None}

    id = request.POST.get('id')
    dt = request.POST.get('dt')

    calculation = []

    try:
        try:
            calculation = [ProductCalculation.objects.get(product=Product.objects.get(pk=id), calc_date=dt)]
        except ProductCalculation.DoesNotExist:
            pass

        response_data['status'] = 'OK'
        response_data['data'] = serialize('json', calculation)

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def action_report_preview(request):
    status = 200
    response_data = {}
    try:
        action = ProductActionDefinition.objects.get(id=request.POST.get('idAction'))
        product = Product.objects.get(pk=request.POST.get('idProduct'))

        data = json.loads(request.POST.get('formData'))

        rd_form = ReportDatasourceForm(data=data, report=action.report, prefix='rdf')

        if rd_form.is_valid():
            if action.report:
                data = report_server.set_xml_datasource(action.report, product.document, request.user, rd_form)
                output_file_name = str(uuid.uuid4())
                output_file_path = os.path.join(settings.MEDIA_ROOT, "reports/tmp/") + output_file_name
                report_server.render(data_file=data['data_file_path'], report_file=action.report.template_name,
                                     output_file=output_file_path)

                response_data['output_file_name'] = output_file_name
        else:
            status = 400
            response_data['errmsg'] = rd_form.errors

    except Exception as e:
        status = 400
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@transaction.atomic
def action_add(request, id_product, id_action=None):
    pam = ProductActionManager(id_product=id_product, id_action=id_action)

    product = Product.objects.get(pk=id_product)
    action = ProductActionDefinition.objects.get(id=id_action)
    report_template = action.report

    form = ProductActionForm(request.POST or None, initial={'name': action.name})
    rd_form = ReportDatasourceForm(request.POST or None, report=report_template, prefix='rdf')

    cl = ReportDatasourceUtils(document=product.document, user=request.user)
    datasource = []
    for i in action.report.datasource_definition_set.all().order_by('sq'):
        value = cl.__getattribute__(i.getter_function)() if i.getter_function else ''
        datasource.append({'name': i.name, 'tag_name': i.tag_name, 'value': value, 'editable': i.editable})

    if request.method == 'POST':
        if all([form.is_valid(), rd_form.is_valid()]):
            product_action = form.save(commit=False)
            product_action.product = product
            product_action.action_date = datetime.datetime.now()
            product_action.created_by = request.user
            if report_template:
                data = report_server.set_xml_datasource(report_template, product.document, request.user, rd_form)
                output_file_name = str(uuid.uuid4())
                output_file_path = os.path.join(settings.MEDIA_ROOT, "reports/output/") + output_file_name
                report_server.render(data_file=data['data_file_path'], report_file=action.report.template_name,
                                     output_file=output_file_path)
                rep = Report.objects.create(document=product.document,
                                            template=report_template,
                                            created_by=request.user,
                                            file_name=output_file_name + '.pdf',
                                            status='DONE',
                                            xml_data=data['data'])
                product_action.report = rep
            product_action.save()

            return redirect('product.edit', product.pk)

    context = {'form': form,
               'rd_form': rd_form,
               'action': action,
               'datasource': datasource,
               'product': product
               }
    return render(request, 'product/action/add.html', context)


def action_edit(request, id_product, id_action):
    action = ProductAction.objects.get(pk=id_action)

    form = ProductActionForm(request.POST or None, instance=action)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('product.edit', id_product)

    context = {'form': form, 'action': action, 'id_product': id_product}
    return render(request, 'product/action/edit.html', context)


@transaction.atomic
def action_delete(request):
    response_data = {}
    id = request.POST.get('id')

    try:
        action = ProductAction.objects.get(pk=id)
        action.delete()

        response_data['status'] = 'OK'
    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def temp_copy_paste(request):
    form = TestCopyPasteForm(request.POST or None)
    if form.is_valid():
        atm_utils.handle_printscreen_image(data=form.cleaned_data['image_data'], file_name='temp_copy.jpg',
                                           path='screens')

    context = {'form': form}
    return render(request, 'product/temp_copy_paste.html', context)


def interest_global(request, id):
    form = ProductInterestGlobalForm(data=request.POST or None)
    document_type = DocumentType.objects.get(pk=id)
    global_interest_list = ProductInterestGlobal.objects.filter(document_type=document_type).order_by('start_date')

    context = {
        'form': form,
        'document_type': document_type,
        'global_interest_list': global_interest_list
    }

    return render(request, 'product/type/interest_global/interest_global.html', context)
