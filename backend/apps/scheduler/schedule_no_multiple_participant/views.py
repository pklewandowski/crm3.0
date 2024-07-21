import pprint
import uuid
import sys
import json
import serwersms

import datetime
import json
import traceback
from operator import itemgetter

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import html
from django.utils.translation import gettext as _
from django.views.decorators.csrf import csrf_exempt
from py3ws.auth.decorators.decorators import p3permission_required
from py3ws.utils import utils as py3ws_utils

from apps.address.forms import AddressForm
from apps.address.models import Address
from apps.hierarchy.models import Hierarchy
from apps.meeting_room.models import MeetingRoom
from apps.message.models import MessageTemplate
from apps.message.utils import MessageException
from apps.product_retail.models import ProductRetail, ProductRetailClient
from apps.product_retail.product_retail import ProductRetailMapper
from apps.user.models import User
from apps.user_func.client.models import Client
from apps.user_func.employee.models import Employee
from apps.message import utils as msg_utils, control_renderer
from py3ws.views.generic_view import GenericView

from py3ws.decorators.decorators import require_lock
from utils.email_message import send_message
from . import EVENT_STATUS
from . import utils as schedule_utils
from .forms import ScheduleForm, ScheduleTypeForm, ScheduleNoteForm, ScheduleFilterForm, ScheduleUserFormset
from .models import Schedule, ScheduleUser, ScheduleType, ScheduleNote, TempBanThaiSpaSent, ScheduleCyclical
from .repository import Repository
from .validate import Validate
from . import view_utils


def send_serwerSMS(phone, loc):
    api = serwersms.SerwerSMS('BANTHAISPA', 'Lemon12!@xxx')
    try:
        ph = TempBanThaiSpaSent.objects.get(phone=phone)
        return
    except TempBanThaiSpaSent.DoesNotExist:
        pass

    try:
        params = {
            'test': 'false',
            'details': 'true'
        }
        locale = {'W': '537595690',
                  'Z': '660587558',
                  'M': '692967479'
                  }

        txt = 'Hoho! Sw. Mikolaj zawital do Ban Thai Spa ze Swiateczna Promocja!Voucher prezentowy 8h masazy w cenie 620PLN a 12h 900PLN.Wilanow/Mokotow/Zoliborz Tel %s' % locale[loc]

        response = api.message.send_sms(phone, txt, '2waySMS', params)
        # response = api.message.send_sms('884908084', txt, '', params)

        result = json.loads(response)

        if 'items' not in result:
            raise Exception('Empty items')

    except Exception:
        pass


def index(request):
    return HttpResponse(_("Zarządzanie harmonogramem."))


def _get_forms_valid(forms, form_errors):
    valid = True

    for form in forms:
        if not form.is_valid():
            valid = False
            form_errors[form.__class__.__name__] = form.errors

    return valid


def _set_schedule_location(schedule, form):
    cl = None
    if not schedule.meeting_room:
        if any(form.cleaned_data.values()):
            address = form.save()
            schedule.custom_location_address = address
    else:
        cl = schedule.custom_location_address
        schedule.custom_location_address = None
    return cl


def _set_schedule_invited_users(invited_users):
    iu = []

    for i in list(invited_users):
        iu.append(ScheduleUser(  # schedule=schedule,
            user=User.objects.get(pk=int(i[0])),
            confirmed=i[1],
            participant_type=i[2],
            exclusive_participant_mode=i[3]
        )
        )
    return iu


def _set_schedule_message(schedule, user, form):
    message = form.save(commit=False)
    if message.text:
        message.schedule = schedule
        message.created_date = datetime.datetime.now()
        message.user = user
        message.save()


# TODO: DRUT!!!!!!!! ZAMIENIĆ DOCELOWO NA FORMSET!!!!!!!!!!!!!
def _get_invited_users(request, form, schedule, mode):
    user_list = []
    if mode == 'basic':
        user_list.append([form.cleaned_data.get('client_'), True, 'P', True])
        user_list.append([form.cleaned_data.get('employee_'), True, 'P', True])
    else:
        if schedule.type.single_person:
            user_list.append([form.cleaned_data.get('single_person_'), True, 'P', True])
        else:
            _list = request.POST.getlist('users-invited_users')
            user_list = list(zip(_list,
                                 list(map(lambda x: True if x == '1' else False, request.POST.getlist('users-invited_users_confirmed'))),
                                 request.POST.getlist('users-invited_users_participant_type'),
                                 list(map(lambda x: True if x == '1' else False, request.POST.getlist('users-invited_users_exclusive_participant_mode')))
                                 )
                             )
    return user_list


def _message(template_code: str, params: dict, recipients: list, source: dict):
    if not recipients:
        raise Exception('[_message]: Brak podanych adresatów wiadomości')
    if not template_code:
        raise Exception('[_message]: Brak parametru szablonu wiadomości')
    try:
        template = MessageTemplate.objects.get(code=template_code)
        msg_utils.register_message(
            template,
            source=source,  # {'user': user},
            add_params=params,
            recipients=recipients
        )

    except MessageTemplate.DoesNotExist:
        raise Exception('Próba wyboru szablonu wiadomości zakończona niepowodzeniem')
    except Exception as ex:
        raise Exception(ex)


class ScheduleView(GenericView):
    form = None
    address_form = None
    note_form = None
    product_retail_client_formset = None

    def __init__(self, *args, **kwargs):
        self._app_name = 'schedule'

        super(ScheduleView, self).__init__()
        self.form = ScheduleForm(data=None, prefix='schedule', instance=None)


