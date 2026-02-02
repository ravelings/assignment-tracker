from flask import render_template, Blueprint, flash, redirect, url_for
from flask_login import login_required, current_user
from forms.assignment import AssignmentCreateForm
from forms.addTokenForm import AddTokenForm
from repositories.assignmentRepo import AssignmentRepo
from repositories.userRepo import UserRepo
from repositories.courseRepo import CourseRepo
from datetime import datetime

assignments_bp = Blueprint("assignments", __name__, static_folder="static", template_folder="templates")

repo = AssignmentRepo()

@assignments_bp.route("/create/", methods=["POST"])
@login_required
def createAssignment():
    courseRepo = CourseRepo()
    form = AssignmentCreateForm().updateCourseSelect(courseRepo.getAllCoursesById(current_user.user_id))

    if form.validate_on_submit():

        user_id = current_user.user_id

        course_id = form.course_id.data 
        title = form.title.data 
        description = form.description.data 
        due = datetime.fromisoformat(str(form.due.data)) 
        points = form.points.data 
        effort = form.effort.data
        status = form.status.data

        repo.createAssignment(
            user_id=user_id,
            course_id=course_id,
            title=title,
            desc=description,
            due=due,
            points=points,
            effort=effort,
            status=status
        )
        flash("Assignment created successfully!", "created")
        return redirect(url_for("mainPage.dashboard"))
    
    print("Form errors", form.errors)
    print("Assignment create error")
    return redirect(url_for("mainPage.dashboard"))

@assignments_bp.route("/addCanvasToken/", methods=["POST", "GET"])
@login_required
def addCanvasToken():
    form = AddTokenForm()
    if form.validate_on_submit:
        repo = UserRepo()
        token = form.token.data
        set = repo.setCanvasToken(user_id=current_user.user_id, token=token)

        if set:
            flash("Token set successfully!", category="token")
            redirect(url_for("assignments.addCanvasToken"))
        else:
            flash("Token set failed.", category="token")
            redirect(url_for("assignments.addCanvasToken"))
    
    return render_template("setCanvasToken.jinja2", form=form)