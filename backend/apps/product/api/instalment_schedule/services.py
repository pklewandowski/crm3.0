import datetime
import json
from decimal import Decimal

from django.conf import settings

from apps.document.models import Document
from apps.product.instalment_schedule.instalment_schedule import InstalmentSchedule
from apps.product.models import Product
from apps.product.utils.utils import LoanUtils
from py3ws.utils import date_utils as py3ws_date_utils, string_utils
from py3ws.utils import utils as py3ws_utils


class ProductInstalmentScheduleException(Exception):
    pass


def recalculate_interest(instalment_data, capital, interest_rate):
    data = json.loads(instalment_data)
    capital = Decimal(capital)
    interest_rate = Decimal(interest_rate) if interest_rate else 0

    interest = []

    for i in data:
        interest.append(capital * interest_rate / len(data))
        capital -= Decimal(i['capital'])

    return interest


def recalculate_dates(start_date, instalment_number: int, instalment_idx: int = 0):
    data = []

    if not start_date:
        return []

    if not instalment_number:
        raise ProductInstalmentScheduleException('Brak parametru liczba rat!')

    nominal_dt = py3ws_utils.add_month(datetime.datetime.strptime(start_date, '%Y-%m-%d').date(), 1)
    data.append(py3ws_date_utils.set_schedule_work_day(nominal_dt))

    for i in range(instalment_number - instalment_idx - 1):
        nominal_dt = py3ws_utils.add_month(nominal_dt, 1)
        data.append(py3ws_date_utils.set_schedule_work_day(nominal_dt))

    return data


def instalment_interest_rates_to_dict(instalment_interest_rates: list) -> dict:
    if not instalment_interest_rates:
        return {}

    _instalment_interest_rates = {settings.MINUS_INFINITY_DATE: Decimal(instalment_interest_rates[0]['value'])}

    del instalment_interest_rates[0]

    for rate in instalment_interest_rates:
        _instalment_interest_rates[
            datetime.datetime.strptime(rate['start_date'], "%Y-%m-%d") if rate[
                'start_date'] else settings.INFINITY_DATE
        ] = Decimal(rate['value'] or 0)

    return _instalment_interest_rates


def _validate_schedule(opts, raise_exception=True):
    return True


def recalculate_on_product(user, product):
    instalment_schedule = InstalmentSchedule(
        user=user,
        product=product
    )


def recalculate(user, opts):
    _validate_schedule(opts)

    instalment_number = int(opts.get('instalmentNumber', 0))
    if not instalment_number:
        raise ProductInstalmentScheduleException('Liczba rat musi być większa od zera')

    instalment_schedule = InstalmentSchedule(
        user=user,
        product=Product.objects.get(pk=opts['idProduct']) if 'idProduct' in opts and opts['idProduct'] else None,
        balance=float(opts['value']) if opts['instalmentInterestCapitalTypeCalcSource'] == 'G' else float(
            opts['capitalNet']),
        interest_rate=float(list(opts['instalmentInterestRate'].items())[0][1] or 0),
        instalment_rate=None,
        instalment_constant_value=float(opts['instalmentTotal'] or 0) if opts['constantInstalment'] == 'T' else None,
        instalment_schedule=opts['scheduleTableData'],
        instalment_number=int(opts['instalmentNumber']),
        start_date=datetime.datetime.strptime(opts['startDate'], '%Y-%m-%d').date() if opts['startDate'] else None,
    ).calculate()

    return instalment_schedule

    # return ProductScheduleUtils.generate_schedule_table(
    #     start_date=opts.get('startDate', None),
    #     capital_net=Decimal(opts.get('capitalNet', 0) if opts.get('capitalNet', 0) else 0),
    #     capital_gross=Decimal(opts.get('value', 0) if opts.get('value', 0) else 0),
    #     commission=Decimal(opts.get('commission', 0) if opts.get('commission', 0) else 0),
    #     instalment_capital=Decimal(opts.get('instalmentCapital', 0) if opts.get('instalmentCapital', 0) else 0),
    #     instalment_commission=Decimal(
    #         opts.get('instalmentCommission', 0) if opts.get('instalmentCommission', 0) else 0),
    #     instalment_total=Decimal(opts.get('instalmentTotal', 0) if opts.get('instalmentTotal', 0) else 0),
    #     instalment_interest_rates=instalment_interest_rates,
    #     instalment_interest_capital_type_calc_source=opts.get('instalmentInterestCapitalTypeCalcSource', 'N')
    #     if 'instalmentInterestCapitalTypeCalcSource' in opts else 'G',
    #     instalment_number=instalment_number,
    #     constant_instalment=opts.get('constantInstalment', 'X') == 'T',
    #     arbitrary_instalment=opts.get('arbitraryInstalment', 'X') == 'T',
    #     schedule_table_data=opts.get('scheduleTableData', [])
    # )


def get_mapping(document: Document) -> dict:
    mapping = LoanUtils._get_mapping(document, True)
    attr_dict = {}
    for k, v in mapping.items():
        if isinstance(v, list):
            attr_list = []
            for i in v:
                attr_list.append(
                    {
                        'id': i['id'],
                        'value': i['value']
                    }
                )
            attr_dict[string_utils.camel_case(k)] = attr_list
        else:
            attr_dict[string_utils.camel_case(k)] = {
                'id': v['id'],
                'value': v['value']
            }

    return attr_dict
