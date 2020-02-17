# Local application imports
from backend.derivatex_models import Derivative, Action, ActionType
from backend.managers import derivative_management
from backend.db import db


def testGetDerivativeRetrievesDerivative(dummy_derivative):
    # Obtain dummy derivative
    derivative = dummy_derivative

    # Add dummy derivative to database session
    db.session.add(derivative)
    db.session.flush()

    # Assert that getDerivative returns the derivative
    assert derivative_management.getDerivative(derivative.id) == derivative


def testGetDerivativeReturnsNoneIfNotFound(free_derivtive_id):
    # Assert that None is returned for the free id
    assert derivative_management.getDerivative(free_derivtive_id) is None


def testAddDerivativeStoresDerivative(dummy_derivative, dummy_user):
    # Obtain dummy derivative and user
    derivative = dummy_derivative
    user = dummy_user

    # Add dummy user to database session
    db.session.add(user)
    db.session.flush()

    # Execute addDerivative
    derivative_management.addDerivative(derivative, user.id)

    # Assert that the derivative has been stored by querying the database
    assert Derivative.query.get(derivative.id) == derivative


def testAddDerivativeRegistersAction(dummy_derivative, dummy_user):
    # Obtain dummy derivative and user
    derivative = dummy_derivative
    user = dummy_user

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


def testDeleteDerivativeFlagsDerivative(dummy_derivative, dummy_user):
    # Obtain dummy derivative and user
    derivative = dummy_derivative
    user = dummy_user

    # Add dummy derivative and user to database session
    db.session.add(derivative)
    db.session.add(user)
    db.session.flush()

    # Execute deleteDerivative
    derivative_management.deleteDerivative(derivative, user.id)

    # Assert that the derivative has been flagged as deleted
    assert Derivative.query.get(derivative.id).deleted


def testDeleteDerivativeRegistersAction(dummy_derivative, dummy_user):
    # Obtain dummy derivative and user
    derivative = dummy_derivative
    user = dummy_user

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


def testUpdateDerivativeUpdatesAttributes(dummy_derivative, dummy_user, dummy_updates):
    # Obtain dummy derivative, user and update
    derivative = dummy_derivative
    user = dummy_user
    updates = dummy_updates

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


def testUpdateDerivativeLogsUpdates(dummy_derivative, dummy_user, dummy_updates):
    # Obtain dummy derivative, user and update
    derivative = dummy_derivative
    user = dummy_user
    updates = dummy_updates

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


def testUpdateDerivativeRegistersAction(dummy_derivative, dummy_user, dummy_updates):
    # Obtain dummy derivative, user and update
    derivative = dummy_derivative
    user = dummy_user
    updates = dummy_updates

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
