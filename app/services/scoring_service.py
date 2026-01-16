import math
from datetime import datetime, timezone
from models.settings import Settings
from models.assignment import Assignment
from models.courses import Course

class ScoringService:
    def __init__(self, user_id):
        self.user_id = user_id
        self.strategy = self._get_strategy()

    def _get_strategy(self):
        settings = Settings.query.filter_by(user_id=self.user_id).first()
        if settings:
            return settings.scoring_strategy
        return "logistic" # Default

    def calculate_urgency(self, due_date_iso):
        if not due_date_iso:
            return 0.0

        try:
            due_date = datetime.fromisoformat(due_date_iso)
            if due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)
            
            now = datetime.now(timezone.utc)
            time_diff = (due_date - now).total_seconds() / 3600.0 # Hours remaining (t)
            
            # If overdue, max urgency? Or treat as 0 time left?
            # Let's say overdue is high urgency, but logic fails if t < 0
            # For this model, let's treat t < 0 as t = 0 (max urgency)
            if time_diff < 0:
                time_diff = 0.0

            if self.strategy == "logistic":
                # Option 1: Logistic Function (3 Day Spike)
                # |u|(t) = 1 / (1 + exp(k(t - 72)))
                # k adjusts steepness. Let's pick k=0.1 for now as an arbitrary slope
                k = 0.1
                t_val = time_diff
                return 1.0 / (1.0 + math.exp(k * (t_val - 72.0)))

            elif self.strategy == "exponential":
                # Option 2: Exponential Decay
                # |u|(t) = epsilon * exp(ln(1/epsilon)/168 * t)
                # Wait, formula was |u|(t) = exp( ln(1/epsilon) / 168 * t) ??? No logic check
                # User wrote: |u|(t) = exp( ln(1/epsilon)/168 * t )
                # Wait, this increases as t increases? No, we want urgency to INCREASE as t DECREASES.
                # Urgency should be high when t is small.
                # Standard decay: N(t) = N0 * e^(-kt)
                # Let's re-read user request:
                # "Option 2: Continuous Pressure... minimum value epsilon at T=168"
                # This implies urgency is LOW at T=168 and HIGH at T=0.
                # If formula is exp( -k * t ), at t=0, val=1. At t=T, val=epsilon.
                # epsilon = exp(-k*T) -> ln(epsilon) = -kT -> k = -ln(epsilon)/T = ln(1/epsilon)/T
                # So Urgency U(t) = exp( - (ln(1/epsilon)/168) * t )
                
                epsilon = 0.01 # Minimum urgency at 7 days out
                T = 168.0
                k = math.log(1.0/epsilon) / T
                return math.exp(-k * time_diff)

        except Exception as e:
            print(f"Error calculating urgency: {e}")
            return 0.0
        
        return 0.0

    def calculate_score(self, assignment: Assignment, course: Course):
        # 1. Urgency
        urgency_score = self.calculate_urgency(assignment.due)

        # 2. Effort (Multiplier)
        # 1=Low, 2=Med, 3=High. 
        # Let's map this to a multiplier: Low=1.0, Med=1.5, High=2.0
        effort_map = {1: 1.0, 2: 1.5, 3: 2.0}
        effort_multiplier = effort_map.get(assignment.effort, 1.0)

        # 3. Course Weight (Multiplier)
        # 0.0 - 2.0
        weight_multiplier = course.weight if course.weight is not None else 1.0

        # 4. Status
        # Pending vs In Progress vs Finished
        # Finished should be 0 score (hidden/done)
        # In Progress should have a bonus to avoid context switching
        # Let's say bonus = 1.2x
        # We need to access status. Assignment model has status as Integer or String? 
        # Plan said: "Update status usage... enum(PENDING, IN PROGRESS, FINISHED)"
        # Current model: status = db.Column("status", db.Integer, nullable=True) # 0/1 or enum-like int
        # Let's assume: 0=Pending, 1=In Progress, 2=Finished
        
        status_multiplier = 1.0
        if assignment.status == 1: # In Progress
            status_multiplier = 1.2
        elif assignment.status == 2: # Finished
            return 0.0

        # Final Score Formula
        # Score = Urgency * Effort * Weight * Status
        final_score = urgency_score * effort_multiplier * weight_multiplier * status_multiplier
        
        return final_score
