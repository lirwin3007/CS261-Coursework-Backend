# Third party imports
from flask import Blueprint

# Local application imports
from cs261.DerivatexModels import *

# Instantiate new blueprint
UserManagementBlueprint = Blueprint('userManagement',
                                          __name__,
                                          url_prefix='/user-management')

# Routes
