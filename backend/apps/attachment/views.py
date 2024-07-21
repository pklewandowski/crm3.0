from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.db import transaction
from django.contrib import messages

from apps.document.models import DocumentAttachment, Document
from . import utils as atm_utils
from .utils import get_mime_type, handle_uploaded_file, add_directory_to_tree, remove_attachment, rename_directory, is_path, is_empty, delete_directory_from_tree
from .utils import Tree
from .models import Attachment
from django.utils.timezone import now
from apps.user.models import User
import json
import uuid
import os
import traceback
from py3ws.utils.utils import myimport
from django.core.serializers import serialize






@csrf_exempt
def get_tree(request):
    response_data = {}
    status = 200

    try:
        id = request.POST.get('id')
        root_name = request.POST.get('root_name')
        root_dir_name = request.POST.get('root_dir_name')

        document = Document.objects.get(pk=id)

        tree = Tree()
        tree.results = '[{"state":{"disabled":false, "selected":true}, "data": {"type": "root"}, "text":"' + root_name + '", "children":['
        tree.get_tree(os.path.join(
            settings.ATTACHMENT_ROOT,
            root_dir_name),
            [i.attachment for i in document.attachment_set.all()]
        )  # TODO: zuniwersalizować, żeby było nietylko dla dokumentów - jakiś plugin wybierający attachments
        tree.results += ']}]'

        response_data['tree'] = tree.results
        response_data['status'] = 'OK'

    except Exception as ex:
        status = 400
        response_data['errmsg'] = str(ex)
        response_data['treaceback'] = traceback.format_exc()

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@transaction.atomic
@csrf_exempt
def upload(request):
    response_data = {}
    files = [request.FILES.get('attachments[%d]' % i) for i in range(0, len(request.FILES))]

    try:
        for f in files:
            file_name = uuid.uuid1().hex  # uuid.uuid4()
            file_ext = f.name.split(".")[-1]
            path = request.POST.get('path')
            id = request.POST.get('atm_owner_id')
            dirname = request.POST.get('dirname')
            atm_classname = request.POST.get('atm_classname')
            atm_owner_classname = request.POST.get('atm_owner_classname')

            handle_uploaded_file(f, file_name + '.' + file_ext, os.path.join(dirname, id, path))

            atm = Attachment.create(
                description=request.POST.get('attachment_description'),
                file_size=f.size,
                file_name=file_name,
                file_original_name=f.name,
                file_ext=file_ext,
                file_mime_type=get_mime_type(atm.file_ext)['type'],
                file_path=request.POST.get('path'),
                created_by_username=request.user.username
            )

            atm_cl = myimport(atm_classname)
            atm_owner_cl = myimport(atm_owner_classname)

            atm_cl.objects.create(attachment=atm, attachment_owner=atm_owner_cl.objects.get(pk=id))

            response_data['status'] = 'OK'

    except Exception as e:
        messages.add_message(request, messages.ERROR, str(e))
        response_data['status'] = 'ERROR'
        response_data['msg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def delete_directory(request):
    response_data = {}
    status = 200

    try:
        root_dir_name = request.POST.get('directory[root_dir_name]')
        _path = request.POST.get('directory[path]')

        path = os.path.join(root_dir_name, _path)

        if not is_path(path):
            raise Exception('Katalog nie istnieje')

        if not is_empty(path):
            raise Exception('Katalog musi być pusty')
        delete_directory_from_tree(path)

    except Exception as ex:
        status = 400
        response_data['errmsg'] = str(ex)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@csrf_exempt
def add_directory(request):
    response_data = {}
    status = 200

    try:

        root_dir_name = request.POST.get('directory[root_dir_name]')
        original_name = request.POST.get('directory[original_name]')
        _path = request.POST.get('directory[path]')
        try:
            path_root = _path.split('/')[-2]
        except IndexError:
            path_root = ''

        original_name_path = os.path.join(root_dir_name, path_root, original_name)
        path = os.path.join(root_dir_name, _path)

        if is_path(original_name_path):
            old_path = os.path.join(settings.ATTACHMENT_ROOT_RELATIVE, original_name_path, '').replace('\\', '/')
            new_path = os.path.join(settings.ATTACHMENT_ROOT_RELATIVE, path, '').replace('\\', '/')

            if old_path != new_path:
                with transaction.atomic():
                    for i in Attachment.objects.filter(file_path__startswith=old_path):
                        i.file_path = i.file_path.replace(old_path, new_path)
                        i.save()

                    rename_directory(original_name_path, path)

        else:
            add_directory_to_tree(path)

    except Exception as ex:
        status = 400
        response_data['errmsg'] = str(ex)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@csrf_exempt
def move(request):
    id = request.POST.get('id')
    doc_id = request.POST.get('doc_id')
    path = request.POST.get('path')
    response_data = {}
    status = 200

    try:
        with transaction.atomic():

            attachment = Attachment.objects.get(pk=id)

            src_path = os.path.join(settings.MEDIA_ROOT, attachment.file_path, attachment.file_name).replace('\\', '/')
            dst_patch = os.path.join(settings.MEDIA_ROOT, 'document/attachments/%s/%s' % (doc_id, path), attachment.file_name).replace('\\', '/')

            os.rename(src_path, dst_patch)

            attachment.file_path = 'document/attachments/%s/%s/' % (doc_id, path)
            attachment.save()

    except Exception as e:
        status = 400
        response_data['status'] = 'ERROR'
        response_data['errmsg'] = str(e)
    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@csrf_exempt
def remove(request):
    response_data = {}

    try:
        atm_owner = request.POST.get('attachment[atm_owner_id]')
        type = request.POST.get('attachment[type]')
        _path = request.POST.get('attachment[path]')
        root_dir_name = request.POST.get('attachment[root_dir_name]')
        filename = request.POST.get('attachment[filename]')

        path = os.path.join(root_dir_name, atm_owner, _path)
        remove_attachment(path, type)

        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['msg'] = str(e)
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def details(request):
    id = request.POST.get('id')
    response_data = {}
    atm = [Attachment.objects.get(pk=id)]
    response_data['data'] = serialize('json', atm)
    response_data['status'] = 'OK'
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@csrf_exempt
def basic_file_upload(request):
    status = 200

    try:
        files = [request.FILES.get('attachments[%d]' % i) for i in range(0, len(request.FILES))]
        _path = request.POST.get('path')
        create_attachment = request.POST.get('createAttachment')
        document_id = request.POST.get('documentId')
        saved_files = []

        if not create_attachment:
            create_attachment = False
        else:
            create_attachment = True

        if not document_id:
            raise Exception('[basic_file_upload]: Nie podano ID dokumentu')

        if not _path:
            _path = ''
            # raise Exception('[basic_file_upload]: nie podano ścieżki do pliku')

        path = os.path.join('document/attachments/', document_id, _path, '').replace('\\', '/')

        with transaction.atomic():

            document = Document.objects.get(pk=document_id)

            for f in files:
                file_name = uuid.uuid4().hex + (('.' + f.name.split(".")[-1]) or '')
                file_original_name = f.name
                file_ext = atm_utils.get_file_extension(file_name)
                file_mime_type = atm_utils.get_mime_type(file_ext)

                atm_utils.handle_uploaded_file(file=f, file_name=file_name, path=path, root_path=settings.MEDIA_ROOT)

                attachment = None
                if create_attachment:
                    attachment = Attachment.objects.create(
                        file_name=file_name,
                        file_ext=file_ext,
                        file_mime_type=file_mime_type['type'],
                        file_path=path,
                        file_original_name=file_original_name,
                        type='file',
                        user=request.user
                    )

                    DocumentAttachment.objects.create(
                        document=document,
                        attachment=attachment,
                        created_by=request.user
                    )

                file_info = {
                    'id': attachment.pk if attachment else '',
                    'file_name': file_name,
                    'file_Ext': file_ext,
                    'file_mime_type': file_mime_type['type'],
                    'file_path': path,
                    'file_original_name': file_original_name,
                    'mime': file_mime_type
                }
                saved_files.append(file_info)

            response_data = {'status': 'OK', 'saved_files': saved_files}

    except Exception as e:
        status = 400
        response_data = {'errmsg': str(e)}

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@csrf_exempt
def basic_scan_upload(request):
    files = [request.FILES.get('attachments[%d]' % i) for i in range(0, len(request.FILES))]
    saved_files = []

    try:
        for f in files:
            file_name = uuid.uuid4().hex + (('.' + f.name.split(".")[-1]) or '')
            file_original_name = f.name
            file_ext = atm_utils.get_file_extension(file_name)
            atm_utils.handle_uploaded_file(file=f, file_name=file_name, path='document/scan/', root_path=settings.MEDIA_ROOT)

            file_info = {
                'id': 1,
                'fileName': file_name,
                'fileExt': file_ext,
                'fileMimeType': atm_utils.get_mime_type(file_ext)['type'],
                'file_path': 'document/scan/',
                'fileOriginalName': file_original_name,
                'mime': atm_utils.get_mime_type(atm_utils.get_file_extension(file_original_name))
            }
            saved_files.append(file_info)

        response_data = {'status': 'OK', 'saved_files': saved_files}
        status = 200

    except Exception as e:
        status = 400
        response_data = {'status': 'ERROR', 'msg': str(e)}

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@csrf_exempt
def basic_prtscn_upload(request):
    try:
        document_id = request.POST.get('documentId')
        create_attachment = request.POST.get('createAttachment')
        image_data = request.POST.get('image_data')
        file_name = uuid.uuid4().hex + '.jpg'
        atm_utils.handle_printscreen_image(data=image_data, file_name=file_name, path='document/attachments/', root_path=settings.MEDIA_ROOT)

        if create_attachment:
            attachment = Attachment.objects.create(
                file_name=file_name,
                file_ext='jpg',
                file_mime_type=atm_utils.get_mime_type('jpg'),
                file_path='document/attachments/',
                file_original_name=file_name,
                type='file',
                user=request.user
            )

            DocumentAttachment.objects.create(document=Document.objects.get(pk=document_id), attachment=attachment)

        response_data = {'status': 'OK',
                         'file_name': file_name,
                         'file_ext': 'jpg',
                         'file_mime_type': atm_utils.get_mime_type('jpg')['type'],
                         'file_path': 'document/attachments/',
                         'file_original_name': file_name,
                         'mime': atm_utils.get_mime_type('jpg')
                         }
        status = 200

    except Exception as e:
        status = 400
        response_data = {'status': 'ERROR', 'msg': str(e)}

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


def download(request, id):
    attachment = Attachment.objects.get(pk=id)
    with open(os.path.join(settings.MEDIA_ROOT, attachment.file_path + attachment.file_name), 'r+b') as f:
        response = HttpResponse(f.read(), content_type='%s; %s' % (attachment.file_mime_type, 'charset=utf-8'))
        response['Content-Disposition'] = 'attachment; filename="%s"' % attachment.file_original_name.encode('ascii', 'replace').decode()
        f.close()
        return response


def download_file(request, file_name):
    mime_type = atm_utils.get_mime_type(file_name.split('.')[-1])
    with open(os.path.join(settings.MEDIA_ROOT, 'document/attachments/' + file_name), 'r+b') as f:
        response = HttpResponse(f.read(), content_type='%s; %s' % (mime_type, 'charset=utf-8'))
        response['Content-Disposition'] = 'attachment; filename="%s"' % file_name.encode('ascii', 'replace').decode()
        f.close()
        return response


def get_zip_attachemnts(request, id):
    document = Document.objects.get(pk=id)
    atm = [i.attachment for i in DocumentAttachment.objects.filter(document=document)]
    zipname = atm_utils.zip(atm)

    with open(zipname, 'r+b') as f:
        response = HttpResponse(f.read(), content_type='%s; %s' % ("application/zip", 'charset=utf-8'))
        response['Content-Disposition'] = 'attachment; filename="%s.zip"' % document.code or 'attm'
        f.close()
        os.remove(zipname)
        return response
