import json
# You can use 'from flask import abort' and then 'abort(http_code)' to abort requests


def exampleFunction(exampleParam):
    return json.dumps(int(exampleParam) + 1)
