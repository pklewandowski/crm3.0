import copy
import datetime
import datetime
import json
import re
from abc import abstractmethod

from django.conf import settings
from django.db import transaction
from django.db.models import Q

from apps.attachment.models import Attachment
from apps.document.type.attribute import utils as attribute_utils
from py3ws.views.generic_view import GenericView
from .models import DocumentType, DocumentTypeSection, DocumentTypeAttribute, \
    DocumentAttribute, DocumentTypeAccountingType, DocumentTypeStatus, DocumentTypeProcessFlow, DocumentTypeStatusFlow, \
    DocumentAttachment, Document
from ..product.models import ProductTypeProcessFlow


class DocumentSourceException(Exception):
    pass


class DocumentSourceAbstract:
    def __init__(self, *args, **kwargs):
        self.document_type = self.get_document_type()
        self.source = self.get_source()
        self.initial_data = self.get_initial_data()
        self.document = None

    @abstractmethod
    def get_source(self):
        raise NotImplementedError

    @abstractmethod
    def get_document_type(self):
        raise NotImplementedError

    @abstractmethod
    def get_initial_data(self):
        raise NotImplementedError

    @abstractmethod
    def get_initial_attributes(self):
        raise NotImplementedError

    @abstractmethod
    def complete(self, document):
        raise NotImplementedError


def get_document_type(code):
    try:
        return DocumentType.objects.get(code=code)
    except DocumentType.DoesNotExist:
        return None


def _get_attribute_set(section, attribute_feature):
    if attribute_feature:
        attribute_set = []
        for c in section.column_set.all().order_by('sq'):
            attr = []
            for atr in section.attribute_set.filter(section_column=c, parent__isnull=True).order_by('sq'):
                if attribute_feature[atr.pk]['visible']:
                    attr.append(atr)
            attribute_set.append({'column': c, 'attributes': attr})

    else:
        attribute_set = [
            {'column': c, 'attributes': section.attribute_set.filter(section_column=c).order_by('sq')}
            for c in section.column_set.all().order_by('sq')
        ]

    return attribute_set


def get_attributes(id, status=None):
    document_type = DocumentType.objects.get(pk=id)
    sections = DocumentTypeSection.objects.filter(document_type=document_type, parent=None).order_by('sq')
    attributes = []

    attribute_feature = attribute_utils.get_attribute_features(document_type=document_type, status=status) if status else None

    for i in sections:
        attributes.append({'section': i,
                           'columns': _get_attribute_set(i, attribute_feature),
                           'children': [{'section': child,
                                         'columns': _get_attribute_set(child, attribute_feature)} for child in i.children.all().order_by('sq')]  # children
                           })
    return attributes


def get_table_attributes(id):
    return DocumentTypeAttribute.objects.filter(parent=id).order_by('sq')


def get_document_attribute_values(id, id_type):
    document_type = DocumentType.objects.get(pk=id_type)
    document_type_attributes = [i for i in DocumentTypeAttribute.objects.filter(document_type=document_type,
                                                                                section__parent__isnull=True,
                                                                                is_table=False,
                                                                                parent__isnull=True).prefetch_related('attribute')]
    document_attributes = {i.attribute.code: i for i in DocumentAttribute.objects.filter(document_id=id)}

    attributes = {}

    for i in document_type_attributes:
        try:
            at = document_attributes[i.code]
            if i.attribute.generic_datatype == 'boolean':
                val = '' if not at.value or at.value == 'False' else 'True'
                attributes[i.code] = val
            else:
                attributes[i.code] = at.value
        except KeyError:
            attributes[i.code] = None
    return attributes


def get_visible_attributes(document_type, status, children=False):
    if not status:
        r = DocumentTypeAttribute.objects.filter(document_type=document_type, section__parent__isnull=True)
    else:
        r = DocumentTypeAttribute.objects.filter(
            document_type=document_type,
            section__parent__isnull=True,
            feature_set__status=status,
            feature_set__visible=True
        )
    return r


