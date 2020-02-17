# Local application imports
from tests import context # noqa # pylint: disable=unused-import
from backend.derivatex_models import User
from backend.managers import user_management
from backend.db import db

def testGetUser():
    # Obtain dummy derivative
    user = dummyUser()

    # Add dummy user to database session
    db.session.add(user)
    db.session.flush()

    # Assert that getUser returns the user
    assert user_management.getUser(user.id) == user


def dummyUser():
    user = User.query.first()
    if user is None:
        user = User(
            f_name='f_name',
            l_name='l_name',
            email='email',
            password='password'
        )
    return user
