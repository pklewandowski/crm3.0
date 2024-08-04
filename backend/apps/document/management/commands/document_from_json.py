import json

from django.core.management import BaseCommand
from django.db import transaction
from rest_framework.serializers import ModelSerializer

from apps.document.models import Document, DocumentAttribute, DocumentStatusCourse, DocumentStatusTrack


class DocumentSerializer(ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class DocumentAttributeSerializer(ModelSerializer):
    class Meta:
        model = DocumentAttribute
        fields = '__all__'


class DocumentStatusCourseSerializer(ModelSerializer):
    class Meta:
        model = DocumentStatusCourse
        fields = '__all__'


class DocumentStatusTrackSerializer(ModelSerializer):
    class Meta:
        model = DocumentStatusTrack
        fields = '__all__'


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-f', '--file', action='store')

    def handle(self, *args, **kwargs):
        with (open(kwargs['file'], 'r') as f):
            doc = json.loads(f.read())
            attributes = doc.pop('attributes')
            status_course = doc.pop('status_course')
            status_track = doc.pop('status_track')

            doc = DocumentSerializer(data=doc)
            with transaction.atomic():
                if doc.is_valid(raise_exception=True):
                    doc = doc.save()

                for at in attributes:
                    at['document_id'] = doc.id

                for sc in status_course:
                    sc['document'] = doc.id

                for st in status_track:
                    st['document'] = doc.id

                at = DocumentAttributeSerializer(data=attributes, many=True)

                if at.is_valid(raise_exception=True):
                    at.save()

                sc = DocumentStatusCourseSerializer(data=status_course, many=True)
                if sc.is_valid(raise_exception=True):
                    sc.save()

                st = DocumentStatusTrackSerializer(data=status_track, many=True)
                if st.is_valid(raise_exception=True):
                    st.save()

                pass
