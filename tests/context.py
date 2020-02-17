# Standard library imports
import sys
import os

# Local application imports
from backend.app import Application
from backend.db import db


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialise test app instance
app = Application.getTestApp()

# Ensure app is configured for Testing
if not app.config['TESTING']:
    raise SystemExit('App must be conifgured for testing')

# Clean derivatex tables in the test database
db.drop_all(bind=None)
db.create_all(bind=None)
