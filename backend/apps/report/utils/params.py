import importlib

from django.db.models import Q
from django.http import HttpRequest
from django.urls import resolve

from apps.document.models import DocumentAttribute, DocumentTypeAttribute
from py3ws.utils import utils as py3ws_utils


class Params:
    def __init__(self, document):
        self.document = document

    @staticmethod
    def bind_query(query: dict, query_params: dict):
        q = query['query_string']
        if not q:
            return ''
        for k, v in query_params.items():
            q = q.replace(f'$P__{k.upper()}__P$', str(v))
        return [i for i in py3ws_utils.get_class(query['class']).objects.raw(q)]

    def _bind_list_param(self, param):
        bind = []
        temp = {}
        length = 0

        for i in param:
            temp[i] = [k.value for k in DocumentAttribute.objects.filter(document_id=self.document.pk, attribute=i).order_by('row_uid', 'row_sq')]
            # there can be no value (no row present) for row attribute if it's null, so we have to get max value to take all rows in the list
            length = max(length, len(temp[i]))

        for i in range(length):
            p = {}
            for k in param:
                try:
                    p[k] = self._bind_param(param=k, value=temp[k][i], idx=i)
                except IndexError:
                    p[k] = ''
            bind.append(p)

        return bind

    def _bind_dynamic_url(self, url, val):
        fn = resolve(url).func

        request = HttpRequest()
        request.method = 'GET'
        request.GET = {'id': val}
        request.query_params = {'id': val}

        return fn(request).data

    def _bind_autocomplete_url_param(self, param, val):
        response_data = self._bind_dynamic_url(param.feature['autocomplete_url'], val)

        if not response_data:
            return None

        response_data = response_data['results']
        filtered = list(filter(lambda x: str(x['id']) == str(val), response_data))
        return filtered[0]['text'] if filtered else ''

    def _bind_lov_param(self, param, val, raise_error=False):
        for item in param.lov['data']:
            if item['lov_value'] == val:
                return {'value': val, 'label': item['lov_label']}
        if raise_error:
            raise Exception(f'[{self.__class__.__name__}]:_bind_lov_param: id: {val} not found in list attribute: {param.name} [{param.id}]')
        return ''

    def _bind_dynamic_lov_param(self, param, val):
        response_data = self._bind_dynamic_url(param.feature['dynamicLov']['url'], val)
        if not response_data:
            return None

        filtered = list(filter(lambda x: str(x['value']) == str(val), response_data))
        return {'value': val, 'label': filtered[0]['label']} if filtered else ''

    def _bind_param(self, param, value=None, idx=None, raise_error=False):
        try:
            param = DocumentTypeAttribute.objects.get(pk=param)
            if not value:
                q = Q(document_id=self.document.pk, attribute=param)
                if idx is not None:
                    q &= Q(row_sq=idx)
                val = DocumentAttribute.objects.get(q).value
            else:
                val = value

            if param.feature and isinstance(param.feature, dict) and 'dynamicLov' in param.feature and val:
                if 'dynamicLov' in param.feature:
                    val = self._bind_dynamic_lov_param(param, val)
                elif 'autocomplete_url' in param.feature:
                    val = self._bind_autocomplete_url_param(param, val)

            elif param.lov:
                val = self._bind_lov_param(param, val)

            elif param.attribute.subtype == 'percent':
                if val:
                    val = round(float(val) * 100, 2)
                else:
                    val = ''

            elif param.attribute.generic_datatype == 'boolean':
                val = 'tak' if val == 'T' else 'nie'

            return val or ''

        except DocumentAttribute.DoesNotExist:
            if not raise_error:
                return ''
            raise DocumentAttribute.DoesNotExist('brak parametru %s' % str(param))

    def bind_params(self, params):
        bind = {}

        for k, v in params.items():
            if isinstance(v, list):
                bind[k] = self._bind_list_param(v)
            else:
                bind[k] = self._bind_param(param=v)

        return bind
