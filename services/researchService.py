"""FastAPI Service for Research Scholar Agent

This module provides REST API endpoints for the Research Scholar Agent,
allowing external applications to request research on specific topics.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import asyncio
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import os

# Dynamically import research_agent from the same directory
spec = importlib.util.spec_from_file_location("research_agent", 
                                               os.path.join(os.path.dirname(__file__), "../agent/research_agent.py"))
research_agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(research_agent)

run_research = research_agent.run_research

# ==================== Pydantic Models ====================

class ResearchResponse(BaseModel):
    """Response model for research results"""
    topic: str
    field: str
    article: str
    summary: str

class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str
    topic: str

# ==================== FastAPI Application ====================

app = FastAPI(
    title="Research Scholar Agent API",
    version="1.0.0",
    description="API for AI-powered research on various topics across multiple disciplines"
)

# ==================== Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running"""
    return {"status": "ok", "service": "Research Scholar Agent API"}

@app.get("/research/{topic}", response_model=ResearchResponse)
async def research_endpoint(topic: str):
    """
    Research a topic using the AI Research Scholar Agent
    
    This endpoint performs in-depth analysis leveraging various research websites
    and returns a comprehensive article with summary.
    
    Args:
        topic: The topic to research (e.g., "AI in medicine", "quantum computing")
        
    Returns:
        ResearchResponse containing:
        - topic: The researched topic
        - field: Classified field/discipline
        - article: Full drafted article with headings and hashtags
        - summary: Key findings summary
        
    Raises:
        HTTPException: If research fails or topic is invalid
        
    Example:
        GET /research/machine%20learning
    """
    if not topic or len(topic.strip()) == 0:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    try:
        # Run the research workflow in a thread pool to avoid blocking
        executor = ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(executor, run_research, topic)
        
        return ResearchResponse(
            topic=topic,
            field=result.get("field", ""),
            article=result.get("article", ""),
            summary=result.get("summary", "")
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error during research: {str(e)}"
        )

# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    

