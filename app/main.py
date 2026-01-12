from flask import Flask
from extensions.extensions import db, loginManager
from Website.Login.login import login_bp
from Website.MainPage.mainPage import mainPage_bp
from Website.Assignments.assignmentManager import assignments_bp
from Website.Courses.courseManager import courses_bp

app = Flask(__name__)
# DB config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///C:/Users/ravel/Documents/Coding/Assignment Tracker/assignment-tracker/app/Database/database.db"
db.init_app(app)
# Login Manager
loginManager.init_app(app)
loginManager.login_view = "login.login"
# Register BPs
## login
app.register_blueprint(login_bp, url_prefix="")
## main page 
app.register_blueprint(mainPage_bp, url_prefix="")
## assignment
app.register_blueprint(assignments_bp, url_prefix="")
## course
app.register_blueprint(courses_bp, url_prefix="")
# secret
app.secret_key = "12345"

if __name__ == "__main__":
    app.run(debug=True)
