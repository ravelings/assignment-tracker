import datetime

def getPendingTasks(assignments: list) -> int:
    pending_tally = 0
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    for assignment in assignments:
        due = datetime.datetime.fromisoformat(assignment['due_at'])
        if due - now < datetime.timedelta(hours=168):
            pending_tally += 1
    return pending_tally