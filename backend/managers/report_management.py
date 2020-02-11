# Standard library imports
from flask import send_file

# Local application imports
from backend.derivatex_models import Derivative, Report
from backend.db import db

def indexReports(date_from,date_to):
    return {"report_ids": [1,2,3]}


def getReport(report_id):
    return {"report_id": 1, "report": {"derivatives": [1,2,3]}}


def downloadCSV(report_id):
    try:
        send_file("static/reports/" + report_id + ".csv")
        return True
    except Exception as e:
        return False


def downloadPDF(report_id):
    try:
        send_file("static/reports/" + report_id + ".pdf")
        return True
    except Exception as e:
        return False


def generateReports():
    # Select dates from Derivative table not reported
    # Create new entry in report table with stats
    # Create new CSV file in static with id
    # Populate CSV with derivatives
    return True
