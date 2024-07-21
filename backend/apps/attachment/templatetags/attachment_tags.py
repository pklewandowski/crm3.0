from django import template
from django.templatetags.static import static
from apps.attachment import utils as atm_utils
from django.conf import settings
register = template.Library()


def _get_file_basic_type(file_mime_type):
    return 'IMG' if 'IMAGE' in file_mime_type.upper() else 'DOC'


def _get_file_mime_type_icon(file_mime_type):
    return static('attachment/img/file_types/bmp/bmp-256_32.png')


@register.simple_tag(name='get_file_icon_image')
def get_file_icon_image(attachment):
    if _get_file_basic_type(attachment.file_mime_type) == 'IMG':
        return settings.MEDIA_URL + attachment.file_path + attachment.file_name
    else:
        return static('attachment/img/file_types' + atm_utils.get_mime_type(attachment.file_ext)['icon_lg'])
            # _get_file_mime_type_icon(attachment.file_mime_type)
