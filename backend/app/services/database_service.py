from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional, TypeVar, Generic, Type
from ..database import Base

T = TypeVar('T', bound=Base)

class DatabaseService(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
    
    async def create(self, db: AsyncSession, obj_in: dict) -> T:
        """Create a new record"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def get(self, db: AsyncSession, id: str) -> Optional[T]:
        """Get a record by ID"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination"""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()
    
    async def update(self, db: AsyncSession, id: str, obj_in: dict) -> Optional[T]:
        """Update a record"""
        result = await db.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in)
            .returning(self.model)
        )
        await db.commit()
        return result.scalar_one_or_none()
    
    async def delete(self, db: AsyncSession, id: str) -> bool:
        """Delete a record"""
        result = await db.execute(delete(self.model).where(self.model.id == id))
        await db.commit()
        return result.rowcount > 0
    
    async def get_by_field(self, db: AsyncSession, field: str, value: any) -> Optional[T]:
        """Get a record by a specific field"""
        result = await db.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalar_one_or_none()
    
    async def get_many_by_field(self, db: AsyncSession, field: str, value: any) -> List[T]:
        """Get multiple records by a specific field"""
        result = await db.execute(
            select(self.model).where(getattr(self.model, field) == value)
        )
        return result.scalars().all()

# Specific service classes for each model
class QuizService(DatabaseService):
    async def get_with_questions(self, db: AsyncSession, id: str):
        """Get quiz with all questions loaded"""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.questions))
            .where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_topic(self, db: AsyncSession, topic: str) -> List:
        """Get quizzes by topic"""
        return await self.get_many_by_field(db, "topic", topic)

class QuizQuestionService(DatabaseService):
    async def get_by_quiz(self, db: AsyncSession, quiz_id: str) -> List:
        """Get all questions for a specific quiz"""
        return await self.get_many_by_field(db, "quiz_id", quiz_id)

class QuizSubmissionService(DatabaseService):
    async def get_with_answers(self, db: AsyncSession, id: str):
        """Get submission with all answers loaded"""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.answers))
            .where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_quiz(self, db: AsyncSession, quiz_id: str) -> List:
        """Get all submissions for a specific quiz"""
        return await self.get_many_by_field(db, "quiz_id", quiz_id)

class ChatSessionService(DatabaseService):
    async def get_with_messages(self, db: AsyncSession, id: str):
        """Get chat session with all messages loaded"""
        result = await db.execute(
            select(self.model)
            .options(selectinload(self.model.messages))
            .where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_user(self, db: AsyncSession, user_id: str) -> List:
        """Get chat sessions by user ID"""
        return await self.get_many_by_field(db, "user_id", user_id)
