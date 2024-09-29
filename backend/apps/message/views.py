import json
import re
import traceback

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from apps.message.forms import MessageTemplateForm
from apps.message.models import MessageTemplate, MessageTemplateParam, MessageTemplateParamDefinition, MessageQueue
from py3ws.utils import utils as py3ws_utils
from py3ws.views import generic_view
from utils.email_message import send_message
from . import utils as msg_utils


class MessageView(generic_view.GenericView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'message'

    def __init__(self):
        super(MessageView, self).__init__()


def index(request):
    return HttpResponse("Zarządzanie powiadomiemiami.")


def list_template(request):
    templates = MessageTemplate.objects.all()
    context = {'templates': templates}
    return render(request, 'message/template/list.html', context=context)


def send(request):
    send_message(to=['pklewandowski@gmail.com', ], subject='CRM INFO', body='Ala Makota')
    return JsonResponse({'status': 'OK'})


class _ManageTemplate(MessageView):
    param_list = MessageTemplateParamDefinition.objects.all()
    include_list = None
    template = None
    instance = None

    def _save_template(self, form):
        template = form.save(commit=False)
        template.editable = True
        template.sms_text = py3ws_utils.translate_pl_to_latin(template.sms_text)
        template.save()
        params = re.findall("(\$(P)__)(\w*)(__P\$)", template.text)
        includes = re.findall("(\$(INC)__)(\w*)(__INC\$)", template.text)
        MessageTemplateParam.objects.filter(template=template).delete()

        if params:
            for i in params:
                MessageTemplateParam.objects.create(template=template, code=i[2], type=i[1])

        if includes:
            for i in includes:
                MessageTemplateParam.objects.create(template=template, code=i[2], type=i[1])

    @method_decorator(login_required)
    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        form = MessageTemplateForm(request.POST or None, instance=self.instance)

        if request.POST:
            if form.is_valid():
                self._save_template(form)
                return redirect('message.template.list')

        context = {'form': form, 'param_list': self.param_list, 'include_list': self.include_list}
        return render(request=request, template_name=self.template, context=context)


class ListView(generic_view.ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'message'

    def __init__(self):
        self.default_sort_field = 'creation_date'
        super(ListView, self).__init__()

    def set_where(self):
        self.where = Q(editable=True)
        if self.search:
            pass

    def set_query(self):
        self.query = MessageQueue.objects.filter(self.where).order_by('%s%s' % (self.sort_dir, self.sort_field))

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        super(ListView, self).dispatch(request, *args, **kwargs)
        return self.list(request=request, template='message/queue_list.html')


class Add(_ManageTemplate):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    template = 'message/template/add.html'
    include_list = MessageTemplate.objects.filter(type='INC')


class Edit(_ManageTemplate):
    template = 'message/template/edit.html'

    def set_mode(self):
        self._mode = settings.MODE_EDIT

    @method_decorator(login_required)
    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        self.instance = MessageTemplate.objects.get(pk=self.kwargs['id'])
        if not self.instance.editable:
            raise Exception('Szablon wiadomości jest oznaczony nie do edycji')
        self.include_list = MessageTemplate.objects.filter(type='INC').exclude(pk=self.instance.pk)
        return super(Edit, self).dispatch(request, *args, **kwargs)


@csrf_exempt
def queue_preview(request):
    status = 200
    response_data = {}
    id = request.POST.get('id')
    try:
        response_data['data'] = MessageQueue.objects.get(pk=id).text
    except Exception as e:
        status = 400
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@csrf_exempt
def test_message(request):
    status = 200
    response_data = {}
    body = request.POST.get('body')
    user = request.user

    try:
        if not user.email:
            raise Exception('Zalogowany użytkownik %s %s nie posiada wprowadzonego do systemu adresu e-mail' % (user.first_name, user.last_name))

        msg = msg_utils.bind_params(text=body, source={}, add_params={}, test=True)
        msg_utils.send_message(to=(user.email,), subject='Test', body=msg['text'])

    except Exception as e:
        status = 500
        response_data = {'errmsg': str(e), 'traceback': traceback.format_exc()}

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)
