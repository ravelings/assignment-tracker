from flask import render_template, Blueprint, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user, logout_user
from datetime import datetime, date, timezone
from repositories.userRepo import UserRepo
from repositories.assignmentRepo import AssignmentRepo
from repositories.courseRepo import CourseRepo
from integrations.canvasClient import CanvasClient
from forms.DeleteAssignment import DeleteAssignment
from services.scoring_service import ScoringService
from forms.SubmitForm import SubmitForm
from forms.assignment import AssignmentCreateForm
from forms.editAssignmentForm import EditAssignmentForm
from forms.checkForm import CheckForm
from forms.SubmitForm import SubmitForm
from Website.MainPage.dashboardFunctions import getPendingTasks

from services.googleCalendar import GoogleCalendar

mainPage_bp = Blueprint("mainPage", __name__, static_folder="static", template_folder="templates")

def _parse_due_datetime(due_value):
    if not due_value:
        return None
    if isinstance(due_value, datetime):
        return due_value if due_value.tzinfo else due_value.replace(tzinfo=timezone.utc)
    if isinstance(due_value, date):
        return datetime.combine(due_value, datetime.min.time(), tzinfo=timezone.utc)
    if isinstance(due_value, str):
        normalized = due_value.strip()
        if not normalized:
            return None
        if normalized.endswith("Z"):
            normalized = f"{normalized[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            try:
                parsed_date = date.fromisoformat(normalized)
            except ValueError:
                return None
            parsed = datetime.combine(parsed_date, datetime.min.time())
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    return None

def format_due_display(due_value):
    due_dt = _parse_due_datetime(due_value)
    if due_dt is None:
        return "No due date", None

    now = datetime.now(timezone.utc)
    delta_seconds = (due_dt - now).total_seconds()

    if delta_seconds >= 0:
        days = int(delta_seconds // 86400)
        if days == 0:
            hours = int(delta_seconds // 3600)
            return f"in {hours} hours", hours
        if days == 1:
            return "in 1 day", days * 24
        if days < 7:
            return f"in {days} days", days * 24
    else:
        days_overdue = int(abs(delta_seconds) // 86400)
        if days_overdue == 0:
            return "overdue", "overdue"
        if days_overdue == 1:
            return "overdue by 1 day", "overdue"
        if days_overdue < 7:
            return f"overdue by {days_overdue} days", "overdue"

    return due_dt.strftime("%b %d, %Y"), None

@mainPage_bp.route("/dashboard/", methods=["POST", "GET"])
@login_required
def dashboard():
    user_id = current_user.user_id
    assignmentRepo = AssignmentRepo()
    courseRepo = CourseRepo()
    userRepo = UserRepo()
    deleteForm = DeleteAssignment()
    assignmentForm = AssignmentCreateForm().updateCourseSelect(courseRepo.getAllCoursesById(user_id))
    editAssignmentForm = EditAssignmentForm()
    checkForm = CheckForm()
    googleCalendarForm = SubmitForm()
    

    sort_key = (request.args.get("sort"))
    if sort_key is None:
        sort_key = "due"
    else:
        sort_key = sort_key.strip().lower()

    SORT_MAP = {
    "course"      : assignmentRepo.get_SortedByName_Assignment,
    "due"       : assignmentRepo.get_SortedByDue_Assignment,
    "points"    : assignmentRepo.get_SortedByPoints_Assignment,
    "priority"  : assignmentRepo.getAllAssignmentById # Sort manually after calculation
    }

    assignments = SORT_MAP.get(sort_key, assignmentRepo.getAllAssignmentById)(user_id)
    pending_tally = getPendingTasks(assignments)
    print(f"Pending = {pending_tally}")
    # Calculate scores
    scoring_service = ScoringService(user_id)
    for assignment in assignments:
        # assignment.course is available via relationship
        assignment.priority_score = scoring_service.calculate_score(assignment, assignment.course)
        assignment.due_display, assignment.due_hour = format_due_display(assignment.due)

    if sort_key == "priority":
        assignments.sort(key=lambda x: x.priority_score, reverse=True)

    if deleteForm.validate_on_submit:
        print(f"Assignment ID: {deleteForm.assignment_id.data}")

    completed = userRepo.getComplete(user_id)

    return render_template("dashboard.html",
                        pending_tally=pending_tally, 
                        completed=completed,
                        assignments=assignments, 
                        deleteForm=deleteForm, 
                        assignmentForm=assignmentForm,
                        editForm=editAssignmentForm,
                        checkForm=checkForm,
                        googleCalendarForm=googleCalendarForm)

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
    user = userRepo.getUserById(user_id)
    instance = userRepo.getCanvasInstance(user_id)
    token = userRepo.getCanvasToken(user_id)

    if token is None:
        flash("Error: Token not set or expired, please set up token in settings before syncing.", category="token")
        return jsonify({"status": "failed"})
    
    client = CanvasClient(user_id=user_id, token=token, instance=instance)
    canvasCourses = client.getCourses()

    if canvasCourses is None:
        flash("Error: Token invalid.", category="fail")
        return jsonify({"status": "failed"})
    
    courseRepo = CourseRepo()
    courseRepo.upsertCanvasCourse(canvasCourses)

    ## calendar = GoogleCalendar(user) if user.calendar_id else None
    
    assignmentRepo = AssignmentRepo()
    userCourses = courseRepo.getAllCanvasCoursesById(current_user.user_id)

    for course in userCourses:
        assignments = client.getAssignmentsByCourse(user_id=current_user.user_id, course=course)
        if assignments is None:
            print("Assignment is none for {course}")
            continue 
        ## returns new assignments and changed assignments
        new, changed = assignmentRepo.createCanvasAssignment(user_id=user_id, canvasAssignment=assignments)
    """
    if calendar is not None:
        if new is not None:
            calendar.batch_create_event(new)
        if changed is not None:
            calendar.batch_update_event(changed)
    """
    
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

@mainPage_bp.route("/dashboard/assignments/<int:assignment_id>/complete", methods=["POST"])
def completeAssignment(assignment_id):
    user_id = current_user.user_id
    form = CheckForm()
    if form.validate_on_submit():
        assignmentRepo = AssignmentRepo()
        userRepo = UserRepo()
        set = assignmentRepo.setStatus(user_id=user_id, assignment_id=assignment_id)
        if set:
            print(f"Status set to: True")
            userRepo.incrementComplete(user_id)
        else:
            print(f"Status set to: False")
            userRepo.decrementComplete(user_id)
    else:
        print(form.errors)
    return redirect(url_for("mainPage.dashboard"))
