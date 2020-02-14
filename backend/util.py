# Standard library imports
import locale


def get_currency_symbol(currency_code):
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
