from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from py3ws.utils.validators import regon_validator
from utils.validators import nip_validator, krs_validator


class AppModel(models.Model):
    class Meta:
        abstract = True


class AuditMixin(models.Model):
    created_by = models.ForeignKey('user.User', db_column='id_creation_user', related_name="+",
                                   on_delete=models.CASCADE)
    updated_by = models.ForeignKey('user.User', db_column='id_update_user', related_name="+", on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now=True)
    update_date = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        abstract = True


class AddressMixin:
    def json_address_validator(self, address: dict):
        address_items = address.keys()
        available_item_list = ['street', 'street_no', 'apartment_no', 'zip_code', 'city', 'province', 'country']
        for key in address_items:
            if key not in available_item_list:
                raise ValidationError(_(f'Address contains not allowed item: {key}'))

    address = JSONField(default=dict, validators=[json_address_validator])

    def get_compact_address(self, split_line=False, html=False, add_country=False):
        new_line = '<br/>' if html else '\n'

        street = self.address['street'] or '' if 'street' in self.address else ''
        street_no = f" {self.address['street_no']}" or '' if 'street_no' in self.address else ''
        apartment_no = f" lok. {self.address['apartment_no']}" or '' if 'apartment_no' in self.address else ''
        zip_code = self.address['zip_code'] or '' if 'zip_code' in self.address else ''
        city = f" {self.address['city']}" or '' if 'city' in self.address else ''
        country = f" {self.address['country']}" if 'country' in self.address else ''

        colon = ', ' if zip_code or city or country else ' '
        separator = f"{new_line if split_line else colon}"

        return f"{street}{street_no}{apartment_no}{separator}{zip_code}{city}{country if add_country else ''}"

    class Meta:
        abstract = True


class CompanyDataMixin:
    nip = models.CharField(verbose_name=_('nip'), max_length=20, null=True, blank=True, unique=True,
                           validators=[nip_validator])
    krs = models.CharField(verbose_name=_('krs'), max_length=20, null=True, blank=True, unique=True,
                           validators=[krs_validator])
    regon = models.CharField(verbose_name=_('regon'), max_length=20, null=True, blank=True, unique=True,
                             validators=[regon_validator])

    class Meta:
        abstract = True


class ContactDataMixin:
    email = models.EmailField(verbose_name=_('email'), null=True, blank=True, unique=True)
    phone_one = models.CharField(verbose_name=_('phone_one'), max_length=20, null=True, blank=True)
    phone_two = models.CharField(verbose_name=_('phone_two'), max_length=20, null=True, blank=True)

    class Meta:
        abstract = True
