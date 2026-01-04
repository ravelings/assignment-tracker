from extensions.extensions import db  # adjust import to where db is defined

class Course(db.Model):
    __tablename__ = "courses"

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
        nullable=True
    )

    canvas_id = db.Column(
        "canvas_id",
        db.Integer,
        nullable=True
    )

    def __init__(
        self,
        user_id: int,
        course_name: str | None = None,
        canvas_id: int | None = None
    ):
        self.user_id = user_id
        self.course_name = course_name
        self.canvas_id = canvas_id
