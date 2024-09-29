from django.utils.translation import gettext_lazy as _
from django.db import models
from apps.dict.models import Dictionary


class Attribute(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('attribute.name.label'))
    description = models.TextField(null=True, blank=True, verbose_name=_('attribute.description.label'))
    # podstawowy walidator dla typu wartości. Wyzwalany na początku. Później poszczególne walidatory dla danego atrybutu z definicji w tabeli AttributeValidator
    regex = models.CharField(max_length=300, verbose_name=_('attribute.regex.label'), null=True, blank=True)
    mask = models.CharField(max_length=200, verbose_name=_('attribute.mask'), null=True, blank=True)
    default_format = models.CharField(max_length=100, null=True, blank=True, verbose_name=_('attribute.default_format.label'))
    generic_datatype = models.CharField(max_length=100, verbose_name=_('attribute.generic_datatype.label'))
    subtype = models.CharField(max_length=100, verbose_name=_('attribute.subtype'), null=True, blank=True)
    min_length = models.IntegerField(null=True, blank=True, verbose_name=_('attribute.min_length.label'))
    max_length = models.IntegerField(null=True, blank=True, verbose_name=_('attribute.max_length.label'))
    min_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name=_('attribute.min_value.label'))
    max_value = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True, verbose_name=_('attribute.max_value.label'))
    decimal_places = models.IntegerField(null=True, blank=True, verbose_name=_('attribute.decimal_places.label'))
    dictionary = models.ForeignKey(Dictionary, null=True, blank=True, verbose_name=_('attribute.dictionary.label'), db_column='id_dictionary', on_delete=models.CASCADE)
    # indicates if attribute is not provided with data (ie. chart is only display data container taking data from other attributes
    # another example is separator
    no_data = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'attribute'


class AttributeFormat(models.Model):
    attribute = models.ForeignKey(Attribute, db_column='id_attribute', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, verbose_name=_('attribute.validator.name.label'))
    code = models.CharField(max_length=20, null=True, blank=True, verbose_name=_('attribute.validator.code.label'))
    description = models.TextField(null=True, blank=True, verbose_name=_('attribute.validator.description.label'))

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'attribute_format'


class AttributeValidator(models.Model):
    attribute_datatype = models.ForeignKey(Attribute, db_column='id_attribute_datatype', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    regex = models.CharField(max_length=300, null=True, blank=True)
    # klasa niestandardowej funkcji walidacyjnej, wywoływanej dynamicznie. Klasa musi posiadać funkcję Validate. Klasa musi implementować interfejs p3ws.validate.attribute.validate
    validator_class = models.CharField(max_length=200, null=True, blank=True)
    error_message = models.TextField(default='')
    sq = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'attribute_validator'


class AttributeObjectType(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100, unique=True)
    attribute_class = models.CharField(max_length=300)

    class Meta:
        db_table = 'attribute_object_type'


class AttributeSection(models.Model):
    object_type = models.ForeignKey(AttributeObjectType, db_column='id_object_type', related_name='section_object_type', on_delete=models.CASCADE)
    object_id = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    sq = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'attribute_section'


class AttributeObjectTypeAttribute(models.Model):
    data_type = models.ForeignKey(Attribute, db_column='id_data_type', related_name='data_type', on_delete=models.CASCADE)
    section = models.ForeignKey(AttributeSection, db_column='id_section', related_name='section', on_delete=models.CASCADE)
    object_type = models.ForeignKey(AttributeObjectType, db_column='id_object_type', related_name='attribute_object_type', on_delete=models.CASCADE)
    object_id = models.IntegerField()
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    is_required = models.BooleanField(default=False)
    sq = models.IntegerField(default=0)

    class Meta:
        db_table = 'attribute_object_type_attribute'
        unique_together = ['code', 'object_type', 'object_id']
