import datetime
import logging
from itertools import product

from django.core.management import BaseCommand

from apps.product.calc import CalculateLoan
from apps.product.models import Product
from apps.user.models import User

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def add_arguments(self, parser):
        # Positional arguments
        # parser.add_argument("product", nargs="+", type=int)

        # # Named (optional) arguments
        parser.add_argument("-p", "--product", action="store", help="Product id")

    def handle(self, *args, **options):
        user = User.objects.get(username="__systemprocess")

        logger.info(f'Start calculating required loan')
        product = Product.objects.get(pk=options["product"])

        with CalculateLoan(product=product, user=user) as calc:
            logger.info(f'Calculating product {product.id} required date: {product.recount_required_date}')
            calc.calculate()

