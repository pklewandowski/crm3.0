TEMPLATE = {
    f'INTEREST_REQUIRED': {
        "title": "odsetki", "field": "instalment_accounting_interest_required",
        "headerSort": False, "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    }
}

COST = {
    'COST_OTHER': {
        "title": "koszty inne", "field": "instalment_accounting.COST_OTHER", "headerSort": False, "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'COST_MAINTENANCE': {
        "title": "koszty utrzymania", "field": "instalment_accounting.COST_MAINTENANCE", "headerSort": False,
        "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'COST_CONTRACTUAL_PENALTY': {
        "title": "kara umowna", "field": "instalment_accounting.COST_CONTRACTUAL_PENALTY", "headerSort": False,
        "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'COST_VINDICATION_FEE': {
        "title": "opłata windykacyjna", "field": "instalment_accounting.COST_VINDICATION_FEE", "headerSort": False,
        "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },
}

ACC = {
    'COMM_REQ': {
        "title": "prowizja wymagalna", "field": "instalment_accounting_commission_required",
        "headerSort": False, "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'COMM_NOT_REQ': {
        "title": "prowizja niewymagalna", "field": "instalment_accounting_commission_not_required",
        "headerSort": False, "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'INTEREST_REQUIRED': {
        "title": "odsetki", "field": "instalment_accounting_interest_required",
        "headerSort": False, "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'COST_OTHER': {
        "title": "koszty inne", "field": "instalment_accounting.COST_OTHER", "headerSort": False, "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'COST_MAINTENANCE': {
        "title": "koszty utrzymania", "field": "instalment_accounting.COST_MAINTENANCE", "headerSort": False,
        "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'COST_CONTRACTUAL_PENALTY': {
        "title": "kara umowna", "field": "instalment_accounting.COST_CONTRACTUAL_PENALTY", "headerSort": False,
        "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'COST_VINDICATION_FEE': {
        "title": "opłata windykacyjna", "field": "instalment_accounting.COST_VINDICATION_FEE", "headerSort": False,
        "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'CAP_REQ': {
        "title": "kapitał wymagalny", "field": "instalment_accounting_capital_required", "headerSort": False,
        "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                            "className": "calc-table-instalment-accounting"}
    },

    'CAP_NOT_REQ': {
        "title": "kapitał niewymagalny", "field": "instalment_accounting_capital_not_required",
        "headerSort": False, "dataType": "currency",
        "hozAlign": "right",
        "formatter": "moneyCss",
        "formatterParams": {
            "decimal": ",", "thousand": " ", "precision": 2,
            "className": "calc-table-instalment-accounting"
        }
    }
}