class Add(ScheduleView):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    def dispatch(self, request, *args, **kwargs):
        self.form.data = request.POST or None
        context = {'form': self.form}
        return render(request, 'schedule/add.html', context=context)


def _send_message(request, schedule, invited_user, id):
    def _get_token(invited_user):
        if invited_user.token_valid and invited_user.token:
            return invited_user.token
        else:
            return uuid.uuid4().hex

    params = {
        'SCHEDULE_TITLE': schedule.title,
        'HOST_USER': '%s %s' % (request.user.first_name, request.user.last_name),
        'SCHEDULE_START_DATE': datetime.datetime.strftime(schedule.start_date, '%Y-%m-%d %H:%M'),
        'SCHEDULE_END_DATE': datetime.datetime.strftime(schedule.end_date, '%Y-%m-%d %H:%M'),
        'CALENDAR': ''  # control_renderer.render_calendar_formant(start=schedule.start_date, end=schedule.end_date)
    }
    try:
        validate_email(invited_user.user.email)
        if schedule.type.participant_confirmation:
            invited_user.token = _get_token(invited_user)
            invited_user.token_valid = True
            invited_user.save()
            params['EVENT_CONFIRMATION_LINK'] = request.build_absolute_uri(reverse('schedule.participant_confirm_from_link', args=(schedule.pk, invited_user.token)))

        if id:
            template_code = 'CHG_EVT_CONFIRM' if not invited_user.confirmed else 'CHG_EVT'
        else:
            template_code = 'NEW_EVT_CONFIRM' if not invited_user.confirmed else 'NEW_EVT'

        _message(template_code=template_code,
                 params=params,
                 recipients=[invited_user.user.email],
                 source={'user': invited_user.user})

    except ValidationError:
        pass
    except Exception as ex:
        raise Exception(traceback.format_exc())


def add(request):
    response_data = {}
    response_status = 200
    form_errors = {}
    address = None
    schedule_instance = None
    product_retail_queryset = ProductRetail.objects.none()

    try:
        if request.method != 'POST':
            raise Exception('Akcja [schedule.add] wymaga metody POST')

        with transaction.atomic():
            require_lock(Schedule, 'EXCLUSIVE')
            require_lock(ScheduleUser, 'EXCLUSIVE')
            id = request.POST.get('id')
            if id:
                schedule_instance = Repository.get(id)
                # product_retail_queryset = ProductRetail.objects.filter(schedule=schedule_instance)

            Validate.validate_permissions(user=request.user, schedule=schedule_instance)

            form = ScheduleForm(request.POST, prefix='schedule', instance=schedule_instance)
            schedule_user_formset = ScheduleUserFormset(
                data=request.POST,
                queryset=ScheduleUser.objects.filter(schedule=schedule_instance) if schedule_instance else ScheduleUser.objects.none(),
                prefix='schedule-user', form_kwargs={}
            )

            address_form = AddressForm(request.POST, prefix='address', instance=address)
            note_form = ScheduleNoteForm(request.POST, prefix='message')
            # product_retail_client_formset = ProductRetailMapper.get_product_client_formset(data=request.POST, queryset=product_retail_queryset)

            if not _get_forms_valid([form, address_form, note_form, ], form_errors):  # product_retail_client_formset
                response_data['form_errors'] = form_errors
                response_data['form_status'] = 'ERROR'
                raise Exception('Wystąpiły błędy')

            form_mode = form.cleaned_data.get('mode')

            # if form.has_changed():
            schedule = form.save(commit=False)

            if not schedule.type.whole_day_event:
                if datetime.datetime.strftime(schedule.end_date, "%Y-%m-%d %H:%M") == datetime.datetime.strftime(schedule.end_date.date(), "%Y-%m-%d %H:%M"):
                    schedule.end_date = schedule.end_date - datetime.timedelta(seconds=60)
            # else:
            #     schedule.start_date
            #     schedule.end_date

            if form_mode == 'basic':
                host_user = form.cleaned_data.get('employee_')
            else:
                host_user = form.cleaned_data.get('host_user_')

            schedule.host_user = User.objects.get(pk=host_user)

            Validate.validate_permissions(user=request.user, schedule=schedule, initial=False)

            exception_list = []
            invited_users = _get_invited_users(request=request, form=form, schedule=schedule, mode=form_mode)
            invited_users = _set_schedule_invited_users(invited_users=invited_users)

            validate = Validate(schedule=schedule)

            if not validate.validate_schedule(exception_list=exception_list):
                raise Exception(';'.join(exception_list))

            validate.validate_invited_users(invited_users)

            if not id:
                schedule.created_by = request.user
                schedule.status = 'NW'

            custom_location = _set_schedule_location(schedule=schedule, form=address_form)

            # if not schedule.type.host_user_confirmation or request.user.pk == schedule.host_user:
            schedule.host_user_confirmed = True

            # if not schedule.type.superior_confirmation:
            schedule.superior_confirmed = True

            schedule.participant_confirmed = all([i.confirmed for i in invited_users])

            schedule.save()
            schedule.invited_users.clear()
            for i in invited_users:
                i.schedule = schedule
                i.save()

            if note_form.has_changed():
                schedule_message = note_form.save(commit=False)
                schedule_message.schedule = schedule
                schedule_message.user = request.user
                schedule_message.save()

            if custom_location:
                custom_location.delete()
                Address.objects.get(pk=custom_location.pk).delete()

            if form_mode == 'basic':
                pass

                # TODO: obsłużyć to również dla advanced mode

                # frm = product_retail_client_formset.save(commit=False)
                # for i in frm:
                #     i.client = Client.objects.get(pk=form.cleaned_data.get('client_'))
                #     i.schedule = schedule
                #     i.created_by = request.user
                #     # TODO: zrobić obsługę typu płatności w formualrzu. Tu  chodzi o to, czy z prepaida, czy gotówka ['PRE', 'CASH']
                #     # Jeśli gotówka, to zdjąć z prepaida odpowiednią ilość kasy. Jak przekroczy wartość na prepaidzie, to wyjątek.
                #     # ten wyjątek obsłużyć w is_valid()
                #     i.payment_type = 'CASH'
                #     i.save()

            if schedule.type.send_message:
                for i in invited_users:
                    _send_message(request=request, schedule=schedule, invited_user=i, id=id)

            if form.cleaned_data.get('is_cyclical') and False:  # TODO: dokończyć
                repeat_period = form.cleaned_data.get('repeat_period')
                days_of_month = form.cleaned_data.get('days_of_month').split('|')
                days_of_week = form.cleaned_data.get('days_of_week').split('|')

                sc = view_utils.save_schedule_cyclical(schedule=schedule,
                                                       repeat_period=repeat_period,
                                                       days_of_week=days_of_week,
                                                       days_of_month=days_of_month
                                                       )
            response_data['id'] = schedule.pk
            response_data['form_status'] = 'OK'

    except Exception as ex:
        response_data['errmsg'] = "%s %s %s" % (str(ex), '\n', traceback.format_exc() or '')
        response_status = 400

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=response_status)


