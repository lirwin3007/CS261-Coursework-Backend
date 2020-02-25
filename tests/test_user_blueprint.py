# Local application imports
from backend.db import db


# Check that trying to look for a non-existent user will result in a 404 error
def testGetUserWillReturn404(test_client, free_user_id):
    # Form endpoint path
    endpoint = '/user-account-control/get-user/{}'.format(free_user_id)
    # Make request and retrieve response
    response = test_client.get(endpoint)
    # Assert that a 404 HTTP error is returned
    assert response.status_code == 404


def testAuthenticateUserValidCredentialsReturn200(test_client, dummy_user):
    # Add dummy user to database session
    db.session.add(dummy_user)
    db.session.flush()

    # Form POST request body
    body = {
        "username": dummy_user.email,
        "password": dummy_user.password
    }

    # Form endpoint path
    endpoint = '/user-account-control/authenticate-user'

    # Make request and retrieve response
    response = test_client.post(endpoint, json=body)

    # Assert that a 200 HTTP error is returned
    assert response.status_code == 200


def testAuthenticateUserIncorrectPasswordReturn401(test_client, dummy_user):
    # Add dummy user to database session
    db.session.add(dummy_user)
    db.session.flush()

    # Form POST request body
    body = {
        "username": dummy_user.email,
        "password": dummy_user.password + "password"
    }

    # Form endpoint path
    endpoint = '/user-account-control/authenticate-user'

    # Make request and retrieve response
    response = test_client.post(endpoint, json=body)

    # Assert that a 401 HTTP error is returned
    assert response.status_code == 401