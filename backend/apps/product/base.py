from apps.product.models import Product, ProductActionDefinition
from apps.report.datasource_utils import ReportDatasourceUtils


class ProductManager:
    pass


class ProductActionManager(ProductManager):
    def __init__(self, *args, **kwargs):
        id_product = kwargs.pop('id_product', None)
        id_action = kwargs.pop('id_action', None)
        self.user = kwargs.pop('user', None)

        self.product = Product.objects.get(pk=id_product)
        self.action = ProductActionDefinition.objects.get(id=id_action)

    def get_datasource(self, product_calculation=None):
        cl = ReportDatasourceUtils(document=self.product.document, user=self.user, product_calculation=product_calculation)
        datasource = []
        for i in self.action.report.datasource_definition_set.all().order_by('sq'):
            value = cl.__getattribute__(i.getter_function)() if i.getter_function else ''
            datasource.append({'name': i.name, 'tag_name': i.tag_name, 'value': value, 'editable': i.editable})
        return datasource
