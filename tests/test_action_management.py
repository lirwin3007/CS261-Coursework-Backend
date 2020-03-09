# Local application imports
from backend.managers import action_management
from backend.db import db


def testGetActionRetrievesAction(dummy_action):
    # Add dummy derivative to database session
    db.session.add(dummy_action)
    db.session.flush()

    # Assert that getDerivative returns the derivative
    assert action_management.getAction(dummy_action.id) == dummy_action
