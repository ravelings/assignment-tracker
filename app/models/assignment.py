from extensions.extensions import db

class Assignment(db.Model):
    __tablename__ = "assignments"

    assignment_id = db.Column("assignment_id", db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column("user_id", db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    course_id = db.Column("course_id", db.Integer, db.ForeignKey("courses.course_id"), nullable=False)

    title = db.Column("title", db.Text, nullable=False)

    description = db.Column("description", db.Text, nullable=True)

    due = db.Column("due", db.Text, nullable=False)        # ISO-8601 text datetime recommended
    status = db.Column("status", db.Integer, nullable=True)  # 0/1 or enum-like int

    created = db.Column("created", db.Text, nullable=True)
    updated = db.Column("updated", db.Text, nullable=True)

    points = db.Column("points", db.Integer, nullable=True)
    canvas_assignment_id = db.Column("canvas_assignment_id", db.Integer, nullable=True)

    def __init__(
        self,
        user_id: int,
        course_id: int,
        title: str,
        due: str,
        description=None,
        status=None,
        created=None,
        updated=None,
        points=None,
        canvas_assignment_id=None,
    ):
        self.user_id = user_id
        self.course_id = course_id
        self.title = title
        self.due = due
        self.description = description
        self.status = status
        self.created = created
        self.updated = updated
        self.points = points
        self.canvas_assignment_id = canvas_assignment_id