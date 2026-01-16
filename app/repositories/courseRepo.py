from extensions.extensions import db
from models.courses import Course
from exceptions.CanvasCourseDeleteError import CanvasCourseDeleteError
from exceptions.CourseEmptyError import CourseEmptyError

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
    def get_SortedByName_Course(self, user_id):
        return (Course.query
                .filter_by(user_id = user_id)
                .order_by(Course.course_name.asc())
                .all())
                
    def get_SortedByWeight_Course(self, user_id):
        return (Course.query
                .filter_by(user_id = user_id)
                .order_by(Course.weight.asc())
                .all())


    def createCourse(self, user_id, course_name, weight=1.0):
        # creates a course
        course = Course(
            user_id=user_id,
            course_name=course_name,
            weight=weight,
        )
        db.session.add(course)
        self.commit()
        
        return course
    
    def deleteCourse(self, user_id, course_id):
        course = Course.query.filter_by(user_id=user_id, course_id=course_id).first()

        if course is None:
            db.session.rollback()
            raise CourseEmptyError("Course not found")

        if course.canvas_course_id is not None:
            db.session.rollback()
            raise CanvasCourseDeleteError("Canvas Course cannot be deleted")

        with db.session.no_autoflush:
            db.session.delete(course)
            return True

    def addCanvasCourse(self, canvasCourse):
        if len(canvasCourse) < 0:
            return False

        db.session.add_all(canvasCourse)
        self.commit()
        return True

    def updateCourseWeight(self, user_id, course_id, weight):
        course = Course.query.filter_by(user_id=user_id, course_id=course_id).first()
        if course is None:
            print("Course not found")
            return False

        course.weight = int(weight)
        db.session.add(course)
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
                new_course = Course(
                    user_id=course.user_id,
                    course_name=course.course_name,
                    canvas_course_id=course.canvas_course_id,
                    workflow_state=course.workflow_state,
                    time_zone=course.time_zone,
                    last_sync=None,
                    canvas_base_url=None,
                    weight=course.weight
                )
                db.session.add(new_course)
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
