# Third party imports
from flask import Blueprint, abort, jsonify

# Local application imports
from backend.managers import action_management

# Instantiate new blueprint
ActionBlueprint = Blueprint('actionManagement',
                            __name__,
                            url_prefix='/action-management')


# Routes
@ActionBlueprint.route('/get-action/<action_id>')
def getAction(action_id):
    # Get action from database
    action = action_management.getAction(action_id)
    if action is None:
        abort(404)

    # Make response
    return jsonify(action=action)


@ActionBlueprint.route('/get-user-actions/<user_id>')
def getUserActions(user_id):
    # Get user actions from database
    actions = action_management.getUserActions(user_id)
    # Make response
    return jsonify(actions=[a.id for a in actions])


@ActionBlueprint.route('/get-recent-actions/<count>')
def getRecentActions(count):
    # Get recent actions from database
    actions = action_management.getRecentActions(count)
    # Make response
    return jsonify(actions=[a.id for a in actions])
