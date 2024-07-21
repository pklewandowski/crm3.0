import calendar
import collections
import datetime

from django.db import connection

from apps.stat.summary_report.utils.stat import Stat

CUMULATIVE_INCOME_COUNT_SQL = """
select to_char(t.creation_date, 'YYYY-MM-DD')          as creation_date,
       sum(t.cnt) over (order by creation_date)        as cumulative,
       sum(t.amount_req) over (order by creation_date) as cumulative_amount_req,
       sum(t.amount_grt) over (order by creation_date) as cumulative_amount_grt
from (
         select count(1)                                                           cnt,
                sum(case when aa_rq.value = '' then 0 else aa_rq.value::float end) amount_req,
                sum(case when aa_gr.value = '' then 0 else aa_gr.value::float end) amount_grt,
                dd.creation_date::timestamp::date                                  creation_date
         from crm.document dd
                  left outer join crm.document_attribute aa_rq on aa_rq.id_attribute = 24 and aa_rq.document_id = dd.id
                  left outer join crm.document_attribute aa_gr on aa_gr.id_attribute = 103 and aa_gr.document_id = dd.id
         where dd.id_type = 1
         {status}
         group by dd.creation_date::timestamp::date
     ) t
where date_trunc('month', t.creation_date) = to_date('{dt}', 'YYYY-MM-DD')                                         
"""


class Dynamics(Stat):
    @staticmethod
    def get_data(date_1=None, date_2=None, date_3=None, status=None):
        result = {}
        date_1 = datetime.date.strftime(date_1, '%Y-%m-01') if date_1 else None
        date_2 = datetime.date.strftime(date_2, '%Y-%m-01') if date_2 else None
        date_3 = datetime.date.strftime(date_3, '%Y-%m-01') if date_3 else None

        for n in list(dict.fromkeys([date_1, date_2, date_3])):
            if not n:
                continue
            with connection.cursor() as c:
                c.execute(CUMULATIVE_INCOME_COUNT_SQL.format(**{
                    'dt': n,
                    'status': ('and dd.id_status in (%s)' % status) if status else ''
                }))

                date_split = list(map(lambda x: int(x), n.split('-')))
                year_month = '%d-%02d' % (date_split[0], date_split[1])

                last_count_value = 0
                last_amount_req_value = 0
                last_amount_grt_value = 0
                last_day = calendar.monthrange(date_split[0], date_split[1])[1]

                result[year_month] = []

                for i in c.fetchall():
                    d_split = list(map(lambda x: int(x), i[0].split('-')))
                    day = d_split[2]

                    while len(result[year_month]) < day:
                        result[year_month].append(
                            {'cnt': last_count_value,
                             'req': last_amount_req_value,
                             'grt': last_amount_grt_value
                             })

                    result[year_month][day - 1] = {
                        'cnt': int(i[1]),
                        'req': float(i[2] or 0),
                        'grt': float(i[3] or 0),
                    }
                    last_count_value = int(i[1])
                    last_amount_req_value = float(i[2] or 0)
                    last_amount_grt_value = float(i[3] or 0)

                while len(result[year_month]) < last_day:
                    result[year_month].append(
                        {'cnt': last_count_value,
                         'req': last_amount_req_value,
                         'grt': last_amount_grt_value
                         }
                    )

        return result
