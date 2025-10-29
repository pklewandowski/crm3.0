import datetime
import json
import os
import traceback

from django.conf import settings
from django.db import transaction
from django.db.models import Q, Prefetch
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.attachment import utils as atm_utils
from apps.attachment.models import Attachment
from apps.document import utils as doc_utils
from apps.document.api.attribute_utils import AttributeUtils
from apps.document.models import DocumentTypeSection, Document, DocumentType, DocumentTypeAttribute, \
    DocumentAttribute, DocumentTypeSectionColumn, DocumentAttachment, DocumentStatusTrack, \
    DocumentStatusCourse, DocumentTypeProcessFlow, DocumentTypeStatus, DocumentTypeAttributeMapping, \
    DocumentTypeReport, DocumentReport
from apps.user.models import User
from .rest_form import DocumentForm
from .serializers import DocumentTypeSectionSerializer, DocumentAttachmentSerializer, \
    DocumentStatusTrackSerializer, DocumentTypeProcessFlowSerializer, DocumentSerializer
from .services import note_services, document_services
from .utils import DocumentApiUtils, DocumentApiCredentials
from ..view_base import DocumentException
from ...hierarchy.models import Hierarchy
from ...product.calc import LoanCalculation
from ...product.models import ProductCalculation, ProductStatusTrack


def add(request, id, owner_id=None):
    document_type = DocumentType.objects.get(pk=id)
    owner = User.objects.get(pk=owner_id) if owner_id else None

    form_attributes = []

    AttributeUtils().get_attributes(parent=None, document_type=document_type, level=form_attributes, type='FORM')

    context = {
        'mode': settings.MODE_CREATE,
        'initial_owner_id': owner.pk if owner else None,
        'initial_owner_name': '%s %s %s' % (
            owner.company_name or '', owner.first_name or '', owner.last_name or '') if owner else '',
        'document_type': document_type,
    }

    return render(request=request, template_name='document/add_v2/add_v2.html', context=context)


def edit(request, id):
    document = Document.objects.get(pk=id)

    context = {
        'document': document,
        'previous_status': get_previous_status_course(document),
        'report_types': DocumentTypeReport.objects.filter(document_type=document.type, is_manual=True),
        # todo: from old version. Finally replace with new processFlow implementation, when done
        'doc_status_flow': [{
            'date': i.creation_date,
            'effective_date': i.effective_date,
            'status': i.status,
            'user': i.created_by
        } for i in DocumentStatusTrack.objects.filter(document=document).order_by('creation_date')],
        'product_status_flow': [{
            'date': i.creation_date,
            'effective_date': i.effective_date,
            'status': i.status,
            'user': i.created_by
        } for i in ProductStatusTrack.objects.filter(product=document.product).order_by('creation_date')] if hasattr(
            document, 'product') else [],
        'doc_statuses': document.type.status_set.all().order_by('sq'),
        'product_statuses': document.type.product_status_set.all().order_by('sq'),
        'reports': DocumentReport.objects.filter(document=document)
    }

    return render(request=request, template_name='document/edit_v2/edit_v2.html', context=context)


def definition(request, id):
    context = {
        'type': DocumentType.objects.get(pk=id)
    }
    return render(request=request, template_name='document/definition/definition.html', context=context)


# ----------------------------------------------


def get_previous_status_course(document):
    previous_status = None

    if document:
        try:
            result = DocumentStatusCourse.objects.filter(document=document).order_by('-creation_date')[1]
            if result:
                previous_status = result.status
        except IndexError:
            pass
    return previous_status


