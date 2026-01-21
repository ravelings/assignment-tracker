from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from repositories.settingsRepo import SettingsRepo
from forms.setScoreMode import SetScoreMode

settings_bp = Blueprint("settings", __name__, template_folder="templates")

@settings_bp.route("/dashboard/settings", methods=["GET", "POST"])
@login_required
def settings():
    user_id = current_user.user_id
    repo = SettingsRepo()
    user_settings = repo.getUserSettings(user_id)
    
    setScoreModeForm = SetScoreMode()

    if not user_settings:
        user_settings = repo.initSettings(user_id).getUserSettings(user_id)

    if request.method == "POST":
        strategy = request.form.get("scoring_strategy")
        if strategy in ["logistic", "exponential"]:
            user_settings.scoring_strategy = strategy
            db.session.commit()
            flash("Settings updated successfully!", "success")
        else:
            flash("Invalid scoring strategy selected.", "error")
        
        return redirect(url_for("settings.settings"))

    return render_template("settings.jinja2", settings=user_settings, scoreForm=setScoreModeForm)
