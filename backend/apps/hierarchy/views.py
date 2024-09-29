from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect

from apps.user.models import User
from py3ws.auth.decorators.decorators import p3permission_required
from .forms import HierarchyForm
from .models import Hierarchy, HierarchyGroup


def index(request):
    # roles = Role.objects.order_by('-name')[:5]
    nodes = Hierarchy.objects.all()

    # template = loader.get_template('role/index.html')
    context = {'nodes': nodes}
    # return HttpResponse(template.render(context, request))
    return render(request, 'hierarchy/index.html', context)


@login_required()
@p3permission_required('hierarchy.add_hierarchy')
@p3permission_required('hierarchy.change_hierarchy')
@transaction.atomic()
def list(request):
    user = request.user
    if request.method == 'POST':
        id = request.POST.get("id", None)
        if id:
            role_instance = Hierarchy.objects.get(pk=request.POST.get("id"))
        else:
            role_instance = None

        form = HierarchyForm(request.POST, instance=role_instance, label_suffix=':')

        if form.is_valid():
            hierarchy = form.save()
            hierarchy.hierarchy_groups.clear()
            for i in form.cleaned_data['group']:
                HierarchyGroup.objects.create(hierarchy=hierarchy, group=i)

            # parent = Role.objects.get(id=form.cleaned_data['parent'])
            # Role.objects.add(name=form.cleaned_data['name'], description=form.cleaned_data['description'],
            # parent=parent)

    else:
        form = HierarchyForm(label_suffix=':', prefix='')

    root = Hierarchy.objects.get(type='ROOT')
    # root = Hierarchy.objects.get(pk=79)
    # nodes = Hierarchy.objects.get(level=0, type='ROOT').get_descendants()
    # nodes = root.get_descendants()
    context = {'root': root}

    return render(request, 'hierarchy/list.html', context)


@login_required()
@p3permission_required('hierarchy.list_user')
def user_list(request):
    id = request.POST.get('id')
    users = User.objects.filter(hierarchy=id)
    users_serialized = serializers.serialize('json', users)

    return JsonResponse({"data": users_serialized, "status": 'OK'}, safe=False)


@login_required()
@p3permission_required('hierarchy.delete_hierarchy')
def delete(request):
    if request.method == 'POST':
        node_id = request.POST.get('node_id', '')
        node = Hierarchy.objects.get(id=node_id)
        node.delete()
        return redirect('/hierarchy/list/')
