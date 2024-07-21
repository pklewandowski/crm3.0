from django.db.models import Q

from .models import Schedule


class Repository:
    def __init__(self, request):
        request = request

    @staticmethod
    def get(id):
        return Schedule.objects.get(pk=id)

    def save(self):
        pass

    @staticmethod
    def get_previous_schedules_for_meeting_room(schedule, count):

        q = Q(end_date__lte=schedule.start_date, meeting_room=schedule.meeting_room) & ~Q(status__in=['DL', 'AN'])
        if schedule.pk:
            q = q & ~Q(pk=schedule.pk)

        return Schedule.objects.filter(q).order_by('-end_date')[:count]

    @staticmethod
    def get_next_schedules_for_meeting_room(schedule, count):

        q = Q(start_date__gte=schedule.end_date, meeting_room=schedule.meeting_room) & ~Q(status__in=['DL', 'AN'])
        if schedule.pk:
            q = q & ~Q(pk=schedule.pk)

        return Schedule.objects.filter(q).order_by('start_date')[:count]

    @staticmethod
    def get_schedules_for_range(start, end, exclude_schedule=None, meeting_room=None):
        q = (Q(start_date__lte=start, end_date__gt=start) | Q(start_date__lt=end, end_date__gte=end) | Q(start_date__gt=start, end_date__lt=end))
        if exclude_schedule:
            q = q & ~Q(pk=exclude_schedule.pk)
        if meeting_room:
            q = q & Q(meeting_room=meeting_room)

        return Schedule.objects.filter(q)
