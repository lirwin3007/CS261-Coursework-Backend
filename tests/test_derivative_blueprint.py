# Third party imports
from flask import jsonify
import pytest

# Local application imports
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
    # Assert that the response data is the derivative serialized
    assert response.data == jsonify(derivative=dummy_derivative).data


def testGetDerivativeWillReturn404(test_client, free_derivtive_id):
    # Make request and retrieve response
    url = f'/derivative-management/get-derivative/{free_derivtive_id}'
    response = test_client.get(url)
    # Assert that a 404 HTTP error is returned
    assert response.status_code == 404
