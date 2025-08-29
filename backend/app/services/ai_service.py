import os
import json
from groq import Groq
from ..config import settings

class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.default_model = "llama3-8b-8192"
    
    def get_model(self, requested_model: str = None) -> str:
        available_models = {
            "llama3-8b-8192": "llama3-8b-8192",
            "llama3-70b-8192": "llama3-70b-8192",
            "gemma-7b-it": "gemma-7b-it",
            "gemma2-9b-it": "gemma2-9b-it"
        }
        
        if requested_model and requested_model in available_models.values():
            return requested_model
        return self.default_model
    
    async def generate_chat_completion(self, messages: list, model: str = None, 
                                     temperature: float = None, max_tokens: int = None):
        model = self.get_model(model)
        temperature = temperature or 0.7
        max_tokens = max_tokens or 1024
        
        completion = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            stream=False,
        )
        
        return completion
    
    async def generate_streaming_chat(self, messages: list, model: str = None,
                                    temperature: float = None):
        model = self.get_model(model)
        temperature = temperature or 0.7
        
        stream = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=1024,
            stream=True,
        )
        
        return stream

ai_service = AIService()
