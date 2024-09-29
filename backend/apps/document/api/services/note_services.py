from apps.document.api.serializers import DocumentNoteSerializer
from apps.document.models import DocumentNote, Document


def _format_header_text(creation_date, created_by):
    return f'{creation_date} {created_by}'


def get_notes(document):
    return DocumentNoteSerializer(DocumentNote.objects.filter(document=document).order_by('-creation_date'), many=True).data


def update_note(id, text, user):
    note = DocumentNote.objects.get(pk=id)
    note.text = text
    note.updated_by = user
    note.save()


def create_note(id, text, user):
    return DocumentNoteSerializer(DocumentNote.objects.create(
        document=Document.objects.get(pk=id),
        text=text,
        created_by=user,
        updated_by=user
    )).data


def delete_note(id_note):
    DocumentNote.objects.get(pk=id_note).delete()
