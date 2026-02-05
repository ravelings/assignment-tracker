import datetime

def getPendingTasks(assignments: list) -> int:
    pending_tally = 0
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    for assignment in assignments:
        due = assignment.due
        if not isinstance(due, datetime.datetime):
            due = datetime.datetime.fromisoformat(due)
        # normalize naive datetimes to UTC so subtraction does not mix aware/naive values
        if due.tzinfo is None or due.tzinfo.utcoffset(due) is None:
            due = due.replace(tzinfo=datetime.timezone.utc)
        if due - now < datetime.timedelta(hours=168):
            pending_tally += 1
    return pending_tally
