from app import db

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)