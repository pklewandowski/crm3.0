from django.contrib import admin
from django.contrib.auth.models import Group

from apps.user.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ['last_name', 'nip', 'personal_id', 'regon']
    list_display = ['company_name', 'first_name', 'last_name', 'nip', 'personal_id']


admin.site.unregister(Group)
