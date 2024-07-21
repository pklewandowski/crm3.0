import os
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render

from apps.document.models import Document
from apps.report.models import ReportTemplate, Report
import crm_settings
from apps.report.utils.params import Params
from apps.report.utils.render import render_html_template
from py3ws.utils.utils import merge_two_dicts


def add(request, template_id, document_id):
    template = ReportTemplate.objects.get(pk=template_id)
    document = Document.objects.get(pk=document_id)

    params = Params(document=document)
    bind = params.bind_params(template.params_mapping)

    bind = merge_two_dicts(
        bind,
        {
            "user": request.user,
            "doc_creation_date": datetime.strftime(datetime.now(), "%Y-%m-%d")
        })

    return render(request, 'report/add.html', {'params': bind, 'txt': render_html_template(template.html_template, bind).replace('\n', ' ')})


def download(request, id):
    report = Report.objects.get(pk=id)

    if not report.file_name:
        raise Exception('Brak nazwy pliku raportu')
    output_file_path = os.path.join(crm_settings.MEDIA_ROOT, "reports/generated/") + report.file_name

    with open(output_file_path, 'r+b') as f:
        generation_date_suffix = datetime.strftime(datetime.now(), '%Y-%m-%d_%H%M%S')
        response = HttpResponse(f.read(), content_type='%s; %s' % ('application/pdf', 'charset=utf-8'))
        response['Content-Disposition'] = 'attachment; filename="%s_%s.pdf"' % (report.template.name.replace(' ', '_'), generation_date_suffix)
        f.close()

        return response
