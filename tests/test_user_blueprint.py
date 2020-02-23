

# Check that trying to look for a non-existent user will result in a 404 error
def testGetUserWillReturn404(test_client, free_user_id):
    # Form endpoint path
    endpoint = '/get-user/{}'.format(free_user_id)
    # Make request and retrieve response
    response = test_client.get(endpoint)
    # Assert that a 404 HTTP error is returned
    assert response.status_code == 404
