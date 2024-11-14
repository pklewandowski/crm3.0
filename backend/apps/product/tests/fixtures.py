import datetime

import pytest

from apps.document.models import DocumentTypeAccountingType, DocumentTypeAccounting
from apps.product.models import ProductSchedule, ProductTypeStatus, Product, ProductInterest, ProductInterestType, \
    ProductStatusTrack, ProductInterestGlobal


def _product_status_track(user, product, status):
    return ProductStatusTrack.objects.create(**{
        "effective_date": "2023-12-18 23:00:00.000000 +00:00",
        "creation_date": "2024-09-21 12:28:54.307983 +00:00",
        "reason": "Product creation",
        "created_by": user,
        "product": product,
        "status": status,
        "is_initial": True
    })


def _product_schedule(product):
    schedule_data = [
        {
            "maturity_date": datetime.datetime.strptime("2024-01-19", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3847.91,
            "instalment_capital": 652.09,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-02-19", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3842.92,
            "instalment_capital": 657.08,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-03-19", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3590.29,
            "instalment_capital": 909.71,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-04-19", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3830.95,
            "instalment_capital": 669.05,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-05-20", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3825.83,
            "instalment_capital": 674.17,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-06-19", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3697.43,
            "instalment_capital": 802.57,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-07-19", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3691.49,
            "instalment_capital": 808.51,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-08-19", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3808.36,
            "instalment_capital": 691.64,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-09-19", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3803.08,
            "instalment_capital": 696.92,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-10-21", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3920.26,
            "instalment_capital": 579.74,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-11-19", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3548.59,
            "instalment_capital": 951.41,
            "instalment_commission": 0.00,
            "instalment_total": 4500.00
        },
        {
            "maturity_date": datetime.datetime.strptime("2024-12-19", '%Y-%m-%d').date(),
            "product": product,
            "instalment_interest": 3663.92,
            "instalment_capital": 495307.11,
            "instalment_commission": 0.00,
            "instalment_total": 498971.03
        }

    ]

    for i in schedule_data:
        ProductSchedule.objects.create(**i)


@pytest.fixture
def fix_product_type_status(fix_document_type):
    return ProductTypeStatus.objects.create(
        id=1,
        name="Pożyczka uruchomiona",
        code="UP",
        is_initial=True,
        is_active=True,
        is_alternate=False,
        is_closing_process=False,
        sq=1,
        type=fix_document_type,
        color="ffffff"
    )


@pytest.fixture
def fix_product_interest_global(fix_user, fix_document_type):
    for i in [
        {
            "start_date": "2020-01-01",
            "creation_date": "2024-07-09 09:05:52.310378 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.0700,
            "interest_max_for_delay_rate": 0.1400
        },
        {
            "start_date": "2020-03-18",
            "creation_date": "2024-07-09 09:15:00.097111 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.0900,
            "interest_max_for_delay_rate": 0.1300
        },
        {
            "start_date": "2020-04-09",
            "creation_date": "2024-07-09 09:16:44.920973 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.0800,
            "interest_max_for_delay_rate": 0.1200
        },
        {
            "start_date": "2020-05-29",
            "creation_date": "2024-07-09 09:18:26.683636 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.0720,
            "interest_max_for_delay_rate": 0.1120
        },
        {
            "start_date": "2021-10-07",
            "creation_date": "2024-07-09 09:33:30.093627 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.0800,
            "interest_max_for_delay_rate": 0.1200
        },
        {
            "start_date": "2021-11-04",
            "creation_date": "2024-07-09 09:34:01.856203 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.0950,
            "interest_max_for_delay_rate": 0.1350
        },
        {
            "start_date": "2021-12-09",
            "creation_date": "2024-07-09 09:34:30.848271 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.1050,
            "interest_max_for_delay_rate": 0.1450
        },
        {
            "start_date": "2022-01-05",
            "creation_date": "2024-07-09 09:34:57.282398 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.1150,
            "interest_max_for_delay_rate": 0.1550
        },
        {
            "start_date": "2022-02-09",
            "creation_date": "2024-07-09 09:35:26.188183 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.1250,
            "interest_max_for_delay_rate": 0.1650
        },
        {
            "start_date": "2022-03-09",
            "creation_date": "2024-07-09 09:35:53.374822 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.1400,
            "interest_max_for_delay_rate": 0.1800
        },
        {
            "start_date": "2022-04-07",
            "creation_date": "2024-07-09 09:36:12.884893 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.1600,
            "interest_max_for_delay_rate": 0.2000
        },
        {
            "start_date": "2022-05-06",
            "creation_date": "2024-07-09 09:36:45.239205 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.1750,
            "interest_max_for_delay_rate": 0.2150
        },
        {
            "start_date": "2022-06-09",
            "creation_date": "2024-07-09 09:38:49.188193 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.1900,
            "interest_max_for_delay_rate": 0.2300
        },
        {
            "start_date": "2022-07-08",
            "creation_date": "2024-07-09 09:39:25.965556 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.2000,
            "interest_max_for_delay_rate": 0.2400
        },
        {
            "start_date": "2022-09-08",
            "creation_date": "2024-07-09 09:40:02.269420 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.2050,
            "interest_max_for_delay_rate": 0.2450
        },
        {
            "start_date": "2023-09-07",
            "creation_date": "2024-07-09 09:41:03.784500 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.1900,
            "interest_max_for_delay_rate": 0.2300
        },
        {
            "start_date": "2023-10-05",
            "creation_date": "2024-07-09 09:41:29.666305 +00:00",
            "created_by": fix_user,
            "document_type": fix_document_type,
            "interest_for_delay_rate": 0.1850,
            "interest_max_for_delay_rate": 0.2250
        }
    ]:
        ProductInterestGlobal.objects.create(**i)


@pytest.fixture
def fix_product_interest_type():
    return ProductInterestType.objects.create(**{
        "name": "Odsetki od całości do końca umowy [typ 3]",
        "code": "3",
        "sq": 3,
        "is_default": True
    })


@pytest.fixture
def fix_document_type_accounting_type(fix_document_type):
    accounting_type = [
        {
            "pk": 1,
            "name": "Koszty",
            "code": "COST",
            "description": "Koszty",
            "direction": 1,
            "is_editable": True,
            "is_accounting_order": True,
            "due_day_accounting_only": False,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 2
        },
        {
            "pk": 2,
            "name": "Wpłata środków",
            "code": "PAYMENT",
            "description": "Wpłata środków",
            "direction": -1,
            "is_editable": True,
            "is_accounting_order": False,
            "due_day_accounting_only": False,
            "min_value": None,
            "subtypes": {},
            "sq": 1

        },
        {
            "pk": 3,
            "name": "Kapitał wymagalny",
            "code": "CAP_REQ",
            "description": "Kapitał wymagalny",
            "direction": 1,
            "is_editable": False,
            "is_accounting_order": True,
            "due_day_accounting_only": False,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 0

        },
        {
            "pk": 4,
            "name": "Kapitał niewymagalny",
            "code": "CAP_NOT_REQ",
            "description": "Kapitał niewymagalny",
            "direction": 1,
            "is_editable": False,
            "is_accounting_order": True,
            "due_day_accounting_only": True,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 0

        },
        {
            "pk": 7,
            "name": "Wypłata środków",
            "code": "PAYOFF",
            "description": "Wypłata środków",
            "direction": 1,
            "is_editable": False,
            "is_accounting_order": False,
            "due_day_accounting_only": False,
            "min_value": None,
            "subtypes": {},
            "sq": 0

        },
        {
            "pk": 9,
            "name": "Odsetki",
            "code": "INTEREST_REQUIRED",
            "description": "Rata odsetkowa",
            "direction": 1,
            "is_editable": False,
            "is_accounting_order": True,
            "due_day_accounting_only": False,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 0

        },
        {
            "pk": 10,
            "name": "Prowizja niewymagalna",
            "code": "COMM_NOT_REQ",
            "description": "Prowizja niewymagalna",
            "direction": 1,
            "is_editable": False,
            "is_accounting_order": True,
            "due_day_accounting_only": True,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 0

        },
        {
            "pk": 11,
            "name": "Prowizja wymagalna",
            "code": "COMM_REQ",
            "description": "Prowizja wymagalna",
            "direction": 1,
            "is_editable": False,
            "is_accounting_order": True,
            "due_day_accounting_only": False,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 0

        },
        {
            "pk": 16,
            "name": "Umorzenie kapitału",
            "code": "REM_CAP",
            "description": "Umorzenie kapitału",
            "direction": -1,
            "is_editable": True,
            "is_accounting_order": False,
            "due_day_accounting_only": False,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 3

        },
        {
            "pk": 17,
            "name": "Umorzenie prowizji",
            "code": "REM_COMM",
            "description": "Umorzenie prowizji",
            "direction": -1,
            "is_editable": True,
            "is_accounting_order": False,
            "due_day_accounting_only": False,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 4

        },
        {
            "pk": 18,
            "name": "Umorzenie raty odsetkowej",
            "code": "REM_INTEREST",
            "description": "Umorzenie raty odsetkowej",
            "direction": -1,
            "is_editable": True,
            "is_accounting_order": False,
            "due_day_accounting_only": False,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 5

        },
        {
            "pk": 19,
            "name": "Umorzenie odsetek za opóźnienie",
            "code": "REM_INTEREST_REQUUIRED",
            "description": "Umorzenie odsetek za opóźnienie",
            "direction": -1,
            "is_editable": True,
            "is_accounting_order": False,
            "due_day_accounting_only": False,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 6
        },
        {
            "pk": 20,
            "name": "Umorzenie kosztów",
            "code": "REM_COST",
            "description": "Umorzenie kosztów",
            "direction": -1,
            "is_editable": True,
            "is_accounting_order": False,
            "due_day_accounting_only": False,
            "min_value": "0.00",
            "subtypes": {},
            "sq": 7
        }
    ]

    for i in accounting_type:
        DocumentTypeAccountingType.objects.create(**i)

@pytest.fixture
def fix_document_type_accounting(fix_document_type, fix_document_type_accounting_type):
    accounting = [
        {
            "pk": 255,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=1),
            "sq": 1

        },
        {
            "pk": 256,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=9),
            "sq": 2
        },
        {
            "pk": 257,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=3),
            "sq": 3
        },
        {
            "pk": 258,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=4),
            "sq": 4
        },
        {
            "pk": 259,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=7),
            "sq": 0
        },
        {
            "pk": 260,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=16),
            "sq": 0
        },
        {
            "pk": 261,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=17),
            "sq": 0
        },
        {
            "pk": 262,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=18),
            "sq": 0
        },
        {
            "pk": 263,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=19),
            "sq": 0
        },
        {
            "pk": 264,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=20),
            "sq": 0
        },
        {
            "pk": 265,
            "document_type": fix_document_type,
            "accounting_type": DocumentTypeAccountingType.objects.get(pk=2),
            "sq": 0
        }
    ]

    for i in accounting:
        DocumentTypeAccounting.objects.create(**i)


@pytest.fixture
def fix_product(
        fix_document_type,
        fix_product_type_status,
        fix_document,
        fix_document_type_accounting,
        fix_user,
        fix_client,
        fix_product_interest_type,
        fix_product_interest_global):
    product = Product.objects.create(
        document=fix_document,
        value=100000,
        client=fix_client,
        type=fix_document_type,
        start_date=datetime.datetime.strptime('2023-12-19', '%Y-%m-%d').date(),
        agreement_no='01/2023',
        status=fix_product_type_status,
        creation_user=fix_user,
        creation_date='2023-12-19'
    )

    _product_schedule(product=product)
    _product_status_track(user=fix_user, product=product, status=fix_product_type_status)

    ProductInterest.objects.create(**{
        "product": product,
        "start_date": "2023-12-19",
        "type": fix_product_interest_type,
        "is_set_globally": False,
        "delay_max_rate": 0.0000,
        "delay_rate": 0.0000,
        "statutory_rate": 0.0900
    })

    return product
