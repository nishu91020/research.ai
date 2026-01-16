"""
Serverless function for research agent on Vercel
"""
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create FastAPI app
app = FastAPI(
    title="Research Scholar Agent API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import research function with error handling
try:
    from pages.agent.research_agent import run_research
    logger.info("Successfully imported run_research")
except Exception as e:
    logger.error(f"Failed to import run_research: {str(e)}", exc_info=True)
    run_research = None

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "Research Scholar Agent API"}

@app.get("/research/{topic}")
async def research_endpoint(topic: str):
    """Research endpoint with streaming response"""
    if not run_research:
        raise HTTPException(status_code=500, detail="Research agent not initialized")
    
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
                await asyncio.sleep(0)
            
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
        media_type="application/x-ndjson"
    )

# Health endpoint at root for Vercel
@app.get("/")
async def root():
    return {"status": "ok", "message": "Research Agent API is running"}

# Vercel handler
handler = app
