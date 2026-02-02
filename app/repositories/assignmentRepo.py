from datetime import date, datetime, timezone
from extensions.extensions import db
from models.assignment import Assignment
from models.courses import Course
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

    def _compare_assignment(self, new_assignment, db_assignment):
        modified = False
        db_due = datetime.fromisoformat(db_assignment.due) if db_assignment.due is None else None
        new_due = datetime.fromisoformat(new_assignment.due) if new_assignment.due is None else None
        # if both due dates exist
        if db_due is not None and new_due is not None:
            db_assignment.due = new_assignment.due
            modified = True
        # if due date is set
        elif new_due is not None:
            db_due = new_due 
            modified = True 
        # if due date is unset
        elif db_due is not None:
            new_due = db_due 
            modified = True
            
        if db_assignment.title != new_assignment.title:
            db_assignment.title = new_assignment.title 
            modified = True
        if db_assignment.description != new_assignment.description:
            db_assignment.description = new_assignment.description
            modified = True
        
        return db_assignment if modified else None
        
            

    def _batch_filter_assignment(self, user_id, assignments):
        new_assignment = []
        changed_assignment = []
        for assignment in assignments:
                db_assignment = Assignment.query.filter_by(user_id=user_id, canvas_assignment_id=assignment.canvas_assignment_id).one_or_none()
                # if assignment not in db
                if db_assignment is None:
                    print("New Assignment")
                    new_assignment.append(assignment)
                else: 
                    print("Assigment exists already. Checking changes...")
                    compared = self._compare_assignment(new_assignment=assignment, db_assignment=db_assignment)
                    # if assignment changed, then append to changed 
                    if compared: changed_assignment.append(compared)

        return new_assignment, changed_assignment

    def createCanvasAssignment(self, user_id, canvasAssignment):
        # if a list is inputted, batch filtering is called
        print("Creating canvas assignment...")
        if isinstance(canvasAssignment, (list, tuple)):
            new_assignments, changed_assignments = self._batch_filter_assignment(user_id, assignments=canvasAssignment)
            # if new assignments are created
            if len(new_assignments) > 0:
                db.session.add_all(new_assignments)
                print("Adding new assignments...")
            # if new assignment created or assignments changed, commit
            if len(new_assignments) > 0 or len(changed_assignments) > 0:
                print("Committing...")
                self.commit()
            # return a list of new assignments and changed assignments for Google Calendar 
            return new_assignments, changed_assignments
        # single assignment object 
        else:
            db_assignment = Assignment.query.filter_by(user_id=user_id, canvas_assignment_id=canvasAssignment.canvas_assignment_id).one_or_none()
            if db_assignment is not None:
                print("Assignment already exists, comparing...")
                # compare db vs new
                db_assignment = self._compare_assignment(new_assignment=canvasAssignment, 
                                                        db_assignment=db_assignment)
                # if changed
                if db_assignment is not None:
                    self.commit()
                    # return changed assignment
                    return db_assignment
            
            print("Adding assignment...")
            db.session.add(canvasAssignment)
            self.commit()
            # return new assignment 
            return canvasAssignment

        

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
    
    def get_active_not_in_calendar(self, user_id, course_id):
        # returns assignment whose due date is in the future
        
        now_iso = datetime.now(timezone.utc)
        assignments = Assignment.query.filter(
                Assignment.user_id == user_id,
                Assignment.course_id == course_id,
                Assignment.status != 1,
                Assignment.event_id.is_(None)
            ).all()
        # if no assignment found
        if len(assignments) < 0: return None 
        active = []
        # finding active assignments
        for assignment in assignments:
            if datetime.fromisoformat(assignment.due) > now_iso: active.append(assignment)
        # return if found
        return active if len(active) > 0 else None
    
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
    
    def set_event_id(self, user_id, assignment_id, event_id):
        assignment = Assignment.query.filter_by(user_id=user_id, assignment_id=assignment_id).first()
        assignment.event_id = event_id 
        self.commit()
        return
