"""Quiz API routes"""

import logging
from datetime import datetime
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_db
from app.models.database_models import Quiz, QuizQuestion
from app.models.database_models import QuizSubmission as DBQuizSubmission
from app.models.quiz import (
    QuizHistory,
    QuizRequest,
    QuizResponse,
    QuizResult,
    QuizSubmission,
)
from app.services.database_service import (
    QuizDatabaseService,
    QuizQuestionService,
    QuizSubmissionService,
)
from app.services.quiz_service import quiz_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize database services
quiz_db_service = QuizDatabaseService(Quiz)
question_db_service = QuizQuestionService(QuizQuestion)
submission_db_service = QuizSubmissionService(DBQuizSubmission)

# In-memory storage (temporary - replace with database-only approach)
current_quiz = None
quiz_results = []


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    force_model: str = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Generate a quiz based on the given topic"""
    global current_quiz

    try:
        # Override model if specified
        if force_model:
            request.model = force_model

        # Generate quiz content
        if request.enhancedPrompt and request.wikipediaEnhanced:
            result = await quiz_service.generate_enhanced_quiz(request)
        else:
            result = await quiz_service.generate_quiz(request)

        # Save to database
        quiz_id = await _save_quiz_to_database(db, request, result)
        result.quiz_id = quiz_id

        # Store in memory as fallback
        current_quiz = result

        return result

    except ValueError as e:
        logger.error("Quiz generation validation error: %{e}")
        raise HTTPException(
            status_code=400, detail={"error": "Invalid quiz request", "details": str(e)}
        )

    except Exception as e:
        logger.error("Quiz generation error: %{e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Quiz generation failed", "details": str(e)},
        )


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(
    submission: QuizSubmission, db: AsyncSession = Depends(get_async_db)
):
    """Submit quiz answers and get results"""
    try:
        # Get quiz and questions
        quiz, questions = await _get_quiz_and_questions(db, submission.quiz_id)

        # Validate submission
        if len(submission.answers) != len(questions):
            raise HTTPException(
                status_code=400, detail=f"Must submit exactly {len(questions)} answers"
            )

        # Calculate results
        correct_answers = [q.correct_answer for q in questions]
        score = sum(
            1
            for user, correct in zip(submission.answers, correct_answers)
            if user == correct
        )

        # Generate feedback
        feedback = _generate_feedback(questions, submission.answers, correct_answers)

        # Create result
        result = QuizResult(
            quiz_id=submission.quiz_id,
            topic=quiz.topic,
            user_answers=submission.answers,
            correct_answers=correct_answers,
            score=score,
            total_questions=len(questions),
            percentage=(score / len(questions)) * 100,
            submitted_at=datetime.now().isoformat(),
            feedback=feedback,
        )

        # Save submission to database
        await _save_submission_to_database(db, submission, result)

        # Store in memory for backward compatibility
        quiz_results.append(result)

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quiz submission error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Submission processing failed", "details": str(e)},
        )


@router.get("/results")
async def get_quiz_results():
    """Get all quiz results"""
    return {"results": quiz_results, "total": len(quiz_results)}


@router.get("/history", response_model=List[QuizHistory])
async def get_quiz_history(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_db)
):
    """Get quiz history from database with statistics"""
    try:
        quizzes = await quiz_db_service.get_all(db, skip=skip, limit=limit)
        history_items = []

        for quiz in quizzes:
            # Get statistics for each quiz
            question_count = await _get_question_count(db, quiz.id)
            submission_count, average_score = await _get_submission_stats(db, quiz.id)

            history_item = QuizHistory(
                id=quiz.id,
                topic=quiz.topic,
                model=quiz.model,
                temperature=quiz.temperature,
                created_at=quiz.created_at,
                question_count=question_count,
                submission_count=submission_count,
                average_score=average_score,
                wikipediaEnhanced=quiz.wikipedia_enhanced,
            )
            history_items.append(history_item)

        # Sort by creation date (newest first)
        history_items.sort(key=lambda x: x.created_at, reverse=True)
        return history_items

    except Exception as e:
        logger.error(f"Error fetching quiz history: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to fetch quiz history", "details": str(e)},
        )


@router.get("/history/{quiz_id}")
async def get_quiz_details(quiz_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get detailed information about a specific quiz"""
    try:
        quiz = await quiz_db_service.get_with_questions(db, quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        submissions = await submission_db_service.get_by_quiz(db, quiz_id)

        return {
            "id": quiz.id,
            "topic": quiz.topic,
            "model": quiz.model,
            "temperature": quiz.temperature,
            "created_at": quiz.created_at,
            "questions": [
                {
                    "id": q.id,
                    "question": q.question,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                    "question_order": q.question_order,
                }
                for q in quiz.questions
            ],
            "submissions": [
                {
                    "id": s.id,
                    "user_id": s.user_id,
                    "score": s.score,
                    "total_questions": s.total_questions,
                    "percentage": s.percentage,
                    "submitted_at": s.submitted_at,
                }
                for s in submissions
            ],
            "total_submissions": len(submissions),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quiz details: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to fetch quiz details", "details": str(e)},
        )


# Helper functions
async def _save_quiz_to_database(
    db: AsyncSession, request: QuizRequest, result: QuizResponse
) -> str:
    """Save quiz and questions to database, return quiz ID"""
    try:
        # Save quiz
        quiz_data = {
            "topic": result.topic,
            "model": request.model or "llama-3.1-8b-instant",
            "temperature": request.temperature or 0.2,
            "wikipedia_enhanced": request.wikipediaEnhanced or False,
        }
        saved_quiz = await quiz_db_service.create(db, quiz_data)

        # Save questions
        for i, question in enumerate(result.questions):
            question_data = {
                "quiz_id": saved_quiz.id,
                "question": question.question,
                "options": question.options,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
                "question_order": i,
            }
            await question_db_service.create(db, question_data)

        return saved_quiz.id

    except Exception as e:
        logger.error(f"Failed to save quiz to database: {e}")
        # Return fallback ID
        return str(uuid4())


async def _get_quiz_and_questions(db: AsyncSession, quiz_id: str):
    """Get quiz and questions from database or memory"""
    # Try database first
    quiz = await quiz_db_service.get(db, quiz_id)
    questions = None

    if quiz:
        questions = await question_db_service.get_by_quiz(db, quiz_id)

    # Fallback to memory
    if not quiz or not questions:
        if current_quiz and current_quiz.quiz_id == quiz_id:
            quiz = type(
                "Quiz", (), {"id": current_quiz.quiz_id, "topic": current_quiz.topic}
            )()
            questions = current_quiz.questions
        else:
            raise HTTPException(
                status_code=400, detail="Quiz not found. Please generate a quiz first."
            )

    return quiz, questions


def _generate_feedback(questions, user_answers, correct_answers) -> List[str]:
    """Generate feedback for quiz submission"""
    feedback = []
    for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers)):
        question = questions[i]
        explanation = getattr(question, "explanation", "No explanation available.")

        if user_ans == correct_ans:
            feedback.append(f"Question {i+1}: Correct! {explanation}")
        else:
            correct_option = chr(65 + correct_ans)  # Convert 0-3 to A-D
            feedback.append(
                f"Question {i+1}: Incorrect. The correct answer was option {correct_option}. {explanation}"
            )
    return feedback


async def _save_submission_to_database(
    db: AsyncSession, submission: QuizSubmission, result: QuizResult
):
    """Save quiz submission to database"""
    try:
        submission_data = {
            "quiz_id": submission.quiz_id,
            "user_id": "anonymous",
            "score": result.score,
            "total_questions": result.total_questions,
            "percentage": result.percentage,
        }
        await submission_db_service.create(db, submission_data)
    except Exception as e:
        logger.error(f"Failed to save submission to database: {e}")


async def _get_question_count(db: AsyncSession, quiz_id: str) -> int:
    """Get question count for a quiz"""
    result = await db.execute(
        select(func.count(QuizQuestion.id)).where(QuizQuestion.quiz_id == quiz_id)
    )
    return result.scalar() or 0


async def _get_submission_stats(db: AsyncSession, quiz_id: str) -> tuple[int, float]:
    """Get submission statistics for a quiz"""
    result = await db.execute(
        select(
            func.count(DBQuizSubmission.id),
            func.avg(DBQuizSubmission.percentage),
        ).where(DBQuizSubmission.quiz_id == quiz_id)
    )
    stats = result.first()
    submission_count = stats[0] or 0
    average_score = float(stats[1]) if stats[1] else None
    return submission_count, average_score
