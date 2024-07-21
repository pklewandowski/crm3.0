from django.conf import settings
import datetime
import pprint


class ScheduleUtils:
    @staticmethod
    def get_working_days():
        return settings.SCHEDULE_WORKING_DAYS

    @staticmethod
    def is_working_day(dt):
        # TODO: dodać do tego obsługę świąt i dni wolnych od pracy
        return dt.isoweekday() in ScheduleUtils.get_working_days()


class ScheduleAvailableRanges(ScheduleUtils):
    def __init__(self, from_date, min_hour, max_hour, min_duration, users, meeting_room):
        self.from_date = from_date
        self.min_hour = min_hour
        self.max_hour = max_hour
        self.min_duration = min_duration
        self.users = users
        self.meeting_room = meeting_room

    def valid_range(self, start, end):
        return (start < end) and self.is_working_day(start) and ((end - start).seconds / 60 >= self.min_duration)

    def append_range(self, ranges, start, end):
        if self.valid_range(start, end):
            ranges.append({'start': start, 'end': end})
            return True
        return False

    def jsonify_range(self, range):
        return [
            {'start': datetime.datetime.strftime(i['start'], '%Y-%m-%dT%H:%M'),
             'end': datetime.datetime.strftime(i['end'], '%Y-%m-%dT%H:%M')} for i in range
        ]

    def get_max_range_date(self, range):
        return max(x['end'] for x in range)

    def __get_common_range(self, r1, r2):
        val = {'x1': r1['start'], 'x2': r1['end'], 'y1': r2['start'], 'y2': r2['end']}
        s = sorted(val, key=val.get)

        if not s[0][:1] == s[1][:1]:
            return {'start': val[s[1]], 'end': val[s[2]]}

        return None

    def get_common_ranges(self, r1, r2):
        # Osługa sytuację gdy jeden range posiada wpisy gdzie start[r1] > max(end[r2]) wtedy dodaje automatycznie ten przedział, czyli wyznaczenie min z endów i jeśli
        # start > min to dodajemy przedział
        # na razie w/w obsługa wyłączona

        if not r1 or not r2:
            return []

        # end_r1 = self.get_max_range_date(r1)
        # end_r2 = self.get_max_range_date(r2)
        #
        # if end_r1 >= end_r2:
        #     max_range, min_range = r1, r2
        # else:
        #     max_range, min_range = r2, r1
        #
        # min_end = min(end_r1, end_r2)

        common_ranges = []
        for i in r1:
            # if i['start'] >= min_end:
            #     self.append_range(common_ranges, i['start'], i['end'])
            #     continue
            for j in r2:
                r = self.__get_common_range(i, j)
                if r:
                    self.append_range(common_ranges, r['start'], r['end'])
        return common_ranges

    def get_final_ranges(self, range_array):
        final_ranges = []
        for idx, i in enumerate(range_array):
            if idx == 0:
                final_ranges = i
                continue
            final_ranges = self.get_common_ranges(final_ranges, i)
        return final_ranges

    def get_available_ranges(self, range_query):
        ranges = []
        start = datetime.datetime.combine(self.from_date, self.min_hour)
        end = datetime.datetime.combine(start.date(), self.max_hour)

        if range_query:

            for i in range_query:
                if not self.is_working_day(i['start']):
                    continue
                if i['end'] < start:
                    continue

                while i['start'] >= end:
                    self.append_range(ranges, start, end)
                    start = datetime.datetime.combine((start + datetime.timedelta(1)).date(), self.min_hour)
                    end = datetime.datetime.combine(start.date(), self.max_hour)

                if i['start'] >= start:
                    self.append_range(ranges, start, i['start'])

                    if i['end'] >= end:
                        start = datetime.datetime.combine((start + datetime.timedelta(1)).date(), self.min_hour)
                        end = datetime.datetime.combine(start.date(), self.max_hour)
                        continue
                start = i['end']  # max(start, i['end'])

            # pewność, że zawsze będzie zamknięty ostatni dzień, oraz, że jeśli range_query zwróci zbiór pusty, to zawsze będzie jeden przedział (min_hour, max_hour)
            # bo range[] oznacza, że przy scalaniu przedziałów (koniunkcji) get_common_ranges zwrócoony zostanie zbiór pusty
            self.append_range(ranges, start, end)

            # dodanie pełnego przedziału (min_hour, max_hour) na następny dzień po ostatnim wystąpieniu eventu - potrzebne, żeby określić faktyczny end przedziałów available,
            # zawsze na następny dzień po końcu query
            while True:
                start = datetime.datetime.combine((start + datetime.timedelta(1)).date(), self.min_hour)
                end = datetime.datetime.combine(start.date(), self.max_hour)
                if self.is_working_day(start):
                    break
            self.append_range(ranges, start, end)

        else:
            while not self.is_working_day(start):
                start = datetime.datetime.combine((start + datetime.timedelta(1)).date(), self.min_hour)
                end = datetime.datetime.combine(start.date(), self.max_hour)
            self.append_range(ranges, start, end)

        return ranges
