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

    def createAssignment(self, user_id, course_id, title, desc=None, due=None, points=None, effort=1, status=0):
        created = date.today().isoformat()

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

    def filterAssignmentByCanvasId(self, user_id, assignments):
        filtered = []
        for assignment in assignments:
                already_exist = Assignment.query.filter_by(user_id=user_id, canvas_assignment_id=assignment.canvas_assignment_id).all()
                if len(already_exist) == 0:
                    print("Filtered.")
                    filtered.append(assignment)
                else: 
                    print("Assigment exists already")
        
        return filtered

    def createCanvasAssignment(self, user_id, canvasAssignment):
        print("Creating canvas assignment...")
        if isinstance(canvasAssignment, (list, tuple)):
            filtered = self.filterAssignmentByCanvasId(user_id, assignments=canvasAssignment)
            if filtered:
                db.session.add_all(filtered)
        else:
            already_exist = Assignment.query.filter_by(user_id, canvas_assignment_id=canvasAssignment.canvas_assignment_id).all()
            if already_exist is not None:
                print("Assignment already exists")
                return
            
            print("Adding assignment...")
            db.session.add(canvasAssignment)

        print("Commiting...")
        self.commit()

    def moveCompleted(self, assignment_list):
        active = [a for a in assignment_list if a.status != 1]
        completed = [a for a in assignment_list if a.status == 1]
        return active + completed

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
        return self.moveCompleted(
            Assignment.query
            .filter_by(user_id=user_id)
            .order_by(Assignment.assignment_id.asc())
            .all()
        )
    
    def get_SortedByPoints_Assignment(self, user_id):
        # returns a list of all assignments sorted by points
        return self.moveCompleted(
            Assignment.query
            .filter_by(user_id=user_id)
            .order_by(Assignment.points_possible.desc())
            .all()
        )
    def get_SortedByDue_Assignment(self, user_id):
        # returns a list of all assignments sorted by due date
        return self.moveCompleted(
            Assignment.query
            .filter_by(user_id=user_id)
            .order_by(Assignment.due.asc())
            .all()
        )
    def get_SortedByName_Assignment(self, user_id):
        # returns a list of all assignments sorted by course name
        return self.moveCompleted(
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

    def setEffort(self, assignment_id, effort):
        assignment = Assignment.query.filter_by(assignment_id=assignment_id).first()
        if assignment is None:
            return False
        
        assignment.effort = effort 
        assignment.updated = date.today().isoformat()
        self.commit()
        return True
    
    def setStatus(self, user_id, assignment_id):
        assignment = Assignment.query.filter_by(user_id=user_id, assignment_id=assignment_id).first()
        if assignment.status == 0:
            assignment.status = 1
            self.commit()
            return True
        else:
            assignment.status = 0
            self.commit()
            return False   