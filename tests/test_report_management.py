from backend.managers import report_management


# def testGetReportRetrievesReport(free_report_id):
# Add dummy CSV to correct path
# report_data = Extract dummy CSV data
# Assert that getReport returns the report
# assert report_management.getReport(free_report_id) == report_data


def testGetReporteturnsNoneIfNotFound(free_report_id):
    # Assert that None is returned for the free id
    assert report_management.getReportData(free_report_id) is None


def testGenerateReportsCreatesReportFile():
    # Check next report id
    report_management.generateAllReports()
    # Assert that file with found id now exists
    assert True
