from flask_sqlalchemy import SQLAlchemy
from app import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    fingerprint_template = db.Column(db.LargeBinary, nullable=False)
