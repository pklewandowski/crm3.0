from apps.product.calc import LoanCalculation
from apps.product.utils.utils import LoanUtils


class ProductAction:

    @staticmethod
    def create_loan(user, document_id):
        product = LoanUtils.create_loan(user=user, id=document_id)
        LoanCalculation(product=product, user=user).calculate()
