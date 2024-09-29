import json
import traceback

from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.scheduler.schedule.api.serializers import ScheduleTypeSerializer, ScheduleCalendarSerializer
from apps.scheduler.schedule.api.services import services
from apps.scheduler.schedule.models import Schedule, ScheduleType, ScheduleCalendar
from apps.user.models import User


class ScheduleEvent(APIView):
    def _change_time(self, request):
        id = request.data.get('id')
        start = request.data.get('start')
        end = request.data.get('end')

        services.resize_event(id, start, end)

    def _update(self, request):
        data = json.loads(request.data.get('formData'))
        services.save_event(data, request.user)

    @rest_api_wrapper
    def get(self, request):
        event_id = request.query_params.get('id', None)

        if event_id:
            return services.get_event(event_id)

        else:
            start_date = request.query_params.get('startDate', None)
            end_date = request.query_params.get('endDate', None)
            user = request.query_params.get('idUser', None)

            if user:
                user = User.objects.get(pk=user)

            return services.get_events(request.user, start=start_date, end=end_date, user=user)

    @rest_api_wrapper
    def post(self, request):
        data = json.loads(request.data.get('formData'))
        services.save_event(data, request.user)

    @rest_api_wrapper
    def put(self, request):
        action = request.data.get('action', None)
        if action == 'CHANGE_TIME':
            self._change_time(request)

        else:
            self._update(request)

    @rest_api_wrapper
    def delete(self, request):
        event = Schedule.objects.get(pk=request.data.get('idEvent'))
        services.delete_event(event=event, user=request.user)


class ScheduleStatus(APIView):
    def put(self, request):
        response_status = status.HTTP_200_OK
        response_data = {}
        action_type = request.data.get('actionType', None)

        try:
            if action_type == 'closeEvent':
                event_id = request.data.get('id', None)
                if not event_id:
                    raise AttributeError(f'[{str(self.__class__)}::put]: no event_id provided')
                services.close_event()

        except Exception as ex:
            response_status = status.HTTP_500_INTERNAL_SERVER_ERROR
            response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}

        return Response(data=response_data, status=response_status)


class ScheduleTypeView(APIView):
    @rest_api_wrapper
    def get(self, request):
        return ScheduleTypeSerializer(ScheduleType.objects.filter(whole_day_event=False).order_by('sq', '-is_default_event', 'name'), many=True).data


class ScheduleCalendarTypeView(APIView):
    @rest_api_wrapper
    def get(self, request):
        calendar_id = request.query_params.get('id', None)
        if calendar_id == '__all__':
            return ScheduleCalendarSerializer(ScheduleCalendar.objects.all(), many=True).data
        if not calendar_id:
            q = Q(is_default=True)
        else:
            q = Q(id=calendar_id)

        return ScheduleCalendarSerializer(ScheduleCalendar.objects.get(q)).data
