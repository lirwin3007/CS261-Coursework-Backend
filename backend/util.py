# Standard library imports
import locale

# Third party imports
from fpdf import FPDF, HTMLMixin


class AbsoluteDerivativeException(Exception):
    """Exception raised when a absolute derivative is modified"""


# Add html functionality to fpdf pdf maker and set footer
class MyFPDF(FPDF, HTMLMixin):
    def footer(self):
        self.set_y(-25)  #-25
        self.set_font('Arial', 'I', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'PAGE %s OF {nb}' % self.page_no(), 0, 0, 'C')


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
