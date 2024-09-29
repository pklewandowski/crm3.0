import datetime
import os
import re
from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import Q

from apps.document.models import DocumentTypeAccountingType
from apps.financial_accounting.transaction.models import Transaction
from apps.product.models import Product, ProductCashFlow, CompanyBankTransactionFile
from .loaderAbstract import LoaderAbstract
from ...utils import get_subsidiary_companies


# {
#     'Nord finance 1 Sp. z o. o.': 'V7GL16EGE',
#     'Nord finance 2 Sp. z o. o.': 'R3K9XSKPR',
#     'Nord finance 3 Sp. z o. o.': 'R1FLIST0G',
#     'Nord finance SA': 'RP2LJ6VHK'
# }


class LoaderMT940(LoaderAbstract):
    SUBSIDIARY_COMPANIES = get_subsidiary_companies()

    def __init__(self, path=None):
        super().__init__()

        self.type = 'MT940'
        self.path = path if path else os.path.join(settings.BATCH_TRANSACTION_FILES_ROOT, self.type, '_incoming/')

        for k, v in self.SUBSIDIARY_COMPANIES.items():
            print(f'subsidiary company {k} code: {v}')
            os.makedirs(os.path.join(self.path, v), exist_ok=True)

    def clean(self, data):
        return data.replace('\n', ' ')

    def check_filename_format(self, filename):
        return filename.endswith('.txt')

    def process(self, filename, data, file):

        transactions = []

        for account_data in re.split('-\x03', data):
            bank_account = self._get_regex_value(regex="(:25:)(\w{2})(\d{26})", group=3, data=account_data, raise_error=False)
            if not bank_account:
                continue

            for idx, transaction_row in enumerate(re.split('\n', re.sub('(:61:)', '\n\g<1>', account_data))):
                try:
                    if transaction_row[0:4] != ':61:':
                        continue

                    transaction_no = self._get_regex_value(regex="(TNR:\s+)(\d+.\d+)", group=2, data=transaction_row)
                    if not transaction_no:
                        continue

                    transaction_type = self._get_regex_value(regex="(:61:\d{10})(C|D)", data=transaction_row, group=2, raise_error=True)

                    if transaction_type not in ['C', 'D']:
                        raise Exception('Niezgodny typ transakcji')

                    value = Decimal(self._get_regex_value(regex=r'(:61:\d*[a-zA-Z]+)(\d+,\d{2})', group=2, data=transaction_row, raise_error=True).replace(',', '.'))

                    transaction_date = datetime.datetime.strptime(self._get_regex_value(regex=r'(:61:)(\d{6})', group=2, data=transaction_row, raise_error=True), '%y%m%d')

                    accounting_date = datetime.datetime.strptime(
                        datetime.datetime.strftime(transaction_date, '%y') +
                        self._get_regex_value(regex=r'(:61:)(\d{6})(\d{4})', group=3, data=transaction_row, raise_error=True), '%y%m%d'
                    )

                    if transaction_type == 'C':
                        bank_account_from = self._get_regex_value(regex=r'(:86:.*)(\w{2}){0,1}(\d{26})', group=3, data=transaction_row)
                        bank_account_to = bank_account
                    else:
                        bank_account_from = bank_account
                        bank_account_to = self._get_regex_value(regex=r'(:86:.*)(\w{2}){0,1}(\d{26})', group=3, data=transaction_row)

                    v_account_iph = self._get_regex_value(regex=r'(:86:.*ID IPH:\s*)(XX)(\d{12})', group=3, data=transaction_row)

                    account_name_from = self._get_regex_value(regex=r'(:86:.*OD:\s*)(.*)(;)', group=2, data=transaction_row)
                    account_name_from = account_name_from[:500] if account_name_from else ''

                    account_name_to = self._get_regex_value(regex=r'(:86:.*DLA:\s*)(.*)(;)', group=2, data=transaction_row)
                    account_name_to = account_name_to[:500] if account_name_to else ''

                    title = self._get_regex_value(regex=r'(TYT.:)(.*)(;)', group=2, data=transaction_row)
                    title = (title[:500]).strip() if title else ''

                    if not bank_account_from or not bank_account_to or not v_account_iph:
                        continue

                    transaction = Transaction(
                        file=file,
                        account_from=bank_account_from,
                        account_to=bank_account_to,
                        account_name_from=account_name_from,
                        account_name_to=account_name_to,
                        v_account_iph=v_account_iph,
                        title=title,
                        value=value,
                        transaction_no=transaction_no,
                        transaction_date=transaction_date,
                        accounting_date=accounting_date,
                        source_filename=filename,
                        source_type=self.source_type,
                        source_name=file.subsidiary_company_code,
                        source_file_type=self.type
                    )

                    transactions.append(transaction)

                except Exception as e:
                    raise Exception(filename + ': transaction_block: ' + str(idx) + ': ' + str(e))

        return transactions

    @staticmethod
    def create_pcfs(product: Product, type, start_date=None):
        # pcfs - product cash flows
        pcfs = []
        trn = []

        if not product.debtor_bank_account:
            return

        iph = product.debtor_bank_account[-12:]
        if len(iph) != 12:
            raise Exception('BAD IPH: %s PRODUCT: %s' % (iph, product.pk))

        q = Q(
            v_account_iph=iph,
            source_name=product.creditor.bank_transaction_file.base_dir if product.creditor else '',
            accounting_date__gte=start_date or product.start_date,
            destination_id__isnull=True
        )

        if product.end_date:
            q &= Q(accounting_date__lte=product.end_date)

        for i in Transaction.objects.filter(q):
            try:
                ProductCashFlow.objects.get(product=product, transaction_uid=f'{i.source_name}_{i.transaction_no}')
                continue
            except ProductCashFlow.DoesNotExist:
                pass
            pcfs.append(ProductCashFlow(
                product=product,
                transaction_uid=f'{i.source_name}_{i.transaction_no}',
                description=f'[MT940] source:{i.source_name}, trn_no:{i.transaction_no}, file: {i.source_filename}',
                type=type,
                value=i.value,
                # Data efektywna (czyli data rozliczenia do algorytmu) jest taka jak data zaksięgowania
                cash_flow_date=i.accounting_date,
                accounting_date=i.accounting_date,
                editable=False,
                entry_source='FILE'
            ))

            i.destination_id = product.pk
            trn.append(i)

        if trn:
            Transaction.objects.bulk_update(trn, ['destination_id'])
        if pcfs:
            ProductCashFlow.objects.bulk_create(pcfs)

    # rozksięgowanie transakcji dla produktów
    @staticmethod
    def account_products(product=None, start_date=None, reset=False):

        # todo: DRUT!!!!!!!!!!! KONIECZNE POPRAWIC JAK NAJSZYBCIEJ!!!!!!!!!!!!!!!!!!!!!DODAĆ typ produktu przy .all()
        products = [product] if product else Product.objects.all()

        with transaction.atomic():
            for product in products:
                if reset:
                    ProductCashFlow.objects.filter(product=product, entry_source='FILE').delete()
                    Transaction.objects.filter(destination_id=product.pk).update(destination_id=None)

                LoaderMT940.create_pcfs(product=product, type=DocumentTypeAccountingType.objects.get(code='PAYMENT'), start_date=start_date)
