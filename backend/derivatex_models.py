# Standard library imports
from datetime import datetime, date
import enum
import statistics

# Local application imports
from backend.db import db
from backend import util
from backend import external_api


class Derivative(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    code = db.Column(db.String(16), nullable=False, unique=True)
    buying_party = db.Column(db.String(6), nullable=False)
    selling_party = db.Column(db.String(6), nullable=False)
    asset = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    strike_price = db.Column(db.Float, nullable=False)
    notional_curr_code = db.Column(db.CHAR(3), nullable=False)
    date_of_trade = db.Column(db.Date, nullable=False)
    maturity_date = db.Column(db.Date, nullable=False)
    reported = db.Column(db.Boolean, nullable=False, default=False)
    deleted = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def absolute(self):
        # Determine time diff between date of trade and now
        delta = date.today() - self.date_of_trade
        # The derivative is absolute if it was traded over a month ago
        return self.deleted or delta.days >= 30

    @property
    def associated_actions(self):
        # Form query for all associated actions
        query = Action.query.filter_by(derivative_id=self.id)
        # Order actions chronologically
        query = query.order_by(Action.timestamp.desc())
        # Return the ids of all the actions
        return [action.id for action in query.all()]

    # TODO: revisit
    @property
    def underlying_price(self):
        up, _ = external_api.getAssetPrice(self.asset, self.selling_party)
        return up

    # TODO: revisit
    @property
    def underlying_curr_code(self):
        _, ucc = external_api.getAssetPrice(self.asset, self.selling_party)
        return ucc

    # TODO: revisit
    @property
    def notional_value(self):
        up = self.underlying_price
        ucc = self.underlying_curr_code
        n_ex_rate = external_api.getUSDExchangeRate(self.notional_curr_code)
        u_ex_rate = external_api.getUSDExchangeRate(ucc)

        return self.quantity * up * u_ex_rate / n_ex_rate

    @property
    def notional_curr_symbol(self):
        return util.getCurrencySymbol(self.notional_curr_code) or '?'

    @property
    def underlying_curr_symbol(self):
        return util.getCurrencySymbol(self.underlying_curr_code) or '?'

    def __str__(self):
        return f'<Derivative : {self.id}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(32), nullable=False)
    l_name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False, unique=True)
    profile_image = db.Column(db.String(128))

    def __str__(self):
        return f'<User : {self.id}>'


class ActionType(str, enum.Enum):
    ADD = 'ADD'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'


