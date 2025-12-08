# generic_wsgi.py
import sys
import os

# Add the project directory to the sys.path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask 'app' instance from your main file
# CHANGE 'main' to the name of your python file (without .py)
from main import app as application
