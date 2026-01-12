from flask import render_template, Blueprint, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from repositories.userRepo import UserRepo
from repositories.assignmentRepo import AssignmentRepo
from repositories.courseRepo import CourseRepo
from integrations.canvasClient import CanvasClient
from forms.DeleteAssignment import DeleteAssignment

mainPage_bp = Blueprint("mainPage", __name__, static_folder="static", template_folder="templates")

@mainPage_bp.route("/dashboard/", methods=["POST", "GET"])
@login_required
def dashboard():
    user_id = current_user.user_id
    repo = AssignmentRepo()
    deleteForm = DeleteAssignment()
    sort_key = (request.args.get("sort") or "default").strip().lower()
    if sort_key is None:
        sort_key = "default"

    SORT_MAP = {
    "default"   : repo.getAllAssignmentById,
    "course"      : repo.get_SortedByName_Assignment,
    "due"       : repo.get_SortedByDue_Assignment,
    "points"    : repo.get_SortedByPoints_Assignment
    }

    assignments = SORT_MAP.get(sort_key)(user_id)

    if deleteForm.validate_on_submit:
        print(f"Assignment ID: {deleteForm.assignment_id.data}")

    return render_template("dashboard.jinja2", assignments=assignments, deleteForm=deleteForm)

@mainPage_bp.route("/userinfo/")
@login_required
def userInfo():
    return render_template("userInfo.html", user=current_user)

@mainPage_bp.route("/dashboard/assignments/delete/<int:assignment_id>/", methods=["POST"])
@login_required
def deleteAssignment(assignment_id):
    repo = AssignmentRepo() 
    delete = repo.deleteAssignmentById(current_user.user_id, assignment_id)

    if delete is True: 
        flash(f"Assignment {assignment_id} deleted successfully", category="deleteTrue")
        return redirect(url_for("mainPage.dashboard"))
    else:
        flash(f"Failed", category="deleteTrue")
        return redirect(url_for("mainPage.dashboard"))
    
@mainPage_bp.route("/dashboard/assignments/sync", methods=["POST"])
@login_required
def syncAssignments():
    userRepo = UserRepo()
    user_id = current_user.user_id
    token = userRepo.getCanvasToken(user_id)

    if token is None:
        flash("Error: Token not set, please set up token before syncing.", category="token")
        return jsonify({"status": "failed"})
    
    client = CanvasClient(user_id=user_id, token=token, instance="canvas")
    canvasCourses = client.getCourses()

    if canvasCourses is None:
        flash("Error: Token invalid.", category="fail")
        return jsonify({"status": "failed"})
    
    courseRepo = CourseRepo()
    courseRepo.upsertCanvasCourse(canvasCourses)

    assignmentRepo = AssignmentRepo()
    userCourses = courseRepo.getAllCoursesById(current_user.user_id)
    for course in userCourses:
        assignments = client.getAssignmentsByCourse(user_id=current_user.user_id, course=course)
        if assignments is None:
            continue 
        assignmentRepo. (assignments)
    
    return jsonify({"status": "success"})
