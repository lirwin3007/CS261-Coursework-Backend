# Local application imports
from backend.db import db

def testGetAction(test_client, dummy_action):
    # Add dummy derivative to session
    db.session.add(dummy_derivative)
    db.session.flush()

    # Make request and retrieve response
    url = f'/derivative-management/get-action/{dummy_derivative.id}'
    response = test_client.get(url)

    # Assert that the response status is 200 OK
    assert response.status_code == 200

    # Assert that the response body is the serialization of the derivative
    assert response.is_json
    expected_response = jsonify(derivative=dummy_derivative)
    assert response.get_json() == expected_response.get_json()