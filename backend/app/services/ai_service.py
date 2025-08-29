import os
import json
from groq import Groq
from ..config import settings

class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.default_model = settings.DEFAULT_MODEL
    
    def get_model(self, requested_model: str = None) -> str:
        """Get the model to use, falling back to default if needed"""
        if requested_model and requested_model in settings.MODELS.values():
            return requested_model
        return self.default_model
    
    async def generate_chat_completion(self, messages: list, model: str = None, 
                                     temperature: float = None, max_tokens: int = None):
        """Generate a chat completion"""
        model = self.get_model(model)
        temperature = temperature or settings.DEFAULT_TEMPERATURE
        max_tokens = max_tokens or settings.DEFAULT_MAX_TOKENS
        
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
        """Generate a streaming chat completion"""
        model = self.get_model(model)
        temperature = temperature or settings.DEFAULT_TEMPERATURE
        
        stream = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=settings.DEFAULT_MAX_TOKENS,
            stream=True,
        )
        
        return stream

# Global instance
ai_service = AIService()
