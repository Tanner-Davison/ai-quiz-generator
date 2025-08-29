import json
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models.chat import (
    ChatRequest, ConversationRequest, StreamRequest, ChatResponse
)
from services.ai_service import ai_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle single message chat requests"""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")

        logger.info(f"Processing chat with model: {request.model}")

        completion = await ai_service.generate_chat_completion(
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

        return ChatResponse(
            response=response_content,
            model=request.model or ai_service.default_model,
            usage=usage_dict,
            finishReason=finish_reason,
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while processing your request",
                "details": str(e),
            },
        )

@router.post("/conversation", response_model=ChatResponse)
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

        completion = await ai_service.generate_chat_completion(
            messages=messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.maxTokens,
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

        return ChatResponse(
            response=response_content,
            model=request.model or ai_service.default_model,
            usage=usage_dict,
            finishReason=finish_reason,
        )

    except Exception as e:
        logger.error(f"Conversation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while processing your request",
                "details": str(e),
            },
        )

@router.post("/stream")
async def chat_stream(request: StreamRequest):
    """Handle streaming chat requests"""
    async def generate():
        try:
            stream = await ai_service.generate_streaming_chat(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": request.message},
                ],
                model=request.model,
                temperature=request.temperature,
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
