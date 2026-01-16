from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions.extensions import db
from models.settings import Settings

settings_bp = Blueprint("settings", __name__, template_folder="templates")

@settings_bp.route("/dashboard/settings", methods=["GET", "POST"])
@login_required
def settings():
    user_settings = Settings.query.filter_by(user_id=current_user.user_id).first()
    
    if not user_settings:
        user_settings = Settings(user_id=current_user.user_id)
        db.session.add(user_settings)
        db.session.commit()

    if request.method == "POST":
        strategy = request.form.get("scoring_strategy")
        if strategy in ["logistic", "exponential"]:
            user_settings.scoring_strategy = strategy
            db.session.commit()
            flash("Settings updated successfully!", "success")
        else:
            flash("Invalid scoring strategy selected.", "error")
        
        return redirect(url_for("settings.settings"))

    return render_template("settings.jinja2", settings=user_settings)
