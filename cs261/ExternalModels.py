# Local application imports
from cs261.application import db


class Company(db.Model):
    # Primary key (id)
    __bind_key__ = 'external'
    id = db.Column(db.String(6), primary_key=True)
    name = db.Column(db.String(32), nullable=False)


class productSeller(db.Model):
    # Composite key (company_id, product_name)
    __bind_key__ = 'external'
    company_id = db.Column(db.String(6), db.ForeignKey('company.id'), primary_key=True)
    product_name = db.Column(db.String(32), db.ForeignKey('product.name'), primary_key=True)


class Currency(db.Model):
    # Composite key (code, valuation_date)
    __bind_key__ = 'external'
    code = db.Column(db.CHAR(3), nullable=False, primary_key=True)
    valuation_date = db.Column(db.Date, primary_key=True)
    usd_exchange_rate = db.Column(db.Float, nullable=False)


class CompanyStock(db.Model):
    # Composite key (company_id, valuation_date)
    __bind_key__ = 'external'
    company_id = db.Column(db.String(6), db.ForeignKey('company.id'), primary_key=True)
    valuation_date = db.Column(db.Date, primary_key=True)
    stock_price = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.CHAR(3), db.ForeignKey('currency.code'))


class Product(db.Model):
    # Composite key (name, valuation_date)
    __bind_key__ = 'external'
    name = db.Column(db.String(32), primary_key=True)
    valuation_date = db.Column(db.Date, primary_key=True)
    market_price = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.CHAR(3), db.ForeignKey('currency.code'))
