from typing import List, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    maxTokens: Optional[int] = 1024

class ConversationRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    systemPrompt: Optional[str] = "You are a helpful assistant."
    temperature: Optional[float] = 0.7
    maxTokens: Optional[int] = 1024

class StreamRequest(BaseModel):
    message: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.7

class ChatResponse(BaseModel):
    response: str
    model: str
    usage: Optional[dict] = None
    finishReason: Optional[str] = None
