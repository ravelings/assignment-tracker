from flask import render_template, request, redirect, url_for, flash, Blueprint, session
from flask_login import login_user, logout_user
from repositories.userRepo import UserRepo
from services.auth_service import verify_password
from forms.LoginRegister import LoginForm, RegisterForm
from extensions.extensions import loginManager

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
    if form.validate_on_submit:
        username = form.username.data
        user = repo.getUserByName(username)
        
        if user is not None:
            password = form.password.data
            verify = verify_password(hashed_password=user.hash, password=password)
            if verify:
                login_user(user)
                return redirect(url_for("login.home"))
            else:

                flash("Password incorrect or user not found!", category="login_error")
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

def loginWithGoogle():
    token_handler = request.form 
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
        google_id = idinfo['sub']

    except ValueError:
        raise "Invalid Token"
    
    return redirect(url_for("settings.settings"))