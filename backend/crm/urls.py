"""crm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import re_path as url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path as url
from django.contrib import admin

import apps.login.views

app_name = 'crm'
urlpatterns = [

    url(r'^login/', apps.login.views.log_in, name='login.login'),
    url(r'^logout/', apps.login.views.log_out, name='login.logout'),

    url(r'^', include('apps.home.urls')),
    url(r'^app-settings/', include('apps.app_settings.urls')),
    url(r'^address/', include('apps.address.urls')),
    url(r'^config/', include('apps.config.urls')),
    url(r'^hierarchy/', include('apps.hierarchy.urls')),
    url(r'^client/', include('apps.user_func.client.urls')),
    url(r'^broker/', include('apps.user_func.broker.urls')),
    url(r'^adviser/', include('apps.user_func.adviser.urls')),
    url(r'^employee/', include('apps.user_func.employee.urls')),
    url(r'^contractor/', include('apps.user_func.contractor.urls')),
    # url(r'^lawoffice/', include('apps.user_func.lawoffice.urls')),
    url(r'^log/', include('apps.log.urls')),
    url(r'^gus/', include('apps.gus.urls')),
    url(r'^user/', include('apps.user.urls')),
    url(r'^schedule-app/', include('apps.schedule_app.urls')),
    url(r'^schedule/', include('apps.scheduler.schedule.urls')),
    # url(r'^calendar/', include('apps.scheduler.calendar.urls')),
    url(r'^meeting-room/', include('apps.meeting_room.urls')),
    url(r'^message/', include('apps.message.urls')),
    url(r'^ocr/', include('apps.ocr.urls')),
    url(r'^product/', include('apps.product.urls')),
    url(r'^document/', include('apps.document.urls')),
    # url(r'^document/', include('apps.document.urls', app_name='document', namespace='apps')),
    url(r'^attachment/', include('apps.attachment.urls')),
    url(r'^attribute/', include('apps.attribute.urls')),
    url(r'^dict/', include('apps.dict.urls')),
    url(r'^report/', include('apps.report.urls')),
    url(r'^stat/summary-report/', include('apps.stat.summary_report.urls')),
    url(r'^fa/invoice/', include('apps.financial_accounting.invoice.urls')),
    url(r'^batch-processing/', include('apps.financial_accounting.batch_processing.urls')),
    url(r'^product-retail/', include('apps.product_retail.urls')),
    url(r'^marketing/lp/', include('apps.marketing.lp.urls')),
    url(r'^marketing/partner/', include('apps.marketing.partner.urls')),
    url(r'^notification/', include('apps.notification.urls')),
    url(r'^tag/', include('apps.tag.urls')),
    url(r'^file-repository/', include('apps.file_repository.urls')),
    url(r'^table-report/', include('apps.table_report.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^_temp/', include('_temp.urls')),
]
