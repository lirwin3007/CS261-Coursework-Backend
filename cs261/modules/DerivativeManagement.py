from cs261.application import db
from cs261.modules.ActionManagement import Action


def getDerviative(derivativeId):
    return Derivative.query.filter_by(id=derivativeId).first()

def addDerivative(derivative_json, userId):
    # Create derivative object
    derivative = Derivative(**derivative_json)

    # Validate the derivative
    if True:
        # Register the user creating the derivative
        action = Action(derivative_id=derivative.id, user_id=userId, type="ADD")

        db.session.add(derivative)
        db.session.add(action)
        db.session.commit()

        return derivative

def deleteDerivative(derivativeId, userId):
    # Select the derivative
    derivative = getDerviative(derivativeId)

    if derivative is not None:
        # Delete the derivative
        derivative.delete()

        # Register the user deleting the derivative
        Action(derivativeId, userId, "DELETE")
        db.session.commit()


class Derivative(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    buying_party = db.Column(db.String(6), db.ForeignKey('company.id'))
    selling_party = db.Column(db.String(6), db.ForeignKey('company.id'))
    asset = db.Column(db.String(128), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    strike_price = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.CHAR(3), db.ForeignKey('currency.code'))
    date_of_trade = db.Column(db.Date, nullable=False)
    maturity_date = db.Column(db.Date, nullable=False)
    modified = db.Column(db.Boolean, nullable=False, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __str__(self):
        return '<Derivative : {}>'.format(self.id)
