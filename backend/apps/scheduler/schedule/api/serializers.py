from rest_framework import serializers

from application.serializers import DynamicFieldsModelSerializer
from apps.scheduler.schedule.models import Schedule, ScheduleType, ScheduleUser, ScheduleCalendar, ScheduleCalendarScheduleTypeM2M
from apps.user.api.serializers import UserSerializer


class ScheduleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleUser
        fields = '__all__'


class ScheduleTypeSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ScheduleType
        fields = '__all__'


class ScheduleCalendarSerializer(serializers.ModelSerializer):
    allowed_event_types = ScheduleTypeSerializer(many=True)

    class Meta:
        model = ScheduleCalendar
        fields = '__all__'


class ScheduleSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    def __init__(self, *args, **kwargs):
        depth = kwargs.pop('depth', None)

        super().__init__(*args, **kwargs)

        if depth:
            self.Meta.depth = 1
        else:
            self.Meta.depth = 0

    class Meta:
        model = Schedule
        fields = '__all__'


class ScheduleSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = '__all__'


class ScheduleSimpleSerializer(serializers.ModelSerializer):
    type = ScheduleTypeSerializer(fields=['name', 'color'])
    participants = serializers.SerializerMethodField()

    def get_participants(self, obj):
        return UserSerializer(instance=obj.invited_users, many=True).data

    class Meta:
        model = Schedule
        fields = ('id', 'start_date', 'end_date', 'title', 'type', 'participants')
