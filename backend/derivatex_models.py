# Standard library imports
from datetime import datetime, date
import enum

# Local application imports
from backend.db import db
from backend import utils
from backend.managers import external_management


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
        up, _ = external_management.getAssetPrice(self.asset, self.selling_party)
        return up

    # TODO: revisit
    @property
    def underlying_curr_code(self):
        _, ucc = external_management.getAssetPrice(self.asset, self.selling_party)
        return ucc

    # TODO: revisit
    @property
    def notional_value(self):
        up = self.underlying_price
        ucc = self.underlying_curr_code
        n_ex_rate = external_management.getUSDExchangeRate(self.notional_curr_code)
        u_ex_rate = external_management.getUSDExchangeRate(ucc)

        return self.quantity * up * u_ex_rate / n_ex_rate

    @property
    def notional_curr_symbol(self):
        return utils.getCurrencySymbol(self.notional_curr_code)

    @property
    def underlying_curr_symbol(self):
        return utils.getCurrencySymbol(self.underlying_curr_code) 

    def __str__(self):
        return f'<Derivative : {self.id}>'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(32), nullable=False)
    l_name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False, unique=True)
    profile_image = db.Column(db.String(30000))

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
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    update_log = db.Column(db.JSON)

    def __str__(self):
        return f'<Action : {self.id}>'


class ReportHead(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    target_date = db.Column(db.Date, nullable=False)
    creation_date = db.Column(db.Date, nullable=False)
    version = db.Column(db.Integer, nullable=False)
    derivative_count = db.Column(db.Integer, nullable=False)

    def __str__(self):
        return f'<ReportHead : {self.id}>'
