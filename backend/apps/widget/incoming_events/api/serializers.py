import datetime

from rest_framework import serializers

from apps.scheduler.schedule.models import Schedule, ScheduleType
from apps.user.models import User


class InvitedUsersSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    class Meta:
        model = User
        fields = ('id', 'name')


class ScheduleTypeForIncomingEvents(serializers.ModelSerializer):
    class Meta:
        model = ScheduleType
        fields = ('color',)


class IncomingEventsSerializer(serializers.ModelSerializer):
    invited_users = InvitedUsersSerializer(read_only=True, many=True)
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    type = ScheduleTypeForIncomingEvents(read_only=True)

    def _split_date(self, date):
        return {
            'date': datetime.datetime.strftime(date, '%Y-%m-%d'),
            'hour': datetime.datetime.strftime(date, '%H:%M')
        }

    def get_start_date(self, obj):
        return self._split_date(obj.start_date)

    def get_end_date(self, obj):
        return self._split_date(obj.end_date)

    class Meta:
        model = Schedule
        fields = ('invited_users', 'start_date', 'end_date', 'title', 'type')
