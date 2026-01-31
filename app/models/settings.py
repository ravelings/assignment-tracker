from extensions.extensions import db

class Settings(db.Model):
    __tablename__ = "settings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, unique=True)
    function = db.Column(db.Integer, default=0, nullable=False) # 'logistic' or 'exponential'

    def __init__(self, user_id, function="logistic"):
        self.user_id = user_id
        self.function = function
