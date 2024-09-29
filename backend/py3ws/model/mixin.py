from django.db import models
from django.utils.translation import gettext_lazy as _


class Address(models.Model):
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

    def get_compact_address(self, split_line=False):
        street = self.street or ''
        street_no = self.street_no or ''
        apartment_no = self.apartment_no or ''
        post_code = self.post_code or ''
        city = self.city or ''

        return '%s %s/%s%s%s %s' % \
               (street, street_no, apartment_no, "<br>" if split_line else '', (", " if not split_line else '' + post_code), city) or ''

    class Meta:
        abstract = True
