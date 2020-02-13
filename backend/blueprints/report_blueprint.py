# Third party imports
from flask import Blueprint

# Local application imports
# You can import database models with 'from backend.derivatex_models import Derivative, User, Action'
# from backend.managers import report_management
# from backend.derivatex_models import Derivative, Report
# from backend.db import db

# Instantiate new blueprint
ReportBlueprint = Blueprint('reportManagement',
                            __name__,
                            url_prefix='/report-management')


# Routes
@ReportBlueprint.route('/index-reports/<date_from>/<date_to>')
def indexReports(date_from, date_to):
    # Get ids from database
    reports = report_management.indexReports(date_from, date_to)
    # Make response
    return reports


@ReportBlueprint.route('/get-report/<report_id>')
def getReport(report_id):
    # Get report from file system and info from db
    report = report_management.indexReports(date_from, date_to)
    # Make response
    return report


@ReportBlueprint.route('/download-report/<format>/<report_id>')
def downloadReport(format, report_id):
    if (format == "CSV"):
        CSV_file = report_management.downloadCSV(report_id)
        return CSV_file
    PDF_file = report_management.downloadPDF(report_id)
    return PDF_file
