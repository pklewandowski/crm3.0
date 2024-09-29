import datetime
import calendar
from uuid import uuid4

import os
import imgkit
import pdfkit
import base64

from py3ws.utils import utils as py3ws_utils

from django.conf import settings

months = ["Unknown",
          "Styczeń",
          "Luty",
          "Marzec",
          "Kwiecień",
          "Maj",
          "Czerwiec",
          "Lipiec",
          "Sierpień",
          "Wrzesień",
          "Październik",
          "Listopad",
          "Grudzień"]
days = ["pn", "wt", "śr", "cz", "pt", "so", "ni"]


def render_calendar(dt, bkg='#378acd', clr='#ffffff'):
    if not isinstance(dt, datetime.date):
        return ''
    weekday, last_day = calendar.monthrange(dt.year, dt.month)
    weekday = weekday
    s = '<tr><td colspan=7 style="width:100%%">%s</td></tr><tr>' % months[dt.month]
    i = 1

    ldwd = last_day + weekday
    cells = (ldwd // 7) * 7 + (7 if ldwd % 7 else 0)

    for r in days:
        s += '<td style="font-weight: 700; background-color: #dddddd;">%s</td>' % r
    s += "</tr><tr>"

    for r in range(0, weekday):
        s += "<td></td>"

    while i <= cells - weekday:
        if not (i + weekday - 1) % 7:
            s += "</tr><tr>"
        s += "<td%s>%s</td>" % (' style="background-color: %s; color: %s;"' % (bkg, clr) if i == dt.day else '', i if i <= last_day else '')
        i += 1
    s += "</tr>"
    return s


def render_calendar_formant(start=None, end=None, template='calendar_template.html', base64=False):
    path_wkthmltoimage = settings.WKHTMLTOIMAGE_PATH  # r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
    config = imgkit.config(wkhtmltoimage=path_wkthmltoimage)
    uid = uuid4().hex
    dt = datetime.date(start.year, start.month, start.day)
    start = datetime.datetime.strftime(start, '%H:%M')
    end = datetime.datetime.strftime(end, '%H:%M')

    file_path = os.path.join(settings.MEDIA_ROOT, "templates/%s") % template
    output_path = os.path.join(settings.MEDIA_ROOT, "templates/output/%s.jpg" % uid)

    f = open(file_path, 'rt')
    txt = f.read()
    f.close()
    txt = txt.replace('$P__CALENDAR_FORMANT__P$', render_calendar(dt))
    txt = txt.replace('$P__START_HOUR__P$', start)
    txt = txt.replace('$P__END_HOUR__P$', end)

    options = {
        'format': 'jpg',
         # 'crop-h': '180',
         'crop-w': '160',
        # 'crop-x': '3',
        # 'crop-y': '3',
        'encoding': "UTF-8",
    }

    options = py3ws_utils.merge_two_dicts(options, settings.WKHTMLTOIMAGE_OPTIONS)

    imgkit.from_string(txt, output_path, config=config, options=options)

    if not base64:
        return output_path

    with open(output_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
        encoded_string = 'data:image/jpg;base64,' + encoded_string
    image_file.close()
    return encoded_string
