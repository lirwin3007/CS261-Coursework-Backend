

def testGetReportWillReturn404(test_client, free_report_id):
    # Make request and retrieve response
    url = f'/report-management/get-report/{free_report_id}'
    response = test_client.get(url)
    # Assert that a 404 HTTP error is returned
    assert response.status_code == 404
