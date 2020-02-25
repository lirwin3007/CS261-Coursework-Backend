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
    # Extract body from request
    body = request.get_json(silent=True) or {}

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


@ReportBlueprint.route('/get-report-head/<report_id>')
def getReportHead(report_id):
    # Get report head from the database
    head = report_management.getReportHead(report_id)

    # Verify report exists
    if head is None:
        return abort(404, f'report with id {report_id} not found')

    # Make response
    return jsonify(report=head)


@ReportBlueprint.route('/get-report-data/<report_id>')
def getReportData(report_id):
    # Get report data from report file
    data = report_management.getReportData(report_id)

    # Verify report exists
    if data is None:
        return abort(404, f'report with id {report_id} not found')

    # Make response
    return jsonify(report=data)


@ReportBlueprint.route('/download-report/<format>/<report_id>')
def downloadReport(format, report_id):
    # Verify report exists
    if report_management.getReportHead(report_id) is None:
        return abort(404, f'report with id {report_id} not found')

    if format.upper() == 'PDF':
        # Generate PDF file and return path
        file_path = report_management.createPDF(report_id)

        # Delete the pdf after it is sent
        @after_this_request
        def deleteFile(response):
            os.remove(file_path)
            return response
    else:
        # Default to the report CSV
        file_path = os.path.realpath(f'res/reports/{report_id}.csv')

    # Return the file
    return send_file(file_path)


@ReportBlueprint.route('/index-pending-reports')
def indexPendingReports():
    dates = report_management.getPendingReportDates()
    return jsonify(dates=dates)


@ReportBlueprint.route('/generate-report/<target_date>')
def generateReport(target_date):
    id = report_management.generateReport(target_date)

    if id is None:
        abort(400, f'failed to generate report for: {target_date}')

    return jsonify(id=id)


@ReportBlueprint.route('/generate-all-reports')
def generateReports():
    report_management.generateAllReports()
    return '', 204
