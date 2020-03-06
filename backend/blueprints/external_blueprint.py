# Third party imports
from flask import Blueprint, jsonify

# Local application imports
from backend.managers import external_management
from backend import utils

# Instantiate new blueprint
ExternalBlueprint = Blueprint('external',
                              __name__,
                              url_prefix='/external')


@ExternalBlueprint.route('/index-companies')
def indexCompanies():
    return jsonify(companies=external_management.indexCompanies())


@ExternalBlueprint.route('/index-assets')
def indexAssets():
    return jsonify(assets=external_management.indexAssets())


@ExternalBlueprint.route('/index-currencies')
def indexCurrencies():
    currency_codes = external_management.indexCurrencyCodes()
    currencies = []

    for code in currency_codes:
        symbol = utils.getCurrencySymbol(code)
        currencies.append(dict(code=code, symbol=symbol))

    return jsonify(currencies=currencies)
