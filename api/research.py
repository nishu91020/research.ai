"""
Serverless function for research agent on Vercel
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.api.researchService import app as research_app

# Create FastAPI app for Vercel
app = FastAPI(title="Research Agent API")

# Mount research routes
app.mount("/", research_app)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "research-agent"}

# Vercel handler
async def handler(request: Request):
    """Main handler for Vercel serverless function"""
    return app(request)
