from django.shortcuts import render, redirect
from django.template import RequestContext
import pprint
from django.http import HttpResponseRedirect, JsonResponse
from django.template import loader
from .models import Role
from apps.user.models import User
from .forms import RoleForm
from django.core import serializers


def index(request):
    # roles = Role.objects.order_by('-name')[:5]
    nodes = Role.objects.all()

    # template = loader.get_template('role/index.html')
    context = {'nodes': nodes}
    # return HttpResponse(template.render(context, request))
    return render(request, 'role/index.html', context)


def role_list(request):
    if request.method == 'POST':

        id = request.POST.get("id", None)

        if id:
            role_instance = Role.objects.get(pk=request.POST.get("id"))
        else:
            role_instance = None

        form = RoleForm(request.POST, instance=role_instance, label_suffix=':')

        if form.is_valid():
            role = form.save()

            # parent = Role.objects.get(id=form.cleaned_data['parent'])
            # Role.objects.create(name=form.cleaned_data['name'], description=form.cleaned_data['description'],
            # parent=parent)

    else:
        form = RoleForm(label_suffix=':', prefix='')

    root = Role.objects.get(id=1)
    nodes = Role.objects.get(level=0, id=1).get_descendants()
    context = {'nodes': nodes, 'root': root, 'form': form}

    # return HttpResponse(template.render(context, request))
    return render(request, 'role/list.html', context)


def role_user_list(request):
    id = request.POST.get('id')
    users = User.objects.filter(roles__pk=id)
    users_serialized = serializers.serialize('json', users)

    return JsonResponse({"data": users_serialized, "status": 'OK'}, safe=False)


def role_delete(request):
    if request.method == 'POST':
        node_id = request.POST.get('node_id', '')
        node = Role.objects.get(id=node_id)
        node.delete()
        return redirect('/role/list/')
