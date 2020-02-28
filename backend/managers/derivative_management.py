# Standard library imports
import datetime
import operator

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


def indexDerivatives(filter_dict, page_size, page_number):  # noqa: C901
    """ Enumerates a page of derivatives from filtered and sorted subset of
    all derivatives in the database.

    Args:
        filter_dict (dict): A dictionary of filtering and ordering keys.
        page_size (int): The number of derivatives that form a page.
        page_number (int): The page number offset of the index list.

    Returns:
        (tuple): tuple containing:
            derivatives (list): The list of derivatives that make up the page
            page_count (int): The number of pages all the derivatives are spread across
    """
    # Create base query
    query = Derivative.query

    # Initialise pre and post query filter sets
    pre_filters = set()
    post_filters = set()

    # Create filters from the filter dictionary
    for filter_name, value in filter_dict.items():
        # Determine filter comparison operation from the filter name prefix
        if filter_name.startswith('min_'):
            # Select >= operator and extract filter name
            filter_name = filter_name[4:]
            op = operator.ge
        elif filter_name.startswith('max_'):
            # Select <= operator and extract filter name
            filter_name = filter_name[4:]
            op = operator.le
        else:
            # Default to equality
            op = operator.eq

        # The filter attribute is a member of the Derivative schema
        if filter_name in Derivative.__table__.columns:
            # Create and add filter to pre-filters
            filter = op(Derivative.__table__.columns[filter_name], value)
            pre_filters.add(filter)

        # The filter attribute is a property of the Derivative class
        elif isinstance(getattr(Derivative, filter_name, None), property):
            # Create and add filter to post-filters
            filter = lambda d: op(getattr(d, filter_name), value)  # noqa: E731
            post_filters.add(filter)

    # Apply all pre-filters to the base query
    for f in pre_filters:
        query = query.filter(f)

    # Determine derivative ordering key
    order_key = filter_dict.get('order_key') or ''
    reverse_order = filter_dict.get('reverse_order') or False

    # Order the query if the order key is a field in the schema
    if order_key in Derivative.__table__.columns:
        query = query.order_by(desc(order_key) if reverse_order else asc(order_key))

    # Determine if there is a post ordering
    post_ordering = isinstance(getattr(Derivative, order_key, None), property)

    # If there is a post query ordering or filters execute the query and apply
    if post_filters or post_ordering:
        # Execute sql query
        derivatives = query.all()

        # Apply post ordering
        if post_ordering:
            derivatives.sort(key=lambda d: getattr(d, order_key), reverse=reverse_order)

        # Apply all post-query filters to derivatives
        for f in post_filters:
            derivatives = [d for d in derivatives if f(d)]

        # Determine page count
        page_count = len(derivatives) // page_size + 1
        # Calculate index offset
        offset = page_size * (clamp(page_number, 1, page_count) - 1)
        # Paginate derivatives
        derivatives = derivatives[offset:offset + page_size]
    else:
        # Determine page count
        page_count = query.count() // page_size + 1
        # Calculate index offset
        offset = page_size * (clamp(page_number, 1, page_count) - 1)
        # Paginate query
        query = query.limit(page_size).offset(offset)
        # Execute sql query
        derivatives = query.all()

    # Return derivatives and page count
    return derivatives, page_count
