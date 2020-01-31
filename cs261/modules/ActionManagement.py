from cs261.application import db
from datetime import datetime

def getAction(actionId):
    return Action.query.filter_by(id=actionId).first()

def getAssociatedActions(derivativeId):
    return Action.query.filter_by(derivative_id=derivativeId)

class Action(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    derivative_id = db.Column(db.String(16), db.ForeignKey('derivative.id'))
    user_id = db.Column(db.Integer) # , db.ForeignKey('user.id')
    type = db.Column(db.String(16), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __init_(self, trade_id, user_id, type):
        self.trade_id = trade_id
        self.user_id = user_id
        self.type = type
        self.timestamp = datetime.datetime.utcnow()

    def __str__(self):
        return '<Action : {}>'.format(self.id)
