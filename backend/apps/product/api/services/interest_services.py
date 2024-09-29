import datetime

from django.conf import settings

from apps.product.calc import CalculateLoan
from apps.product.models import ProductInterestGlobal, Product, ProductInterest, ProductInterestType


def save_interest_global(interest_global: ProductInterestGlobal, user):
    for product in Product.objects.filter(status__is_closing_process=False, start_date__lte=interest_global.start_date):
        start_date = interest_global.start_date if interest_global.start_date >= product.start_date else product.start_date

        try:
            interest = product.interest_set.get(start_date=interest_global.start_date)

            interest.statutory_rate = product.instalment_interest_rate
            interest.delay_rate = interest_global.interest_for_delay_rate
            interest.delay_max_rate = interest_global.interest_max_for_delay_rate
            interest.is_set_globally = True

            interest.save()

        except ProductInterest.DoesNotExist:
            ProductInterest.objects.create(
                product=product,
                start_date=interest_global.start_date,
                statutory_rate=product.instalment_interest_rate,
                delay_rate=interest_global.interest_for_delay_rate,
                delay_max_rate=interest_global.interest_max_for_delay_rate,
                type=ProductInterestType.objects.get(is_default=True),
                is_set_globally=True
            )

        product.recount_required_date = min(start_date, product.recount_required_date or settings.INFINITY_DATE)
        product.recount_required_date_creation_marker = datetime.datetime.now()
        product.save()

def delete_interest_global(interest_global: ProductInterestGlobal):
    for product in Product.objects.filter(status__is_closing_process=False, start_date__lte=interest_global.start_date):
        interest = product.interest_set.filter(start_date=interest_global.start_date, is_set_globally=True)

        if interest:
            start_date = interest_global.start_date if interest_global.start_date >= product.start_date else product.start_date
            interest.delete()

            product.recount_required_date = start_date
            product.recount_required_date_creation_marker = datetime.datetime.now()
            product.save()



