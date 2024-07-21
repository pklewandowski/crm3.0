import os
from django.conf import settings

from apps.report.datasource_utils import ReportDatasourceUtils
from apps.report import data_utils as rep_data_utils


def set_xml_datasource(report, document, user, rd_form=None):
    xml = '<?xml version="1.0" encoding="UTF-8"?><document>'
    cl = ReportDatasourceUtils(document=document, user=user)

    for i in report.datasource_definition_set.all().order_by('sq'):
        if rd_form and i.tag_name in rd_form.cleaned_data:
            value = rd_form.cleaned_data[i.tag_name]
        else:
            value = cl.__getattribute__(i.getter_function)() if i.getter_function else ''
        xml += "<%s>%s</%s>" % (i.tag_name, "<![CDATA[%s]]>" % value if value else '', i.tag_name)
    xml += "</document>"

    return {'data_file_path': rep_data_utils._create_data_file(xml), 'data': xml}


def subreport_example(data_file, output_file, parameters):
    # input_file_header = os.path.dirname(os.path.abspath(__file__)) + \
    #                     '/examples/subreports/header.jrxml'
    #
    # input_file_details = os.path.dirname(os.path.abspath(__file__)) + \
    #                      '/examples/subreports/details.jrxml'
    #
    input_file_clients = os.path.join(settings.MEDIA_ROOT, 'reports/files/') + 'SCP_LOAN_DECISION_clients.jrxml'

    input_file_main = os.path.join(settings.MEDIA_ROOT, 'reports/files/') + 'SCP_LOAN_DECISION.jrxml'

    input_file = os.path.join(settings.MEDIA_ROOT, 'reports/files/') + 'SCP_LOAN_DECISION.jasper'

    data_file = data_file  # os.path.join(settings.MEDIA_ROOT, 'reports/data/') + 'scp_loan.xml'

    output = os.path.join(settings.MEDIA_ROOT, 'reports/output/')

    # jasper = PyReportJasper()
    #
    # jasper.compile(input_file_clients)
    # jasper.compile(input_file_main)
    #
    # jasper.process(
    #     input_file,
    #     output_file=output_file,
    #     format_list=["pdf"],
    #     parameters=parameters,
    #     db_connection={
    #         'data_file': data_file,
    #         'driver': 'xml',
    #         'xml_xpath': '/',
    #     },
    #     locale='pl_PL',  # LOCALE Ex.:(en_US, de_GE)
    #     resource=os.path.join(settings.MEDIA_ROOT, 'reports/files/')
    # )


def render(data_file, report_file, output_file):
    input_file = os.path.join(settings.MEDIA_ROOT, 'reports/files/') + report_file + '.jasper'

    output = os.path.join(settings.MEDIA_ROOT, 'reports/output/')

    jasper = JasperPy()

    jasper.process(
        input_file,
        output_file=output_file,
        format_list=["pdf"],
        parameters={},
        db_connection={
            'data_file': data_file,
            'driver': 'xml',
            'xml_xpath': '/document',
        },
        locale='pl_PL',  # LOCALE Ex.:(en_US, de_GE)
        resource=os.path.join(settings.MEDIA_ROOT, 'reports/files/')
    )
