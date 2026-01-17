"""
Root API endpoint for Vercel
"""
from http.server import BaseHTTPRequestHandler
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        response = {
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
        }
        
        self.wfile.write(json.dumps(response).encode())
        return
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
