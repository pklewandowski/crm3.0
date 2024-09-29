from django.contrib import admin

from apps.document.models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    search_fields = ['code', 'owner__last_name', 'owner__nip', 'owner__personal_id', 'owner__regon']
    list_display = ['code', 'owner']
