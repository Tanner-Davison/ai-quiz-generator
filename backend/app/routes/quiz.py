import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_async_db
from ..models.database_models import Quiz, QuizQuestion
from ..models.database_models import QuizSubmission as DBQuizSubmission
from ..models.quiz import (
    QuizHistory,
    QuizRequest,
    QuizResponse,
    QuizResult,
    QuizSubmission,
)
from ..services.database_service import (
    QuizQuestionService,
    QuizDatabaseService,
    QuizSubmissionService,
)
from ..services.quiz_service import quiz_service

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize database services with proper models
quiz_db_service = QuizDatabaseService(Quiz)
question_db_service = QuizQuestionService(QuizQuestion)
submission_db_service = QuizSubmissionService(DBQuizSubmission)

# In-memory storage for quiz results (in production, use a database)
quiz_results = []
# Store the most recently generated quiz
current_quiz = None


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizRequest,
    force_model: str = None,
    db: AsyncSession = Depends(get_async_db),
):
    """Generate a quiz based on the given topic"""
    global current_quiz  # Add this line

    print("=" * 60)
    print("ROUTE CALLED: /quiz/generate")
    print(f"Request topic: {request.topic}")
    print(f"Request model: {request.model}")
    print(f"Request wikipediaEnhanced: {request.wikipediaEnhanced}")
    print(f"Request wikipediaEnhanced type: {type(request.wikipediaEnhanced)}")
    print(f"Request enhancedPrompt: {request.enhancedPrompt is not None}")
    print(
        f"Request enhancedPrompt length: {len(request.enhancedPrompt) if request.enhancedPrompt else 0}"
    )
    print("=" * 60)

    try:
        # Allow overriding the model via query parameter for testing
        if force_model:
            logger.info(f"Overriding model to: {force_model}")
            request.model = force_model

        print("About to call quiz_service.generate_quiz()")
        # Use enhanced prompt if available, otherwise use regular topic
        if request.enhancedPrompt and request.wikipediaEnhanced is True:
            print("Using enhanced prompt with Wikipedia data")
            # Pass the enhanced prompt to the quiz service but keep original topic
            result = await quiz_service.generate_enhanced_quiz(request)
        else:
            print("Using regular topic")
            result = await quiz_service.generate_quiz(request)
        print("quiz_service.generate_quiz() completed successfully")

        print("🔍 DEBUG: About to start database save process...")

        try:
            print("🔄 Attempting to save quiz to database...")

            # Save the quiz
            quiz_data = {
                "topic": result.topic,
                "model": request.model or "llama-3.1-8b-instant",
                "temperature": request.temperature or 0.2,
                "wikipedia_enhanced": request.wikipediaEnhanced or False,
            }
            print(f"📝 Quiz data to save: {quiz_data}")
            print(f"🔍 DEBUG: request.wikipediaEnhanced = {request.wikipediaEnhanced}")
            print(
                f"🔍 DEBUG: request.wikipediaEnhanced or False = {request.wikipediaEnhanced or False}"
            )

            saved_quiz = await quiz_db_service.create(db, quiz_data)
            print(f"✅ Quiz saved to database with ID: {saved_quiz.id}")

            # Save each question
            for i, question in enumerate(result.questions):
                question_data = {
                    "quiz_id": saved_quiz.id,
                    "question": question.question,
                    "options": question.options,
                    "correct_answer": question.correct_answer,
                    "explanation": question.explanation,
                    "question_order": i,
                }
                print(f"📝 Question {i+1} data to save: {question_data}")

                saved_question = await question_db_service.create(db, question_data)
                print(f"✅ Question {i+1} saved with ID: {saved_question.id}")

            # Update the result with the database ID
            result.quiz_id = saved_quiz.id
            print(f"🔄 Quiz saved with database ID: {saved_quiz.id}")

        except Exception as db_error:
            logger.error(f"Failed to save quiz to database: {db_error}")
            print(f"❌ Database save failed with error: {db_error}")
            print(f"❌ Error type: {type(db_error)}")
            import traceback

            print(f"❌ Full traceback: {traceback.format_exc()}")
            # Continue without database save for now
            saved_quiz = None

        # current quiz for submission
        current_quiz = result

        # Add the quiz ID to the result (use saved quiz ID or generate a fallback)
        if saved_quiz:
            result.quiz_id = saved_quiz.id
        else:
            # Generate a fallback ID for in-memory storage
            import uuid

            result.quiz_id = str(uuid.uuid4())
            print(f"🔄 Using fallback quiz ID: {result.quiz_id}")

        print("🔍 DEBUG: About to return result...")
        return result
    except ValueError as e:
        print(f"ValueError caught: {str(e)}")
        logger.error(f"Quiz generation validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid quiz request",
                "details": str(e),
            },
        )
    except Exception as e:
        print(f"Exception caught: {str(e)}")
        logger.error(f"Quiz generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while processing the quiz submission",
                "details": str(e),
            },
        )


