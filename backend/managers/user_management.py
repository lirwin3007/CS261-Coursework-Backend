# Local application imports
from backend.derivatex_models import User


def getUser(userId):
    # Query database for the user
    return User.query.get(userId)


def getAllUsers():
    # Query database for all users
    return User.query.all()
