import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import wikipedia
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Available models on Groq
MODELS = {
    "LLAMA3_70B": "llama3-70b-8192",
    "LLAMA3_8B": "llama3-8b-8192",
    "MIXTRAL": "mixtral-8x7b-32768",
    "GEMMA_7B": "gemma-7b-it",
    "GEMMA2_9B": "gemma2-9b-it",
}

# Default model
DEFAULT_MODEL = MODELS["LLAMA3_70B"]

# In-memory storage for quiz results (in production, use a database)
quiz_results = []


# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = DEFAULT_MODEL
    temperature: Optional[float] = 0.7
    maxTokens: Optional[int] = 1024


class Message(BaseModel):
    role: str
    content: str


class ConversationRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = DEFAULT_MODEL
    systemPrompt: Optional[str] = "You are a helpful assistant."
    temperature: Optional[float] = 0.7
    maxTokens: Optional[int] = 1024


class StreamRequest(BaseModel):
    message: str
    model: Optional[str] = DEFAULT_MODEL
    temperature: Optional[float] = 0.7


# New quiz-related models
class QuizRequest(BaseModel):
    topic: str
    model: Optional[str] = DEFAULT_MODEL
    temperature: Optional[float] = (
        0.3  # Lower temperature for more consistent quiz generation
    )


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int  # Index of correct answer (0-3)
    explanation: str


class QuizResponse(BaseModel):
    topic: str
    questions: List[QuizQuestion]
    generated_at: str


class QuizSubmission(BaseModel):
    quiz_id: str
    answers: List[int]  # User's selected answers (0-3 for each question)


class QuizResult(BaseModel):
    quiz_id: str
    topic: str
    user_answers: List[int]
    correct_answers: List[int]
    score: int
    total_questions: int
    percentage: float
    submitted_at: str
    feedback: List[str]  # Explanation for each answer


# Create FastAPI app
app = FastAPI(title="AI Quiz Generator", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_wikipedia_context(topic: str) -> str:
    """Get relevant context from Wikipedia to improve factual accuracy"""
    try:
        # Search for the topic
        search_results = wikipedia.search(topic, results=3)
        if not search_results:
            return ""

        # Get summary of the first result
        page = wikipedia.page(search_results[0], auto_suggest=False)
        summary = page.summary[:1000]  # Limit to first 1000 characters

        return f"Context about {topic}: {summary}"
    except Exception as e:
        print(f"Wikipedia context error: {e}")
        return ""


def generate_quiz_prompt(topic: str, context: str) -> str:
    """Generate a comprehensive prompt for quiz creation"""
    return f"""You are an expert educator creating a multiple-choice quiz about "{topic}".

{context}

Create exactly 5 multiple-choice questions with the following requirements:
1. Each question should test different aspects of the topic
2. All questions should be factual and accurate
3. Each question must have exactly 4 options (A, B, C, D)
4. Only one option should be correct
5. Include an explanation for why the correct answer is right

Format your response as a JSON object with this exact structure:
{{
    "questions": [
        {{
            "question": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Explanation of why this answer is correct"
        }}
    ]
}}

Ensure the JSON is valid and follows the exact structure above. The correct_answer should be the index (0-3) of the correct option."""


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check server health status"""
    return {
        "status": "OK",
        "message": "Server is running",
        "availableModels": list(MODELS.keys()),
    }


# List available models
@app.get("/models")
async def get_models():
    """Get list of available models"""
    return {
        "models": MODELS,
        "recommended": DEFAULT_MODEL,
        "description": "All models are free to use with rate limits",
    }


# Generate quiz endpoint
@app.post("/quiz/generate")
async def generate_quiz(request: QuizRequest):
    """Generate a quiz based on the given topic"""
    try:
        if not request.topic:
            raise HTTPException(status_code=400, detail="Topic is required")

        print(f"Generating quiz for topic: {request.topic}")

        # Get Wikipedia context for factual accuracy
        context = get_wikipedia_context(request.topic)

        # Generate quiz prompt
        prompt = generate_quiz_prompt(request.topic, context)

        completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educator. Always respond with valid JSON in the exact format requested.",
                },
                {"role": "user", "content": prompt},
            ],
            model=request.model,
            temperature=request.temperature,
            max_tokens=2048,
            top_p=1,
            stream=False,
        )

        if not completion.choices or not completion.choices[0].message:
            raise HTTPException(status_code=500, detail="No response generated")

        response_content = completion.choices[0].message.content

        # Try to parse the JSON response
        try:
            # Clean up the response to extract JSON
            if "```json" in response_content:
                json_start = response_content.find("```json") + 7
                json_end = response_content.find("```", json_start)
                if json_end != -1:
                    response_content = response_content[json_start:json_end].strip()
            elif "```" in response_content:
                json_start = response_content.find("```") + 3
                json_end = response_content.find("```", json_start)
                if json_end != -1:
                    response_content = response_content[json_start:json_end].strip()

            quiz_data = json.loads(response_content)

            # Validate the structure
            if "questions" not in quiz_data or not isinstance(
                quiz_data["questions"], list
            ):
                raise ValueError("Invalid quiz structure")

            # Create quiz response
            quiz_response = QuizResponse(
                topic=request.topic,
                questions=[
                    QuizQuestion(
                        question=q["question"],
                        options=q["options"],
                        correct_answer=q["correct_answer"],
                        explanation=q["explanation"],
                    )
                    for q in quiz_data["questions"]
                ],
                generated_at=datetime.now().isoformat(),
            )

            return quiz_response

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"JSON parsing error: {e}")
            print(f"Response content: {response_content}")
            raise HTTPException(
                status_code=500,
                detail="Failed to parse quiz response. Please try again.",
            )

    except Exception as e:
        print(f"Quiz generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while generating the quiz",
                "details": str(e),
            },
        )


# Submit quiz answers endpoint
@app.post("/quiz/submit")
async def submit_quiz(submission: QuizSubmission):
    """Submit quiz answers and get results"""
    try:
        # For now, we'll generate a simple quiz ID
        # In production, you'd store the original quiz and retrieve it
        quiz_id = submission.quiz_id

        # This is a simplified version - in production you'd retrieve the actual quiz
        # For now, we'll return a mock result
        correct_answers = [0, 1, 2, 3, 4]  # Mock correct answers

        if len(submission.answers) != 5:
            raise HTTPException(status_code=400, detail="Must submit exactly 5 answers")

        # Calculate score
        score = sum(
            1
            for user_ans, correct_ans in zip(submission.answers, correct_answers)
            if user_ans == correct_ans
        )

        # Generate feedback
        feedback = []
        for i, (user_ans, correct_ans) in enumerate(
            zip(submission.answers, correct_answers)
        ):
            if user_ans == correct_ans:
                feedback.append(f"Question {i+1}: Correct! Well done.")
            else:
                feedback.append(
                    f"Question {i+1}: Incorrect. The correct answer was option {chr(65 + correct_ans)}."
                )

        result = QuizResult(
            quiz_id=quiz_id,
            topic="Sample Topic",  # In production, get from stored quiz
            user_answers=submission.answers,
            correct_answers=correct_answers,
            score=score,
            total_questions=5,
            percentage=(score / 5) * 100,
            submitted_at=datetime.now().isoformat(),
            feedback=feedback,
        )

        # Store result
        quiz_results.append(result)

        return result

    except Exception as e:
        print(f"Quiz submission error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while processing the quiz submission",
                "details": str(e),
            },
        )


# Get quiz results endpoint
@app.get("/quiz/results")
async def get_quiz_results():
    """Get all quiz results"""
    return {"results": quiz_results, "total": len(quiz_results)}


# Simple chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle single message chat requests"""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")

        print(f"Processing chat with model: {request.model}")

        completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant. Provide clear and concise responses.",
                },
                {"role": "user", "content": request.message},
            ],
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.maxTokens,
            top_p=1,
            stream=False,
        )

        response_content = "No response generated"
        finish_reason = None
        usage_dict = None

        if completion.choices:
            if completion.choices[0].message:
                response_content = completion.choices[0].message.content
            finish_reason = completion.choices[0].finish_reason

        if completion.usage:
            usage_dict = {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens,
            }

        return {
            "response": response_content,
            "model": request.model,
            "usage": usage_dict,
            "finishReason": finish_reason,
        }

    except Exception as e:
        # Handle rate limiting
        if hasattr(e, "status_code") and e.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded. Please wait a moment and try again.",
                    "retryAfter": "60 seconds",
                },
            )

        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while processing your request",
                "details": str(e),
            },
        )


