from django.contrib.auth.models import Group
from rest_framework import serializers

from apps.address.api.serializers import AddressSerializer
from apps.hierarchy.models import Hierarchy, HierarchyGroup
from apps.user.api.serializers import UserSerializer
from apps.user.models import UserHierarchy, User


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name', 'description')


class HierarchyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = HierarchyGroup
        fields = '__all__'


class HierarchySerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        hierarchy = Hierarchy(**validated_data)
        hierarchy.level = hierarchy.parent.level + 1
        hierarchy.save()
        return hierarchy

    class Meta:
        model = Hierarchy
        exclude = ('level',)


class HierarchyDetailSerializer(serializers.ModelSerializer):
    parent = HierarchySerializer()
    address = AddressSerializer()

    class Meta:
        model = Hierarchy
        fields = '__all__'


class HierarchyGetSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    is_root = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    HTMLclass = serializers.SerializerMethodField()

    class Meta:
        depth = 1
        model = Hierarchy
        fields = ('id', 'name', 'type', 'text', 'children', 'is_root', 'icon', 'HTMLclass', 'description', 'level')

    def get_text(self, obj):
        return "%s%s" % (obj.name, " - Dyrektor" if obj.type == 'DEP' else '')

    def get_children(self, obj):
        return HierarchyGetSerializer(obj.get_children(), many=True).data

    def get_is_root(self, obj):
        return obj.is_root_node()

    def get_icon(self, obj):
        if obj.type == 'DEP':
            return 'fas fa-user-friends'
        elif obj.type == 'POS':
            return 'far fa-user'

    def get_HTMLclass(self, obj):
        if obj.type == 'ROOT':
            return 'node-root'
        elif obj.type == 'CMP':
            return 'hierarchy-company'
        elif obj.type == 'HDQ':
            return 'hierarchy-headquarter'
        elif obj.type == 'DEP':
            return 'hierarchy-department'
        elif obj.type == 'POS':
            return 'hierarchy-position'

        return ''


class UserForHierarchySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = 'id', 'first_name', 'last_name', 'email', 'personal_id', 'nip'


class UserHierarchySerializer(serializers.ModelSerializer):
    user = UserForHierarchySerializer()

    class Meta:
        model = UserHierarchy
        fields = 'user',
