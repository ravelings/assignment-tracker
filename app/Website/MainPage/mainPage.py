from flask import render_template, Blueprint
from flask_login import login_required, current_user

mainPage_bp = Blueprint("mainPage", __name__, static_folder="static", template_folder="templates")

@mainPage_bp.route("/dashboard/")
@login_required
def dashboard():
    return render_template("dashboard.html")

@mainPage_bp.route("/userinfo/")
@login_required
def userInfo():
    return render_template("userInfo.html", user=current_user)