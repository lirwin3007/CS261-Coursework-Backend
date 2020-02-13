# Standard library imports
import locale


def get_currency_symbol(currency_code):
    for l in locale.locale_alias.values():
        try:
            locale.setlocale(locale.LC_ALL, l)
            conv = locale.localeconv()
            code = conv['int_curr_symbol'].strip()

            if code.upper() == currency_code.upper():
                return conv['currency_symbol']
        except NameError:
            return None

    return None
