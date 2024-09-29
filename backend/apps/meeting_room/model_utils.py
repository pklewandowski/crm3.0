from apps.scheduler.schedule.models import Schedule
import datetime


class ModelUtils:
    def get_last_events(self, meeting_room, date_to):
        events = Schedule.objects.filter(end_date__lte=date_to, meeting_room=meeting_room).order_by('-end_date')[:meeting_room.max_continuous_events]

