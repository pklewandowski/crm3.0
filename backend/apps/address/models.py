from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords


class AddressStreetPrefix(models.Model):
    code = models.CharField(max_length=10)
    description = models.TextField(null=True)
    sq = models.IntegerField(db_column='sq')

    def __str__(self):
        return self.code

    class Meta:
        db_table = "address_street_prefix"


class Address(models.Model):
    type = models.ForeignKey('AddressType', db_column='id_type', null=True, blank=True, on_delete=models.CASCADE)
    street_prefix = models.CharField(max_length=10, null=True, blank=True)
    street = models.CharField(max_length=100, null=True, blank=True)
    street_no = models.CharField(max_length=15, null=True, blank=True)
    apartment_no = models.CharField(max_length=10, null=True, blank=True)
    post_code = models.CharField(max_length=10, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True, default=_('Polska'))
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    lat = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    lng = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    history = HistoricalRecords(table_name='h_address')

    def get_compact_address(self, split_line=False):
        street = self.street or ''
        street_no = self.street_no or ''
        apartment_no = self.apartment_no or ''
        post_code = self.post_code or ''
        city = self.city or ''

        return '%s %s/%s %s%s %s' % (street, street_no, apartment_no, "<br>" if split_line else '', (", " if not split_line else '' + post_code), city) or ''

    def get_two_line_address(self):
        street_prefix = self.street_prefix or ''
        street = self.street or ''
        street_no = self.street_no or ''
        apartment_no = self.apartment_no or ''
        post_code = self.post_code or ''
        city = self.city or ''

        return [
            f"{street_prefix} {street} {street_no} {'/' if apartment_no else ''} {apartment_no}",
            f"{post_code}{', ' if city else ''}{city}"
        ]

    def __str__(self):
        return self.get_compact_address()

    class Meta:
        db_table = "address"


class AddressType(models.Model):
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "address_type"
