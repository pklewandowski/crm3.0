import logging
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.product.calc import LoanCalculation
from apps.product.models import Product, ProductCalculation
from apps.user.models import User

logging.basicConfig(level=logging.DEBUG, filename="../logfile", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-d', '--start_date', action='store')
        parser.add_argument('-p', '--product_id', action='store')

    def handle(self, *args, **kwargs):
        print('------------STARTING PRODUCT CALCULATION-------------')
        print('----------------------------------------------------\n')
        print('start date:', kwargs['start_date'])
        print('product id:', kwargs['product_id'])

        user = User.get_system_user()

        q = Q(recount_required_date__isnull=True, end_date__isnull=True)
        q &= Q(pk=kwargs['product_id']) if kwargs['product_id'] else Q()

        for product in Product.objects.filter(q):
            if kwargs['start_date']:
                start_date = datetime.strptime(kwargs['start_date'], '%Y-%m-%d').date()
            else:
                start_date = ProductCalculation.get_max_calculation_date(product)

            if start_date >= datetime.today().date():
                logger.info(f'product {product} up to date')
                continue

            logger.info(f'Calculating product: {product}')

            LoanCalculation(product.pk, user).calculate(start_date=start_date)

        print('--------------------DONE---------------------\n')
