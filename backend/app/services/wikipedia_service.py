import wikipedia
import logging

logger = logging.getLogger(__name__)

class WikipediaService:
    @staticmethod
    def get_context(topic: str) -> str:
        """Get relevant context from Wikipedia to improve factual accuracy"""
        try:
            # Search for the topic
            search_results = wikipedia.search(topic, results=3)
            if not search_results:
                return ""

            # Get summary of the first result
            page = wikipedia.page(search_results[0], auto_suggest=False)
            summary = page.summary[:1000]  # Limit to first 1000 characters

            return f"Context about {topic}: {summary}"
        except Exception as e:
            logger.error(f"Wikipedia context error: {e}")
            return ""

# Global instance
wikipedia_service = WikipediaService()
