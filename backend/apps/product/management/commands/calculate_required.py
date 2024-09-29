import datetime
import logging

from django.core.management import BaseCommand

from apps.product.calc import CalculateLoan
from apps.product.models import Product
from apps.user.models import User

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     # Positional arguments
    #     parser.add_argument("poll_ids", nargs="+", type=int)
    #
    #     # Named (optional) arguments
    #     parser.add_argument(
    #         "--delete",
    #         action="store_true",
    #         help="Delete poll instead of closing it",
    #     )

    def handle(self, *args, **options):
        user = User.objects.get(username="__systemprocess")

        logger.info(f'Start calculating required loan')

        for product in Product.objects.filter(recount_required_date__isnull=False):
            with CalculateLoan(product=product, user=user) as calc:
                logger.info(f'Calculating product {product.id} required date: {product.recount_required_date}')

                calc.calculate(product.recount_required_date)

