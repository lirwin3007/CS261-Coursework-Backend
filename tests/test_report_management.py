# Local application imports
from backend.managers import report_management
from backend.db import db


def testGetReportHeadRetrievesReportHead(dummy_report_head):
    # Add dummy report to database session
    db.session.add(dummy_report_head)
    db.session.flush()

    # Assert that getReportHead returns the report
    assert report_management.getReportHead(dummy_report_head.id) == dummy_report_head


def testGetReportHeadReturnsNoneIfNotFound(free_report_id):
    # Assert that None is returned for the free id
    assert report_management.getReportHead(free_report_id) is None


def testGetReportDataReturnsNoneIfNotFound(free_report_id):
    # Assert that None is returned for the free id
    assert report_management.getReportData(free_report_id) is None
