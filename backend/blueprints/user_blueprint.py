# Third party imports
from flask import Blueprint, abort, jsonify

# Local application imports
from backend.managers import user_management

# Instantiate new blueprint
UserBlueprint = Blueprint('userManagement',
                          __name__,
                          url_prefix='/user-management')


# Routes
@UserBlueprint.route('/get-user/<user_id>')
def getUser(user_id):
    # Get user from database
    user = user_management.getUser(user_id)
    # Make response
    return user.as_dict() if user is not None else abort(404)


@UserBlueprint.route('/index-users')
def indexUsers():
    # Get all users from database
    users = user_management.getAllUsers()
    # Make response
    return jsonify(users=[u.id for u in users])


# TODO: implement
@UserBlueprint.route('/authenticate-user')
def authenticateUser():
    # No content, return a 204
    return '', 204
