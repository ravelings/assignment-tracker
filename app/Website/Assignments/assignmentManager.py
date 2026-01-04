from flask import render_template, Blueprint, flash, redirect, url_for
from flask_login import login_required, current_user
from forms.assignment import AssignmentCreateForm
from repositories.assignmentRepo import AssignmentRepo

assignments_bp = Blueprint("assignments", __name__, static_folder="static", template_folder="templates")

repo = AssignmentRepo()

@assignments_bp.route("/create/", methods=["POST", "GET"])
@login_required
def createAssignment():
    form = AssignmentCreateForm()

    if form.validate_on_submit():

        user_id = current_user.user_id

        course_name = form.course_name.data 
        title = form.title.data 
        description = form.description.data 
        due = form.due.data 
        points = form.points.data 

        repo.createAssignment(
            user_id=user_id,
            course_name=course_name,
            title=title,
            desc=description,
            due=due,
            points=points
        )
        flash("Assignment created successfully!", "created")
        return redirect(url_for("assignments.createAssignment"))

    return render_template("addAssignment.html", form=form)