# Standard library imports
from datetime import datetime
import operator
import csv

# Third party imports
from flask import send_file
from sqlalchemy import func

# Local application imports
from backend.managers import derivative_management
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
    report_dates = db.session.query(Derivative.date_of_trade.distinct()).filter_by(reported=False).all()

    for target_date in report_dates:
        # Get next report id or initialise as 0
        report_id = db.session.query(func.max(Report.id)).scalar()
        if report_id is None:
            report_id = 0
        else
            report_id += 1

        # Make CSV and open for writing
        with open('static/reports/' + report_id + '.csv', 'w', newline=' ') as file:
            writer = csv.writer(file)
            # Get derivatives for target_date that arent deleted
            derivatives = Derivative.query.filter_by(date_of_trade=target_date).filter_by(deleted=False).order_by(asc(id)).all()
            for d in derivatives:
                # Write each derivative to file and set reported attribute
                writer.writerow([d.id, d.code, d.buying_party, d.selling_party, d.asset, d.quantity, d.strike_price, d.currency_code, d.date_of_trade, d.maturity_date])
                derivative_management.getDerivative(d.id).reported = True

        # Get creation date
        creation_date = datetime.date(datetime.now())

        # Get next version of report or initialise as 0
        version = db.session.query(func.max(Report.version)).filter_by(target_date=target_date).scalar()
        if version is None:
            version = 0
        else
            version += 1

        report = Report(report_id, target_date, creation_date, version)
        db.add(report)
        db.flush()
        db.session.commit()

    return True
