from django.core.management.base import BaseCommand

from apps.financial_accounting.batch_processing.loaders.loaderMT940 import LoaderMT940
from apps.product.models import Product


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-s', '--start_date', action='store')
        parser.add_argument('-e', '--end_date', action='store', default=None)
        parser.add_argument('-p', '--product_id', action='store', default=None)
        parser.add_argument('-r', '--reset', action='store_true', default=False, help='Delete all cash flow from product first')

    def handle(self, *args, **options):
        product = Product.objects.get(pk=options['product_id']) if options['product_id'] else None
        LoaderMT940.account_products(product=product, start_date=options['start_date'], reset=options['reset'])
