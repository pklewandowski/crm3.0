from apps.product.models import CompanyBankTransactionFile


def get_subsidiary_companies():
    return {}
    # return {i.company.name: i.base_dir for i in CompanyBankTransactionFile.objects.all()}
