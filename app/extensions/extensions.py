from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher
from flask_login import LoginManager

db = SQLAlchemy() # database 
ph = PasswordHasher() # password hasher
loginManager = LoginManager() # login manager
client_id = "191762128708-5mo6v6td9hseta7244b9gjbubonssqhu.apps.googleusercontent.com"