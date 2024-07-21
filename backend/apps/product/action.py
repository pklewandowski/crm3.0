from apps.product.calc import CalculateLoan
from apps.product.utils.utils import LoanUtils


class ProductAction:

    @staticmethod
    def create_loan(user, document_id):
        product = LoanUtils.create_loan(user=user, id=document_id)
        CalculateLoan(product=product, user=user).calculate()
