from django.core.management import BaseCommand
from apps.document.models import Document
from apps.product.utils.utils import LoanUtils
from apps.user.models import User


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        user = User.objects.get(pk=1)

        for i in Document.objects.raw(
                """
                SELECT dd.*
                    FROM crm.document dd,
                      crm.rsc_01_pozyczka pp
                    WHERE dd.id=pp.ref_id
                    AND NOT exists(SELECT FROM product pr WHERE pr.id_document=dd.id)
        """):
            LoanUtils.create_loan(user, i.pk)

