import datetime
import json

from repositories.userRepo import UserRepo
from repositories.assignmentRepo import AssignmentRepo

from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError

class GoogleCalendar():
    def __init__(self, userObject):
        print("Init calendar...")
        self.user_id = userObject.user_id
        self.token = userObject.google_token
        self.refresh_token = userObject.refresh_token
        self.scopes = self._parse_scopes(userObject.granted_scopes)
        self.expiry = self._parse_expiry(userObject.expiry)
        self.now = datetime.datetime.now(tz=datetime.timezone.utc)
        
        self.storage = [] # stores temp event resources for update mechanic

        if not self.token or not self.expiry:
            raise ValueError("Missing Google OAuth token or expiry; user must connect Google first.")

        if self.expiry <= self.now: # token expire test
            if not self.refresh_token:
                raise ValueError("Missing Google OAuth refresh token; user must reconnect.")
            self._refresh_token()
        
        self.cred = Credentials(token=self.token, refresh_token=self.refresh_token, scopes=self.scopes)

        userRepo = UserRepo()
        self.calendar_id = userRepo.get_calendar_id(user_id=self.user_id)
        if self.calendar_id is None:
            self.create_calendar()
            self.calendar_id = userRepo.get_calendar_id(user_id=self.user_id)

    def _parse_expiry(self, expiry_value):
        if not expiry_value:
            return None
        if isinstance(expiry_value, datetime.datetime):
            if expiry_value.tzinfo is None:
                return expiry_value.replace(tzinfo=datetime.timezone.utc)
            return expiry_value
        try:
            expiry_dt = datetime.datetime.fromisoformat(expiry_value)
            if expiry_dt.tzinfo is None:
                expiry_dt = expiry_dt.replace(tzinfo=datetime.timezone.utc)
            return expiry_dt
        except ValueError:
            return None

    def _parse_scopes(self, scopes_value):
        if not scopes_value:
            return None
        if isinstance(scopes_value, str):
            try:
                return json.loads(scopes_value)
            except json.JSONDecodeError:
                return [scopes_value]
        return scopes_value
        
    def _refresh_token(self):
        app_dir = Path(__file__).resolve().parents[1]
        secret_path = app_dir / "Database" / "client_secret.json"

        with secret_path.open("r", encoding="utf-8") as handle:
            secret_data = json.load(handle)
        web_config = secret_data.get("web", {})
        client_id = web_config.get("client_id")
        client_secret = web_config.get("client_secret")
        token_uri = web_config.get("token_uri")

        cred = Credentials(token=self.token,
                           refresh_token=self.refresh_token,
                           token_uri=token_uri,
                           client_id=client_id,
                           client_secret=client_secret,
                           scopes=self.scopes)
        try:
            cred.refresh(Request())
        except RefreshError as e:
            print("Refresh error")
            print("Error:", e)
            if hasattr(e, "description"):
                print("Description:", e.description)
            if hasattr(e, "uri"):
                print("URI:", e.uri)
            raise
        
        self.token = cred.token 
        expiry_dt = cred.expiry or datetime.datetime.now(tz=datetime.timezone.utc)
        if expiry_dt.tzinfo is None:
            expiry_dt = expiry_dt.replace(tzinfo=datetime.timezone.utc)
        self.expiry = expiry_dt.isoformat()
        userRepo = UserRepo()
        userRepo.refreshCredentials(self.user_id, self.token, self.expiry)
    
    def create_calendar(self):
        print("Create calendar called")

        body = {
            "summary" : "Osmos Tracker",
            "timeZone" : "UTC"
        }
        try:
            service = build("calendar", "v3", credentials=self.cred)
            request_insert = service.calendars().insert(body=body)
            response = request_insert.execute()
            print(f"Calendar Creation Response: {response}")
            calendar_id = response['id']
            userRepo = UserRepo()
            userRepo.set_calendar_id(self.user_id, calendar_id)

        except HttpError as e:
            print(f"An error has occured: {e}")

    def create_assignment_event(self, assignment):
        event = self._create_assignment_body(assignment)
        for attempt in range(2):
            try:
                userRepo = UserRepo()
                calendar_id = userRepo.get_calendar_id(user_id=self.user_id)
                service = build("calendar", "v3", credentials=self.cred)
                response = (service.events().insert(calendarId=calendar_id, body=event)).execute()
                print(f"Response: {response}")
                break

            except HttpError as e:
                print(f"An error has occured: {e}")
                status = e.resp.status 
                
                if status == 404:   # calendar not found / deleted
                    print("Calendar not found... creating")
                    self.create_calendar()
                    continue
                if status == 403: # OAuth failure
                    print("OAuth error")
                    raise Exception("OAuth error")
                if status == 400:
                    print("Bad request")
                    raise Exception("Bad request: invalid information")
                else:
                    print("Unkown Error")
                    raise Exception("Unkown Error")
        else:
            print("Creating event failed after 2 attempts")
            raise Exception("Creating event failed after 2 attempts")

    def _create_update_body(self, assignment):
        dt = datetime.datetime.fromisoformat(assignment.due)
        # creates timezone info
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        
        # body to be upserted into old event
        event = {
        'summary': f"{assignment.title} | {assignment.course.course_name}",
        'description': assignment.desc,
        'start': {
            'dateTime': dt.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (dt + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'UTC', 
        }
        }
        
        return event

    def _create_assignment_body(self, assignment):
        due_date = assignment.due
        title = assignment.title
        desc = assignment.description
        request_id = assignment.id
        course = assignment.course.course_name

        dt = datetime.datetime.fromisoformat(due_date)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        event = {
        'summary': f"{title} | {course}",
        'description': desc,
        'start': {
            'dateTime': dt.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (dt + datetime.timedelta(hours=1)).isoformat(),
            'timeZone': 'UTC',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
            {'method': 'popup', 'minutes': 24 * 60},
            ],
        },
        }

        return event, request_id
        
    def _handle_batch(self, request_id, response, exception):
        # request ID = Assignment ID
        if exception is not None:
            print(f"Event Assignment {request_id} failed!")
            print(f"Status: {exception.resp.status}, Error: {exception}")
            return 
        # creates/updates event ID for assignment
        event_id = response['id']
        assignmentRepo = AssignmentRepo()
        assignmentRepo.set_event_id(user_id=self.user_id, 
                                    assignment_id=request_id, 
                                    event_id=event_id)
        return

    def batch_create_event(self, assignment_list):
        try:
            userRepo = UserRepo()
            calendar_id = userRepo.get_calendar_id(user_id=self.user_id)
            service = build("calendar", "v3", credentials=self.cred)
            batch = service.new_batch_http_request()

            for assignment in assignment_list:
                event, request_id = self._create_assignment_body(assignment)
                batch.add(service.events().insert(calendarId=calendar_id, body=event), 
                        request_id=request_id,
                        callback=self._handle_batch)
            else:
                batch.execute()

        except HttpError as e:
            print(f"An error has occured: {e}")
            status = e.resp.status 
            
            if status == 404:   # calendar not found / deleted
                print("Calendar not found... creating")
                self.create_calendar()
                
            if status == 403: # OAuth failure
                print("OAuth error")
                raise Exception("OAuth error")
            if status == 400:
                print("Bad request")
                raise Exception("Bad request: invalid information")
            else:
                print("Unkown Error")
                raise Exception("Unkown Error")
            
    def batch_update_event(self, assignment_list):
        try:
            userRepo = UserRepo()
            calendar_id = userRepo.get_calendar_id(user_id=self.user_id)
            service = build("calendar", "v3", credentials=self.cred)
            batch = service.new_batch_http_request()

            for assignment in assignment_list:
                event_id = assignment.event_id
                # if assignment does not exist on calendar, skip
                if event_id is None:
                    continue
    
                event = self._create_update_body(assignment)
                batch.add(service.events().get(calendarId=calendar_id, eventId=event_id, body=event), 
                        request_id=assignment.assignment_id,
                        callback=self._handle_batch)
            else:
                batch.execute()

        except HttpError as e:
            print(f"An error has occured: {e}")
            status = e.resp.status 
            
            if status == 404:   # calendar not found / deleted
                print("Calendar not found... creating")
                self.create_calendar()
                
            if status == 403: # OAuth failure
                print("OAuth error")
                raise Exception("OAuth error")
            if status == 400:
                print("Bad request")
                raise Exception("Bad request: invalid information")
            else:
                print("Unkown Error")
                raise Exception("Unkown Error")

