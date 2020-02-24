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
    """ Check if the a valid user id and the correct password for that user id is entered
    Args:
        user_id (int): The ID of the user which needs to be returned
    Returns:
        JSON: A JSON object representing user
    """
    # Get user from database
    user = user_management.getUser(user_id)

    # Verify user exists
    if user is None:
        return abort(404, f'user with id {user_id} does not exist')

    # Make response
    return jsonify(user=user)


@UserBlueprint.route('/index-users')
def indexUsers():
    """ Check if the a valid user id and the correct password for that user id is entered
    Args:
        None
    Returns:
        JSON: A JSON object representing all the user
    """
    # Get all users from database
    users = user_management.getAllUsers()
    # Make response
    return jsonify(users=[u.id for u in users])


# TODO: implement
@UserBlueprint.route('/authenticate-user', methods=['POST'])
def authenticateUser():
    """ Check if the a valid user id and the correct password for that user id is entered
    Args:
        None
    Returns:
        None
    """
    # Verify request
    if not request.data or not request.is_json:
        return abort(400)

    # Retrieve json body from request
    body = request.get_json()
    user_id = body.get('user_id')
    password = body.get('password')

    # Get user from database
    user = user_management.getUser(user_id)

    # Validate user id
    if user is None:
        return abort(404, f'user id {user_id} does not exist')
    else:
        # Check if correct credentials are supplied
        if user.password == password:
            return abort(200, "OK")
        return abort(401, "Incorrect username or password")
        