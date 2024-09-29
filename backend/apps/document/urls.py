from django.urls import re_path as url
from django.views.decorators.csrf import csrf_exempt

from . import views, vindication_views
from .api import views as rest
from .type import views as type_views
from .type.api import views as rest_type

urlpatterns = [
    # url(r'^add/(?P<type>\d+)/$', views.Add.as_view(), name='document.add'),
    # url(r'^add/(?P<type>\d+)/(?P<owner_id>\d+)/$', views.Add.as_view(), name='document.add'),
    # url(r'^add/(?P<type>\d+)/(?P<source_code>\w+)/(?P<source_id>\d+)/$', views.Add.as_view(), name='document.add'),

    # url(r'^edit/(?P<id>\d+)/$', views.Edit.as_view(), name='document.edit'),
    url(r'^edit/(?P<id>\d+)/(?P<redirection>\w)/$', views.Edit.as_view(), name='document.edit'),

    url(r'^view/(?P<id>\d+)/$', views.view, name='document.view'),

    url(r'^list/(?P<type>\d+)/$', views.ListView.as_view(), name='document.list'),
    url(r'^vindication/list/(?P<type>\d+)/$', vindication_views.ListView.as_view(), name='document.vindication.list'),

    url(r'^revert-status/$', views.RevertStatus.as_view(), name='document.revert_status'),
    url(r'^print-process-flow/$', views.PrintProcessFlow.as_view(), name='document.print_process_flow'),

    url(r'^type/category/list/$', views.list_category, name='document.type.category.list'),
    url(r'^type/list/$', views.list_document_type, name='document.type.list'),
    url(r'^type/list/(?P<id>\d+)/$', views.list_document_type, name='document.type.list'),
    url(r'^type/add/$', type_views.add_type, name='document.type.add'),
    url(r'^type/edit/(?P<id>\d+)/$', type_views.edit_type, name='document.type.edit'),
    url(r'^type/section/list/(?P<id>\d+)/$', views.list_document_type_section, name='document.type.section.list'),
    url(r'^type/section/add/(?P<id>\d+)/$', views.add_document_type_section, name='document.type.section.add'),
    url(r'^type/section/add/(?P<id>\d+)/(?P<id_parent>\d+)/$', views.add_document_type_section,
        name='document.type.section.add_repeat_subsection'),
    url(r'^type/section/edit/(?P<id>\d+)/$', views.edit_document_type_section, name='document.type.section.edit'),
    url(r'^type/section/section-delete/$', views.delete_document_type_section, name='document.type.section.delete'),
    url(r'^type/section/get-columns/$', views.get_section_columns, name='document.type.section.get_columns'),
    url(r'^type/attribute/list/(?P<id>\d+)/$', views.list_document_type_attribute, name='document.type.attribute.list'),
    url(r'^type/attribute/feature/(?P<id>\d+)/$', views.DocumentAttributeFeature.as_view(),
        name='document.type.attribute.feature'),
    url(r'^type/attribute/feature/(?P<id>\d+)/(?P<id_section>\d+)/$', views.DocumentAttributeFeature.as_view(),
        name='document.type.attribute.feature'),
    url(r'^type/attribute/add/(?P<id>\d+)/(?P<id_section>\d+)/$', views.add_document_type_attribute,
        name='document.type.attribute.add'),
    url(r'^type/attribute/edit/(?P<id>\d+)/$', views.edit_document_type_attribute, name='document.type.attribute.edit'),
    url(r'^type/attribute/attribute-delete/$', views.delete_document_type_attribute,
        name='document.type.attribute.delete'),
    url(r'^type/get-status-flow/$', views.get_status_flow, name='document.type.get_status_flow'),

    url(r'^ocr/box/$', views.DocumentOcrBox.as_view(), name='document.ocr.box'),

    # ---------------------- V2 -----------------

    url(r'^add/(?P<id>\d+)/$', rest.add, name='document.add'),
    url(r'^add/(?P<id>\d+)/(?P<owner_id>\d+)/$', rest.add, name='document.add'),
    url(r'^edit/(?P<id>\d+)/$', rest.edit, name='document.edit'),
    url(r'^type/definition/(?P<id>\d+)/$', rest.definition, name='document.type.definition'),

    url(r'^api/$', rest.DocumentApi.as_view(), name='document.api'),

    url(r'^api/attribute/$', rest.AttributeApi.as_view(), name='document.api.attribute'),
    url(r'^api/attribute/model/$', rest.AttributeModel.as_view(), name='document.api.attribute_model'),
    url(r'^api/attribute/data/$', rest.AttributeSectionData.as_view(), name='document.api.section_attribute'),

    url(r'^api/type/attribute/predefined/$', rest.PredefinedView.as_view(), name='document.api.type.predefined'),
    url(r'^api/get-for-annex$', rest.DocumentAnnexApi.as_view(), name='document.api.get_for_annex'),
    url(r'^api/attachment/$', csrf_exempt(rest.AttachmentApi.as_view()), name='document.api.attachment'),
    url(r'^api/note/$', rest.NoteApi.as_view(), name='document.api.note'),
    url(r'^type/api/status/$', rest_type.DocumentTypeStatusApi.as_view(), name='document.type.api.status')
]
