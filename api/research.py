"""
Serverless function for research agent on Vercel
"""
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import sys
import os

os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGCHAIN_ENDPOINT"] = ""
os.environ["LANGCHAIN_API_KEY"] = ""

import json
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

run_research = None
import_error = None

try:
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    from api.research_agent import run_research
    logger.info("Successfully imported run_research from api.research_agent")
        
except Exception as e:
    import_error = f"{str(e)}\n{traceback.format_exc()}"
    logger.error(f"Failed to import run_research: {import_error}")


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            path_parts = parsed_path.path.split('/')
            
            topic = None
            if len(path_parts) >= 4 and path_parts[1] == 'api' and path_parts[2] == 'research':
                topic = path_parts[3]
            
            if not topic or len(topic.strip()) == 0:
                self.send_error(400, "Topic cannot be empty")
                return
            
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
            
            result = run_research(topic)
            
            logger.info(f"Research completed for topic: {topic}")
            
            article_raw = result.get("article", "")
            try:
                parsed_article = json.loads(article_raw)
                if isinstance(parsed_article, list):
                    for item in parsed_article:
                        if isinstance(item, dict) and item.get("type") == "message":
                            content = item.get("content", [])
                            if content and len(content) > 0:
                                for content_item in content:
                                    if content_item.get("type") == "output_text":
                                        article = content_item.get("text", article_raw)
                                        break
                                break
                    else:
                        article = article_raw
                else:
                    article = article_raw
            except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                article = article_raw
            
            summary_raw = result.get("summary", "")
            try:
                parsed_summary = json.loads(summary_raw)
                if isinstance(parsed_summary, list):
                    for item in parsed_summary:
                        if isinstance(item, dict) and item.get("type") == "message":
                            content = item.get("content", [])
                            if content and len(content) > 0:
                                for content_item in content:
                                    if content_item.get("type") == "output_text":
                                        summary = content_item.get("text", summary_raw)
                                        break
                                break
                    else:
                        summary = summary_raw
                else:
                    summary = summary_raw
            except (json.JSONDecodeError, KeyError, IndexError, TypeError):
                summary = summary_raw
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.end_headers()
            
            response_data = {
                "topic": topic,
                "field": result.get("field", ""),
                "fetched_data": result.get("fetched_data", {}),
                "selected_articles": result.get("selected_articles", []),
                "article": article,
                "summary": summary
            }
            
            self.wfile.write(json.dumps(response_data).encode())
            
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
