import unittest
from datetime import datetime, timedelta, timezone
from services.scoring_service import ScoringService
from models.assignment import Assignment
from models.courses import Course
from models.settings import Settings
from extensions.extensions import db
from main import app

class TestScoringService(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_calculate_urgency_logistic(self):
        # Setup Settings
        settings = Settings(user_id=1, scoring_strategy="logistic")
        db.session.add(settings)
        db.session.commit()
        
        service = ScoringService(user_id=1)
        
        # Test Case 1: Due in 72 hours (Midpoint) -> Should be 0.5
        due_date = (datetime.now(timezone.utc) + timedelta(hours=72)).isoformat()
        urgency = service.calculate_urgency(due_date)
        # 1 / (1 + exp(0.1 * (72 - 72))) = 1 / (1 + 1) = 0.5
        self.assertAlmostEqual(urgency, 0.5, places=2)

        # Test Case 2: Due Now (0 hours) -> High Urgency
        due_now = datetime.now(timezone.utc).isoformat()
        urgency_now = service.calculate_urgency(due_now)
        # 1 / (1 + exp(0.1 * (0 - 72))) = 1 / (1 + exp(-7.2)) ~ 1 / 1.0007 ~ 0.999
        self.assertGreater(urgency_now, 0.99)

    def test_calculate_urgency_exponential(self):
        # Setup Settings
        settings = Settings(user_id=1, scoring_strategy="exponential")
        db.session.add(settings)
        db.session.commit()
        
        service = ScoringService(user_id=1)

        # Test Case 1: Due in 168 hours (7 days) -> Should be approx epsilon (0.01)
        due_far = (datetime.now(timezone.utc) + timedelta(hours=168)).isoformat()
        urgency = service.calculate_urgency(due_far)
        self.assertAlmostEqual(urgency, 0.01, places=2)
        
        # Test Case 2: Due Now (0 hours) -> Should be 1.0
        due_now = datetime.now(timezone.utc).isoformat()
        urgency_now = service.calculate_urgency(due_now)
        self.assertAlmostEqual(urgency_now, 1.0, places=2)

    def test_full_scoring(self):
        # Setup
        settings = Settings(user_id=1, scoring_strategy="logistic")
        db.session.add(settings)
        db.session.commit()
        
        service = ScoringService(user_id=1)
        
        # Create Dummy Course & Assignment
        course = Course(user_id=1, course_name="Test Course", canvas_course_id=None, workflow_state=None, time_zone=None, last_sync=None, canvas_base_url=None, weight=1.5)
        
        # Due in 72 hours (Urgency 0.5), Effort 2 (1.5x), Status Pending (1.0x), Course Weight 1.5
        due_date = (datetime.now(timezone.utc) + timedelta(hours=72)).isoformat()
        assignment = Assignment(user_id=1, course_id=1, title="Test", due=due_date, effort=2, status=0)
        
        score = service.calculate_score(assignment, course)
        
        # Expected: 0.5 * 1.5 * 1.5 * 1.0 = 1.125
        self.assertAlmostEqual(score, 1.125, places=2)

if __name__ == '__main__':
    unittest.main()
