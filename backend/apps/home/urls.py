from django.urls import re_path as url
from . import views
from .api.widget import views as widget
from apps.widget.current_contacts.api import views as current_contacts
from apps.widget.incoming_events.api import views as incoming_events

urlpatterns = [
    url(r'^$', views.index, name='home.index'),
    # ------------------------ REST ------------------------------
    url(r'^api/number-widget/$', widget.NumberWidget.as_view(), name='home.widget.number_widget'),
    url(r'^api/chart-widget/$', widget.ChartWidgetView.as_view(), name='home.widget.chart_widget_view'),
    url(r'^api/current-contacts/$', current_contacts.CurrentContacts.as_view(), name='home.widget.current_contacts'),
    url(r'^api/incoming-events/$', incoming_events.IncomingEvents.as_view(), name='home.widget.incoming_events'),
    url(r'^api/current-contacts/(?P<p>\d+)/$', current_contacts.CurrentContacts.as_view(), name='home.widget.current_contacts'),
]
