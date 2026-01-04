from extensions.extensions import db
from models.courses import Course

class CourseRepo:
    def __init__(self):
        pass
    def commit(self):
        db.session.commit()

    def getCourseByName(self, user_id, course_name):
        return Course.query.filter_by(user_id=user_id, course_name=course_name).first() 

    def createCourse(self, user_id, course_name):
        course = Course(
            user_id=user_id,
            course_name=course_name,
        )
        db.session.add(course)
        self.commit()
        
        return course
