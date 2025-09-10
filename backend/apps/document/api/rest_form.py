import json

from django.db.models import Q

from apps.document import utils as doc_utils
from apps.document.api.attribute_utils import AttributeUtils
from apps.document.api.utils import DocumentApiCredentials
from apps.document.models import Document, DocumentAttribute, DocumentTypeAttribute, DocumentTypeStatus
from apps.user.models import User
from py3ws.utils.utils import findkeys


class RestForm():
    def __init__(self):
        self.form_attributes = []

    pass

    def get_form(self):
        return self.form_attributes


class DocumentForm(RestForm):
    def __init__(self, document_type, instance, user):
        super().__init__()

        readonly = not DocumentApiCredentials.check_user_in_hierarchy(user=user,
                                                                      status=instance.status if instance else None)

        AttributeUtils().get_attributes(parent=None,
                                        document_type=document_type,
                                        level=self.form_attributes,
                                        type='FORM',
                                        status=instance.status if instance else doc_utils.get_initial_status(
                                            type=document_type),
                                        readonly=readonly
                                        )

        def set_annex(node):
            for i in node:
                if 'children' in i:
                    set_annex(i['children'])

                if i['code'] == 'annex':
                    if instance:
                        lov = []
                        if instance.annex:
                            lov.append({
                                "lov_label": '{code} z dn.: {day}, wartość: {value}'.format(
                                    code=instance.annex.code,
                                    day=instance.annex.product.start_date,
                                    value='{:,.2f}'.format(instance.annex.product.value).replace(',', ' ').replace('.',
                                                                                                                   ',')),
                                "lov_value": instance.annex.pk,
                                "lov_description": ''
                            })

                        lov.extend(
                            [{
                                "lov_label": '{code} z dn.: {day}, wartość: {value}'.format(code=j.code,
                                                                                            day=j.product.start_date,
                                                                                            value='{:,.2f}'.format(
                                                                                                j.product.value).replace(
                                                                                                ',', ' ').replace('.',
                                                                                                                  ',')),
                                "lov_value": j.pk,
                                "lov_description": ''
                            } for j in Document.objects.filter(
                                Q(owner=instance.owner, product__isnull=False, annexed_by__isnull=True)
                            ).exclude(Q(pk=instance.pk) | Q(status__code='ANX'))
                            ]
                        )

                        if lov:
                            i['lov'] = {"data": lov, "nullvalue": True}
                            return

                    i['lov'] = {"data": []}
                    return

        set_annex(self.form_attributes)
