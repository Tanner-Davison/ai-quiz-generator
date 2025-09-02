
import json
import re
import logging
from datetime import datetime
from typing import Dict, Any
from .ai_service import ai_service
from ..models.quiz import QuizRequest, QuizResponse, QuizQuestion

logger = logging.getLogger(__name__)

def extract_json_from_response(response_text):
    """Simple JSON extraction - find first { and last }"""
    # Find the first { and last }
    start = response_text.find('{')
    end = response_text.rfind('}') + 1
    
    if start != -1 and end != 0:
        json_str = response_text[start:end]
        return json.loads(json_str)
    else:
        raise ValueError("No JSON object found in response")

class QuizService:
    def __init__(self):
        self.ai_service = ai_service
        self.inappropriate_topics = {
            "vagina", "nipple", "sphincter", "feces", "penis", "breast", 
            "sexual", "porn", "nude", "explicit", "nsfw", "adult"
        }
    
    def is_topic_appropriate(self, topic: str) -> bool:
        """Check if a topic is appropriate for quiz generation"""
        topic_lower = topic.lower()
        return not any(inappropriate in topic_lower for inappropriate in self.inappropriate_topics)
    
    def generate_quiz_prompt(self, topic: str) -> str:
        """Generate a basic prompt for quiz creation"""
        return f"""Create a multiple-choice quiz about "{topic}" with exactly 5 questions.

Each question should have 4 options (A, B, C, D) with only one correct answer.
Include an explanation for the correct answer.

Respond with ONLY this JSON format:
{{
    "questions": [
        {{
            "question": "Question text?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": 0,
            "explanation": "Why this answer is correct"
        }}
    ]
}}

The correct_answer should be the index (0-3) of the correct option."""
    
    async def generate_enhanced_quiz(self, request: QuizRequest) -> QuizResponse:
        """Generate an enhanced quiz using Wikipedia data while preserving original topic"""
        try:
            if not request.topic:
                raise ValueError("Topic is required")
            
            # Check if topic is appropriate
            if not self.is_topic_appropriate(request.topic):
                raise ValueError("This topic is not appropriate for quiz generation. Please choose a different topic.")

            print(f"DEBUG: Starting enhanced quiz generation for topic: {request.topic}")
            logger.info(f"Generating enhanced quiz for topic: {request.topic}")
            
            # Use the enhanced prompt for generation, but keep original topic for response
            prompt = request.enhancedPrompt or self.generate_quiz_prompt(request.topic)
            print(f"DEBUG: Using enhanced prompt length: {len(prompt)}")

            completion = await self.ai_service.generate_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a JSON generator. You must respond with ONLY valid, complete JSON. Never include explanatory text, markdown formatting, or any content outside the JSON object. Ensure all JSON syntax is correct with proper quotes, commas, and brackets.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=request.model,
                temperature=request.temperature or 0.1,
                max_tokens=1500,
            )

            response_text = completion.choices[0].message.content
            print(f"DEBUG: Raw AI response length: {len(response_text)}")
            print(f"DEBUG: Raw AI response: {response_text}")
            
            # Extract JSON from response
            quiz_data = extract_json_from_response(response_text)
            print(f"DEBUG: Extracted quiz data keys: {list(quiz_data.keys())}")
            print(f"DEBUG: Extracted quiz data: {quiz_data}")
            
            # Validate and create quiz response
            if "questions" not in quiz_data:
                raise ValueError("Invalid quiz format: missing questions")
            
            questions = []
            for i, q_data in enumerate(quiz_data["questions"]):
                if not all(key in q_data for key in ["question", "options", "correct_answer", "explanation"]):
                    raise ValueError(f"Invalid question format at index {i}")
                
                question = QuizQuestion(
                    question=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"]
                )
                questions.append(question)
            
            # Create response with original topic (not the enhanced prompt)
            response = QuizResponse(
                topic=request.topic,  # Use original topic, not enhanced prompt
                questions=questions,
                generated_at=datetime.now().isoformat()
            )
            
            print(f"DEBUG: Successfully generated enhanced quiz with {len(questions)} questions")
            return response
            
        except Exception as e:
            logger.error(f"Enhanced quiz generation error: {str(e)}")
            raise ValueError(f"Failed to generate enhanced quiz: {str(e)}")

    async def generate_quiz(self, request: QuizRequest) -> QuizResponse:
        """Generate a quiz based on the given topic"""
        try:
            if not request.topic:
                raise ValueError("Topic is required")
            
            # Check if topic is appropriate
            if not self.is_topic_appropriate(request.topic):
                raise ValueError("This topic is not appropriate for quiz generation. Please choose a different topic.")

            print(f"DEBUG: Starting quiz generation for topic: {request.topic}")
            logger.info(f"Generating quiz for topic: {request.topic}")
            
            # Generate quiz prompt
            prompt = self.generate_quiz_prompt(request.topic)
            print(f"DEBUG: Generated prompt length: {len(prompt)}")

            completion = await self.ai_service.generate_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a JSON generator. You must respond with ONLY valid, complete JSON. Never include explanatory text, markdown formatting, or any content outside the JSON object. Ensure all JSON syntax is correct with proper quotes, commas, and brackets.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=request.model,
                temperature=request.temperature or 0.1,
                max_tokens=1500,
            )

            print(f"DEBUG: Got completion response")
            if not completion.choices or not completion.choices[0].message:
                print("DEBUG: No completion choices or message")
                raise ValueError("No response generated")

            response_content = completion.choices[0].message.content
            print(f"DEBUG: Response content length: {len(response_content)}")
            print(f"DEBUG: Response starts with: {response_content[:100]}...")
            
            # Use the simple JSON extraction
            try:
                print("DEBUG: Attempting JSON extraction...")
                quiz_data = extract_json_from_response(response_content)
                print("DEBUG: JSON extraction successful!")
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON parsing error: {e}")
                logger.error(f"JSON parsing error: {e}")
                raise ValueError("Failed to parse quiz response. Please try again.")
            
            print(f"DEBUG: Quiz data keys: {list(quiz_data.keys())}")
            print(f"DEBUG: Number of questions: {len(quiz_data.get('questions', []))}")
            
            # Basic validation
            if "questions" not in quiz_data or not isinstance(quiz_data["questions"], list):
                print("DEBUG: Validation failed - missing questions field")
                raise ValueError("Invalid quiz structure: missing 'questions' field")
            
            # Create quiz response
            quiz_response = QuizResponse(
                topic=request.topic,
                questions=[
                    QuizQuestion(
                        question=q["question"],
                        options=q["options"],
                        correct_answer=q["correct_answer"],
                        explanation=q["explanation"]
                    ) for q in quiz_data["questions"]
                ],
                generated_at=datetime.now().isoformat()
            )
            
            print("DEBUG: Created quiz response object")
            
            # Log the successful JSON output to terminal
            logger.info("=" * 50)
            logger.info("SUCCESSFULLY GENERATED QUIZ")
            logger.info("=" * 50)
            logger.info(f"Topic: {request.topic}")
            logger.info(f"Number of questions: {len(quiz_data['questions'])}")
            logger.info("Quiz JSON output:")
            logger.info(json.dumps(quiz_data, indent=2))
            logger.info("=" * 50)
            
            # Also print to console for immediate visibility
            print("\n" + "=" * 50)
            print("SUCCESSFULLY GENERATED QUIZ")
            print("=" * 50)
            print(f"Topic: {request.topic}")
            print(f"Number of questions: {len(quiz_data['questions'])}")
            print("Quiz JSON output:")
            print(json.dumps(quiz_data, indent=2))
            print("=" * 50 + "\n")

            logger.info(f"Successfully generated quiz with {len(quiz_data['questions'])} questions")
            return quiz_response

        except Exception as e:
            print(f"DEBUG: Exception occurred: {str(e)}")
            logger.error(f"Quiz generation error: {str(e)}")
            raise

# Global instance
quiz_service = QuizService()