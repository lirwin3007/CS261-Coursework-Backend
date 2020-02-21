# Standard library imports
from datetime import date
import csv

# Third party imports
from sqlalchemy import asc

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
    with open(f'res/reports/{report.id}.csv') as file:
        reader = csv.reader(file, delimiter=",")
        # Create and return list storing derivative data in the report
        return [row for row in reader]


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
    # Filter the unreported derivatives
    query = Derivative.query.filter_by(reported=False)
    # Query distinct dates with unreported derivatives
    query = query.with_entities(Derivative.date_of_trade).distinct()
    # Execute query and extract dates from sqlalchemy.util._collections.result
    report_dates = [d[0] for d in query.all()]
    report_dates = [report_dates[0]]

    for target_date in report_dates:
        # Get next version of report or initialise as 0
        query = Report.query.filter_by(target_date=target_date)
        query = query.with_entities(Report.version)
        versions = [v[0] for v in query.all()]
        versions = [versions[0]]
        version = max(versions) or 0

        # Create new Report
        report = Report(target_date=target_date,
                        creation_date=date.today(),
                        version=version + 1)

        # Add report to database session
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

        # Commit session to database
        db.session.commit()

    return True
