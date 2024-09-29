from django.shortcuts import render


def index(request):
    return render(request, 'schedule_app/index.html', context={})
