import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import html

from apps.product_retail.forms import ProductRetailForm
from py3ws.utils.utils import is_ajax
from . import *
from .product_retail import *


def index(request):
    return HttpResponse('Product_Retail')


class ProductRetailView(generic_view.GenericView):

    def set_app_name(self):
        self._app_name = 'product_retail'

    def __init__(self):
        super().__init__()


class Add(ProductRetailView):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):
        super().dispatch(request, *args, **kwargs)

        form = ProductRetailForm(request.POST or None)
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('product_retail.list')

        context = self._context
        context['form'] = form
        return render(request, 'product_retail/add.html', context)


class Edit(ProductRetailView):
    def set_mode(self):
        self._mode = settings.MODE_EDIT

    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):

        id = kwargs.pop('id', None)
        if not id:
            raise AttributeError('Brak ID produktu detalicznego do edycji')

        super().dispatch(request, *args, **kwargs)

        form = ProductRetailForm(request.POST or None, instance=ProductRetail.objects.get(pk=id))
        if request.method == 'POST':
            if form.is_valid():
                form.save()
                return redirect('product_retail.list')

        context = self._context
        context['form'] = form
        return render(request, 'product_retail/add.html', context)


class List(generic_view.ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    def set_app_name(self):
        self._app_name = 'product_retail'

    def set_where(self):
        if self.search:
            self.where &= (
                Q(name__icontains=self.search) |
                Q(category__name__icontains=self.search)
            )

    def set_query(self):
        self.query = ProductRetail.objects.all().prefetch_related('category').order_by('%s%s' % (self.sort_dir, self.sort_field))

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        super(List, self).dispatch(request, *args, **kwargs)
        self.check_permissions(request.user)

        return self.list(request=request, template='product_retail/list.html')

    def __init__(self):
        self.default_sort_field = 'name'
        super(List, self).__init__()


class AddCategory(ProductRetailView):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if not is_ajax(request):
            raise TypeError('HTTP requests Not Implemented yet!')

        status = 200
        response_data = {}

        try:
            if request.method == 'POST':
                name = html.mark_safe(request.POST.get('name'))
                parent_id = html.mark_safe(request.POST.get('parentId'))

                parent = ProductRetailCategory.objects.get(pk=parent_id)
                sq = ProductRetailCategory.objects.filter(parent=parent).count() + 1

                category = ProductRetailCategory.objects.create(name=name, sq=sq, parent=parent)
                response_data = {'id': category.pk, 'name': category.name}

        except Exception as e:
            status = 400
            response_data['errmsg'] = str(e)

        return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)


class AddToClient(ProductRetailView, ProductRetailMapper):
    def set_mode(self):
        self._mode = settings.MODE_CREATE

    @login_required()
    @transaction.atomic()
    def dispatch(self, request, *args, **kwargs):

        status = 200
        response_data = {}

        super(self, AddToClient).dispatch(request, *args, **kwargs)

        form = ProductRetailClientForm(data=request.POST or None)

        try:
            if request.method == 'POST':
                if form.is_valid():
                    self.add_to_client(ProductRetailMapper._get_data(form, request))
                else:
                    status = 400
                    response_data['errors'] = form.errors

        except Exception as e:
            status = 400
            response_data['errmsg'] = str(e)

        if is_ajax(request):
            return HttpResponse(json.dumps(response_data), content_type="application/json", status=status)
        else:
            raise TypeError('HTTP type requests not implemented yet!')


class GetListForAutocomplete(ProductRetailView, ProductRetailMapper):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if not is_ajax(request):
            raise TypeError('HTTP requests Not Implemented yet!')

        status = 200
        response_data = {}
        key = request.POST.get('key')

        try:
            if key and len(key) > MIN_AUTOCOMPLETE_CHAR_LEN:
                response_data['data'] = [{'id': i.pk, 'text': i.name} for i in self.get_list_for_autocomplete(key)]

        except Exception as e:
            status = 400
            response_data['errmsg'] = str(e)

        return HttpResponse(json.dumps(response_data), status=status)


class GetCategoryTree(ProductRetailView, ProductRetailMapper):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if not is_ajax(request):
            raise TypeError('HTTP requests Not Implemented yet!')
        status = 200
        response_data = {}

        try:
            response_data['data'] = ProductRetailMapper.get_category_tree(parent=None)

        except Exception as e:
            status = 400
            response_data['errmsg'] = str(e)

        return HttpResponse(json.dumps(response_data), status=status, content_type="application/json")


class GetProductsForCategory(generic_view.ListView):
    def set_mode(self):
        self._mode = settings.MODE_VIEW

    _category_id = None

    def set_app_name(self):
        self._app_name = 'product_retail'

    def set_query(self):
        self.query = ProductRetail.objects.filter(self.where)

    def set_where(self):
        self.where = Q(category=ProductRetailCategory.objects.get(pk=self._category_id))

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax:
            raise TypeError('HTTP requests Not Implemented yet!')

        self._category_id = request.POST.get('id')

        if not self._category_id:
            raise AttributeError('Brak id kategorii')

        super(GetProductsForCategory, self).dispatch(request, *args, **kwargs)

        return self.list(request)


class DeleteCategory(ProductRetailView):
    def set_mode(self):
        self._mode = settings.MODE_DELETE

    @transaction.atomic()
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax:
            raise TypeError('HTTP requests Not Implemented yet!')

        status = 200
        response_data = {}

        try:
            if request.method == 'POST':
                category_id = html.mark_safe(request.POST.get('id'))
                if not category_id:
                    raise Exception('Brak parametru ID kategorii')

                category = ProductRetailCategory.objects.get(pk=category_id)
                if ProductRetail.objects.filter(category=category).count():
                    raise Exception('Dla kategorii istnieją produkty. Aby usunąć kategorię należy najpierw usunąć lub przenieść wszystkie jej produkty')

                category.delete()

        except Exception as e:
            response_data['errmsg'] = str(e)
            status = 400

        return HttpResponse(json.dumps(response_data), status=status, content_type="application/json")
