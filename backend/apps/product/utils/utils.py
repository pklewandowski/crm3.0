import datetime
import decimal

from django.db import transaction
from django.db.models import Min

from apps.document.models import Document, DocumentAttribute, DocumentTypeAttribute, \
    DocumentTypeAccounting, DocumentTypeStatus, DocumentTypeAttributeMapping
from apps.document.view_base import DocumentException
from apps.hierarchy.models import Hierarchy
from apps.notification.utils import Notification
from apps.product import ANNEX_STATUS
from apps.product.base import ProductActionManager
from apps.product.models import Product, ProductInterest, ProductInterestType, ProductAccounting, \
    ProductAction, ProductStatusTrack, ProductTypeStatus, ProductTypeProcessFlow, \
    INSTALMENT_INTEREST_CAPITAL_TYPE_CALC_SOURCE_DEFAULT
from apps.product.utils.schedule_utils import ProductScheduleUtils
from apps.user.models import User
from apps.user_func.client.models import Client


class ProductException(Exception):
    pass


class ProductUtils:
    @staticmethod
    def change_status(product, status, user, effective_date=None, reason=None):
        if not user:
            raise AttributeError('[DocumentApi.change_status]: [user] parameter not defined')

        if isinstance(status, ProductTypeStatus):
            product_status = status

        elif type(status).__name__ in ('int', 'str'):
            product_status = ProductTypeStatus.objects.get(pk=status)

        else:
            raise TypeError(
                '[DocumentApi.change_status]: status parameter of incorrect type. Can be either [DocumentTypeStatus], or [int] or [str]')

        ProductStatusTrack.objects.create(
            product=product,
            status=product_status,
            reason=reason,
            created_by=user,
            effective_date=effective_date if effective_date else datetime.datetime.now()
        )

        product.status = product_status
        product.save()

        return product_status

    @staticmethod
    def calculate_balance(data):
        return data['capital_not_required'] + data['commission_not_required'] + data['interest_for_delay_required'] + \
            data['required_liabilities_sum'] + data['cost'] - \
            data['instalment_overpaid']

    @staticmethod
    def get_available_statuses(status):
        if not status:
            return
        return ProductTypeProcessFlow.objects.filter(status=status).order_by('sq')


