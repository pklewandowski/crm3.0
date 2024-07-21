from django.core.management.base import BaseCommand

from apps.document.models import Document
from apps.product.utils.utils import LoanUtils
from apps.user.models import User


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        exceptions = (1892, 1298)
        user = User.objects.get(pk=1)

        for d in Document.objects.raw('SELECT dd.* FROM crm.document dd, crm.rsc_01_pozyczka pp WHERE pp.ref_id = dd.id'):
            if d.pk in exceptions:
                continue
            LoanUtils.create_loan(user, d.pk)
