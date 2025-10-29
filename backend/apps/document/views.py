import datetime
import json
import uuid

import pytesseract
from PIL import Image
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import html
from django.views.decorators.csrf import csrf_exempt

from apps.attachment import utils as attm_utils
from apps.attachment.models import Attachment
from apps.document import forms
from apps.document.view_base import DocumentManagement, _get_repeated_section_formsets, _get_table_formsets, DocumentException, DocumentAttributeFeatureManager, DocumentOcrManager
from apps.product.utils.utils import LoanUtils
from apps.report.models import Report
from apps.user.models import User
from py3ws.utils import utils as py3ws_utils
from py3ws.views import generic_view
from py3ws.views.generic_view import GenericView
from . import utils as doc_utils
from .forms import DocumentTypeAttributeForm, DocumentTypeSectionForm, DocumentForm, \
    LovFormset
from .models import DocumentType, DocumentTypeAttribute, DocumentTypeSection, DocumentTypeSectionColumn, DocumentTypeCategory, Document, DocumentTypeStatus, DocumentTypeAttributeFeature, \
    DocumentAttribute, DocumentSource, DocumentStatusCourse, DocumentStatusTrack, DocumentTypeReport
from .utils import get_attributes


def list_category(request):
    categories = DocumentTypeCategory.objects.all()
    context = {'categories': categories}
    return render(request, 'document/type/category/list.html', context)


def list_document_type(request, id=None):
    if id is None:
        document_types = DocumentType.objects.filter(is_shadow=False, is_active=True)
    else:
        document_types = DocumentType.objects.filter(category=DocumentTypeCategory.objects.get(pk=id), is_shadow=False, is_active=True)
    context = {'document_types': document_types}
    return render(request, 'document/type/list.html', context)


# def _save_document_type(form, accounting_ordered_choosen):
#     document_type = form.save()
#     document_type.accounting_order.clear()
#
#     for idx, i in enumerate(accounting_ordered_choosen):
#         DocumentTypeAccounting.objects.create(document_type=document_type, accounting_type=i, sq=idx + 1)
#
#     for i in form.cleaned_data['accounting_unordered']:
#         DocumentTypeAccounting.objects.create(document_type=document_type, accounting_type=i, sq=0)


