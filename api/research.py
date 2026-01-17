"""
Serverless function for research agent on Vercel
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
import os
import json
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import research function with error handling
run_research = None
import_error = None

try:
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Try importing from agent directory first (cleaner path)
    try:
        from agent.research_agent import run_research
        logger.info("Successfully imported run_research from agent.research_agent")
    except ImportError:
        # Fall back to pages.agent path
        from pages.agent.research_agent import run_research
        logger.info("Successfully imported run_research from pages.agent.research_agent")
        
except Exception as e:
    import_error = f"{str(e)}\n{traceback.format_exc()}"
    logger.error(f"Failed to import run_research: {import_error}")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse URL to extract topic
            parsed_path = urlparse(self.path)
            path_parts = parsed_path.path.split('/')
            
            # Extract topic from /api/research/{topic}
            topic = None
            if len(path_parts) >= 4 and path_parts[1] == 'api' and path_parts[2] == 'research':
                topic = path_parts[3]
            
            if not topic or len(topic.strip()) == 0:
                self.send_error(400, "Topic cannot be empty")
                return
            
            # Check for import errors
            if import_error:
                logger.error(f"Cannot process request due to import error: {import_error}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": "Research agent initialization failed",
                    "detail": import_error
                }).encode())
                return
            
            if not run_research:
                self.send_error(500, "Research agent not initialized")
                return
            
            logger.info(f"Starting research for topic: {topic}")
            
            # Run the research workflow
            result = run_research(topic)
            
            logger.info(f"Research completed for topic: {topic}")
            
            # Send successful response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.end_headers()
            
            # Format response
            response = {
                "topic": topic,
                "field": result.get("field", ""),
                "fetched_data": result.get("fetched_data", {}),
                "selected_articles": result.get("selected_articles", []),
                "article": result.get("article", ""),
                "summary": result.get("summary", "")
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            logger.error(f"Error during research: {error_detail}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Error during research",
                "detail": str(e)
            }).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
