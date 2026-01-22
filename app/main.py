from flask import Flask
from pathlib import Path
from extensions.extensions import db, loginManager
from Website.Login.login import login_bp
from Website.MainPage.mainPage import mainPage_bp
from Website.Assignments.assignmentManager import assignments_bp
from Website.Courses.courseManager import courses_bp
from Website.Scores.scoreManager import scores_bp
from Website.Settings.settings import settings_bp

app = Flask(__name__)
# DB config
basedir = Path(__file__).resolve().parent
db_path = basedir / "Database" / "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
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
app.register_blueprint(assignments_bp, url_prefix="/dashboard/assignment")
## course
app.register_blueprint(courses_bp, url_prefix="/dashboard/course")
## scores
app.register_blueprint(scores_bp, url_prefix="/dashboard/")
## settings
app.register_blueprint(settings_bp, url_prefix="")
# secret
app.secret_key = "12345"

if __name__ == "__main__":
    app.run(debug=True)
