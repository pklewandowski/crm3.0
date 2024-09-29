from django.utils.translation import gettext_lazy as _
from django.db import models


class Dictionary(models.Model):
    type = models.CharField(max_length=20)  # , verbose_name='[R]eferencja albo [S]ugestia'
    code = models.CharField(max_length=200)
    label = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True, blank=True)
    active = models.BooleanField(default=True)
    editable = models.BooleanField(default=True)

    def __str__(self):
        return self.label

    class Meta:
        db_table = 'dictionary'
        # default_permissions = ('change',)
        # permissions = (
        #     ('view_dictionary', _('permissions.app.dict.view_dictionary')),
        #     ('list_dictionary', _('permissions.app.dict.list_dictionary')),
        # )


class DictionaryReference(models.Model):
    dictionary = models.ForeignKey(Dictionary, db_column='id_dictionary', on_delete=models.CASCADE)
    table_name = models.CharField(max_length=100, db_column='table_name')
    column_name = models.CharField(max_length=100, db_column='column_name')

    def __str__(self):
        return '%s %s' % (self.table_name, self.column_name)

    class Meta:
        db_table = 'dictionary_reference'
        default_permissions = ()


class DictionaryEntry(models.Model):
    dictionary = models.ForeignKey(Dictionary, db_column='id_dictionary', on_delete=models.CASCADE)
    label = models.CharField(max_length=200, db_column='label')
    value = models.CharField(max_length=20, db_column='value', null=True, blank=True)
    active = models.BooleanField(default=True, db_column='active')
    sq = models.IntegerField(db_column='sq')

    def __str__(self):
        return self.label

    class Meta:
        db_table = 'dictionary_entry'
        unique_together = ('dictionary', 'value')
        default_permissions = ('add', 'change')
        permissions = ()
