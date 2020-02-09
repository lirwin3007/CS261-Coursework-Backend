# Standard library imports
import sys
import os

# Local application imports
from backend.app import Application


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
app = Application.getTestApp()
