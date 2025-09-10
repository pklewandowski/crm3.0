import copy
import re

from django.db.models import Q
from django.forms.models import model_to_dict

from apps.document.models import DocumentTypeAttribute, DocumentTypeAttributeFeature


class AttributeUtils:
    @staticmethod
    def render_calc_func(f):
        sources = re.findall(r'_(\d+)', f)
        body = re.sub(r'_(\d+)', 'document.getElementById(\'\g<1>\')', f)
        body = body.replace('#V', 'Input.getValue')
        return {'sources': sources, 'body': body}

    @staticmethod
    def get_attributes(document_type,
                       parent,
                       level,
                       type=None,
                       status=None,
                       only_data_items=False,
                       readonly=False):

        q = Q(is_active=True)
        q &= Q(type=type) if type else Q()
        q &= Q(parent=parent) if parent else Q(document_type=document_type, is_section=True, parent__isnull=True)

        for i in DocumentTypeAttribute.objects.filter(q).order_by('sq'):
            if only_data_items and (i.is_section or i.is_column or i.is_combo):
                AttributeUtils.get_attributes(parent=i, document_type=document_type, level=level, status=status,
                                              readonly=readonly)
                continue

            item = model_to_dict(i, fields=[field.name for field in i._meta.fields])

            if i.attribute:
                item['attribute'] = {
                    'id': i.attribute.pk,
                    'generic_datatype': i.attribute.generic_datatype,
                    'mask': i.attribute.mask,
                    'regex': i.attribute.regex,
                    'subtype': i.attribute.subtype,
                    'decimal_places': i.attribute.decimal_places,
                    'min_value': str(i.attribute.min_value or ''),
                    'max_value': str(i.attribute.max_value or ''),
                    'no_data': i.attribute.no_data
                }

                # if item has attribute assigned we can be sure that is field neither section nor column nor combo

                if status:
                    try:
                        df = DocumentTypeAttributeFeature.objects.get(attribute=i, status=status)
                        item['VER'] = {
                            'visible': df.visible,
                            'editable': df.editable and df.visible and not readonly,
                            'required': df.required and df.editable and not readonly,
                        }

                    except DocumentTypeAttributeFeature.DoesNotExist:
                        item['VER'] = {
                            'visible': True,
                            'editable': not readonly,
                            'required': False
                        }
                else:
                    item['VER'] = {
                        'visible': True,
                        'editable': not readonly,
                        'required': False
                    }

            level.append(item)

            if i.is_section or i.is_column or i.is_combo:
                item['children'] = []
                AttributeUtils.get_attributes(parent=i, document_type=document_type, level=item['children'], type=type,
                                              status=status, readonly=readonly)

    @staticmethod
    def get_attribute_list(document_type, parent, level, type):
        q = Q(type=type) if type else Q()
        q &= Q(parent=parent) if parent else Q(document_type=document_type, is_section=True, parent__isnull=True)

        for i in DocumentTypeAttribute.objects.filter(q).order_by('sq'):

            if i.is_section or i.is_column or i.is_combo:
                AttributeUtils.get_attribute_list(parent=i, document_type=document_type, level=level, type=type)
                continue

            level.append(i)

    @staticmethod
    def copy_attributes(source_document_type, new_document_type, parent_node=None, new_parent_node=None):

        def f(parent=None, new_parent=None):
            q = Q(parent=parent) if parent else Q(document_type=source_document_type, is_section=True,
                                                  parent__isnull=True)
            for i in DocumentTypeAttribute.objects.filter(q).order_by('sq'):
                attribute = copy.copy(i)
                attribute.pk = None
                attribute.parent = new_parent if new_parent else attribute.parent
                attribute.document_type = new_document_type
                if source_document_type.pk == new_document_type.pk:
                    attribute.code = None
                    attribute.save()
                    attribute.code = attribute.pk
                    attribute.save()
                else:
                    attribute.save()
                f(parent=i, new_parent=attribute)

        f(parent=parent_node, new_parent=new_parent_node)
