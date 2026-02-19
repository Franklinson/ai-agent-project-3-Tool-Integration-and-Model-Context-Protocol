"""
DuckDuckGo Search API Client
No authentication required - free to use
"""

import time
from typing import List, Dict, Optional
from duckduckgo_search import DDGS


class SearchAPIError(Exception):
    """Base exception for search API errors"""
    pass


class RateLimitError(SearchAPIError):
    """Raised when rate limit is exceeded"""
    pass


class NetworkError(SearchAPIError):
    """Raised when network connection fails"""
    pass


class TimeoutError(SearchAPIError):
    """Raised when request times out"""
    pass


class InvalidInputError(SearchAPIError):
    """Raised when input is invalid"""
    pass


class SearchAPIClient:
    """DuckDuckGo search API client with error handling and rate limiting"""
    
    def __init__(self, rate_limit_delay: float = 1.0):
        """
        Initialize the search client
        
        Args:
            rate_limit_delay: Delay between requests in seconds (default: 1.0)
        """
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0
    
    def _handle_rate_limit(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, str]]:
        """
        Perform a web search
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return (default: 10)
            
        Returns:
            List of search results with title, link, and snippet
            
        Raises:
            SearchAPIError: If search fails
            RateLimitError: If rate limit is exceeded
        """
        if not query or not query.strip():
            raise InvalidInputError("Query cannot be empty")
        
        if max_results < 1 or max_results > 50:
            raise InvalidInputError(f"max_results must be between 1 and 50, got {max_results}")
        
        self._handle_rate_limit()
        
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                return [
                    {
                        'title': r.get('title', ''),
                        'link': r.get('href', ''),
                        'snippet': r.get('body', '')
                    }
                    for r in results
                ]
        except Exception as e:
            error_str = str(e).lower()
            
            if 'ratelimit' in error_str or 'rate limit' in error_str:
                raise RateLimitError(f"Rate limit exceeded: {e}")
            elif 'timeout' in error_str:
                raise TimeoutError(f"Request timed out: {e}")
            elif 'network' in error_str or 'connection' in error_str:
                raise NetworkError(f"Network error: {e}")
            else:
                raise SearchAPIError(f"Search failed: {e}")
