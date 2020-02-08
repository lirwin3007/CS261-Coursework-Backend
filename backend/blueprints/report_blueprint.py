# Third party imports
from flask import Blueprint

# Local application imports
# from backend.managers import report_management

# Instantiate new blueprint
ReportBlueprint = Blueprint('reportManagement',
                            __name__,
                            url_prefix='/report-management')


# Routes
@ReportBlueprint.route('/example-route')
def exampleRoute():
    # No content, return a 204
    return '', 204
