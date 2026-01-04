#import sqlite3
#from Packages.user import User
from models.user import User
from extensions.extensions import db
from services.auth_service import get_hash_password

class UserRepo:
    def __init__(self):
        pass
    
    def commit(self):
        db.session.commit()

    def getUserByName(self, username):

        user = User.query.filter_by(username=username).first()

        if user is not None:
            return user
        
        else:
            return None
        
    def getUserById(self, user_id):

        user = User.query.filter_by(user_id=user_id).first()

        if user is not None:
            return user
        
        else:
            return None
        
    def createUser(self, username, password):
        check = self.getUser(username)
        if check is None:
            hashed_pw = get_hash_password(password)
            user = User(username, hashed_pw)
            db.session.add(user)
            self.commit()
            return user
        else:
            return None
