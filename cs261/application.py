from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create flask web-app
app = Flask(__name__)

# Initialise database engine
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://derivatex_backend:qwerty123@localhost/derivatex'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Reigster all end-point blueprints
from cs261.blueprints.DerivativeManagement import DerivativeManagementBlueprint # pylint: disable=C0413
from cs261.blueprints.ActionManagement import ActionManagementBlueprint # pylint: disable=C0413

app.register_blueprint(DerivativeManagementBlueprint)
app.register_blueprint(ActionManagementBlueprint)



# Create new tables for all ORM classes inheriting the base Model
import cs261.modules.ExternalModels
db.create_all()
