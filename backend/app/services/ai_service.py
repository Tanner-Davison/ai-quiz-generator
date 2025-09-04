"""AI WRAPPER SERVICE"""

from groq import Groq

from app.config import settings


class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.default_model = "llama-3.1-8b-instant"

    def get_model(self, requested_model: str = None) -> str:
        available_models = {
            "llama-3.1-8b-instant": "llama-3.1-8b-instant",
            "llama-3.1-70b-versatile": "llama-3.1-70b-versatile",
            "llama3-70b-8192": "llama3-70b-8192",
            "mixtral-8x7b-32768": "mixtral-8x7b-32768",
            "gemma-7b-it": "gemma-7b-it",
            "gemma2-9b-it": "gemma2-9b-it",
        }

        if requested_model and requested_model in available_models.values():
            return requested_model
        return self.default_model

    async def generate_chat_completion(
        self,
        messages: list,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None,
    ):
        model = self.get_model(model)
        temperature = temperature or 0.7
        max_tokens = max_tokens or 1024

        # groq library has completions and create methods called below
        completion = self.client.chat.completions.create(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=1,
            stream=False,
        )

        return completion


ai_service = AIService()
