from backend.managers import user_management

def validateDerivative(derivative):
    return True

# def validateDerivativeId(derivative_id):
#     if derivative_id is not

# def isValidDerivativeId(derivative_id):
#     if derivative_id is

def isValidDerivative(request):
    # Verify request
    if not request.data or not request.is_json:
        return abort(400, 'empty request body')

    # Retreive json body from request
    body = request.get_json()
    user_id = body.get('user_id')

    # Validate user id
    if user_management.getUser(user_id) is None:
        return abort(404, f'user id {user_id} does not exist')
    # print(derivative, 'derivative')

    return True
