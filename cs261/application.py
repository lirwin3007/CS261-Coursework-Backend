from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create flask web-app
app = Flask(__name__)

# Initialise database engine
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://test_user:derivatex2020@localhost/derivatex'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Reigster all end-point blueprints
from cs261.blueprints.DerivativeManagement import DerivativeManagementBlueprint
app.register_blueprint(DerivativeManagementBlueprint)
# ...




# Create new tables for all ORM classes inheriting the base Model
db.create_all()
