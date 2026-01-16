"""
Serverless function for research agent on Vercel
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.api.researchService import app

# Vercel requires the app to be named 'app' or exported as 'handler'
# This makes the FastAPI app available to Vercel's Python runtime
handler = app
