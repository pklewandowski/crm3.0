import datetime
import decimal

from django.conf import settings
from django.db import transaction

from apps.document.api.attribute_utils import AttributeUtils
from apps.document.models import DocumentTypeAttribute, DocumentAttribute
from apps.product.api.instalment_schedule import \
    INSTALMENT_MATURITY_DATE_SELECTOR, \
    INSTALMENT_CAPITAL_SELECTOR, \
    INSTALMENT_COMMISSION_SELECTOR, \
    INSTALMENT_INTEREST_SELECTOR, \
    INSTALMENT_TOTAL_SELECTOR
from apps.product.models import ProductSchedule, Product
from py3ws.utils import date_utils as py3ws_date_utils
from py3ws.utils import utils as py3ws_utils


class ProductScheduleUtils:

    @staticmethod
    def _calculate_daily_interest(capital, interest_rate):
        return round(capital * interest_rate / 365, 4)

    @staticmethod
    def _calculate_instalment_interest(
            capital,
            instalment_interest_rates: dict,
            start_date=None,
            end_date=None,
            current_rate=None,
            is_first_instalment=False
    ):
        """
        Calculates daily interest multiplied by days between latest and current instalment
        :param capital:
        :param instalment_interest_rates: list of instalment interest rate changes
               list structure:
               [{"start_date": datetime.date, "value": Decimal},...]
        :return:
        """
        if not instalment_interest_rates:
            return 0

        if current_rate is None:
            current_rate = round(instalment_interest_rates[settings.MINUS_INFINITY_DATE] or 0, 4) \
                if settings.MINUS_INFINITY_DATE in instalment_interest_rates else 0

        if not start_date or start_date == settings.INFINITY_DATE:
            return round((capital * current_rate) / 12, 4), current_rate

        daily_value = ProductScheduleUtils._calculate_daily_interest(capital=capital, interest_rate=current_rate)

        instalment_interest = 0

        for i in range((end_date - start_date).days):
            if start_date + datetime.timedelta(days=i) in instalment_interest_rates:
                current_rate = instalment_interest_rates[start_date + datetime.timedelta(days=i)]
                daily_value = ProductScheduleUtils._calculate_daily_interest(capital=capital, interest_rate=current_rate)
            instalment_interest += daily_value

        return round(instalment_interest, 2), current_rate

    @staticmethod
    def _calculate_real_instalment(
            nominal_total_instalment,
            instalment_capital,
            instalment_commission,
            _instalment_interest):

        if _instalment_interest >= nominal_total_instalment:
            return 0, 0

        if instalment_capital and instalment_commission:
            ratio = instalment_capital / instalment_commission + instalment_capital
        else:
            ratio = 1

        _instalment_commission = round(ratio * (nominal_total_instalment - _instalment_interest), 2) if instalment_commission else 0
        _instalment_capital = (nominal_total_instalment - _instalment_interest - _instalment_commission) if instalment_capital else 0

        return round(_instalment_capital, 2), _instalment_commission

    @staticmethod
    def _calculate_days(dt, dt_prev):
        return (dt - dt_prev).days

    @staticmethod
    def _get_next_date(schedule_table_data, idx, nominal_date):
        dt = py3ws_utils.add_month(nominal_date, 1)

        """
        If there is a change_flag set on maturity date field then it can equal 1 or 2.
        value 1 means that only this occurrence of maturity date changes (exactly only date in the row is changed)
        value 2 means that current row date change causes recalculating all following dates adding full month but caunting
        just from the new date of current row  
        
        """
        if schedule_table_data:
            """
            first condition checks if there is any change in current row.
            If so, then set the date from submited schedule table where the change is indicated
            The second (or) condition checks if the change was only for that field or the recalculation 
            is to be happen. If only one field, we take the next row value from submited schedule table.
            In other way we leave calculated above.
            """

            if idx < len(schedule_table_data) and (
                    (
                            'change_flag' in schedule_table_data[idx]['maturityDate'] and
                            int(schedule_table_data[idx]['maturityDate']['change_flag']) in [1, 2]
                    ) or (
                            idx and 'change_flag' in schedule_table_data[idx - 1]['maturityDate'] and
                            int(schedule_table_data[idx - 1]['maturityDate']['change_flag']) == 1
                    )
            ):
                dt = datetime.datetime.strptime(schedule_table_data[idx]['maturityDate']['value'], '%Y-%m-%d').date()

        return dt, py3ws_date_utils.set_schedule_work_day(dt)

    @staticmethod
    def map_instalment_schedule_attributes(attributes):
        return {i['selector_class']: i['id'] for i in attributes}

    @staticmethod
    def _is_arbitrary_change(schedule_table_data, keys, idx):
        if not schedule_table_data:
            return False

        for key in keys:
            try:
                if (key in schedule_table_data[idx] and
                        'change_flag' in schedule_table_data[idx][key] and
                        int(schedule_table_data[idx][key]['change_flag']) != 0):
                    return True

            except IndexError:
                return False
        return False

    @staticmethod
    def generate_schedule_table(capital_net,
                                capital_gross: decimal.Decimal,
                                commission: decimal.Decimal,
                                instalment_capital: decimal.Decimal,
                                instalment_commission: decimal.Decimal,
                                instalment_total: decimal.Decimal,
                                instalment_interest_rates: dict,
                                instalment_interest_capital_type_calc_source: str,
                                instalment_number: int,
                                schedule_table_data: list,
                                constant_instalment=False,
                                arbitrary_instalment=False,
                                start_date=None):
        schedule_table = []

        instalment_capital_aggregate = decimal.Decimal(0)
        instalment_interest_aggregate = decimal.Decimal(0)
        instalment_commission_aggregate = decimal.Decimal(0)

        """
        if calculation on capital gross then only capital and interest is taken,
        commission is included as part of capital: capital = capital_net + commission + others
        instalment_interest_capital_type_calc_source: 'N' for net, 'G' for gross
        """
        if instalment_interest_capital_type_calc_source != 'N':
            instalment_commission = 0

        capital_oper = capital_net if instalment_interest_capital_type_calc_source == 'N' else capital_gross or 0

        if not arbitrary_instalment:
            commission_oper = commission if instalment_interest_capital_type_calc_source == 'N' else 0
            if instalment_commission * instalment_number > commission_oper:
                raise ValueError('Suma rat prowizyjnych przewyższa wartość prowizji')

            if instalment_capital * instalment_number > capital_oper:
                raise ValueError('Suma rat kapitałowych przewyższa wartość pożyczki')

        else:
            commission_oper = 0

        nominal_dt = None
        days = None
        prev_dt = None

        if start_date:
            prev_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            nominal_dt, dt = ProductScheduleUtils._get_next_date(
                schedule_table_data=schedule_table_data,
                idx=0,
                nominal_date=prev_dt
            )
            days = ProductScheduleUtils._calculate_days(dt, prev_dt)
        else:
            dt = None

        current_rate = instalment_interest_rates[settings.MINUS_INFINITY_DATE]

        nominal_instalment_interest, current_rate = ProductScheduleUtils._calculate_instalment_interest(
            capital=capital_oper,
            instalment_interest_rates=instalment_interest_rates,
            current_rate=current_rate
        )
        nominal_total_instalment = instalment_capital + instalment_commission + nominal_instalment_interest

        for i in range(instalment_number - 1):
            _instalment_interest, current_rate = ProductScheduleUtils._calculate_instalment_interest(
                start_date=prev_dt,  # first day of loan shouldn't be counted with interest
                end_date=dt,
                capital=capital_oper,
                instalment_interest_rates=instalment_interest_rates,
                current_rate=current_rate,
                is_first_instalment=i == 0
            )
            _instalment_total = instalment_total

            if ProductScheduleUtils._is_arbitrary_change(
                    schedule_table_data=schedule_table_data,
                    keys=['instalmentCapital', 'instalmentCommission', 'instalmentTotal'],
                    idx=i):

                if arbitrary_instalment:
                    _instalment_total = decimal.Decimal(schedule_table_data[i]['instalmentTotal']['value'])
                else:
                    _instalment_capital = decimal.Decimal(schedule_table_data[i]['instalmentCapital']['value'])
                    _instalment_commission = decimal.Decimal(schedule_table_data[i]['instalmentCommission']['value'])

            if arbitrary_instalment:
                _instalment_capital = _instalment_total - _instalment_interest
                if _instalment_capital < 0:
                    raise ValueError(
                        f'Wystąpił błąd podczas obliczania raty nr {i + 1}: '
                        f'zbyt niska rata całkowita. Rata kapitałowa nr {i + 1} nie może być ujemna: {_instalment_capital} (odsetki: {_instalment_interest}). '
                        f'Proszę zwiększyć kwotę raty całkowitej.')

                _instalment_commission = 0
            else:
                if constant_instalment:
                    _instalment_capital, _instalment_commission = ProductScheduleUtils._calculate_real_instalment(
                        nominal_total_instalment,
                        instalment_capital,
                        instalment_commission,
                        _instalment_interest
                    )

                else:
                    _instalment_capital, _instalment_commission = instalment_capital, instalment_commission

            schedule_table.append(
                {
                    INSTALMENT_MATURITY_DATE_SELECTOR: dt or '',
                    INSTALMENT_CAPITAL_SELECTOR: round(_instalment_capital, 2),
                    INSTALMENT_COMMISSION_SELECTOR: round(_instalment_commission, 2) if not arbitrary_instalment else 0,
                    INSTALMENT_INTEREST_SELECTOR: round(_instalment_interest, 2),
                    INSTALMENT_TOTAL_SELECTOR:
                        round(_instalment_capital + _instalment_commission + _instalment_interest, 2) if not arbitrary_instalment else _instalment_total,
                    "days": days
                }

            )
            instalment_capital_aggregate += _instalment_capital
            instalment_commission_aggregate += _instalment_commission
            instalment_interest_aggregate += _instalment_interest

            capital_oper -= _instalment_capital
            commission_oper -= _instalment_commission

            if capital_oper < 0 or commission_oper < 0:
                raise ValueError("Zbyt duża rata kapitałowa lub / i prowizyjna")

            if start_date:
                prev_dt = dt
                nominal_dt, dt = ProductScheduleUtils._get_next_date(
                    schedule_table_data=schedule_table_data,
                    idx=i + 1,
                    nominal_date=nominal_dt
                )
                days = ProductScheduleUtils._calculate_days(dt, prev_dt)

        # calculating last (balloon) instalment
        _instalment_interest, _ = ProductScheduleUtils._calculate_instalment_interest(
            start_date=prev_dt,
            end_date=dt,
            capital=capital_oper,
            instalment_interest_rates=instalment_interest_rates,
            current_rate=current_rate
        )

        schedule_table.append(
            {
                INSTALMENT_MATURITY_DATE_SELECTOR: dt or '',
                INSTALMENT_CAPITAL_SELECTOR: capital_oper,
                INSTALMENT_COMMISSION_SELECTOR: commission_oper,
                INSTALMENT_INTEREST_SELECTOR: _instalment_interest,
                INSTALMENT_TOTAL_SELECTOR: capital_oper + commission_oper + _instalment_interest,
                "days": days
            })

        instalment_capital_aggregate += capital_oper
        instalment_commission_aggregate += commission_oper
        instalment_interest_aggregate += _instalment_interest

        return {
            'sections': schedule_table,
            'aggregates': {
                'instalment_capital_aggregate': instalment_capital_aggregate,
                'instalment_commission_aggregate': instalment_commission_aggregate,
                'instalment_interest_aggregate': instalment_interest_aggregate
            }
        }

    @staticmethod
    def generate_schedule(product, instalment_capital, instalment_interest, instalment_commission, instalment_number, schedule_section=None):
        if not isinstance(product, Product):
            raise TypeError("Nieprawidłowy typ parametru 'product'")

        nominal_dt = py3ws_utils.add_month(product.start_date, 1)
        dt = py3ws_date_utils.set_schedule_work_day(py3ws_utils.add_month(product.start_date, 1))

        with (transaction.atomic()):
            ProductSchedule.objects.filter(product=product).delete()

            # get schedule section table data
            if schedule_section:
                attributes = []
                AttributeUtils().get_attributes(
                    document_type=product.document.type,
                    parent=DocumentTypeAttribute.objects.get(pk=schedule_section),
                    level=attributes,
                    only_data_items=True
                )

                # transform data into schedule
                schedule_table = {}
                for i in DocumentAttribute.objects.filter(
                        document_id=product.document.pk, attribute__pk__in=[i['id'] for i in attributes]
                ):
                    if i.row_sq not in schedule_table:
                        schedule_table[i.row_sq] = {i.attribute.id: i.value}
                        continue
                    schedule_table[i.row_sq][i.attribute.id] = i.value

                product_schedule_attributes_map = ProductScheduleUtils.map_instalment_schedule_attributes(attributes)

                product_schedule = []

                # create ProductSchedule rows
                for val in schedule_table.values():
                    product_schedule.append(
                        ProductSchedule(
                            product=product,
                            maturity_date=(val[product_schedule_attributes_map[INSTALMENT_MATURITY_DATE_SELECTOR]] or dt)
                            if product_schedule_attributes_map[
                                   INSTALMENT_MATURITY_DATE_SELECTOR] in val else dt,
                            instalment_capital=val[product_schedule_attributes_map[INSTALMENT_CAPITAL_SELECTOR]] if INSTALMENT_CAPITAL_SELECTOR in product_schedule_attributes_map else 0,
                            instalment_commission=val[product_schedule_attributes_map[INSTALMENT_COMMISSION_SELECTOR]] if INSTALMENT_COMMISSION_SELECTOR in product_schedule_attributes_map else 0,
                            instalment_interest=val[product_schedule_attributes_map[INSTALMENT_INTEREST_SELECTOR]] if INSTALMENT_INTEREST_SELECTOR in product_schedule_attributes_map else 0,
                            instalment_total=val[product_schedule_attributes_map[INSTALMENT_TOTAL_SELECTOR]] if INSTALMENT_TOTAL_SELECTOR in product_schedule_attributes_map else 0,
                        )
                    )
                    nominal_dt = py3ws_utils.add_month(nominal_dt, 1)
                    dt = py3ws_date_utils.set_schedule_work_day(nominal_dt)

                # save ProductSchedule schedule
                ProductSchedule.objects.bulk_create(product_schedule)

                return

            for i in range(0, instalment_number - 1):
                ProductSchedule.objects.create(
                    product=product,
                    maturity_date=dt,
                    instalment_capital=instalment_capital,
                    instalment_interest=instalment_interest,
                    instalment_commission=instalment_commission
                )
                nominal_dt = py3ws_utils.add_month(nominal_dt, 1)
                dt = py3ws_date_utils.set_schedule_work_day(nominal_dt)

            ProductSchedule.objects.create(
                product=product,
                maturity_date=dt,
                instalment_capital=product.capital_net - instalment_capital * (instalment_number - 1),
                instalment_interest=instalment_interest,
                instalment_commission=product.commission - instalment_commission * (instalment_number - 1)
            )