class DocumentApi(APIView):
    @staticmethod
    def calculate_document(document, user):
        if not document.product:
            return None
        LoanCalculation(document.product, user=user).calculate(start_date=datetime.date.today())
        return ProductCalculation.objects.filter(product=document.product).order_by('calc_date').last()

    @staticmethod
    def set_annex(document, annex, user):
        # recount calculation for today
        calculation = DocumentApi.calculate_document(annex, user)
        # todo: following tasks should be taken when annex document become working product
        return {
            "capital_required": calculation.capital_required or 0,
            "commission_required": calculation.commission_required or 0,
            "interest_for_delay_required": calculation.interest_for_delay_required or 0,
            "interest_required": calculation.interest_required
        }

    @staticmethod
    def get_hierarchy(document_type, attributes):
        try:
            hierarchy_attr = str(DocumentTypeAttributeMapping.objects.get(type=document_type,
                                                                          mapped_name='CREDITOR').attribute.pk)
        except DocumentTypeAttributeMapping.DoesNotExist:
            return None

        return Hierarchy.objects.get(
            pk=attributes[hierarchy_attr]['value']) if hierarchy_attr and hierarchy_attr in attributes else None

    @rest_api_wrapper
    def get(self, request):
        response_data = {}

        pk = request.query_params.get('id', None)
        type_id = request.query_params.get('typeId')

        document = Document.objects.get(pk=pk) if pk else None
        document_type = document.type if document else DocumentType.objects.get(pk=type_id)

        if document:
            process_flow_serializer = DocumentStatusTrackSerializer(
                DocumentStatusTrack.objects.filter(document=document).order_by('creation_date'), many=True
            )
            available_statuses_serializer = DocumentTypeProcessFlowSerializer(
                DocumentTypeProcessFlow.objects.filter(status=document.status).order_by('sq'), many=True
            )

            response_data = {
                'availableStatuses': available_statuses_serializer.data,
                'processFlow': process_flow_serializer.data
            }

        response_data['formAttributes'] = DocumentForm(document_type=document_type, instance=document,
                                                       user=request.user).get_form()

        return response_data

    @rest_api_wrapper
    def post(self, request):
        response_data = {}
        copy_annex_data = request.data.get('copyAnnexData', None)

        with transaction.atomic():
            document_type = DocumentType.objects.get(pk=request.data.get('type'))
            document_status = doc_utils.get_initial_status(document_type)

            # attributes processing
            attributes = json.loads(request.data.get('formData'))

            # get attribute codes for document creation
            del attributes['__REPEATABLE_SECTIONS']
            attribute_codes = {i.code: attributes[str(i.pk)]['value']
                               for i in DocumentTypeAttribute.objects.filter(pk__in=list(attributes.keys()))}

            if 'responsible' not in attribute_codes or not attribute_codes['responsible']:
                attribute_codes['responsible'] = request.user.pk

            attribute_codes['created_by'] = request.user.pk
            attribute_codes['code'] = doc_utils.get_document_code(document_type)
            attribute_codes['type'] = document_type.pk
            attribute_codes['status'] = document_status.pk

            serializer = DocumentSerializer(data=attribute_codes)

            if serializer.is_valid():
                # save document data based on attribute_codes
                if settings.APP_IN_VINDICATION:
                    if serializer.validated_data['owner'].last_name != 'Fasola':
                        raise Exception('Dokument może być wprowadzony jedynie dla klienta testowego (Jaś Fasola). '
                                        'Prosimy o kontakt z działem windykacji.')

                document = serializer.save()

                # save document attributes
                #  non-repeatable attribute processing
                for key, value in attributes.items():
                    DocumentApiUtils.save_value(document=document, key=key, value=value)
            else:
                raise DocumentException('Wystąpiły błędy w formularzu!', error_list=serializer.errors)

            # annex
            try:
                DocumentTypeAttributeMapping.objects.get(mapped_name='ANNEX').attribute.pk
            except DocumentTypeAttributeMapping.DoesNotExist:
                raise DocumentException("Brak mapowania dla atrybutu 'ANNEX', określającego id umowy ankesowanej")

            if document.annex:
                try:
                    Document.objects.get(pk=attribute_codes['annex'], status__code='ANX')
                    raise DocumentException("Umowa posiada już status 'Aneksowana'")

                except Document.DoesNotExist:
                    pass

                document.annex.annexed_by = document
                serializer.instance.annex.save()

                if copy_annex_data:
                    doc_utils.copy_annex_data(document=document)

            DocumentStatusTrack.objects.create(document=document, status=document_status, created_by=request.user)
            DocumentStatusCourse.objects.create(document=document, status=document_status, created_by=request.user)

            response_data['id'] = document.pk

        return response_data

    @rest_api_wrapper
    def put(self, request):
        response_data = {}

        document = Document.objects.get(pk=request.data.get('document'))

        if not DocumentApiCredentials.check_user_in_hierarchy(user=request.user, status=document.status):
            raise PermissionError(
                f"You don't have permission to perform this action as user '{request.user.username}'")

        with transaction.atomic():
            # document processing
            ver = document_services.get_ver(document.type, document.status)

            # attributes processing
            attributes = json.loads(request.data.get('attributes'))
            repeatable_sections = attributes.pop('__REPEATABLE_SECTIONS')

            # non-repeatable attribute processing
            for key, value in attributes.items():
                DocumentApiUtils.save_value(document=document, key=key, value=value,
                                            ver=ver[key] if key in ver else None)

            # repeatable section attribute processing
            for key, value in repeatable_sections.items():
                DocumentApiUtils.save_repeatable_section(document=document, key=key, value=value,
                                                         idx=attributes[key]['value'], ver=ver)

            # status processing
            document_status_id = request.data.get('status')
            if document_status_id:
                if settings.APP_IN_VINDICATION:
                    raise Exception('Funkcjonalność zmiany statusu dokumentu wstrzymana. '
                                    'Prosimy o kontakt z działem windykacji.')
                # BE AWARE: DocumentApi.change_status commits changes on the document!!!
                DocumentApiUtils.change_status(document, document_status_id, request.user)
            response_data['documentStatus'] = document_status_id

            DocumentApiUtils.trigger_common_action(user=request.user, document=document)

            # trigger action from class package
            DocumentApiUtils.trigger_action(user=request.user, document=document)

            document.hierarchy = DocumentApi.get_hierarchy(document_type=document.type, attributes=attributes)
            document.save()

        return response_data


