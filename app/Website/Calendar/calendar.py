from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from datetime import timezone, datetime
from flask_login import login_required, current_user
from repositories.settingsRepo import SettingsRepo
from repositories.userRepo import UserRepo
from forms.setScoreMode import SetScoreMode
from forms.addTokenForm import AddTokenForm
from google_auth_oauthlib.flow import Flow
from pathlib import Path
from oauthlib.oauth2 import OAuth2Error
from services.googleCalendar import GoogleCalendar



calendar_bp = Blueprint("calendar", __name__, template_folder="templates")

@calendar_bp.route("/dashboard/calendar/", methods=["GET", "POST"])
@login_required
def calendar():
    return render_template("calendar.html")