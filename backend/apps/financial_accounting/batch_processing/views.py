from django.http import HttpResponse
from django.db import transaction

from apps.financial_accounting.batch_processing.models import File
from apps.financial_accounting.transaction.models import Transaction


@transaction.atomic()
def add(request):

    # ld = LoaderMT940()
    # files = ld.get_file_list()
    #
    # for f in files:
    #     try:
    #         File.objects.get(name=f)
    #         continue
    #     except File.DoesNotExist:
    #         pass
    #
    #     transactions = ld.load(f)
    #     File.objects.create(
    #         loader_name=ld.type,
    #         name=f,
    #         records=len(transactions)
    #     )
    #
    #     Transaction.objects.bulk_create(transactions)

    # ld.account_products()

    return HttpResponse('add')


@transaction.atomic
def edit(request, id):
    return HttpResponse('edit')


def list(request):
    return HttpResponse('list')
