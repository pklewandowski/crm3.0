from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.product.calc import CalculateLoan
from apps.product.models import Product
from apps.user.models import User


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

        q = Q(pk=kwargs['product_id']) if kwargs['product_id'] else Q()

        for product in Product.objects.filter(q):
            print(f'Calculating product: {product}')
            CalculateLoan(product.pk, user).calculate(
                start_date=kwargs['start_date'] if kwargs['start_date'] else None,
            )

        print('--------------------DONE---------------------\n')
