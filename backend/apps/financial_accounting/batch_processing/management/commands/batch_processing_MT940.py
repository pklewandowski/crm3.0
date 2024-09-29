# _*_ coding:utf-8 _*_
import logging
import os.path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.financial_accounting.batch_processing.loaders.loaderMT940 import LoaderMT940
from apps.financial_accounting.batch_processing.models import File
from apps.financial_accounting.transaction.models import Transaction
from apps.financial_accounting.utils import get_subsidiary_companies


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-p', '--path', action='store')
        parser.add_argument('-d', '--directory', action='store')

    def handle(self, *args, **kwargs):
        directory = kwargs.get('directory', '')
        path = kwargs.get('path', None)

        print('------------STARTING batch processing for MT940 files -------------')
        print('----------------------------------------------------\n')
        print('path: ', path)
        print('directory: ', directory)

        exceptions = ()
        ld = LoaderMT940(path)
        path = ld.path

        for subsidiary_company_code in get_subsidiary_companies().values():
            ld.path = os.path.join(path, subsidiary_company_code, directory)

            files = ld.get_file_list()

            for f in files:
                if f in exceptions:
                    continue

                with transaction.atomic():
                    try:
                        File.objects.get(name=f, type=ld.type, subsidiary_company_code=subsidiary_company_code)
                        logging.log(logging.INFO, f'file %s already exists: {f}')
                        print(f'file {f} already exists:')
                        continue

                    except File.DoesNotExist:
                        pass

                    file = File.objects.create(
                        type=ld.type,
                        name=f,
                        # records=len(transactions),
                        subsidiary_company_code=subsidiary_company_code
                    )

                    transactions = ld.load(f, file)
                    file.records = len(transactions)
                    file.save()

                    print(f'{subsidiary_company_code}/{f}: {len(transactions)} records processed.')

                    Transaction.objects.bulk_create(transactions)
