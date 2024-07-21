# _*_ coding:utf-8 _*_
from pprint import pprint

from django.core.management.base import BaseCommand
from django.db import connection

from apps.document.models import Document, DocumentTypeAttribute, DocumentTypeSection, DocumentAttribute, DocumentTypeAttributeMapping, DocumentType


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def dictfetchone(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, cursor.fetchone()))



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        mapping = {i.attribute.pk: i.mapped_name for i in DocumentTypeAttributeMapping.objects.filter(type=DocumentType.objects.get(pk=1))}
        mapping[413] = 'REP'

        attributes = DocumentTypeAttribute.objects.filter(section=DocumentTypeSection.objects.get(pk=12))

        for d in Document.objects.raw('SELECT dd.* FROM crm.document dd, crm.rsc_01_pozyczka pp WHERE pp.ref_id = dd.id'):
            q = """
                SELECT nr_rachunku "DEBTOR_BANK_ACCOUNT", 
                       '' "CREDITOR_BANK_ACCOUNT",   
                       data_z_umowy_pozyczki "START_DATE",
                       '3' "INTEREST_TYPE",
                       '10' "INTEREST_PERCENT",
                       kapital_brutto "VALUE",
                       rata "INSTALMENT_VALUE",
                       liczba_rat "INSTALMENT_NUMBER",
                       nr_rep_firma "REP"                                                 
                  FROM crm.rsc_01_pozyczka pp 
                WHERE pp.ref_id = %s
                """ % d.pk
            with connection.cursor() as c:
                c.execute(q)
                result = dictfetchone(c)
                if result:
                    for a in attributes:
                        if a.pk in mapping:
                            try:
                                attr = DocumentAttribute.objects.get(document_id=d.pk, attribute=a)
                                val = result[mapping[a.pk]]
                                if val:
                                    attr.value = val
                                    attr.save()

                            except DocumentAttribute.DoesNotExist:
                                DocumentAttribute.objects.create(
                                    document_id=d.pk,
                                    attribute=a,
                                    value=result[mapping[a.pk]]
                                )
