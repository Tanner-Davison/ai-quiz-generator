from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class QuizRequest(BaseModel):
    topic: str
    model: Optional[str] = None
    temperature: Optional[float] = 0.2

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: int
    explanation: str

class QuizResponse(BaseModel):
    topic: str
    questions: List[QuizQuestion]
    generated_at: str

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
