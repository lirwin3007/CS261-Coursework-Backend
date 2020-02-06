# Standard library imports
from datetime import datetime
import enum

# Local application imports
from cs261.application import db


class Derivative(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    buying_party = db.Column(db.String(6), nullable=False)
    selling_party = db.Column(db.String(6), nullable=False)
    asset = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    strike_price = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.CHAR(3), nullable=False)
    date_of_trade = db.Column(db.Date, nullable=False)
    maturity_date = db.Column(db.Date, nullable=False)
    modified = db.Column(db.Boolean, nullable=False, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return '<Derivative : {}>'.format(self.id)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    f_name = db.Column(db.String(32), nullable=False)
    l_name = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False, unique=True)
    profile_image = db.Column(db.String(128))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return '<User : {}>'.format(self.id)


class ActionType(enum.Enum):
    ADD = "Derivative recorded"
    UPDATE = "Derivative updated"
    DELETE = "Derivative deleted"


class Action(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    derivative_id = db.Column(db.BigInteger, db.ForeignKey('derivative.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.Enum(ActionType), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())
    update_info = db.Column(db.JSON)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return '<Action : {}>'.format(self.id)
