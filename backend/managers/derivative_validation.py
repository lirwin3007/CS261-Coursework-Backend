from flask import abort, jsonify, request
from sqlalchemy.exc import IntegrityError

from backend.managers import user_management

def isValidDerivative(request):
    # Verify request
    try:
        body = getJSON(request)
        user_id = body.get('user_id')

        # Validate user id
        if user_management.getUser(user_id) is None:
            return abort(404, f'user id {user_id} does not exist')
        # print(derivative, 'derivative')
        return True
    except Exception:
        return abort(400, 'JSON properties invalid')

def getJSON(request):
    try:
        return request.get_json()
    except Exception:
        return abort(400, 'JSON required')
