# Standard library imports
import locale
from datetime import date

# Third party imports
from sqlalchemy.ext.declarative import DeclarativeMeta
from flask.json import JSONEncoder
from fpdf import FPDF, HTMLMixin


class AbsoluteDerivativeException(Exception):
    """Exception raised when a absolute derivative is modified"""


# Custom JSON encoder for SQLAlchemy Models and dates
class MyJSONEncoder(JSONEncoder):
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o.__class__, DeclarativeMeta):
            # Gather object attributes
            columns = [c.name for c in o.__table__.columns]
            properties = [n for n, v in vars(o.__class__).items() if isinstance(v, property)]
            attributes = columns + properties
            # Return a dictionary of attribute-value pairs
            return {attribute: getattr(o, attribute) for attribute in attributes}

        return super(MyJSONEncoder, self).default(o)


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


# Add html functionality to fpdf pdf maker and set footer
class MyFPDF(FPDF, HTMLMixin):
    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, 'PAGE %s OF {nb}' % self.page_no(), 0, 0, 'C')


def clamp(val, min_val, max_val):
    return max(min(max_val, val), min_val)
