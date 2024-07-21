from django.urls import re_path as url
from django.views.decorators.csrf import csrf_exempt

from . import views
from .api import view as rest

urlpatterns = [
    url(r'^$', views.index, name='user.index'),
    url(r'^inactive/$', views.inactive, name='user.inactive'),
    url(r'^list/$', views.list, name='user.list'),
    url(r'^list/(?P<process_id>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$', views.list, name='user.list'),
    url(r'^add/$', views.Add.as_view(), name='user.add'),
    url(r'^add/(?P<user_type>\w+)/$', views.Add.as_view(), name='user.add'),
    url(r'^add/(?P<user_type>\w+)/(?P<source_code>\w+)/(?P<source_id>\d+)/$', views.Add.as_view(), name='user.add'),
    url(r'^added_iframe/$', views.added_iframe, name='user.added_iframe'),
    url(r'^user-active/$', views.active, name='user.active'),
    url(r'^user-anonimize/$', views.anonimize, name='user.anonimize'),
    url(r'^id-exist/$', views.id_exist, name='user.id_exist'),
    url(r'^autocomplete-check/$', views.autocomplete_check, name='user.autocomplete_check'),
    url(r'^edit/(?P<id>\d+)/$', views.edit, name='user.edit'),
    url(r'^edit/(?P<id>\d+)/(?P<type>\w+)/$', views.edit, name='user.edit'),
    url(r'^view/(?P<id>\d+)/$', views.view, name='user.view'),
    url(r'^changepassword/$', views.changepassword, name='user.changepassword'),
    url(r'^reset-password/$', views.reset_password, name='user.reset_password'),
    url(r'^group/add/$', views.addgroup, name='user.addgroup'),
    url(r'^group/edit/(?P<id>\d+)$', views.editgroup, name='user.editgroup'),
    url(r'^group/list/$', views.listgroup, name='user.listgroup'),
    url(r'^group/activate-group/$', views.activate_group, name='user.activate_group'),
    url(r'^user-delete/$', views.Delete.as_view(), name='user.delete'),
    url(r'^api/user$', rest.UserView.as_view(), name='user.api'),

    # ------------------------------- REST ----------------------------------
    url(r'^api/attachment/$', csrf_exempt(rest.AttachmentApi.as_view()), name='user.api.attachment'),
    url(r'^api/agreement-request/$', rest.AgreementApi.as_view(), name='user.api.agreement_request'),
    url(r'^api/reset-password/$', rest.PasswordReset.as_view(), name='user.api.password_reset'),
    url(r'^api/relation/$', rest.UserRelationApi.as_view(), name='user.api.relation'),
    url(r'^api/note/$', rest.UserNote.as_view(), name='user.api.note'),
    url(r'^api/details/$', rest.UserDetails.as_view(), name='user.api.user_details'),
    url(r'^api/get-for-select2/$', rest.get_for_select2, name='user.get_for_select2'),

]
