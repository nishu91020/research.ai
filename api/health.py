"""
Health check endpoint for Vercel
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
@app.get("/")
async def health_check():
    """Health check endpoint"""
    return JSONResponse(
        content={"status": "ok", "service": "Research Scholar Agent API"},
        status_code=200
    )

# Vercel handler
handler = app
