import json
from flask import abort

class DerivativeManagement:
    def __init__(self):
        pass

    def exampleFunction(self, exampleParam):
        return json.dumps(int(exampleParam) + 1)
