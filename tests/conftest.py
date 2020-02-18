# pylint: disable=redefined-outer-name

# Standard library imports
from datetime import datetime, timedelta

# Third party imports
import pytest

# Local application imports
from backend.derivatex_models import Derivative, User
from backend.app import Application
from backend.db import db


@pytest.fixture(scope="session", autouse=True)
def test_app():
    # Initialise test app instance
    app = Application.getTestApp()

    # Ensure app is configured for Testing
    if not app.config['TESTING']:
        raise SystemExit('App must be conifgured for testing')

    # Clean derivatex tables in the test database
    db.drop_all(bind=None)
    db.create_all(bind=None)

    # Return the flask app
    return app


@pytest.fixture(scope="session", autouse=True)
def test_client(test_app):
    # Get test client
    testing_client = test_app.test_client()

    # Establish an application context before running the tests.
    ctx = test_app.app_context()
    ctx.push()

    # Return the test client
    yield testing_client

    ctx.pop()


@pytest.fixture(autouse=True)
def rollback_session():
    # Run the test
    yield
    # Rollback the session after running the test
    db.session.rollback()


@pytest.fixture
def free_derivtive_id(dummy_derivative):
    # Add dummy derivative to database session
    db.session.add(dummy_derivative)
    db.session.flush()

    # Store the id of the new derivative
    free_id = dummy_derivative.id
    # Discard the new derivative from the session to free the id
    db.session.rollback()
    # Return the free id
    return free_id


@pytest.fixture
def dummy_derivative():
    today = datetime.date(datetime.now())

    return Derivative(
        code='doe',
        buying_party='foo',
        selling_party='bar',
        asset='baz',
        quantity=1,
        strike_price=20.20,
        currency_code='USD',
        date_of_trade=today,
        maturity_date=today + timedelta(days=365)
    )


@pytest.fixture
def dummy_abs_derivative():
    today = datetime.date(datetime.now())

    return Derivative(
        code='doe',
        buying_party='foo',
        selling_party='bar',
        asset='baz',
        quantity=1,
        strike_price=20.20,
        currency_code='USD',
        date_of_trade=today - timedelta(days=365),
        maturity_date=today + timedelta(days=365)
    )


@pytest.fixture
def dummy_user():
    user = User.query.first()
    if user is None:
        user = User(
            f_name='f_name',
            l_name='l_name',
            email='email',
            password='password'
        )
    return user


@pytest.fixture
def dummy_updates():
    return {
        'buying_party': 'foo',
        'selling_party': 'bar',
        'asset': 'baz'
    }