from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create flask web-app
app = Flask(__name__)

# Initialise database engine
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://derivatex_backend:qwerty123@localhost/derivatex'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_BINDS'] = {
#     'external':'mysql+mysqlconnector://derivatex_backend:qwerty123@localhost/external'
# }
db = SQLAlchemy(app)



# Reigster all end-point blueprints
from cs261.blueprints.DerivativeManagement import DerivativeManagementBlueprint # noqa # pylint: disable=wrong-import-position
from cs261.blueprints.UserManagement import UserManagementBlueprint # noqa # pylint: disable=wrong-import-position
from cs261.blueprints.ActionManagement import ActionManagementBlueprint # noqa # pylint: disable=wrong-import-position

app.register_blueprint(DerivativeManagementBlueprint)
app.register_blueprint(UserManagementBlueprint)
app.register_blueprint(ActionManagementBlueprint)

# Create new tables for all ORM classes inheriting the base Model
import cs261.ExternalModels # noqa # pylint: disable=unused-import, wrong-import-position
db.create_all()
