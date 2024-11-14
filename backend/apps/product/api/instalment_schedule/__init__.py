INSTALMENT_MATURITY_DATE_SELECTOR = 'instalment-maturity-date'
INSTALMENT_CAPITAL_SELECTOR = 'instalment-capital'
INSTALMENT_COMMISSION_SELECTOR = 'instalment-commission'
INSTALMENT_INTEREST_SELECTOR = 'instalment-interest'
INSTALMENT_TOTAL_SELECTOR = 'instalment-total'

INSTALMENT_DATE_CHANGE_FLAG = 0b001
INSTALMENT_DATE_CHANGE_RECOUNT_FLAG = 0b010
INSTALMENT_CAPITAL_CHANGE_FLAG = 0b010
INSTALMENT_COMMISSION_CHANGE_FLAG = 0b100


def set_instalment_change_flag(value, flag):
    return value | flag


def unset_instalment_change_flag(value, flag):
    return value & (~flag & 7)


def match_instalment_change_flag(value, flag):
    return value & flag
