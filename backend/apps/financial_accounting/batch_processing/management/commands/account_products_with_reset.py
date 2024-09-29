from django.core.management.base import BaseCommand

from apps.financial_accounting.batch_processing.loaders.loaderMT940 import LoaderMT940


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        LoaderMT940.account_products(start_date='2020-02-12', reset=True)