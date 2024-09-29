from apps.user_func.client.models import Client
from apps.widget.current_contacts.api.serializers import ClientSerializerForCurrentContacts

RECORDS_PER_PAGE = 200
MIN_INFINITY = -9999999999
QUERY = f"""select t2.id,
                   max_event_date, date_diff
from (
         select id, 
         max_event_date, coalesce(max_event_date::date - current_date::date, {MIN_INFINITY}) date_diff
         from (
                  select uu.id, 
                         max(ss.start_date) max_event_date
                  from user_client cl,
                       "user" uu,
                       schedule ss,
                       schedule_user su1,
                       schedule_user su2
                  where uu.id = cl.id
                    and su1.id_schedule = su2.id_schedule
                    and su1.id_user = uu.id
                    and cl.id_adviser = %s
                    and su2.id_user = %s
                    and ss.id = su1.id_schedule
                  group by uu.id, uu.first_name, uu.last_name, uu.company_name, uu.phone_one, uu.email, cl.status, uu.tags
                  UNION ALL
                  select uu.id, 
                         null
                  from "user" uu,
                       user_client cl
                  where cl.id = uu.id
                    and cl.id_adviser = %s
                    and not exists(
                          select 1
                          from schedule_user su1,
                               schedule_user su2
                          where su1.id_schedule = su2.id_schedule
                            and su1.id_user = uu.id
                            and su2.id_user = %s
                      )
              ) t
     ) t2
order by t2.date_diff
"""


def get_list(request):
    page = int(request.query_params.get('p', 1)) - 1
    result = Client.objects.raw(QUERY, params=[request.user.pk, request.user.pk, request.user.pk, request.user.pk])
    count = len(result)

    return {
        'data': ClientSerializerForCurrentContacts(result[page * RECORDS_PER_PAGE: page * RECORDS_PER_PAGE + RECORDS_PER_PAGE], many=True).data,
        'count': count,
        'pages': count // RECORDS_PER_PAGE,
        'min_infinity': MIN_INFINITY
    }

