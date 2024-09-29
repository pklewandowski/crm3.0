from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from .models import Agreement
from .forms import AgreementForm



def index(request):
    return HttpResponse("agreement")


def list(request):
    agreements = Agreement.objects.all()

    context = {'agreements': agreements}
    return render(request, 'agreement/list.html', context)


@transaction.atomic
def add(request):
    form = AgreementForm(request.POST or None, prefix='agreement')

    if request.method == 'POST':
        if form.is_valid():
            agr = form.save()
            return redirect('agreement.edit', id=agr.pk)

    context = {'form': form, 'mode': 'C'}
    return render(request, 'agreement/add.html', context)


@transaction.atomic
def edit(request, id):
    agreement = get_object_or_404(Agreement, id=id)
    form = AgreementForm(request.POST or None, prefix='agreement', instance=agreement)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('agreement.list')

    context = {'agreement': agreement, 'form': form, 'mode': 'E'}
    return render(request, 'agreement/edit.html', context)


