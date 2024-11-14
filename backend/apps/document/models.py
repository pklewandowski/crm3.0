from django.db.models import JSONField, OuterRef, Exists, Q
from django.core import validators
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from apps.attachment.models import Attachment
from apps.attribute.models import Attribute
from apps.dict.models import Dictionary
from apps.hierarchy.models import Hierarchy

from apps.report.models import ReportTemplate, Report
from apps.user.models import User


# typy źródeł danych inicjalnych dla dokumentu
class DocumentSource(models.Model):
    document_type = models.ForeignKey('DocumentType', db_column='id_document_type', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    class_name = models.CharField(max_length=500)

    class Meta:
        db_table = 'document_source'
        unique_together = ('code', 'document_type')


class DocumentTypeAccountingType(models.Model):
    name = models.CharField(verbose_name='document.type.accounting.type.name', max_length=100)
    code = models.CharField(verbose_name='document.type.accounting.type.code', max_length=50)
    description = models.TextField(null=True, blank=True)
    direction = models.IntegerField(
        verbose_name=_('document.type.accounting.type.direction'))  # 1 - przepływ dodatni, -1 - przepływ ujemny
    is_editable = models.BooleanField(verbose_name=_('document.type.accounting.type.is_editable'), default=True)
    is_accounting_order = models.BooleanField(verbose_name=_('document.type.accounting.type.is_accounting_order'),
                                              default=True)
    # księgowane tylko w dniu wymagalności raty
    due_day_accounting_only = models.BooleanField(
        verbose_name=_('document.type.accounting.type.due_day_accounting_only'), default=False)
    min_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    subtypes = JSONField(default=dict)
    parent = models.ForeignKey('self', db_column='id_parent', null=True, blank=True, on_delete=models.CASCADE)
    sq = models.IntegerField(default=0)

    # TODO : powiązać typ przepływu z typem atrybutu

    def __str__(self):
        return str(self.name)

    @staticmethod
    def get_accounting_types(editable_only=True):
        q = Q(parent__isnull=True)
        if editable_only:
            q &= Q(is_editable=True)

        from apps.document.api.serializers import DocumentTypeAccountingTypeSerializer
        return {i['code']: i for i in DocumentTypeAccountingTypeSerializer(DocumentTypeAccountingType.objects.filter(q), many=True).data}

    class Meta:
        db_table = 'document_type_accounting_type'


class DocumentTypeCategory(models.Model):
    name = models.CharField(verbose_name=_('document.category.name'), max_length=200)
    code = models.CharField(verbose_name=_('document.category.code'), max_length=50)
    description = models.TextField(verbose_name=_('document.category.description'), null=True, blank=True)
    avatar_image = models.CharField(verbose_name='document.category.avatar_image', max_length=300, null=True,
                                    blank=True)
    attributes = JSONField(null=True, blank=True)
    sq = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'document_type_category'


# class DocumentTypeCategoryAttributes(models.Model):
#     name = models.CharField(max_length=300)
#     value = models.CharField(max_length=500)


class DocumentType(models.Model):
    category = models.ForeignKey(DocumentTypeCategory, verbose_name=_('Kategoria'), db_column='id_category',
                                 on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('Nazwa'), max_length=200)
    code = models.CharField(verbose_name=_('Kod'), max_length=50)
    owner_type = models.CharField(max_length=50)
    auto_generated_code_pattern = models.CharField(verbose_name=_('Pattern dla kodu automatycznego'), max_length=50,
                                                   null=True, blank=True)
    description = models.TextField(verbose_name=_('Opis'), null=True, blank=True)
    avatar_image = models.CharField(verbose_name='document.type.avatar_image', max_length=300, null=True, blank=True)
    icon_font_name = models.CharField(verbose_name=_('document.type.icon_font_name'), max_length=50, null=True,
                                      blank=True)
    editable = models.BooleanField(verbose_name=_('document.type.editable'), default=True)
    is_schedule = models.BooleanField(verbose_name=_('Posiada harmonogram'), default=False)

    is_interest = models.BooleanField(verbose_name=_('Posiada zarządzanie odsetkami'), default=False)

    is_product = models.BooleanField(verbose_name=_('document.type.is_product'), default=False)
    is_process_flow = models.BooleanField(verbose_name=_('document.type.is_process_flow'))
    is_shadow = models.BooleanField(verbose_name=_('document.type.is_shadow'))
    is_active = models.BooleanField(verbose_name=_('document.type.is_active'), default=True)
    is_code = models.BooleanField(verbose_name=_('document.type.is_code'))
    is_code_editable = models.BooleanField(verbose_name=_('document.type.is_code_editable'))
    is_owner = models.BooleanField(verbose_name=_('document.type.is_owner'))

    calculation_class = models.CharField(verbose_name=_('document.type.calculation_class'), max_length=500, null=True,
                                         blank=True)
    accounting_order = models.ManyToManyField(DocumentTypeAccountingType, through='DocumentTypeAccounting')
    form_name = models.CharField(max_length=200, verbose_name=_('document.type.form_name'), null=True, blank=True)
    form_attributes = JSONField(null=True, blank=True)
    attributes = JSONField(null=True, blank=True)
    model = JSONField(null=True, blank=True)
    financial_rules = JSONField(null=True, blank=True)
    settings = JSONField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'document_type'
        default_permissions = ('add', 'change')


class DocumentTypeSection(models.Model):
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', related_name='section_set',
                                      on_delete=models.CASCADE)
    parent = models.ForeignKey('self', db_column='id_parent', null=True, blank=True, related_name='children',
                               on_delete=models.CASCADE)
    parent_column = models.ForeignKey('DocumentTypeSectionColumn', db_column='id_parent_column', null=True, blank=True,
                                      related_name='column_children', on_delete=models.CASCADE)
    attributes = JSONField(null=True, blank=True)
    name = models.CharField(max_length=100)
    conditional_name_attribute = models.CharField(max_length=200, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    """
    view_type - dotyczy tylko sekcji powtarzalnych
    BLOCK - wyświetlanie jako bloku pól w zdefiniowanych kolumnach
    TABLE - wyświetlanie jako rekordu pól w tabeli
    """
    view_type = models.CharField(verbose_name=_('document.type.section.view.type'), max_length=10, default='BLOCK')
    sq = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'document_type_section'
        unique_together = ('document_type', 'name')


class DocumentTypeSectionColumn(models.Model):
    section = models.ForeignKey(DocumentTypeSection, db_column='section_id', related_name='column_set',
                                on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('attribute.section.column.panel_name'), max_length=200, null=True,
                            blank=True)
    lg_width = models.IntegerField(verbose_name=_('attribute.section.column.lg_width'), null=True, blank=True,
                                   validators=[validators.MinValueValidator(1), validators.MaxValueValidator(12)])
    md_width = models.IntegerField(verbose_name=_('attribute.section.column.md_width'), null=True, blank=True,
                                   validators=[validators.MinValueValidator(1), validators.MaxValueValidator(12)])
    sm_width = models.IntegerField(verbose_name=_('attribute.section.column.sm_width'),
                                   validators=[validators.MinValueValidator(1), validators.MaxValueValidator(12)])
    xs_width = models.IntegerField(verbose_name=_('attribute.section.column.xs_width'), null=True, blank=True,
                                   validators=[validators.MinValueValidator(1), validators.MaxValueValidator(12)])
    sq = models.IntegerField(verbose_name=_('attribute.section.column.sq'), blank=True)

    def __str__(self):
        return str(self.sq)

    class Meta:
        db_table = 'document_type_section_column'
        ordering = ['section', 'sq']


class DocumentTypeAccounting(models.Model):
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', on_delete=models.CASCADE)
    accounting_type = models.ForeignKey(DocumentTypeAccountingType, db_column='id_accounting_type',
                                        on_delete=models.CASCADE)
    sq = models.IntegerField()

    def __str__(self):
        return str((self.document_type.name or 'nodoctype') + '.' + (self.accounting_type.name or 'noacctype'))

    class Meta:
        db_table = 'document_type_accounting'
        unique_together = ('document_type', 'accounting_type')


class DocumentTypeVersionDefinition(models.Model):
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', related_name='definition_set',
                                      on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    status = models.CharField(max_length=3)
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_type_version_definition'


class DocumentTypeAttribute(models.Model):
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', related_name='attribute_set',
                                      on_delete=models.CASCADE)
    dictionary = models.ForeignKey(Dictionary, db_column='dictionary',
                                   verbose_name=_('document.type.attribute.dictionary'),
                                   null=True, blank=True, on_delete=models.CASCADE)
    attribute = models.ForeignKey(Attribute, db_column='id_attribute',
                                  verbose_name=_('document.type.attribute.attribute'), null=True, blank=True,
                                  on_delete=models.CASCADE)
    parent = models.ForeignKey('self', db_column='id_parent', null=True, blank=True, related_name='children_set',
                               on_delete=models.CASCADE)
    # type - Type of attribute, if ATTR then standard attribute, when FORM then attribute of main document form
    type = models.CharField(max_length=10, default='ATTR', verbose_name=_('document.type.attribute.type'))
    name = models.CharField(max_length=300, verbose_name=_('document.type.attribute.name'))
    name_short = models.CharField(max_length=50, verbose_name=_('document.type.attribute.name_short'), null=True,
                                  blank=True)
    # iconic symbol class of an attribute
    name_icon = JSONField(null=True, blank=True, default=dict)
    code = models.CharField(max_length=100, verbose_name=_('document.type.attribute.code'), null=True, blank=True)
    width_prc = models.IntegerField(validators=[MinValueValidator(limit_value=1), MaxValueValidator(limit_value=100)],
                                    null=True, blank=True)
    feature = JSONField(null=True, blank=True, default=dict)
    css_class = models.CharField(verbose_name=_('document.type.attribute.css_class'), max_length=200, null=True,
                                 blank=True)
    selector_class = models.CharField(verbose_name=_('document.type.attribute.selector_class'), max_length=200,
                                      null=True, blank=True)
    lov = JSONField(null=True, blank=True, default=dict)
    dependency = JSONField(null=True, blank=True, default=dict)
    description = models.TextField(null=True, blank=True, verbose_name=_('document.type.attribute.description'))
    placeholder = models.CharField(max_length=300, null=True, blank=True,
                                   verbose_name=_('document.type.attribute.placeholder'))
    default_value = models.TextField(null=True, blank=True, verbose_name=_('document.type.attribute.default_value'))
    is_required = models.BooleanField(default=False, verbose_name=_('document.type.attribute.is_required'))
    is_table = models.BooleanField(default=False, verbose_name=_('document.type.attribute.is_table'))
    is_section = models.BooleanField(default=False, verbose_name=_('document.type.attribute.is_section'))
    is_column = models.BooleanField(default=False, verbose_name=_('document.type.attribute.is_column'))
    is_combo = models.BooleanField(default=False, verbose_name=_('document.type.attribute.is_combo'))
    is_active = models.BooleanField(default=True, verbose_name=_('document.type.attribute.is_active'))
    hierarchy = JSONField(null=True, blank=True)
    # container indicates where (under what parent dom element) section is to be rendered. It only applies to section with NO PARENT specified
    # it is made for handling FORM-like attributes separately from ATTR-like attributes but to be possible to put ATTR attributes together with FORM attributes in one tab/layout
    container = models.CharField(max_length=300, null=True, blank=True)
    sq = models.IntegerField(default=0, verbose_name=_('document.type.attribute.sq'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'document_type_attribute'
        unique_together = [('document_type', 'code')]
        constraints = [
            models.CheckConstraint(
                name='section_container_chk',
                check=(models.Q(container__isnull=True, parent__isnull=False) | models.Q(parent__isnull=True))
            ),
            models.CheckConstraint(
                name='code_double_undsarscore_preventer_chk',
                check=(~models.Q(code__startswith='__'))
            ),
        ]


class DocumentTypeAssociate(models.Model):
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    class_name = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'document_type_associate'


class DocumentTypeAttributeFeature(models.Model):
    attribute = models.ForeignKey(DocumentTypeAttribute,
                                  db_column='id_document_type_attribute',
                                  on_delete=models.CASCADE,
                                  related_name='feature_set')
    status = models.ForeignKey('DocumentTypeStatus', db_column='id_document_type_status', on_delete=models.CASCADE)
    visible = models.BooleanField()
    editable = models.BooleanField()
    required = models.BooleanField()
    # flaga informująca, czy ma być wypełniane pole value_operator - dla dwustopniowej walidacji danych
    value_operator = models.BooleanField(default=False)
    permission = JSONField(null=True, blank=True)

    class Meta:
        db_table = 'document_type_attribute_feature'
        unique_together = ('attribute', 'status')


class DocumentAttribute(models.Model):
    attribute = models.ForeignKey(DocumentTypeAttribute, db_column='id_attribute', related_name='attribute_value_set',
                                  on_delete=models.CASCADE)
    parent = models.ForeignKey('self', db_column='id_parent', null=True, blank=True, on_delete=models.CASCADE)
    document_id = models.IntegerField(verbose_name=_('document.attribute.document_id'))
    # value - wartość zatwierdzona przez weryfikatora
    value = models.TextField(null=True, blank=True)  # typ wartości będzie brany z attribute
    # data-meta_xxx value for the field (ie. <input type="text" .... data-meta_change_flag = 1 />
    # then entry is going ot be like this: {"change_meta": "1"}
    value_data_meta = JSONField(default=dict)
    # value_operator - wartość wprowadzana przez operatora
    value_operator = models.TextField(null=True, blank=True)
    value_text = models.TextField(null=True, blank=True)
    row_sq = models.IntegerField(null=True, blank=True)
    row_uid = models.CharField(max_length=200, null=True, blank=True)
    history = HistoricalRecords(table_name='h_document_attribute')

    class Meta:
        db_table = 'document_attribute'
        unique_together = ('document_id', 'attribute', 'row_uid', 'row_sq')


class Document(models.Model):
    type = models.ForeignKey(DocumentType, db_column='id_type', related_name="document_type_set",
                             on_delete=models.CASCADE)
    owner = models.ForeignKey(User, verbose_name=_('document.owner'), db_column='id_owner', related_name="owner_set",
                              on_delete=models.CASCADE)
    # remove this field cause it brokes universality of document intentions
    # lender = models.ForeignKey(Hierarchy, verbose_name=_('document.lender'), db_column='id_lender', related_name="lender_set", on_delete=models.CASCADE)
    responsible = models.ForeignKey(User, verbose_name=_('document.responsible'), db_column='id_responsible', null=True,
                                    blank=True, related_name="responsible_set", on_delete=models.CASCADE)
    annex = models.OneToOneField('self', db_column='id_annex', null=True, blank=True, on_delete=models.DO_NOTHING,
                                 related_name='document_annex', unique=True)
    annexed_by = models.OneToOneField('self', db_column='id_annexed_by', null=True, blank=True,
                                      on_delete=models.DO_NOTHING, related_name='document_annexed_by', unique=True)
    hierarchy = models.ForeignKey(Hierarchy, null=True, blank=True, on_delete=models.CASCADE)
    status = models.ForeignKey('DocumentTypeStatus', db_column='id_status', verbose_name=_('document.status'),
                               blank=True, on_delete=models.CASCADE)
    code = models.CharField(verbose_name=_('document.code'), max_length=50, null=True, blank=True)
    # document number given by the user
    custom_code = models.CharField(verbose_name=_('document.custom_code'), max_length=50, null=True, blank=True)
    creation_date = models.DateTimeField(verbose_name=_('document.creation_date'), auto_now_add=True)
    created_by = models.ForeignKey(User, verbose_name=_('document.created_by'), db_column='id_created_by',
                                   related_name='document_created_by', on_delete=models.PROTECT)
    description = models.TextField(verbose_name=_('document.description'), null=True, blank=True)
    form_data = JSONField(null=True, default=dict, verbose_name=_('document.form_data'))
    attachments = models.ManyToManyField(Attachment, through='DocumentAttachment')
    history = HistoricalRecords(table_name='h_document')

    def __str__(self):
        return self.code or 'BRAK'

    class Meta:
        db_table = 'document'
        constraints = [
            models.UniqueConstraint(fields=['type', 'code'], name='document_type_code_uq'),
            # models.UniqueConstraint(fields=['type', 'custom_code'], name='document_type_code_uq_1')
        ]
        default_permissions = ()
        verbose_name = _('Dokument')
        verbose_name_plural = _('Dokumenty')
        permissions = (
            ('view:all', _('permissions.app.document.view.all')),
            ('view:department', _('permissions.app.document.view.department')),
            ('view:position', _('permissions.app.document.view.position')),
            ('view:own', _('permissions.app.document.view.own')),

            ('list:all', _('permissions.app.document.list.all')),
            ('list:department', _('permissions.app.document.list.department')),
            ('list:position', _('permissions.app.document.list.position')),
            ('list:own', _('permissions.app.document.list.own')),

            ('add:all', _('permissions.app.document.add.all')),
            ('add:department', _('permissions.app.document.add.department')),
            ('add:position', _('permissions.app.document.add.position')),
            ('add:own', _('permissions.app.document.add.own')),

            ('change:all', _('permissions.app.document.change.all')),
            ('change:department', _('permissions.app.document.change.department')),
            ('change:position', _('permissions.app.document.change.position')),
            ('change:own', _('permissions.app.document.change.own')),
        )


class DocumentScan(models.Model):
    document = models.ForeignKey(Document, db_column='id_document', on_delete=models.CASCADE, related_name='scan_set')
    file_name = models.CharField(max_length=300)
    file_path = models.CharField(max_length=500)
    ocr_text = models.TextField(null=True, blank=True)
    sq = models.IntegerField()
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, db_column='id_user', on_delete=models.CASCADE)

    class Meta:
        db_table = 'document_scan'


class DocumentStatusCourse(models.Model):
    """
    DocumentStatusCourse entity
    stores only the 'default' change route of document statuses. if we have 3 statuses: A, B, C and
    the way is A(2020-01-01)->B(2020-01-02)->A(2020-01-03)->B(2020-01-04)->C(2020-01-05)->B(2020-01-06),
    in DocumentStatusCourse there will be only A(2020-01-01)->B(2020-01-06) entry.
    Another words it doesn't track changes, but deletes entry when user back status
    """
    document = models.ForeignKey(Document, db_column='id_document', db_index=True, related_name='status_course',
                                 on_delete=models.CASCADE)
    status = models.ForeignKey('DocumentTypeStatus', db_column='id_status', db_index=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, db_column='id_user', on_delete=models.CASCADE)
    effective_date = models.DateTimeField(default=timezone.now)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'document_status_course'


class DocumentStatusTrack(models.Model):
    """
    DocumentStatusTrack
    track all the status changes of given document with chance to descripbe reason of change
    """
    document = models.ForeignKey(Document, db_column='id_document', db_index=True, related_name='status_track',
                                 on_delete=models.CASCADE)
    status = models.ForeignKey('DocumentTypeStatus', db_column='id_status', db_index=True, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, db_column='id_created_by', on_delete=models.CASCADE)
    effective_date = models.DateTimeField(default=timezone.now)
    creation_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(null=True, default=_('standard.process.flow'))

    class Meta:
        db_table = 'document_status_track'
        ordering = ['creation_date']


class DocumentNote(models.Model):
    document = models.ForeignKey(Document, db_column='id_document', related_name='note_set', on_delete=models.CASCADE)
    document_status_track = models.ForeignKey(DocumentStatusTrack,
                                              db_column='id_document_status_track',
                                              related_name='track_note_set',
                                              on_delete=models.CASCADE,
                                              null=True,
                                              blank=True)
    header = models.CharField(max_length=300, null=True)
    text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, db_column='id_created_by', related_name='created_by_set',
                                   on_delete=models.PROTECT)
    update_date = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, db_column='id_updated_by', related_name='updated_by_set',
                                   on_delete=models.PROTECT)
    history = HistoricalRecords(table_name='h_document_note')

    class Meta:
        db_table = 'document_note'