class DocumentAnnexApi(APIView):
    def get(self, request):
        response_status = status.HTTP_200_OK
        response_data = []

        document_type = DocumentType.objects.get(pk=request.query_params.get('documentTypeId'))
        document_id = request.query_params.get('documentId')
        document = Document.objects.get(pk=document_id) if document_id else None
        owner = User.objects.get(pk=request.query_params.get('clientId'))

        try:
            # todo: zrobić to pobieranie w jednim miejscu, bo jest takie samo w rest_form
            response_data.extend([
                {"value": i.pk, "text": 'nr: %s z dn.: %s, wartość: %s' % (
                    i.code, i.product.start_date,
                    "{:,.2f}".format(i.product.value).replace(',', ' ').replace(',', '.'))}
                for i in Document.objects.filter(
                    type=document_type,
                    owner=owner,
                    product__isnull=False,
                    annexed_by__isnull=True,
                ).exclude(Q(status__code='ANX') | (Q(pk=document.pk) if document else Q()))
            ])

            if document and document.annex:
                response_data.append(
                    {"value": document.annex.pk, "text": 'nr: %s z dn.: %s, wartość: %s' %
                                                         (document.annex.code,
                                                          document.annex.product.start_date,
                                                          "{:,.2f}".format(document.annex.product.value).replace(',',
                                                                                                                 ' ').replace(
                                                              ',', '.'))
                     }
                )

        except Exception as ex:
            response_data = {}
            response_status = status.HTTP_400_BAD_REQUEST
            response_data['errmsg'] = str(ex)
            response_data['traceback'] = traceback.format_exc()

        return Response(data=response_data, status=response_status)


class AttachmentApi(APIView):

    @staticmethod
    def _save_attachment(*args, **kwargs):
        parent_id = kwargs.get('parent_id')

        attachment = Attachment.create(
            file_name=kwargs.get('file_name'),
            file_ext=kwargs.get('file_ext'),
            file_mime_type=kwargs.get('file_mime_type'),
            file_path=kwargs.get('file_path'),
            file_original_name=kwargs.get('file_original_name'),
            attachment_type='file',
            created_by_username=kwargs.get('created_by_username')
        )

        da = DocumentAttachment.objects.create(
            document=kwargs.get('document'),
            attachment=attachment,
            created_by=kwargs.get('user'),
            parent=DocumentAttachment.objects.get(pk=parent_id) if parent_id else None
        )
        return da

    def get(self, request):
        document = Document.objects.get(pk=request.query_params.get('id'))
        parent = DocumentAttachment.objects.get(pk=request.query_params.get('parent')) if request.query_params.get(
            'parent') else None

        q = DocumentAttachment.objects.filter(document=document, parent=parent).order_by('-is_dir', 'name',
                                                                                         'attachment__file_original_name')
        serializer = DocumentAttachmentSerializer(q, many=True)

        return Response(serializer.data)

    def post(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}

        try:
            response_data['saved_files'] = atm_utils.save_attachments(request=request,
                                                                      api={
                                                                          'path': 'document/attachments/',
                                                                          'store_class': Document,
                                                                          'save_fn': AttachmentApi._save_attachment,
                                                                          # getattr(AttachmentApi, '_save_attachment'),
                                                                          'serializer': DocumentAttachmentSerializer
                                                                      })

        except Exception as e:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data = {'errmsg': str(e), "traceback": traceback.format_exc()}

        return Response(response_data, status=response_status)

    def delete(self, request):
        try:
            with transaction.atomic():
                attachment = Attachment.objects.get(pk=request.data.get('attachmentId'))
                document = Document.objects.get(pk=request.data.get('documentId'))

                # No need to delete DocumentAttachment record due to on_delete.CASCADE entry in model
                # DocumentAttachment.objects.get(attachment=attachment, document=document).delete()
                attachment.delete()

                path = os.path.join(settings.ATTACHMENT_ROOT, str(document.pk), attachment.file_name)
                if os.path.exists(path):
                    os.remove(path)

                return Response(data={})

        except Exception as e:
            return Response(data={'errmsg': str(e), 'traceback': traceback.format_exc()}, exception=True,
                            status=status.HTTP_400_BAD_REQUEST)


