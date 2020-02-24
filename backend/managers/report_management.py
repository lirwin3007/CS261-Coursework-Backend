# Standard library imports
from datetime import date
import csv
import os

# Third party imports
from sqlalchemy import asc

# Local application imports
from backend.derivatex_models import ReportHead, Derivative
from backend.db import db
from backend.util import clamp
import backend.util.MyFPDF


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
    query = ReportHead.query

    # Filter and order query
    query.filter(date_from < ReportHead.target_date)
    query.filter(ReportHead.target_date < date_to)
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
    """ Retrieve the report from the database that has the given ID.

    Args:
        report_id (int): The ID of the desired report.

    Returns:
        Report: The report in the database with the corrosponding ID.
    """
    # Locate and read CSV or return nothing if it does not exist
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


def createCSV(report_id):
    """ Create a temporary CSV file containing the data required by the trade repository.

    Args:
        report_id (int): The ID of the report which a CSV is required for.

    Returns:
        String: A string corresponding to the path to the generated CSV.
    """
    # Get report data
    data = getReportData(report_id)

    # Open report file and CSV writer
    with open(f'res/temp/{report_id}.csv', 'w') as file:
        writer = csv.writer(file)

        for derivative in data:
            # Get desired data from rows of stored CSV report
            row = [derivative["id"], derivative["date_of_trade"], derivative["code"]]  # TBC
            writer.writerow(row)

    # Return path to csv outfile
    return os.path.realpath(file.name)


def createPDF(report_id):
    """ Create a temporary PDF file containing the data required by the trade repository.

    Args:
        report_id (int): The ID of the report which a PDF is required for.

    Returns:
        String: A string corresponding to the path to the generated PDF.
    """
    try:
        # Get report derivative rows as list of lists
        data = getReportData(report_id)
        date = data[0]["date_of_trade"]

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
        for row in range(0, len(data)):
            html_out += "<tr bgcolor=\"#E1E1E1\"><td>" if grey else "<tr bgcolor=\"#FFFFFF\"><td>"
            grey = not grey
            html_out += data[row].id
            html_out += ("</td><td>" + data["date_of_trade"])
            html_out += ("</td><td>" + data["code"])
            html_out += ("</td><td>" + data["asset"])
            html_out += ("</td><td>" + data["quantity"])
            html_out += ("</td><td>" + data["buying_party"])
            html_out += ("</td><td>" + data["selling_party"])
            html_out += ("</td><td>" + data["notional_value"])
            html_out += ("</td><td>" + data["notional_curr_code"])
            html_out += ("</td><td>" + data["maturity_date"])
            html_out += ("</td><td>" + data["underlying_price"])
            html_out += ("</td><td>" + data["underlying_curr_code"])
            html_out += ("</td><td>" + data["strike_price"])
            html_out += "</td></tr>\n"

        # Create final html that represents table
        html = header + html_out + "</tbody></table>"

        # Create PDF
        pdf = MyFPDF('P','mm','letter')
        pdf.set_top_margin(margin=18)  # 18
        pdf.set_auto_page_break(True, 27)  # 27
        pdf.add_page()
        pdf.alias_nb_pages()
        pdf.set_font("Arial", style="B", size=14)
        pdf.cell(200, 5, txt=f'Derivative Report {date}', ln=1, align="C")
        pdf.write_html(html)

        file_path = f'res/temp/{report_id}.pdf'

        pdf.output(file_path)

        # Return path to PDF
        return os.path.realpath(file_path)
    except Exception as e:
        print(e, '--------------------------------------------------------')
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
        # Get all the existing reports for the given target_date
        reports = ReportHead.query.filter_by(target_date=target_date).all()

        # Obtain latest report version number or default to 0
        version = max([report.version for report in reports], default=0)

        # Get all none-deleted erivatives traded on the target_date
        derivatives = Derivative.query.filter_by(date_of_trade=target_date,
                                                 deleted=False).all()
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
            writer = csv.writer(file)

            # Append each of the derivative to the report
            for d in derivatives:
                row = [d.id, d.date_of_trade, d.code, d.asset, d.quantity,
                       d.buying_party, d.selling_party, d.notional_value,
                       d.notional_curr_code, d.maturity_date, d.underlying_price,
                       d.underlying_curr_code, d.strike_price]

                writer.writerow(row)

        # Mark all derivatives on the target date as reported
        Derivative.query.filter_by(date_of_trade=target_date).update(dict(reported=True))

        # Commit the session to the database
        db.session.commit()
