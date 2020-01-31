# Third party imports
from flask import Blueprint, request, jsonify, abort

# Local application imports
from cs261.modules import ActionManagement

# Instantiate new blueprint
ActionManagementBlueprint = Blueprint('actionManagement',
                                          __name__,
                                          url_prefix='/action-management')

# Routes
@ActionManagementBlueprint.route('/get-action/<actionId>')
def getAction(actionId):
    # Retreive action with the Id
    action = ActionManagement.getAction(actionId)

    # The given action does not exist, return a 404
    if action is None:
        return abort(404)

    # Return action attributes as dictionary
    return action.as_dict()