@transaction.atomic()
def delete(request):
    try:
        response_data = {}

        if not (request.user.has_perm('schedule.delete:all') or request.user.has_perm('schedule.delete:own')):
            raise Exception('Użytkownik nie posiada uprawnień do usuwania zdarzeń')

        if request.method == 'POST':
            id = request.POST.get('id')

            schedule = Schedule.objects.get(pk=id)
            schedule.status = 'DL'
            schedule.save()

            params = {
                'SCHEDULE_TITLE': schedule.title,
                'HOST_USER': '%s %s' % (request.user.first_name, request.user.last_name),
                'SCHEDULE_START_DATE': datetime.datetime.strftime(schedule.start_date, '%Y-%m-%d %H:%M'),
                'SCHEDULE_END_DATE': datetime.datetime.strftime(schedule.end_date, '%Y-%m-%d %H:%M'),
            }
            try:
                for invited_user in ScheduleUser.objects.filter(schedule=schedule):
                    validate_email(invited_user.user.email)

                    _message(template_code='DEL_EVT',
                             params=params,
                             recipients=[invited_user.user.email],
                             source={'user': invited_user.user})

            except Exception as ex:
                # todo: handle it
                pass

        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


@transaction.atomic()
@require_lock(Schedule, 'EXCLUSIVE')
@require_lock(ScheduleUser, 'EXCLUSIVE')
def move(request):
    id_event = html.mark_safe(request.POST.get('id'))
    start = html.mark_safe(request.POST.get('start'))
    end = html.mark_safe(request.POST.get('end'))

    response_data = {}

    try:
        schedule = Schedule.objects.get(pk=id_event)
        if schedule.type.whole_day_event:

            schedule.start_date = datetime.datetime.strptime(start[0:10], '%Y-%m-%d')
            schedule.end_date = datetime.datetime.strptime(end[0:10], '%Y-%m-%d')
        else:
            schedule.start_date = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
            schedule.end_date = datetime.datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')

        exception_list = []
        invited_users = ScheduleUser.objects.filter(schedule=schedule)

        validate = Validate(schedule=schedule)
        if not validate.validate_schedule(exception_list):
            raise Exception(';'.join(exception_list))

        validate.validate_invited_users(invited_users)

        if schedule.type.participant_confirmation:
            schedule.participant_confirmed = False

            u = ScheduleUser.objects.filter(schedule=schedule)
            for i in u:
                i.confirmed = False
                i.save()

        schedule.save()

        for i in ScheduleUser.objects.filter(schedule=schedule):
            _send_message(request=request, schedule=schedule, invited_user=i, id=schedule.id)

        return HttpResponse(json.dumps(response_data), content_type="application/json")

    except Exception as e:
        response_data['errmsg'] = str(e)
        return HttpResponse(json.dumps(response_data), content_type="application/json", status=400)