def _handle_file_field(value, id, user):
    if not value:
        return
    _value = json.loads(value)
    document = Document.objects.get(pk=id)
    for i in _value:
        try:
            attachment = Attachment.objects.get(file_name=i['file_name'])
            try:
                DocumentAttachment.objects.get(attachment=attachment)
            except DocumentAttachment.DoesNotExist:
                DocumentAttachment.objects.create(attachment=attachment, document=document)
        except Attachment.DoesNotExist:
            attachment = Attachment.objects.create(
                file_name=i['file_name'],
                file_ext=i['file_name'].split('.')[-1],
                file_mime_type=i['file_mime_type'],
                file_path=i['file_path'],
                file_original_name=i['file_original_name'],
                type='file',
                user=user
            )
            DocumentAttachment.objects.create(attachment=attachment, document=document)


def _save_main_attributes(form_data, attr, curr_attr, id, user):
    for i in attr:
        # kontener atrybutów tabelarycznych będzie zapisany w _save_table_attributes
        if i.is_table:
            continue
        attr = None
        if i.code in curr_attr:
            attr = curr_attr[i.code]
            if curr_attr[i.code].value != form_data[i.code]:
                curr_attr[i.code].value = form_data[i.code]
                curr_attr[i.code].save()
        else:
            try:
                attr = DocumentAttribute.objects.create(attribute=i, value=form_data[i.code] or None, document_id=id)
            except KeyError:
                pass

        if attr and attr.attribute.attribute.generic_datatype == 'file':
            _handle_file_field(value=curr_attr[i.code].value, user=user, id=id)


def _save_repeated_subsections(section_formsets, id, user):
    for k, forms in section_formsets.items():

        for idx, form in enumerate(forms):
            row_uid = form.cleaned_data.get('row_uid')

            if form.cleaned_data.get('DELETE'):
                DocumentAttribute.objects.filter(row_uid=row_uid).delete()
                continue

            del form.cleaned_data['row_uid']
            del form.cleaned_data['DELETE']

            curr_attr = {i.attribute.code: i for i in DocumentAttribute.objects.filter(document_id=id, row_uid=row_uid)}

            for dk, dv in form.cleaned_data.items():
                if dk in curr_attr:
                    attr = curr_attr[dk]
                    curr_attr[dk].value = dv
                    curr_attr[dk].row_sq = idx
                    curr_attr[dk].save()
                else:
                    attr = DocumentAttribute.objects.create(
                        attribute=DocumentTypeAttribute.objects.get(code=dk),
                        value=dv or None,
                        document_id=id,
                        row_uid=row_uid,
                        row_sq=idx
                    )

                if attr.attribute.attribute.generic_datatype == 'file':
                    _handle_file_field(value=dv, user=user, id=id)


def _save_table_attributes(table_formsets, id, user):
    for k, forms in table_formsets.items():
        parent = DocumentTypeAttribute.objects.get(pk=k)

        for idx, form in enumerate(forms['formset']):

            row_uid = form.cleaned_data.get('row_uid')
            parent_row_uid = form.cleaned_data.get('parent_row_uid')
            try:
                tab_parent = DocumentAttribute.objects.get(document_id=id, row_uid=parent_row_uid, attribute=parent)
            except DocumentAttribute.DoesNotExist:
                tab_parent = DocumentAttribute.objects.create(
                    attribute=parent,
                    document_id=id,
                    row_uid=parent_row_uid,
                    row_sq=0
                )
                # raise Exception('Brak obiektu rodzica (kontenera tabeli) dla atrybutu tabelatycznego: %s' % parent.name)

            if form.cleaned_data.get('DELETE'):
                DocumentAttribute.objects.filter(row_uid=row_uid).delete()
                continue

            del form.cleaned_data['parent_row_uid']
            del form.cleaned_data['row_uid']
            del form.cleaned_data['DELETE']

            curr_attr = {i.attribute.code: i for i in DocumentAttribute.objects.filter(
                document_id=id,
                row_uid=row_uid
            )}

            for dk, dv in form.cleaned_data.items():
                if dk in curr_attr:
                    attr = curr_attr[dk]
                    if curr_attr[dk].value != dv:
                        curr_attr[dk].value = dv
                        curr_attr[dk].save()
                else:
                    attr = DocumentAttribute.objects.create(
                        attribute=DocumentTypeAttribute.objects.get(code=dk),
                        parent=tab_parent,
                        value=dv or None,
                        document_id=id,
                        row_uid=row_uid,
                        row_sq=idx
                    )

                if attr.attribute.attribute.generic_datatype == 'file':
                    _handle_file_field(value=dv, user=user, id=id)


