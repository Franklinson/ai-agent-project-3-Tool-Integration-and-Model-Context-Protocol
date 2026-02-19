"""
Test script for DuckDuckGo Search API Client
"""

from search_api_client import SearchAPIClient, SearchAPIError, RateLimitError


def test_basic_search():
    """Test basic search functionality"""
    print("Testing basic search...")
    client = SearchAPIClient()
    
    try:
        results = client.search("Python programming", max_results=5)
        print(f"✓ Found {len(results)} results")
        
        if results:
            print("\nFirst result:")
            print(f"  Title: {results[0]['title']}")
            print(f"  Link: {results[0]['link']}")
            print(f"  Snippet: {results[0]['snippet'][:100]}...")
    except SearchAPIError as e:
        print(f"✗ Search failed: {e}")


def test_empty_query():
    """Test error handling for empty query"""
    print("\nTesting empty query handling...")
    client = SearchAPIClient()
    
    try:
        client.search("")
        print("✗ Should have raised SearchAPIError")
    except SearchAPIError:
        print("✓ Empty query correctly rejected")


def test_rate_limiting():
    """Test rate limiting"""
    print("\nTesting rate limiting...")
    client = SearchAPIClient(rate_limit_delay=0.5)
    
    import time
    start = time.time()
    
    try:
        client.search("test query 1", max_results=1)
        client.search("test query 2", max_results=1)
        
        elapsed = time.time() - start
        if elapsed >= 0.5:
            print(f"✓ Rate limiting working (elapsed: {elapsed:.2f}s)")
        else:
            print(f"✗ Rate limiting may not be working (elapsed: {elapsed:.2f}s)")
    except SearchAPIError as e:
        print(f"✗ Search failed: {e}")


if __name__ == "__main__":
    print("DuckDuckGo Search API Client Tests\n" + "="*40)
    test_basic_search()
    test_empty_query()
    test_rate_limiting()
    print("\n" + "="*40)
    print("Tests completed!")
