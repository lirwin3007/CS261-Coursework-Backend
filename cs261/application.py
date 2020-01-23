from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from cs261.blueprints.DerivativeManagement import DerivativeManagementBlueprint
import json

# Create flask web-app
app = Flask(__name__)

# Initialise database engine
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://test_user:derivatex2020@localhost/derivatex'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Reigster all end-point blueprints
app.register_blueprint(DerivativeManagementBlueprint)
# ...
# ...
# ...

# Move to DerivativeManagement
class Trade(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    buying_party = db.Column(db.String(6))
    selling_party = db.Column(db.String(6))
    quantity = db.Column(db.Integer)
    strike_price = db.Column(db.Float)
    # modified = db.Column(db.Boolean)

    # def __init__(self, json_data):
    #     self.__dict__ = json.loads(json_data)

    def __str__(self):
        return '<Trade : {}>'.format(self.id)

    def __repr__(self):
        return json.dumps(self.__dict__)

# Move to DerivativeManagement
# class ArchivedTrade(Trade):
#     hash = db.Column(db.String(128), nullable=False)

db.create_all()

# # Test
if not Trade.query.filter_by(id='test').first():
    db.session.add(Trade(id = "test"))
    # db.session.add(Trade('{"id":"test", "buying_party":"me", "selling_party":"them", "quantity":42, "strike_price":3.75}'))
    db.session.commit()
