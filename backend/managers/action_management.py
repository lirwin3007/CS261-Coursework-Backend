# Local application imports
from backend.derivatex_models import Action


def getAction(actionId):
    # Query database for the action
    return Action.query.get(actionId)


def getUserActions(userID):
    return Action.query.filter_by(user_id=userID).order_by(Action.timestamp.desc()).all()


def getDerivativeActions(derivativeId):
    return Action.query.filter_by(derivative_id=derivativeId).order_by(Action.timestamp.desc()).all()


def getRecentActions(count):
    return Action.query.order_by(Action.timestamp.desc()).limit(count).all()
