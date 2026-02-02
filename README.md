## Osmo Tracker

**Live app: <https://osmotracker.app>**

An app allow users to track assignments. Includes integrations with Canvas LMS, allowing users to sync their 
Canvas assignments with Osmo; Google Calendar, allowing assignments to be created automatically as events.

## How to Set up Locally
DB template is included inside /app/database/database_template.db, please make a copy of
a seperate DB to use locally. Make sure to modify db_path inside main-debug.py

Google OAuth does not work locally unless client_secret.json is provided -- please 
make your own and follow setups accordingly.

### 1. Install all dependencies:
pip install -r requirements.txt

### 2. Start Flask Dev Web Server
Run main-debug.py

Connect to: localhost:5000


