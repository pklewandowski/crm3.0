import datetime
import json
from decimal import Decimal

import crm_settings
from apps.document.models import Document
from apps.product.utils.schedule_utils import ProductScheduleUtils
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

    _instalment_interest_rates = {crm_settings.MINUS_INFINITY_DATE: Decimal(instalment_interest_rates[0]['value'])}

    del instalment_interest_rates[0]

    for rate in instalment_interest_rates:
        _instalment_interest_rates[
            datetime.datetime.strptime(rate['start_date'], "%Y-%m-%d") if rate[
                'start_date'] else crm_settings.INFINITY_DATE
        ] = Decimal(rate['value'] or 0)

    return _instalment_interest_rates


def _validate_schedule(opts, raise_exception=True):
    return True


def recalculate(opts):
    # mapping = get_mapping(Document.objects.get(pk=opts.get('documentId')))

    _validate_schedule(opts)

    instalment_number = int(opts.get('instalmentNumber', 0))
    if not instalment_number:
        raise ProductInstalmentScheduleException('Liczba rat musi być większa od zera')

    """
    instalment_interest_rates
    if there is no start_date, it means that schedule is generated with no date specified.
    In that case there should be only one entry in instalment_interest_rates parameter
    As an initial interest rate the MINUS_INFINITY_DATE is taken
    """
    instalment_interest_rates = {
        datetime.datetime.strptime(k, '%Y-%m-%d').date(): round(Decimal(v or 0), 4)
        for k, v in opts.get('instalmentInterestRate', {}).items()
    }

    return ProductScheduleUtils.generate_schedule_table(
        start_date=opts.get('startDate', None),
        capital_net=Decimal(opts.get('capitalNet', 0) if opts.get('capitalNet', 0) else 0),
        capital_gross=Decimal(opts.get('value', 0) if opts.get('value', 0) else 0),
        commission=Decimal(opts.get('commission', 0) if opts.get('commission', 0) else 0),
        instalment_capital=Decimal(opts.get('instalmentCapital', 0) if opts.get('instalmentCapital', 0) else 0),
        instalment_commission=Decimal(
            opts.get('instalmentCommission', 0) if opts.get('instalmentCommission', 0) else 0),
        instalment_total=Decimal(opts.get('instalmentTotal', 0) if opts.get('instalmentTotal', 0) else 0),
        instalment_interest_rates=instalment_interest_rates,
        instalment_interest_capital_type_calc_source=opts.get('instalmentInterestCapitalTypeCalcSource', 'N')
        if 'instalmentInterestCapitalTypeCalcSource' in opts else 'G',
        instalment_number=instalment_number,
        constant_instalment=opts.get('constantInstalment', 'X') == 'T',
        arbitrary_instalment=opts.get('arbitraryInstalment', 'X') == 'T',
        schedule_table_data=opts.get('scheduleTableData', [])
    )


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
