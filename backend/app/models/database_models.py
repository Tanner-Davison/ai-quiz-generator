from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    topic = Column(String(255), nullable=False)
    model = Column(String(100))
    temperature = Column(Float, default=0.2)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    questions = relationship("QuizQuestion", back_populates="quiz", cascade="all, delete-orphan")
    submissions = relationship("QuizSubmission", back_populates="quiz", cascade="all, delete-orphan")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    quiz_id = Column(String, ForeignKey("quizzes.id"), nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # List of strings
    correct_answer = Column(Integer, nullable=False)
    explanation = Column(Text)
    question_order = Column(Integer, default=0)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    answers = relationship("QuizAnswer", back_populates="question", cascade="all, delete-orphan")

class QuizSubmission(Base):
    __tablename__ = "quiz_submissions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    quiz_id = Column(String, ForeignKey("quizzes.id"), nullable=False)
    user_id = Column(String(100))  # Optional user identification
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quiz = relationship("Quiz", back_populates="submissions")
    answers = relationship("QuizAnswer", back_populates="submission", cascade="all, delete-orphan")

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    submission_id = Column(String, ForeignKey("quiz_submissions.id"), nullable=False)
    question_id = Column(String, ForeignKey("quiz_questions.id"), nullable=False)
    user_answer = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    
    # Relationships
    submission = relationship("QuizSubmission", back_populates="answers")
    question = relationship("QuizQuestion", back_populates="answers")

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String(100))  # Optional user identification
    model = Column(String(100))
    system_prompt = Column(Text, default="You are a helpful assistant.")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(50), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    model = Column(String(100))
    usage = Column(JSON)  # Store token usage information
    finish_reason = Column(String(100))
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
