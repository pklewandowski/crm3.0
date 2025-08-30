import datetime
import mimetypes
import os
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

from django.conf import settings
from django.core.mail import EmailMessage

from apps.message.models import MessageQueue, MessageTemplate, MessageTemplateParamDefinition


class MessageException(Exception):
    pass


def _bind_formal_params(text: str):
    _text = text.replace('$P__DATE__P$', datetime.date.today().strftime("%Y-%m-%d"))
    _text = _text.replace('$P__TIME__P$', datetime.datetime.today().strftime("%H:%M"))
    return _text


def bind_params(text: str, source: dict = None, add_params: dict = None, test=False):
    """
    bind_params: binds params to the message text placeholders
    :param text: Message text
    :param source: dict containing class object instance which data is used to compose mail, ie: 'user': [<Admin Admin> apps.user.User object], ...}
    :param add_params: additional parameters specific for particular template
    :param test: Indicator if processing test message. If so, bind message with test params and sends test on the logged user email.
    :return: dict {message binded text, attachments}
    """
    if not text:
        text = ''

    include_list = MessageTemplate.objects.filter(type='INC')
    text = _bind_formal_params(text)
    attachments = {}

    if source:
        param_list = MessageTemplateParamDefinition.objects.all()
        for p in param_list:
            if test:
                text = text.replace("$P__%s__P$" % p.code, p.test_value)
            else:
                if p.type == 'model':
                    if p.model and p.field:
                        text = text.replace("$P__%s__P$" % p.code, getattr(source[p.model], p.field) or '')
                    else:
                        raise MessageException('Parametr typu \'model\' musi posiadać wypełone pola [model] oraz [field]')

                elif p.type == 'cid':
                    if type(add_params) == 'dict':
                        if p.code in add_params.keys():
                            text = text.replace("$P__%s__P$" % p.code, '<img src="cid:%s"/>' % p.code)
                            attachments[p.code] = add_params[p.code]

    if type(add_params) == dict:
        for k, v in add_params.items():
            text = text.replace("$P__%s__P$" % k, v)

    for i in include_list:
        text = text.replace("$INC__%s__INC$" % i.code, i.text)

    return {'text': text, 'attachments': attachments}


def register_message(template, source=None, add_params=None, recipients=None, phones=None, subject=None, send_immediately=False):
    if not recipients and not phones:
        raise MessageException('Brak adresatów')

    subject = subject if subject else template.subject

    if not subject:
        raise MessageException('Temat wiadomości nie może być pusty')

    bind = bind_params(text=template.text, source=source, add_params=add_params)
    text = bind['text']

    attachments = bind['attachments']

    bind = bind_params(text=template.sms_text, source=source, add_params=add_params)
    sms_text = bind['text']

    mq = MessageQueue.objects.create(
        template=template,
        subject=subject,
        text=text,
        sms_text=sms_text,
        attachments=attachments,
        recipients=recipients,
        phones=phones,
        is_sent=False)

    if send_immediately:
        try:
            send_message(subject=subject, body=text, attachments=attachments, to=recipients, phones=phones)
            mq.is_sent = True
            mq.send_date = datetime.datetime.now()
            mq.save()
        except Exception:
            raise MessageException('Wiadomość została dodana do listy wysyłkowej, ale nie udało się jej wysłać natychmiastowo. System ponowi próbę wysłania w ciągu kilku minut.')


def attach_file_to_multipart_message(message, file, content_id=None):
    content_type, encoding = mimetypes.guess_type(file)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'

    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(file, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(file, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(file, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(file, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(file)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    if content_id:
        msg.add_header('Content-ID', '<%s>' % content_id)

    message.attach(msg)


def send_message(subject, body, sms_text=None, to=None, cc=None, phones=None, attachments=None):
    if to:
        msg = EmailMessage(subject=subject, body=body, to=to, cc=cc)
        msg.content_subtype = "html"

        if attachments:
            if type(attachments) is not dict:
                raise MessageException('[send_message] lista załączników nie jest typu dict')
            for content_id, file_path in attachments.items():
                try:
                    attach_file_to_multipart_message(msg, file_path, content_id=content_id)
                except Exception as ex:
                    # todo: Handle this exception somehow
                    pass

        msg.send(fail_silently=False)

        if attachments:
            for file_path in attachments.values():
                os.remove(file_path)

    if phones:
        pass
        # from smsapi.client import SmsApiPlClient
        # from smsapi.exception import SmsApiException
        #
        # client = SmsApiPlClient(access_token=settings.SMSAPI_ACCESS_TOKEN)
        # for phone in phones:
        #     try:
        #         send_results = client.sms.send(to=phone, message=sms_text)
        #     except SmsApiException as ex:
        #         # todo: Handle this exception somehow
        #         pass
