import json
import datetime
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404

def calendar(request):
    return render(request, 'schedule/year_calendar/year_calendar.html')