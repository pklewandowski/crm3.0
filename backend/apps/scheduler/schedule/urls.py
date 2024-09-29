from django.urls import re_path as url

from .api import views as rest
from . import views
from .view import year_calendar_views

urlpatterns = [
    url(r'^$', views.index, name='schedule.index'),
    url(r'^list/$', views.list_schedule, name='schedule.list'),
    url(r'^add/$', views.Add.as_view(), name='schedule.add_basic'),
    url(r'^list/(?P<id_user>\d+)/$', views.list_schedule, name='list'),
    url(r'^stats/$', views.stats, name='schedule.stats'),
    url(r'^type/list/$', views.type_list, name='schedule.type.list'),
    url(r'^type/add/$', views.type_add, name='schedule.type.add'),
    url(r'^type/edit/(?P<id_type>\d+)/$', views.type_add, name='schedule.type.edit'),

    url(r'^schedule-add/$', views.add, name='schedule.add'),
    url(r'^schedule-add/(?P<id_user>\d+)/$', views.add, name='schedule.add'),
    url(r'^schedule-delete/$', views.delete, name='schedule.delete'),
    url(r'^schedule-participant-confirm/$', views.participant_confirm, name='schedule.participant_confirm'),
    url(r'^schedule-participant-confirm-from-link/(?P<id>\d+)/(?P<token>\w+)/$', views.participant_confirm_from_link, name='schedule.participant_confirm_from_link'),
    url(r'^schedule-participant-reject/$', views.participant_reject, name='schedule.participant_reject'),
    url(r'^schedule-status/$', views.status, name='schedule.status'),

    url(r'^get-users-for-meeting-filter/$', views.get_users_for_meeting_filter, name='schedule.get_users_for_meeting_filter'),
    url(r'^get-clients-for-meeting-filter/$', views.get_clients_for_meeting_filter, name='schedule.get_clients_for_meeting_filter'),
    url(r'^get-employees-for-meeting-filter/$', views.get_employees_for_meeting_filter, name='schedule.get_employees_for_meeting_filter'),
    url(r'^get-available-date/$', views.get_available_date, name='schedule.get_available_date'),
    url(r'^get-available-meeting-rooms/$', views.get_available_meeting_rooms, name='schedule.get_available_meeting_room'),

    url(r'^calendar/$', views.calendar, name='schedule.calendar.all'),
    url(r'^calendar/(?P<id_user>\d+)/$', views.calendar, name='schedule.calendar'),
    url(r'^calendar/year/$', year_calendar_views.calendar, name='schedule.year_calendar.calendar'),
    url(r'^calendar/get-user-list/$', views.get_user_list, name='schedule.user_list'),
    url(r'^calendar/get-event-data/$', views.calendar_get_event_data, name='calendar.event_data'),
    url(r'^calendar/get-events/$', views.calendar_get_events, name='calendar.get_events'),
    url(r'^calendar/move-event/$', views.move, name='calendar.move_event'),

    # --------------------------------------- REST --------------------------------------------
    url(r'^api/status/$', rest.ScheduleStatus.as_view(), name='schedule.api.status'),
    url(r'^api/events/$', rest.ScheduleEvent.as_view(), name='schedule.api.events'),
    url(r'^api/types/$', rest.ScheduleTypeView.as_view(), name='schedule.api.types'),
    url(r'^api/calendar-type/$', rest.ScheduleCalendarTypeView.as_view(), name='schedule.api.calendar.type'),
]
