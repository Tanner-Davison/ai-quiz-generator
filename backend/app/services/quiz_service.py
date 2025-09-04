"""Quiz service for generating AI-powered quizzes."""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from app.models.quiz import QuizQuestion, QuizRequest, QuizResponse, WikipediaContext
from app.services.ai_service import ai_service
from app.services.wikipedia_service import wikipedia_service

logger = logging.getLogger(__name__)


def extract_json_from_response(response_text):
    """Simple JSON extraction - find first { and last }"""
    # Find the first { and last }
    start = response_text.find("{")
    end = response_text.rfind("}") + 1

    if start != -1 and end != 0:
        json_str = response_text[start:end]
        return json.loads(json_str)
    else:
        raise ValueError("No JSON object found in response")


class QuizService:
    """Service for managing quiz generation and operations."""

    def __init__(self):
        self.ai_service = ai_service
        self.inappropriate_topics = {
            "vagina",
            "nipple",
            "boobs",
            "penis",
            "breast",
            "sexual",
            "porn",
            "nude",
            "explicit",
            "nsfw",
            "adult",
        }

    def is_topic_appropriate(self, topic: str) -> bool:
        """Check if a topic is appropriate for quiz generation"""
        topic_lower = topic.lower()
        return not any(
            inappropriate in topic_lower for inappropriate in self.inappropriate_topics
        )

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
                raise ValueError(
                    "This topic is not appropriate for quiz generation. "
                    "Please choose a different topic."
                )

            print(
                "DEBUG: Starting enhanced quiz generation for topic: %s", request.topic
            )
            logger.info("Generating enhanced quiz for topic: %s", request.topic)

            # Gather Wikipedia data for enhanced quiz
            wikipedia_context = await self._gather_wikipedia_context(request.topic)
            
            # Create enhanced prompt with Wikipedia data
            prompt = self._create_enhanced_prompt(request.topic, wikipedia_context)
            print("DEBUG: Using enhanced prompt length: %d", len(prompt))

            completion = await self.ai_service.generate_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a JSON generator. You must respond with ONLY "
                        "valid, complete JSON. Never include explanatory text, "
                        "markdown formatting, or any content outside the JSON object. "
                        "Ensure all JSON syntax is correct with proper quotes, "
                        "commas, and brackets.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=request.model or "default-model",
                temperature=request.temperature or 0.1,
                max_tokens=1500,
            )

            response_text = completion.choices[0].message.content
            print("DEBUG: Raw AI response length: %d", len(response_text))
            print("DEBUG: Raw AI response: %s", response_text)

            # Extract JSON from response
            quiz_data = extract_json_from_response(response_text)
            print("DEBUG: Extracted quiz data keys: %s", list(quiz_data.keys()))
            print("DEBUG: Extracted quiz data: %s", quiz_data)

            # Validate and create quiz response
            if "questions" not in quiz_data:
                raise ValueError("Invalid quiz format: missing questions")

            questions = []
            for i, q_data in enumerate(quiz_data["questions"]):
                if not all(
                    key in q_data
                    for key in ["question", "options", "correct_answer", "explanation"]
                ):
                    raise ValueError(f"Invalid question format at index {i}")

                question = QuizQuestion(
                    question=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    explanation=q_data["explanation"],
                )
                questions.append(question)

            # Create Wikipedia context object
            wikipedia_context_obj = WikipediaContext(
                articles=wikipedia_context.get("articles", []),
                key_facts=wikipedia_context.get("key_facts", []),
                related_topics=wikipedia_context.get("related_topics", []),
                summary=wikipedia_context.get("summary", "")
            )
            
            # Create response with original topic and Wikipedia context
            response = QuizResponse(
                topic=request.topic,  # Use original topic, not enhanced prompt
                questions=questions,
                generated_at=datetime.now().isoformat(),
                wikipedia_context=wikipedia_context_obj,
                wikipedia_enhanced=True
            )

            print(
                "DEBUG: Successfully generated enhanced quiz with %d questions",
                len(questions),
            )
            return response

        except Exception as exc:
            logger.error("Enhanced quiz generation error: %s", str(exc))
            raise ValueError(f"Failed to generate enhanced quiz: {str(exc)}") from exc

    async def generate_quiz(self, request: QuizRequest) -> QuizResponse:
        """Generate a quiz based on the given topic"""
        try:
            if not request.topic:
                raise ValueError("Topic is required")

            # Check if topic is appropriate
            if not self.is_topic_appropriate(request.topic):
                raise ValueError(
                    "This topic is not appropriate for quiz generation. "
                    "Please choose a different topic."
                )

            print("DEBUG: Starting quiz generation for topic: %s", request.topic)
            logger.info("Generating quiz for topic: %s", request.topic)

            # Generate quiz prompt
            prompt = self.generate_quiz_prompt(request.topic)
            print("DEBUG: Generated prompt length: %d", len(prompt))

            completion = await self.ai_service.generate_chat_completion(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a JSON generator. You must respond with ONLY "
                        "valid, complete JSON. Never include explanatory text, "
                        "markdown formatting, or any content outside the JSON object. "
                        "Ensure all JSON syntax is correct with proper quotes, "
                        "commas, and brackets.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=request.model,
                temperature=request.temperature or 0.1,
                max_tokens=1500,
            )

            print("DEBUG: Got completion response")
            if not completion.choices or not completion.choices[0].message:
                print("DEBUG: No completion choices or message")
                raise ValueError("No response generated")

            response_content = completion.choices[0].message.content or ""
            print("DEBUG: Response content length: %d", len(response_content))
            print("DEBUG: Response starts with: %s...", response_content[:100])

            # Use the simple JSON extraction
            try:
                print("DEBUG: Attempting JSON extraction...")
                quiz_data = extract_json_from_response(response_content)
                print("DEBUG: JSON extraction successful!")
            except json.JSONDecodeError as exc:
                print("DEBUG: JSON parsing error: %s", exc)
                logger.error("JSON parsing error: %s", exc)
                raise ValueError(
                    "Failed to parse quiz response. Please try again."
                ) from exc

            print("DEBUG: Quiz data keys: %s", list(quiz_data.keys()))
            print("DEBUG: Number of questions: %d", len(quiz_data.get("questions", [])))

            # Basic validation
            if "questions" not in quiz_data or not isinstance(
                quiz_data["questions"], list
            ):
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
                        explanation=q["explanation"],
                    )
                    for q in quiz_data["questions"]
                ],
                generated_at=datetime.now().isoformat(),
            )

            print("DEBUG: Created quiz response object")

            # Log the successful JSON output to terminal
            logger.info("=" * 50)
            logger.info("SUCCESSFULLY GENERATED QUIZ")
            logger.info("=" * 50)
            logger.info("Topic: %s", request.topic)
            logger.info("Number of questions: %d", len(quiz_data["questions"]))
            logger.info("Quiz JSON output:")
            logger.info(json.dumps(quiz_data, indent=2))
            logger.info("=" * 50)

            # Also print to console for immediate visibility
            print("\n" + "=" * 50)
            print("SUCCESSFULLY GENERATED QUIZ")
            print("=" * 50)
            print("Topic: %s", request.topic)
            print("Number of questions: %d", len(quiz_data["questions"]))
            print("Quiz JSON output:")
            print(json.dumps(quiz_data, indent=2))
            print("=" * 50 + "\n")

            logger.info(
                "Successfully generated quiz with %d questions",
                len(quiz_data["questions"]),
            )
            return quiz_response

        except Exception as exc:
            print("DEBUG: Exception occurred: %s", str(exc))
            logger.error("Quiz generation error: %s", str(exc))
            raise

    async def _gather_wikipedia_context(self, topic: str) -> Dict[str, Any]:
        """Gather Wikipedia context for enhanced quiz generation"""
        try:
            # Search for articles
            search_results = await wikipedia_service.search_articles(topic, 3)
            
            if not search_results:
                return {"articles": [], "key_facts": [], "related_topics": [], "summary": ""}
            
            articles = []
            key_facts = []
            related_topics = []
            
            # Get articles and extract information
            for search_result in search_results[:2]:  # Limit to 2 articles
                article = await wikipedia_service.get_article(search_result.title)
                if article:
                    articles.append({
                        "title": article.title,
                        "extract": article.extract,
                        "url": article.url,
                        "pageid": article.pageid,
                        "lastrevid": article.lastrevid,
                        "sections": article.sections
                    })
                    
                    # Extract key facts
                    facts = self._extract_key_facts(article.extract)
                    key_facts.extend(facts)
                    
                    # Add sections as related topics
                    if article.sections:
                        related_topics.extend(article.sections[:5])
            
            # Create summary
            summary = self._create_summary(articles)
            
            return {
                "articles": articles,
                "key_facts": list(set(key_facts))[:10],  # Remove duplicates and limit
                "related_topics": list(set(related_topics))[:5],  # Remove duplicates and limit
                "summary": summary
            }
            
        except Exception as e:
            logger.error(f"Error gathering Wikipedia context: {e}")
            return {"articles": [], "key_facts": [], "related_topics": [], "summary": ""}

    def _create_enhanced_prompt(self, topic: str, context: Dict[str, Any]) -> str:
        """Create enhanced prompt with Wikipedia data"""
        prompt = f'Generate a comprehensive quiz about "{topic}". '
        
        if context.get("summary"):
            prompt += f'\n\nWikipedia Summary: {context["summary"]}'
        
        if context.get("key_facts"):
            prompt += f'\n\nKey Facts from Wikipedia:\n'
            for fact in context["key_facts"][:10]:
                prompt += f'- {fact}\n'
        
        if context.get("related_topics"):
            prompt += f'\n\nRelated Topics: {", ".join(context["related_topics"][:5])}'
        
        prompt += '\n\nPlease create 5 multiple choice questions that are:\n'
        prompt += '1. Factually accurate based on the Wikipedia information provided\n'
        prompt += '2. Cover different aspects of the topic\n'
        prompt += '3. Include one correct answer and three plausible but incorrect options\n'
        prompt += '4. Provide detailed explanations that reference the Wikipedia facts\n'
        prompt += '5. Vary in difficulty from basic to intermediate\n\n'
        
        prompt += 'Respond with ONLY this JSON format:\n'
        prompt += '{\n'
        prompt += '    "questions": [\n'
        prompt += '        {\n'
        prompt += '            "question": "Question text?",\n'
        prompt += '            "options": ["Option A", "Option B", "Option C", "Option D"],\n'
        prompt += '            "correct_answer": 0,\n'
        prompt += '            "explanation": "Why this answer is correct"\n'
        prompt += '        }\n'
        prompt += '    ]\n'
        prompt += '}\n\n'
        prompt += 'The correct_answer should be the index (0-3) of the correct option.'
        
        return prompt

    def _extract_key_facts(self, text: str) -> List[str]:
        """Extract key facts from Wikipedia text"""
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]
        
        key_indicators = [
            "is a", "are a", "is the", "are the", "was", "were", "has", "have",
            "can", "cannot", "includes", "consists of", "refers to", "means",
            "defined as", "known as"
        ]
        
        facts = []
        for sentence in sentences:
            lower_sentence = sentence.lower()
            if any(indicator in lower_sentence for indicator in key_indicators):
                facts.append(sentence)
                if len(facts) >= 8:  # Limit facts
                    break
        
        return facts

    def _create_summary(self, articles: List[Dict[str, Any]]) -> str:
        """Create summary from Wikipedia articles"""
        if not articles:
            return ""
        
        main_extract = articles[0].get("extract", "")
        
        if len(articles) > 1:
            additional_facts = []
            for article in articles[1:]:
                first_sentence = article.get("extract", "").split('.')[0]
                if len(first_sentence) > 20:
                    additional_facts.append(first_sentence)
                if len(additional_facts) >= 2:
                    break
            
            if additional_facts:
                return f"{main_extract} {' '.join(additional_facts)}."
        
        return main_extract


# Global instance
quiz_service = QuizService()
