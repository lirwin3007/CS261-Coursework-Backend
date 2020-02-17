# Standard library imports
from datetime import datetime

# Local application imports
from tests import context # noqa # pylint: disable=unused-import
from backend.derivatex_models import Derivative, User, Action, ActionType
from backend.managers import derivative_management
from backend.db import db


def testGetDerivativeRetrievesDerivative():
    # Obtain dummy derivative
    derivative = dummyDerivative()

    # Add dummy derivative to database session
    db.session.add(derivative)
    db.session.flush()

    # Assert that getDerivative returns the derivative
    assert derivative_management.getDerivative(derivative.id) == derivative


def testGetDerivativeReturnsNoneIfNotFound():
    # Obtain dummy derivative
    derivative = dummyDerivative()

    # Add dummy derivative to database session
    db.session.add(derivative)
    db.session.flush()

    # Store the newly generated derivative id
    fresh_id = derivative.id
    # Discard the new derivative from the session to free the id
    db.session.rollback()

    # Assert that None is returned for the given id
    assert derivative_management.getDerivative(fresh_id) is None


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


def testUpdateDerivativeUpdatesAttributes():
    # Obtain dummy derivative, user and update
    derivative = dummyDerivative()
    user = dummyUser()
    updates = dummyUpdates()

    # Add dummy derivative and user to database session
    db.session.add(derivative)
    db.session.add(user)
    db.session.flush()

    # Execute updateDerivative
    derivative_management.updateDerivative(derivative, user.id, updates)

    # Assert that all attribute values have been correctly updated
    assert all(getattr(derivative, a) == v for a, v in updates.items())

    # Assert that all other attributes remain unchanged
    assert True


def testUpdateDerivativeLogsUpdates():
    # Obtain dummy derivative, user and update
    derivative = dummyDerivative()
    user = dummyUser()
    updates = dummyUpdates()

    # Add dummy derivative and user to database session
    db.session.add(derivative)
    db.session.add(user)
    db.session.flush()

    # Generate expected update log
    expected_update_log = []
    for attribute, new_value in updates.items():
        expected_update_log.append({
            "attribute": attribute,
            "old_value": getattr(derivative, attribute),
            "new_value": new_value
        })

    # Execute updateDerivative
    update_log = derivative_management.updateDerivative(derivative, user.id, updates)

    # Assert that updateDerivative returns the correct update log
    assert update_log == expected_update_log


def testUpdateDerivativeRegistersAction():
    # Obtain dummy derivative, user and update
    derivative = dummyDerivative()
    user = dummyUser()
    updates = dummyUpdates()

    # Add dummy derivative and user to database session
    db.session.add(derivative)
    db.session.add(user)
    db.session.flush()

    # Execute updateDerivative
    update_log = derivative_management.updateDerivative(derivative, user.id, updates)

    # Query the database for an action that corrosponds to updating the derivative
    action = Action.query.filter_by(derivative_id=derivative.id,
                                    user_id=user.id,
                                    type=ActionType.UPDATE).first()
    # Assert that such an action exists
    assert action is not None

    # Assert that the action stored the update log
    assert action.update_log == update_log


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


def dummyUpdates():
    return {
        'buying_party': 'foo',
        'selling_party': 'bar',
        'asset': 'baz'
    }
