from django.views import View
from py3ws.utils.utils import myimport
from django.db.models import Q
import json
from io import StringIO, BytesIO
from django.http import HttpResponse, StreamingHttpResponse
import csv
from django.conf import settings
from django.utils.dateformat import DateFormat
from django.utils import timezone


class List(View):
    def filter_sort(self, request, initial_queryset, form, default_sort_field):

        sort_field = default_sort_field
        sort_dir = ''

        qset = initial_queryset
        if request.method == 'POST':

            for i in form.fields:
                if i.startswith('p3_'):
                    continue

                classname = form.fields[i].__class__.__name__

                q1 = Q()
                q2 = Q()
                q = None

                if classname == 'DateTimeField':

                    d_from = request.POST.get(i + '__from')
                    d_to = request.POST.get(i + '__to')

                    if d_from:
                        q1 = Q(**{'{0}__{1}'.format(i, 'gte'): d_from})
                    if d_to:
                        q2 = Q(**{'{0}__{1}'.format(i, 'lte'): d_to})
                    q = Q(q1, q2)

                else:
                    value = request.POST.get(i)
                    if value:
                        if classname == 'LvTxt':
                            json_value = json.loads(value)

                            if not form.fields[i].multi:

                                if json_value['dtc']:
                                    q = Q(**{'{0}__dtc__{1}'.format(i, 'icontains'): json_value['dtc']})
                                else:
                                    q = Q(**{'{0}__custom__{1}'.format(i, 'icontains'): json_value['custom']})
                            else:

                                if json_value['dtc']:
                                    for n in json_value['dtc']:
                                        q1 |= Q(**{'{0}__dtc__{1}'.format(i, 'icontains'): n})
                                if json_value['custom']:
                                    q2 = Q(**{'{0}__custom__{1}'.format(i, 'icontains'): json_value['custom']})

                                q = Q(q1 | q2)
                        else:
                            q = Q(**{'{0}__{1}'.format(i, 'icontains'): value})

                if q:
                    qset = qset.filter(q)

            sort_field = request.POST.get('p3_sort_field') or 'issue_date'
            sort_dir = request.POST.get('p3_sort_dir') or ''

        return {'queryset': qset.order_by(sort_dir + sort_field), 'sort_field': sort_field, 'sort_dir': sort_dir}

    def csv(self, data, form, model):

        dict_class = settings.DICTIONARY_CLASS
        dtc_entry_class = myimport(dict_class)

        header = []
        header_names = []
        # f = BytesIO()
        # f.write(';'.join(header) + '\n')

        response_args = {'content_type': 'text/csv'}
        response = HttpResponse(**response_args)
        response['Content-Disposition'] = 'attachment; filename=%s;' % 'output.csv'
        response['Cache-Control'] = 'no-cache'

        response.write(u'\ufeff'.encode('utf8'))

        for i in form.fields:
            if i.startswith('p3_') or i.endswith('__from') or i.endswith('__to'):
                continue
            try:
                header.append(model._meta.get_field(i).verbose_name)
                header_names.append(i)
            except AttributeError:
                pass

        writer = csv.writer(response, delimiter=';', dialect='excel')
        writer.writerow(header)

        for i in data:
            row = []

            for j in header_names:

                try:
                    if i.__dict__[j] is not None:
                        if form.fields[j].__class__.__name__ == 'LvTxt':

                            val = i.__dict__[j]
                            dtc_entry = dtc_entry_class.objects.filter(pk__in=val['dtc'], dictionary__code=form.fields[j].dictname)

                            bundle_val = ''

                            for n in dtc_entry:
                                bundle_val += n.label + '|'

                            bundle_val += val['custom']
                            row.append(str(bundle_val))

                        elif form.fields[j].__class__.__name__ == 'DictChoiceField':
                            if not i.__dict__[j] is None and i.__dict__[j] != '':
                                dtc_entry = dtc_entry_class.objects.get(value=i.__dict__[j], dictionary__code=form.fields[j].dictname)

                                if dtc_entry:
                                    row.append(str(dtc_entry.label))
                                else:
                                    row.append('')
                            else:
                                row.append('')
                        elif form.fields[j].__class__.__name__ == 'DateTimeField':

                            val = DateFormat(timezone.localtime(i.__dict__[j]))

                            row.append(val.format('Y-m-d H:i:s'))
                        else:
                            row.append(str(i.__dict__[j]))

                    else:
                        row.append('')

                except KeyError:
                    row.append('')

            writer.writerow(row)

        return response












