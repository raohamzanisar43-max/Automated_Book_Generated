import httpx
from typing import List, Dict, Any, Optional
from app.config import settings
from app.schemas import WebSearchResult
import logging
from bs4 import BeautifulSoup
import asyncio

logger = logging.getLogger(__name__)

class ResearchService:
    def __init__(self):
        self.serpapi_key = settings.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"

    async def search_web(self, query: str, num_results: int = 5) -> List[WebSearchResult]:
        """Perform web search using SerpAPI"""
        if not self.serpapi_key:
            logger.warning("SerpAPI key not configured, skipping web search")
            return []
        
        try:
            params = {
                "api_key": self.serpapi_key,
                "engine": "google",
                "q": query,
                "num": num_results,
                "safe": "active"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                results = []
                if "organic_results" in data:
                    for result in data["organic_results"][:num_results]:
                        web_result = WebSearchResult(
                            title=result.get("title", ""),
                            snippet=result.get("snippet", ""),
                            url=result.get("link", ""),
                            published_date=result.get("date", None)
                        )
                        results.append(web_result)
                
                return results
                
        except Exception as e:
            logger.error(f"Error performing web search: {str(e)}")
            return []

    async def scrape_content(self, url: str) -> Optional[str]:
        """Scrape content from a URL"""
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extract text from common content tags
                content_tags = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
                content = ' '.join([tag.get_text().strip() for tag in content_tags])
                
                # Clean up whitespace
                content = ' '.join(content.split())
                
                return content[:2000]  # Limit to 2000 characters
                
        except Exception as e:
            logger.error(f"Error scraping content from {url}: {str(e)}")
            return None

    async def get_research_context(self, query: str, max_content_length: int = 1000) -> str:
        """Get research context for a given query"""
        try:
            # Perform web search
            search_results = await self.search_web(query)
            
            if not search_results:
                return ""
            
            # Scrape content from top results
            scraping_tasks = [self.scrape_content(result.url) for result in search_results[:3]]
            scraped_contents = await asyncio.gather(*scraping_tasks, return_exceptions=True)
            
            # Build context
            context_parts = []
            for i, content in enumerate(scraped_contents):
                if isinstance(content, str) and content:
                    context_parts.append(f"Source {i+1}: {content[:max_content_length]}")
            
            return "\n\n".join(context_parts) if context_parts else ""
            
        except Exception as e:
            logger.error(f"Error getting research context: {str(e)}")
            return ""

    async def research_chapter_topic(self, book_title: str, chapter_topic: str) -> str:
        """Research specific chapter topic"""
        query = f"{book_title} {chapter_topic}"
        return await self.get_research_context(query)


# Global research service instance
research_service = ResearchService()
