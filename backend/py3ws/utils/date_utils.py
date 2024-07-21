import datetime

from apps.scheduler.schedule.models import ScheduleTimeOff


class DataSingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DataSingleton(metaclass=DataSingletonMeta):
    off_dates = {}


def set_schedule_work_day(dt: datetime.date):
    # if payment day is not workday, but saturday or sunday, add appropriate day to get monday
    # weekday() returns range <0;6>
    if not dt:
        return
    if dt.year not in DataSingleton().off_dates:
        DataSingleton().off_dates[dt.year] = [i.off_date for i in ScheduleTimeOff.objects.filter(off_date__year=dt.year)]

    days = 7 - dt.weekday()
    if days in (1, 2):
        dt = dt + datetime.timedelta(days=days)

    if dt.year in DataSingleton.off_dates:
        while dt in DataSingleton().off_dates[dt.year]:
            dt = dt + datetime.timedelta(days=1)

    return dt
