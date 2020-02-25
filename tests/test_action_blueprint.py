# Local application imports
from backend.db import db

def testGetAction(test_client, dummy_action):
    # Add dummy derivative to session
    db.session.add(dummy_action)
    db.session.flush()

    # Make request and retrieve response
    endpoint = f'/action-management/get-action/{dummy_action.id}'
    response = test_client.get(endpoint)

    # Assert that the response status is 200
    assert response.status_code == 200

    # Assert that the response body is the serialization of the action
    assert response.is_json
    expected_response = jsonify(action=dummy_action)
    assert response.get_json() == expected_response.get_json()
