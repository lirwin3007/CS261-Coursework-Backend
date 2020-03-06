# Local application imports
from backend.db import db
from backend import utils


class Company(db.Model):
    # Bind schema to external database
    __bind_key__ = 'external'
    # Primary key (id)
    id = db.Column(db.String(6), primary_key=True)
    name = db.Column(db.String(32), nullable=False)


class ProductSeller(db.Model):
    # Bind schema to external database
    __bind_key__ = 'external'
    # Composite key (company_id, product_name)
    company_id = db.Column(db.String(6), db.ForeignKey('company.id'), primary_key=True)
    product_name = db.Column(db.String(32), db.ForeignKey('product.name'), primary_key=True)


class Currency(db.Model):
    # Bind schema to external database
    __bind_key__ = 'external'
    # Composite key (code, valuation_date)
    code = db.Column(db.CHAR(3), nullable=False, primary_key=True)
    valuation_date = db.Column(db.Date, primary_key=True)
    usd_exchange_rate = db.Column(db.Float, nullable=False)

    @property
    def symbol(self):
        return utils.getCurrencySymbol(self.code) or '?'


class CompanyStock(db.Model):
    # Bind schema to external database
    __bind_key__ = 'external'
    # Composite key (company_id, valuation_date)
    company_id = db.Column(db.String(6), db.ForeignKey('company.id'), primary_key=True)
    valuation_date = db.Column(db.Date, primary_key=True)
    stock_price = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.CHAR(3), db.ForeignKey('currency.code'))


class Product(db.Model):
    # Bind schema to external database
    __bind_key__ = 'external'
    # Composite key (name, valuation_date)
    name = db.Column(db.String(32), primary_key=True)
    valuation_date = db.Column(db.Date, primary_key=True)
    market_price = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.CHAR(3), db.ForeignKey('currency.code'))
