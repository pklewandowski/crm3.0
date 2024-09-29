from django.core.exceptions import MiddlewareNotUsed
from .config import *


class ProductRetailMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        if not CLIENT_CLASS:
            raise AttributeError('Nie zdefiniowano wartości dla app.product_retail.CLIENT_CLASS')
        if not USER_CLASS:
            raise AttributeError('Nie zdefiniowano wartości dla app.product_retail.USER_CLASS')

        raise MiddlewareNotUsed
