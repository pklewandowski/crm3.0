from apps.scheduler.schedule.models import ScheduleCyclical, ScheduleCyclicalUser, ScheduleUser


def save_schedule_cyclical(schedule, repeat_period, days_of_month=None, days_of_week=None):
    sc = ScheduleCyclical.objects.create(
        type=schedule.type,
        title=schedule.title,
        description=schedule.description,
        start_date=schedule.start_date,
        start_time=schedule.start_date.time(),
        end_time=schedule.end_date.time(),
        days_of_month=days_of_month,
        days_of_week=days_of_week,
        repeat_period=repeat_period,
        status='NW',
        created_by=schedule.created_by,
        host_user=schedule.host_user,
        meeting_room=schedule.meeting_room,
        custom_location_address=schedule.custom_location_address  # TODO: zrobić osobny wpis dla adresu
    )

    for i in ScheduleUser.objects.filter(schedule=schedule):
        ScheduleCyclicalUser.objects.create(schedule=sc,
                                            user=i.user,
                                            participant_type=i.participant_type,
                                            exclusive_participant_mode=i.exclusive_participant_mode
                                            )

    return sc