@transaction.atomic()
def status(request):
    response_data = {}

    try:
        if request.method == 'POST':
            schedule = Schedule.objects.get(pk=request.POST.get('id_schedule'))
            status = request.POST.get('status')
            note = request.POST.get('note')

            if status == 'DL':
                if not (request.user.has_perm('schedule.delete:all') or request.user.has_perm('schedule.delete:own')):
                    raise Exception('Użytkownik nie posiada uprawnień do usuwania zdarzeń')

                if not request.user.has_perm('schedule.delete:all') and (schedule.host_user.pk != request.user.pk or schedule.created_by.pk != request.user.pk):
                    raise Exception('Użytkownik nie posiada uprawnień do usuwania zdarzeń innych użytkowników')

            elif status == 'AN':
                if not (request.user.has_perm('schedule.cancel:all') or request.user.has_perm('schedule.cancel:own')):
                    raise Exception('Użytkownik nie posiada uprawnień do anulowania zdarzeń')

                if not request.user.has_perm('schedule.cancel:all') and (schedule.host_user.pk != request.user.pk or schedule.created_by.pk != request.user.pk):
                    raise Exception('Użytkownik nie posiada uprawnień do anulowania zdarzeń innych użytkowników')

            elif status == 'CL':
                if not (request.user.has_perm('schedule.close:all') or request.user.has_perm('schedule.close:own')):
                    raise Exception('Użytkownik nie posiada uprawnień do zamykania zdarzeń')

                if not request.user.has_perm('schedule.close:all') and (schedule.host_user.pk != request.user.pk or schedule.created_by.pk != request.user.pk):
                    raise Exception('Użytkownik nie posiada uprawnień do zamykania zdarzeń innych użytkowników')

            schedule.status = status
            schedule.save()

            if note:
                ScheduleNote.objects.create(
                    schedule=schedule,
                    user=request.user,
                    text=note
                )

            l = [i.email for i in schedule.invited_users.all()]

            user = request.user
            message_text = "Witamy!\n\nInformujemy, że użytkownik " + user.first_name + ' ' + user.last_name \
                           + ' zmienił status zdarzenia "' + schedule.title + '". Termin: ' \
                           + str(schedule.start_date) + ' - ' + str(schedule.end_date) + '. Obecny status zdarzenia: ' + EVENT_STATUS[status]

            if l:
                send_message(to=l, cc=[user.email], subject="Zmiana statusu zdarzenia w kalendarzu", body=message_text)

            response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def _confirm_schedule_participants(schedule):
    confirmed = True
    for i in ScheduleUser.objects.filter(schedule=schedule):
        if not i.confirmed:
            confirmed = False
            break
    schedule.participant_confirmed = confirmed
    schedule.save()


@transaction.atomic()
def participant_confirm(request):
    response_data = {}

    try:
        if not request.method == 'POST':
            raise Exception('Not POST')

        schedule = Schedule.objects.get(pk=request.POST.get('id_schedule'))
        user = User.objects.get(pk=request.POST.get('id_user'))

        su = ScheduleUser.objects.get(schedule=schedule, user=user)
        su.confirmed = True
        su.save()

        _confirm_schedule_participants(schedule=schedule)

        recipients = []
        for i in schedule.invited_users.all():
            try:
                validate_email(i.email)
                recipients.append(i.email)
            except ValidationError as e:
                # TODO: DOCELOWO ZALOGOWAĆ WYJĄTEK DO ERROR_LOG!!!
                pass

        if recipients:
            try:
                msg_utils.register_message(
                    template=MessageTemplate.objects.get(code='EVT_PART_CONFIRM'),
                    source={'user': user},
                    add_params={
                        'EVENT_PARTICIPANT': user.first_name + ' ' + user.last_name,
                        'SCHEDULE_TITLE': schedule.title,
                        'SCHEDULE_START_DATE': datetime.datetime.strftime(schedule.start_date, '%Y-%m-%d %H:%M'),
                        'SCHEDULE_END_DATE': datetime.datetime.strftime(schedule.end_date, '%Y-%m-%d %H:%M')
                    },
                    recipients=recipients
                )

                response_data['status'] = 'OK'

            except MessageTemplate.DoesNotExist:
                response_data['status'] = 'ERROR'
                response_data['errmsg'] = 'Potwierdzenie uczestnictwa zakończone pomyślnie, jednakże próba wysłania wiadomości o potwierdzeniu zakończona niepowodzeniem: BRAK SZABLONU WIADOMOŚCI'
                # TODO: DOCELOWO ZALOGOWAĆ WYJĄTEK DO ERROR_LOG!!!
                pass
            except MessageException as e:
                response_data['status'] = 'ERROR'
                response_data['errmsg'] = str(e)
                # TODO: DOCELOWO ZALOGOWAĆ WYJĄTEK DO ERROR_LOG!!!
            except Exception as e:
                raise Exception(e)

        else:
            response_data['status'] = 'OK'
            response_data['warning'] = 'Nie można wysłać wiadomości do uczestników zdarzednia z powodu braku poprawnych adresów e-mail'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


class TokenNotValidException(Exception):
    pass


@transaction.atomic()
def participant_confirm_from_link(request, id, token):
    schedule = Schedule.objects.get(pk=id)
    try:
        su = ScheduleUser.objects.get(schedule=schedule, token=token)
        if not su.token_valid:
            raise TokenNotValidException('Podany token jest nieważny')

        su.confirmed = True
        su.token = None
        su.token_valid = False
        su.save()

        _confirm_schedule_participants(schedule=schedule)
        return render(request, 'schedule/participant_confirmed.html', context={'schedule': schedule})

    except (ScheduleUser.DoesNotExist, TokenNotValidException):
        return render(request, 'schedule/token_not_valid.html', context={'errmsg': "Podany token jest nieważny"})
    except Exception as ex:
        return render(request, 'schedule/token_not_valid.html', context={'errmsg': str(ex)})


