from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher
from flask_login import LoginManager

db = SQLAlchemy() # database 
ph = PasswordHasher() # password hasher
loginManager = LoginManager() # login manager