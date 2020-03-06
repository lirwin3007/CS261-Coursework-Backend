# Standard library imports
import math
from datetime import date

# Local application imports
from backend.external_models import Company, Currency, Product, CompanyStock


def indexCompanies():
    return Company.query.all()


def indexAssets():
    assets = Product.query.with_entities(Product.name).distinct().all()
    return [asset[0] for asset in assets]


def indexCurrencyCodes():
    currency_codes = Currency.query.with_entities(Currency.code).distinct().all()
    return [code[0] for code in currency_codes]


def getUSDExchangeRate(currency_code):
    currency = Currency.query.get((currency_code, date.today()))
    if currency is not None:
        return currency.usd_exchange_rate
    return math.nan


def getProductPrice(product_name):
    product = Product.query.get((product_name, date.today()))
    if product is not None:
        return product.market_price, product.currency_code
    return math.nan, '?'


def getCompanyStockPrice(company_id):
    company_stock = CompanyStock.query.get((company_id, date.today()))
    if company_stock is not None:
        return company_stock.stock_price, company_stock.currency_code
    return math.nan, '?'


def getAssetPrice(asset_name, selling_party):
    if asset_name.lower() == 'stocks':
        return getCompanyStockPrice(selling_party)
    return getProductPrice(asset_name)
