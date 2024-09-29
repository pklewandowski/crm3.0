import base64
import os
import re
import traceback
import uuid
import zipfile
from pprint import pprint

from django.conf import settings
from django.db import transaction
from django.forms import modelformset_factory, forms
from django import forms

from apps.attachment.forms import AttachmentForm
from apps.attachment.models import Attachment
from apps.document.forms import DocumentAttachmentForm
from apps.document.models import DocumentAttachment
from py3ws.utils import utils as py3ws_utils

_md_size = '48_32'
mime_types = {
    "pdf": {'type': "application/pdf", 'icon_lg': '/pdf/pdf-256_32.png', 'icon_md': f'/pdf/pdf-{_md_size}.png', 'icon_sm': '/pdf/pdf-sm-32_32.png'}
    , "pdfx": {'type': "application/pdf", 'icon_md': '', 'icon_lg': '', 'icon_sm': ''}
    , "exe": {'type': "application/octet-stream", 'icon_md': '', 'icon_lg': '', 'icon_sm': ''}
    , "zip": {'type': "application/zip", 'icon_lg': '/zip/zip-256_32.png', 'icon_md': f'/zip/zip-{_md_size}.png', 'icon_sm': '/zip/zip-sm-32_32.png'}
    , "rar": {'type': "application/rar", 'icon_lg': '/rar/rar-256_32.png', 'icon_md': f'/rar/rar-{_md_size}.png', 'icon_sm': '/rar/rar-sm-32_32.png'}
    , "docx": {'type': "application/msword", 'icon_lg': '/docx_win/docx_win-256_32.png', 'icon_md': f'/docx_win/docx_win-{_md_size}.png', 'icon_sm': '/docx_win/docx_win-sm-32_32.png'}
    , "doc": {'type': "application/msword", 'icon_lg': '/docx_win/docx_win-256_32.png', 'icon_md': f'/docx_win/docx_win-{_md_size}.png', 'icon_sm': '/docx_win/docx_win-sm-32_32.png'}
    , "rtf": {'type': "application/msword", 'icon_lg': '/docx_win/docx_win-256_32.png', 'icon_md': f'/docx_win/docx_win-{_md_size}.png', 'icon_sm': '/docx_win/docx_win-sm-32_32.png'}
    , "csv": {'type': "application/vnd.ms-excel", 'icon_lg': '/xlsx_win/xlsx_win-256_32.png', 'icon_md': f'/xlsx_win/xlsx_win-{_md_size}.png', 'icon_sm': '/xlsx_win/xlsx_win-sm-32_32.png'}
    , "xls": {'type': "application/vnd.ms-excel", 'icon_lg': '/xlsx_win/xlsx_win-256_32.png', 'icon_md': f'/xlsx_win/xlsx_win-{_md_size}.png', 'icon_sm': '/xlsx_win/xlsx_win-sm-32_32.png'}
    , "xlsx": {'type': "application/vnd.ms-excel", 'icon_lg': '/xlsx_win/xlsx_win-256_32.png', 'icon_md': f'/xlsx_win/xlsx_win-{_md_size}.png', 'icon_sm': '/xlsx_win/xlsx_win-sm-32_32.png'}
    , "xlsm": {'type': "application/vnd.ms-excel", 'icon_lg': '/xlsx_win/xlsx_win-256_32.png', 'icon_md': f'/xlsx_win/xlsx_win-{_md_size}.png', 'icon_sm': '/xlsx_win/xlsx_win-sm-32_32.png'}
    , "ppt": {'type': "application/vnd.ms-powerpoint", 'icon_lg': '/pptx_win/pptx_win-256_32.png', 'icon_md': f'/pptx_win/pptx_win-{_md_size}.png', 'icon_sm': '/pptx_win/pptx_win-sm-32_32.png'}
    , "pptx": {'type': "application/vnd.ms-powerpoint", 'icon_lg': '/pptx_win/pptx_win-256_32.png', 'icon_md': f'/pptx_win/pptx_win-{_md_size}.png', 'icon_sm': '/pptx_win/pptx_win-sm-32_32.png'}
    , "gif": {'type': "image/gif", 'icon_lg': '/gif/gif-256_32.png', 'icon_md': f'/gif/gif-{_md_size}.png', 'icon_sm': '/gif/gif-sm-32_32.png'}
    , "tif": {'type': "image/tiff", 'icon_lg': '/tiff/tiff-256_32.png', 'icon_md': f'/tiff/tiff-{_md_size}.png', 'icon_sm': '/tiff/tiff-sm-32_32.png'}
    , "tiff": {'type': "image/tiff", 'icon_lg': '/tiff/tiff-256_32.png', 'icon_sm': '/tiff/tiff-sm-32_32.png'}
    , "png": {'type': "image/png", 'icon_lg': '/png/png-256_32.png', 'icon_md': f'/png/png-{_md_size}.png', 'icon_sm': '/png/png-sm-32_32.png'}
    , "jpeg": {'type': "image/jpg", 'icon_lg': '/jpeg/jpeg-256_32.png', 'icon_md': f'/jpeg/jpeg-{_md_size}.png', 'icon_sm': '/jpeg/jpeg-sm-32_32.png'}
    , "jpg": {'type': "image/jpg", 'icon_lg': '/jpeg/jpeg-256_32.png', 'icon_md': f'/jpeg/jpeg-{_md_size}.png', 'icon_sm': '/jpeg/jpeg-sm-32_32.png'}
    , "mp3": {'type': "audio/mpeg", 'icon_lg': '/mp3/mp3-256_32.png', 'icon_sm': '/mp3/mp3-sm-32_32.png'}
    , "wav": {'type': "audio/x-wav", 'icon_lg': '/wav/wav-256_32.png', 'icon_sm': '/wav/wav-sm-32_32.png'}
    , "mpeg": {'type': "video/mpeg", 'icon_lg': '/mpeg/mpeg-256_32.png', 'icon_sm': '/mpeg/mpeg-sm-32_32.png'}
    , "mpg": {'type': "video/mpeg", 'icon_lg': '/mpeg/mpeg-256_32.png', 'icon_sm': '/mpeg/mpeg-sm-32_32.png'}
    , "mpe": {'type': "video/mpeg", 'icon_lg': '/mpeg/mpeg-256_32.png', 'icon_sm': '/mpeg/mpeg-sm-32_32.png'}
    , "mov": {'type': "video/quicktime", 'icon_lg': '/mov/mov-256_32.png', 'icon_sm': '/mov/mov-sm-32_32.png'}
    , "avi": {'type': "video/x-msvideo", 'icon_lg': '/avi/avi-256_32.png', 'icon_sm': '/avi/avi-sm-32_32.png'}
    , "3gp": {'type': "video/3gpp", 'icon_lg': '', 'icon_sm': ''}
    , "css": {'type': "text/css", 'icon_lg': '/css/css-256_32.png', 'icon_sm': '/css/css-sm-32_32.png'}
    , "jsc": {'type': "application/javascript", 'icon_lg': '', 'icon_sm': ''}
    , "js": {'type': "application/javascript", 'icon_lg': '', 'icon_sm': ''}
    , "php": {'type': "text/html", 'icon_lg': '', 'icon_sm': ''}
    , "htm": {'type': "text/html", 'icon_lg': '', 'icon_sm': ''}
    , "html": {'type': "text/html", 'icon_lg': '', 'icon_sm': ''}
    , "flac": {'type': "audio/flac", 'icon_lg': '/waw/waw-256_32.png', 'icon_sm': '/waw/waw-sm-32_32.png'}
    , "eml": {'type': "message/rfc822", 'icon_lg': '/eml/eml-256_32.png', 'icon_sm': '/eml/eml-sm-32_32.png'}
    , "msg": {'type': "message/rfc822", 'icon_lg': '/eml/eml-256_32.png', 'icon_sm': '/eml/eml-sm-32_32.png'}
    , "__default__": {'type': "application/octet-stream", 'icon_lg': '', 'icon_md': '', 'icon_sm': ''}
}