class ListView(generic_view.ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'document'

    def __init__(self):
        self.default_sort_field = 'creation_date'
        self.sort_dir = '-'
        self.rows_per_page = 30

        super(ListView, self).__init__()

    def set_where(self):
        self.where = Q(type=self.document_type)
        user = self.request.user

        # if user.has_perm('document.list:all'):
        #     pass
        # elif user.has_perm('document.list:department'):
        #     self.where &= Q(created_by__hierarchy__in=list(hierarchy_utils.get_departments(user.hierarchy.all(), with_descendants=True).values()))
        # elif user.has_perm('document.list:position'):
        #     self.where &= Q(created_by__hierarchy__in=user.hierarchy.all())
        # elif user.has_perm('document.list:own'):
        #     self.where &= Q(created_by=user)
        # else:
        #     raise PermissionError('Użytkownik nie ma uprawnień pozwalających na przeglądanie')

        if self.search:
            self.where &= (
                    Q(custom_code__icontains=self.search) |
                    Q(code__icontains=self.search) |
                    Q(owner__first_name__icontains=self.search) |
                    Q(owner__last_name__icontains=self.search) |
                    Q(owner__company_name__icontains=self.search) |
                    Q(owner__phone_one__icontains=self.search) |
                    Q(owner__nip__icontains=self.search) |
                    Q(owner__personal_id__icontains=self.search) |
                    Q(owner__email__icontains=self.search) |
                    Q(created_by__first_name__icontains=self.search) |
                    Q(created_by__last_name__icontains=self.search) |
                    Q(status__name__icontains=self.search) |
                    Q(product__value__icontains=self.search)
            )

    def set_query(self):
        self.query = Document.objects.filter(self.where).select_related('product', 'owner', 'created_by').order_by('%s%s' % (self.sort_dir, self.sort_field))

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        self.document_type = self.kwargs['type']
        # self.has_any_permissions(request.user)
        # if not self.has_any_permission:
        #     raise PermissionDenied
        super(ListView, self).dispatch(request, *args, **kwargs)
        self.check_permissions(request.user)
        return self.list(request=request, template='document/list.html',
                         extra_context={'document_type': DocumentType.objects.get(pk=self.document_type)})


class Add(DocumentManagement):
    def set_mode(self):
        return settings.MODE_CREATE

    def set_app_name(self):
        self._app_name = 'document'

    def __init__(self):
        self._mode = settings.MODE_CREATE
        self.source = None

        super(Add, self).__init__()

    def _get_type(self):
        try:
            type_id = self.kwargs['type'] or None
            if not type_id:
                raise Exception("Parametr 'type' nie może być pusty")
            self.type = DocumentType.objects.get(pk=type_id)

        except KeyError:
            raise AttributeError("Brak parametru 'type'")

        except DocumentType.DoesNotExist:
            raise Exception('Brak definicji typu dokumentu')

    def _get_status(self):
        try:
            self.status = DocumentTypeStatus.objects.get(type=self.type, is_initial=True)
            self.prev_status = self.status

        except DocumentTypeStatus.DoesNotExist:
            raise AttributeError('Brak definicji statusu inicjalnego dla dokumentu: %s' % self.type.name)

    def _get_owner(self):
        try:
            owner_id = self.kwargs['owner_id'] or None
            self.owner = User.objects.get(pk=owner_id) if owner_id else None
        except KeyError:
            pass

    def _get_source(self):
        try:
            source_code = self.kwargs.pop('source_code', None)
            source_id = self.kwargs.pop('source_id')
        except KeyError:
            source_code = None
            source_id = None

        if source_code:
            if not source_id:
                raise DocumentException('Podano source_type_id a nie podano source_id')

            document_source = DocumentSource.objects.get(code=source_code)

            source_class = py3ws_utils.get_class(document_source.class_name)(id=source_id)
            self.source = source_class.get_source()

    def _get_initials(self):
        if self.source:
            self.initial = self.source.get_initial_data()
            self.initial_attributes = self.source.get_initial_attributes()

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        self.render = 'document/add.html'

        self._get_type()
        if not self.type.is_code_editable:
            self.exclude_list = ('code',)

        self._get_source()
        self._get_initials()

        self._get_status()
        self._get_owner()

        return super().dispatch(request, *args, **kwargs)


class Edit(DocumentManagement):
    def set_mode(self):
        return settings.MODE_EDIT

    def set_app_name(self):
        self._app_name = 'document'

    def __init__(self):
        self._mode = settings.MODE_EDIT
        self.render = 'document/edit.html'
        super(Edit, self).__init__()

    def get_report_types(self, manual=True):
        return DocumentTypeReport.objects.filter(type=self.type, is_manual=manual)

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        try:
            self.id = self.kwargs['id'] or None
            if not self.id:
                raise DocumentException("Parametr 'id' nie może być pusty")
        except KeyError:
            raise DocumentException("Nie podano parametru 'id'")

        self._get_instance()

        if not self._check_hierarchy(request.user):
            self.readonly = True

        try:
            redirection = self.kwargs['redirection'] or None
            if self.instance.product and redirection == 'Y':
                return redirect('product.edit', id=self.instance.product.pk)
        except KeyError:
            pass

        self.type = self.instance.type
        self.status = self.instance.status
        self.prev_status = self.get_previous_status_course()
        self.report_types = self.get_report_types()

        if request.POST:
            status_flow = request.POST.get('document-status_flow', None)
            self.status_flow = DocumentTypeStatus.objects.get(type=self.type, code=status_flow) if status_flow else None
        else:
            self.status_flow = None

        return super().dispatch(request, *args, **kwargs)


class RevertStatus(GenericView):
    # TODO: zrobić możliwość dodania notatki, tak, jak przy zmianie statusu
    def set_mode(self):
        return settings.MODE_EDIT

    def set_app_name(self):
        self._app_name = 'document'

    def __init__(self):
        self._mode = settings.MODE_EDIT
        super(RevertStatus, self).__init__()

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        status = 200
        response_data = {}

        try:
            with transaction.atomic():
                if request.method == 'POST':
                    id = html.mark_safe(request.POST.get('id'))

                    if not id:
                        raise DocumentException('RevertStatus: nie podano parametru ID')

                    document = Document.objects.get(pk=id)

                    doc_status = DocumentTypeStatus.objects.get(type=document.type, is_initial=True)
                    rs = DocumentStatusCourse.objects.filter(document=document).order_by('-creation_date')

                    if rs:
                        try:
                            doc_status = rs[1].status
                        except IndexError:
                            pass

                        rs[0].delete()

                    document.status = doc_status
                    document.save()

                    DocumentStatusTrack.objects.create(
                        document=document,
                        status=doc_status,
                        created_by=request.user
                    )

        except DocumentException as ex:
            status = 400
            response_data['errmsg'] = str(ex)

        return HttpResponse(json.dumps(response_data), status=status)


@login_required()
def view(request, id):
    document = Document.objects.prefetch_related('type', 'status', 'note_set', 'attachment_set').get(pk=id)
    status = document.status
    form = DocumentForm(is_owner=document.type.is_owner,
                        is_code=document.type.is_code,
                        is_code_editable=document.type.is_code_editable,
                        owner_type=document.type.owner_type,
                        available_statuses=doc_utils.get_available_statuses(type=document.type, status=document.status),
                        readonly=True,
                        instance=document,
                        prefix='document')

    attr_form = forms.get_document_attribute_form(data=None,
                                                  document=document,
                                                  document_status=status,
                                                  document_type=document.type,
                                                  readonly=True,
                                                  prefix='attr')

    section_formsets = _get_repeated_section_formsets(id=id, type=document.type, status=status, readonly=True)
    table_formsets = _get_table_formsets(type=document.type, status=status, id=id, readonly=True)

    attachment_formset = attm_utils.get_attachment_formset(
        request.POST or None,
        queryset=Attachment.objects.filter(pk__in=document.attachment_set.all().values('attachment'))
    )

    context = {'type': document.type,
               'form': form,
               'attr_form': attr_form,
               'reports': Report.objects.filter(document=document).order_by('-creation_date'),
               'section_formsets': section_formsets,
               'table_formsets': table_formsets,
               'attachment_formset': attachment_formset,
               'attr': doc_utils.get_attributes(document.type.pk, status),
               'atm_classname': 'apps.document.models.DocumentAttachment',
               'atm_owner_classname': 'apps.document.models.Document',
               'atm_root_name': 'doc',
               'mode': settings.MODE_VIEW
               }

    return render(request, 'document/edit.html', context)


@login_required()
@transaction.atomic()
def list_document_type_attribute(request, id):
    # attributes = document_type.attribute_set.all().order_by('sq')

    if request.method == 'POST':
        section_id = request.POST.getlist('section_id')

        attribute_id = request.POST.getlist('attribute_id')
        attribute_section_id = request.POST.getlist('attribute_section_id')
        attribute_section_column_id = request.POST.getlist('attribute_section_column_id')
        attribute_sq = request.POST.getlist('attribute_sq')

        sections = {}
        n = 1

        for i in section_id:
            s = DocumentTypeSection.objects.get(pk=int(i))
            s.sq = n
            s.save()
            n += 1

        n = 0

        for i in attribute_id:
            a = DocumentTypeAttribute.objects.get(pk=i)
            a.sq = int(attribute_sq[n])
            # TODO: nieefektywne - zoptymalizować
            a.section = DocumentTypeSection.objects.get(pk=int(attribute_section_id[n]))  # sections[int(attribute_section_id[n])]
            a.section_column = DocumentTypeSectionColumn.objects.get(pk=int(attribute_section_column_id[n]))
            a.save()
            n += 1

    attr = get_attributes(id)
    document_type = DocumentType.objects.get(pk=id)

    context = {'document_type': document_type, 'attr': attr}
    return render(request, 'document/type/attribute/list.html', context)


class DocumentAttributeFeature(DocumentAttributeFeatureManager):
    def set_mode(self):
        self._mode = settings.MODE_EDIT

    def set_app_name(self):
        self._app_name = 'document'

    def dispatch(self, request, *args, **kwargs):
        self.id = self.kwargs['id']
        self.id_section = self.kwargs['id_section']
        try:
            self.id_column = self.kwargs['id_column']
        except KeyError:
            self.id_column = None

        return super(DocumentAttributeFeature, self).dispatch(request, *args, **kwargs)


def _convert_lov_formset_to_json(lov_formset, null_value):
    if not len(lov_formset):
        return None
    lov = {}
    data = []
    for f in lov_formset:
        c = f.cleaned_data
        if f.cleaned_data.get('DELETE'):
            continue
        if not c.get('lov_value'):
            continue
        data.append({'lov_value': c.get('lov_value'), 'lov_label': c.get('lov_label'), 'lov_description': c.get('lov_description')})
    lov['data'] = data
    lov['nullvalue'] = null_value

    return lov


@transaction.atomic()
def add_document_type_attribute(request, id, id_section):
    section = DocumentTypeSection.objects.get(pk=id_section)
    form = DocumentTypeAttributeForm(request.POST or None)
    lov_formset = LovFormset(data=request.POST or None,
                             prefix='lov',
                             form_kwargs={'field_base_class': 'form-control input-sm'})

    form.fields['section_column'].queryset = DocumentTypeSectionColumn.objects.filter(section=id_section)

    document_type = DocumentType.objects.get(pk=id)

    if request.method == 'POST':

        if all([form.is_valid(), lov_formset.is_valid()]):
            attribute = form.save(commit=False)
            attribute.lov = _convert_lov_formset_to_json(lov_formset, form.cleaned_data.get('null_value'))
            attribute.section = section
            attribute.code = "%s_%s" % (document_type.pk, uuid.uuid4().hex)
            attribute.document_type = document_type
            attribute.sq = document_type.attribute_set.count() + 1
            attribute.save()

            for i in DocumentTypeStatus.objects.filter(type=document_type):
                DocumentTypeAttributeFeature.objects.create(attribute=attribute, status=i, visible=True, editable=True, required=False)

            return redirect('document.type.attribute.list', id=attribute.document_type.pk)

    context = {'form': form,
               'document_type': document_type,
               'lov_formset': lov_formset}
    return render(request, 'document/type/attribute/add.html', context)


def edit_document_type_attribute(request, id):
    attribute = DocumentTypeAttribute.objects.get(pk=id)
    lov_null_value = False
    if attribute.lov and attribute.lov['nullvalue']:
        lov_null_value = True
    form = DocumentTypeAttributeForm(request.POST or None, instance=attribute, initial={'null_value': lov_null_value})

    lov_data = []
    try:
        for l in attribute.lov['data']:
            lov_data.append({"lov_value": l['lov_value'], "lov_label": l['lov_label'], "lov_description": l['lov_description'], "new_row": ''})
    except TypeError:
        lov_data = None

    lov_formset = LovFormset(data=request.POST or None,
                             initial=lov_data,
                             prefix='lov',
                             form_kwargs={'field_base_class': 'form-control input-sm'})

    form.fields['section_column'].queryset = DocumentTypeSectionColumn.objects.filter(section=attribute.section)

    # form.fields['section'].choices = [(None, '---------')] + [(i, j) for i, j in DocumentTypeSection.objects.filter(document_type=attribute.document_type).order_by('sq').values_list('pk', 'name')]
    form.fields['attribute'].choices = [(attribute.attribute.pk, attribute.attribute.name)]
    form.fields['attribute'].widget.attrs['readonly'] = True

    if request.method == 'POST':

        if all([form.is_valid(), lov_formset.is_valid()]):
            attr = form.save(commit=False)
            attr.lov = _convert_lov_formset_to_json(lov_formset, form.cleaned_data.get('null_value'))
            attr.save()
            return redirect('document.type.attribute.list', id=attr.document_type.pk)

    context = {'form': form,
               'lov_formset': lov_formset,
               'document_type': attribute.document_type}
    return render(request, 'document/type/attribute/edit.html', context)


def list_document_type_section(request, id):
    document_type = DocumentType.objects.get(pk=id)
    sections = DocumentTypeSection.objects.filter(document_type=document_type).order_by('sq')

    context = {'document_type': document_type, 'sections': sections}
    return render(request, 'document/type/section/list.html', context)


@transaction.atomic
def add_document_type_section(request, id, id_parent=None):
    document_type = DocumentType.objects.get(pk=id)
    form = DocumentTypeSectionForm(request.POST or None)
    # document_type_section_column_formset = DocumentTypeSectionColumnFormset(data=request.POST or None, prefix='section-column')

    if request.method == 'POST':
        if form.is_valid():

            section = form.save(commit=False)
            section.document_type = document_type
            section.sq = document_type.section_set.count() + 1
            section.parent = DocumentTypeSection.objects.get(pk=id_parent) if id_parent else None
            section.save()

            width = 0
            columns = list(map(lambda x: int(x), request.POST.get('section_columns').split(",")))
            for index, i in enumerate([i for i in columns]):
                DocumentTypeSectionColumn.objects.create(sm_width=i - width, sq=index + 1, section=section, name=str(index + 1))
                width = i

            return redirect('document.type.attribute.list', section.document_type.pk)

    context = {
        'form': form,
        # 'document_type_section_column_formset': document_type_section_column_formset,
        'document_type': document_type
    }
    return render(request, 'document/type/section/add.html', context)


def _delete_section_column(col, append_to_col):
    col_items = DocumentTypeAttribute.objects.filter(section_column=col)
    for i in col_items:
        i.section_column = append_to_col
        i.save()


@transaction.atomic
def edit_document_type_section(request, id):
    section = DocumentTypeSection.objects.get(pk=id)
    section_columns = section.column_set.all().order_by('sq')

    c = []
    form = DocumentTypeSectionForm(request.POST or None, instance=section)

    if request.method == 'POST':
        columns = list(map(lambda x: int(x), request.POST.get('section_columns').split(",")))

        if form.is_valid():
            section = form.save()

            width = 0

            for idx, i in enumerate(section_columns):
                try:
                    i.sm_width = columns[idx] - width
                    width = columns[idx]
                    i.save()
                except IndexError:
                    # This can only happen if len(section_column) >= 2 (section MUST have at least one column). So [-2] does not make IndexError
                    _delete_section_column(i, section_columns[-2])

            if len(columns) > len(section_columns):
                for i in range(len(section_columns) - 1, len(columns) - 1):
                    DocumentTypeSectionColumn.objects.create(sm_width=columns[i] - width, sq=i + 1, section=section, name=str(i + 1))
                    width = columns[i]

            # section_columns_count = len(section_columns)

            # if section_columns_count <= len(columns):
            #     for index, i in enumerate(section_columns):
            #         i.sm_width = columns[index] - width
            #         i.save()
            #         width = columns[index]
            #     for i in range(0, len(columns) - section_columns_count):
            #         index = section_columns_count + i
            #         DocumentTypeSectionColumn.objects.create(sm_width=columns[index] - width, sq=index + 1, section=section, name=str(index + 1))
            #         width = columns[index]
            # else:
            #
            #     for index, i in enumerate(columns):
            #         DocumentTypeSectionColumn.objects.create(sm_width=i - width, sq=index + 1, section=section, name=str(index + 1))
            #         width = i

            return redirect('document.type.attribute.list', section.document_type.pk)

    width = 0

    for i in section_columns:
        width += int(i.sm_width)
        c.append(width)

    context = {'form': form,
               'columns': c
               }
    return render(request, 'document/type/section/edit.html', context)


@transaction.atomic()
def delete_document_type_attribute(request):
    response_data = {}
    status = 200

    try:
        id = request.POST.get('id')

        attribute = DocumentTypeAttribute.objects.get(pk=id)
        DocumentTypeAttributeFeature.objects.filter(attribute=attribute).delete()
        DocumentAttribute.objects.filter(attribute=attribute).delete()
        attribute.delete()
        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


def delete_document_type_section(request):
    status = 200
    response_data = {}

    try:
        id = request.POST.get('id')

        section = DocumentTypeSection.objects.get(pk=id)
        if section.attribute_set.exists():
            raise Exception('Usuwana sekcja nie może zawierać atrybutów!')

        section.delete()
        response_data['status'] = 'OK'

    except Exception as e:
        status = 400
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


def get_section_columns(request):
    response_data = {'data': None, 'message': None}
    try:
        id = request.POST.get('id')

        response_data['data'] = [{'id': i.pk, 'name': i.name} for i in DocumentTypeSectionColumn.objects.filter(section=DocumentTypeSection.objects.get(pk=id)).order_by('sq')]
        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


# def get_zip_attachemnts(request, id):
#     document = Document.objects.get(pk=id)
#     atm = [i.attachment for i in DocumentAttachment.objects.filter(document=document)]
#     zipname = attm_utils.zip(atm)
#
#     with open(zipname, 'r+b') as f:
#         response = HttpResponse(f.read(), content_type='%s; %s' % ("application/zip", 'charset=utf-8'))
#         response['Content-Disposition'] = 'attachment; filename="%s.zip"' % document.code or 'attm'
#         f.close()
#         return response


@csrf_exempt
def get_status_flow(request):
    status = 200
    response_data = {'data': None, 'errmsg': None}
    try:
        type = request.POST.get('type')
        code = request.POST.get('code')

        response_data['data'] = [{'value': i.pk, 'label': i.name} for i in doc_utils.get_status_flow(type=DocumentType.objects.get(pk=type), code=code)]
        response_data['status'] = 'OK'

    except Exception as e:
        status = 400
        response_data['status'] = 'ERROR'
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


def rsc_generate_product():
    user = User.objects.get(pk=1)
    with transaction.atomic():
        for i in Document.objects.filter(status__in=[17, 29]):
            LoanUtils.create_loan(user, i.pk)


class DocumentOcrBox(DocumentOcrManager):
    def set_mode(self):
        self._mode = settings.MODE_EDIT

    def set_app_name(self):
        self._app_name = 'document'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        response_data = {}
        status = 200
        try:
            if not request.is_ajax():
                raise DocumentException('Musi być ajax')

            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_EXECUTABLE_PATH  # r'C:/Program Files/Tesseract-OCR/tesseract.exe'

            filename = html.mark_safe(request.POST.get('filename'))
            box = json.loads(request.POST.get('box'))

            img = Image.open('%s%s%s' % (settings.MEDIA_ROOT, '/document/scan/', filename))
            crp = img.crop((box['left'], box['top'], box['left'] + box['width'], box['top'] + box['height']))

            txt = pytesseract.image_to_string(crp, lang='pol')
            txt = txt.replace('\n\n', '\n')

            response_data['text'] = txt

        except Exception as ex:
            status = 400
            response_data['errmsg'] = str(ex)

        return HttpResponse(json.dumps(response_data), status=status)


class PrintProcessFlow(GenericView):
    def set_mode(self):
        self._mode = settings.MODE_EDIT

    def set_app_name(self):
        self._app_name = 'document'

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        response_data = {}
        status = 200
        try:
            if not request.is_ajax():
                raise DocumentException('Musi być ajax')

            id = request.POST.get('id', None)

            if not id:
                raise DocumentException('Brak id')

            document = Document.objects.get(pk=id)
            status_track = DocumentStatusTrack.objects.filter(document=document) \
                .select_related('created_by', 'status').prefetch_related('track_note_set') \
                .order_by('creation_date')

            track = []

            for i in status_track:
                track.append(
                    {
                        'status': {'name': i.status.name,
                                   'createdBy': str(i.created_by),
                                   'creationDate': datetime.datetime.strftime(i.creation_date, '%Y-%m-%d %H:%M:%S')},
                        'notes': [{'text': n.text,
                                   'createdBy': str(n.created_by),
                                   'creationDate': datetime.datetime.strftime(n.creation_date, '%Y-%m-%d %H:%M:%S')} for n in i.track_note_set.all()]
                    }
                )

                response_data['track'] = track

        except Exception as ex:
            status = 400
            response_data['errmsg'] = str(ex)

        return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)
