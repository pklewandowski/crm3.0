import json

from django.core.management import BaseCommand
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from apps.document.models import Document, DocumentAttribute, DocumentStatusCourse, DocumentStatusTrack


class DocumentAttributeSerializer(ModelSerializer):
    class Meta:
        model = DocumentAttribute
        exclude = ('id', 'document_id')


class DocumentStatusCourseSerializer(ModelSerializer):
    class Meta:
        model = DocumentStatusCourse
        exclude = ('id', 'document')


class DocumentStatusTrackSerializer(ModelSerializer):
    class Meta:
        model = DocumentStatusTrack
        exclude = ('id', 'document')


class DocumentSerializer(ModelSerializer):
    attributes = serializers.SerializerMethodField()
    status_track = DocumentStatusTrackSerializer(many=True)
    status_course = DocumentStatusCourseSerializer(many=True)

    def get_attributes(self, obj):
        return DocumentAttributeSerializer(
            DocumentAttribute.objects.filter(document_id=obj.id), many=True).data

    class Meta:
        model = Document
        exclude = ('id', 'attachments')


def get_attributes(attributes: list[DocumentAttribute], attribute_list: list) -> dict:
    for attribute in attributes:
        _attribute_dict = DocumentAttributeSerializer(attribute).data
        _attribute_dict['__children'] = []
        attribute_list.append(_attribute_dict)

        children = DocumentAttribute.objects.filter(parent=attribute)

        if children:
            get_attributes(children, attribute_list[-1]['__children'])


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-i', '--id', type=int, action='store')
        parser.add_argument('-f', '--file', action='store')

    def handle(self, *args, **kwargs):
        document = Document.objects.get(pk=kwargs['id'])

        # its recursive option when needed inf future. Not used at the moment
        # attribute_list = []
        # get_attributes(
        #     DocumentAttribute.objects.filter(document_id=document.pk, parent__isnull=True),
        #     attribute_list)

        doc = DocumentSerializer(document).data

        # its recursive option when needed inf future. Not used at the moment
        # doc['__attributes'] = attribute_list

        j = json.dumps(doc)

        with open(kwargs['file'], 'w') as f:
            f.write(j)
