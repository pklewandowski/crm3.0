import datetime
import pprint

from django.db.models import Q

from apps.scheduler.schedule.models import Schedule, ScheduleUser
from apps.user.models import User
from .repository import Repository


class Validate:
    schedule = None

    def __init__(self, schedule: Schedule):
        if not isinstance(schedule, Schedule):
            raise Exception('Obiekt nie należy do klasy Schedule')

        self.schedule = schedule

    @staticmethod
    def validate_permissions(user, schedule=None, initial=True):
        if initial:
            if schedule:
                if not (user.has_perm('schedule.change:all') or user.has_perm('schedule.change:own')):
                    raise Exception('Użytkownik nie ma uprawnień do edycji zdarzenia')

                if not user.has_perm('schedule.change:all') and schedule.host_user.pk != user.pk and schedule.created_by.pk != user.pk:
                    raise Exception('Użytkownik nie ma uprawnień do edycji zdarzeń innych użytkowników')

            else:
                if not (user.has_perm('schedule.add:all') or user.has_perm('schedule.add:own')):
                    raise Exception('Użytkownik nie ma uprawnień do dodawania zdarzenia')
        else:
            if not user.has_perm('schedule.add:all') and schedule.host_user.pk != user.pk:
                raise Exception('Użytkownik nie ma uprawnień do dodawania / edycji zdarzeń innych użytkowników')

    def _validate_start_end_date(self):
        start = self.schedule.start_date
        end = self.schedule.end_date

        date_pattern = '%Y-%m-%dT%H:%M:%S'

        if not start or not end:
            raise ValueError('Brak daty początku / końca zdarzenia')

        if type(start).__name__ == 'str':
            test_start = datetime.datetime.strptime(start, date_pattern)
        elif type(start).__name__ == 'datetime':
            test_start = start
        else:
            raise ValueError('Niepoprany typ daty początku zdarzenia')

        if type(end).__name__ == 'str':
            test_end = datetime.datetime.strptime(end, date_pattern)
        elif type(start).__name__ == 'datetime':
            test_end = end
        else:
            raise ValueError('Niepoprany typ daty końca zdarzenia')

        if test_start >= test_end:
            raise ValueError('Data początku zdarzenia musi być mniejsza od daty końca')

        if not self.schedule.type.whole_day_event and test_end.date() != test_start.date():
            raise ValueError('Typ zdarzenia nie pozwala na zakładanie zdarzeń wielodniowych')

        return True

    def _validate_meeting_room(self, exclude_schedule=None):
        start, end, meeting_room = self.schedule.start_date, self.schedule.end_date, self.schedule.meeting_room

        if not meeting_room:
            return True
        if Repository.get_schedules_for_range(start=start,
                                              end=end,
                                              meeting_room=meeting_room,
                                              exclude_schedule=exclude_schedule
                                              ).exists():
            raise Exception('Wybrana lokalizacja jest w tym terminie zajęta')
        return True

    def _validate_min_break(self):

        if not self.schedule.meeting_room:
            return True

        min_break = self.schedule.meeting_room.min_break
        max_continous_events = self.schedule.meeting_room.max_continous_events

        if not min_break or min_break == 0:
            return True

        if not max_continous_events or max_continous_events == 0:
            return True

        previous_schedules = Repository.get_previous_schedules_for_meeting_room(schedule=self.schedule, count=max_continous_events)
        next_schedules = Repository.get_next_schedules_for_meeting_room(schedule=self.schedule, count=max_continous_events)

        schedules = [i for i in reversed(previous_schedules)] + [self.schedule] + [j for j in next_schedules]

        if len(schedules) < max_continous_events:
            return True

        iterator = iter(schedules)

        i = next(iterator)
        continous_events = 1

        try:
            while i:
                start = i.end_date
                i = next(iterator)
                end = i.start_date

                if abs((end - start).total_seconds() / 60) < min_break:
                    continous_events += 1
                    if continous_events > max_continous_events:
                        raise ValueError('Zdarzenie naruszy warunek minimalnego odstępu %s min. po '
                                         'następujących po sobie zdarzeniach (max. %s zdarzeń ciągłych) w sali %s, '
                                         'zdarzenie: %s'
                                         % (min_break, max_continous_events, self.schedule.meeting_room.name, i.title))
                else:
                    continous_events = 1
        except StopIteration:
            pass

        return True

    def validate_invited_users(self, invited_users):
        for i in invited_users:
            q = Q(user=i.user) & ~Q(schedule__status__in=('AN', 'DL'))
            if not i.exclusive_participant_mode:
                q &= Q(exclusive_participant_mode=True)
            q &= (
                (
                    Q(schedule__start_date__lte=self.schedule.start_date) &
                    Q(schedule__end_date__gt=self.schedule.start_date)
                ) |
                (
                    Q(schedule__start_date__lt=self.schedule.end_date) &
                    Q(schedule__end_date__gte=self.schedule.end_date)
                ) |
                (
                    Q(schedule__start_date__gte=self.schedule.start_date) &
                    Q(schedule__end_date__lte=self.schedule.end_date)
                )
            )

            if self.schedule.pk:
                su = ScheduleUser.objects.filter(q).exclude(schedule=self.schedule)
            else:
                su = ScheduleUser.objects.filter(q)
            if su:
                raise Exception(
                    'Użytkownik %s %s uczestniczy już (na wyłączność) w innym zdarzeniu w tym terminie.'
                    % (i.user.first_name, i.user.last_name)
                )

    def validate_schedule(self, exception_list):
        exclude_schedule = self.schedule if self.schedule.pk else None

        try:
            valid = self._validate_start_end_date()

            # Sprawdzenie, czy istnieje zaplanowane zdarzenie z wybraną lokalizacją (salą) dla danego przedziału czasowego
            valid = valid & self._validate_meeting_room(exclude_schedule=exclude_schedule)

            valid = valid & self._validate_min_break()

            return valid

        except Exception as e:
            exception_list.append(str(e))
            return False
