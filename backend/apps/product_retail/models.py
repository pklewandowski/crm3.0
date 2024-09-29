from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.user_func.client.models import Client
from apps.user.models import User
from apps.scheduler.schedule.models import Schedule

CLIENT_CLASS = Client
USER_CLASS = User
SCHEDULE_CLASS = Schedule
MIN_AUTOCOMPLETE_CHAR_LEN = 2


class ProductRetailCategory(models.Model):
    parent = models.ForeignKey('self', db_column='id_parent', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(verbose_name=_('product.retail.category.name'), max_length=200)
    description = models.TextField(verbose_name=_('product.retail.category.description'), null=True, blank=True)
    sq = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'product_retail_category'


class ProductRetail(models.Model):
    category = models.ForeignKey(ProductRetailCategory, db_column='id_category', on_delete=models.CASCADE)
    name = models.CharField(verbose_name=_('product.retail.name'), max_length=200)
    description = models.TextField(verbose_name=_('product.retail.description'), null=True, blank=True)
    unit_price = models.DecimalField(verbose_name=_('product.retail.unit_price'), max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'product_retail'


class ProductRetailClient(models.Model):
    client = models.ForeignKey(CLIENT_CLASS, db_column='id_client', on_delete=models.CASCADE)
    if SCHEDULE_CLASS:
        schedule = models.ForeignKey(SCHEDULE_CLASS, db_column='id_schedule', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(ProductRetail, db_column='id_product', on_delete=models.CASCADE)
    quantity = models.DecimalField(verbose_name=_('product.retail.client.quantity'), max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(verbose_name=_('product.retail.client.unit_price'), max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(verbose_name=_('product.retail.client.total_cost'), max_digits=10, decimal_places=2, null=True, blank=True)
    payment_type = models.CharField(verbose_name=_('product.retail.client.payment_type'), max_length=50, blank=True)
    creation_date = models.DateTimeField(verbose_name=_('product.retail.client.total_cost'), auto_now_add=True)
    created_by = models.ForeignKey(USER_CLASS, db_column='id_created_by', blank=True, on_delete=models.CASCADE)

    class Meta:
        db_table = 'product_retail_client'
