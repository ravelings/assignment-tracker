from flask import render_template, Blueprint, flash, redirect, url_for
from flask import jsonify
from flask_login import login_required, current_user
from forms.courseCreateForm import CourseCreateForm
from repositories.courseRepo import CourseRepo
from repositories.userRepo import UserRepo
from integrations.canvasClient import CanvasClient

courses_bp = Blueprint("courses", __name__, static_folder="static", template_folder="templates")

@courses_bp.route("/createCourse/", methods=["POST", "GET"])
@login_required
def createCourse():
    form = CourseCreateForm()

    if form.validate_on_submit():
        repo = CourseRepo()

        user_id = current_user.user_id

        course_name = form.course_name.data 

        repo.createCourse(
            user_id=user_id,
            course_name=course_name,
        )
        flash("Course created successfully!", "created")
        return redirect(url_for("courses.createCourse"))

    return render_template("createCourse.jinja2", form=form)

@courses_bp.route("/createCourse/sync", methods=["POST"])
@login_required
def syncCourse():
    userRepo = UserRepo()
    courseRepo = CourseRepo()
    user_id = current_user.user_id
    token = userRepo.getCanvasToken(user_id)
    if token is None:
        flash("Error: Token not set, please set up token before syncing.", category="fail")
        return jsonify({"status": "failed"})
    
    client = CanvasClient(user_id=user_id, token=token, instance="canvas")
    canvasCourses =  client.getCourses()
    if canvasCourses is None:
        flash("Error: Token invalid.", category="fail")
        return jsonify({"status": "failed"})
        
    add_course = courseRepo.addCanvasCourse(canvasCourses)

    if add_course is True:
        return jsonify({"status": "success"})
    else:
        flash("Error: Sync failed.", category="fail")
        return jsonify({"status": "failed"})