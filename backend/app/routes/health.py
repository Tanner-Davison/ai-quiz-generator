import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_async_db
from ..utils.db_utils import health_check_database

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """Check server health status"""
    return {
        "status": "OK",
        "message": "Server is running",
        "environment": settings.ENVIRONMENT,
        "groq_configured": bool(settings.GROQ_API_KEY),
    }


@router.get("/health/database")
async def database_health_check(db: AsyncSession = Depends(get_async_db)):
    """Check database health status"""
    return await health_check_database(db)


@router.get("/models")
async def get_models():
    """Get list of available models"""
    available_models = {
        "llama-3.1-8b-instant": "llama-3.1-8b-instant",
        "llama-3.1-70b-versatile": "llama-3.1-70b-versatile",
        "llama3-70b-8192": "llama3-70b-8192",
        "mixtral-8x7b-32768": "mixtral-8x7b-32768",
        "gemma-7b-it": "gemma-7b-it",
        "gemma2-9b-it": "gemma2-9b-it",
    }

    return {
        "models": available_models,
        "recommended": "llama-3.1-8b-instant",
        "description": "All models are free to use with rate limits",
        "current_default": "llama-3.1-8b-instant",
        "model_descriptions": {
            model_id: f"Groq {model_name} model"
            for model_name, model_id in available_models.items()
        },
    }


@router.get("/test-model/{model_name}")
async def test_model(model_name: str):
    """Test a specific model with a simple prompt"""
    from ..services.ai_service import ai_service

    try:
        # Test the model with a simple JSON generation task
        test_prompt = 'Generate a simple JSON object with one question: {"questions": [{"question": "What is 2+2?", "options": ["3", "4", "5", "6"], "correct_answer": 1, "explanation": "2+2 equals 4"}]}'

        completion = await ai_service.generate_chat_completion(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Generate the exact JSON requested.",
                },
                {"role": "user", "content": test_prompt},
            ],
            model=model_name,
            temperature=0.1,
            max_tokens=100,
        )

        if completion.choices and completion.choices[0].message:
            response = completion.choices[0].message.content
            return {
                "model": model_name,
                "success": True,
                "response": response,
                "response_length": len(response),
                "starts_with_json": response.strip().startswith("{"),
                "contains_questions": '"questions"' in response,
            }
        else:
            return {
                "model": model_name,
                "success": False,
                "error": "No response generated",
            }

    except Exception as e:
        return {"model": model_name, "success": False, "error": str(e)}