@transaction.atomic()
def participant_reject(request):
    response_data = {}

    try:
        if request.method == 'POST':
            schedule = Schedule.objects.get(pk=request.POST.get('id_schedule'))
            user = User.objects.get(pk=request.POST.get('id_user'))

            su = ScheduleUser.objects.get(schedule=schedule, user=user)
            su.confirmed = False
            su.save()
            schedule.participant_confirmed = False
            schedule.save()

            l = [i.email for i in schedule.invited_users.all()]

            message_text = "Witamy!\n\nInformujemy, że użytkownik " + user.first_name + ' ' + user.last_name \
                           + ' odrzucił zdarzenie "' + schedule.title + '". Termin: ' \
                           + str(schedule.start_date) + ' - ' + str(schedule.end_date) + '.'

            if l:
                send_message(to=l, subject="Odrzucenie zdarzenia w kalendarzu", body=message_text)

            response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def stats(request):
    q = """
        SELECT tt.cnt, s.id, s.title, us.first_name, us.last_name, tp.name AS type_name, hs.history_date FROM (
            SELECT id, COUNT(1) cnt FROM(
                SELECT
                    id,
                    id_host_user,
                    start_date AS start,
                    lag(start_date) OVER (PARTITION BY id ORDER BY history_date DESC) AS prev_start,
                    end_date AS end,
                    lag(end_date) OVER (PARTITION BY id ORDER BY history_date DESC) AS prev_end
                FROM h_schedule
                )t
                WHERE (t.start <> t.prev_start OR t.end <> t.prev_end)
                GROUP BY id
            )tt, schedule s, "user" us, schedule_type AS tp, h_schedule hs
            WHERE s.id=tt.id AND us.id=s.id_host_user AND tp.id = s.id_type AND hs.id=s.id AND hs.history_type='+'
            ORDER BY cnt DESC, id
        """
    top_ten_move = Schedule.objects.raw(q)

    context = {'top_ten_move': top_ten_move}
    return render(request, 'schedule/stats/stats.html', context)


@p3permission_required('schedule.list:own', 'schedule.list:all')
def calendar(request, id_user=None):
    try:
        form = ScheduleForm(request.POST or None, prefix='schedule')
        filter_form = ScheduleFilterForm(prefix='filter')
        custom_address_form = AddressForm(request.POST or None, prefix='address')
        note_form = ScheduleNoteForm(request.POST or None, prefix='message')
        schedule_type = ScheduleType.objects.all().order_by("sq")

        product_retail_client_formset = ProductRetailMapper.get_product_client_formset(request.POST or None)

        if request.user.has_perm('schedule.list:all'):
            if id_user:
                calendar_user = get_object_or_404(User, pk=id_user)
            else:
                calendar_user = None
        else:
            calendar_user = request.user

        schedule_default_event = []

        for i in schedule_type:
            if i.is_default_event:
                schedule_default_event.append({"id": i.pk, "title": i.default_title})
                break

        context = {'calendar_user': calendar_user,
                   'current_user': request.user,
                   'is_headquarter': Hierarchy.is_headquarter(),
                   'user_headquarters': html.mark_safe(request.session['user_headquarters']),
                   'form': form,
                   'filter_form': filter_form,
                   'product_retail_client_formset': product_retail_client_formset,
                   'note_form': note_form,
                   'custom_address_form': custom_address_form,
                   'schedule_type': schedule_type,
                   'working_hours': {k: datetime.time.strftime(v, '%H:%M:%S') for k, v in settings.SCHEDULE_WORKING_HOURS.items()},
                   'schedule_default_event': json.dumps(schedule_default_event),
                   }

        return render(request, 'schedule/calendar.html', context)

    except Exception as e:
        messages.add_message(request, messages.ERROR, e)
        return render(request, 'schedule/calendar.html')


def _get_compact_address(adr):
    street = adr.street or ''
    street_no = adr.street_no or ''
    apartment_no = adr.apartment_no or ''
    post_code = adr.post_code or ''
    city = adr.city or ''

    return '%s %s %s%s %s' % (street, street_no, apartment_no, (", " + post_code), city)


