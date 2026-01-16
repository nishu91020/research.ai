"""FastAPI Service for Research Scholar Agent

This module provides REST API endpoints for the Research Scholar Agent,
allowing external applications to request research on specific topics.
"""

import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import asyncio
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
    fetched_data: dict
    selected_artices: list
    summary: str
    article: str

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://researchai-vert.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ==================== Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service is running"""
    return {"status": "ok", "service": "Research Scholar Agent API"}

@app.get("/research/{topic}")
async def research_endpoint(topic: str):
    """
    Research a topic using the AI Research Scholar Agent with streaming response.
    
    This endpoint performs in-depth analysis leveraging various research websites
    and streams the comprehensive article with summary.
    
    Args:
        topic: The topic to research (e.g., "AI in medicine", "quantum computing")
        
    Returns:
        StreamingResponse yielding JSON chunks containing:
        - topic: The researched topic
        - field: Classified field/discipline
        - fetched_data: Research data chunks
        - selected_articles: Article sources
        - article: Full drafted article (streamed)
        - summary: Key findings summary
        
    Raises:
        HTTPException: If research fails or topic is invalid
        
    Example:
        GET /research/machine%20learning
    """
    if not topic or len(topic.strip()) == 0:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    async def stream_research():
        try:
            executor = ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            
            # Run the research workflow
            result = await loop.run_in_executor(executor, run_research, topic)
            
            # Stream the response chunks
            yield json.dumps({
                "type": "metadata",
                "topic": topic,
                "field": result.get("field", ""),
                "fetched_data": result.get("fetched_data", {}),
                "selected_articles": result.get("selected_articles", [])
            }) + "\n"
            
            # Stream the article in chunks
            article = json.loads(result.get("article", []))[0].get("content",[])[0].get("text","")
            chunk_size = 100
            for i in range(0, len(article), chunk_size):
                yield json.dumps({
                    "type": "article",
                    "text": article[i:i + chunk_size]
                }) + "\n"
                await asyncio.sleep(0)  # Allow other tasks to run
            
            # Stream the summary
            yield json.dumps({
                "type": "summary",
                "text": json.loads(result.get("summary", []))[0].get("content",[])[0].get("text","")
            }) + "\n"
            
            yield json.dumps({"type": "complete"}) + "\n"
            
        except Exception as e:
            logger.error(f"Error during research for topic '{topic}': {str(e)}", exc_info=True)
            yield json.dumps({
                "type": "error",
                "message": f"Error during research: {str(e)}"
            }) + "\n"
    
    return StreamingResponse(
        stream_research(),
        media_type="application/x-ndjson"  # Newline-delimited JSON
    )

# ==================== Main ====================

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    

