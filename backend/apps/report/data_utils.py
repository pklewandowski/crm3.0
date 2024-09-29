import codecs
import uuid

import os

from django.conf import settings


def _create_data_file(xml_data):
    file_name_uuid = str(uuid.uuid4())
    data_file_name = file_name_uuid + ".xml"
    data_file_path = os.path.join(settings.MEDIA_ROOT, "reports/data/") + data_file_name
    f = codecs.open(data_file_path, "w", "utf-8")
    f.write(xml_data)
    f.close()
    return data_file_path
