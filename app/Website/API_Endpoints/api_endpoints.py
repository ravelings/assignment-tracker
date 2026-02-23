from datetime import datetime
from repositories.userRepo import UserRepo
from integrations.canvasClient import CanvasClient

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from models.assignment import Assignment
from repositories.assignmentRepo import AssignmentRepo
from repositories.courseRepo import CourseRepo 
from models.courses import Course

api_bp = Blueprint("api", __name__, template_folder="templates")

@api_bp.route("/auth/login", methods=["POST"])
def login():
    content_type = request.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        return jsonify({"error": "Invalid data type"}), 400
    data = request.get_json(silent=True)
    
    if data is None:
        return jsonify({"error": "Invalid/Missing JSON"}), 400
    
    username = data.get("username")
    password = data.get("password")
    print(f"Received username: {username}, password: {password}")
    
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    
    userRepo = UserRepo()
    user = userRepo.getUserByName(username)
    access_token = create_access_token(identity=user.user_id)
    refresh_token = create_refresh_token(identity=user.user_id)
    print(f"Returned: access token: {access_token}, refresh_token: {refresh_token}")
    
    return jsonify(access_token=access_token, refresh_token=refresh_token)
        
@api_bp.route("/courses/get/all", methods=["POST"])
@jwt_required()
def courses_get_all():
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity in token"}), 400
    courseRepo = CourseRepo()
    courses = courseRepo.getAllCoursesById(user_id)

    def serialize_assignment(course):
        serialized = {}
        for column in Course.__table__.columns:
            value = getattr(course, column.name)
            if isinstance(value, datetime):
                serialized[column.name] = value.isoformat()
            else:
                serialized[column.name] = value
        return serialized

    payload = {
        str(course.course_id): serialize_assignment(course)
        for course in courses
    }

    return jsonify(payload), 200

    
@api_bp.route("/assignments/get/all", methods=["POST"])
@jwt_required()
def assignments_get_all():
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity in token"}), 400
    assignmentRepo = AssignmentRepo()
    assignments = assignmentRepo.getAllAssignmentById(user_id)
    active_assignments = [assignment for assignment in assignments if assignment.status != 1]

    def serialize_assignment(assignment):
        serialized = {}
        for column in Assignment.__table__.columns:
            value = getattr(assignment, column.name)
            if isinstance(value, datetime):
                serialized[column.name] = value.isoformat()
            else:
                serialized[column.name] = value
        return serialized

    payload = {
        str(assignment.assignment_id): serialize_assignment(assignment)
        for assignment in active_assignments
    }

    return jsonify(payload), 200

@api_bp.route("/sync/canvas", methods=["POST"])
@jwt_required()
def sync_canvas():
    try:
        user_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid user identity in token"}), 401
    userRepo = UserRepo()
    instance = userRepo.getCanvasInstance(user_id)
    token = userRepo.getCanvasToken(user_id)

    if token is None:
        return jsonify({"status": "failed"}), 400
    
    client = CanvasClient(user_id=user_id, token=token, instance=instance)
    canvasCourses = client.getCourses()

    if canvasCourses is None:
        return jsonify({"status": "failed"}), 400
    
    courseRepo = CourseRepo()
    courseRepo.upsertCanvasCourse(canvasCourses)

    ## calendar = GoogleCalendar(user) if user.calendar_id else None
    
    assignmentRepo = AssignmentRepo()
    userCourses = courseRepo.getAllCanvasCoursesById(user_id)

    for course in userCourses:
        assignments = client.getAssignmentsByCourse(user_id=user_id, course=course)
        if assignments is None:
            print("Assignment is none for {course}")
            continue 
        ## returns new assignments and changed assignments
        new, changed = assignmentRepo.createCanvasAssignment(user_id=user_id, canvasAssignment=assignments)
    else:
        return jsonify({"status": "success"}), 200