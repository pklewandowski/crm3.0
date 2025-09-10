import datetime
from pprint import pprint

import os
from django.conf import settings
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import html

from py3ws.utils import utils as py3ws_utils
from py3ws.views import generic_view

from apps.attachment.models import Attachment
from apps.attachment import utils as attm_utils

from apps.document import DOCUMENT_PROCESS_FLOW_RAW_SQL_QUERY
from apps.document.forms import DocumentForm, AttributeFormset
from apps.document.models import Document, DocumentTypeAttribute, DocumentAttribute, DocumentNote, \
    DocumentTypeStatus, DocumentType, DocumentTypeAccounting, DocumentStatusCourse, DocumentTypeAttributeFeature, DocumentScan, DocumentStatusTrack
from apps.document.type.attribute import utils as attribute_utils

import apps.document.forms as forms
from apps.report.models import Report
from py3ws.views.generic_view import GenericView

from apps.user.models import User
from . import utils as doc_utils


class DocumentException(Exception):
    def __init__(self, *args, **kwargs):
        if args[0]:
            self.message = args[0]
        else:
            self.message = None

        self.error_list = kwargs.pop('error_list', None)
        super(DocumentException, self).__init__(args, kwargs)


def _save_document_type(form, accounting_ordered_choosen):
    document_type = form.save()
    document_type.accounting_order.clear()

    for idx, i in enumerate(accounting_ordered_choosen):
        DocumentTypeAccounting.objects.create(document_type=document_type, accounting_type=i, sq=idx + 1)

    for i in form.cleaned_data['accounting_unordered']:
        DocumentTypeAccounting.objects.create(document_type=document_type, accounting_type=i, sq=0)

    return document_type


def _get_repeated_section_formsets(type, attribute_features, status=None, status_flow=None, data=None, id=None, readonly=False, user=None):
    section_formsets = {}
    for i in type.section_set.filter(parent__isnull=False):
        initial = []
        if id:
            initial_rows = DocumentAttribute.objects.distinct().filter(attribute__section=i,
                                                                       document_id=id).values('row_uid', 'row_sq').order_by('row_sq')
            for r in initial_rows:
                initial_set = DocumentAttribute.objects.filter(
                    attribute__section=i,
                    document_id=id,
                    attribute__is_table=False,
                    attribute__parent__isnull=True,
                    row_uid=r['row_uid'], row_sq=r['row_sq']).prefetch_related('attribute')

                if initial_set:
                    initial_row = {}
                    for iset in initial_set:
                        if iset.attribute.attribute.generic_datatype == 'boolean':
                            val = '' if not iset.value or iset.value == 'False' else 'True'
                        else:
                            val = iset.value
                        initial_row[iset.attribute.code] = val

                    initial_row['row_uid'] = initial_set[0].row_uid
                    initial.append(initial_row)

        attributes = {i.pk: i for i in DocumentTypeAttribute.objects.filter(document_type=type, section=i, parent__isnull=True).prefetch_related('attribute')}
        section_formsets[i.pk] = AttributeFormset(data=data,
                                                  initial=initial,
                                                  prefix='attr-formset-%s' % str(i.pk),
                                                  form_kwargs={'document_type': type,
                                                               'status': status,
                                                               'status_flow': status_flow,
                                                               'attributes': attributes,
                                                               'attribute_features': attribute_features,
                                                               'section': i,
                                                               'defaults': False,
                                                               'readonly': readonly,
                                                               'empty': False,
                                                               'form_name': i.name,
                                                               'user': user})
    return section_formsets


