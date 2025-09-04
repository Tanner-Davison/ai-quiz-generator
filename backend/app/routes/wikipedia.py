"""Wikipedia API routes"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.wikipedia_service import wikipedia_service

logger = logging.getLogger(__name__)
router = APIRouter()


class WikipediaSearchResponse(BaseModel):
    results: List[dict]
    total: int


class WikipediaArticleResponse(BaseModel):
    title: str
    extract: str
    url: str
    pageid: int
    lastrevid: int
    sections: List[str]


class FactCheckResponse(BaseModel):
    query: str
    found: bool
    article: Optional[dict] = None
    search_results: List[dict] = []
    confidence: str
    relevance_score: float


@router.get("/search", response_model=WikipediaSearchResponse)
async def search_wikipedia_articles(
    query: str = Query(..., description="Search query"),
    limit: int = Query(5, ge=1, le=20, description="Maximum number of results")
):
    """Search for Wikipedia articles."""
    try:
        results = await wikipedia_service.search_articles(query, limit)
        
        search_results = []
        for result in results:
            search_results.append({
                "title": result.title,
                "snippet": result.snippet,
                "pageid": result.pageid,
                "url": result.url
            })
        
        return WikipediaSearchResponse(
            results=search_results,
            total=len(search_results)
        )
    
    except Exception as e:
        logger.error(f"Wikipedia search error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Wikipedia search failed", "details": str(e)}
        )


@router.get("/article/{title}", response_model=WikipediaArticleResponse)
async def get_wikipedia_article(title: str):
    """Get a Wikipedia article by title."""
    try:
        article = await wikipedia_service.get_article(title)
        
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found"
            )
        
        return WikipediaArticleResponse(
            title=article.title,
            extract=article.extract,
            url=article.url,
            pageid=article.pageid,
            lastrevid=article.lastrevid,
            sections=article.sections
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Wikipedia article fetch error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to fetch article", "details": str(e)}
        )


@router.post("/fact-check", response_model=FactCheckResponse)
async def fact_check_content(
    content: str = Query(..., description="Content to fact-check"),
    topic: Optional[str] = Query(None, description="Optional topic context")
):
    """Perform fact-checking using Wikipedia data."""
    try:
        result = await wikipedia_service.fact_check(content, topic)
        
        article_dict = None
        if result.article:
            article_dict = {
                "title": result.article.title,
                "extract": result.article.extract,
                "url": result.article.url,
                "pageid": result.article.pageid,
                "lastrevid": result.article.lastrevid,
                "sections": result.article.sections
            }
        
        search_results = []
        for search_result in result.search_results:
            search_results.append({
                "title": search_result.title,
                "snippet": search_result.snippet,
                "pageid": search_result.pageid,
                "url": search_result.url
            })
        
        return FactCheckResponse(
            query=result.query,
            found=result.found,
            article=article_dict,
            search_results=search_results,
            confidence=result.confidence,
            relevance_score=result.relevance_score
        )
    
    except Exception as e:
        logger.error(f"Fact-checking error: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Fact-checking failed", "details": str(e)}
        )


@router.get("/articles", response_model=List[dict])
async def get_wikipedia_articles(
    topic: str = Query(..., description="Topic to search for"),
    limit: int = Query(3, ge=1, le=10, description="Maximum number of articles")
):
    """Get Wikipedia articles for a topic (convenience endpoint for frontend)."""
    try:
        search_results = await wikipedia_service.search_articles(topic, limit)
        articles = []
        
        for result in search_results:
            article = await wikipedia_service.get_article(result.title)
            if article:
                articles.append({
                    "title": article.title,
                    "extract": article.extract,
                    "url": article.url,
                    "pageid": article.pageid,
                    "lastrevid": article.lastrevid,
                    "sections": article.sections
                })
        
        return articles
    
    except Exception as e:
        logger.error(f"Error getting Wikipedia articles: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to get articles", "details": str(e)}
        )
