#import sqlite3
#from Packages.user import User
from models.user import User
from extensions.extensions import db
from services.auth_service import get_hash_password
import json

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
        check = self.getUserByName(username)
        if check is None:
            hashed_pw = get_hash_password(password)
            user = User(username, hashed_pw)
            db.session.add(user)
            self.commit()
            return user
        else:
            return None

    def getGoogleUser(self, iss, sub):
        return (User.query.filter_by(iss=iss, sub=sub).one_or_none())

    def createGoogleUser(self, iss, sub, username):
        user = User(username=username, iss=iss, sub=sub)
        db.session.add(user)
        self.commit() 
        return user

    def setCredentials(self, user_id, token, refresh_token, scopes, expiry):
        user = User.query.filter_by(user_id=user_id).first()
        user.google_token = token 
        user.refresh_token = refresh_token
        user.granted_scopes = json.dumps(scopes) 
        user.expiry = expiry
        self.commit()

    def refreshCredentials(self, user_id, token, expiry):
        user = User.query.filter_by(user_id=user_id).first()
        user.google_token = token
        user.expiry = expiry 
        self.commit()

    def set_calendar_id(self, user_id, calendar_id):
        user = User.query.filter_by(user_id=user_id).first()
        user.calendar_id = calendar_id 
        self.commit()
    
    def get_calendar_id(self, user_id):
        return (User.query.filter_by(user_id=user_id).first()).calendar_id
        
    def setCanvasToken(self, user_id, token):
        user = User.query.filter_by(user_id=user_id).first()

        if user is None:
            return False 
        
        user.canvas_token = token 
        self.commit()

        return True
    
    def getCanvasToken(self, user_id):
        
        token = (User.query.filter_by(user_id=user_id).first()).canvas_token
        
        return token
    
    def getComplete(self, user_id):
        return User.query.filter_by(user_id=user_id).first().total_completed
    
    def incrementComplete(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        user.total_completed += 1
        self.commit()

    def decrementComplete(self, user_id):
        user = User.query.filter_by(user_id=user_id).first()
        user.total_completed -= 1
        self.commit()