"""
Root API endpoint for Vercel
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api")
@app.get("/")
async def root():
    """Root endpoint for debugging"""
    return JSONResponse(
        content={
            "status": "ok", 
            "message": "Research Agent API",
            "endpoints": {
                "/api/health": "Health check",
                "/api/research/{topic}": "Research endpoint"
            },
            "env_vars": {
                "AZURE_OPENAI_ENDPOINT": "set" if os.getenv("AZURE_OPENAI_ENDPOINT") else "not set",
                "AZURE_OPENAI_KEY": "set" if os.getenv("AZURE_OPENAI_KEY") else "not set"
            }
        },
        status_code=200
    )

# Vercel handler
handler = app
