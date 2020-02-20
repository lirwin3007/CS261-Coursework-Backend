# Standard library imports
import datetime

# Third party imports
from flask import jsonify
import pytest

# Local application imports
from backend.derivatex_models import Derivative
from backend.db import db


@pytest.mark.skip()
def testGetDerivativeRetrievesDerivative(test_client, dummy_derivative):
    # Add dummy derivative to session
    db.session.add(dummy_derivative)
    db.session.flush()

    # Make request and retrieve response
    url = f'/derivative-management/get-derivative/{dummy_derivative.id}'
    response = test_client.get(url)

    # Assert that the response status is 200 OK
    assert response.status_code == 200

    # Assert that the response body is the serialization of the derivative
    assert response.is_json()
    assert response.get_json() == jsonify(derivative=dummy_derivative)


def testGetDerivativeWillReturn404(test_client, free_derivtive_id):
    # Make request and retrieve response
    url = f'/derivative-management/get-derivative/{free_derivtive_id}'
    response = test_client.get(url)
    # Assert that a 404 HTTP error is returned
    assert response.status_code == 404


def testAddDerivativeStoresDerivative(test_client, dummy_derivative_json, dummy_user):
    # Add dummy user to database session
    db.session.add(dummy_user)
    db.session.flush()

    # Form POST request body
    body = {
        'user_id': dummy_user.id,
        'derivative': dummy_derivative_json
    }

    # Make request and retrieve response
    url = '/derivative-management/add-derivative'
    response = test_client.post(url, json=body)

    # Assert that a json body is returned
    assert response.is_json

    # Extract derivative id from response body
    derivative_id = response.get_json().get('id')

    # Assert that the derivative has been stored
    derivative = Derivative.query.get(derivative_id)
    assert derivative is not None

    # Assert that the stored derivative is correct
    for attribute, value in dummy_derivative_json.items():
        stored_value = getattr(derivative, attribute)

        if isinstance(stored_value, datetime.date):
            stored_value = str(stored_value)

        assert stored_value == value
