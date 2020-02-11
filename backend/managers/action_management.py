# Local application imports
from backend.derivatex_models import Action


def getAction(action_id):
    # Query database for the action
    return Action.query.get(action_id)


def getUserActions(user_id):
    return Action.query.filter_by(user_id=user_id).order_by(Action.timestamp.desc()).all()


def getDerivativeActions(derivative_id):
    return Action.query.filter_by(derivative_id=derivative_id).order_by(Action.timestamp.desc()).all()


def getRecentActions(count):
    return Action.query.order_by(Action.timestamp.desc()).limit(count).all()
