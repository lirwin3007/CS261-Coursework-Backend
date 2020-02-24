# Third party imports
from flask import Blueprint, abort, jsonify

# Local application imports
from backend.managers import user_management

# Instantiate new blueprint
UserBlueprint = Blueprint('userAccountControl',
                          __name__,
                          url_prefix='/user-account-control')


# Routes
@UserBlueprint.route('/get-user/<user_id>')
def getUser(user_id):
    # Get user from database
    user = user_management.getUser(user_id)

    # Verify user exists
    if user is None:
        return abort(404, f'user with id {user_id} does not exist')

    # Make response
    return jsonify(user=user)


@UserBlueprint.route('/index-users')
def indexUsers():
    # Get all users from database
    users = user_management.getAllUsers()
    # Make response
    return jsonify(users=[u.id for u in users])


# TODO: implement
@UserBlueprint.route('/authenticate-user', methods=['POST'])
def authenticateUser(user_id, password):
    # Attempt to find user in database
    user = user_management.getUser(user_id)
    # Check if correct credentials are supplied
    if user.password == password:
        return abort(200, "OK")  # placeholder code
    return abort(401, "Incorrect username or password")
