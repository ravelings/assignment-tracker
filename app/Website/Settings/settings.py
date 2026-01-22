from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from repositories.settingsRepo import SettingsRepo
from repositories.userRepo import UserRepo
from forms.setScoreMode import SetScoreMode
from forms.addTokenForm import AddTokenForm

settings_bp = Blueprint("settings", __name__, template_folder="templates")

@settings_bp.route("/dashboard/settings", methods=["GET", "POST"])
@login_required
def settings():
    user_id = current_user.user_id
    repo = SettingsRepo()
    user_settings = repo.getUserSettings(user_id)
    
    tokenForm = AddTokenForm()
    setScoreModeForm = SetScoreMode(function=int(user_settings.scoring_strategy))

    if not user_settings:
        user_settings = repo.initSettings(user_id).getUserSettings(user_id)

    return render_template("settings.html", 
                           settings=user_settings, 
                           scoreForm=setScoreModeForm,
                           tokenForm=tokenForm)

@settings_bp.route("/dashboard/settings/function", methods=["POST"])
@login_required
def setFunction():
    print("Endpoint get")
    form = SetScoreMode()
    if form.validate_on_submit():
        print("Form validated")
        function = form.function.data
        repo = SettingsRepo()
        set = repo.setFunction(current_user.user_id, function)
        if set == False:
            print("Unkown error")
            flash("Unkown Error", "error")
            return redirect(url_for("settings.settings"))
        print("Set success")
        flash("Function set successfully", "success")
        return redirect(url_for("settings.settings"))
    
    print(form.errors)
    return redirect(url_for("settings.settings"))

@settings_bp.route("/dashboard/settings/setToken", methods=["POST"])
@login_required
def setToken():
    form = AddTokenForm()
    if form.validate_on_submit:
        repo = UserRepo()
        token = form.token.data
        set = repo.setCanvasToken(user_id=current_user.user_id, token=token)

        if set:
            flash("Token set successfully!", category="token")
            return redirect(url_for("settings.settings"))
        else:
            flash("Token set failed.", category="token")
            return redirect(url_for("settings.settings"))
        
    print(form.errors)
    return redirect(url_for("settings.settings"))