import pprint
import traceback

from abc import ABC, abstractmethod

from django.forms import modelformset_factory
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext as _
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponse

from py3ws.views import generic_view
from py3ws.forms.p3form import ModelForm

from .models import ProductRetailCategory, ProductRetailClient
from .models import ProductRetail
from .config import SCHEDULE_CLASS, CLIENT_CLASS
from .forms import ProductRetailClientForm, ProductRetailClientFormset


#
# class ProductRetailBase(generic_view):
#     @abstractmethod
#     def save_product_category(self, data):
#         pass
#
#     @abstractmethod
#     def save_product(self, data):
#         pass
#
#     @abstractmethod
#     def add_to_client(self, data):
#         pass
#
#     @abstractmethod
#     def get_product_list(self, client: CLIENT_CLASS, schedule):
#         pass


class ProductRetailMapper:

    @staticmethod
    def _get_data(form: ModelForm, request):
        data = form.save(commit=False)
        data.created_by = request.user
        return data

    @staticmethod
    def get_client_form(post_data, instance=None):
        return ProductRetailClientForm(data=post_data, instance=instance)

    @staticmethod
    def get_product_client_formset(data, queryset=ProductRetailClient.objects.none(), prefix='product_retail_client_formset'):
        return ProductRetailClientFormset(data=data, queryset=queryset, prefix=prefix)

    def save_product_category(self, data: ProductRetailCategory):
        pass

    def save_product(self, data: ProductRetail):
        pass

    def add_to_client(self, data: ProductRetailClient):
        if data.pk:
            return data.save()
        else:
            return ProductRetailClient.objects.create(data)

    def get_product_list(self, client: CLIENT_CLASS, schedule):
        q = Q(client=client)
        if SCHEDULE_CLASS and isinstance(schedule, SCHEDULE_CLASS):
            q &= Q(schedule=schedule)

        return ProductRetailClient.objects.filter(q).prefetch_related('product')

    def get_list_for_autocomplete(self, key):
        return ProductRetail.objects.filter(name__istartswith=key).order_by('name')

    @staticmethod
    def get_category_tree(parent):
        data = []
        if not parent:
            nodes = ProductRetailCategory.objects.filter(parent__isnull=True).order_by('sq')
        else:
            nodes = ProductRetailCategory.objects.filter(parent=parent).order_by('sq')

        for node in nodes:
            data.append({
                'text': node.name,
                'id': node.id,
                'state': {
                    'opened': True,
                    'selected': False
                },
                'children': ProductRetailMapper.get_category_tree(node.pk)
            })
        return data

    @staticmethod
    def get_products_for_category(id):
        return ProductRetail.objects.filter(category=ProductRetailCategory.objects.get(pk=id)).order_by('name')
