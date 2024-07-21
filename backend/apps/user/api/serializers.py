from rest_framework import serializers

from apps.address.api.serializers import AddressSerializer
from apps.attachment.api.serializers import AttachmentSerializer
from apps.user.models import User, UserAttachment, UserRelation, UserRelationType


class UserSerializer(serializers.ModelSerializer):
    company_address = AddressSerializer()
    home_address = AddressSerializer()
    mail_address = AddressSerializer()

    class Meta:
        model = User
        exclude = ('password',)


class UserAttachmentSerializer(serializers.ModelSerializer):
    attachment = AttachmentSerializer()

    class Meta:
        model = UserAttachment
        exclude = ('document',)
        # depth = 1


class UserRelationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRelationType
        fields = '__all__'


class UserRelationSerializer(serializers.ModelSerializer):
    left = UserSerializer()
    right = UserSerializer()
    type = UserRelationTypeSerializer()

    class Meta:
        model = UserRelation
        fields = ('id', 'left', 'right', 'type', 'description')