@router.post("/submit", response_model=QuizResult)
async def submit_quiz(
    submission: QuizSubmission, db: AsyncSession = Depends(get_async_db)
):
    """Submit quiz answers and get results"""

    try:
        # Try to retrieve quiz from database first
        quiz = await quiz_db_service.get(db, submission.quiz_id)
        questions = None

        if quiz:
            # Get questions for this quiz from database
            questions = await question_db_service.get_by_quiz(db, submission.quiz_id)

        # If not found in database, try to use the current quiz (fallback for in-memory storage)
        if not quiz or not questions:
            if current_quiz and current_quiz.quiz_id == submission.quiz_id:
                quiz = type(
                    "Quiz",
                    (),
                    {"id": current_quiz.quiz_id, "topic": current_quiz.topic},
                )()
                questions = current_quiz.questions
                print(
                    f"🔄 Using current quiz from memory for submission: {submission.quiz_id}"
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Quiz not found. Please generate a quiz first.",
                )

        if len(submission.answers) != len(questions):
            raise HTTPException(
                status_code=400, detail=f"Must submit exactly {len(questions)} answers"
            )

        # Get correct answers
        if hasattr(questions[0], "correct_answer"):
            # Database questions
            correct_answers = [q.correct_answer for q in questions]
        else:
            # In-memory questions (QuizQuestion objects)
            correct_answers = [q.correct_answer for q in questions]

        # Calculate score
        score = sum(
            1
            for user_ans, correct_ans in zip(submission.answers, correct_answers)
            if user_ans == correct_ans
        )

        # Generate feedback based on actual quiz questions
        feedback = []
        for i, (user_ans, correct_ans) in enumerate(
            zip(submission.answers, correct_answers)
        ):
            question = questions[i]
            # Handle both database and in-memory question objects
            explanation = getattr(question, "explanation", "No explanation available.")

            if user_ans == correct_ans:
                feedback.append(f"Question {i+1}: Correct! {explanation}")
            else:
                correct_option = chr(65 + correct_ans)  # Convert 0-3 to A-D
                feedback.append(
                    f"Question {i+1}: Incorrect. The correct answer was option {correct_option}. {explanation}"
                )

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
        try:
            submission_data = {
                "quiz_id": submission.quiz_id,
                "user_id": "anonymous",  # For now, use anonymous user
                "score": score,
                "total_questions": len(questions),
                "percentage": (score / len(questions)) * 100,
            }
            print(f"💾 Saving quiz submission to database: {submission_data}")
            saved_submission = await submission_db_service.create(db, submission_data)
            print(f"✅ Quiz submission saved with ID: {saved_submission.id}")
        except Exception as db_error:
            print(f"❌ Failed to save submission to database: {db_error}")
            # Continue without database save for now

        # Store result in memory (for backward compatibility)
        quiz_results.append(result)

        return result

    except Exception as e:
        logger.error(f"Quiz submission error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while processing the quiz submission",
                "details": str(e),
            },
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
        # Get all quizzes with pagination
        quizzes = await quiz_db_service.get_all(db, skip=skip, limit=limit)

        history_items = []

        for quiz in quizzes:
            # Get question count for this quiz
            question_count_result = await db.execute(
                select(func.count(QuizQuestion.id)).where(
                    QuizQuestion.quiz_id == quiz.id
                )
            )
            question_count = question_count_result.scalar() or 0

            # Get submission count and average score for this quiz
            submission_stats_result = await db.execute(
                select(
                    func.count(DBQuizSubmission.id),
                    func.avg(DBQuizSubmission.percentage),
                ).where(DBQuizSubmission.quiz_id == quiz.id)
            )
            submission_stats = submission_stats_result.first()
            submission_count = submission_stats[0] or 0
            average_score = float(submission_stats[1]) if submission_stats[1] else None

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
        logger.error(f"Error fetching quiz history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while fetching quiz history",
                "details": str(e),
            },
        )


@router.get("/history/{quiz_id}")
async def get_quiz_details(quiz_id: str, db: AsyncSession = Depends(get_async_db)):
    """Get detailed information about a specific quiz including questions and submissions"""
    try:
        # Get the quiz with questions
        quiz = await quiz_db_service.get_with_questions(db, quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        # Get submissions for this quiz
        submissions = await submission_db_service.get_by_quiz(db, quiz_id)

        # Format the response
        quiz_details = {
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

        return quiz_details

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching quiz details: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "An error occurred while fetching quiz details",
                "details": str(e),
            },
        )
