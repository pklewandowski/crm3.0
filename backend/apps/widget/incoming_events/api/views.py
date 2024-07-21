import datetime

from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.scheduler.schedule.models import Schedule
from apps.widget.incoming_events.api.serializers import IncomingEventsSerializer


class IncomingEvents(APIView):
    @rest_api_wrapper
    def get(self, request):
        user = request.query_params.get('user', None)
        if not user:
            return []

        return IncomingEventsSerializer(Schedule.objects.filter(
            invited_users__in=[request.user], start_date__gte=datetime.datetime.now()
        ).order_by('start_date')[:20], many=True).data
