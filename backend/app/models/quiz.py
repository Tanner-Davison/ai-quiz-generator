"""Quiz Classes"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class QuizRequest(BaseModel):
    topic: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.2
    wikipediaEnhanced: Optional[bool] = False
    enhancedPrompt: Optional[str] = None


class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str


class WikipediaContext(BaseModel):
    articles: List[dict] = []
    key_facts: List[str] = []
    related_topics: List[str] = []
    summary: str = ""


class QuizResponse(BaseModel):
    quiz_id: Optional[str] = None
    topic: str
    questions: List[QuizQuestion]
    generated_at: str
    wikipedia_context: Optional[WikipediaContext] = None
    wikipedia_enhanced: Optional[bool] = False


class QuizSubmission(BaseModel):
    quiz_id: str
    answers: List[int]


class QuizResult(BaseModel):
    quiz_id: str
    topic: str
    user_answers: List[int]
    correct_answers: List[int]
    score: int
    total_questions: int
    percentage: float
    submitted_at: str
    feedback: List[str]


class QuizHistory(BaseModel):
    id: str
    topic: str
    model: Optional[str]
    temperature: float
    created_at: datetime
    question_count: int
    submission_count: int
    average_score: Optional[float] = None
    wikipediaEnhanced: Optional[bool] = False
