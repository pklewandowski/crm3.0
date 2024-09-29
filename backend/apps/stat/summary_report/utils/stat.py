from apps.document.models import DocumentTypeAttribute


class Stat:
    pass
    # ATTRIBUTES = {
    #     'amount_granted_id': DocumentTypeAttribute.objects.get(code='1_2d241cb0dd7d4482b1156015b064f691').pk,  # 103
    #     'amount_requested_id': DocumentTypeAttribute.objects.get(code='1_bc8ed3b4a06548c1a0adc38cfa25baae').pk,  # 24,
    #     'commission_id': DocumentTypeAttribute.objects.get(code='1_cb42d402395f9d423aa5ec79c9af0e0d').pk,  # 444,
    #     'broker_id': DocumentTypeAttribute.objects.get(code='1_96d12f8f4eea41a6b7222d4a4ac1e95a').pk,  # 248
    #     'adviser_id': DocumentTypeAttribute.objects.get(code='1_7481de1bee294fd5a4b6bf9103e7fbf4').pk,  # 222
    #     'agreement_type_id': DocumentTypeAttribute.objects.get(code='1_0df32a2e0e25427e83c93bbc58628510').pk,  # 249
    # }
    #
    # @staticmethod
    # def dictfetchall(cursor):
    #     desc = cursor.description
    #     return [
    #         dict(zip([col[0] for col in desc], row))
    #         for row in cursor.fetchall()
    #     ]
