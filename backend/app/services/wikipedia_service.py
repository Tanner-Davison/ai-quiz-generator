"""Wikipedia service for fetching and processing Wikipedia data."""

import logging
from typing import List, Optional, Dict, Any
import httpx
import re

logger = logging.getLogger(__name__)


class WikipediaSearchResult:
    def __init__(self, title: str, snippet: str, pageid: int, url: str):
        self.title = title
        self.snippet = snippet
        self.pageid = pageid
        self.url = url


class WikipediaArticle:
    def __init__(self, title: str, extract: str, url: str, pageid: int, 
                 lastrevid: int, sections: Optional[List[str]] = None):
        self.title = title
        self.extract = extract
        self.url = url
        self.pageid = pageid
        self.lastrevid = lastrevid
        self.sections = sections or []


class FactCheckResult:
    def __init__(self, query: str, found: bool, article: Optional[WikipediaArticle] = None,
                 search_results: Optional[List[WikipediaSearchResult]] = None,
                 confidence: str = 'low', relevance_score: float = 0.0):
        self.query = query
        self.found = found
        self.article = article
        self.search_results = search_results or []
        self.confidence = confidence
        self.relevance_score = relevance_score


class WikipediaService:
    """Service for interacting with Wikipedia API."""
    
    def __init__(self):
        self.base_url = 'https://en.wikipedia.org/api/rest_v1'
        self.search_url = 'https://en.wikipedia.org/w/api.php'
        self.timeout = 10.0

    async def search_articles(self, query: str, limit: int = 5) -> List[WikipediaSearchResult]:
        """Search for Wikipedia articles."""
        try:
            search_query = self._clean_query(query)
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': search_query,
                'srlimit': str(limit),
                'srprop': 'snippet|size',
                'origin': '*'
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.search_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if not data.get('query') or not data['query'].get('search'):
                    return []

                results = []
                for result in data['query']['search']:
                    search_result = WikipediaSearchResult(
                        title=result['title'],
                        snippet=self._clean_snippet(result['snippet']),
                        pageid=result['pageid'],
                        url=f"https://en.wikipedia.org/wiki/{self._encode_title(result['title'])}"
                    )
                    results.append(search_result)

                return results

        except Exception as e:
            logger.error(f"Wikipedia search error: {e}")
            return []

    async def get_article(self, title: str) -> Optional[WikipediaArticle]:
        """Get a Wikipedia article by title."""
        try:
            clean_title = title.replace(' ', '_')
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/page/summary/{self._encode_title(clean_title)}")
                
                if response.status_code != 200:
                    return None

                data = response.json()
                
                # Handle different possible field names for revision ID
                lastrevid = data.get('rev') or data.get('revision') or data.get('lastrevid') or 0
                
                article = WikipediaArticle(
                    title=data['title'],
                    extract=data.get('extract', ''),
                    url=data.get('content_urls', {}).get('desktop', {}).get('page', 
                        f"https://en.wikipedia.org/wiki/{clean_title}"),
                    pageid=data['pageid'],
                    lastrevid=lastrevid,
                    sections=[s['title'] for s in data.get('sections', [])]
                )
                
                return article

        except Exception as e:
            logger.error(f"Wikipedia article fetch error: {e}")
            return None

    async def fact_check(self, content: str, topic: Optional[str] = None) -> FactCheckResult:
        """Perform fact-checking using Wikipedia data."""
        try:
            key_terms = self._extract_key_terms(content, topic)
            
            if not key_terms:
                return FactCheckResult(
                    query=content,
                    found=False,
                    confidence='low',
                    relevance_score=0.0
                )

            primary_term = key_terms[0]
            search_results = await self.search_articles(primary_term, 3)
            
            if not search_results:
                return FactCheckResult(
                    query=content,
                    found=False,
                    confidence='low',
                    relevance_score=0.0
                )

            best_match = search_results[0]
            article = await self.get_article(best_match.title)
            
            if not article:
                return FactCheckResult(
                    query=content,
                    found=False,
                    search_results=search_results,
                    confidence='low',
                    relevance_score=0.3
                )

            relevance_score = self._calculate_relevance_score(content, article, key_terms)
            
            confidence = 'low'
            if relevance_score > 0.7:
                confidence = 'high'
            elif relevance_score > 0.4:
                confidence = 'medium'

            return FactCheckResult(
                query=content,
                found=True,
                article=article,
                search_results=search_results,
                confidence=confidence,
                relevance_score=relevance_score
            )

        except Exception as e:
            logger.error(f"Fact-checking error: {e}")
            return FactCheckResult(
                query=content,
                found=False,
                confidence='low',
                relevance_score=0.0
            )

    def _extract_key_terms(self, content: str, topic: Optional[str] = None) -> List[str]:
        """Extract key terms from content for searching."""
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }

        full_text = f"{topic} {content}" if topic else content
        
        words = re.sub(r'[^\w\s]', ' ', full_text.lower()).split()
        words = [word for word in words if len(word) >= 2 and word not in stop_words]

        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1

        return [word for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:3]]

    def _calculate_relevance_score(self, content: str, article: WikipediaArticle, key_terms: List[str]) -> float:
        """Calculate relevance score between content and article."""
        content_lower = content.lower()
        article_text = f"{article.title} {article.extract}".lower()
        
        score = 0.0
        matches = 0

        for term in key_terms:
            if term.lower() in article_text:
                score += 0.3
                matches += 1

        if any(term.lower() in article.title.lower() for term in key_terms):
            score += 0.4

        content_words = [word for word in content_lower.split() if len(word) > 3]
        article_words = [word for word in article_text.split() if len(word) > 3]
        
        common_words = [word for word in content_words if word in article_words]
        overlap_ratio = len(common_words) / max(len(content_words), 1)
        score += overlap_ratio * 0.3

        return min(score, 1.0)

    def _clean_query(self, query: str) -> str:
        """Clean search query."""
        return re.sub(r'[^\w\s]', ' ', query).strip()[:100]

    def _clean_snippet(self, snippet: str) -> str:
        """Clean HTML from snippet."""
        # Remove HTML tags
        snippet = re.sub(r'<[^>]*>', '', snippet)
        # Decode HTML entities
        snippet = snippet.replace('&quot;', '"').replace('&amp;', '&')
        snippet = snippet.replace('&lt;', '<').replace('&gt;', '>')
        # Clean whitespace
        snippet = re.sub(r'\s+', ' ', snippet).strip()
        return snippet

    def _encode_title(self, title: str) -> str:
        """Encode title for URL."""
        import urllib.parse
        return urllib.parse.quote(title.replace(' ', '_'))


# Global instance
wikipedia_service = WikipediaService()
