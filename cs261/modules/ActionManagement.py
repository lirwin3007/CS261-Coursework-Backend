import json
# You can use 'from flask import abort' and then 'abort(http_code)' to abort requests


class ActionManagement:
    def __init__(self):
        pass

    def exampleFunction(self, exampleParam):
        return json.dumps(int(exampleParam) + 1)