class DocumentAttachment(models.Model):
    document = models.ForeignKey(Document, db_column='id_document', related_name='attachment_set',
                                 on_delete=models.CASCADE)
    parent = models.ForeignKey('self', db_column='id_parent', on_delete=models.CASCADE, null=True)
    attachment = models.ForeignKey(Attachment, db_column='id_attachment', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=200, null=True)
    is_dir = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, db_column='id_created_by', on_delete=models.PROTECT)

    class Meta:
        db_table = 'document_attachment'


class DocumentTypeStatus(models.Model):
    type = models.ForeignKey(DocumentType, db_column='id_type', related_name='status_set', on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('document.type.status.name'), max_length=100)
    code = models.CharField(verbose_name=_('document.type.status.code'), max_length=10)
    permission = models.CharField(verbose_name=_('document.type.status.permission'), max_length=200)
    is_initial = models.BooleanField(verbose_name=_('document.type.status.is_initial'))
    is_product = models.BooleanField(verbose_name=_('document.type.status.is_product'), default=False)
    is_active = models.BooleanField(verbose_name=_('document.type.status.is_active'), default=True)
    is_alternate = models.BooleanField(verbose_name=_('document.type.status.is_alternate'), default=False)
    is_required_validation = models.BooleanField(verbose_name=_('document.type.status.is_required_validation'),
                                                 default=False)
    is_closing_process = models.BooleanField(verbose_name=_('document.type.status.is_closing_process'), default=False)
    can_revert = models.BooleanField(verbose_name=_('document.type.status.can_revert'), default=True)
    action_class = models.CharField(max_length=300, null=True, blank=True)
    action = models.CharField(max_length=300, null=True, blank=True)
    common_action = JSONField(null=True)
    redirect = models.CharField(verbose_name=_('document.type.redirect'), max_length=200, null=True, blank=True)
    sq = models.IntegerField(default=0)
    hierarchies = JSONField(null=True)
    color = models.CharField(verbose_name=_('document.type.status.can_revert'), max_length=8, default='ffffff')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'document_type_status'
        default_permissions = ('add', 'change')
        permissions = (
            ('list_document_status', _('permissions.app.document.status.list_document_status')),
        )