class Section(APIView):
    @csrf_exempt
    def get(self, request):
        document_type = DocumentType.objects.get(pk=request.query_params.get('documentType'))
        data_type = request.query_params.get('dataType')
        q = Q(document_type=document_type)
        if data_type == 'MAIN':
            q &= Q(parent__isnull=True)

        queryset = DocumentTypeSection.objects.filter(q).prefetch_related(
            Prefetch('column_set', queryset=DocumentTypeSectionColumn.objects.order_by('sq').prefetch_related(
                Prefetch('column_attribute_set', queryset=DocumentTypeAttribute.objects.order_by('sq'))))).order_by(
            'sq')

        serializer = DocumentTypeSectionSerializer(queryset, many=True)
        return Response(serializer.data)


class AttributeModel(APIView):
    def __init__(self):
        super().__init__()
        self.document_type = None
        self.repeatable = False

    def update_model(self, document_type):
        attributes = []
        AttributeUtils.get_attributes(parent=None, document_type=document_type, level=attributes)

        document_type.model = attributes
        document_type.save()

    @staticmethod
    def _get_VER(attributes, attribute_VER, readonly, ver):

        for i in attributes:
            if any([i['is_section'], i['is_column'], i['is_combo']]):
                AttributeModel._get_VER(i['children'], attribute_VER, readonly, ver)
            else:
                # TODO: finally get VER from database DocumentTypeAttributeFeature for given document_status
                ver[i['id']] = {'visible': True, 'editable': not readonly, 'required': False}

    def get(self, request):
        document_type = DocumentType.objects.get(pk=request.query_params.get('documentType'))
        document_status = DocumentTypeStatus.objects.get(
            pk=request.query_params.get('documentStatus')) if request.query_params.get('documentStatus') else None

        attribute_type = request.query_params.get('type', None)

        attributes = []

        readonly = not DocumentApiCredentials.check_user_in_hierarchy(user=request.user, status=document_status)

        if not request.query_params.get('cache'):
            AttributeUtils.get_attributes(parent=None, document_type=document_type, level=attributes,
                                          type=attribute_type,
                                          status=document_status)
        else:
            attributes = document_type.model

        ver = {}
        AttributeModel._get_VER(attributes, None, readonly, ver)

        # TODO: at the moment detail VER taken for individual attributes from stored table data disabled.
        #  Have to back to it
        # if document_status:
        #     ver = {i.attribute.pk: {'v': i.visible, 'e': i.editable, 'r': i.required}
        #            for i in DocumentTypeAttributeFeature.objects.filter(status=document_status)}

        return Response(data={'model': attributes, 'ver': ver})

    def post(self, request):
        self.update_model(document_type=DocumentType.objects.get(pk=request.data['documentType']))
        return Response(data=[])


class AttributeSectionData(APIView):
    def get(self, request):
        section = request.query_params.get('sectionId')

        q = Q(attribute__is_section=False,
              attribute__is_column=False)
        if section:
            q &= Q(attribute__parent=section)

        data = {i.attribute.id: {'id': i.id,
                                 'value': i.value,
                                 'row_sq': i.row_sq,
                                 'row_uid': i.row_uid,
                                 'parent': i.parent.id if i.parent else ''} for i in DocumentAttribute.objects.filter(q)
                }
        return Response(data)


