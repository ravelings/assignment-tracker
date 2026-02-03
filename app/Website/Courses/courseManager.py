from flask import render_template, Blueprint, flash, redirect, url_for, request
from flask import jsonify
from flask_login import login_required, current_user
from forms.courseCreateForm import CourseCreateForm
from forms.courseWeightForm import CourseWeightForm
from forms.deleteCourseForm import DeleteCourseForm
from repositories.courseRepo import CourseRepo
from repositories.assignmentRepo import AssignmentRepo
from repositories.userRepo import UserRepo
from integrations.canvasClient import CanvasClient
from exceptions.CanvasCourseDeleteError import CanvasCourseDeleteError
from exceptions.CourseEmptyError import CourseEmptyError

courses_bp = Blueprint("courses", __name__, static_folder="static", template_folder="templates")

@courses_bp.route("/", methods=["POST", "GET"])
@login_required
def course():
    user_id = current_user.user_id
    repo = CourseRepo()
    deleteForm = DeleteCourseForm()
    weightForm = CourseWeightForm()
    courseForm = CourseCreateForm()
    sort_key = (request.args.get("sort") or "default").strip().lower()
    if sort_key is None:
        sort_key = "default"

    SORT_MAP = {
    "default"   : repo.getAllCoursesById,
    "name"      : repo.get_SortedByName_Course,
    "weight"       : repo.get_SortedByWeight_Course,
    }

    courses = SORT_MAP.get(sort_key, repo.getAllCoursesById)(user_id)

    return render_template("course.jinja2", courses=courses, form=courseForm, deleteForm=deleteForm, weightForm=weightForm)

@courses_bp.route("/create/", methods=["POST"])
@login_required
def createCourse():
    form = CourseCreateForm()

    if form.validate_on_submit():
        repo = CourseRepo()

        user_id = current_user.user_id

        course_name = form.course_name.data 
        weight = form.weight.data

        repo.createCourse(
            user_id=user_id,
            course_name=course_name,
            weight=weight
        )
        flash("Course created successfully!", "created")
        return redirect(url_for("courses.course"))
    return redirect(url_for("courses.course"))

@courses_bp.route("/sync/", methods=["POST"])
@login_required
def syncCourse():
    userRepo = UserRepo()
    courseRepo = CourseRepo()
    user_id = current_user.user_id
    token = userRepo.getCanvasToken(user_id)
    instance = userRepo.getCanvasInstance(user_id)
    if token is None:
        print("Token not set up")
        flash("Error: Token not set, please set up token before syncing.", category="fail")
        return jsonify({"status": "failed"})
    
    client = CanvasClient(user_id=user_id, token=token, instance=instance)
    canvasCourses =  client.getCourses()
    if canvasCourses is None:
        print("Canvas course is none")
        flash("Error: Token invalid.", category="fail")
        return jsonify({"status": "failed"})
        
    add_course = courseRepo.upsertCanvasCourse(canvasCourses)

    if add_course is True:
        return jsonify({"status": "success"})
    else:
        print("Unkown error")
        flash("Error: Sync failed.", category="fail")
        return jsonify({"status": "failed"})

@courses_bp.route("/delete/<int:course_id>/", methods=["POST"])
@login_required
def deleteCourse(course_id):
    print("Deleting...")
    courseRepo = CourseRepo()
    user_id = current_user.user_id

    try:
        delete = courseRepo.deleteCourse(user_id=user_id, course_id=course_id)
        assignmentRepo = AssignmentRepo()
        assignmentRepo.deleteAllAssignmentsByCourseId(user_id=user_id, course_id=course_id)
        courseRepo.commit()

    except CanvasCourseDeleteError:
        flash("WARNING: Canvas Courses cannot be deleted", category="deleteFail")
        return redirect(url_for("courses.course"))

    except CourseEmptyError:

        flash("Course not found", category="deleteFail")
        return redirect(url_for("courses.course"))

    if delete is True: 
        flash(f"Course {course_id} and all assignments associated deleted successfully", category="deleteTrue")
        return redirect(url_for("courses.course"))
    else:
        flash(f"Unkown Error", category="deleteFail")
        return redirect(url_for("courses.course"))

@courses_bp.route("/<int:course_id>/setweight/", methods=["POST"])
@login_required
def updateCourseWeight(course_id):
    form = CourseWeightForm()
    if form.validate_on_submit():
        weight = form.weight.data
        repo = CourseRepo()
        print(f"Updating Course Weight with: ID: {course_id}, Weight: {weight}")
        update = repo.updateCourseWeight(user_id=current_user.user_id, course_id=course_id, weight=weight)

        if update is True: 
            flash(f"Course {course_id} weight updated successfully", category="weight")
            return redirect(url_for("courses.course"))
        else:
            flash(f"Failed", category="weight")
            return redirect(url_for("courses.course"))
    else:
        print(form.errors)
        flash("Invalid form data", category="weight")
        return redirect(url_for("courses.course"))