@transaction.atomic()
def save_document_attributes(id, id_type, form_data, user=None, section_formsets=None, table_formsets=None, status=None):
    document_type = DocumentType.objects.get(pk=id_type)
    curr_attr = {i.attribute.code: i for i in DocumentAttribute.objects.filter(document_id=id, attribute__parent__isnull=True, attribute__is_table=False)}
    attr = get_visible_attributes(document_type=document_type, status=status)  # DocumentTypeAttribute.objects.filter(document_type=document_type, section__parent__isnull=True)

    _save_main_attributes(form_data=form_data, attr=attr, curr_attr=curr_attr, id=id, user=user)

    if section_formsets:
        _save_repeated_subsections(section_formsets=section_formsets, id=id, user=user)

    if table_formsets:
        _save_table_attributes(table_formsets=table_formsets, id=id, user=user)


def get_accounting_ordered_choosen_list(accounting_ordered):
    if accounting_ordered:
        return list(map(lambda x: int(x), accounting_ordered.split(",")))
    return []


def get_av_choosen_list(accounting_ordered_choosen_list, choosen_only=False):
    if not choosen_only:
        accounting_available = DocumentTypeAccountingType.objects.filter(is_accounting_order=True).exclude(pk__in=accounting_ordered_choosen_list)
        if accounting_ordered_choosen_list is None:
            return {'choosen': [], 'available': accounting_available}
    else:
        accounting_available = []

    _accounting_ordered_choosen = DocumentTypeAccountingType.objects.filter(is_accounting_order=True, pk__in=accounting_ordered_choosen_list)
    accounting_ordered_choosen = []

    if len(accounting_ordered_choosen_list) > 0:
        for i in accounting_ordered_choosen_list:
            for j in _accounting_ordered_choosen:
                if j.pk == i:
                    accounting_ordered_choosen.append(j)
                    break

    return {'choosen': accounting_ordered_choosen, 'available': accounting_available}


def _get_sequential_code(type):
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("select nextval('document_type_id_%s_sq')" % type.pk)
    return cursor.fetchone()[0]


def get_document_code(type):
    code = type.auto_generated_code_pattern
    if not code:
        return None

    p = re.findall(r'\{[A-Z]+\}', code)

    for i in p:
        if i == '{SQ}':
            code = code.replace(i, str(_get_sequential_code(type)))
        elif i == '{Y}':
            code = code.replace(i, str(datetime.date.today().year))
    return code


def get_initial_status(type):
    try:
        return DocumentTypeStatus.objects.get(type=type, is_initial=True)
    except DocumentTypeStatus.DoesNotExist:
        return None


def get_available_statuses(type, status):
    if not status:
        return
    return DocumentTypeProcessFlow.objects.filter(status=status).order_by('sq')


def get_status_flow(type, code):
    try:
        flow = DocumentTypeStatusFlow.objects.filter(status=DocumentTypeStatus.objects.get(type=type, code=code).pk)
    except DocumentTypeStatus.DoesNotExist:
        return []
    return [i.hierarchy for i in flow]


def save_scan(user, document, filename, type):
    for i in filename:
        attachment = Attachment(
            user=user,
            name='',
            type=type,
            description='',
            file_path=settings.MEDIA_ROOT + '/document/scan/tmp/',
            file_name=i['file_name'],
            file_original_name='',
            file_ext='',
            file_mime_type='image/jpg',
            file_size=None,
            creation_date=datetime.datetime.now()
        )
        attachment.save()

        doc_atm = DocumentAttachment(document=document, attachment=attachment)
        doc_atm.save()


def copy_annex_data(document):
    if not document.annex:
        return
    attributes = DocumentAttribute.objects.filter(document_id=document.annex.pk, attribute__type='ATTR')
    for i in attributes:
        attr = copy.copy(i)
        attr.id = None
        attr.document_id = document.pk
        attr.save()
