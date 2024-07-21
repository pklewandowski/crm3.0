from django.shortcuts import render


def calendar(request):
    return render(request, 'schedule/year_calendar/year_calendar.html')
