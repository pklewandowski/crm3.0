import collections

from django.db import connection
from apps.stat.summary_report.utils.stat import Stat

ADVISER_RANK_SQL = """
select * 
from(
select uu_id, last_name, first_name, sum_val, sum(coalesce(sum_val, 0)) over (partition by uu_id) total, cnt, agr_type
from (
         select uu_id,
                last_name,
                first_name,
                coalesce(agr_type, 'XXX') agr_type,
                sum(val) sum_val,
                count(distinct (document_id)) cnt
         from (
                  select dd.id                                                                 document_id,
                         case when aa_val.value = '' then 0 else aa_val.value::float end       val,
                         case when aa_agr_type.value = '' then null else aa_agr_type.value end agr_type,
                         uu_adv.first_name                                                     first_name,
                         uu_adv.last_name                                                      last_name,
                         uu_adv.id                                                             uu_id
                  from crm.document dd
                           left outer join crm.document_attribute aa_val on aa_val.document_id = dd.id and aa_val.id_attribute = {amount_requested_id}
                           left outer join crm.document_attribute aa_agr_type on aa_agr_type.document_id = dd.id and aa_agr_type.id_attribute = {agreement_type_id}
                           left outer join crm.document_attribute aa_adv on aa_adv.document_id = dd.id and aa_adv.id_attribute = {adviser_id}
                           left outer join crm.user uu_adv on uu_adv.id = case when aa_adv.value = '' then null else aa_adv.value::int end
                  where dd.id_type = 1
           {date_from}
           {date_to}
           {advisers}
              ) t
         group by uu_id, last_name, first_name, agr_type
     )t1
     )t2
     where t2.total > 0
order by t2.total, t2.last_name
"""


class AdviserRank(Stat):
    @staticmethod
    def get_data(date_from=None, date_to=None, advisers=None):
        result = collections.OrderedDict()

        with connection.cursor() as c:
            c.execute(ADVISER_RANK_SQL.format(
                **{
                    'adviser_id': Stat.ATTRIBUTES['adviser_id'],
                    'broker_id': Stat.ATTRIBUTES['broker_id'],
                    'amount_requested_id': Stat.ATTRIBUTES['amount_requested_id'],
                    'amount_granted_id': Stat.ATTRIBUTES['amount_granted_id'],
                    'commission_id': Stat.ATTRIBUTES['commission_id'],
                    'agreement_type_id': Stat.ATTRIBUTES['agreement_type_id'],
                    'date_from': ("and dd.creation_date >= to_date('%s', 'YYYY-MM-DD')" % date_from) if date_from else '',
                    'date_to': ("and dd.creation_date <= to_date('%s', 'YYYY-MM-DD')" % date_to) if date_to else '',
                    'advisers': ("and aa_adv.value in(%s)" % advisers) if advisers else '',
                }
            ))

            for i in Stat.dictfetchall(c):
                if i['uu_id'] not in result:
                    result[i['uu_id']] = []
                result[i['uu_id']].append(i)

            return {'keys': [i for i in result.keys()], 'data': result}
