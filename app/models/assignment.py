from extensions.extensions import db

class Assignment(db.Model):
    __tablename__ = "assignments"

    assignment_id = db.Column("assignment_id", db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column("user_id", db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    course_id = db.Column("course_id", db.Integer, db.ForeignKey("courses.course_id"), nullable=False)
    course = db.relationship("Course", back_populates="assignments", foreign_keys="Assignment.course_id")

    title = db.Column("title", db.Text, nullable=False)

    description = db.Column("description", db.Text, nullable=True)

    due = db.Column("due", db.Text, nullable=False)        # ISO-8601 text datetime recommended
    status = db.Column("status", db.Integer, nullable=True)  # 0/1 or enum-like int

    created = db.Column("created", db.Text, nullable=True)
    updated = db.Column("updated", db.Text, nullable=True)

    points_possible = db.Column("points_possible", db.Integer, nullable=True)
    score = db.Column("score", db.Float, nullable=True)  # Actual score achieved
    canvas_assignment_id = db.Column("canvas_assignment_id", db.Integer, nullable=True)
    
    workflow_state = db.Column("workflow_state", db.Text, nullable=True)
    unlock_at = db.Column("unlock_at", db.Text, nullable=True)
    html_url = db.Column("html_url", db.Text, nullable=True)
    submission_type = db.Column("submission_type", db.Text, nullable=True)
    canvas_base_url = db.Column("canvas_base_url", db.Text, nullable=True)
    last_canvas_sync = db.Column("last_canvas_sync", db.Text, nullable=True)
    effort = db.Column("effort", db.Integer, nullable=True, default=1) # 1=Low, 2=Med, 3=High

    event_id = db.Column("event_id", db.Text, nullable=True)

    def __init__(
        self,
        user_id: int,
        course_id: int,
        title: str,
        due: str,
        canvas_assignment_id=None,
        canvas_course_id=None,
        workflow_state=None,
        description=None,
        status=0,
        created=None,
        updated=None,
        points_possible=None,
        score=None,
        unlock_at=None,
        html_url=None,
        submission_type=None,
        canvas_base_url=None,
        last_canvas_sync=None,
        effort=1,
        event_id=None
    ):
        self.user_id = user_id
        self.course_id = course_id
        self.title = title
        self.due = due
        self.description = description
        self.status = status
        self.created = created
        self.updated = updated
        self.points_possible = points_possible
        self.score = score
        self.canvas_assignment_id = canvas_assignment_id
        self.canvas_course_id = canvas_course_id
        self.workflow_state = workflow_state
        self.unlock_at = unlock_at
        self.html_url = html_url
        self.submission_type = submission_type
        self.canvas_base_url = canvas_base_url
        self.last_canvas_sync = last_canvas_sync
        self.effort = effort
        self.event_id=event_id