@csrf_exempt
def calendar_get_events(request):
    response_data = {}
    schedule_list = []
    is_headquarter = Hierarchy.is_headquarter()
    debug = 0

    status = 200

    try:
        if not (request.user.has_perm('schedule.list:all') or request.user.has_perm('schedule.list:own')):
            raise Exception('Użytkownik nie posiada uprawnień do przeglądania zgłoszeń')

        id_user = request.POST.get('id_user', None)

        if not request.user.has_perm('schedule.list:all') and id_user and int(id_user) != request.user.pk:
            raise Exception('Użytkownik nie posiada uprawnień do zdarzeń innych użytkowników')

        calendar_mode = html.mark_safe(request.POST.get('calendar_mode'))
        start = html.mark_safe(request.POST.get('start'))
        end = html.mark_safe(request.POST.get('end'))
        filter_str = html.mark_safe(request.POST.get('filter') or '')

        filter = json.loads(filter_str) if filter_str else None
        filter_phrase = filter['text'] if filter else None
        filter_types = filter['scheduleTypes'] if filter else None
        filter_statuses = filter['scheduleStatuses'] if filter else None

        headquarter = request.POST.get('headquarter', None)

        debug = '0.1'
        user = User.objects.get(pk=id_user) if id_user else None
        debug = '0.2'
        host_user_pk = user.pk if id_user else None

        debug = '1'

        q = Q()
        q = q & Q(start_date__gte=start, start_date__lte=end)
        q = q & ~Q(status='DL')

        if not calendar_mode == 'room':

            if not request.user.has_perm('schedule.list:all'):
                q = q & Q(host_user=request.user) | Q(created_by=request.user) | Q(invited_users__in=(request.user,))

            elif user is not None:
                q = q & (Q(host_user=user) | Q(created_by=user) | Q(invited_users=user))

        else:
            q = q & Q(meeting_room__isnull=False)

        if filter_phrase:
            q = q & (Q(title__icontains=filter_phrase) |
                     Q(description__icontains=filter_phrase) |
                     Q(meeting_room__name__icontains=filter_phrase) |
                     Q(host_user__first_name__icontains=filter_phrase) |
                     Q(host_user__last_name__icontains=filter_phrase) |
                     Q(host_user__company_name__icontains=filter_phrase) |
                     Q(host_user__personal_id__icontains=filter_phrase) |
                     Q(host_user__nip__icontains=filter_phrase) |
                     Q(host_user__krs__icontains=filter_phrase) |
                     Q(invited_users__first_name__icontains=filter_phrase) |
                     Q(invited_users__last_name__icontains=filter_phrase) |
                     Q(invited_users__company_name__icontains=filter_phrase) |
                     Q(invited_users__personal_id__icontains=filter_phrase) |
                     Q(invited_users__nip__icontains=filter_phrase) |
                     Q(invited_users__krs__icontains=filter_phrase)
                     )
        if filter_types:
            q &= Q(type__in=filter_types)
        if filter_statuses:
            q &= Q(status__in=filter_statuses)

        debug = 1.5

        if is_headquarter:
            if headquarter:
                q = q & Q(meeting_room__headquarter=headquarter)
            else:
                q = q & Q(meeting_room__headquarter__in=[i['id'] for i in request.session['user_headquarters']])

        schedules = Schedule.objects.filter(q).distinct().select_related('type',
                                                                         'host_user',
                                                                         'created_by',
                                                                         'meeting_room',
                                                                         'custom_location_address'
                                                                         ).prefetch_related('invited_users')

        for i in schedules:
            if calendar_mode == 'room':
                color = i.meeting_room.color
                title = i.meeting_room.name
            else:
                color = i.type.color
                title = i.title

            editable = i.status == 'NW' and (request.user.has_perm('schedule.change:all') or
                                             (request.user.has_perm('schedule.change:own') and (
                                                 (i.type.host_user_editable and i.host_user.pk == host_user_pk) or i.created_by.pk == request.user.pk)
                                              )
                                             )

            # TODO: SPOWALNIA O 0.5 sek. wymyślić inny sposób na sprawdzenie, czy uzytkownik może widzieć zdarzenie
            # is_in_users = False
            # for j in i.invited_users.all().prefetch_related('user'):
            #     if j.pk == request.user.pk:
            #         is_in_users = True
            #         break
            # viewable = editable or is_in_users \
            #            or (request.user.has_perm('schedule.view:all')
            #                or (request.user.has_perm('schedule.view:own') and
            #                    (i.host_user.pk == request.user.pk or i.created_by.pk == request.user.pk))
            #                )
            viewable = True
            details_viewable = True

            # custom_address = ''
            # if i.custom_location_address:
            #     custom_address = _get_compact_address(i.custom_location_address)

            schedule_list.append([
                i.pk,
                i.cyclical,
                False,  # is_cyclical
                # True, # allDay
                title or '',
                i.start_date.strftime('%G-%m-%dT%H:%M:00'),
                i.end_date.strftime('%G-%m-%dT%H:%M:00'),
                color,
                viewable,
                editable,
                details_viewable,
                [
                    i.type.single_person,
                    i.type.whole_day_event,
                    i.participant_confirmed and i.superior_confirmed and i.host_user_confirmed,
                    [
                        i.host_user.pk,
                        i.host_user.first_name or '',
                        i.host_user.last_name or '',
                        i.host_user.email or '',
                        i.host_user.phone_one or '',
                    ],
                    '[' + i.meeting_room.name + ']' if i.meeting_room else i.custom_location_address.street if i.custom_location_address else '',
                    True,  # resizable not i.type.whole_day_event,
                    i.status,
                    [
                        [
                            n.pk,
                            n.first_name or '',
                            n.last_name or '',
                            n.phone_one or '',
                            n.phone_two or '',
                            n.email,
                            reverse('user.edit', args=[n.pk]),
                            [
                                [
                                    j.product.name,
                                    str(j.quantity),
                                    str(j.unit_price),
                                    # str(j.total_cost),
                                    j.payment_type,
                                    # j.creation_date,
                                    # j.created_by
                                ]
                                for j in ProductRetailClient.objects.filter(schedule=i, client=n.pk)
                            ]
                        ]
                        for n in i.invited_users.all()
                    ]
                ],
            ])

        debug = '3'

        response_data['events'] = schedule_list
        response_data['status'] = 'OK'

    except Exception as e:
        status = 400
        response_data['errmsg'] = str(e)
        response_data['debug'] = debug

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


