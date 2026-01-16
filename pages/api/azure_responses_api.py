"""
Wrapper for Azure OpenAI Responses API
Handles the new input/output format instead of messages/completions
"""

import os
import requests
import json
from dotenv import load_dotenv
from langchain_core.runnables import Runnable

# Load environment variables - only load from file if it exists (local dev)
env_path = os.path.join(os.path.dirname(__file__), '..', '.env.local')
if os.path.exists(env_path):
    load_dotenv(env_path)

AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_KEY = os.getenv('AZURE_OPENAI_KEY')

if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY:
    raise ValueError("Azure OpenAI credentials not found. Please set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_KEY environment variables.")


class AzureResponsesAPIClient:
    """Client for Azure OpenAI Responses API"""
    
    def __init__(self):
        self.endpoint = AZURE_OPENAI_ENDPOINT
        self.api_key = AZURE_OPENAI_KEY
        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def invoke(self, input_text: str, model: str = "gpt-4.1") -> str:
        """
        Call the Responses API with the new input format
        
        Args:
            input_text: The prompt/input text
            model: Model to use (e.g., "gpt-4.1")
            
        Returns:
            The response output text
        """
        payload = {
            "model": model,
            "input": input_text
        }
        
        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"API Error {response.status_code}: {response.text}")
            
            result = response.json()
            # Extract the output from the response
            if "output" in result:
                return result["output"]
            else:
                return str(result)
                
        except Exception as e:
            raise Exception(f"Failed to call Azure Responses API: {str(e)}")


class ResponsesAPIChatModel(Runnable):
    """
    Wrapper to make Responses API compatible with LangChain's chat model interface
    Inherits from Runnable to work with LangChain chains
    """
    
    def __init__(self, model: str = "gpt-4.1"):
        super().__init__()
        self.client = AzureResponsesAPIClient()
        self.model = model
    
    def invoke(self, input_dict, config=None):
        """
        Invoke the model with LangChain-style input
        
        Args:
            input_dict: Dictionary with template variables or a prompt string
            config: Optional config dict for LangChain compatibility
            
        Returns:
            Object with .content attribute containing the response
        """
        # Extract the input text from the dict
        if isinstance(input_dict, dict):
            # Handle LangChain template variables
            if len(input_dict) == 1:
                input_text = list(input_dict.values())[0]
            else:
                # For multiple variables, format them as a readable string
                input_text = "; ".join([f"{k}: {v}" for k, v in input_dict.items()])
        else:
            input_text = str(input_dict)
        
        response_text = self.client.invoke(str(input_text), self.model)
        
        # Ensure response is always a string
        if isinstance(response_text, list):
            response_text = json.dumps(response_text)
        elif not isinstance(response_text, str):
            response_text = str(response_text)
        
        # Return an object with .content attribute to match LangChain's interface
        return type('Response', (), {'content': response_text})()
    
    def batch(self, inputs, config=None, **kwargs):
        """Support batch processing"""
        return [self.invoke(input_item, config) for input_item in inputs]
    
    def stream(self, input, config=None, **kwargs):
        """Support streaming (yields the single response)"""
        yield self.invoke(input, config)