class Action(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    derivative_id = db.Column(db.BigInteger, db.ForeignKey('derivative.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.Enum(ActionType), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    update_log = db.Column(db.JSON)

    def __str__(self):
        return f'<Action : {self.id}>'


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_date = db.Column(db.Date, nullable=False)
    creation_date = db.Column(db.Date, nullable=False)
    version = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return f'<Report : {self.id}>'
        return '<Report : {}>'.format(self.id)


class Features(str, enum.Enum):
    BUYING_PARTY = 'BUYING_PARTY'
    SELLING_PARTY = 'SELLING_PARTY'
    ASSET = 'ASSET'
    QUANTITY = 'QUANTITY'
    STRIKE_PRICE = 'STRIKE_PRICE'


class Label(str, enum.Enum):
    ERRONEOUS = 'ERRONEOUS'
    VALID = 'VALID'


class DecisionTreeNode(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    parent_id = db.Column(db.BigInteger, db.ForeignKey('decision_tree_node.id'))
    true_node_id = db.Column(db.BigInteger, db.ForeignKey('decision_tree_node.id'))
    false_node_id = db.Column(db.BigInteger, db.ForeignKey('decision_tree_node.id'))
    feature = db.Column(db.Enum(Features))
    criteria = db.Column(db.Text)
    label = db.Column(db.Enum(Label))

    def calculateBuyingPartyFeature(self, item):
        """ Calculate the buying party feature of a given item.

        Args:
            item (Derivative): The derivative to get the feature for

        Returns:
            Boolean: The value of the feature for the given item
        """
        return item.buying_party == self.criteria

    def calculateSellingPartyFeature(self, item):
        """ Calculate the selling party feature of a given item.

        Args:
            item (Derivative): The derivative to get the feature for

        Returns:
            Boolean: The value of the feature for the given item
        """
        return item.selling_party == self.criteria

    def calculateAssetFeature(self, item):
        """ Calculate the asset party feature of a given item.

        Args:
            item (Derivative): The derivative to get the feature for

        Returns:
            Boolean: The value of the feature for the given item
        """
        return item.asset == self.criteria

    def calculateQuantityFeature(self, item, mean=0, standardDeviation=0):
        """ Calculate the quantity feature of a given item.

        Args:
            item (Derivative): The derivative to get the feature for
            mean (Integer): The mean to compare ``item`` to
            standardDeviation (Integer): The standard deviation to compare ``item`` to

        Returns:
            Boolean: The value of the feature for the given item
        """
        result = False
        if self.criteria == 'less_than_mean':
            result = item.quantity < mean
        elif self.criteria == 'more_than_mean':
            result = item.quantity > mean
        elif self.criteria == '0_to_1_std':
            result = abs(mean - item.quantity) <= standardDeviation
        elif self.criteria == '1_to_2_std':
            deviation = abs(mean - item.quantity)
            result = standardDeviation < deviation <= 2 * standardDeviation
        elif self.criteria == '2_to_3_std':
            deviation = abs(mean - item.quantity)
            result = 2 * standardDeviation < deviation <= 3 * standardDeviation
        elif self.criteria == '3_to_inf_std':
            deviation = abs(mean - item.quantity)
            result = deviation > 3 * standardDeviation
        return result

    def calculateStrikePriceFeature(self, item, mean=0, standardDeviation=0):
        """ Calculate the strike price feature of a given item.

        Args:
            item (Derivative): The derivative to get the feature for
            mean (Integer): The mean to compare ``item`` to
            standardDeviation (Integer): The standard deviation to compare ``item`` to

        Returns:
            Boolean: The value of the feature for the given item
        """
        result = False
        if self.criteria == 'less_than_mean':
            result = item.strike_price < mean
        elif self.criteria == 'more_than_mean':
            result = item.strike_price > mean
        elif self.criteria == '0_to_1_std':
            result = abs(mean - item.strike_price) <= standardDeviation
        elif self.criteria == '1_to_2_std':
            deviation = abs(mean - item.strike_price)
            result = standardDeviation < deviation <= 2 * standardDeviation
        elif self.criteria == '2_to_3_std':
            deviation = abs(mean - item.strike_price)
            result = 2 * standardDeviation < deviation <= 3 * standardDeviation
        elif self.criteria == '3_to_inf_std':
            deviation = abs(mean - item.strike_price)
            result = deviation > 3 * standardDeviation
        return result

    def split(self, data):
        """ Split given data on this node.

        Args:
            data (List of Derivative): The data to split

        Returns:
            (List of Derivative, List of Derivative): The split data. The first
            item is the data that matches this node's feature, the second item
            is the remaining data
        """
        trueSplit = []
        falseSplit = []
        if self.feature == Features.BUYING_PARTY:
            trueSplit = filter(self.calculateBuyingPartyFeature, data)
            falseSplit = filter(lambda x: not self.calculateBuyingPartyFeature(x), data)
        elif self.feature == Features.SELLING_PARTY:
            trueSplit = filter(self.calculateSellingPartyFeature, data)
            falseSplit = filter(lambda x: not self.calculateSellingPartyFeature(x), data)
        elif self.feature == Features.SELLING_PARTY:
            trueSplit = filter(self.calculateSellingPartyFeature, data)
            falseSplit = filter(lambda x: not self.calculateSellingPartyFeature(x), data)
        elif self.feature == Features.ASSET:
            trueSplit = filter(self.calculateAssetFeature, data)
            falseSplit = filter(lambda x: not self.calculateAssetFeature(x), data)
        elif self.feature == Features.QUANTITY:
            mean = 0
            standardDeviation = 0
            if self.criteria == 'less_than_mean' or self.criteria == 'more_than_mean':
                mean = statistics.mean([x.quantity for x in data])
            else:
                standardDeviation = statistics.stdev([x.quantity for x in data])
            trueSplit = filter(lambda x: self.calculateQuantityFeature(x, mean, standardDeviation), data)
            falseSplit = filter(lambda x: not self.calculateQuantityFeature(x, mean, standardDeviation), data)
        elif self.feature == Features.STRIKE_PRICE:
            mean = 0
            standardDeviation = 0
            if self.criteria == 'less_than_mean' or self.criteria == 'more_than_mean':
                mean = statistics.mean([x.strike_price for x in data])
            else:
                standardDeviation = statistics.stdev([x.strike_price for x in data])
            trueSplit = filter(lambda x: self.calculateStrikePriceFeature(x, mean, standardDeviation), data)
            falseSplit = filter(lambda x: not self.calculateStrikePriceFeature(x, mean, standardDeviation), data)

        return {
            'true': list(trueSplit),
            'false': list(falseSplit)
        }

    def __str__(self):
        return f'<DecisionTreeNode : {self.id}>'
