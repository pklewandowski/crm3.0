import pprint
import json
import traceback
import uuid
import os
import codecs
import datetime

from django.conf import settings
from django.core import serializers
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt

from py3ws.report.jasper.server import report_server

from apps.document.models import Document
from apps.report.models import ReportDatasourceDefinition, Report, ReportTemplate
from .forms import ReportForm
from apps.report import utils as report_utils


def index(request):
    return HttpResponse(_("reports index"))


def list(request):
    context = {}
    return render(request, 'report/list.html', context)


# @transaction.atomic()
# def add(request):
#     form = ReportForm(request.POST or None)
#
#     context = {'form': form}
#     return render(request, 'report/add.html', context)


def _genereate_datasource(id):
    datasource_definition = ReportDatasourceDefinition.objects.filter(parent__isnull=True).order_by('sq')


@transaction.atomic()
@csrf_exempt
def add(request):
    id = request.POST.get('id')
    response_data = {}
    status = 200
    try:
        document = Document.objects.get(pk=id)
        xml_data = report_utils.get_xml_data(document.pk, 2)
        res = Report.objects.filter(document=document, template=ReportTemplate.objects.get(pk=2))  # TODO: DRUT CHAMSKI!!!!!!!!!!!!
        if res:
            for i in res:
                i.status = 'ANL'
                i.save()
            cnt = res.count() + 1
        else:
            cnt = 1

        code = "%s/%s" % (document.code, cnt)

        file_name_uuid = str(uuid.uuid4())
        data_file_name = file_name_uuid + ".xml"
        output_file_name = file_name_uuid

        data_file_path = os.path.join(settings.MEDIA_ROOT, "reports/data/") + data_file_name
        output_file_path = os.path.join(settings.MEDIA_ROOT, "reports/output/") + output_file_name
        f = codecs.open(data_file_path, "w", "utf-8")
        f.write(xml_data)
        f.close()
        report_server.subreport_example(data_file=data_file_path,
                                        output_file=output_file_path,
                                        parameters={"p_currency": "zl", "p_status": 'PRJ', "p_code": code})

        report = Report.objects.create(document=document,
                                       code=code,
                                       status='PRJ',
                                       template=ReportTemplate.objects.get(pk=2),  # TODO: DRUT CHAMSKI!!!!!!!!!!!!
                                       xml_data=xml_data,
                                       created_by=request.user,
                                       file_name=output_file_name + '.pdf'
                                       )
        response_data['data'] = {
            'id': report.pk,
            'name': report.template.name,
            'code': report.code,
            'status': 'PRJ',
            'creation_date': datetime.datetime.strftime(report.creation_date, '%Y-%m-%d %H:%M:%S'),
            'created_by': '%s %s' % (report.created_by.first_name, report.created_by.last_name)
        }
    except Exception as e:
        status = 400
        response_data["errmsg"] = str(traceback.format_exc())
    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


# TODO: DRUT - jak najszybciej to poprawić!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def download(request, id):
    report = Report.objects.get(pk=id)
    xml_data = report.xml_data
    file_name_uuid = str(uuid.uuid4())
    data_file_name = file_name_uuid + ".xml"
    output_file_name = file_name_uuid

    data_file_path = os.path.join(settings.MEDIA_ROOT, "reports/data/") + data_file_name
    output_file_path = os.path.join(settings.MEDIA_ROOT, "reports/output/") + output_file_name
    f = codecs.open(data_file_path, "w", "utf-8")
    f.write(xml_data)
    f.close()
    report_server.subreport_example(data_file=data_file_path,
                                    output_file=output_file_path,
                                    parameters={"p_currency": "zl", "p_status": report.status, "p_code": report.code})

    with open(output_file_path + ".pdf", 'r+b') as f:
        response = HttpResponse(f.read(), content_type='%s; %s' % ('application/pdf', 'charset=utf-8'))
        response['Content-Disposition'] = 'attachment; filename="%s_%s.pdf"' % ('report', report.code.replace('/', '_'))
        f.close()
        os.remove(data_file_path)
        os.remove(output_file_path + ".pdf")
        return response



