import datetime

from django.shortcuts import render
from django.utils import translation

from apps.scheduler.schedule.models import Schedule


def index(request):
    # todo: DRUT!!! move it to the language chooser select handling
    user_language = 'pl'
    translation.activate(user_language)
    # request.session[translation.LANGUAGE_SESSION_KEY] = user_language

    # todo: change to widget
    incoming_events = Schedule.objects.filter(
        invited_users__in=[request.user], start_date__gte=datetime.datetime.now()
    ).order_by('start_date')[:20]

    context = {'incoming_events': incoming_events}

    return render(request, 'home/index.html', context=context)
