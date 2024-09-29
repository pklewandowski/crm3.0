from django.urls import re_path as url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='product_retail.index'),
    url(r'^add/$', views.Add.as_view(), name='product_retail.add'),
    url(r'^edit/(?P<id>\d+)/$', views.Edit.as_view(), name='product_retail.edit'),
    url(r'^list/$', views.List.as_view(), name='product_retail.list'),
    url(r'^category/add-category/$', views.AddCategory.as_view(), name='product_retail.category.add'),
    url(r'^category/delete-category/$', views.DeleteCategory.as_view(), name='product_retail.category.delete'),
    url(r'^add-to-client/$', views.AddToClient.as_view(), name='product_retail.add_to_client'),
    url(r'^get-list-for-autocomplete/$', views.GetListForAutocomplete.as_view(), name='product_retail.get_list_for_autocomplete'),
    url(r'^get-category-tree/$', views.GetCategoryTree.as_view(), name='product_retail.get_category_tree'),
    url(r'^get-products-for-category/$', views.GetProductsForCategory.as_view(), name='product_retail.get_products_for_category'),
]