class AttributeApi(APIView):
    @staticmethod
    def get_form_attribute_data(document, data):
        _attributes = DocumentTypeAttribute.objects.filter(type='FORM', document_type=document.type, is_section=False,
                                                           is_column=False, is_combo=False, attribute__isnull=False)
        attributes = {}
        for i in _attributes:
            attributes[i.pk] = data[i.code] if i.code in data else None
        return attributes

    @staticmethod
    def get_attribute_data(document, attribute_type=None):
        q = Q(document_id=document.pk)
        if attribute_type:
            q &= Q(attribute__type=attribute_type)

        attributes = DocumentAttribute.objects.filter(q).order_by('attribute__pk', 'row_sq').prefetch_related(
            'attribute')
        attribute_data = {}

        for i in attributes:
            if i.row_sq is None or i.row_sq == '':
                attribute_data[i.attribute.pk] = {"value": i.value, "meta": i.value_data_meta}

            else:
                if i.attribute.pk not in attribute_data:
                    attribute_data[i.attribute.pk] = []
                attribute_data[i.attribute.pk].append({"value": i.value, "meta": i.value_data_meta})

        return attribute_data

    def get(self, request):
        document = Document.objects.get(pk=request.query_params.get('id'))
        attribute_data = AttributeApi.get_attribute_data(document)

        return Response(attribute_data)

    @transaction.atomic()
    def post(self, request):
        document = Document.objects.get(pk=request.data['document'])
        attributes = json.loads(request.data['attributes'])

        for key, value in attributes.items():
            if type(value) in (tuple, list):
                DocumentAttribute.objects.filter(attribute=key, document_id=document.pk,
                                                 row_sq__gte=len(value)).delete()
                for idx, i in enumerate(value):
                    try:
                        attr = DocumentAttribute.objects.get(attribute=key, document_id=document.pk, row_sq=idx)
                        attr.value = i
                        attr.save()
                    except DocumentAttribute.DoesNotExist:
                        DocumentAttribute.objects.create(
                            document_id=document.pk,
                            attribute=DocumentTypeAttribute.objects.get(pk=key),
                            value=i,
                            row_sq=idx
                        )
            else:
                try:
                    attr = DocumentAttribute.objects.get(attribute=key, document_id=document.pk)
                    attr.value = value
                    attr.save()
                except DocumentAttribute.DoesNotExist:
                    DocumentAttribute.objects.create(
                        document_id=document.pk,
                        attribute=DocumentTypeAttribute.objects.get(pk=key),
                        value=value
                    )

        return Response('ok')


class PredefinedView(APIView):
    def get(self, request):
        pass

    def post(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}
        try:
            predefined_list = json.loads(request.data.get('list'))
            id = request.data.get('id')

            at = DocumentTypeAttribute.objects.get(pk=id)
            at.feature['predefined']['list'] = predefined_list
            at.save()

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(data=response_data, status=response_status)

    def delete(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}
        try:
            id = request.data.get('id')
            at = DocumentTypeAttribute.objects.get(pk=request.data.get('attributeId'))
            document_id = request.data.get('documentId')
            row_id_attribute = DocumentTypeAttribute.objects.get(pk=at.feature['predefined']['rowid'])

            if DocumentAttribute.objects.filter(document_id=document_id, attribute=row_id_attribute, value=id).count():
                raise Exception('Wpis istnieje w przynajmniej jednym dokumencie')

            for i in at.feature['predefined']['list']:
                if i['id'] == id:
                    at.feature['predefined']['list'].remove(i)
                    at.save()
                    break

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = status.HTTP_400_BAD_REQUEST

        return Response(data=response_data, status=response_status)


class NoteApi(APIView):
    def get(self, request):
        response_status = status.HTTP_200_OK
        try:
            response_data = note_services.get_notes(Document.objects.get(pk=request.query_params.get('idDocument')))

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(data=response_data, status=response_status)

    def put(self, request):
        response_status = status.HTTP_200_OK
        try:
            response_data = note_services.update_note(request.data.get('id'), request.data.get('text'), request.user)

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(data=response_data, status=response_status)

    def post(self, request):
        response_status = status.HTTP_200_OK
        try:
            response_data = note_services.create_note(request.data.get('idDocument'), request.data.get('text'),
                                                      request.user)

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(data=response_data, status=response_status)

    def delete(self, request):
        response_status = status.HTTP_200_OK
        try:
            response_data = note_services.delete_note(request.data.get('id'))

        except Exception as ex:
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(data=response_data, status=response_status)
