from extensions.extensions import db  # adjust import to where db is defined

class Course(db.Model):
    __tablename__ = "courses"

    assignments = db.relationship("Assignment", 
                                  back_populates="course",
                                  foreign_keys="Assignment.course_id",
                                  primaryjoin = "Course.course_id == Assignment.course_id"
                                  )

    course_id = db.Column(
        "course_id",
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id = db.Column(
        "user_id",
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    course_name = db.Column(
        "course_name",
        db.Text,
        nullable=False
    )

    canvas_course_id = db.Column(
        "canvas_course_id",
        db.Integer,
        nullable=True
    )

    workflow_state = db.Column(
        "workflow_state",
        db.Text,
        nullable=True
    )

    time_zone = db.Column(
        "time_zone",
        db.Text,
        nullable=True
    )

    last_sync = db.Column(
        "last_sync",
        db.Text,
        nullable=True
    )

    canvas_base_url = db.Column(
        "canvas_base_url",
        db.Text,
        nullable=True
    )

    def __init__(
        self,
        user_id: int,
        course_name: str,
        canvas_course_id: int | None,
        workflow_state: str | None,
        time_zone: str | None,
        last_sync: str | None,
        canvas_base_url: str | None,
    ):
        self.user_id = user_id
        self.course_name = course_name
        self.canvas_course_id = canvas_course_id
        self.workflow_state = workflow_state
        self.time_zone = time_zone
        self.last_sync = last_sync
        self.canvas_base_url = canvas_base_url

        
