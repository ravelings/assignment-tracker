from flask_login import UserMixin
from extensions.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column("user_id", db.Integer, primary_key = True)
    username = db.Column("username", db.String(50), nullable=False, unique=True)
    hash = db.Column("hash", db.String(255))

    def __init__(self, username, hash):
        self.username   = username
        self.hash       = hash

    def get_id(self):
        return str(self.user_id)
