# Third party imports
from flask import Blueprint

# Local application imports
# You can import database models with 'from cs261.DerivatexModels import Derivative, User, Action'
from cs261.modules.UserManagement import UserManagement

# Instantiate new blueprint
UserManagementBlueprint = Blueprint('userManagement',
                                    __name__,
                                    url_prefix='/user-management')

# Instantiate module
UserManagementModule = UserManagement()

# Routes
@UserManagementBlueprint.route('/example-route/<exampleParam>')
def exampleRoute(exampleParam):
    return UserManagementModule.exampleFunction(exampleParam)
