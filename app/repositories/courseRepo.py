from extensions.extensions import db
from models.courses import Course

class CourseRepo:
    def __init__(self):
        pass
    def commit(self):
        db.session.commit()

    def getCourseByName(self, user_id, course_name):
        return Course.query.filter_by(user_id=user_id, course_name=course_name).first() 

    def getAllCoursesById(self, user_id):
        return (Course.query
                .filter_by(user_id = user_id)
                .all())

    def createCourse(self, user_id, course_name):
        course = Course(
            user_id=user_id,
            course_name=course_name,
        )
        db.session.add(course)
        self.commit()
        
        return course
    
    def addCanvasCourse(self, canvasCourse):
        if len(canvasCourse) < 0:
            return False

        db.session.add_all(canvasCourse)
        self.commit()
        return True
    
    def upsertCanvasCourse(self, canvasCourses: Course) -> bool:
        for course in canvasCourses:
            old_course = Course.query.filter_by(
                user_id=course.user_id, 
                canvas_course_id=course.canvas_course_id, 
                canvas_base_url=course.canvas_base_url
                ).first()
            
            if old_course is None:
                db.session.add(course)
                continue
            else:
                MUTABLE_FIELDS = ['workflow_state', 'time_zone', 'last_sync', 'canvas_base_url']
                for field in MUTABLE_FIELDS:
                    new_entry = getattr(course, field)
                    if new_entry is None: 
                        continue
                    elif new_entry != getattr(old_course, field):
                        setattr(old_course, field, new_entry)

                db.session.add(old_course)
        else:
            self.commit()
