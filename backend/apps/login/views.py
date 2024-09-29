import os
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.sessions.models import Session
from django.db.models import Q
from django.shortcuts import render, redirect

from apps.hierarchy.models import Hierarchy
from apps.user.models import User
from .forms import LoginForm


def set_user_headquarters(user):
    user_headquarters = []

    if user.is_superuser:
        user_headquarters = [i for i in Hierarchy.objects.filter(type='HDQ')]
    else:
        for i in user.hierarchy.all():
            node = i.parent
            while node.type != 'ROOT':
                if node.type == 'HDQ':
                    user_headquarters.append(node)
                    break
                node = node.parent
    return user_headquarters


def log_in(request):
    form = LoginForm(data=request.POST or None)
    msg = None
    user = None

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                _user = User.objects.get(Q(username=username) | Q(personal_id=username) | Q(nip=username) | Q(email=username))
                if os.getenv('CRM_DEVELOP_NO_AUTH'):
                    user = _user
                else:
                    user = authenticate(username=_user.username, password=password)
                # Check if user is already logged to another session
                sessions = Session.objects.filter(expire_date__gte=datetime.now())
                # check if user is logged to another session. Useful when want to restrict user amount to client and
                if sessions:
                    pass

            except (User.DoesNotExist, User.MultipleObjectsReturned):
                msg = 'Niepoprawny login lub hasło [1]'

            if user is not None:
                login(request, user)
                request.session['user_headquarters'] = [{'id': i.id, 'name': i.name} for i in set_user_headquarters(user)]
                request.session['company_name'] = settings.COMPANY_NAME
                return redirect('home.index')
            else:
                msg = msg or 'Niepoprawny login lub hasło'

    context = {'form': form, 'msg': msg}

    return render(request, 'login/login.html', context)


def log_out(request):
    logout(request)
    return render(request, 'login/logout.html')