def _get_table_formsets(type, attribute_features, status=None, status_flow=None, data=None, id=None, readonly=False, user=None):
    table_formsets = {}
    for i in DocumentTypeAttribute.objects.filter(document_type=type, is_table=True):
        initial = []
        if id:
            for r in DocumentAttribute.objects.filter(document_id=id, attribute__parent=i).distinct('row_sq').order_by('row_sq'):

                row = {}
                for a in DocumentAttribute.objects.filter(document_id=id, attribute__parent=i, row_sq=r.row_sq):
                    row[a.attribute.code] = a.value
                    row['parent'] = a.parent.pk
                    row['parent_row_uid'] = a.parent.row_uid
                    row['row_uid'] = a.row_uid
                initial.append(row)

        attributes = {i.pk: i for i in DocumentTypeAttribute.objects.filter(document_type=type, parent=i).prefetch_related('attribute')}
        table_formsets[i.pk] = {
            'formset': AttributeFormset(data=data,
                                        initial=initial,
                                        prefix='attr-table-formset-%s' % str(i.pk),
                                        form_kwargs={'document_type': type,
                                                     'status': status,
                                                     'status_flow': status_flow,
                                                     'attributes': attributes,
                                                     'attribute_features': attribute_features,
                                                     'table': i,
                                                     'defaults': False,
                                                     'readonly': readonly,
                                                     'empty': False,
                                                     'user': user}),
            'attributes': DocumentTypeAttribute.objects.filter(parent=i).order_by('sq')
        }
    return table_formsets


