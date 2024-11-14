from rest_framework import serializers

from apps.attachment.api.serializers import AttachmentSerializer
from apps.attribute.models import Attribute
from apps.document.models import DocumentTypeSection, DocumentTypeAttribute, DocumentAttribute, \
    DocumentTypeSectionColumn, DocumentAttachment, DocumentStatusTrack, DocumentTypeProcessFlow, \
    DocumentTypeStatus, Document, DocumentNote, DocumentTypeAccountingType


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute
        fields = '__all__'


class DocumentAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAttribute
        fields = '__all__'


class DocumentTypeAttributeSerializer(serializers.ModelSerializer):
    attribute = AttributeSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentTypeAttribute
        fields = '__all__'


class DocumentTypeSectionColumnSerializer(serializers.ModelSerializer):
    column_attribute_set = DocumentTypeAttributeSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentTypeSectionColumn
        fields = '__all__'


class DocumentTypeSubSectionSerializer(serializers.ModelSerializer):
    column_set = DocumentTypeSectionColumnSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentTypeSection
        fields = '__all__'


class DocumentTypeSectionSerializer(serializers.ModelSerializer):
    column_set = DocumentTypeSectionColumnSerializer(many=True, read_only=True)

    class Meta:
        model = DocumentTypeSection
        fields = '__all__'


class DocumentAttachmentSerializer(serializers.ModelSerializer):
    attachment = AttachmentSerializer()

    class Meta:
        model = DocumentAttachment
        exclude = ('document',)
        # depth = 1


class DocumentTypeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentTypeStatus
        fields = ('id', 'name', 'is_alternate')


class DocumentStatusTrackSerializer(serializers.ModelSerializer):
    status = DocumentTypeStatusSerializer()

    class Meta:
        model = DocumentStatusTrack
        fields = ('status',)
        depth = 1


class DocumentTypeProcessFlowSerializer(serializers.ModelSerializer):
    available_status = DocumentTypeStatusSerializer()

    class Meta:
        model = DocumentTypeProcessFlow
        fields = ('available_status',)
        depth = 1


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'


class DocumentFormSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        at = super(DocumentFormSerializer, self).validate(attrs)
        return at

    class Meta:
        model = Document
        fields = ('owner', 'responsible', 'annex')


class DocumentNoteSerializer(serializers.ModelSerializer):
    headerText = serializers.CharField
    bodyText = serializers.CharField

    class Meta:
        model = DocumentNote
        fields = '__all__'


class DocumentTypeAccountingTypeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def get_children(self, obj):
        return DocumentTypeAccountingTypeSerializer(DocumentTypeAccountingType.objects.filter(parent=obj).order_by('sq'), many=True).data

    class Meta:
        model = DocumentTypeAccountingType
        fields = 'id', 'code', 'name', 'children'
