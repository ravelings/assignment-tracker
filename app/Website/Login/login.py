from pathlib import Path
import json

from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from flask_login import login_user, logout_user
from repositories.userRepo import UserRepo
from services.auth_service import verify_password
from forms.LoginRegister import LoginForm, RegisterForm
from extensions.extensions import loginManager

from google.oauth2 import id_token
from google.auth.transport import requests


login_bp = Blueprint("login", __name__, static_folder="static", template_folder="templates")
repo = UserRepo()

@loginManager.user_loader
def load_user(user_id):
    return repo.getUserById(user_id=user_id)

@login_bp.route("/")
def home():
    return render_template("home.html") # home page

@login_bp.route("/login/", methods=["POST", "GET"]) # login page
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        user = repo.getUserByName(username)
        
        if user is not None:
            password = form.password.data
            verify = verify_password(hashed_password=user.hash, password=password)
            if verify:
                login_user(user)
                return redirect(url_for("login.home"))
            else:

                flash("Password incorrect or user not found!", category="error")
                return redirect(url_for("login.login"))
    
    return render_template("login.html", form=form)

@login_bp.route("/register/", methods=["POST", "GET"])   # register page
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        password2 = form.password2.data

        if password == password2:
            user = repo.createUser(username=username, password=password)
            
            if user is not None:
                return redirect(url_for("login.home"))
            else:
                return redirect(url_for("login.register"))
        else:
            flash("Passwords does not match!", category="password_mismatch")
            return redirect(url_for("login.register"))
    else:
        return render_template("register.html")
    
@login_bp.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for("login.login"))

def _create_or_verify_google(idinfo: dict, client_id: str) -> bool:
    print(f"ISS: {idinfo['iss']}")
    print(f"Client ID: {idinfo['azp']} vs {client_id}")
    if idinfo['iss'] != "https://accounts.google.com": return False
    if client_id != idinfo['azp']: return False 
    userRepo = UserRepo()
    user = userRepo.getGoogleUser(iss=idinfo['iss'], sub=idinfo['sub'])
    
    if user is not None: return True 
    # create
    print(f"iss {idinfo['iss']}")
    print(f"sub: {idinfo['sub']}")
    user = userRepo.createGoogleUser(iss=idinfo['iss'], sub=idinfo['sub'])
    return True if user else False

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
        creation = _create_or_verify_google(idinfo, client_id)
        print(f"Creation status: {creation}")
        if creation is True:
            userRepo = UserRepo()
            user = userRepo.getGoogleUser(iss=idinfo['iss'], sub=idinfo['sub'])
            login_user(user=user)
            return redirect(url_for("mainPage.dashboard"))
        else:
            flash("Error logging in with Google!", "error")
            return redirect(url_for("login.login"))

    except ValueError:
        raise "Invalid Token"