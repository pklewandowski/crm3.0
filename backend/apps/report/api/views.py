import datetime
import json
import os
import traceback
import uuid

import pdfkit
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from pyvirtualdisplay import Display
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.document.models import Document, DocumentAttribute, DocumentTypeAttribute, DocumentReport
from apps.hierarchy.models import Hierarchy
from apps.report.api.serializers import ReportSerializer
from apps.report.models import ReportTemplate, Report
from apps.report.utils.params import Params
from apps.report.utils.render import set_jinja2_env
from py3ws.utils.utils import merge_two_dicts

BOOLEAN_VALUE_MAPPING = {'T': 'TAK', 'F': 'NIE', '': ''}


class ReportException(Exception):
    pass


class ReportApi(APIView):

    def __init__(self):
        super().__init__()
        self.document = None

    @rest_api_wrapper
    def get(self, request):
        return ReportSerializer(Report.objects.get(pk=request.query_params.get('id'))).data

    def post(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}
        header_path = None
        footer_path = None
        try:
            self.document = Document.objects.get(pk=request.data.get('documentId'))
            report_template = ReportTemplate.objects.get(code=request.data.get('templateCode'))
            preview = request.data.get('preview')
            query_params = json.loads(request.data.get('queryParams', '[]'))

            hierarchy = {i.pk: i for i in Hierarchy.objects.filter(type='CMP')}

            params = Params(document=self.document)

            jinja_env = set_jinja2_env()

            template = jinja_env.from_string(report_template.html_template)
            header_template = jinja_env.from_string(report_template.header_template_include.html_template if report_template.header_template_include else '')
            footer_template = jinja_env.from_string(report_template.footer_template_include.html_template if report_template.footer_template_include else '')

            header = ''
            if header_template:
                header = header_template.render({
                    "logo": settings.LOGO_BASE64,
                    "doc_creation_date": datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"),
                    "hierarchy": hierarchy
                })

            footer = ''
            if footer_template:
                footer = footer_template.render(
                    merge_two_dicts(
                        params.bind_params(report_template.footer_template_include.params_mapping),
                        {
                            "logo": settings.LOGO_BASE64,
                            "doc_creation_date": datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"),
                            "user": request.user,
                            "hierarchy": hierarchy
                        }
                    )
                )

            txt = template.render(
                merge_two_dicts(
                    params.bind_params(report_template.params_mapping),
                    {
                        "logo": settings.LOGO_BASE64,
                        "user": request.user,
                        "document": self.document,
                        # "product": self.document.product if self.document.product else {},
                        "doc_creation_date": datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d"),
                        "now_date": datetime.datetime.now(),
                        "hierarchy": hierarchy,

                        # "query": report_template.query.replace(report_template.query, dynaparams[re.match('(\$P__)(.*)(__P\$)')[2].lower()]) if report_template.source_type == 'QUERY' else ''
                        "query": Params.bind_query(report_template.query_json, query_params) if report_template.query_json else ''
                    })
            )

            report_name = '%s.pdf' % str(uuid.uuid4()).replace('-', '')
            _path = os.path.join(settings.MEDIA_ROOT, 'reports/%s' % ('temp' if preview else 'generated'))
            os.makedirs(_path, exist_ok=True)
            path = os.path.join(_path, report_name, )

            config = pdfkit.configuration(wkhtmltopdf=settings.WKHTMLTOPDF_PATH)

            if header:
                header_path = os.path.join(settings.MEDIA_ROOT, 'temp/%s.html' % str(uuid.uuid4()))
            if footer:
                footer_path = os.path.join(settings.MEDIA_ROOT, 'temp/%s.html' % str(uuid.uuid4()))

            if header_path:
                with open(header_path, 'w', encoding='utf-8') as f:
                    f.write(header)

            if footer_path:
                with open(footer_path, 'w', encoding='utf-8') as f:
                    f.write(footer)

            options = {
                "enable-local-file-access": None,
                'encoding': "UTF-8",
                # "--header-html": header_path,
                # "--footer-html": footer_path,
                # "margin-top": '15mm',
                # "margin-bottom": '30mm',
                # "margin-left": '5mm',
                # "margin-right": '5mm',
                # "--footer-center": "[page] / [topage]" to display pages but not not flexible if u have custom --footer-html
            }
            if header_path:
                options['--header-html'] = header_path
            if footer_path:
                options['--footer-html'] = footer_path

            options = merge_two_dicts(options, report_template.features)

            if os.name == 'nt':
                pdfkit.from_string(input=txt, output_path=path, configuration=config, options=options)
            else:
                # needed for linux error wkhtmltopdf cannot connect to x-display
                with Display():
                    pdfkit.from_string(input=txt, output_path=path, configuration=config, options=options)

            try:
                if header_path:
                    os.remove(header_path)
            except OSError:
                pass

            try:
                if footer_path:
                    os.remove(footer_path)
            except OSError:
                pass

            report = None

            if not preview:
                report = Report.objects.create(
                    xml_data=txt,
                    file_path=_path,
                    file_name=report_name,
                    created_by=request.user,
                    template=report_template, status='NW')

                DocumentReport.objects.create(
                    report=report,
                    file_name=report_name,
                    document=self.document,
                    created_by=request.user,
                    template=report_template
                )

            response_data = {'reportName': report_name, 'fullPath': path, 'reportId': report.pk if report else ''}

        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data['errmsg'] = _(str(ex))
            response_data['errmsg_trace'] = str(traceback.format_exc())

        return Response(data=response_data, status=response_status)

    @rest_api_wrapper
    def put(self, request):
        report = Report.objects.get(pk=request.data.get('id'))
        for k, v in request.data.items():
            setattr(report, k, v)
        report.save()

    @rest_api_wrapper
    def delete(self, request):
        with transaction.atomic():
            report = Report.objects.get(pk=request.data.get('id'))
            path = os.path.join(report.file_path, report.file_name)

            if os.path.exists(path):
                os.remove(path)

            report.delete()


class ReportTemplateApi(APIView):
    def __init__(self):
        super(ReportTemplateApi, self).__init__()
        self.document_id = None
        self.document = None

    def get_param_value(self, param, is_list=False, raise_error=False):
        q = Q(attribute=param, document_id=self.document_id)
        try:
            if is_list:
                return [i.value for i in DocumentAttribute.objects.filter(q)]
            return DocumentAttribute.objects.get(q).value
        except DocumentAttribute.DoesNotExist:
            if raise_error:
                raise ReportException('Wartość parametru nie jest wprowadzona i zapisana w atrybutach dokumentu (parametr: %s)' % DocumentTypeAttribute.objects.get(pk=param))
            return None

    def get_params(self, params):
        par = {}
        for k, v in params.items():
            if type(v).__name__ == 'list':
                par[k] = []
                for i in v:
                    par[k].append({'id': i, 'name': DocumentTypeAttribute.objects.get(pk=i).parent.name, 'value': self.get_param_value(i, is_list=True)})
            else:
                dta = DocumentTypeAttribute.objects.get(pk=v)
                par[k] = {'id': dta.pk, 'name': dta.name, 'value': self.get_param_value(v)}
        return par

    def get(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}

        template_id = request.query_params.get('templateId')
        self.document_id = request.query_params.get('documentId')

        try:
            rt = ReportTemplate.objects.get(pk=template_id)
            response_data['html_template'] = rt.html_template
            response_data['name'] = rt.name
            response_data['code'] = rt.code
            response_data['params'] = self.get_params(rt.params_mapping)
        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data['errmsg'] = _(str(ex))
            response_data['traceback'] = str(traceback.format_exc())
        return Response(data=response_data, status=response_status)
