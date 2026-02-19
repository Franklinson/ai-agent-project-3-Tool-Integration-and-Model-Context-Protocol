"""
Result processor for structuring and formatting search results
"""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from urllib.parse import urlparse


def parse_results(raw_results: List[Dict[str, str]], query: str) -> List[Dict[str, Any]]:
    """
    Parse and structure raw API results
    
    Args:
        raw_results: Raw results from API
        query: Original search query
        
    Returns:
        Structured results with metadata
    """
    parsed = []
    
    for rank, result in enumerate(raw_results, 1):
        parsed_url = urlparse(result.get('link', ''))
        
        parsed.append({
            'rank': rank,
            'title': result.get('title', '').strip(),
            'url': result.get('link', ''),
            'snippet': result.get('snippet', '').strip(),
            'metadata': {
                'domain': parsed_url.netloc,
                'query': query,
                'retrieved_at': datetime.utcnow().isoformat() + 'Z'
            }
        })
    
    return parsed


def filter_results(
    results: List[Dict[str, Any]],
    allowed_domains: Optional[List[str]] = None,
    blocked_domains: Optional[List[str]] = None,
    remove_duplicates: bool = True
) -> List[Dict[str, Any]]:
    """
    Filter results based on criteria
    
    Args:
        results: Parsed results
        allowed_domains: Only include these domains
        blocked_domains: Exclude these domains
        remove_duplicates: Remove duplicate URLs
        
    Returns:
        Filtered results
    """
    filtered = []
    seen_urls: Set[str] = set()
    
    for result in results:
        url = result['url']
        domain = result['metadata']['domain']
        
        # Check duplicates
        if remove_duplicates and url in seen_urls:
            continue
        
        # Check allowed domains
        if allowed_domains and not any(d in domain for d in allowed_domains):
            continue
        
        # Check blocked domains
        if blocked_domains and any(d in domain for d in blocked_domains):
            continue
        
        filtered.append(result)
        seen_urls.add(url)
    
    return filtered


def format_for_llm(results: List[Dict[str, Any]], query: str, max_results: Optional[int] = None) -> str:
    """
    Format results for LLM consumption
    
    Args:
        results: Parsed and filtered results
        query: Original search query
        max_results: Maximum results to include
        
    Returns:
        Formatted string for LLM
    """
    if max_results:
        results = results[:max_results]
    
    if not results:
        return f"No results found for query: '{query}'"
    
    output = [f"Search Results for: '{query}'"]
    output.append(f"Total Results: {len(results)}\n")
    
    for result in results:
        output.append(f"[{result['rank']}] {result['title']}")
        output.append(f"URL: {result['url']}")
        output.append(f"Domain: {result['metadata']['domain']}")
        output.append(f"Snippet: {result['snippet']}")
        output.append("")
    
    return "\n".join(output)


def format_for_json(results: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
    """
    Format results as structured JSON
    
    Args:
        results: Parsed and filtered results
        query: Original search query
        
    Returns:
        JSON-serializable dictionary
    """
    return {
        'query': query,
        'total_results': len(results),
        'results': results,
        'processed_at': datetime.utcnow().isoformat() + 'Z'
    }


class ResultProcessor:
    """Complete result processing pipeline"""
    
    def __init__(
        self,
        allowed_domains: Optional[List[str]] = None,
        blocked_domains: Optional[List[str]] = None,
        remove_duplicates: bool = True
    ):
        self.allowed_domains = allowed_domains
        self.blocked_domains = blocked_domains
        self.remove_duplicates = remove_duplicates
    
    def process(
        self,
        raw_results: List[Dict[str, str]],
        query: str,
        format_type: str = 'json'
    ) -> Any:
        """
        Complete processing pipeline
        
        Args:
            raw_results: Raw API results
            query: Search query
            format_type: Output format ('json' or 'llm')
            
        Returns:
            Processed results in specified format
        """
        # Parse
        parsed = parse_results(raw_results, query)
        
        # Filter
        filtered = filter_results(
            parsed,
            self.allowed_domains,
            self.blocked_domains,
            self.remove_duplicates
        )
        
        # Format
        if format_type == 'llm':
            return format_for_llm(filtered, query)
        else:
            return format_for_json(filtered, query)
