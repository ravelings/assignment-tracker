from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from datetime import timezone
from flask_login import login_required, current_user, logout_user
from repositories.settingsRepo import SettingsRepo
from repositories.userRepo import UserRepo
from forms.setScoreMode import SetScoreMode
from forms.addTokenForm import AddTokenForm
from forms.addInstanceForm import AddInstanceForm
from forms.deleteForm import DeleteForm
from forms.SubmitForm import SubmitForm
from google_auth_oauthlib.flow import Flow
from pathlib import Path
from oauthlib.oauth2 import OAuth2Error
from repositories.assignmentRepo import AssignmentRepo
from repositories.courseRepo import CourseRepo
from services.googleCalendar import GoogleCalendar



settings_bp = Blueprint("settings", __name__, template_folder="templates")

@settings_bp.route("/dashboard/settings/", methods=["GET", "POST"])
@login_required
def settings():
    print(f"URL: {request.scheme}://{request.host}")
    userRepo = UserRepo()
    user = userRepo.getUserById(user_id=current_user.user_id)
    user_id = current_user.user_id
    settingsRepo = SettingsRepo()
    user_settings = settingsRepo.getUserSettings(user_id)
    if not user_settings:
        user_settings = settingsRepo.initSettings(user_id).getUserSettings(user_id)
        
    userRepo = UserRepo()
    
    tokenForm = AddTokenForm()
    instanceForm = AddInstanceForm()
    setScoreModeForm = SetScoreMode(function=int(user_settings.function))
    submitForm = SubmitForm()
    deleteForm = DeleteForm()

    return render_template("settings.html",
                        user = user, 
                        settings=user_settings, 
                        scoreForm=setScoreModeForm,
                        tokenForm=tokenForm,
                        instanceForm=instanceForm,
                        submitForm = submitForm,
                        deleteForm = deleteForm)

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
            flash("Unkown Error", "fail")
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
    if form.validate_on_submit():
        repo = UserRepo()
        token = (form.token.data).strip()
        set = repo.setCanvasToken(user_id=current_user.user_id, token=token)

        if set:
            flash("Token set successfully!", category="success")
            return redirect(url_for("settings.settings"))
        else:
            flash("Token set failed.", category="fail")
            return redirect(url_for("settings.settings"))
        
    print(form.errors)
    return redirect(url_for("settings.settings"))

def _store_token(auth_code):
    app_dir = Path(__file__).resolve().parents[2]
    secret_path = app_dir / "Database" / "client_secret.json"
    flow = Flow.from_client_secrets_file(
        secret_path,
        scopes=["https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
                "openid", 
                "https://www.googleapis.com/auth/calendar.readonly", 
                "https://www.googleapis.com/auth/calendar"])
    origin = f"{request.scheme}://{request.host}"
    flow.redirect_uri = origin
    print(f"Redirect URI: {flow.redirect_uri}")
    print("Fetching token...")

    # Store the credentials in browser session storage, but for security: client_id, client_secret,
    # and token_uri are instead stored only on the backend server.

    try:
        flow.fetch_token(code=auth_code)

    except OAuth2Error as e:
        # OAuthlib-parsed error (most useful)
        print("OAuth2Error occurred")
        print("Error:", e)
        if hasattr(e, "description"):
            print("Description:", e.description)
        if hasattr(e, "uri"):
            print("URI:", e.uri)
        raise

    except Exception as e:
        # Anything else (network, misconfiguration, etc.)
        print("Unexpected exception during token exchange")
        print(type(e), e)
        raise
    
    credentials = flow.credentials

    expiry = credentials.expiry
    if expiry is not None:
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        else:
            expiry = expiry.astimezone(timezone.utc)
        expiry = expiry.isoformat()

    print(f"Expiry: {expiry}")
    print("Access token:", credentials.token)
    print("Refresh token:", credentials.refresh_token)
    print(f"Account: {credentials.account}")

    userRepo = UserRepo()
    user_id = current_user.user_id
    userRepo.setCredentials(user_id=user_id, 
                            token=credentials.token,
                            refresh_token=credentials.refresh_token,
                            scopes=credentials.granted_scopes,
                            expiry=expiry)
    return

@settings_bp.route("/dashboard/settings/setInstance", methods=["POST"])
@login_required
def setInstance():
    form = AddInstanceForm()
    if form.validate_on_submit():
        ## get instancce from https://
        url = form.instance.data
        start = url.find("https://")
        if start == -1:
            flash("Error: Invalid instance URL", "error")
            return redirect(url_for('settings.settings'))
        rest = url[start + len("https://"): ]
        instance = rest.split(".", 1)[0]
        ## sets canvas instance on user object
        repo = UserRepo()
        repo.setCanvasInstance(current_user.user_id, instance)
        flash("Instance set successfully!", "success")
    return redirect(url_for('settings.settings'))

#def _store_user_info()

@settings_bp.route("/dashboard/settings/auth/google", methods=["POST", "GET"])
@login_required
def authGoogle():
    if request.headers.get("X-Requested-With") != "XmlHttpRequest":
        print("Header mismatch")
        abort(403)
    if request.method == "POST":
        print("Method: POST")
        auth_code = request.form.get("code")
    else:
        print("Method: GET")
        auth_code = request.args.get("code")

    print(f"Auth Code: {auth_code}")
    if not auth_code:
        print("Missing auth code")
        abort(400, "Missing authorization code")

    _store_token(auth_code)

    return url_for("settings.settings")

@settings_bp.route("/dashboard/settings/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.login'))

@settings_bp.route("/dashboard/settings/delete/canvas", methods=["POST"])
@login_required
def deleteCanvasData():
    form = SubmitForm()
    if form.validate_on_submit():
        user_id = current_user.user_id
        userRepo = UserRepo()
        token = userRepo.getCanvasToken(user_id)
        if token is None:
            flash("Error! Canvas token not set!", "fail")
            return redirect(url_for("settings.settings"))
        
        userRepo.deleteCanvasToken(user_id)
        assignmentRepo = AssignmentRepo()
        assignmentRepo.deleteAllCanvasAssignments(user_id)
        courseRepo = CourseRepo()
        courseRepo.deleteAllCanvasCourses(user_id)
        flash("Delete successful!", "success")
    return redirect(url_for("settings.settings"))

@settings_bp.route("/dashboard/settings/delete/google", methods=["POST"])
@login_required
def deleteGoogleData():
    form = DeleteForm()
    if form.validate_on_submit():
        user_id = current_user.user_id
        userRepo = UserRepo()
        user = userRepo.getUserById(user_id)
        refresh_token = user.refresh_token
        if refresh_token is None:
            flash("Error! Google has not been authorized", "error")
            return redirect(url_for("settings.settings"))
        
        calendar_id = user.calendar_id
        if calendar_id is None or not calendar_id.strip():
            userRepo.deleteGoogleTokens(user_id)
            flash("Your Google information has been successfully removed!", "success")
            return redirect(url_for("settings.settings"))
        
        calendar = GoogleCalendar(user)
        calendar.delete_calendar()
        userRepo.deleteGoogleTokens(user_id)
        flash("Your Google information and Calendar has been successfully removed!", "success")
        return redirect(url_for("settings.settings"))