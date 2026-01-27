from flask_login import UserMixin
from extensions.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column("user_id", db.Integer, primary_key = True)
    username = db.Column("username", db.String(50), nullable=False, unique=True)
    hash = db.Column("hash", db.String(255))

    canvas_token = db.Column("canvas_token", db.String(255), nullable=True)
    total_completed = db.Column("total_completed", db.Integer, nullable=False)
    
    google_token = db.Column("google_token", db.String(255), nullable=True)
    refresh_token = db.Column("refresh_token", db.String(255), nullable=True)
    granted_scopes = db.Column("granted_scopes", db.String(255), nullable=True)
    expiry = db.Column("expiry", db.String(255), nullable=True)
    calendar_id = db.Column("calendar_id", db.String(255), nullable=True)

    def __init__(self, username, hash):
        self.username   = username
        self.hash       = hash
        self.total_completed = 0

    def get_id(self):
        return str(self.user_id)
