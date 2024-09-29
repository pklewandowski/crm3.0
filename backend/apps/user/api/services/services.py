from django.db import transaction

from apps.document.api.serializers import DocumentSerializer
from apps.document.models import Document
from apps.home.api.serializers import DocumentSerializerForUserDetails
from apps.note.api.serializers import NoteSerializer
from apps.note.models import Note
from apps.product.api.serializers import ProductSerializer
from apps.product.models import Product
from apps.scheduler.schedule.api.serializers import ScheduleSerializer
from apps.scheduler.schedule.models import Schedule
from apps.user.api.serializers import UserSerializer
from apps.user.models import UserNote, User
from apps.user_func.client.api.serializers import ClientSerializer
from apps.user_func.client.models import Client


class UserServices:
    def __init__(self, user):
        self.user = user

    def save_note(self, note_text, note_user):
        with transaction.atomic():
            note = Note(
                text=note_text,
                created_by=self.user,
                updated_by=self.user
            )
            note.save()

            user_note = UserNote(user=note_user, note=note)
            user_note.save()

            return NoteSerializer(note).data


def get_details(request):
    id_user = request.query_params.get('id')

    user = User.objects.get(pk=id_user)

    try:
        client = Client.objects.get(pk=id_user)
    except Client.DoesNotExist:
        client = None

    notes = [i.note for i in UserNote.objects.filter(user=user).order_by('-note__creation_date')]
    events = Schedule.objects.filter(invited_users=user).order_by('-start_date')
    documents = Document.objects.filter(owner=user)

    products = Product.objects.filter(client=client) if client else None

    return {
        'user': UserSerializer(user).data,
        'client': ClientSerializer(client).data if client else None,
        'notes': NoteSerializer(notes, many=True).data,
        'events': ScheduleSerializer(events, many=True).data,
        'documents': DocumentSerializerForUserDetails(documents, many=True).data,
        'products': ProductSerializer(products, many=True).data
    }
