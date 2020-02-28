# Local application imports
from backend.derivatex_models import User


def getUser(user_id):
    """ Return a particular user with a given user_id.

    Args:
        user_id (int): The ID of the user which needs to be returned.

    Returns:
        User: A user object.
    """
    return User.query.get(user_id)


def getUserFromUsername(username):
    """ Return a particular user with a given username (email).

    Args:
        username (string): The username / email of the user to be returned.

    Returns:
        User: A user object.
    """
    return User.query.filter_by(email=username).first()


def getAllUsers():
    """ Return all the users in the database as a list.

    Args:
        None

    Returns:
        list: The list of all users.
    """
    return User.query.all()
