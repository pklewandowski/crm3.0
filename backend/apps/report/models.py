from django.db.models import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.user.models import User


class ReportTemplate(models.Model):
    REPORT_TYPE_CHOICES = [('JASPER', 'jasper'), ('XLS', 'Excel template'), ('DOC', 'Word template'), ('HTML', 'Html template')]
    header_template_include = models.ForeignKey('self', db_column='id_header_template_include', null=True, blank=True, on_delete=models.CASCADE, related_name='header_template_include_set')
    footer_template_include = models.ForeignKey('self', db_column='id_footer_template_include', null=True, blank=True, on_delete=models.CASCADE, related_name='footer_template_include_set')
    html_template = models.TextField(verbose_name=_("report.template.html_template"), null=True, blank=True)
    name = models.CharField(verbose_name=_("report.template.name"), max_length=200)
    code = models.CharField(max_length=100)
    type = models.CharField(verbose_name='report.template.type', max_length=200, choices=REPORT_TYPE_CHOICES)
    description = models.TextField(verbose_name=_("report.template.description"), null=True, blank=True)
    file_name = models.CharField(verbose_name=_("report.template.file_name"), max_length=200, unique=True, db_index=True, null=True, blank=True)
    source_type = models.CharField(verbose_name="report.template.source_type", max_length=10, default='STATIC')
    query = models.TextField(verbose_name="report.template.source_type", null=True, blank=True)
    # todo: finally delete query field and use query_json
    query_json = JSONField(default=dict)

    params_mapping = JSONField(default=dict)
    root_dir = models.CharField(verbose_name=_("report.template.root_dir"), max_length=500, null=True, blank=True)

    features = JSONField(default=dict)

    class Meta:
        db_table = 'report_template'


class ReportDatasourceDefinition(models.Model):
    report = models.ForeignKey(ReportTemplate, db_column="id_report", on_delete=models.CASCADE, related_name='datasource_definition_set')
    parent = models.ForeignKey('self', db_column="id_parent", on_delete=models.CASCADE, null=True, blank=True)
    document_type_id = models.IntegerField(verbose_name='report.data.definition.document_type_id')
    document_attribute_id = models.IntegerField(verbose_name='report.data.definition.document_attribute_id', null=True, blank=True)
    name = models.CharField(verbose_name='report.data.definition.name', max_length=200, null=True, blank=True)
    tag_name = models.CharField(verbose_name='report.data.definition.tag_name', max_length=200)
    detail_section_id = models.IntegerField(verbose_name='report.data.definition.document_type_id', null=True, blank=True)
    getter_function = models.CharField(verbose_name='report.data.definition.getter_function', max_length=200, null=True, blank=True)
    mapping_column = models.CharField(verbose_name='report.data.definition.mapping_column', max_length=200, null=True, blank=True)
    format = models.CharField(verbose_name='report.data.definition.format', max_length=200, null=True, blank=True)
    type = models.CharField(verbose_name='report.data.definition.type', max_length=200, null=True, blank=True)
    editable = models.BooleanField(verbose_name='report.data.definition.editable', default=False)
    required = models.BooleanField(verbose_name='report.data.definition.editable', default=False)
    sq = models.IntegerField()

    class Meta:
        db_table = 'report_datasource_definition'


class Report(models.Model):
    # document = models.ForeignKey(Document, db_column="id_document", on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default='')
    code = models.CharField(max_length=200, null=True)
    template = models.ForeignKey(ReportTemplate, db_column="id_template", on_delete=models.CASCADE)
    xml_data = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, db_column='id_created_by', on_delete=models.CASCADE)
    status = models.CharField(max_length=10)
    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=300, null=True, blank=True)

    class Meta:
        db_table = 'report'
