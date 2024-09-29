from django.urls import re_path as url
from . import views
from .view import year_calendar_views

urlpatterns = [
    url(r'^$', views.index, name='calendar.index'),
    url(r'^calendar/year/$', year_calendar_views.calendar, name='calendar.year_calendar.calendar'),
    url(r'^calendar/(?P<id_user>\d+)/$', views.index, name='calendar.index'),
    url(r'^get-users-for-meeting-filter/$', views.get_users_for_meeting_filter, name='calendar.get_users_for_meeting_filter'),
    url(r'^get-clients-for-meeting-filter/$', views.get_clients_for_meeting_filter, name='calendar.get_clients_for_meeting_filter'),
    url(r'^get-employees-for-meeting-filter/$', views.get_employees_for_meeting_filter, name='calendar.get_employees_for_meeting_filter'),
    url(r'^get-available-date/$', views.get_available_date, name='calendar.get_available_date'),
    url(r'^calendar/get-event-data/$', views.calendar_get_event_data, name='calendar.event_data'),
    url(r'^calendar/get-events/$', views.calendar_get_events, name='calendar.get_events'),
    # url(r'^add/$', views.schedule_add, name='add'),

]
