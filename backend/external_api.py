# Standard library imports
from datetime import datetime

# Local application imports
from backend.external_models import Company, Currency, Product, CompanyStock


# TODO: revisit this whole file
def getCurrentDate():
    return datetime.date(datetime.now()).replace(year=2019)


def getCompanyName(company_id):
    company = Company.query.get(company_id)
    if company is not None:
        return company.name
    return None


def getUSDExchangeRate(currency_code):
    currency = Currency.query.get((currency_code, getCurrentDate()))
    if currency is not None:
        return currency.usd_exchange_rate
    return None


def getProductPrice(product_name):
    product = Product.query.get((product_name, getCurrentDate()))
    if product is not None:
        return product.market_price, product.currency_code
    return None


def getCompanyStockPrice(company_id):
    company_stock = CompanyStock.query.get((company_id, getCurrentDate()))
    if company_stock is not None:
        return company_stock.stock_price, company_stock.currency_code
    return None


def getAssetPrice(asset_name, selling_party):
    if asset_name.lower() == 'stocks':
        return getCompanyStockPrice(selling_party)
    else:
        return getProductPrice(asset_name)