import json
import traceback

from django import urls
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from application.wrapper import rest_api_wrapper
from apps.hierarchy.models import Hierarchy, HierarchyGroup
from .serializers import HierarchyGetSerializer, HierarchyDetailSerializer, HierarchySerializer, GroupSerializer
from .. import HIERARCHY_TYPE_STATUS


class HierarchyApi(APIView):
    def _get_nodes(self, root_node_id=None):
        q = Q(pk=root_node_id) if root_node_id else Q(parent=None)
        return HierarchyGetSerializer(Hierarchy.objects.get(q)).data

    def _move(self, node_id, node_to):
        Hierarchy.objects.get(pk=node_id).move_to(Hierarchy.objects.get(pk=node_to))
        return self._get_nodes()

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

        with transaction.atomic():
            data = json.loads(request.data.dict()['form'])
            hierarchy_groups = data.pop('hierarchy_groups')
            hierarchy = HierarchySerializer(
                instance=Hierarchy.objects.get(pk=data.get('id')),
                data=data
            )
            hierarchy.is_valid(raise_exception=True)
            hierarchy = hierarchy.save()

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

        with transaction.atomic():
            hierarchy = HierarchySerializer(data=data)
            hierarchy.is_valid(raise_exception=True)
            hierarchy = hierarchy.save()

            for group in hierarchy_groups:
                HierarchyGroup.objects.create(
                    hierarchy=hierarchy,
                    group=Group.objects.get(pk=group['id'])
                )

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
