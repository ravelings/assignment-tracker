from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from repositories.userRepo import UserRepo
from repositories.assignmentRepo import AssignmentRepo
from repositories.courseRepo import CourseRepo
from forms.SubmitForm import SubmitForm
from services.googleCalendar import GoogleCalendar

calendar_bp = Blueprint("calendar", __name__, template_folder="templates")

@calendar_bp.route("/dashboard/calendar/", methods=["GET", "POST"])
@login_required
def calendar():
    form = SubmitForm()
    return render_template("calendar.html", submitForm=form)

@calendar_bp.route("/dashboard/calendar/sync", methods=["POST"])
@login_required
def sync():
    form = SubmitForm()
    if form.validate_on_submit():
        user_id = current_user.user_id
        userRepo = UserRepo() 
        user = userRepo.getUserById(user_id)
        # if user does not have a calendar
        if user.calendar_id is None:
            return 
        assignmentRepo = AssignmentRepo()
        courseRepo = CourseRepo()
        courses = courseRepo.getAllCoursesById(user_id=user_id)
        to_add = []
        for course in courses:
            assignments = assignmentRepo.get_active_not_in_calendar(user_id=user_id, course_id=course.course_id)
            # if assignment not in calendar exists, add to list
            if assignments: to_add.extend(assignments)
        # if no assignments to add, return
        if len(to_add) < 0: 
            print("No assignments to be added.")
            return 

        calendar = GoogleCalendar(user)
        print(f"Adding {len(to_add)} assignments...")
        calendar.batch_create_event(to_add)
            
    return redirect(url_for("calendar.calendar"))
        
        