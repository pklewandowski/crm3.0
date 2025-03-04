from django.db import transaction
from django.db.models import Q, Exists, OuterRef
from rest_framework import status

from apps.address.api.serializers import AddressSerializer
from apps.scheduler.schedule.models import Schedule, ScheduleType, ScheduleUser
from apps.scheduler.schedule.api.serializers import ScheduleSerializer, ScheduleSimpleSerializer, ScheduleUserSerializer, ScheduleSaveSerializer
from apps.user.models import User

EVENT_MAP = {'start': 'start_date', 'end': 'end_date', 'participants': 'invited_users'}


def get_event(event_id):
    return ScheduleSerializer(Schedule.objects.get(pk=event_id), depth=1).data


def get_events(logged_user, start=None, end=None, user=None, simple=True):
    q = Q()
    excq = (
            Q(is_private=True, logged_user_not_invited=True) &
            ~Q(created_by=logged_user)
            # ~Q(host_user=logged_user)
    )

    if start:
        q &= Q(start_date__gte=start)
    if end:
        q &= Q(end_date__lte=end)
    if user:
        q &= Q(invited_users__in=user)

    query = Schedule.objects.annotate(
        logged_user_not_invited=~Exists(ScheduleUser.objects.filter(schedule=OuterRef('pk'), user=logged_user).values('user'))). \
        filter(q).exclude(excq)

    if simple:
        return ScheduleSimpleSerializer(query, many=True).data

    return ScheduleSerializer(query, many=True).data


def _map_event_keys(event_key):
    if event_key in EVENT_MAP:
        return EVENT_MAP[event_key]
    return event_key


def resize_event(id, start, end):
    event = Schedule.objects.get(pk=id)
    event.start_date = start
    event.end_date = end
    event.save()


def save_event(event, user):
    id_event = event['id'] if 'id' in event and event['id'] else None

    schedule_instance = Schedule.objects.get(pk=event['id']) if id_event else None
    if schedule_instance and schedule_instance.created_by != user:
        raise Exception('Wydarzenie może być edytowane jedynie przez użytkownika, który je utworzył')

    event = {_map_event_keys(k): v for k, v in event.items()}
    event['created_by'] = user.pk
    event['status'] = 'NW'
    if 'host_user' not in event or not event['host_user']:
        event['host_user'] = user.pk

    if event['location']:
        if event['location']['lat'] and event['location']['lng']:
            event['location']['lat'] = event['location']['lat'][:10]
            event['location']['lng'] = event['location']['lng'][:10]
        else:
            del event['location']['lat']
            del event['location']['lng']


        if not event['location']['country']:
            event['location']['country'] = 'Polska'

    schedule = ScheduleSaveSerializer(instance=schedule_instance, data=event)

    schedule_address = AddressSerializer(
        instance=schedule_instance.custom_location_address if schedule_instance else None,
        data=event['location']) if len(event['location']) else None

    address = None

    if event['location']:
        if schedule_address.is_valid():
            address = schedule_address.save()
        else:
            raise Exception(schedule_address.errors)

    with transaction.atomic():
        if schedule.is_valid():
            if not schedule.validated_data.get('title'):
                schedule.validated_data['title'] = schedule.validated_data['type'].name

            schedule.validated_data['custom_location_address'] = address
            schedule_obj = schedule.save()

        else:
            raise Exception(schedule.errors)

        schedule_user_instance = []

        if id_event:
            schedule_user_instance = ScheduleUser.objects.filter(schedule=schedule_obj)

        if 'invited_users' in event and event['invited_users']:
            create = [
                ScheduleUser(
                    schedule=schedule_obj,
                    user=User.objects.get(pk=i)
                ) for i in event['invited_users'] if i not in [j.user.pk for j in schedule_user_instance]
            ]
            ScheduleUser.objects.bulk_create(create)

            delete = [i for i in schedule_user_instance if i.user.pk not in event['invited_users']]
            for i in delete:
                i.delete()


def delete_event(event, user):
    if event.created_by != user:
        raise Exception('Wydarzenie może być usunięte jedynie przez użytkownika, który je utworzył')

    event.delete()


def close_event(event_id):
    s = Schedule.objects.get(pk=event_id)
    s.status = Schedule.SCHEDULE_STATUS_CLOSED
    s.save()
