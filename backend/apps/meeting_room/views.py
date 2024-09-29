import pprint
import traceback

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponse

from py3ws.auth.decorators.decorators import p3permission_required

from apps.address.forms import AddressForm
from apps.document.models import DocumentType, DocumentAttribute
from apps.document.forms import DocumentAttributeForm
from apps.document import utils as doc_utils
from apps.address.models import Address

from .models import MeetingRoom, MeetingRoomAttribute, MeetingRoomRoomAttribute
from .forms import MeetingRoomForm, MeetingRoomAttributeForm


def index(request):
    return HttpResponse("Zarządzanie salami spotkań.")


def meeting_room_list(request):
    meeting_rooms = MeetingRoom.objects.all()
    context = {'meeting_rooms': meeting_rooms}
    return render(request, 'meeting_room/list.html', context)


def meeting_room_attribute_list(request):
    meeting_room_attributes = MeetingRoomAttribute.objects.all()
    context = {'meeting_room_attributes': meeting_room_attributes}
    return render(request, 'meeting_room/attributes_list.html', context)

@login_required()
@p3permission_required('meeting_room.add_meetingroom')
@transaction.atomic()
def add(request, id=None):
    # try:

    document_type = DocumentType.objects.get(code='SKONF')  # TODO: kody dla takich statycznych typów dokumentów zdefiniować w pliku settings

    if id is not None:
        meeting_room = MeetingRoom.objects.get(pk=id)
        address_form = AddressForm(request.POST or None, instance=meeting_room.address, label_suffix=':', prefix='address')
        attr_values = doc_utils.get_document_attribute_values(id=id, id_type=document_type.pk)
    else:
        meeting_room = None
        address_form = AddressForm(request.POST or None, instance=None, label_suffix=':', prefix='address')
        attr_values = None

    form = MeetingRoomForm(request.POST or None, instance=meeting_room, label_suffix=':', prefix='meeting_room')
    attr = doc_utils.get_attributes(document_type.pk)
    attr_form = DocumentAttributeForm(data=request.POST or None, document_type=document_type, defaults=False, prefix='attribute', initial=attr_values)

    if request.method == 'POST':
        if all([form.is_valid(), attr_form.is_valid(), address_form.is_valid()]):
            meeting_room = form.save(commit=False)

            if not meeting_room.is_local:
                meeting_room.address = address_form.save()
            elif meeting_room.address:
                meeting_room.address.delete()
            meeting_room.save()

            doc_utils.save_document_attributes(meeting_room.pk, document_type.pk, attr_form.cleaned_data)

            return redirect('meeting_room.list')

    context = {'form': form,
               'address_form': address_form,
               'document_type': document_type,
               'attr': attr,
               'attr_form': attr_form}

    return render(request, 'meeting_room/add.html', context)



