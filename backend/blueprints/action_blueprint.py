# Third party imports
from flask import Blueprint, abort, jsonify

# Local application imports
from backend.managers import action_management
from backend.managers import user_management

# Instantiate new blueprint
ActionBlueprint = Blueprint('actionManagement',
                            __name__,
                            url_prefix='/action-management')


# Routes
@ActionBlueprint.route('/get-action/<action_id>')
def getAction(action_id):
    # Get action from database
    action = action_management.getAction(action_id)

    # Verify action exists
    if action is None:
        return abort(404, f'action id {action_id} does not exist')

    # Make response
    return jsonify(action=action)


@ActionBlueprint.route('/get-user-actions/<user_id>')
def getUserActions(user_id):
    # Validate user id
    if user_management.getUser(user_id) is None:
        return abort(404, f'user id {user_id} does not exist')

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
