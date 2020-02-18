

def testGetDerivativeWillReturn404(test_client, free_derivtive_id):
    # Form endpoint path
    endpoint = '/derivative-management/get-derivative/{}'.format(free_derivtive_id)
    # Make request and retrieve response
    response = test_client.get(endpoint)
    # Assert that a 404 HTTP error is returned
    assert response.status_code == 404
