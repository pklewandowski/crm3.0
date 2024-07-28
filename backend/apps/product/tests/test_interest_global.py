import datetime

import pytest

from apps.product.models import ProductInterestGlobal


@pytest.fixture
def global_interest_list(user, document_type):
    ProductInterestGlobal.objects.create(
        start_date=datetime.date(2024, 1, 20),
        interest_for_delay_rate=10.0,
        interest_max_for_delay_rate=15.0,
        created_by=user,
        document_type=document_type
    )

    ProductInterestGlobal.objects.create(
        start_date=datetime.date(2024, 2, 12),
        interest_for_delay_rate=11.0,
        interest_max_for_delay_rate=16.0,
        created_by=user,
        document_type=document_type
    )

    ProductInterestGlobal.objects.create(
        start_date=datetime.date(2024, 6, 10),
        interest_for_delay_rate=12.0,
        interest_max_for_delay_rate=17.0,
        created_by=user,
        document_type=document_type
    )

    ProductInterestGlobal.objects.create(
        start_date=datetime.date(2024, 8, 14),
        interest_for_delay_rate=13.0,
        interest_max_for_delay_rate=18.0,
        created_by=user,
        document_type=document_type
    )


@pytest.mark.django_db
class TestProductInterestGlobal:
    def test_empty_global_interest_list(self):
        ProductInterestGlobal.interest_list = None
        interest = ProductInterestGlobal.get_for(datetime.date(2024, 5, 10))

        assert len(ProductInterestGlobal.interest_list) == 0
        assert interest[0] == 0
        assert interest[1] == 0

    def test_product_interest_for_out_older_date(self, global_interest_list):
        ProductInterestGlobal.interest_list = None
        interest = ProductInterestGlobal.get_for(datetime.date(2023, 1, 1))

        assert len(ProductInterestGlobal.interest_list) == 4
        assert interest[0] == 0
        assert interest[1] == 0

    def test_product_interest_for_inrange_date(self, global_interest_list):
        ProductInterestGlobal.interest_list = None
        interest = ProductInterestGlobal.get_for(datetime.date(2024, 5, 10))

        assert len(ProductInterestGlobal.interest_list) == 4
        assert interest[0] == 11
        assert interest[1] == 16

    def test_product_interest_for_out_greater_date(self, global_interest_list):
        ProductInterestGlobal.interest_list = None
        interest = ProductInterestGlobal.get_for(datetime.date(2024, 11, 10))

        assert len(ProductInterestGlobal.interest_list) == 4
        assert interest[0] == 13
        assert interest[1] == 18
