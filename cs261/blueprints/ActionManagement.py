# Third party imports
from flask import Blueprint, abort

# Local application imports
from cs261.DerivatexModels import Action

# Instantiate new blueprint
ActionManagementBlueprint = Blueprint('actionManagement',
                                      __name__,
                                      url_prefix='/action-management')

# Routes
@ActionManagementBlueprint.route('/get-action/<actionId>')
def getAction(actionId):
    # Retreive action with the Id
    action = Action.query.get(actionId)

    # The given action does not exist, respond with a 404
    if action is None:
        return abort(404)

    # Return action attributes as dictionary
    return action.as_dict()
