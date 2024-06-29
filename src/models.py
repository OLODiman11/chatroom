from . import db

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String, nullable=False)
    text = db.Column(db.String)
    