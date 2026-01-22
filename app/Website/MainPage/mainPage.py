from flask import render_template, Blueprint, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user, logout_user
from repositories.userRepo import UserRepo
from repositories.assignmentRepo import AssignmentRepo
from repositories.courseRepo import CourseRepo
from integrations.canvasClient import CanvasClient
from forms.DeleteAssignment import DeleteAssignment
from services.scoring_service import ScoringService
from forms.SubmitForm import SubmitForm
from forms.assignment import AssignmentCreateForm
from forms.editAssignmentForm import EditAssignmentForm

mainPage_bp = Blueprint("mainPage", __name__, static_folder="static", template_folder="templates")

@mainPage_bp.route("/dashboard/", methods=["POST", "GET"])
@login_required
def dashboard():
    user_id = current_user.user_id
    assignmentRepo = AssignmentRepo()
    courseRepo = CourseRepo()
    deleteForm = DeleteAssignment()
    assignmentForm = AssignmentCreateForm().updateCourseSelect(courseRepo.getAllCoursesById(user_id))
    editAssignmentForm = EditAssignmentForm()

    sort_key = (request.args.get("sort") or "default").strip().lower()
    if sort_key is None:
        sort_key = "default"

    SORT_MAP = {
    "default"   : assignmentRepo.getAllAssignmentById,
    "course"      : assignmentRepo.get_SortedByName_Assignment,
    "due"       : assignmentRepo.get_SortedByDue_Assignment,
    "points"    : assignmentRepo.get_SortedByPoints_Assignment,
    "priority"  : assignmentRepo.getAllAssignmentById # Sort manually after calculation
    }

    assignments = SORT_MAP.get(sort_key, assignmentRepo.getAllAssignmentById)(user_id)
    
    # Calculate scores
    scoring_service = ScoringService(user_id)
    for assignment in assignments:
        # assignment.course is available via relationship
        assignment.priority_score = scoring_service.calculate_score(assignment, assignment.course)

    if sort_key == "priority":
        assignments.sort(key=lambda x: x.priority_score, reverse=True)

    if deleteForm.validate_on_submit:
        print(f"Assignment ID: {deleteForm.assignment_id.data}")

    return render_template("dashboard.html", 
                           assignments=assignments, 
                           deleteForm=deleteForm, 
                           assignmentForm=assignmentForm,
                           editForm=editAssignmentForm)

@mainPage_bp.route("/userinfo/")
@login_required
def userInfo():
    submitForm = SubmitForm()
    return render_template("userInfo.html", user=current_user, submitForm=submitForm)

@mainPage_bp.route("/dashboard/logout/", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("login.login"))


@mainPage_bp.route("/dashboard/assignments/delete/<int:assignment_id>/", methods=["POST"])
@login_required
def deleteAssignment(assignment_id):
    repo = AssignmentRepo() 
    delete = repo.deleteAssignmentById(current_user.user_id, assignment_id)

    if delete is True: 
        flash(f"Assignment {assignment_id} deleted successfully", category="deleteTrue")
        return redirect(url_for("mainPage.dashboard"))
    else:
        flash(f"Failed", category="deleteFalse")
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
        assignmentRepo.createCanvasAssignment(assignments)
    
    return jsonify({"status": "success"})

@mainPage_bp.route("/dashboard/assignments/<int:assignment_id>/edit", methods=["POST"])
def editAssignment(assignment_id):
    form = EditAssignmentForm()
    if form.validate_on_submit():
        effort = form.effort.data 
        repo = AssignmentRepo()
        repo.setEffort(assignment_id, effort)
        print("Changed successful!")
    else:
        print(form.errors)
    
    return redirect(url_for("mainPage.dashboard"))


@mainPage_bp.route("/test", methods=["GET"])
def test():
    return render_template("base.html")