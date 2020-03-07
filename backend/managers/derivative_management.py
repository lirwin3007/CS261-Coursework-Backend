# Standard library imports
import datetime

# Third party imports
from sqlalchemy import asc, desc

# Local application imports
from backend.derivatex_models import Derivative, Action, ActionType
from backend.db import db
from backend.utils import clamp, AbsoluteDerivativeException


def getDerivative(derivative_id):
    """ Retrieve the derivative from the database that has the given ID.

    Args:
        derivative_id (int): The ID of the desired derivative.

    Returns:
        Derivative: The derivative in the database with the corrosponding ID.
    """
    return Derivative.query.filter_by(deleted=False, id=derivative_id).first()


def addDerivative(derivative, user_id):
    """ Adds a derivative and a corrosponding user action to the database

    Args:
        derivative (Derivative): The derivative to be added to the database.
        user_id (int): The ID of the user requesting the derivative addition.

    Returns:
        None
    """
    # Add the derivative to the database session
    db.session.add(derivative)
    db.session.flush()

    # Flag that the derivative needs to be reported
    derivative.reported = False

    # Add corrosponding user action to the database session
    action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.ADD)
    db.session.add(action)
    db.session.flush()


def deleteDerivative(derivative, user_id):
    """ Labels a derivative in the database as deleted and registers a
    user action that corrosponds to the deletion.

    Args:
        derivative (Derivative): The derivative to be marked as deleted.
        user_id (int): The ID of the user requesting the derivative addition.

    Returns:
        None

    Raises:
        AbsoluteDerivativeException: If the derivative is absolute
    """
    if derivative.absolute:
        raise AbsoluteDerivativeException

    # Mark the derivative as deleted
    derivative.deleted = True

    # Flag that the derivative needs to be reported
    derivative.reported = False

    # Register the user deleting the derivative
    action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.DELETE)
    db.session.add(derivative)
    db.session.add(action)


def updateDerivative(derivative, user_id, updates):
    """ Updates the attributes of the given derivative with new values and
    registers corrosponding actions.

    Args:
        derivative (Derivative): The derivative to be updated.
        user_id (int): The ID of the user performing the derivative update.
        updates (dict): A dictionary of derivative attribute, value pairs.

    Returns:
        list: A list of dictionarys that each log an update to an derivative attribute.

    Raises:
        AbsoluteDerivativeException: If the derivative is absolute
    """
    if derivative.absolute:
        raise AbsoluteDerivativeException

    # Apply and log all updates to the derivative
    update_log = []
    for attribute, new_value in updates.items():
        # Restrict updatable attributes
        if not hasattr(derivative, attribute) or attribute in ['id', 'deleted', 'modified']:
            continue

        # Retrieve the current value
        old_value = getattr(derivative, attribute)

        # Ignore the update if it doesn't change anything
        if old_value == new_value:
            continue

        # Cast date attributes to strings
        if isinstance(old_value, datetime.date):
            old_value = str(old_value)

        # Perform update
        setattr(derivative, attribute, new_value)

        # Log update one at a time
        log = {
            'attribute': attribute,
            'old_value': old_value,
            'new_value': new_value
        }

        # Register update action
        action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.UPDATE, update_log=log)
        db.session.add(action)
        update_log.append(log)

    if update_log:
        # Flag that the derivative needs to be reported
        derivative.reported = False

        # Add the updated derivative to the session
        db.session.add(derivative)
        db.session.flush()

    # Return the update log
    return update_log


def indexDerivatives(page_size, page_number, order_key, reverse_order,  # noqa: C901
                     min_notional, max_notional, min_strike, max_strike,
                     min_maturity, max_maturity, min_trade_date, max_trade_date,
                     buyers, sellers, assets):
    # Enforce a minimum page size
    page_size = max(page_size, 3)

    # Create base query
    query = Derivative.query

    # Apply query filters
    if min_strike is not None:
        query = query.filter(Derivative.strike_price >= min_strike)
    if max_strike is not None:
        query = query.filter(Derivative.strike_price <= max_strike)
    if min_maturity is not None:
        query = query.filter(Derivative.maturity_date >= min_maturity)
    if max_maturity is not None:
        query = query.filter(Derivative.maturity_date <= max_maturity)
    if min_trade_date is not None:
        query = query.filter(Derivative.date_of_trade >= min_trade_date)
    if max_trade_date is not None:
        query = query.filter(Derivative.date_of_trade <= max_trade_date)
    if buyers:
        query = query.filter(Derivative.buying_party.in_(buyers))
    if sellers:
        query = query.filter(Derivative.selling_party.in_(sellers))
    if assets:
        query = query.filter(Derivative.asset.in_(assets))

    # Order the query if the order key is a field in the schema
    if order_key in Derivative.__table__.columns:
        query = query.order_by(desc(order_key) if reverse_order else asc(order_key))

    # Determine if there is any post query processing
    post_filters = min_notional is not None or max_notional is not None
    post_ordering = isinstance(getattr(Derivative, order_key, None), property)

    # If there is a post query processing, execute the query and apply afterwards
    if post_filters or post_ordering:
        # Execute sql query
        derivatives = query.all()

        # Apply post ordering
        if post_ordering:
            derivatives.sort(key=lambda d: getattr(d, order_key), reverse=reverse_order)

        # Apply post query filters
        if min_notional is not None:
            derivatives = [d for d in derivatives if d.notional_value >= min_notional]
        if max_notional is not None:
            derivatives = [d for d in derivatives if d.notional_value <= max_notional]

        # Paginate derivatives
        page_count = len(derivatives) // page_size + 1
        offset = page_size * (clamp(page_number, 1, page_count) - 1)
        derivatives = derivatives[offset:offset + page_size]
    else:
        # Paginate query
        page_count = query.count() // page_size + 1
        offset = page_size * (clamp(page_number, 1, page_count) - 1)
        query = query.limit(page_size).offset(offset)
        # Execute sql query
        derivatives = query.all()

    # Return derivatives and page count
    return derivatives, page_count