class DocumentManagement(generic_view.GenericView):
    _app_name = 'document'

    def __init__(self):
        self.exclude_list = ()
        self.id = None
        self.type_id = None
        self.document = None
        self.type = None
        self.instance = None
        self.available_statuses = None
        self.form = None
        self.attribute_form = None
        self.attachment_formset = None
        self.scan_formset = None
        self.section_formsets = None
        self.table_formsets = None
        self.initial_status = None
        self.status = None
        self.prev_status = None
        self.status_flow = None
        self.user = None
        # self.context = None
        self.owner = None
        self.errors = None
        self.source = None
        self.initial = None
        self.initial_attributes = None
        self.readonly = False
        self.report_types = None

        super().__init__()

    def get_status_flow(self):
        if self.instance:
            self.status_flow = DocumentStatusTrack.objects.filter(document=self.instance).order_by('creation_date')

    def get_all_statuses(self):
        return DocumentTypeStatus.objects.filter(type=self.type).order_by('sq')

    def get_previous_status_course(self):
        previous_status = None

        if self.instance:
            try:
                result = DocumentStatusCourse.objects.filter(document=self.instance).order_by('-creation_date')[1]
                if result:
                    previous_status = result.status
            except IndexError:
                pass
        return previous_status

    # def get_previous_status(self):
    #     if not self.status_flow:
    #         if self.instance:
    #             self.get_status_flow()
    #         else:
    #             return None
    #     return self.status_flow[-1].lag

    def _get_instance(self):
        if not self.instance:
            try:
                self.instance = Document.objects.select_related(
                    'type', 'status').prefetch_related('note_set', 'attachment_set').get(pk=self.id)
            except Document.DoesNotExist:
                raise DocumentException('Próba pobrania danych dokumentu zakończona niepowodzeniem!')

    def _check_hierarchy(self, user):
        if not self.instance.status.hierarchies:
            return True

        if user.is_superuser:
            return True

        user_hierarchies = [i.pk for i in user.hierarchy.all()]
        valid = False

        for i in self.instance.status.hierarchies:
            if i in user_hierarchies:
                valid = True
                break

        return valid

    def validate(self):
        self.errors = []
        valid = True

        for k, v in self.section_formsets.items():
            _valid = v.is_valid()
            valid = valid and _valid
            if not _valid:
                self.errors.append({k: v.errors})

        for k, v in self.table_formsets.items():
            _valid = v['formset'].is_valid()
            valid = valid and _valid
            if not _valid:
                self.errors.append({k: v['formset'].errors})

        valid = all([
            valid,
            self.form.is_valid(),
            self.attribute_form.is_valid(),
            self.attachment_formset.is_valid(),
            self.scan_formset.is_valid()
        ])

        if self.form.errors:
            self.errors.append({'dane dokumentu': self.form.errors})
        if self.attribute_form.errors:
            self.errors.append({'atrybuty': self.attribute_form.errors})
        return valid

    def get_forms(self, data):
        self.form = DocumentForm(data=data,
                                 initial=(self.initial or {'owner': self.owner}) if not self.instance else None,
                                 instance=self.instance,
                                 is_owner=self.type.is_owner,
                                 is_code=self.instance.type.is_code if self.instance else None,
                                 is_code_editable=self.instance.type.is_code_editable if self.instance else None,
                                 owner_type=self.type.owner_type,
                                 exclude_list=self.exclude_list,
                                 available_statuses=self.available_statuses,
                                 prefix='document',
                                 form_name='Dokument',
                                 readonly=self.readonly
                                 )
        if self._mode == settings.MODE_EDIT and not self.instance.type.is_code_editable:
            self.form.fields['code'].widget.attrs['readonly'] = True

        attributes = {i.pk: i for i in DocumentTypeAttribute.objects.filter(
            document_type=self.type,
            section__parent__isnull=True,
            parent__isnull=True
        ).prefetch_related('attribute')}

        attribute_features = attribute_utils.get_attribute_features(document_type=self.type, status=self.status, readonly=False)

        self.attribute_form = forms.get_document_attribute_form(data=data,
                                                                initial=self.initial_attributes,
                                                                document=self.instance,
                                                                document_status=self.status,
                                                                document_status_flow=self.status_flow,
                                                                document_type=self.type,
                                                                attributes=attributes,
                                                                attribute_features=attribute_features,
                                                                prefix='attr',
                                                                form_name='Atrybuty',
                                                                readonly=self.readonly,
                                                                user=self.user
                                                                )
        self.attachment_formset = attm_utils.get_attachment_formset(
            data,
            queryset=Attachment.objects.filter(pk__in=self.instance.attachment_set.all().values('attachment')) if self.instance else Attachment.objects.none()
        )

        self.scan_formset = forms.DocumentScanFormset(
            data=data,
            queryset=self.instance.scan_set.all().order_by('sq') if self.instance else DocumentScan.objects.none(),
            prefix='scan',
        )

        self.section_formsets = _get_repeated_section_formsets(data=data,
                                                               type=self.type,
                                                               status=self.status,
                                                               status_flow=self.status_flow,
                                                               id=self.id,
                                                               attribute_features=attribute_features,
                                                               readonly=self.readonly,
                                                               user=self.user
                                                               )

        self.table_formsets = _get_table_formsets(data=data,
                                                  type=self.type,
                                                  status=self.status,
                                                  status_flow=self.status_flow,
                                                  id=self.id,
                                                  attribute_features=attribute_features,
                                                  readonly=self.readonly,
                                                  user=self.user
                                                  )

    def save_status(self, document, status, type):
        if type == 'course':
            return DocumentStatusCourse.objects.create(
                document=document,
                status=status,
                created_by=self.user,
                # effective_date=effective_date
            )
        elif type == 'track':
            return DocumentStatusTrack.objects.create(
                document=document,
                status=status,
                created_by=self.user,
                # effective_date=effective_date
            )
        else:
            raise DocumentException('Nieprawidłowy parametr type')

    def save(self, user):
        if self.form.readonly:
            return self.instance
        document = self.form.save(commit=False)
        document_status_track = None

        if self._mode == settings.MODE_CREATE and not self.instance:
            document.created_by = self.user
            document.type = self.type
            document.status = self.status

            if self.type.is_code and not self.type.is_code_editable:
                document.code = doc_utils.get_document_code(self.type)

            document.save()
            document_status_track = self.save_status(document, self.status, 'track')
            self.save_status(document, self.status, 'course')

        doc_utils.save_document_attributes(id=document.pk,
                                           id_type=document.type.pk,
                                           form_data=self.attribute_form.cleaned_data,
                                           section_formsets=self.section_formsets,
                                           table_formsets=self.table_formsets,
                                           status=document.status,
                                           user=user
                                           )

        status = self.form.cleaned_data.get('status_flow', None)
        if status:
            document_status = DocumentTypeStatus.objects.get(type=document.type, code=self.form.cleaned_data.get('status_flow'))
            document.status = document_status
            document_status_course = self.save_status(document=document, status=document_status, type='course')
            document_status_track = self.save_status(document=document, status=document_status, type='track')
        else:
            document.status = self.status
            if not document_status_track:
                try:
                    document_status_track = DocumentStatusTrack.objects.filter(document=document).order_by('-creation_date')[0]
                except KeyError:
                    pass
                except IndexError:
                    document_status_track = DocumentStatusTrack.objects.create(
                        document=document,
                        status=document.status,
                        created_by=user,
                        creation_date=datetime.datetime.today()
                    )

        document.save()

        note = self.form.cleaned_data.get('note')
        if note:
            DocumentNote.objects.create(
                document=document,
                created_by=self.user,
                text=note,
                document_status_track=document_status_track
            )

        if self._mode == settings.MODE_CREATE:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'document/attachments', str(document.pk)), exist_ok=True)

        for i in self.scan_formset:
            ds = i.save(commit=False)
            ds.document = document
            ds.file_path = '/media/document/scan/'
            ds.created_by = self.request.user
            ds.save()

        return document

    def get_context(self):
        self.get_status_flow()

        return {'type': self.type,
                'form': self.form,
                'status_flow': [{
                    'date': i.creation_date,
                    'effective_date': i.effective_date,
                    'status': i.status,
                    'user': i.created_by
                } for i in self.status_flow] if self.status_flow else None,
                'all_statuses': self.get_all_statuses(),
                'scan_formset': self.scan_formset,
                'previous_status': self.get_previous_status_course(),
                'attr_form': self.attribute_form,
                'reports': Report.objects.filter(document=self.instance).order_by('-creation_date') if self.instance else None,
                'section_formsets': self.section_formsets,
                'table_formsets': self.table_formsets,
                'attachment_formset': self.attachment_formset,
                'attr': doc_utils.get_attributes(self.type.pk, self.status),
                'atm_classname': 'apps.document.models.DocumentAttachment',
                'atm_owner_classname': 'apps.document.models.Document',
                'atm_root_name': 'doc',
                'mode': settings.MODE_VIEW if self.readonly else settings.MODE_EDIT if self.id else settings.MODE_CREATE,
                'errors': self.errors,
                'report_types': self.report_types
                }

    def trigger_action(self, document):
        if document.status.action_class and document.status.action:
            cl = py3ws_utils.get_class(document.status.action_class)()
            id_value = getattr(cl, document.status.action)(self.user, document.pk)

            if document.status.redirect:
                return redirect(document.status.redirect, id=id_value)

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        self.user = request.user

        if not self.status:
            raise AttributeError('Brak definicji przebiegu procesu dla dokumentu: %s' % self.type.name)

        self.available_statuses = doc_utils.get_available_statuses(type=self.type, status=self.status)

        self.user = request.user
        self.get_forms(request.POST or None)

        if request.POST:
            if self.readonly:
                return redirect('document.edit', id=self.instance.pk)

            if self.validate():
                document = self.save(user=request.user)
                self.trigger_action(document)
                if self.source:
                    self.source.complete(document)
                return redirect('document.edit', id=document.pk)

            else:
                section_formset_forms = []
                for forms in list(map(lambda x: list(x), list(self.section_formsets.values()))):
                    for form in forms:
                        section_formset_forms.append(form)
                self.errors = GenericView.collect_errors([self.form, self.attribute_form] + section_formset_forms)

        return render(request, self.render, self.get_context())