class LoanUtils:
    @staticmethod
    def get_mapped_attributes(document):
        mapping = {}

        for i in DocumentTypeAttributeMapping.objects.filter(type=document.type):
            try:
                value = DocumentAttribute.objects.get(document_id=document.pk, attribute=i.attribute).value
            except DocumentAttribute.DoesNotExist:
                value = i.default_value
            mapping[i.mapped_name] = {
                'id': i.attribute.pk if i.attribute else None,
                'value': value,
                'required': i.is_required
            }

        return mapping

    @staticmethod
    def get_document_owner(document):
        row_sq = DocumentAttribute.objects.filter(document_id=document.pk, value='1',
                                                  attribute=DocumentTypeAttribute.objects.filter(pk=393)).aggregate(
            Min('row_sq'))
        u = DocumentAttribute.objects.get(document_id=document.pk,
                                          attribute=DocumentTypeAttribute.objects.filter(pk=251),
                                          row_sq=row_sq['row_sq__min'])
        if u:
            try:
                return Client.objects.get(pk=int(u.value))
            except Client.DoesNotExist:
                return None
        else:
            return None

    @staticmethod
    def _get_mapping(document, empty=False):
        mapping = LoanUtils.get_mapped_attributes(document)

        for i in mapping.values():
            if not empty and i["required"] and not i["value"]:
                raise ProductException(
                    'Brak wymaganych danych do utworzenia pożyczki %s' %
                    str([k for k in mapping.keys() if (mapping[k]["required"] and not mapping[k]["value"])])
                )

        return mapping

    @staticmethod
    def _create_product(user, document, mapping):
        product = Product()

        product.start_date = datetime.datetime.strptime(mapping['START_DATE']['value'], '%Y-%m-%d').date()
        if product.start_date > datetime.date.today():
            raise ProductException(f'Produkt może być utworzony dopiero w dniu daty startu: {product.start_date}')

        product.creditor = Hierarchy.objects.get(pk=mapping['CREDITOR']["value"])
        product.document = document
        product.type = document.type
        product.agreement_no = document.code
        product.creation_user = user
        product.creation_date = datetime.datetime.now()

        product.value = decimal.Decimal(mapping['VALUE']["value"])
        product.capital_net = decimal.Decimal(mapping['CAPITAL_NET']["value"] or 0)
        product.commission = decimal.Decimal(
            mapping['COMMISSION']["value"] or 0) if 'COMMISSION' in mapping else decimal.Decimal(0.0)
        product.instalment_capital = decimal.Decimal(mapping['INSTALMENT_CAPITAL']["value"] or 0) \
            if 'INSTALMENT_CAPITAL' in mapping else decimal.Decimal(0.0)
        product.instalment_commission = decimal.Decimal(mapping['INSTALMENT_COMMISSION']["value"] or 0) \
            if 'INSTALMENT_COMMISSION' in mapping else decimal.Decimal(0.0)
        product.instalment_interest_rate = decimal.Decimal(mapping['INSTALMENT_INTEREST_RATE']["value"] or 0) \
            if 'INSTALMENT_INTEREST_RATE' in mapping else decimal.Decimal(0.0)

        product.client = Client.objects.get(user=document.owner)

        # product.creditor_bank_account = mapping['CREDITOR_BANK_ACCOUNT']
        product.debtor_bank_account = mapping['DEBTOR_BANK_ACCOUNT']["value"]

        # liczba dni karencji do rozpoczęcia naliczania odsetek za opóźnienie
        product.grace_period = decimal.Decimal(
            mapping['GRACE_PERIOD']["value"] or 0) if 'GRACE_PERIOD' in mapping else decimal.Decimal(0.0)
        product.debt_collection_fee_period = decimal.Decimal(mapping['DEBT_COLLECTION_FEE_PERIOD'][
                                                                 'value']) if 'DEBT_COLLECTION_FEE_PERIOD' in mapping else decimal.Decimal(
            0.0)
        product.status = ProductTypeStatus.objects.get(is_initial=True)
        product.capital_type_calc_source = \
            mapping['INSTALMENT_INTEREST_CAPITAL_TYPE_CALC_SOURCE'][
                'value'] if 'INSTALMENT_INTEREST_CAPITAL_TYPE_CALC_SOURCE' in mapping else INSTALMENT_INTEREST_CAPITAL_TYPE_CALC_SOURCE_DEFAULT

        interest_for_delay_type_use_list = ['BOTH', 'MIN', 'MAX', 'BOTH']

        interest_for_delay_type_use = 0
        if 'INTEREST_FOR_DELAY_RATE' in mapping and mapping['INTEREST_FOR_DELAY_RATE']['id']:
            interest_for_delay_type_use |= 1

        if 'INTEREST_FOR_DELAY_RATE_MAX' in mapping and mapping['INTEREST_FOR_DELAY_RATE_MAX']['id']:
            interest_for_delay_type_use |= 2
        product.interest_for_delay_rate_use = interest_for_delay_type_use_list[interest_for_delay_type_use]
        product.interest_for_delay_calculation_add_value = \
            decimal.Decimal((mapping['INTEREST_FOR_DELAY_CALCULATION_ADD_VALUE'][
                                 'value'] or 0)) if 'INTEREST_FOR_DELAY_CALCULATION_ADD_VALUE' in mapping else decimal.Decimal(
                0.0)

        product.interest_for_delay_type = int(mapping['INTEREST_FOR_DELAY_TYPE']['value'])

        return product

    @staticmethod
    def _set_product_initial_status(product):
        ProductStatusTrack.objects.create(
            product=product,
            status=product.status,
            created_by=product.creation_user,
            effective_date=product.start_date,
            creation_date=datetime.datetime.now(),
            reason='Product creation',
            is_initial=True
        )

    @staticmethod
    def _process_annex(user, document, mapping):
        try:
            annex_status = ProductTypeStatus.objects.get(type=document.type, code=ANNEX_STATUS)
            ProductUtils.change_status(product=document.annex.product,
                                       status=annex_status,
                                       user=user,
                                       effective_date=mapping['START_DATE']['value']
                                       )
        except DocumentTypeStatus.DoesNotExist:
            raise DocumentException('Brak zdefiniowanego statusu dla umowy aneksowanej: %s' % ANNEX_STATUS)

    @staticmethod
    def _create_interest(product, mapping):
        ProductInterest.objects.create(product=product,
                                       start_date=product.start_date,
                                       delay_rate=decimal.Decimal(mapping['INTEREST_FOR_DELAY_RATE'][
                                                                      "value"] or 0 if 'INTEREST_FOR_DELAY_RATE' in mapping else 0),
                                       delay_max_rate=decimal.Decimal(mapping['INTEREST_FOR_DELAY_RATE_MAX'][
                                                                          "value"] or 0 if 'INTEREST_FOR_DELAY_RATE_MAX' in mapping else 0),
                                       statutory_rate=decimal.Decimal(mapping['INSTALMENT_INTEREST_RATE'][
                                                                          "value"] or 0 if 'INSTALMENT_INTEREST_RATE' in mapping else 0),
                                       type=ProductInterestType.objects.get(pk=mapping['INTEREST_FOR_DELAY_TYPE'][
                                                                                   "value"] or 1 if 'INSTALMENT_INTEREST_RATE' in mapping else 1)
                                       if 'INTEREST_FOR_DELAY_TYPE' in mapping else ProductInterestType.get_default())

    @staticmethod
    def _create_schedule(product, mapping):
        ProductScheduleUtils.generate_schedule(
            product=product,
            schedule_section=mapping['SCHEDULE_SECTION']["id"] if 'SCHEDULE_SECTION' in mapping else None,
            instalment_capital=decimal.Decimal(
                mapping['INSTALMENT_CAPITAL']["value"] or 0 if 'INSTALMENT_CAPITAL' in mapping else 0),
            instalment_interest=decimal.Decimal(
                mapping['INSTALMENT_INTEREST']["value"] or 0 if 'INSTALMENT_INTEREST' in mapping else 0),
            instalment_commission=decimal.Decimal(
                mapping['INSTALMENT_COMMISSION']["value"] or 0 if 'INSTALMENT_COMMISSION' in mapping else 0),
            instalment_number=int(mapping['INSTALMENT_NUMBER']["value"])
        )

    @staticmethod
    def _create_accounting(product):
        for idx, i in enumerate(
                DocumentTypeAccounting.objects.filter(document_type=product.document.type).order_by('sq')):
            ProductAccounting.objects.create(product=product, accounting_type=i.accounting_type, sq=idx + 1)

    @staticmethod
    @transaction.atomic()
    def create_loan(user, id):
        document = Document.objects.get(pk=id)

        try:
            product = Product.objects.get(document=document)
            return product.pk
        except Product.DoesNotExist:
            pass

        mapping = LoanUtils._get_mapping(document=document)

        if document.annex:
            LoanUtils._process_annex(user=user, document=document, mapping=mapping)

        product = LoanUtils._create_product(user=user, document=document, mapping=mapping)
        product.save()

        LoanUtils._set_product_initial_status(product=product)
        LoanUtils._create_schedule(product=product, mapping=mapping)
        LoanUtils._create_interest(product=product, mapping=mapping)
        LoanUtils._create_accounting(product=product)

        return product.pk

    @staticmethod
    def _generate_action(user, id_product, id_action):
        pam = ProductActionManager(
            id_product=id_product,
            id_action=id_action,
            user=user
        )

        ds = pam.get_datasource()

        # TODO: W funkcji product:calc:calculateLoan jest bardzo podobnie. Zrobić jedną funkcją

        ProductAction.objects.create(
            product=pam.product,
            action=pam.action,
            name=pam.action.name,
            action_date=datetime.datetime.now(),
            created_by=user,
            datasource=ds,
            action_execution_date=datetime.date.today()
        )

    @staticmethod
    def generate_clause(user, id):
        document = Document.objects.get(pk=id)
        product = None

        try:
            product = Product.objects.get(document=document)
        except Product.DoesNotExist:
            pass

        if not product:
            return

        LoanUtils._generate_action(user=user, id_product=product.pk, id_action=12)  # Wniosek o klauzulę
        Notification(user_list=User.objects.filter(
            groups__name__in=['WDK_TEREN', 'WDK_SPECJALISTA', 'WDK_PRAWNIK', 'WDK_OPIEKUN_POSP']).distinct(),
                     template_code='PRODUCT_ACTION',
                     params={"CRM_ID": product.document.code,
                             "DATE": '{:%Y-%m-%d}'.format(datetime.date.today()),
                             "ACTION_NAME": "Wniosek o klauzulę"
                             }
                     ).register()

    @staticmethod
    def generate_bailiff_application(user, id):
        document = Document.objects.get(pk=id)
        product = None

        try:
            product = Product.objects.get(document=document)
        except Product.DoesNotExist:
            pass

        if not product:
            return

        LoanUtils._generate_action(user=user, id_product=product.pk, id_action=9)  # Komornik - wniosek o kwotę
        Notification(user_list=User.objects.filter(
            groups__name__in=['WDK_TEREN', 'WDK_SPECJALISTA', 'WDK_PRAWNIK', 'WDK_OPIEKUN_POSP']).distinct(),
                     template_code='PRODUCT_ACTION',
                     params={"CRM_ID": product.document.code,
                             "DATE": '{:%Y-%m-%d}'.format(datetime.date.today()),
                             "ACTION_NAME": "Wniosek o wszczęcie egzekucji"
                             }
                     ).register()
