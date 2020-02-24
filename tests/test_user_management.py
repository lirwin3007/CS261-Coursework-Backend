# Local application imports
from backend.managers import user_management
from backend.db import db


def testGetUser(dummy_user):
    # Add dummy user to database session
    db.session.add(dummy_user)
    db.session.flush()

    # Assert that getUser returns the user
    assert user_management.getUser(dummy_user.id) == dummy_user

def testGetAllUsers(dummy_user, dummy_user_2):
    # Add two dmmy users to database session
    db.session.add(dummy_user)
    users = [dummy_user]
    db.session.add(dummy_user_2)
    users.append(dummy_user_2)
    db.session.flush()

    # Assert that getAllUsers returns all the users
    assert user_management.getAllUsers() == users


def testGetUserReturnsNoneIfNotFound(free_user_id):
    # Assert that None is returned for the free id
    assert user_management.getUser(free_user_id) is None
