import json
import traceback

from django import urls
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q, Exists, OuterRef
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.hierarchy.models import Hierarchy, HierarchyGroup
from .serializers import HierarchyGetSerializer, HierarchyDetailSerializer, HierarchySerializer, GroupSerializer, \
    UserHierarchySerializer, UserForHierarchySerializer
from .. import HIERARCHY_TYPE_STATUS
from ...address.api.serializers import AddressSerializer
from ...address.models import Address
from ...user.models import UserHierarchy, User
from ...user_func.employee.models import Employee


class HierarchyApi(APIView):
    @staticmethod
    def _get_nodes(root_node_id=None):
        q = Q(pk=root_node_id) if root_node_id else Q(parent=None)
        return HierarchyGetSerializer(Hierarchy.objects.get(q)).data

    def _move(self, node_id, node_to):
        Hierarchy.objects.get(pk=node_id).move_to(Hierarchy.objects.get(pk=node_to))
        return self._get_nodes()

    @staticmethod
    def _get_address(data):
        hierarchy_address = data.pop('address')
        hierarchy_address['id'] = hierarchy_address['address_id']
        del hierarchy_address['address_id']

        return hierarchy_address

    @rest_api_wrapper
    def get(self, request):
        if request.path == urls.reverse('hierarchy.api.groups'):
            return GroupSerializer(Group.objects.all().order_by('name'), many=True).data

        if request.query_params.get('detail', None):
            return HierarchyDetailSerializer(Hierarchy.objects.get(pk=request.query_params.get('nodeId'))).data

        root_node_id = request.query_params.get('rootNodeId', None)
        return self._get_nodes(root_node_id)

    @rest_api_wrapper
    def put(self, request):
        if request.path == urls.reverse('hierarchy.api.move'):
            return self._move(request.data.get('nodeId'), request.data.get('nodeTo'))

        with (transaction.atomic()):
            data = json.loads(request.data.dict()['form'])

            hierarchy_groups = data.pop('hierarchy_groups')
            hierarchy_address = self._get_address(data)

            if data['type'] not in ['CMP', 'HDQ']:
                data['nip'] = None
                data['krs'] = None
                data['regon'] = None
                data['address'] = None
                data['share_capital_amount'] = 0.00

            hierarchy = HierarchySerializer(
                instance=Hierarchy.objects.get(pk=data.get('id')),
                data=data
            )
            hierarchy.is_valid(raise_exception=True)
            hierarchy = hierarchy.save()

            if hierarchy.type in ['CMP', 'HDQ']:
                hierarchy_address = AddressSerializer(
                    instance=Address.objects.get(pk=hierarchy_address['id']) if hierarchy_address.get('id') else None,
                    data=hierarchy_address
                )

                hierarchy_address.is_valid(raise_exception=True)
                hierarchy.address = hierarchy_address.save()

            hierarchy.save()

            hierarchy.groups.all().delete()

            for group in hierarchy_groups:
                HierarchyGroup.objects.create(
                    hierarchy=hierarchy,
                    group=Group.objects.get(pk=group['id'])
                )

    @rest_api_wrapper
    def post(self, request):
        data = json.loads(request.data.dict()['form'])
        data.pop('id')
        hierarchy_groups = data.pop('hierarchy_groups')
        hierarchy_address = data.pop('address')

        cleaned_data = {}

        for k, v in data.items():
            if not v:
                continue
            cleaned_data[k] = v

        data = cleaned_data

        with transaction.atomic():
            hierarchy = HierarchySerializer(data=data)
            hierarchy.is_valid(raise_exception=True)
            hierarchy = hierarchy.save()

            for group in hierarchy_groups:
                HierarchyGroup.objects.create(
                    hierarchy=hierarchy,
                    group=Group.objects.get(pk=group['id'])
                )

            if hierarchy.type in ['CMP', 'HDQ']:
                address = AddressSerializer(data=hierarchy_address)
                address.is_valid(raise_exception=True)
                address = address.save()

                hierarchy.address = address
                hierarchy.save()

    @rest_api_wrapper
    def delete(self, request):
        Hierarchy.objects.get(pk=request.data.get('id')).delete()


@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def get_company_list_for_select(request):
    response_status = status.HTTP_200_OK

    try:
        response_data = [{'label': i.name, 'value': i.id, 'data': [{'name': 'account', 'value': i.bank_account}]}
                         for i in Hierarchy.objects.filter(type=HIERARCHY_TYPE_STATUS['subcompany']).order_by('name')]
    except Exception as ex:
        response_data = {'errmsg': str(ex), 'traceback': traceback.format_exc()}
        response_status = status.HTTP_422_UNPROCESSABLE_ENTITY

    return Response(data=response_data, status=response_status)


class HierarchyUserApi(APIView):
    @rest_api_wrapper
    def get(self, request):
        return UserHierarchySerializer(
            UserHierarchy.objects.filter(
                hierarchy=request.query_params.get('id')).order_by('user__last_name'), many=True).data

    @rest_api_wrapper
    def post(self, request):
        user_id = request.data.get('userId')
        node_id = request.data.get('nodeId')

        user = User.objects.get(pk=user_id)

        UserHierarchy.objects.create(
            user=user,
            hierarchy=Hierarchy.objects.get(pk=node_id)
        )

        return UserForHierarchySerializer(instance=user).data

    @rest_api_wrapper
    def delete(self, request):
        user_id = request.data.get('userId')
        node_id = request.data.get('nodeId')

        UserHierarchy.objects.get(
            user=User.objects.get(pk=user_id),
            hierarchy=Hierarchy.objects.get(pk=node_id)
        ).delete()


@api_view(['GET'])
@renderer_classes((JSONRenderer,))
def get_employee_for_hierarchy_select2(request):
    key = request.query_params.get('q', None)
    node_id = request.query_params.get('nodeId', None)

    response_data = {}
    response_status = status.HTTP_200_OK

    q = Q(user__is_active=True) & (
            Q(user__last_name__icontains=key) |
            Q(user__first_name__icontains=key) |
            Q(user__phone_one__icontains=key)
    ) if key else Q()

    try:
        result = Employee.objects.filter(q).filter(
            ~Exists(UserHierarchy.objects.filter(user=OuterRef("pk"), hierarchy=node_id)))
        response_data['results'] = [
            {'id': i.pk, 'text': (i.user.first_name + ' ' if i.user.first_name else '') + (i.user.last_name or '')} for
            i in result]

    except Exception as e:
        response_status = status.HTTP_400_BAD_REQUEST
        response_data = {'errmsg': str(e), 'errtype': e.__class__.__name__, 'traceback': traceback.format_exc()}

    return Response(response_data, status=response_status)