class DocumentTypeStatusFlow(models.Model):
    status = models.ForeignKey(DocumentTypeStatus, db_column='id_status', on_delete=models.CASCADE)
    hierarchy = models.ForeignKey(Hierarchy, db_column='id_hierarchy', on_delete=models.CASCADE)

    class Meta:
        db_table = 'document_type_status_flow'


class DocumentTypeProcessFlow(models.Model):
    status = models.ForeignKey(DocumentTypeStatus, db_column='id_current_status', related_name='status',
                               on_delete=models.CASCADE)
    available_status = models.ForeignKey(DocumentTypeStatus, db_column='id_available_status', null=True, blank=True,
                                         related_name='available_status', on_delete=models.CASCADE)
    is_note_required = models.BooleanField()
    is_default = models.BooleanField(default=False)
    sq = models.IntegerField()

    class Meta:
        db_table = 'document_type_process_flow'


class DocumentTypeAttributeMapping(models.Model):
    type = models.ForeignKey(DocumentType, db_column='id_type', related_name='attribute_mapping_set',
                             on_delete=models.CASCADE)
    attribute = models.ForeignKey(DocumentTypeAttribute, db_column='id_document_type_atribute',
                                  related_name='mapping_set', on_delete=models.CASCADE, null=True)
    mapped_name = models.CharField(verbose_name=_('document.type.attribute.mapping.mapped_name'), max_length=200)
    is_required = models.BooleanField(verbose_name=_('document.type.attribute.mapping.is_required'), default=True)
    default_value = models.CharField(max_length=500, null=True)
    description = models.TextField(null=True)

    class Meta:
        db_table = 'document_type_attribute_mapping'
        unique_together = ('type', 'attribute', 'mapped_name')


