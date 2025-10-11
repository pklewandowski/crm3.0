from django.apps import AppConfig


def update_global_interest_list(sender, **kwargs):
    from apps.product.models import ProductInterestGlobal
    ProductInterestGlobal.update_list()


class ProductConfig(AppConfig):
    name = 'apps.product'

    def ready(self):
        from apps.product.api.views import global_interest_changed
        global_interest_changed.connect(update_global_interest_list)
