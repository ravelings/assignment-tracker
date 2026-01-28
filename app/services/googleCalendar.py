import datetime
import json

from repositories.userRepo import UserRepo

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

    def create_assignment_event(self, due_date):
        dt = datetime.datetime.fromisoformat(due_date)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        event = {
        'summary': 'Test Event',
        'description': 'Osmos Tracker Test',
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

        
