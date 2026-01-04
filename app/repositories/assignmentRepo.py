from extensions.extensions import db
from models.assignment import Assignment
from datetime import date
from repositories.courseRepo import CourseRepo

class AssignmentRepo:
    def __init__(self):
        self.courseRepo = CourseRepo() 
    
    def commit(self):
        db.session.commit()

    def createAssignment(self, user_id, course_name, title, desc=None, due=None, points=None):
        created = date.today().isoformat()

        course = self.courseRepo.getCourseByName(user_id, course_name)

        if course is None:
            course = self.courseRepo.createCourse(user_id, course_name)

        course_id = course.course_id

        assignment = Assignment(
            user_id=user_id,
            course_id = course_id,
            title=title,
            description=desc,
            due=due,
            status=0,
            created=created,
            updated=created,
            points=points,
            canvas_assignment_id=None
        )

        db.session.add(assignment)
        self.commit()