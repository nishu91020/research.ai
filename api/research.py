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
import traceback

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
run_research = None
import_error = None

try:
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Files in parent: {os.listdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))}")
    
    from pages.agent.research_agent import run_research
    logger.info("Successfully imported run_research")
except Exception as e:
    import_error = f"{str(e)}\n{traceback.format_exc()}"
    logger.error(f"Failed to import run_research: {import_error}")


@app.get("/api/research/{topic}")
async def research_endpoint(topic: str):
    """Research endpoint with streaming response"""
    
    if import_error:
        logger.error(f"Cannot process request due to import error: {import_error}")
        raise HTTPException(
            status_code=500, 
            detail=f"Research agent initialization failed: {import_error}"
        )
    
    if not run_research:
        raise HTTPException(status_code=500, detail="Research agent not initialized")
    
    if not topic or len(topic.strip()) == 0:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    
    async def stream_research():
        try:
            executor = ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            
            logger.info(f"Starting research for topic: {topic}")
            
            # Run the research workflow
            result = await loop.run_in_executor(executor, run_research, topic)
            
            logger.info(f"Research completed for topic: {topic}")
            
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
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Error during research for topic '{topic}': {error_detail}")
            yield json.dumps({
                "type": "error",
                "message": f"Error during research: {str(e)}"
            }) + "\n"
    
    return StreamingResponse(
        stream_research(),
        media_type="application/x-ndjson"
    )

# Vercel handler
handler = app
