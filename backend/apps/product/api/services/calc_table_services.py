from django.db.models import Q

from apps.document.models import DocumentTypeAccounting, DocumentTypeAttributeMapping
from apps.product.api import columns_accounting


def get_calc_table_columns(document_type):
    column_accounting_order = DocumentTypeAccounting.objects.filter(document_type=document_type).order_by('sq')
    mapping = [
        i.mapped_name
        for i in DocumentTypeAttributeMapping.objects.filter(type=document_type).filter(
            Q(attribute__isnull=False) | Q(default_value__isnull=False))
    ]

    columns = [
        {"title": "Data", "frozen": True, "field": "calc_date", "width": 120,
         "hozAlign": "center", "dataType": "date", "formatter": "css",
         "formatterParams": {"className": "calc-table-calc-date"}
         },

        {
            "title": "Saldo", "field": "balance", "headerSort": False, "dataType": "currency",
            "hozAlign": "right",
            "formatter": "moneyCss",
            "formatterParams": {
                "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-capital",
                "css": {"borderRightWidth": "2px"}
            }
        },

        {
            "title": "Saldo - nadpłata", "field": "balance_with_overpaid", "headerSort": False, "dataType": "currency",
            "hozAlign": "right",
            "formatter": "moneyCss",
            "formatterParams": {
                "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-capital",
                "css": {"borderRightWidth": "2px"}
            }
        },

        {"title": "Kapitał", "columns":
            [
                {"title": "niewymagalny", "field": "capital_not_required", "headerSort": False, "dataType": "currency",
                 "hozAlign": "right",
                 "formatter": "moneyCss",
                 "formatterParams": {
                     "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-capital"}
                 },

                {"title": "wymagalny", "field": "capital_required", "headerSort": False, "dataType": "currency",
                 "hozAlign": "right",
                 "formatter": "moneyCss",
                 "formatterParams": {
                     "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-capital",
                 }
                 },

                {"title": "z harmonogramu", "field": "capital_required_from_schedule", "headerSort": False,
                 "dataType": "currency",
                 "hozAlign": "right",
                 "formatter": "moneyCss",
                 "formatterParams": {
                     "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-capital",
                     "css": {"borderRightWidth": "2px"}
                 }
                 }
            ]
         }
    ]

    if 'COMMISSION' in mapping:
        columns.append(
            {"title": "Prowizja", "columns":
                [
                    {"title": "niewymagalna", "field": "commission_not_required", "headerSort": False,
                     "dataType": "currency",
                     "hozAlign": "right",
                     "formatter": "moneyCss", "formatterParams": {
                        "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-commission"}
                     },

                    {"title": "wymagalna", "field": "commission_required", "headerSort": False, "dataType": "currency",
                     "hozAlign": "right", "tooltip": True,
                     "formatter": "moneyCss", "formatterParams": {
                        "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-commission"
                    }
                     },

                    {"title": "z harmonogramu", "field": "commission_required_from_schedule", "headerSort": False,
                     "dataType": "currency",
                     "hozAlign": "right", "tooltip": True,
                     "formatter": "moneyCss",
                     "formatterParams": {
                         "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-commission",
                     }
                     }
                ],
             },
        )
    if 'INSTALMENT_INTEREST_RATE' in mapping:
        columns.append(
            {"title": "Odsetki", "columns":
                [
                    {
                        "title": "wymagalne", "field": "interest_required", "headerSort": False,
                        "dataType": "currency",
                        "hozAlign": "center", "tooltip": True,
                        "formatter": "moneyCss", "formatterParams":
                        {
                            "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-interest"
                        }
                    },
                    {"title": "procent", "field": "interest_rate", "headerSort": False, "dataType": "currency",
                     "hozAlign": "right",
                     "formatter": "moneyCss",
                     "formatterParams":
                         {
                             "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-interest",
                         }
                     },
                    {
                        "title": "dziennie", "field": "interest_daily", "headerSort": False, "dataType": "currency",
                        "hozAlign": "center", "tooltip": True,
                        "formatter": "moneyCss", "formatterParams":
                        {
                            "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-interest"
                        }
                    },
                    {
                        "title": "na dzień", "field": "interest_per_day", "headerSort": False, "dataType": "currency",
                        "hozAlign": "center", "tooltip": True,
                        "formatter": "moneyCss", "formatterParams":
                        {
                            "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-interest"
                        }
                    },
                    {
                        "title": "skumulowane", "field": "interest_cumulated_per_day", "headerSort": False,
                        "dataType": "currency",
                        "hozAlign": "right",
                        "formatter": "moneyCss", "formatterParams":
                        {
                            "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-interest",
                            # "css": {"borderRightWidth": "2px"}
                        }
                    },
                    # {
                    #     "title": "czy za opóźnienie", "field": "is_interest_for_delay", "headerSort": False,
                    #     "hozAlign": "right",
                    #     "formatter": "moneyCss", "formatterParams":
                    #     {
                    #         "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-interest",
                    #         "css": {"borderRightWidth": "2px"}
                    #     }
                    # },
                ]
             }
        )

    columns.extend(
        [
            {"title": "Suma zobowiązań", "columns":
                [
                    {"title": "na dzień", "field": "required_liabilities_sum", "headerSort": False,
                     "dataType": "currency",
                     "hozAlign": "right",
                     "formatter": "moneyCss", "formatterParams": {
                        "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-liabilities"
                    }
                     },

                    {"title": "z harmonogramu", "field": "required_liabilities_sum_from_schedule", "headerSort": False,
                     "dataType": "currency",
                     "hozAlign": "right",
                     "formatter": "moneyCss",
                     "formatterParams": {
                         "decimal": ",", "thousand": " ", "precision": 2, "className": "calc-table-liabilities",
                         "css": {"borderRightWidth": "2px"}
                     }
                     },
                ]
             },
            {"title": "Koszty", "columns":
                [
                    {
                        "title": "koszty utrzymania", "field": "cost_occurrence.COST_MAINTENANCE",
                        "headerSort": False,
                        "dataType": "currency",
                        "hozAlign": "right",
                        "formatter": "moneyCss",
                        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                            "className": "calc-table-cost"}
                    },

                    {
                        "title": "kara umowna", "field": "cost_occurrence.COST_CONTRACTUAL_PENALTY", "headerSort": False,
                        "dataType": "currency",
                        "hozAlign": "right",
                        "formatter": "moneyCss",
                        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                            "className": "calc-table-cost"}
                    },

                    {
                        "title": "opłata windykacyjna", "field": "cost_occurrence.COST_VINDICATION_FEE", "headerSort": False,
                        "dataType": "currency",
                        "hozAlign": "right",
                        "formatter": "moneyCss",
                        "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                            "className": "calc-table-cost"}
                    },

                    {
                        "title": "koszty inne", "field": "cost_occurrence.COST_OTHER", "headerSort": False,
                        "dataType": "currency",
                        "hozAlign": "right",
                        "formatter": "moneyCss",
                        "formatterParams": {
                            "decimal": ",", "thousand": " ",
                            "precision": 2,
                            "className": "calc-table-cost",
                            "css": {"borderRightWidth": "2px"}
                        }
                    },

                    # {"title": "w dniu", "field": "cost_occurrence", "headerSort": False, "dataType": "currency",
                    #  "hozAlign": "right",
                    #  "formatter": "moneyCss",
                    #  "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                    #                      "className": "calc-table-cost"}
                    #  },

                    {"title": "całkowite na dzień", "field": "cost_sum_per_day", "headerSort": False, "dataType": "currency",
                     "hozAlign": "right",
                     "formatter": "moneyCss",
                     "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                         "className": "calc-table-cost"}
                     },

                    {"title": "całkowite suma", "field": "cost_total", "headerSort": False, "dataType": "currency",
                     "hozAlign": "right",
                     "formatter": "moneyCss",
                     "formatterParams": {
                         "decimal": ",", "thousand": " ", "precision": 2,
                         "className": "calc-table-cost",
                         "css": {"borderRightWidth": "2px"}
                     }
                     }
                ]
             },

            {"title": "Wpłaty", "columns":
                [
                    {"title": "wpłata", "width": 80, "field": "instalment", "headerSort": False, "dataType": "currency",
                     "hozAlign": "right",
                     "formatter": "moneyCss",
                     "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                         "className": "calc-table-instalment"}
                     },

                    {"title": "suma", "width": 80, "field": "instalment_total", "headerSort": False,
                     "dataType": "currency",
                     "hozAlign": "right",
                     "formatter": "moneyCss",
                     "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                         "className": "calc-table-instalment",

                                         }
                     },
                    {"title": "nadpłata na dzień", "field": "instalment_overpaid", "headerSort": False,
                     "dataType": "currency",
                     "hozAlign": "right",
                     "formatter": "moneyCss",
                     "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                         "className": "calc-table-instalment", "css": {"borderRightWidth": "2px"}}
                     }
                ]
             }
        ])

    acc_columns = []
    for i in column_accounting_order:
        if i.accounting_type.code in columns_accounting.ACC:
            acc_columns.append(columns_accounting.ACC[i.accounting_type.code])

    columns.append({"title": "Wpłaty - rozksięgowanie (w kolejności księgowania)", "columns": acc_columns})

    columns.append(
        {"title": "Umorzenia", "columns":
            [
                {"title": "kapitał", "field": "remission_capital", "headerSort": False, "dataType": "currency",
                 "hozAlign": "right",
                 "formatter": "moneyCss",
                 "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                     "className": "calc-table-remission"}
                 },
                {"title": "prowizja", "field": "remission_commission", "headerSort": False, "dataType": "currency",
                 "hozAlign": "right",
                 "formatter": "moneyCss",
                 "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                     "className": "calc-table-remission"}
                 },
                {"title": "rata odsetkowa", "field": "remission_interest", "headerSort": False, "dataType": "currency",
                 "hozAlign": "right",
                 "formatter": "moneyCss",
                 "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                     "className": "calc-table-remission"}
                 },
                {"title": "odsetki za opóźnienie", "field": "remission_interest_for_delay", "headerSort": False,
                 "dataType": "currency",
                 "hozAlign": "right",
                 "formatter": "moneyCss",
                 "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                     "className": "calc-table-remission"}
                 },
                {"title": "koszt", "field": "remission_cost", "headerSort": False, "dataType": "currency",
                 "hozAlign": "right",
                 "formatter": "moneyCss",
                 "formatterParams": {"decimal": ",", "thousand": " ", "precision": 2,
                                     "className": "calc-table-remission"}
                 },
            ]
         }
    )

    return columns
