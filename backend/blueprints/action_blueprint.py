# Third party imports
from flask import Blueprint, abort, jsonify

# Local application imports
from backend.managers import action_management

# Instantiate new blueprint
ActionBlueprint = Blueprint('actionManagement',
                            __name__,
                            url_prefix='/action-management')


# Routes
@ActionBlueprint.route('/get-action/<actionId>')
def getAction(actionId):
    # Get action from database
    action = action_management.getAction(actionId)
    # Make response
    return action.as_dict() if action is not None else abort(404)


@ActionBlueprint.route('/get-user-actions/<userId>')
def getUserActions(userId):
    # Get user actions from database
    actions = action_management.getUserActions(userId)
    # Make response
    return jsonify(actions=[a.id for a in actions])


@ActionBlueprint.route('/get-recent-actions/<count>')
def getRecentActions(count):
    # Get recent actions from database
    actions = action_management.getRecentActions(count)
    # Make response
    return jsonify(actions=[a.id for a in actions])