def handle_uploaded_file(file, file_name, path, root_path=None):
    if root_path:
        path_bundled = os.path.join(root_path, path)
    else:
        path_bundled = os.path.join(settings.ATTACHMENT_ROOT, path)

    if not os.path.exists(path_bundled):
        os.makedirs(path_bundled, exist_ok=True)

    with open(os.path.join(path_bundled, file_name), 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def handle_file(file, file_name, path, root_path=None):
    if root_path:
        path_bundled = os.path.join(root_path, path)
    else:
        path_bundled = os.path.join(settings.ATTACHMENT_ROOT, path)

    if not os.path.exists(path_bundled):
        os.makedirs(path_bundled, exist_ok=True)

    with open(os.path.join(path_bundled, file_name), 'wb+') as destination:
        destination.write(file)


def handle_printscreen_image(data, file_name, path, root_path=None):
    data_url_pattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
    image_data = data
    image_data = data_url_pattern.match(image_data).group(2)
    image_data = image_data.encode()
    image_data = base64.b64decode(image_data)

    handle_file(file=image_data, file_name=file_name, path=path, root_path=root_path)


def is_path(path):
    path_bundled = os.path.join(settings.ATTACHMENT_ROOT, path)
    return os.path.exists(path_bundled)


def is_empty(path):
    path_bundled = os.path.join(settings.ATTACHMENT_ROOT, path)
    return False if os.listdir(path_bundled) else True


def add_directory_to_tree(path):
    path_bundled = os.path.join(settings.ATTACHMENT_ROOT, path)

    if not os.path.exists(path_bundled):
        os.makedirs(path_bundled, exist_ok=True)


def rename_directory(src_path, dst_path):
    src_path_bundled = os.path.join(settings.ATTACHMENT_ROOT, src_path)
    dst_path_bundled = os.path.join(settings.ATTACHMENT_ROOT, dst_path)
    os.rename(src_path_bundled, dst_path_bundled)


def delete_directory_from_tree(path):
    path_bundled = os.path.join(settings.ATTACHMENT_ROOT, path)
    os.rmdir(path_bundled)


def remove_attachment(path, type):
    path_bundled = os.path.join(settings.ATTACHMENT_ROOT, path)

    if type == 'directory':
        os.rmdir(path_bundled)
    else:
        os.remove(path_bundled)


def get_file_extension(file_name):
    return file_name.rsplit('.', 1)[1].lower()


def get_mime_type(mime):
    try:
        return mime_types[mime]
    except KeyError:
        return mime_types['__default__']


def get_attachment_formset(data, queryset, prefix='attachment'):
    AttachmentFormset = modelformset_factory(AttachmentForm.Meta.model, form=AttachmentForm, extra=0, can_delete=True)
    attachment_formset = AttachmentFormset(data=data, queryset=queryset, prefix=prefix)
    for i in attachment_formset:
        i.fields['DELETE'].widget = forms.HiddenInput()
        i.fields['DELETE'].widget.attrs = {'class': 'formset-row-delete'}
    return attachment_formset


def zip(attachments):
    zipname = uuid.uuid4().hex
    full_path = settings.MEDIA_ROOT + "/temp/%s.zip" % zipname
    os.makedirs(settings.MEDIA_ROOT + "/temp", exist_ok=True)

    with zipfile.ZipFile(full_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for attachment in attachments:
            atm_path = os.path.join(settings.MEDIA_ROOT, attachment.file_path + attachment.file_name)
            zipf.write(atm_path, attachment.file_original_name)
    return full_path


class Tree:
    def __init__(self, *args, **kwargs):
        self.results = ''
        self.directory_only = kwargs.get('directory_only', False)

    def get_tree(self, document, attachment_class):
        tree = []

        def f(level, parent):
            dirs = attachment_class.objects.filter(document=document, parent=parent).order_by('name')

            for i in dirs:
                if i.is_dir:
                    data = {
                        "data": {"type": "directory"},
                        "text": i.name,
                        "id": i.pk
                    }
                else:
                    if self.directory_only:
                        continue
                    data = {"data": {"type": "file", "filename": i.attachment.file_name},
                            "text": i.attachment.file_original_name,
                            "icon": "jstree-file",
                            "id": i.pk
                            }
                data['children'] = []
                level.append(data)

                f(level[-1]['children'], i)

        f(tree, parent=None)

        return tree


def save_attachments(request, api):
    files = [request.FILES.get('attachments[%d]' % i) for i in range(0, len(request.FILES))]
    image_data = request.data.get('image_data')
    _path = request.data.get('path')
    document_id = request.data.get('documentId')
    parent_id = request.data.get('parent') or None

    if parent_id == '__root__':
        parent_id = None

    saved_files = []

    if not document_id:
        raise Exception('[basic_file_upload]: Nie podano ID dokumentu')

    if not _path:
        _path = ''

    path = os.path.join(api['path'], document_id, _path, '').replace('\\', '/')
    document = api['store_class'].objects.get(pk=document_id)

    with transaction.atomic():
        if image_data:
            file_name = uuid.uuid4().hex + '.png'
            handle_printscreen_image(data=image_data, file_name=file_name, path=path, root_path=settings.MEDIA_ROOT)

            da = api['save_fn'](
                file_name=file_name,
                file_ext='png',
                file_mime_type='image/png',
                file_path=path,
                file_original_name=file_name,
                type='file',
                created_by_username=request.user.username,
                document=document,
                parent_id=parent_id,
                user=request.user
            )

        elif files:
            for f in files:
                file_name = uuid.uuid4().hex + (('.' + f.name.split(".")[-1]) or '')
                file_original_name = f.name
                file_ext = get_file_extension(file_name)
                file_mime_type = get_mime_type(file_ext)

                handle_uploaded_file(file=f, file_name=file_name, path=path, root_path=settings.MEDIA_ROOT)

                da = api['save_fn'](
                    file_name=file_name,
                    file_ext=file_ext,
                    file_mime_type=file_mime_type['type'],
                    file_path=path,
                    file_original_name=file_original_name,
                    type='file',
                    document=document,
                    created_by_username=request.user.username,
                    parent_id=parent_id,
                    user=request.user
                )

        saved_files.append(api['serializer'](da).data)

    return saved_files
