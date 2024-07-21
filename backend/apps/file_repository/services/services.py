import datetime
import os.path
import uuid

from django.db import transaction
from rest_framework import status

from apps.file_repository import REPORT_REPO_DIR
import crm_settings
from apps.attachment.utils import get_mime_type
from apps.file_repository.api.serializers import FileRepositorySerializer
from apps.file_repository.models import FileRepository
from py3ws.decorators.decorators import rest_exception_handler
from py3ws.utils.utils import merge_two_dicts


@rest_exception_handler
def get_file(id=None):
    if id:
        return FileRepositorySerializer(instance=FileRepository.objects.get(pk=id), many=True).data

    return FileRepositorySerializer(instance=FileRepository.objects.all(), many=True).data


def _save_file(file):
    file_original_name = file.name
    file_internal_name = uuid.uuid4()
    file_ext = file_original_name[file_original_name.rfind(".") + 1:] if file_original_name.rfind(".") != -1 else None
    file_internal_full_name = f'{file_internal_name}.{file_ext}' if file_ext else file_internal_name
    path = os.path.join(crm_settings.MEDIA_ROOT, REPORT_REPO_DIR)

    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, f'{file_internal_name}.{file_ext}'), 'wb+') as dest_file:
        for chunk in file.chunks():
            dest_file.write(chunk)

    return [file_internal_full_name, file_ext]


@rest_exception_handler
def add_file(data, report_file, user):
    response_data = {}
    response_status = status.HTTP_200_OK
    serializer = FileRepositorySerializer(data=data)

    if not report_file:
        response_data = {"formErrors": {"file": ["Proszę wybrać plik dokumentu"]}}
        response_status = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"data": response_data, "status": response_status}

    if serializer.is_valid():
        with transaction.atomic():
            filename, file_ext = _save_file(report_file)

            serializer.validated_data['created_by'] = user.username
            serializer.validated_data['creation_date'] = datetime.datetime.now()
            serializer.validated_data['filename'] = filename
            serializer.validated_data['original_filename'] = report_file.name
            serializer.validated_data['mimetype'] = get_mime_type(file_ext)['type']
            serializer.save()

            response_data = serializer.data
    else:
        response_data = {"formErrors": merge_two_dicts(response_data, serializer.errors)}
        response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    return {"data": response_data, "status": response_status}


@rest_exception_handler
def delete_file(id=None):
    with transaction.atomic():
        reports = FileRepository.objects.get(pk=id) if id else FileRepository.objects.all()
        if type(reports == list):
            for report in reports:
                report.delete()
            return
        reports.delete()
