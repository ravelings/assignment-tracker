import json
import logging
import requests 
from models.assignment import Assignment
from models.courses import Course
from datetime import datetime, timezone, date, timedelta

class CanvasClient:

    def __init__(self, user_id, token, instance):
        self.user_id = user_id
        self.token = token
        self.base_url = "https://"+instance+".instructure.com/api/v1/users/self/"

    def verifyToken(self):
        pass 

    def call_api(self, type, id=None):
        if id is None:
            request_url = self.base_url + f"{type}"
        else:
            request_url = self.base_url + f"{type}" + "/" + f"{id}"
            
        request = request_url+"?access_token="+self.token 
        resp = requests.get(request)
        logging.error("Canvas status=%s content-type=%s", resp.status_code, resp.headers.get("Content-Type"))
        logging.error("Canvas body head=%r", resp.text[:200])
        return resp

    def getCourses(self):
        request_url = self.base_url + "courses"
        request = request_url+"?access_token="+self.token

        resp = requests.get(request)
        logging.error("Canvas status=%s content-type=%s", resp.status_code, resp.headers.get("Content-Type"))
        logging.error("Canvas body head=%r", resp.text[:200])
        courses = resp.json()
        print("Course Obtained")
        today = date.today().isoformat()
        if [next(iter(courses))] == "errors":
            return None
        course_list = []
        for course in courses:
            end_at = course['end_at']
            if end_at:
                if today > course['end_at']:
                    continue
            
            to_append = Course(
                user_id=self.user_id,
                course_name = course['name'],
                course_code = course['course_code'],
                canvas_course_id=course['id'],
                workflow_state=course['workflow_state'],
                time_zone=course['time_zone'],
                end_at=course['end_at'],
                last_sync=datetime.now(timezone.utc).isoformat(),
                canvas_base_url=self.base_url
            )
            course_list.append(to_append)

        if len(course_list) > 0:
            return course_list 
        else:
            return None
            

    def getCourseById(self, course_id):
        course = self.call_api(type='courses', id=course_id)
        if course:
            course = course.json()
            courseObject = Course(
                user_id=self.user_id,
                course_name = course['name'],
                course_code = course['course_code'],
                canvas_course_id=course['id'],
                workflow_state=course['workflow_state'],
                time_zone=course['time_zone'],
                end_at=course['end_at'],
                last_sync=datetime.now(timezone.utc).isoformat(),
                canvas_base_url=self.base_url
            )
            return courseObject
        return None

    def _create_assignment_list(self, user_id, course_id, canvas_course_id, assignments: Assignment):
        assignments_list = []
        continue_page = True
        
        for assignment in assignments:
        # print(f"Assigment Object: {assignment}")
            state = assignment['workflow_state']
            due = assignment['due_at']
            if state != "published":
                print("Assignment unavailable")
                continue
            if due is None:
                print("No due date")
                continue

            print(f"Assignment Course ID: {course_id}" )
            due_date = datetime.fromisoformat(assignment['due_at'])
            created = datetime.fromisoformat(assignment['created_at'])
            updated = datetime.fromisoformat(assignment['updated_at'])
            raw_unlock = assignment.get("unlock_at")
            
            today = datetime.now(timezone.utc).date()
            due = due_date.date()
            
            if due < today:
                continue
            
            if raw_unlock:
                unlock = datetime.fromisoformat(raw_unlock)
            else:
                unlock = None
            assignment_obj = Assignment(
                user_id=user_id,
                course_id=course_id,
                title=assignment['name'],
                due=due_date, # date 
                canvas_assignment_id=assignment['id'],
                canvas_course_id=int(canvas_course_id),
                workflow_state=assignment['workflow_state'],
                description=assignment['description'],
                status=None,
                created=created,
                updated=updated,
                points_possible=assignment['points_possible'],
                unlock_at=unlock,
                html_url=assignment['html_url'],
                submission_type=json.dumps(assignment.get('submission_types')),
                canvas_base_url=self.base_url,
                last_canvas_sync=datetime.now(timezone.utc)
            )
            if due > today + timedelta(days=21):
                continue_page = False
                print("Due date exceeded 21 days, stopping page continuation")
                continue
            
            assignments_list.append(assignment_obj)
            
        print("Assignment created")
        return assignments_list, continue_page
    
    def getAssignmentsByCourse(self, user_id: int, course: Course):
        state = course.workflow_state
        end_at = course.end_at
        today = date.today().isoformat()
        print(f"Course Object: {course}")
        if state not in ("available", "active", "published"):
            print("Course unavailable")
            return None
        if end_at:
            if today > end_at:
                print("Course expired")
                return None
        canvas_course_id = str(course.canvas_course_id)
        course_id = course.course_id
        request_url = self.base_url + "courses/" + canvas_course_id + "/assignments/"
        print(f"Fetching assignment for {course}")
        resp = requests.get(request_url, params={"access_token": self.token, "per_page": 50})
        assignments_list = []
        # while loop for parsing response to assignment -> next page
        while resp:
            assignments =  resp.json()
            assignments, continue_page = self._create_assignment_list(user_id=user_id,
                                                                    course_id=course_id,
                                                                    canvas_course_id=canvas_course_id,
                                                                    assignments=assignments)
            print(f"Assignment Object obtained")
            assignments_list.extend(assignments)
            next_link = resp.links.get("next")
            if continue_page is False or not next_link:
                break 
            resp = requests.get(next_link["url"])
        
        if len(assignments_list) > 0:
            print(f"Returned assignment list for {course}")
            return assignments_list 
        else:
            print(f"Returned None for {course}")
            return None