# Chat with conversation history
@app.post("/chat/conversation")
async def chat_conversation(request: ConversationRequest):
    """Handle chat with conversation history"""
    try:
        if not request.messages:
            raise HTTPException(status_code=400, detail="Messages array is required")

        # Prepare messages with system prompt
        messages = [{"role": "system", "content": request.systemPrompt}]

        # Add user messages
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})

        completion = groq_client.chat.completions.create(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.maxTokens,
            top_p=1,
            stream=False,
        )

        response_content = "No response generated"
        finish_reason = None
        usage_dict = None

        if completion.choices:
            if completion.choices[0].message:
                response_content = completion.choices[0].message.content
            finish_reason = completion.choices[0].finish_reason

        if completion.usage:
            usage_dict = {
                "prompt_tokens": completion.usage.prompt_tokens,
                "completion_tokens": completion.usage.completion_tokens,
                "total_tokens": completion.usage.total_tokens,
            }

        return {
            "response": response_content,
            "model": request.model,
            "usage": usage_dict,
            "finishReason": finish_reason,
        }

    except Exception as e:
        # Handle rate limiting
        if hasattr(e, "status_code") and e.status_code == 429:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded. Please wait a moment and try again.",
                    "retryAfter": "60 seconds",
                },
            )

        print(f"Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while processing your request",
                "details": str(e),
            },
        )


# Streaming chat endpoint
@app.post("/chat/stream")
async def chat_stream(request: StreamRequest):
    """Handle streaming chat requests"""

    async def generate():
        try:
            stream = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": request.message},
                ],
                model=request.model,
                temperature=request.temperature,
                max_tokens=1024,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, "content") and delta.content:
                        yield f"data: {json.dumps({'content': delta.content})}\n\n"

            yield "data: [DONE]\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


# Main entry point
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 3000))

    print(f"🚀 AI Quiz Generator server running at http://localhost:{port}")
    print("\nAvailable endpoints:")
    print(f"  GET  http://localhost:{port}/health")
    print(f"  GET  http://localhost:{port}/models")
    print(f"  POST http://localhost:{port}/quiz/generate")
    print(f"  POST http://localhost:{port}/quiz/submit")
    print(f"  GET  http://localhost:{port}/quiz/results")
    print(f"  POST http://localhost:{port}/chat")
    print(f"  POST http://localhost:{port}/chat/conversation")
    print(f"  POST http://localhost:{port}/chat/stream")
    print(f"  GET  http://localhost:{port}/docs (Swagger UI)")
    print(f"  GET  http://localhost:{port}/redoc (ReDoc)")
    print("\nMake sure to set your GROQ_API_KEY in the .env file!")

    uvicorn.run(app, host="0.0.0.0", port=port)
