# Standard library imports
import os

from flask import Blueprint, abort, jsonify, request, send_file, after_this_request
# Third party imports

# Local application imports
from backend.managers import report_management

# Instantiate new blueprint
ReportBlueprint = Blueprint('reporting',
                            __name__,
                            url_prefix='/reporting')


# Routes
@ReportBlueprint.route('/index-reports')
def indexReports():
    # Determine body from request
    if request.data and request.is_json:
        body = request.get_json()
    else:
        body = {}

    # Retrieve input data
    date_from = request.args.get('date_from', type=str)
    date_to = request.args.get('date_to', type=str)

    # Determine page parameters
    page_size = max(body.get('page_size') or 15, 1)
    page_number = request.args.get('page_number', default=0, type=int)

    # Index reports
    reports, page_count = report_management.indexReports(date_from,
                                                         date_to,
                                                         page_size,
                                                         page_number)
    # Make response
    return jsonify(page_count=page_count, reports=reports)


@ReportBlueprint.route('/get-report/<report_id>')
def getReport(report_id):
    # Get report from file system and info from db
    report = report_management.getReport(report_id)

    # Verify report exists
    if report is None:
        return abort(404, f'report with id {report_id} not found')

    # Make response
    return jsonify(report=report)


@ReportBlueprint.route('/download-report/<format>/<report_id>')
def downloadReport(format, report_id):
    if format == 'CSV':
        # Generate CSV and return file path
        path_to_file = report_management.downloadCSV(report_id)
    else:
        # Generate PDF and return file path
        path_to_file = report_management.downloadPDF(report_id)

    # Verify file exists
    if path_to_file is None:
        return abort(404, f'report with id {report_id} not found')

    # Set to delete file after it is sent
    @after_this_request
    def deleteFile(response):
        os.remove(path_to_file)
        return response

    # Return the file
    return send_file(path_to_file)


@ReportBlueprint.route('/debug-generate-reports')
def generateReportsDebugEndpoint():
    report_management.generateReports()
    return '', 204
