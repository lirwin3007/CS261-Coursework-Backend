# Standard library imports
from datetime import datetime

# Local application imports
from tests import context # noqa # pylint: disable=unused-import
from backend.derivatex_models import Derivative, User, Action, ActionType
from backend.managers import derivative_management
from backend.db import db


def testGetDerivative():
    # Obtain dummy derivative
    derivative = dummyDerivative()

    # Add dummy derivative to database session
    db.session.add(derivative)
    db.session.flush()

    # Assert that getDerivative returns the derivative
    assert derivative_management.getDerivative(derivative.id) == derivative


def testAddDerivativeStoresDerivative():
    # Obtain dummy derivative and user
    derivative = dummyDerivative()
    user = dummyUser()

    # Add dummy user to database session
    db.session.add(user)
    db.session.flush()

    # Execute addDerivative
    derivative_management.addDerivative(derivative, user.id)

    # Assert that the derivative has been stored by querying the database
    assert Derivative.query.get(derivative.id) == derivative


def testAddDerivativeRegistersAction():
    # Obtain dummy derivative and user
    derivative = dummyDerivative()
    user = dummyUser()

    # Update database session
    db.session.add(user)
    db.session.flush()

    # Execute addDerivative
    derivative_management.addDerivative(derivative, user.id)

    # Query the database for an action that corrosponds to adding the derivative
    action = Action.query.filter_by(derivative_id=derivative.id,
                                    user_id=user.id,
                                    type=ActionType.ADD).first()
    # Assert that such an action exists
    assert action is not None


def testDeleteDerivativeFlagsDerivative():
    # Obtain dummy derivative and user
    derivative = dummyDerivative()
    user = dummyUser()

    # Add dummy derivative and user to database session
    db.session.add(derivative)
    db.session.add(user)
    db.session.flush()

    # Execute deleteDerivative
    derivative_management.deleteDerivative(derivative, user.id)

    # Assert that the derivative has been flagged as deleted
    assert Derivative.query.get(derivative.id).deleted


def testDeleteDerivativeRegistersAction():
    # Obtain dummy derivative and user
    derivative = dummyDerivative()
    user = dummyUser()

    # Add dummy derivative and user to database session
    db.session.add(derivative)
    db.session.add(user)
    db.session.flush()

    # Execute deleteDerivative
    derivative_management.deleteDerivative(derivative, user.id)

    # Query the database for an action that corrosponds to deleting the derivative
    action = Action.query.filter_by(derivative_id=derivative.id,
                                    user_id=user.id,
                                    type=ActionType.DELETE).first()
    # Assert that such an action exists
    assert action is not None


def dummyDerivative():
    return Derivative(
        buying_party='foo',
        selling_party='bar',
        asset='baz',
        quantity=1,
        strike_price=20.20,
        currency_code='USD',
        date_of_trade=datetime.now(),
        maturity_date=datetime.now()
    )


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
