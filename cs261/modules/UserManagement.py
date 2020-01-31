from cs261.application import db

class User(db.Model):
    id = db.Column(db.String(16), primary_key=True)
    name = db.Column(db.String(32), nullable=False)
