"""Database models for the AI Quiz Generator application."""

import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())


class Quiz(Base):
    """Quiz model representing a quiz with multiple questions."""

    __tablename__ = "quizzes"

    id = Column(String, primary_key=True, default=generate_uuid)
    topic = Column(String(255), nullable=False)
    model = Column(String(100))
    temperature = Column(Float, default=0.2)
    wikipedia_enhanced = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    questions = relationship(
        "QuizQuestion", back_populates="quiz", cascade="all, delete-orphan"
    )
    submissions = relationship(
        "QuizSubmission", back_populates="quiz", cascade="all, delete-orphan"
    )


class QuizQuestion(Base):
    """Quiz question model."""

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
    answers = relationship(
        "QuizAnswer", back_populates="question", cascade="all, delete-orphan"
    )


class QuizSubmission(Base):
    """Quiz submission model tracking user quiz attempts."""

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
    answers = relationship(
        "QuizAnswer", back_populates="submission", cascade="all, delete-orphan"
    )


class QuizAnswer(Base):
    """Individual quiz answer model."""

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
    """Chat session model for storing conversation history."""

    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String(100))  # Optional user identification
    model = Column(String(100))
    system_prompt = Column(Text, default="You are a helpful assistant.")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    """Chat message model for individual messages in conversations."""

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