class DocumentAttributeFeatureException(Exception):
    pass


class DocumentAttributeFeatureManager(generic_view.GenericView):
    def set_mode(self):
        raise NotImplementedError

    FEATURE_ICON_MAPPING = {'V': 'fa-eye', 'E': 'fa-edit', 'R': 'fa-exclamation-circle'}
    id = None
    id_section = None
    id_column = None

    def __init__(self):
        self._document_type = None
        self._sections = None
        self._statuses = []
        self._attributes = []
        self._initial = {}
        self._form = None
        super().__init__()

    def _set_statuses(self):
        self._statuses = list(self._document_type.status_set.all().order_by('sq'))

    def _set_attributes(self):
        if not self._sections:
            raise DocumentAttributeFeatureException('Brak zdefiniopwanych sekcji')
        for i in self._sections:
            self._attributes.append(
                list(DocumentTypeAttribute.objects.select_related('section', 'section_column').filter(section=i).order_by('section_column__sq', 'sq'))
            )

    def _set_form(self, request):
        self._form = forms.DocumentTypeAttributeFeatureForm(data=request.POST or None,
                                                            initial=self._initial,
                                                            document_type=self._document_type,
                                                            sections=self._sections,
                                                            attributes=self._attributes,
                                                            statuses=self._statuses
                                                            )

    def _set_initials(self):
        for i in DocumentTypeAttributeFeature.objects.select_related('attribute',
                                                                     'attribute__section',
                                                                     'status').filter(attribute__in=self._document_type.attribute_set.filter(section__in=self._sections)):
            self._initial[attribute_utils.get_field_name(attribute=i.attribute, section=i.attribute.section, status_code=i.status.code, feature='V')] = i.visible
            self._initial[attribute_utils.get_field_name(attribute=i.attribute, section=i.attribute.section, status_code=i.status.code, feature='E')] = i.editable
            self._initial[attribute_utils.get_field_name(attribute=i.attribute, section=i.attribute.section, status_code=i.status.code, feature='R')] = i.required

    def _save_attribute_features(self, create=False):

        def _clean_feature(feature):
            if not feature['V']:
                feature['E'] = False
                feature['R'] = False

            if feature['E']:
                feature['V'] = True

            if feature['R']:
                feature['V'] = True
                # feature['E'] = True

        if create:
            DocumentTypeAttributeFeature.objects.filter(attribute__document_type=self._form.document_type).delete()

        for idx, a in enumerate(self._form.attributes):
            for i in a:
                for j in self._form.statuses:
                    feature = {'V': False, 'E': False, 'R': False}
                    for k in self._form.feature:
                        field = self._form.cleaned_data.get(attribute_utils.get_field_name(attribute=i, status_code=j.code, section=i.section, feature=k))
                        if field:
                            feature[k] = True

                    _clean_feature(feature)

                    try:
                        attribute_feature = DocumentTypeAttributeFeature.objects.get(attribute=i, status=j)
                        attribute_feature.visible = feature['V']
                        attribute_feature.editable = feature['E']
                        attribute_feature.required = feature['R']
                        attribute_feature.save()

                    except DocumentTypeAttributeFeature.DoesNotExist:
                        DocumentTypeAttributeFeature.objects.create(attribute=i,
                                                                    status=j,
                                                                    visible=feature['V'],
                                                                    editable=feature['E'],
                                                                    required=feature['R'])

    def _set_context(self):
        return {'document_type': self._document_type,
                'sections': self._sections,
                'attributes': self._attributes,
                'form': self._form,
                'feature_icon_mapping': self.FEATURE_ICON_MAPPING}

    def _set_document_type(self, id):
        self._document_type = DocumentType.objects.get(pk=id)

    def _set_sections(self, id=None):
        if not id:
            self._sections = [i for i in self._document_type.section_set.all().order_by('sq')]
        else:
            self._sections = [self._document_type.section_set.get(pk=id)]

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        if not self.id:
            raise DocumentAttributeFeatureException('Brak ID Typu dokumentu')
        self._set_document_type(self.id)
        self._set_sections(self.id_section)
        self._set_statuses()
        self._set_attributes()
        self._set_initials()
        self._set_form(request)

        if request.POST:
            if self._form.is_valid():
                self._save_attribute_features()
                return redirect('document.type.attribute.feature', self.id, self.id_section)

        return render(request, 'document/type/attribute/feature.html', context=self._set_context())


class DocumentOcrManager(GenericView):
    pass
