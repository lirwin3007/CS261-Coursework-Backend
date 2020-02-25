import pytest


def testGetReportWillReturn404(test_client, free_report_id):
    # Make request and retrieve response
    url = f'/report-management/get-report/{free_report_id}'
    response = test_client.get(url)
    # Assert that a 404 HTTP error is returned
    assert response.status_code == 404


@pytest.mark.skip(reason='Test not fully implemented')
def testIndexReportWillReturnCorrectFormat(test_client):
    # Make request and retrieve response
    url = f'/report-management/index-reports?date_from=2018-01-01&date_to=2020-01-01'
    response = test_client.get(url)
    # Assert that the response body is the correct format
    assert response.is_json
    # json = response.get_json()
    # get json contents
    # assert contents of correct types
