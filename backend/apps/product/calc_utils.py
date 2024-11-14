import decimal


def calculate_nominal_interest_daily(
        capital_total: decimal.Decimal,
        interest_rate: decimal.Decimal,
        days_in_year: int,
) -> decimal.Decimal:
    return round(capital_total * interest_rate / days_in_year, 4)
