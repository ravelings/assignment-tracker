from extensions.extensions import db
from models.assignment import Assignment
from models.courses import Course
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

    def filterAssignmentByCanvasId(self, assignments):
        filtered = []
        for assignment in assignments:
                already_exist = Assignment.query.filter_by(canvas_assignment_id=assignment.canvas_assignment_id).all()
                if already_exist is None:
                    filtered.append(assignment)
        
        return filtered

    def createCanvasAssignment(self, canvasAssignment):

        if isinstance(canvasAssignment, (list, tuple)):
            filtered = self.filterAssignmentByCanvasId(assignments=canvasAssignment)
            if filtered:
                db.session.add_all(filtered)
        else:
            already_exist = Assignment.query.filter_by(canvas_assignment_id=canvasAssignment.canvas_assignment_id).all()
            if already_exist is not None:
                return 
            
            db.session.add(canvasAssignment)

        self.commit()

    def getAllAssignmentById(self, user_id):
        # returns a list of all assignments
        return (
            Assignment.query
            .filter_by(user_id=user_id)
            .order_by(Assignment.assignment_id.asc())
            .all()
        )
    
    def get_SortedByPoints_Assignment(self, user_id):
        # returns a list of all assignments sorted by points
        return (
            Assignment.query
            .filter_by(user_id=user_id)
            .order_by(Assignment.points.desc())
            .all()
        )
    def get_SortedByDue_Assignment(self, user_id):
        # returns a list of all assignments sorted by due date
        return (
            Assignment.query
            .filter_by(user_id=user_id)
            .order_by(Assignment.due.asc())
            .all()
        )
    def get_SortedByName_Assignment(self, user_id):
        # returns a list of all assignments sorted by course name
        return (
            Assignment.query
            .join(Course)
            .filter_by(user_id=user_id)
            .order_by(Course.course_name.asc())
            .all()
        )

    def getAssignmentById(self, user_id, assignment_id):
        return (
            Assignment.query 
            .filter_by(user_id=user_id, assignment_id=assignment_id) 
            .first()
        )
    
    def deleteAssignmentById(self, user_id, assignment_id):
        assignment = self.getAssignmentById(user_id, assignment_id)

        if assignment is None:
            return False
        else:
            db.session.delete(assignment)
            self.commit()
            return True

