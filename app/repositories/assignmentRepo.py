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

    def createAssignment(self, user_id, course_name, title, desc=None, due=None, points=None, effort=1, status=0):
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
            status=status,
            created=created,
            updated=created,
            points_possible=points,
            canvas_assignment_id=None,
            effort=effort
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

    def getAllAssignmentsByCourseId(self, user_id, course_id):
        return Assignment.query.filter_by(user_id=user_id, course_id=course_id).all()

    def deleteAllAssignmentsByCourseId(self, user_id, course_id):
        with db.session.no_autoflush:
            assignments = Assignment.query.filter_by(user_id=user_id, course_id=course_id).all()
            if assignments:
                for assignment in assignments:
                    db.session.delete(assignment)
                self.commit()
                return True
            return False

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
    
    def updateScore(self, user_id, assignment_id, score):
        """Update the score for a specific assignment"""
        assignment = self.getAssignmentById(user_id, assignment_id)
        
        if assignment is None:
            return False
        
        assignment.score = score
        assignment.updated = date.today().isoformat()
        self.commit()
        return True
    
    def getScore(self, user_id, assignment_id):
        """Retrieve the score for a specific assignment"""
        assignment = self.getAssignmentById(user_id, assignment_id)
        
        if assignment is None:
            return None
        
        return assignment.score
    
    def getAllScores(self, user_id):
        """Retrieve all assignments with their scores for a user"""
        assignments = self.getAllAssignmentById(user_id)
        
        scores_data = []
        for assignment in assignments:
            scores_data.append({
                'assignment_id': assignment.assignment_id,
                'title': assignment.title,
                'course_name': assignment.course.course_name if assignment.course else None,
                'points_possible': assignment.points_possible,
                'score': assignment.score,
                'due': assignment.due
            })
        
        return scores_data

