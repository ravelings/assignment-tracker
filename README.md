## Osmos Tracker
A simple CRUD app that allows users to track assignments. Includes integrations with Canvas LMS, allowing users to sync their 
Canvas assignments with Osmos; Google Calendar, allowing assignments to be created automatically as events.

## How to Set up Locally
Example DB is included inside /app/database/database.db

### Install all dependencies:

## Flask:
pip install Flask Flask-SQLAlchemy Flask-Login WTForms 

## Google Calendar API + OAuth:
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib

### Run main.py
