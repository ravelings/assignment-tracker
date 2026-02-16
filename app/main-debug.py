from datetime import timedelta
from flask import Flask, jsonify
from pathlib import Path
from extensions.extensions import db, loginManager
from Website.Login.login import login_bp
from Website.MainPage.mainPage import mainPage_bp
from Website.Assignments.assignmentManager import assignments_bp
from Website.Courses.courseManager import courses_bp
from Website.Scores.scoreManager import scores_bp
from Website.Settings.settings import settings_bp
from Website.Calendar.calendar import calendar_bp
from Website.API_Endpoints.api_endpoints import api_bp

from flask_jwt_extended import JWTManager
# app config
app = Flask(__name__)
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(weeks=1)
# JWT config
app.config["JWT_SECRET_KEY"] = "8v`£^gRP;3]d6Ook2yf8v`£^gRP;3]d6Ook2yf8v`£^gRP;3]d6Ook2yf" 
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
jwt = JWTManager(app)
@jwt.expired_token_loader
def handle_expired(jwt_header, jwt_payload):
    print("Token expired")
    return (
        jsonify({
            "error": "access_token expired",
            "expired_at": jwt_payload["exp"],
        }),
        401,
    )
# DB config
# SQLite file paths on Windows need three slashes after sqlite:
app_dir = Path(__file__).resolve().parent
db_path = app_dir / "Database" / "database_local.db" # change to LOCAL database
print(f"Dir: {db_path}")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
#app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
#app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

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
## calendar
app.register_blueprint(calendar_bp, url_prefix="")
## scores
app.register_blueprint(scores_bp, url_prefix="/dashboard/")
## settings
app.register_blueprint(settings_bp, url_prefix="")
## API
app.register_blueprint(api_bp, url_prefix="/api/v1")
# secret
app.secret_key = "1234"

if __name__ == "__main__":
    app.run(debug=True)
