import collections
import pandas as pd
import numpy as np

from django.db import connection

from apps.document.models import DocumentTypeAttribute
from apps.stat.summary_report.utils.stat import Stat

from . import INCOME_SQL, INCOME_SQL_3



class Income(Stat):
    @staticmethod
    def get_data(date_from=None, date_to=None, status=None, advisers=None, brokers=None, business_type=None):
        result = collections.OrderedDict()
        business_type_str = ''
        if business_type:
            business_type_str = 'and uu_owner.is_company = %s' % ('TRUE' if business_type == 'B2B' else 'FALSE')

        with connection.cursor() as c:
            c.execute(INCOME_SQL.format(
                **{
                    'adviser_id': Stat.ATTRIBUTES['adviser_id'],
                    'broker_id': Stat.ATTRIBUTES['broker_id'],
                    'amount_requested_id': Stat.ATTRIBUTES['amount_requested_id'],
                    'amount_granted_id': Stat.ATTRIBUTES['amount_granted_id'],
                    'commission_id': Stat.ATTRIBUTES['commission_id'],
                    'agreement_type_id': Stat.ATTRIBUTES['agreement_type_id'],
                    'date_from': ("and dd.creation_date >= date_trunc('month', to_date('%s', 'YYYY-MM-DD'))" % date_from) if date_from else '',
                    'date_to': ("and dd.creation_date <= date_trunc('month', to_date('%s', 'YYYY-MM-DD'))" % date_to) if date_to else '',
                    'status': ('and dd.id_status in (%s)' % status) if status else '',
                    'advisers': ("and aa_adv.value in(%s)" % advisers) if advisers else '',
                    'brokers': ("and aa_brk.value in(%s)" % brokers) if brokers else '',
                    'bussiness_type': business_type_str,

                }
            ))

            for i in Stat.dictfetchall(c):
                if i['mc'] not in result:
                    result[i['mc']] = []
                result[i['mc']].append(i)
            return {'mc': [i for i in result.keys()], 'data': result}

    @staticmethod
    def get_pivot_data(date_from=None, date_to=None, status=None, advisers=None, brokers=None, business_type=None, agreement_type=None):
        business_type_str = ''
        if business_type:
            business_type_str = 'and uu_owner.is_company = %s' % ('TRUE' if business_type == 'B2B' else 'FALSE')

        with connection.cursor() as c:
            c.execute(INCOME_SQL_3.format(
                **{
                    'adviser_id': Stat.ATTRIBUTES['adviser_id'],
                    'broker_id': Stat.ATTRIBUTES['broker_id'],
                    'amount_requested_id': Stat.ATTRIBUTES['amount_requested_id'],
                    'amount_granted_id': Stat.ATTRIBUTES['amount_granted_id'],
                    'commission_id': Stat.ATTRIBUTES['commission_id'],
                    'agreement_type_id': Stat.ATTRIBUTES['agreement_type_id'],
                    'date_from': ("and dd.creation_date >= date_trunc('month', to_date('%s', 'YYYY-MM-DD'))" % date_from) if date_from else '',
                    'date_to': ("and dd.creation_date <= date_trunc('month', to_date('%s', 'YYYY-MM-DD')) + interval '1 month' - interval '1 day'" % date_to) if date_to else '',
                    'status': ('and dd.id_status in (%s)' % status) if status else '',
                    'advisers': ("and aa_adv.value in(%s)" % advisers) if advisers else '',
                    'brokers': ("and aa_brk.value in(%s)" % brokers) if brokers else '',
                    'bussiness_type': business_type_str,
                    'agreement_type': ("and aa_agr_type.value in(%s)" % agreement_type) if agreement_type else ''
                }
            ))
            ds = Stat.dictfetchall(c)

            if not ds:
                return {}

            data = pd.DataFrame(ds)[['adviser', 'mc', 'amount_req', 'amount_gr', 'commission']]

            pvt = data.pivot_table(
                values=['amount_req', 'amount_gr', 'commission'],
                columns='mc', index=['adviser'],
                aggfunc=['sum', 'count'],
                dropna=False,
                margins=True,
                margins_name='Suma',
                fill_value='-').sort_index(axis='columns', level='mc', ascending=False)
            return {
                'sum_req': pvt['sum']['amount_req'].to_dict('split')['data'],
                'count': pvt['count']['amount_req'].to_dict('split')['data'],
                'sum_gr': pvt['sum']['amount_gr'].to_dict('split')['data'],
                'sum_cm': pvt['sum']['commission'].to_dict('split')['data'],
                'index': pvt['sum']['amount_req'].to_dict('split')['index'],
                'columns': pvt['sum']['amount_req'].to_dict('split')['columns']
            }
