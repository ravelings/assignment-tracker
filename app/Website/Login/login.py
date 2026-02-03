from pathlib import Path
import json
import os
from flask_login import current_user
from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from flask_login import login_user, logout_user
from repositories.userRepo import UserRepo
from services.auth_service import verify_password
from forms.LoginRegister import LoginForm, RegisterForm
from forms.UsernameForm import UsernameForm
from extensions.extensions import loginManager
from services.recaptcha_service import create_assessment
from flask import request

from google.oauth2 import id_token
from google.auth.transport import requests


login_bp = Blueprint("login", __name__, static_folder="static", template_folder="templates")
repo = UserRepo()

@loginManager.user_loader
def load_user(user_id):
    return repo.getUserById(user_id=user_id)

@login_bp.route("/")
def home():
    return redirect(url_for("login.login"))

@login_bp.route("/login/", methods=["POST", "GET"]) # login page
def login():
    if current_user.is_authenticated:
        return redirect(url_for("mainPage.dashboard"))
    form = LoginForm()
    recaptcha_site_key = os.getenv("RECAPTCHA_KEY")
    if form.validate_on_submit():
        print("Validated!")
        ## Captcha verificiation
        recaptcha_token = request.form.get("g-recaptcha-response")
        print(f"Captcha Token {recaptcha_token}")
        if not recaptcha_token or not recaptcha_token.strip():
            print("Token missing!")
            flash("Captcha token missing; please try again.", category="error")
            return redirect(url_for("login.login"))
        
        project_id = os.getenv("GOOGLE_PROJECT_ID")
        key = recaptcha_site_key
        print("Creating response...")
        response = create_assessment(project_id=project_id, recaptcha_key=key, 
                                    token=recaptcha_token, recaptcha_action="LOGIN")
        if response is None or response.risk_analysis.score < 0.5:
            print(f"CAPTCHA FAILED: {response.risk_analysis.reasons}")
            flash("Captcha failed! Please try again", category="error")
            return redirect(url_for("login.login"))
        ## User verification
        username = form.username.data
        user = repo.getUserByName(username)
        if user is not None:
            password = form.password.data
            verify = verify_password(hashed_password=user.hash, password=password)
            if verify:
                login_user(user, remember=True)
                return redirect(url_for("mainPage.dashboard"))
            
        flash("Password incorrect or user not found!", category="error")
        return redirect(url_for("login.login"))
    
    return render_template("login.html", form=form)

@login_bp.route("/register/", methods=["POST", "GET"])   # register page
def register():
    if current_user.is_authenticated:
        return redirect(url_for("mainPage.dashboard"))
    form = RegisterForm()
    recaptcha_site_key = os.getenv("RECAPTCHA_KEY")
    if form.validate_on_submit():
        
        print("Validated!")
        ## Captcha verificiation
        recaptcha_token = request.form.get("g-recaptcha-response")
        print(f"Captcha Token {recaptcha_token}")
        if not recaptcha_token or not recaptcha_token.strip():
            print("No captcha token")
            flash("Captcha token missing; please try again.", category="error")
            return redirect(url_for("login.register"))
        project_id = os.getenv("GOOGLE_PROJECT_ID")
        key = recaptcha_site_key
        print("Creating response...")
        response = create_assessment(project_id=project_id, recaptcha_key=key, 
                                    token=recaptcha_token, recaptcha_action="LOGIN")
        if response is None or response.risk_analysis.score < 0.5:
            print(f"CAPTCHA FAILED: {response.risk_analysis.reasons}")
            flash("Captcha failed! Please try again", category="error")
            return redirect(url_for("login.register"))

        username = form.username.data
        password = form.password.data
        password2 = form.password2.data

        if password == password2:
            print("Creating account")
            user = repo.createUser(username=username, password=password)
            
            if user is not None:
                print("User created")
                return redirect(url_for("login.home"))
            else:
                print("User not created")
                return redirect(url_for("login.register"))
        else:
            print("Password mismatch!")
            flash("Passwords does not match!", category="password_mismatch")
            return redirect(url_for("login.register"))
    else:
        return render_template("register.html", form=form)
    
@login_bp.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("login.login"))

def _create_google(username, sub, iss):
    userRepo = UserRepo()
    user = userRepo.createGoogleUser(username=username, iss=iss, sub=sub)
    return user if user else None

def _verify_google(idinfo: dict) -> bool:
    userRepo = UserRepo()
    user = userRepo.getGoogleUser(iss=idinfo['iss'], sub=idinfo['sub'])
    return True if user is not None else False


@login_bp.route("login/auth/google/", methods=["POST"])
def loginWithGoogle():
    app_dir = Path(__file__).resolve().parents[2]
    secret_path = app_dir / "Database" / "client_secret.json"

    with secret_path.open("r", encoding="utf-8") as handle:
        secret_data = json.load(handle)
        client_config = secret_data.get("web", {})
    token_handler = request.form 
    client_id = client_config.get("client_id")
    cred = token_handler["credential"]
    cookie = (request.cookies)["g_csrf_token"]
    token = token_handler["g_csrf_token"]
    if token is None:
        return 
    elif cookie is None: 
        return 
    elif token != cookie:
        return
    
    try:
        idinfo = id_token.verify_oauth2_token(cred, requests.Request(), client_id)

        print(f"ID Info: {idinfo}")
        ## Checks to make sure the ID info is valid
        if idinfo['iss'] != "https://accounts.google.com":
            flash("Error logging in with google! Invalid issuer", category="error")
            return redirect(url_for('login.login'))
        if client_id != idinfo['azp']:
            flash("Error logging in with google! Invalid Client ID", category="error")
            return redirect(url_for('login.login'))
        ## DB check to see if user exists
        verify = _verify_google(idinfo)
        print(f"Verify status: {verify}")
        if verify is True:
            userRepo = UserRepo()
            user = userRepo.getGoogleUser(iss=idinfo['iss'], sub=idinfo['sub'])
            login_user(user=user, remember=True)
            return redirect(url_for("mainPage.dashboard"))
        if verify is False:
            session['pending_google'] = {
                'iss': idinfo['iss'],
                'sub': idinfo['sub']
            }
            return redirect(url_for("login.createGoogleUsername"))

    except ValueError:
        raise "Invalid Token"

@login_bp.route("login/username/", methods=["GET", "POST"])
def createGoogleUsername():
    pending = session.get('pending_google')
    if pending is None:
        flash("Google sign-in session failed", category="error")
        return redirect(url_for('login.login'))

    iss = pending['iss']
    sub = pending['sub']
    usernameForm = UsernameForm()
    if usernameForm.validate_on_submit():
        username = usernameForm.data.username 
        user = _create_google(username=username, sub=sub, iss=iss)
        if user: 
            session.pop('pending_google', None)
            login_user(user, remember=True)
            return redirect(url_for('mainPage.dashboard'))
        else: 
            flash("Error in creating Username", category="error")
    return render_template('username.html', form=usernameForm)

@login_bp.route("login/captcha", methods=["POST"])
def captchaVerify():
    pass
