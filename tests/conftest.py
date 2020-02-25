# pylint: disable=redefined-outer-name

# Standard library imports
from datetime import date, timedelta

# Third party imports
import pytest

# Local application imports
from backend.derivatex_models import Derivative, User, ReportHead
from backend.app import Application
from backend.db import db


@pytest.fixture(scope='session', autouse=True)
def test_app():
    # Initialise test app instance
    app = Application.getTestApp()

    # Ensure app is configured for Testing
    if not app.config['TESTING']:
        raise SystemExit('App must be conifgured for testing')

    # Return the flask app
    return app


@pytest.fixture(scope='session', autouse=True)
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
def clean_database():
    # Clean the session and all tables in the test database
    db.session.rollback()
    db.drop_all(bind=None)
    db.create_all(bind=None)


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


# TODO: revisit
@pytest.fixture
def dummy_derivative():
    today = date.today()

    return Derivative(
        code='doe',
        buying_party='foo',
        selling_party='bar',
        asset='Stocks',
        quantity=1,
        strike_price=20.20,
        notional_curr_code='USD',
        date_of_trade=today,
        maturity_date=today + timedelta(days=365)
    )


# TODO: revisit
@pytest.fixture
def dummy_derivative_json(dummy_derivative):
    return {
        'code': dummy_derivative.code,
        'buying_party': dummy_derivative.buying_party,
        'selling_party': dummy_derivative.selling_party,
        'asset': dummy_derivative.asset,
        'quantity': dummy_derivative.quantity,
        'strike_price': dummy_derivative.strike_price,
        'notional_curr_code': dummy_derivative.notional_curr_code,
        'maturity_date': str(dummy_derivative.maturity_date),
        'date_of_trade': str(dummy_derivative.date_of_trade)
    }


# TODO: revisit
@pytest.fixture
def dummy_abs_derivative(dummy_derivative):
    # Get the current date
    today = date.today()
    # Modify the dummy derivatives date of trade to make it absolute
    dummy_derivative.date_of_trade = today - timedelta(days=365)
    # Return absolute dummy derivative
    return dummy_derivative


# TODO: revisit
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


# TODO: revisit
@pytest.fixture
def dummy_updates():
    return {
        'buying_party': 'newfoo',
        'selling_party': 'newbar',
        'asset': 'newbaz'
    }


@pytest.fixture
def free_report_id(dummy_report):
    # Add dummy report to database session
    db.session.add(dummy_report)
    db.session.flush()
    # Store the id of the new report
    free_id = dummy_report.id
    # Discard the new report from the session to free the id
    db.session.rollback()
    # Return the free id
    return free_id


@pytest.fixture
def dummy_report():
    today = date.today()

    return ReportHead(
        target_date=today,
        creation_date=today,
        version=1,
        derivative_count=0,
    )


@pytest.fixture
def date_from():
    return date.today() - timedelta(days=8)


@pytest.fixture
def date_to():
    return date.today() - timedelta(days=1)
