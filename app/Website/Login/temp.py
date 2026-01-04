if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = repo.getUser(username)

        if user is not None:
            verify = verify_password(password=password, hashed_password=user.hash)
            if verify:
                session["user"] = username
                return redirect(url_for("login.home"))
        else:
            return render_template("login.html")
    else:
        return render_template("login.html")