class DocumentTypeReport(models.Model):
    document_type = models.ForeignKey(DocumentType, db_column='id_document_type', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='document.type.report.name', max_length=200)
    template = models.ForeignKey(ReportTemplate, db_column='id_template', on_delete=models.CASCADE, null=True,
                                 blank=True)
    # report html content covering placeholders in form of $P__ATTRIBUTE_ID__P$ to be filled with data when created
    # Data source for reports comes from document attribute as well as from document main form
    html_template = models.TextField(null=True, blank=True, verbose_name='document.type.report.html_template')

    # flag if report can be fired manually by the user. If false, report can be fired only within the document processing flow
    is_manual = models.BooleanField(verbose_name='document.type.report.html_template', default=True)
    sq = models.IntegerField(default=0)

    class Meta:
        db_table = 'document_type_report'


class DocumentTypeReportAttributeMapping(models.Model):
    report = models.ForeignKey(DocumentTypeReport, on_delete=models.CASCADE)
    attribute = models.ForeignKey(DocumentTypeAttribute, db_column='id_attribute', on_delete=models.CASCADE)
    # mapping can be a cell descriptor (like "A:52" in case of xls template report) or parameter name (ie. 454 wchich be converted to [P_454_P]) -
    # in case of word template report
    # or the code of the parameter in case of jasper or any other future report type
    mapping = models.CharField(max_length=200)
    idx = models.IntegerField(null=True)

    class Meta:
        db_table = 'document_type_report_attribute_mapping'


class DocumentReport(models.Model):
    document = models.ForeignKey(Document, db_column='id_document', on_delete=models.CASCADE)
    report = models.ForeignKey(Report, db_column='id_report', on_delete=models.CASCADE, null=True)
    created_by = models.ForeignKey(User, db_column='id_created_by', on_delete=models.CASCADE)
    template = models.ForeignKey(ReportTemplate, db_column='id_template', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=500)

    class Meta:
        db_table = 'document_report'
