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
        with open(f'res/reports/{report_id}.csv') as file:
            reader = csv.reader(file, delimiter=",")
            # Create and return list storing derivative data in the report
            data = []
            for row in reader:
                data.append({"id": row[0], "date_of_trade": row[1], "code": row[2], "asset": row[3],
                        "quantity": row[4], "buying_party": row[5], "selling_party": row[6],
                        "notional_value": row[7], "notional_curr_code": row[8], "maturity_date": row[9],
                        "underlying_price": row[10], "underlying_curr_code": row[11], "strike_price": row[12]})
            return data
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
                new_row = [row.id, row.date_of_trade, row.code]  # TBC
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
        date = data[0].date_of_trade

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
            html_out += data[row].id
            html_out += ("</td><td>" + data.date_of_trade)
            html_out += ("</td><td>" + data.code)
            html_out += ("</td><td>" + data.asset)
            html_out += ("</td><td>" + data.quantity)
            html_out += ("</td><td>" + data.buying_party)
            html_out += ("</td><td>" + data.selling_party)
            html_out += ("</td><td>" + data.notional_value)
            html_out += ("</td><td>" + data.notional_curr_code)
            html_out += ("</td><td>" + data.maturity_date)
            html_out += ("</td><td>" + data.underlying_price)
            html_out += ("</td><td>" + data.underlying_curr_code)
            html_out += ("</td><td>" + data.strike_price)
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
                        version=version + 1,
                        derivative_count = 0)

        # Add report to database session
        db.session.add(report)
        db.session.flush()

        # Make CSV and open for writing
        with open(f'res/reports/{report.id}.csv', 'w') as file:
            writer = csv.writer(file)
            # Get all derivatives traded on the target_date
            derivatives = Derivative.query.filter_by(date_of_trade=target_date).all()

            # Write report header
            # writer.writerow('') TODO

            # Track how many derivatives are added to the report
            count = 0

            for d in derivatives:
                # Append the derivative to the report if it has not been deleted
                if not d.deleted:
                    row = [d.id, d.date_of_trade, d.code, d.asset, d.quantity, d.buying_party,
                            d.selling_party, d.notional_value, d.notional_curr_code, d.maturity_date,
                            d.underlying_price, d.underlying_curr_code, d.strike_price]

                    # Write the derivative to the file
                    writer.writerow(row)
                    count += 1

                # Mark the derivative as reported
                d.reported = True
                db.session.add(d)

        # Set derivative count and commit session
        report.derivative_count = count
        db.session.add(report)
        db.session.commit()
