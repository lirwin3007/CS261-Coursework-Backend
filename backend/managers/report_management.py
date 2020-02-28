# Standard library imports
from datetime import date
import csv
import os

# Third party imports
from sqlalchemy import asc

# Local application imports
from backend.derivatex_models import ReportHead, Derivative
from backend.db import db
from backend.utils import clamp
from backend.utils import MyFPDF


def indexReports(from_date, to_date, page_size, page_number):
    """ Enumerates a page of reports from a date range filtered subset of
    all reports in the database.

    Args:
        from_date (date): The earliest date a returned report can be for.
        to_date (date): The latest date a returned report can be for.
        page_size (int): The number of reports that form a page.
        page_number (int): The page number offset of the index list.

    Returns:
        (tuple): tuple containing:
            reports (list): The list of reports that make up the page
            page_count (int): The number of pages all the reports are spread across
    """
    # Create base query
    query = ReportHead.query

    # Filter and order query
    if from_date is not None:
        query = query.filter(ReportHead.target_date >= from_date)

    if to_date is not None:
        query = query.filter(ReportHead.target_date <= to_date)

    query = query.order_by(asc(ReportHead.target_date))

    # Paginate query
    page_count = query.count() // page_size + 1
    offset = page_size * (clamp(page_number, 1, page_count) - 1)
    query = query.limit(page_size).offset(offset)

    # Execute query
    reports = query.all()

    return reports, page_count


def getReportHead(report_id):
    """ Retrieve the report metadata from the database that has the given ID.

    Args:
        report_id (int): The ID of the desired report.

    Returns:
        Report: The report in the database with the corrosponding ID.
    """
    return ReportHead.query.get(report_id)


def getReportData(report_id):
    """ Retrieve the report contents from the CSV file of the report that has the given ID.

    Args:
        report_id (int): The ID of the desired report.

    Returns:
        Report: A list of dictionaries which represent each derivative in the report
    """
    # Form report CSV path
    path = f'res/reports/{report_id}.csv'

    if os.path.isfile(path):
        # Open report file if it exists
        with open(path) as file:
            # Read report using dictionary reader
            return list(csv.DictReader(file))

    # Report does not exist
    return None


def createPDF(report_id):
    """ Create a temporary PDF file containing the data required by the trade repository.

    Args:
        report_id (int): The ID of the report which a PDF is required for.

    Returns:
        String: A string corresponding to the path to the generated PDF.
    """
    # Get report derivative rows as list of lists
    data = getReportData(report_id)
    date = data[0]['date_of_trade']

    # Creates design for table to be added to PDF
    header = """
    <font size="8" face="Courier New" >
    <table align="center" width="100%">
    <thead><tr>
    <th width="15%">Trade Code</th><th width="8%">Trade Date</th>
    <th width="18%">Asset</th><th width="6%">QTY</th><th width="7%">Buy PTY</th>
    <th width="7%">Sell PTY</th><th width="9%">Notional Val</th><th width="4%">Curr</th>
    <th width="8%">Mat Date</th><th width="6%">Price</th><th width="4%">Curr</th>
    <th width="8%">Strike Price</th>
    </tr></thead>
    """

    # Adds every row of data to html which will be used to create table
    html_out = ''
    grey = True
    for derivative in data:
        html_out += '<tr bgcolor="#E1E1E1"><td>' if grey else '<tr bgcolor="#FFFFFF"><td>'
        grey = not grey
        html_out += derivative['code']
        html_out += ('</td><td>' + derivative['date_of_trade'])
        html_out += ('</td><td>' + derivative['asset'])
        html_out += ('</td><td>' + derivative['quantity'])
        html_out += ('</td><td>' + derivative['buying_party'])
        html_out += ('</td><td>' + derivative['selling_party'])
        html_out += ('</td><td>' + "{:.2f}".format(float(derivative['notional_value'])))
        html_out += ('</td><td>' + derivative['notional_curr_code'])
        html_out += ('</td><td>' + derivative['maturity_date'])
        html_out += ('</td><td>' + derivative['underlying_price'])
        html_out += ('</td><td>' + derivative['underlying_curr_code'])
        html_out += ('</td><td>' + "{:.2f}".format(float(derivative['strike_price'])))
        html_out += '</td></tr>\n'

    # Create final html that represents table
    html = header + html_out + '</tbody></table>'

    # Create PDF
    pdf = MyFPDF('P', 'mm', 'letter')
    pdf.set_top_margin(margin=18)
    pdf.set_auto_page_break(True, 27)
    pdf.add_page()
    pdf.alias_nb_pages()
    pdf.set_font('Arial', style='B', size=14)
    pdf.cell(200, 5, txt=f'Derivative Report {date}', ln=1, align='C')
    pdf.write_html(html)

    file_path = f'res/temp/{report_id}.pdf'

    pdf.output(file_path)

    # Return path to PDF
    return os.path.realpath(file_path)


def getPendingReportDates():
    """ Creates a list containing all dates that contain unreported derivatives.

    Args:
        None

    Returns:
        Dates: A list of distinct date objects that have unreported derivatives in the database.
    """
    # Filter the unreported derivatives
    query = Derivative.query.filter_by(reported=False)
    # Query the distinct dates of unreported derivatives
    query = query.with_entities(Derivative.date_of_trade).distinct()
    # Execute query and extract dates from sqlalchemy.util._collections.result
    return [d[0] for d in query.all()]


def generateAllReports():
    """ Create a new report for each date that contains unreported derivatives

    Args:
        None

    Returns:
        report_ids: A list containing the ids of all the newly generated reports
    """
    target_dates = getPendingReportDates()
    report_ids = []

    # Generate a report for each of the target_dates
    for target_date in target_dates:
        id = generateReport(target_date)
        report_ids.append(id)

    return report_ids


def generateReport(target_date):
    """ Create a new report for the specified date

    Args:
        target_date (date): The date for which a new report is required

    Returns:
        id: The id of the newly generated report for the requested date
    """
    # Get all none-deleted erivatives traded on the target_date
    derivatives = Derivative.query.filter_by(date_of_trade=target_date,
                                             deleted=False).all()
    # Return if there are no derivatives to report
    if not derivatives:
        return None

    # Get all the existing reports for the given target_date
    reports = ReportHead.query.filter_by(target_date=target_date).all()

    # Obtain latest report version number or default to 0
    version = max([report.version for report in reports], default=0)

    # Create new report metadata object
    report = ReportHead(target_date=target_date,
                        creation_date=date.today(),
                        version=version + 1,
                        derivative_count=len(derivatives))

    # Add report to database session
    db.session.add(report)
    db.session.flush()

    # Make CSV and open for writing
    with open(f'res/reports/{report.id}.csv', 'w') as file:
        # Derivative fields to include in report
        fieldnames = ['code', 'date_of_trade', 'asset', 'quantity',
                      'buying_party', 'selling_party', 'notional_value',
                      'notional_curr_code', 'maturity_date', 'underlying_price',
                      'underlying_curr_code', 'strike_price']

        # Create CSV writer
        writer = csv.DictWriter(file, fieldnames, extrasaction='ignore')

        # Write fieldname header to the report
        writer.writeheader()

        # Append the values of each derivative to the report
        for d in derivatives:
            data = {a: getattr(d, a) for a in vars(d.__class__) if a in fieldnames}
            writer.writerow(data)

    # Mark all derivatives on the target date as reported
    Derivative.query.filter_by(date_of_trade=target_date).update(dict(reported=True))

    # Commit the session to the database
    db.session.commit()

    # Return the id of the report
    return report.id
