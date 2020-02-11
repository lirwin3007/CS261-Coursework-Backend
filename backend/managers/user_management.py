# Local application imports
from backend.derivatex_models import User


def getUser(user_id):
    # Query database for the user
    return User.query.get(user_id)


def getAllUsers():
    # Query database for all users
    return User.query.all()
