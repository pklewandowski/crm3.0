import datetime
import json

from django.db.models import Q

from apps.document.models import DocumentTypeStatus, DocumentStatusTrack, DocumentStatusCourse, DocumentAttribute, DocumentTypeAttribute
from py3ws.utils import utils as py3ws_utils


class DocumentApiUtils:
    @staticmethod
    def change_status(document, status, user, effective_date=None, reason=None):
        if not user:
            raise AttributeError('[DocumentApi.change_status]: [user] parameter not defined')

        if isinstance(status, DocumentTypeStatus):
            document_status = status

        elif type(status).__name__ in ('int', 'str'):
            document_status = DocumentTypeStatus.objects.get(pk=status)

        else:
            raise TypeError('[DocumentApi.change_status]: status parameter of incorrect type. Can be either [DocumentTypeStatus], or [int] or [str]')

        DocumentStatusTrack.objects.create(
            document=document,
            status=document_status,
            reason=reason,
            created_by=user,
            effective_date=effective_date if effective_date else datetime.datetime.now()

        )
        DocumentStatusCourse.objects.create(
            document=document,
            status=document_status,
            created_by=user,
            effective_date=effective_date if effective_date else datetime.datetime.now()
        )

        document.status = document_status
        document.save()

        return document_status

    @staticmethod
    def delete_document_attribute_with_children(document, id_section, idx=None):
        attribute = DocumentTypeAttribute.objects.get(pk=id_section)

        def f(attribute):
            children = DocumentTypeAttribute.objects.filter(parent=attribute)
            if children:
                for i in children:
                    f(i)

            q = Q(attribute=attribute, document_id=document.pk)
            if idx:
                q &= Q(row_sq__gte=idx)
            DocumentAttribute.objects.filter(q).delete()

        f(attribute)

    @staticmethod
    def save_repeatable_section(document, key, value, idx=None, ver: dict = None):
        #  if not value, then delete all entries
        DocumentApiUtils.delete_document_attribute_with_children(document, key, idx)
        for key, val in value.items():
            for _idx, _val in enumerate(val):
                DocumentApiUtils.save_value(document, key, _val, _idx, ver[key] if key in ver else None)

    @staticmethod
    def save_value(document, key, value, idx=None, ver: dict = None):
        v = json.dumps(value['value']) if type(value['value']) in [dict, tuple, list] else value['value']
        m = value['meta']
        try:
            attr = DocumentAttribute.objects.get(attribute__pk=key, document_id=document.pk, row_sq=idx)
            # if item is not editable for given document status then do nothing
            # todo: also on frontend side, if item is not editable but ie. calculable or modified by action, raise error that it cannot be modified
            if ver and not ver['E']:
                return

            if attr.value == v and attr.value_data_meta == m:
                return

            attr.value = v
            attr.value_data_meta = m
            attr.save()

        except DocumentAttribute.DoesNotExist:
            DocumentAttribute.objects.create(
                document_id=document.pk,
                attribute=DocumentTypeAttribute.objects.get(pk=key),
                value=v,
                value_data_meta=m,
                row_sq=idx
            )

    @staticmethod
    def trigger_action(user, document):
        if document.status.action_class and document.status.action:
            cl = py3ws_utils.get_class(document.status.action_class)()
            return getattr(cl, document.status.action)(user, document.pk)

    @staticmethod
    def _copy_items(item_list, document):
        for k, v in item_list.items():
            try:
                attribute_from = DocumentTypeAttribute.objects.get(pk=k)
                attribute_to = DocumentTypeAttribute.objects.get(pk=v)
            except DocumentTypeAttribute.DoesNotExist:
                continue

            try:
                item_from_value = DocumentAttribute.objects.get(attribute=attribute_from, document_id=document.pk).value
            except DocumentAttribute.DoesNotExist:
                continue
            try:
                item_to = DocumentAttribute.objects.get(attribute=attribute_to, document_id=document.pk)
                item_to.value = item_from_value

            except DocumentAttribute.DoesNotExist:
                item_to = DocumentAttribute(
                    document_id=document.pk,
                    attribute=attribute_to,
                    value=item_from_value
                )
            item_to.save()

    @staticmethod
    def trigger_common_action(user, document):
        action = document.status.common_action
        if not action:
            return

        if "copy" in action:
            DocumentApiUtils._copy_items(action['copy'], document)
