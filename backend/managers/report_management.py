# Standard library imports
from flask import send_file

# Local application imports
from backend.derivatex_models import Report, Derivative
from backend.db import db
from backend.util import clamp


def indexReports(body, page_size, page_number, date_from, date_to):  # noqa: C901
    # Create base query
    query = Report.query

    # Apply filters to query
    query = query.filter(operator.ge(Report.__table__.collumns[target_date], date_from))
    query = query.filter(operator.le(Report.__table__.collumns[target_date], date_to))

    # Order query
    query = query.order_by(asc(target_date))

    # Determine page count
    page_count = query.count() // page_size + 1
    # Calculate index offset
    offset = page_size * (clamp(page_number, 1, page_count) - 1)
    # Paginate query
    query = query.limit(page_size).offset(offset)
    # Execute SQL query
    reports = query.all()

    return reports, page_count


def getReport(report_id):
    # Locate and read CSV
    # Turn data into list
    # Return list
    return {"report_id": 1, "report": {"derivatives": [1, 2, 3]}}


def createCSV(report_id):
    try:
        # Make CSV file and return path
        return "static/temp/" + report_id + ".csv"
    except Exception as e:
        print(e)


def createPDF(report_id):
    try:
        # Make PDF file and return path
        return "static/temp/" + report_id + ".csv"
    except Exception as e:
        print(e)


def generateReports():
    # Select dates from Derivative table not reported
    # Create new entry in report table with stats
    # Create new CSV file in static with id
    # Populate CSV with derivatives
    return True
