import datetime

import pytest

from apps.product.models import ProductInterestGlobal


@pytest.mark.django_db
class TestProductInterestGlobal:
    def test_empty_global_interest_list(self):
        ProductInterestGlobal.interest_list = None
        interest = ProductInterestGlobal.get_for(datetime.date(2024, 5, 10))

        assert len(ProductInterestGlobal.interest_list) == 0
        assert interest[0] == 0
        assert interest[1] == 0

    def test_product_interest_for_out_older_date(self, fix_product_interest_global):
        ProductInterestGlobal.interest_list = None
        interest = ProductInterestGlobal.get_for(datetime.date(2023, 1, 1))

        assert len(ProductInterestGlobal.interest_list) == 17
        assert interest[0] == 0.2050
        assert interest[1] == 0

    def test_product_interest_for_inrange_date(self, fix_product_interest_global):
        ProductInterestGlobal.interest_list = None
        interest = ProductInterestGlobal.get_for(datetime.date(2024, 5, 10))

        assert len(ProductInterestGlobal.interest_list) == 17
        assert interest[0] == 0.1850
        assert interest[1] == 16

    def test_product_interest_for_out_greater_date(self, fix_product_interest_global):
        ProductInterestGlobal.interest_list = None
        interest = ProductInterestGlobal.get_for(datetime.date(2024, 11, 10))

        assert len(ProductInterestGlobal.interest_list) == 17
        assert interest[0] == 0.1850
        assert interest[1] == 18
