"""
Serverless function for Azure OpenAI responses on Vercel
"""

from fastapi import FastAPI, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pages.api.azure_responses_api import AzureResponsesAPIClient

app = FastAPI(title="Azure OpenAI API")

class AzureRequestModel(BaseModel):
    input_text: str
    model: str = "gpt-4.1"

@app.post("/query")
async def query_azure(request: AzureRequestModel):
    """Query Azure OpenAI API"""
    try:
        client = AzureResponsesAPIClient()
        response = client.invoke(request.input_text, request.model)
        return {"success": True, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "azure-api"}

# Vercel handler
async def handler(request: Request):
    """Main handler for Vercel serverless function"""
    return app(request)
