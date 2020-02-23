# Standard library imports
from datetime import date
import csv

# Third party imports
from sqlalchemy import asc
from fpdf import FPDF, HTMLMixin

# Local application imports
from backend.derivatex_models import Report, Derivative
from backend.db import db
from backend.util import clamp


def indexReports(date_from, date_to, page_size, page_number):
    """ Enumerates a page of reports from a date range filtered subset of
    all reports in the database.

    Args:
        date_from (date): The earliest date a returned report can be for.
        date_to (date): The latest date a returned report can be for.
        page_size (int): The number of reports that form a page.
        page_number (int): The page number offset of the index list.

    Returns:
        (tuple): tuple containing:
            reports (list): The list of reports that make up the page
            page_count (int): The number of pages all the reports are spread across
    """
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
    """ Retrieve the report from the database that has the given ID.

    Args:
        report_id (int): The ID of the desired report.

    Returns:
        Report: The report in the database with the corrosponding ID.
    """
    # Locate and read CSV or return nothing if it does not exist
    try:
        with open(f'res/reports/{report.id}.csv') as file:
            reader = csv.reader(file, delimiter=",")
            # Create and return list storing derivative data in the report
            return [row for row in reader]
    except:
        return



def createCSV(report_id):
    """ Create a temporary CSV file containing the data required by the trade repository.

    Args:
        report_id (int): The ID of the report which a CSV is required for.

    Returns:
        String: A string corresponding to the path to the generated CSV.
    """
    try:
        data = getReport(report_id)

        with open(f'res/temp/{report_id}.csv', 'w') as file:
            writer = csv.writer(file)
            for row in data:
                # Get desired data from rows of stored CSV report
                new_row = [row[0], row[1], row[2]]  # TBC
                writer.writerow(new_row)

        # Make CSV file and return path
        return f'res/temp/{report_id}.csv'
    except:
        return


def createPDF(report_id):
    """ Create a temporary PDF file containing the data required by the trade repository.

    Args:
        report_id (int): The ID of the report which a PDF is required for.

    Returns:
        String: A string corresponding to the path to the generated PDF.
    """
    try:
        # Get report derivative rows as list of lists
        data = getReport(report_id)
        date = data[0][1]

        # Creates design for table to be added to PDF
        header = """
        <table align="center" width="100%">
        <thead><tr>
        <th width="5%">id</th><th width="8%">Date Of Trade</th><th width="18%">Trade Code</th>
        <th width="12%">Asset</th><th width="5%">Quantity</th><th width="6%">Buying Party</th>
        <th width="6%">Selling Party</th><th width="8%">Notional Value</th><th width="4%">Notional Currency</th>
        <th width="8%">Maturity Date</th><th width="6%">Underlying Price</th><th width="4%">Underlying Currency</th>
        <th width="10%">Strike Price</th>
        </tr></thead>
        """

        # Adds every row of data to html which will be used to create table
        html_out = ""
        grey = False
        for row in range(0,len(data)):
            html_out += "<tr bgcolor=\"#E1E1E1\"><td>" if grey else "<tr bgcolor=\"#FFFFFF\"><td>"
            grey = not grey
            html_out += data[row][0]
            for i in range(1,len(data[row])):
                html_out += ("</td><td>" + data[row][i])
            html_out += "</td></tr>\n"

        # Create final html that represents table
        html = header + html_out + "</tbody></table>"

        # Create PDF
        pdfFile=MyFPDF('P','mm','letter')
        pdfFile.set_top_margin(margin=18)  #18
        pdfFile.set_auto_page_break(True, 27) #27
        pdfFile.add_page()
        pdfFile.alias_nb_pages()
        pdfFile.set_font("Arial", style="B", size=14)
        pdfFile.cell(200, 5, txt=f'Derivative Report {date}', ln=1, align="C")
        pdfFile.write_html(html)
        pdfFile.output(f'res/temp/{report_id}.pdf')

        # Return path to PDF
        return f'res/temp/{report_id}.pdf'
    except Exception as e:
        return


def generateReports():
    """ Generates and stores new report CSVs for dates containing unreported derivatives.

    Args:
        None

    Returns:
        None
    """
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
        # Execute query
        reports = query.all()

        # Obtain latest version number or default to 0
        version = max([report.version for report in reports], default=0)

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
                row = [d.id, d.date_of_trade, d.code, d.asset, d.quantity, d.buying_party,
                        d.selling_party, d.notional_value, d.notional_curr_code, d.maturity_date,
                        d.underlying_price, d.underlying_curr_code, d.strike_price]

                # Write the derivative to the file
                writer.writerow(row)

                # Mark the derivative as reported
                d.reported = True
                db.session.add(d)

        # Commit session to database
        db.session.commit()
