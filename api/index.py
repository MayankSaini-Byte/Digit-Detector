import os
import sys

# Append parent directory to sys.path so Vercel can locate app.py and models correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
