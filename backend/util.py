# Standard library imports
import locale


class AbsoluteDerivativeException(Exception):
    """Exception raised when a absolute derivative is modified"""
    pass


def getCurrencySymbol(currency_code):
    for l in locale.locale_alias.values():
        try:
            locale.setlocale(locale.LC_ALL, l)
        except locale.Error:
            continue

        conv = locale.localeconv()
        code = conv['int_curr_symbol'].strip()

        if code.upper() == currency_code.upper():
            return conv['currency_symbol']

    return None


def clamp(val, min_val, max_val):
    return max(min(max_val, val), min_val)
