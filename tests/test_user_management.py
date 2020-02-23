# Local application imports
from backend.managers import user_management
from backend.db import db


def testGetUser(dummy_user):
    # Add dummy user to database session
    db.session.add(dummy_user)
    db.session.flush()

    # Assert that getUser returns the user
    assert user_management.getUser(dummy_user.id) == dummy_user


def testGetUserReturnsNoneIfNotFound(free_user_id):
    # Assert that None is returned for the free id
    assert user_management.getUser(free_user_id) is None
