# Standard library imports
import datetime
import operator

# Third party imports
from sqlalchemy import asc, desc

# Local application imports
from backend.derivatex_models import Derivative, Action, ActionType
from backend.db import db
from backend.util import clamp


def getDerivative(derivative_id):
    """Example Google style docstrings.

    This module demonstrates documentation as specified by the `Google Python
    Style Guide`_. Docstrings may extend over multiple lines. Sections are created
    with a section header and a colon followed by a block of indented text.

    Example:
        Examples can be given using either the ``Example`` or ``Examples``
        sections. Sections support any reStructuredText formatting, including
        literal blocks::

            $ python example_google.py

    Section breaks are created by resuming unindented text. Section breaks
    are also implicitly created anytime a new section starts.

    Attributes:
        module_level_variable1 (int): Module level variables may be documented in
            either the ``Attributes`` section of the module docstring, or in an
            inline docstring immediately following the variable.

            Either form is acceptable, but the two should not be mixed. Choose
            one convention to document module level variables and be consistent
            with it.

    .. _Google Python Style Guide:
       http://google.github.io/styleguide/pyguide.html

    """
    # Query database for the derivative
    return Derivative.query.filter_by(deleted=False, id=derivative_id).first()


def addDerivative(derivative, user_id):
    # Add the derivative to the database session
    db.session.add(derivative)
    db.session.flush()

    # Add corrosponding user action to the database session
    action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.ADD)
    db.session.add(action)
    db.session.flush()


def deleteDerivative(derivative, user_id):
    # The derivative has already been flagged as deleted or is absolute, return
    if derivative.deleted or derivative.absolute:
        return

    # Mark the derivative as deleted
    derivative.deleted = True

    # Register the user deleting the derivative
    action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.DELETE)
    db.session.add(derivative)
    db.session.add(action)
    db.session.commit()


def updateDerivative(derivative, user_id, updates):
    # The derivative has been deleted or is absolute, return
    if derivative.deleted or derivative.absolute:
        return

    # Apply and log all updates to the derivative
    update_log = []
    for attribute, new_value in updates.items():
        # Restrict updatable attributes
        if not hasattr(derivative, attribute) or attribute in ['id', 'deleted', 'modified']:
            continue

        # Retrieve the current value
        old_value = getattr(derivative, attribute)
        if isinstance(old_value, datetime.date):
            old_value = str(old_value)

        # Perform update
        setattr(derivative, attribute, new_value)

        # Log update
        update_log.append({
            'attribute': attribute,
            'old_value': old_value,
            'new_value': new_value
        })

    # Register the derivative updates and corrosponding user action to the database session
    action = Action(derivative_id=derivative.id, user_id=user_id, type=ActionType.UPDATE, update_log=update_log)
    db.session.add(action)
    db.session.add(derivative)
    db.session.flush()

    # Return the update log
    return update_log


# TODO: simplify / optimize performance
def indexDerivatives(filter_dict, page_size, page_number):  # noqa: C901
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
