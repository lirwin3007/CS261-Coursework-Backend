def testGetReportWillReturn404(test_client, free_report_id):
    # Make request and retrieve response
    url = f'/report-management/get-report/{free_report_id}'
    response = test_client.get(url)
    # Assert that a 404 HTTP error is returned
    assert response.status_code == 404


def testIndexReportWillReturnCorrectFormat(test_client, date_from, date_to):
    # Make request and retrieve response
    url = f'/report-management/index-reports?date_from={date_from}&date_to={date_to}'
    response = test_client.get(url)
    # Assert that the response body is the correct format
    assert response.is_json
    # json = response.get_json()
    # get json contents
    # assert contents of correct types