def calendar_get_event_data(request):
    id = request.POST.get('id')
    schedule = Schedule.objects.get(pk=id)

    event_type_serial = serializers.serialize("json", [schedule.type])
    schedule_serial = serializers.serialize("json", [schedule])

    if schedule.custom_location_address:
        custom_address = serializers.serialize("json", [schedule.custom_location_address])
    else:
        custom_address = None

    if schedule.meeting_room:
        meeting_room_serial = serializers.serialize("json", [schedule.meeting_room])
    else:
        meeting_room_serial = None

    users_serial = None

    l = []
    u = ScheduleUser.objects.filter(schedule=id)
    for i in u:
        l.append(
            {'id': i.user.pk,
             'first_name': i.user.first_name,
             'last_name': i.user.last_name,
             'email': i.user.email,
             'phone_one': i.user.phone_one,
             'phone_two': i.user.phone_two,
             'confirmed': i.confirmed,
             'participant_type': i.participant_type,
             'exclusive_participant_mode': i.exclusive_participant_mode
             })
    if len(l):
        users_serial = json.dumps(l)

    return JsonResponse(
        {'status': 'OK',
         'schedule': schedule_serial,
         'event_type': event_type_serial,
         'users': users_serial,
         'custom_address': custom_address,
         'meeting_room': meeting_room_serial,
         'notes': json.dumps([
             {'created_date': i.created_date.strftime("%Y-%m-%d %H:%M:%S"),
              'user': i.user.first_name + ' ' + i.user.last_name,
              'text': i.text
              } for i in ScheduleNote.objects.filter(schedule=schedule).order_by('-created_date')]),
         'host_user': (schedule.host_user.first_name or '') + ' ' + (schedule.host_user.last_name or ''),
         'created_by': (schedule.created_by.first_name or '') + ' ' + (schedule.created_by.last_name or '')})


def type_list(request):
    schedule_types = ScheduleType.objects.all().order_by('sq')

    context = {'schedule_types': schedule_types}
    return render(request, 'schedule/type/list.html', context)


@transaction.atomic()
@p3permission_required('permissions.type:add', )
def type_add(request, id_type=None):
    if id_type is not None:
        schedule_type = get_object_or_404(ScheduleType, pk=id_type)
    else:
        schedule_type = None

    form = ScheduleTypeForm(request.POST or None, instance=schedule_type, label_suffix=':')
    form.fields['color'].widget.attrs['readonly'] = True

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('schedule.type.list')

    context = {'form': form}
    return render(request, 'schedule/type/add.html', context)


