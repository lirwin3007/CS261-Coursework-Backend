# Standard library imports
from datetime import date
import csv

# Third party imports
from sqlalchemy import func, asc

# Local application imports
from backend.derivatex_models import Report, Derivative
from backend.db import db
from backend.util import clamp


def indexReports(date_from, date_to, page_size, page_number):
    # Create base query
    query = Report.query

    # Filter and order query
    query.filter(date_from < Report.target_date)
    query.filter(Report.target_date < date_to)
    query = query.order_by(asc(Report.target_date))

    # Paginate query
    page_count = query.count() // page_size + 1
    offset = page_size * (clamp(page_number, 1, page_count) - 1)
    query = query.limit(page_size).offset(offset)

    # Execute query
    reports = query.all()

    return reports, page_count


def getReport(report_id):
    # Locate and read CSV
    # Turn data into list
    # Return list
    return {'report_id': 1, 'report': {'derivatives': [1, 2, 3]}}


def createCSV(report_id):
    try:
        # Make CSV file and return path
        return f'res/temp/{report_id}.csv'
    except Exception as e:
        print(e)


def createPDF(report_id):
    try:
        # Make PDF file and return path
        return f'res/temp/{report_id}.pdf'
    except Exception as e:
        print(e)


def generateReports():
    report_dates = db.session.query(Derivative.date_of_trade.distinct()).filter_by(reported=False).all()

    for target_date in report_dates:
        # Create new Report and flush session
        report = Report(target_date=target_date, creation_date=date.today())
        db.session.add(report)
        db.session.flush()

        # Make CSV and open for writing
        with open(f'res/reports/{report.id}.csv', 'w') as file:
            writer = csv.writer(file)
            # Filter derivatives for the target_date that have not been deleted
            query = Derivative.query.filter_by(date_of_trade=target_date, deleted=False)
            # Execute query
            derivatives = query.all()

            for d in derivatives:
                row = [d.id, d.code, d.buying_party, d.selling_party,
                       d.asset, d.quantity, d.strike_price, d.notional_curr_code,
                       d.date_of_trade, d.maturity_date]

                # Write the derivative to the file
                writer.writerow(row)

                # Mark the derivative as reported
                d.reported = True
                db.session.add(d)

        # Get creation date
        creation_date = date.today()

        # Get next version of report or initialise as 0
        version = db.session.query(func.max(Report.version)).filter_by(target_date=target_date).scalar()
        if version is None:
            version = 0
        else:
            version += 1

        # Set the report version
        report.version = version

        # Commit session to database
        db.session.add(report)
        db.session.commit()

    return True
