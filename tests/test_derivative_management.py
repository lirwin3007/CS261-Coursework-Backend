# Local application imports
from backend.derivatex_models import Derivative, Action, ActionType
from backend.managers import derivative_management
from backend.db import db


def testGetDerivativeRetrievesDerivative(dummy_derivative):
    # Add dummy derivative to database session
    db.session.add(dummy_derivative)
    db.session.flush()

    # Assert that getDerivative returns the derivative
    assert derivative_management.getDerivative(dummy_derivative.id) == dummy_derivative


def testGetDerivativeReturnsNoneIfNotFound(free_derivtive_id):
    # Assert that None is returned for the free id
    assert derivative_management.getDerivative(free_derivtive_id) is None


def testAddDerivativeStoresDerivative(dummy_derivative, dummy_user):
    # Add dummy user to database session
    db.session.add(dummy_user)
    db.session.flush()

    # Execute addDerivative
    derivative_management.addDerivative(dummy_derivative, dummy_user.id)

    # Assert that the derivative has been stored by querying the database
    assert Derivative.query.get(dummy_derivative.id) == dummy_derivative


def testAddDerivativeRegistersAction(dummy_derivative, dummy_user):
    # Execute addDerivative
    derivative_management.addDerivative(dummy_derivative, dummy_user.id)

    # Query the database for an action that corrosponds to adding the derivative
    action = Action.query.filter_by(derivative_id=dummy_derivative.id,
                                    user_id=dummy_user.id,
                                    type=ActionType.ADD).first()
    # Assert that such an action exists
    assert action is not None


def testDeleteDerivativeFlagsDerivative(dummy_derivative, dummy_user):
    # Add dummy derivative and user to database session
    db.session.add(dummy_derivative)
    db.session.add(dummy_user)
    db.session.flush()

    # Execute deleteDerivative
    derivative_management.deleteDerivative(dummy_derivative, dummy_user.id)

    # Assert that the derivative has been flagged as deleted
    assert Derivative.query.get(dummy_derivative.id).deleted


def testDeleteDerivativeRegistersAction(dummy_derivative, dummy_user):
    # Add dummy derivative and user to database session
    db.session.add(dummy_derivative)
    db.session.add(dummy_user)
    db.session.flush()

    # Execute deleteDerivative
    derivative_management.deleteDerivative(dummy_derivative, dummy_user.id)

    # Query the database for an action that corrosponds to deleting the derivative
    action = Action.query.filter_by(derivative_id=dummy_derivative.id,
                                    user_id=dummy_user.id,
                                    type=ActionType.DELETE).first()
    # Assert that such an action exists
    assert action is not None


def testUpdateDerivativeUpdatesAttributes(dummy_derivative, dummy_user, dummy_updates):
    # Add dummy derivative and user to database session
    db.session.add(dummy_derivative)
    db.session.add(dummy_user)
    db.session.flush()

    # Execute updateDerivative
    derivative_management.updateDerivative(dummy_derivative,
                                           dummy_user.id,
                                           dummy_updates)

    # Assert that all attribute values have been correctly updated
    assert all(getattr(dummy_derivative, a) == v for a, v in dummy_updates.items())

    # Assert that all other attributes remain unchanged
    assert True


def testUpdateDerivativeLogsUpdates(dummy_derivative, dummy_user, dummy_updates):
    # Add dummy derivative and user to database session
    db.session.add(dummy_derivative)
    db.session.add(dummy_user)
    db.session.flush()

    # Generate expected update log
    expected_update_log = []
    for attribute, new_value in dummy_updates.items():
        expected_update_log.append({
            "attribute": attribute,
            "old_value": getattr(dummy_derivative, attribute),
            "new_value": new_value
        })

    # Execute updateDerivative
    update_log = derivative_management.updateDerivative(dummy_derivative,
                                                        dummy_user.id,
                                                        dummy_updates)

    # Assert that updateDerivative returns the correct update log
    assert update_log == expected_update_log


def testUpdateDerivativeRegistersAction(dummy_derivative, dummy_user, dummy_updates):
    # Add dummy derivative and user to database session
    db.session.add(dummy_derivative)
    db.session.add(dummy_user)
    db.session.flush()

    # Execute updateDerivative
    update_log = derivative_management.updateDerivative(dummy_derivative,
                                                        dummy_user.id,
                                                        dummy_updates)

    # Query the database for an action that corrosponds to updating the derivative
    action = Action.query.filter_by(derivative_id=dummy_derivative.id,
                                    user_id=dummy_user.id,
                                    type=ActionType.UPDATE).first()
    # Assert that such an action exists
    assert action is not None

    # Assert that the action stored the update log
    assert action.update_log == update_log
