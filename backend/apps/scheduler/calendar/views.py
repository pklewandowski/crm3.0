import datetime
import json
from operator import itemgetter

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import html
from django.views.decorators.csrf import csrf_exempt

from apps.address.forms import AddressForm
from apps.hierarchy.models import Hierarchy
from apps.meeting_room.models import MeetingRoom
from apps.product_retail.product_retail import ProductRetailMapper
from apps.scheduler.schedule.forms import ScheduleForm, ScheduleFilterForm, ScheduleMessageForm, ScheduleUserFormset
from apps.scheduler.schedule.models import ScheduleType, Schedule, ScheduleUser, ScheduleMessage
from apps.user.models import User
from apps.user_func.client.models import Client
from apps.user_func.employee.models import Employee
from py3ws.auth.decorators.decorators import p3permission_required
from py3ws.utils import utils as py3ws_utils
from . import utils as schedule_utils


@p3permission_required('schedule.list_schedule', 'schedule.list_all_schedule')
def index(request, id_user=None):
    try:
        form = ScheduleForm(request.POST or None, prefix='schedule')
        filter_form = ScheduleFilterForm(prefix='filter')
        custom_address_form = AddressForm(request.POST or None, prefix='address')
        message_form = ScheduleMessageForm(request.POST or None, prefix='message')
        schedule_type = ScheduleType.objects.all().order_by("sq")

        product_retail_client_formset = ProductRetailMapper.get_product_client_formset(request.POST or None)
        schedule_user_formset = ScheduleUserFormset(
            data=None,
            queryset=ScheduleUser.objects.none(),
            prefix='schedule-user', form_kwargs={}
        )

        if request.user.has_perm('schedule.list_all_schedule'):
            if id_user:
                user = get_object_or_404(User, pk=id_user)
            else:
                user = None
        else:
            user = request.user

        schedule_default_event = []

        for i in schedule_type:
            if i.is_default_event:
                schedule_default_event.append({"id": i.pk, "title": i.default_title})
                break

        context = {'user': user,
                   'is_headquarter': Hierarchy.is_headquarter(),
                   'user_headquarters': html.mark_safe(request.session['user_headquarters']),
                   'current_user': request.user,
                   'form': form,
                   'filter_form': filter_form,
                   'product_retail_client_formset': product_retail_client_formset,
                   'schedule_user_formset': schedule_user_formset,
                   'message_form': message_form,
                   'custom_address_form': custom_address_form,
                   'schedule_type': schedule_type,
                   'working_hours': {k: datetime.time.strftime(v, '%H:%M:%S') for k, v in settings.SCHEDULE_WORKING_HOURS.items()},
                   'schedule_default_event': json.dumps(schedule_default_event),
                   }

        return render(request, 'calendar/calendar.html', context)

    except Exception as e:
        messages.add_message(request, messages.ERROR, e)
        return render(request, 'schedule/calendar.html')


@csrf_exempt
def calendar_get_events(request):
    response_data = {}
    schedule_list = []
    is_headquarter = Hierarchy.is_headquarter()

    status = 200

    try:
        if not (request.user.has_perm('schedule.list_all_schedule') or request.user.has_perm('schedule.list_schedule')):
            raise Exception('Użytkownik nie posiada uprawnień do przeglądania zgłoszeń')

        id_user = request.POST.get('id_user')

        if not request.user.has_perm('schedule.list_all_schedule') and id_user and int(id_user) != request.user.pk:
            raise Exception('Użytkownik nie posiada uprawnień do zdarzeń innych użytkowników')

        calendar_mode = request.POST.get('calendar_mode')
        start = request.POST.get('start')
        end = request.POST.get('end')
        filter_phrase = request.POST.get('filter_phrase')
        headquarter = request.POST.get('headquarter')

        if id_user:
            user = User.objects.get(pk=id_user)
            host_user_pk = user.pk
        else:
            user = None
            host_user_pk = request.user.pk

        debug = '1'

        q = Q()
        q = q & Q(start_date__gte=start, start_date__lte=end)
        q = q & ~Q(status='DL')

        if not calendar_mode == 'room':

            if not request.user.has_perm('schedule.list_all_schedule'):
                q = q & Q(host_user=request.user) | Q(created_by=request.user) | Q(invited_users__in=(request.user,))

            elif user is not None:
                q = q & (Q(host_user=user) | Q(created_by=user))

        else:
            q = q & Q(meeting_room__isnull=False)

        if filter_phrase:
            q = q & (Q(title__icontains=filter_phrase) |
                     Q(description__icontains=filter_phrase) |
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
        # tm = datetime.datetime.now()

        for i in schedules:

            if calendar_mode == 'room':
                color = i.meeting_room.color
                title = i.meeting_room.name
            else:
                color = i.type.color
                title = i.title

            editable = i.status == 'NW' and \
                       (request.user.has_perm('schedule.change_all_schedule') or
                        (request.user.has_perm('schedule.change_schedule') and ((i.type.host_user_editable and i.host_user.pk == host_user_pk) or i.created_by.pk == request.user.pk))
                        )

            # TODO: SPOWALNIA O 0.5 sek. wymyślić inny sposób na sprawdzenie, czy uzytkownik może widzieć zdarzenie
            # is_in_users = False
            # for j in i.invited_users.all().prefetch_related('user'):
            #     if j.pk == request.user.pk:
            #         is_in_users = True
            #         break
            # viewable = editable or is_in_users \
            #            or (request.user.has_perm('schedule.view_all_schedule')
            #                or (request.user.has_perm('schedule.view_schedule') and
            #                    (i.host_user.pk == request.user.pk or i.created_by.pk == request.user.pk))
            #                )
            viewable = True
            details_viewable = True

            # custom_address = ''
            # if i.custom_location_address:
            #     custom_address = _get_compact_address(i.custom_location_address)

            schedule_list.append([
                i.pk,
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
                    not i.type.whole_day_event,
                    i.status,
                    [
                        [
                            n.pk,
                            n.first_name or '',
                            n.last_name or '',
                            n.phone_one or '',
                            n.phone_two or '',
                            n.email,
                            reverse('user.edit', args=[n.pk])
                        ]
                        for n in i.invited_users.all()
                    ]
                ]
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
    if l:
        users_serial = json.dumps(l)

    return JsonResponse(
        {'status': 'OK',
         'schedule': schedule_serial,
         'event_type': event_type_serial,
         'users': users_serial,
         'custom_address': custom_address,
         'meeting_room': meeting_room_serial,
         'messages': json.dumps([
             {'created_date': i.created_date.strftime("%Y-%m-%d %H:%M:%S"),
              'user': i.user.first_name + ' ' + i.user.last_name,
              'text': i.text
              } for i in ScheduleMessage.objects.filter(schedule=schedule).order_by('-created_date')]),
         'host_user': (schedule.host_user.first_name or '') + ' ' + (schedule.host_user.last_name or ''),
         'created_by': (schedule.created_by.first_name or '') + ' ' + (schedule.created_by.last_name or '')})


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
    response_data = {}
    status = 200

    try:
        result = Client.objects.filter(Q(user__last_name__istartswith=key) | Q(user__phone_one__startswith=key))
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
