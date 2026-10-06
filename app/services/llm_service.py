import json
from typing import Dict, Any
import httpx
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.is_mock = settings.MOCK_LLM

    def generate(self, prompt: str) -> str:
        if self.is_mock:
            return "This is a mock response from the LLM."
        
        try:
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except Exception as e:
            return f"Error connecting to LLM: {str(e)}"
    
    def structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        if self.is_mock:
            # Very basic mock
            if "route" in str(schema):
                return {"route": "RAG"}
            return {}
            
        try:
            # Using Ollama format=json
            sys_prompt = f"Respond strictly in JSON matching this schema: {json.dumps(schema)}"
            response = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": sys_prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=30.0
            )
            response.raise_for_status()
            res_text = response.json().get("response", "{}")
            return json.loads(res_text)
        except Exception:
            # Fallback for routing
            if "route" in str(schema):
                return {"route": "CLARIFICATION"}
            return {}