def get_user_list(request):
    users = None
    response_data = {}
    try:

        ids = json.loads(request.POST.get('id'))
        key = request.POST.get('key')
        mode = request.POST.get('mode')
        mode = 'all'

        # q = Q(first_name__icontains=key) | \
        #     Q(last_name__icontains=key) | \
        #     Q(personal_id__icontains=key) | \
        #     Q(phone_one__icontains=key) | \
        #     Q(phone_two__icontains=key) | \
        #     Q(email__icontains=key) | \
        #     Q(personal_id__icontains=key) | \
        #     Q(nip__icontains=key) | \
        #     Q(krs__icontains=key)

        q = Q(last_name__istartswith=key) | \
            Q(personal_id__istartswith=key) | \
            Q(phone_one__istartswith=key) | \
            Q(email__istartswith=key) | \
            Q(personal_id__istartswith=key) | \
            Q(nip__istartswith=key) | \
            Q(krs__istartswith=key)

        if len(key) > 0:
            if mode == 'all':
                users = [i for i in User.objects.filter(q).exclude(id__in=ids)]
            else:
                users = [i.user for i in py3ws_utils.get_class(settings.SCHEDULE_CLIENT_CONTACT_CLASS).objects.filter(user__pk__in=User.objects.filter(q).exclude(id__in=ids))]
        if users:
            response_data['data'] = serializers.serialize("json", users)

        response_data['status'] = 'OK'

    except Exception as e:
        response_data['status'] = 'ERROR'
        response_data['message'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def list_schedule(request, id_user):
    return HttpResponse(_("harmonogram dla usera."))


def _get_minute_delta(start, end):
    if start > end:
        return None
    return (datetime.datetime.combine(datetime.date.today(), end) - datetime.datetime.combine(datetime.date.today(), start)).seconds / 60


def __set_from_date(from_date):
    if from_date:
        dt = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
    else:
        dt = datetime.date.today()
    return dt


def _get_union_range(result):
    rg = []
    if result:
        if len(result) == 1:
            return result
        r = result[0]
        for i in range(1, len(result)):
            if result[i]['start'] > r['end']:
                rg.append(r)
                r = result[i]
            elif result[i]['end'] > r['end']:
                r['end'] = result[i]['end']
        rg.append(r)
    return rg


def _get_range_query(ranges):
    result = []
    user_result = []
    mr_result = []

    q = Q(end_date__gte=ranges.from_date) & ~Q(status__in=['DL', 'AN'])

    if ranges.users:
        users = User.objects.filter(pk__in=ranges.users)
        q &= q & (Q(host_user__in=users) | Q(invited_users__in=users))
        for i in Schedule.objects.filter(q).extra(select={'start': 'start_date', 'end': 'end_date'}).values('start', 'end'):
            user_result.append(i)
    else:
        range_array = []
        # TODO: tutaj wybrać tylko pracowników /doradców / masażystów - w zależności od tego, kto jest do kontaktu z klientem
        users = py3ws_utils.get_class(settings.SCHEDULE_CLIENT_CONTACT_CLASS).objects.all()

        for idx, user in enumerate(users):
            q1 = q & Q(host_user=user.user) | Q(invited_users=user.user)
            range_array.append([i for i in Schedule.objects.filter(q1).extra(select={'start': 'start_date', 'end': 'end_date'}).order_by('start_date').values('start', 'end')])

        user_result = ranges.get_final_ranges(range_array)

    if ranges.meeting_room:
        q &= Q(meeting_room=MeetingRoom.objects.get(pk=ranges.meeting_room))
        for i in Schedule.objects.filter(q).extra(select={'start': 'start_date', 'end': 'end_date'}).values('start', 'end'):
            mr_result.append(i)
    else:
        range_array = []
        meeting_rooms = MeetingRoom.objects.all()

        for idx, meeting_room in enumerate(meeting_rooms):
            q1 = q & Q(meeting_room=meeting_room)
            range_array.append([i for i in Schedule.objects.filter(q1).extra(select={'start': 'start_date', 'end': 'end_date'}).values('start', 'end')])

        mr_result = ranges.get_final_ranges(range_array)

    result = user_result + mr_result
    sort_result = sorted(result, key=itemgetter('start', 'end'))

    return _get_union_range(sort_result)


@csrf_exempt
def get_available_date(request):
    response_data = {'ranges': []}
    status = 200

    try:
        if request.method == 'POST':
            users = request.POST.getlist('user_id[]', None) + request.POST.getlist('employee_id[]', None)
            meeting_room = html.mark_safe(request.POST.get('meeting_room_id', None))
            from_date = __set_from_date(html.mark_safe(request.POST.get('from_date', None)))
            from_hour = html.mark_safe(request.POST.get('from_hour', None))
            to_hour = html.mark_safe(request.POST.get('to_hour', None))
            min_duration = int(html.mark_safe(request.POST.get('min_duration', None))) or settings.SCHEDULE_EVENT_MIN_DURATION

            min_hour = datetime.datetime.strptime(from_hour, '%H:%M').time() if from_hour else settings.SCHEDULE_WORKING_HOURS['start']
            max_hour = datetime.datetime.strptime(to_hour, '%H:%M').time() if to_hour else settings.SCHEDULE_WORKING_HOURS['end']

            ranges = schedule_utils.ScheduleAvailableRanges(from_date=from_date,
                                                            min_hour=min_hour,
                                                            max_hour=max_hour,
                                                            min_duration=min_duration,
                                                            users=users,
                                                            meeting_room=meeting_room)

            response_data['ranges'] = ranges.jsonify_range(ranges.get_available_ranges(_get_range_query(ranges)))

    except Exception as e:
        status = 400
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@csrf_exempt
def get_available_meeting_rooms(request):
    response_data = {}
    status = 200

    start = html.mark_safe(request.POST.get('start', None))
    end = html.mark_safe(request.POST.get('end', None))
    exclude = html.mark_safe(request.POST.get('exclude', None))

    try:
        if not start or not end:
            raise ValueError('Brak daty startu lub/i końca zdarzenia')

        q = Q(meeting_room__isnull=False) & ~Q(status='DL') & \
            (Q(start_date__lte=start, end_date__gt=start) | Q(start_date__lt=end, end_date__gte=end) | Q(start_date__gt=start, end_date__lt=end))
        if exclude:
            q = q & ~Q(pk=int(exclude))
        av_meeting_rooms = MeetingRoom.objects.filter().exclude(id__in=Schedule.objects.filter(q).values('meeting_room__pk'))
        response_data['data'] = [i.pk for i in av_meeting_rooms]

    except Exception as e:
        status = 400
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@login_required()
@csrf_exempt
def get_users_for_meeting_filter(request):
    key = request.POST.get('q')
    response_data = {}
    status = 200

    try:
        result = User.objects.filter(Q(last_name__istartswith=key) | Q(phone_one__startswith=key))
        # if users.count() > 500:
        #     response_data['results'] = []
        # else:
        response_data['results'] = [{'id': i.pk, 'text': (i.first_name + ' ' if i.first_name else '') +
                                                         (i.last_name or '') + ' ' + (i.phone_one or '')} for i in result]
    except Exception as e:
        status = 400
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@login_required()
@csrf_exempt
def get_clients_for_meeting_filter(request):
    key = request.POST.get('q')
    id_employee = request.POST.get('idEmployee')

    response_data = {}
    status = 200

    try:
        if not id_employee:
            employee = None
            #
        else:
            employee = User.objects.get(pk=id_employee)

        if not employee and not request.user.has_perm('schedule.client:add:all'):
            raise Exception('Nie wybrano pracownika!')

        q = Q()
        if employee:
            q = Q(adviser__user=employee) if not request.user.has_perm('schedule.client:add:all') else Q()

        q &= (Q(user__last_name__istartswith=key) | Q(user__phone_one__startswith=key))

        result = Client.objects.filter(q)
        # if users.count() > 500:
        #     response_data['results'] = []
        # else:
        response_data['results'] = [{'id': i.pk, 'text': (i.user.first_name + ' ' if i.user.first_name else '') +
                                                         (i.user.last_name or '') + ' ' + (i.user.phone_one or '')} for i in result]
    except Exception as e:
        status = 400
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


@login_required()
@csrf_exempt
def get_employees_for_meeting_filter(request):
    key = request.POST.get('q')
    response_data = {}
    status = 200

    try:
        result = Employee.objects.filter(Q(user__last_name__istartswith=key) | Q(user__phone_one__startswith=key))
        # if users.count() > 500:
        #     response_data['results'] = []
        # else:
        response_data['results'] = [{'id': i.pk, 'text': (i.user.first_name + ' ' if i.user.first_name else '') +
                                                         (i.user.last_name or '') + ' ' + (i.user.phone_one or '')} for i in result]
    except Exception as e:
        status = 400
        response_data['errmsg'] = str(e)

    return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)
