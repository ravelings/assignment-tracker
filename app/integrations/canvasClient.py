import json
import requests 
from models.assignment import Assignment
from models.courses import Course
from datetime import datetime, timezone

class CanvasClient:

    def __init__(self, user_id, token, instance):
        self.user_id = user_id
        self.token = token
        self.base_url = "https://"+instance+".instructure.com/api/v1/"

    def verifyToken(self):
        pass 

    def getCourses(self):
        request_url = self.base_url + "courses"
        request = request_url+"?access_token="+self.token

        courses = requests.get(request).json()
        print(f"Course status: {courses}")
        if [next(iter(courses))] == "errors":
            return None
        course_list = []
        for course in courses:
            to_append = Course(
                user_id=self.user_id,
                course_name = course['name'],
                canvas_course_id=course['id'],
                workflow_state=course['workflow_state'],
                time_zone=course['time_zone'],
                last_sync=datetime.now(timezone.utc).isoformat(),
                canvas_base_url=self.base_url
            )
            course_list.append(to_append)

        if len(course_list) > 0:
            return course_list 
        else:
            return None
            

    def getAssignmentsByCourse(self, user_id: int, course: Course):
        if course.workflow_state != "available":
            return None
        
        canvas_course_id = str(course.canvas_course_id)
        course_id = course.course_id
        request_url = self.base_url + "courses/" + canvas_course_id + "/assignments"
        request = request_url+"?access_token="+self.token

        assignments = requests.get(request).json()

        assignment_list = []

        for assignment in assignments:
            print(f"Course ID: {course_id}" )
            to_append = Assignment(
                user_id=user_id,
                course_id=course_id,
                title=assignment['name'],
                due=assignment['due_at'], # date 
                canvas_assignment_id=assignment['id'],
                canvas_course_id=int(canvas_course_id),
                workflow_state=assignment['workflow_state'],
                description=assignment['description'],
                status=None,
                created=assignment['created_at'],
                updated=assignment['updated_at'],
                points_possible=assignment['points_possible'],
                unlock_at=assignment['unlock_at'],
                html_url=assignment['html_url'],
                submission_type=json.dumps(assignment.get('submission_types')),
                canvas_base_url=self.base_url,
                last_canvas_sync=datetime.now(timezone.utc).isoformat()
            )

            assignment_list.append(to_append)
        
        if len(assignment_list) > 0:
            return assignment_list 
        else:
            return None
