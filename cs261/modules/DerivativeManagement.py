from cs261.application import db
from cs261.modules.UserManagement import User
import datetime

def getDerviative(derivativeId):
    return Derivative.query.filter_by(id=derivativeId).first()

def getDerviatives(filter):
    return Derivative.query.filter(filter)

def addDerivative(derivative_json):
    # Create derivative object
    derivative = Derivative(**derivative_json)

    # Validate the derivative
    if True:
        # Register the user creating the derivative
        # Action(derivativeId, uid, "ADD")
        db.session.commit()
    else:
        db.session.rollback()

def deleteDerivative(derivativeId):
    # Delete the derivative
    Derivative.query.filter_by(id=derivativeId).delete()

    # Register the user deleting the derivative
    # Action(derivativeId, uid, "DELETE")

# ...
class Derivative(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    buying_party = db.Column(db.String(6), nullable=False)
    selling_party = db.Column(db.String(6), nullable=False)
    product = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    strike_price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.CHAR(3), nullable=False)
    maturity_date = db.Column(db.Date)
    modified = db.Column(db.Boolean, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return '<Derivative : {}>'.format(self.id)

# ...
class Action(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.String(16), db.ForeignKey('derivative.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(16), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init_(self, trade_id, user_id, type):
        self.trade_id = trade_id
        self.user_id = user_id
        self.type = type
        self.timestamp = datetime.datetime.utcnow()

    def __str__(self):
        return '<Action : {}>'.format(self.id)
