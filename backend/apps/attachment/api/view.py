import os
import traceback

from django.db import transaction
from rest_framework import status

import crm_settings

from rest_framework.response import Response
from rest_framework.views import APIView

import py3ws.utils.utils as py3ws_utils
from apps.document.models import Document, DocumentAttachment, DocumentTypeAssociate, DocumentType
from apps.attachment.utils import Tree


class TreeApi(APIView):

    def get(self, request):
        response_data = {}
        response_status = status.HTTP_200_OK

        try:
            id = request.query_params.get('id')
            document_type = DocumentType.objects.get(pk=request.query_params.get('documentTypeId'))
            root_name = request.query_params.get('root_name')

            attachment_class = py3ws_utils.get_class(DocumentTypeAssociate.objects.get(document_type=document_type, type='ATTACHMENT').class_name)
            document = py3ws_utils.get_class(DocumentTypeAssociate.objects.get(document_type=document_type, type='HOME').class_name).objects.get(pk=id)

            tree = Tree(directory_only=True)

            tree.results = {
                "state": {"disabled": False, "selected": True},
                "data": {"type": "root", "id": '__root__'},
                "id": "__root__",
                "text": root_name,
                "children": tree.get_tree(document, attachment_class)
            }

            response_data['tree'] = tree.results
            response_data['status'] = 'OK'

        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data['errmsg'] = str(ex)
            response_data['traceback'] = traceback.format_exc() or ''

        return Response(data=response_data, status=response_status)

    def post(self, request, *args, **kwargs):
        response_data = {}
        response_status = status.HTTP_200_OK

        try:
            name = request.data.get('name')
            parent_id = request.data.get('parentId')
            document_id = request.data.get('documentId')
            document_type = DocumentType.objects.get(pk=request.data.get('documentTypeId'))

            if not name or not parent_id:
                raise AttributeError('Brak wymagalnych danych: nazwa i/lub id parent')

            attachment_class = py3ws_utils.get_class(DocumentTypeAssociate.objects.get(document_type=document_type, type='ATTACHMENT').class_name)
            document = py3ws_utils.get_class(DocumentTypeAssociate.objects.get(document_type=document_type, type='HOME').class_name).objects.get(pk=document_id)

            parent = attachment_class.objects.get(pk=parent_id) if not parent_id == '__root__' else None

            # validate name
            try:
                if attachment_class.objects.get(document=document, name=name, name__isnull=False, parent=parent):
                    raise AttributeError('Nazwa katalogu \'%s\' już istnieje' % name)
            except attachment_class.DoesNotExist:
                pass

            node = attachment_class.objects.create(
                document=document,
                is_dir=True,
                name=name,
                parent=attachment_class.objects.get(pk=parent_id) if not parent_id == '__root__' else None,
                created_by=request.user
            )

            response_data['node'] = {"id": node.pk, "name": name, "parent": parent_id}

        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data['errmsg'] = str(ex)
            response_data['traceback'] = traceback.format_exc() or ''

        return Response(data=response_data, status=response_status)

    def put(self, request, *args, **kwargs):
        response_data = {}
        response_status = status.HTTP_200_OK

        try:
            id = request.data.get('id')
            name = request.data.get('name')
            document_type = DocumentType.objects.get(pk=request.data.get('documentTypeId'))
            attachment_class = py3ws_utils.get_class(DocumentTypeAssociate.objects.get(document_type=document_type, type='ATTACHMENT').class_name)

            node = attachment_class.objects.get(pk=id)
            node.name = name
            node.save()

        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data['errmsg'] = str(ex)
            response_data['traceback'] = traceback.format_exc() or ''

        return Response(data=response_data, status=response_status)

    def delete(self, request, *args, **kwargs):
        response_data = {"deleted_files": []}
        response_status = status.HTTP_200_OK

        document_type = DocumentType.objects.get(pk=request.data.get('documentTypeId'))
        attachment_class = py3ws_utils.get_class(DocumentTypeAssociate.objects.get(document_type=document_type, type='ATTACHMENT').class_name)

        def f(parent):

            for i in attachment_class.objects.filter(parent=parent):
                if i.is_dir:
                    f(i)
                else:
                    i.attachment.delete()
                    path = os.path.join(crm_settings.MEDIA_ROOT, i.attachment.file_path, i.attachment.file_name)
                    if os.path.exists(path):
                        os.remove(path)
                    response_data['deleted_files'].append(i.pk)


        try:
            with transaction.atomic():
                node = attachment_class.objects.get(pk=request.data.get('id'))
                f(node)
                node.delete()

        except Exception as ex:
            response_status = status.HTTP_400_BAD_REQUEST
            response_data['errmsg'] = str(ex)
            response_data['traceback'] = traceback.format_exc() or ''

        return Response(data=response_data, status=response_status)
