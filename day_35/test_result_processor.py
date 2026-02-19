"""
Test suite for Result Processor
"""

from result_processor import (
    parse_results, filter_results, format_for_llm, 
    format_for_json, ResultProcessor
)
import json


# Sample test data
SAMPLE_RESULTS = [
    {'title': 'Python Tutorial', 'link': 'https://python.org/tutorial', 'snippet': 'Learn Python basics'},
    {'title': 'Python Docs', 'link': 'https://docs.python.org', 'snippet': 'Official documentation'},
    {'title': 'Python Guide', 'link': 'https://realpython.com/guide', 'snippet': 'Real Python guide'},
    {'title': 'Python Tutorial', 'link': 'https://python.org/tutorial', 'snippet': 'Duplicate entry'},
]


def test_parse_results():
    """Test result parsing"""
    print("Test 1: Parse results")
    
    parsed = parse_results(SAMPLE_RESULTS[:2], 'Python tutorial')
    
    assert len(parsed) == 2
    assert parsed[0]['rank'] == 1
    assert parsed[1]['rank'] == 2
    assert 'metadata' in parsed[0]
    assert parsed[0]['metadata']['domain'] == 'python.org'
    
    print("✓ Parsing works correctly")


def test_filter_duplicates():
    """Test duplicate removal"""
    print("\nTest 2: Filter duplicates")
    
    parsed = parse_results(SAMPLE_RESULTS, 'Python')
    filtered = filter_results(parsed, remove_duplicates=True)
    
    assert len(filtered) == 3  # 4 results, 1 duplicate
    print(f"✓ Removed duplicates: {len(SAMPLE_RESULTS)} -> {len(filtered)}")


def test_filter_domains():
    """Test domain filtering"""
    print("\nTest 3: Filter by domain")
    
    parsed = parse_results(SAMPLE_RESULTS, 'Python')
    
    # Allowed domains
    filtered = filter_results(parsed, allowed_domains=['python.org'])
    assert all('python.org' in r['metadata']['domain'] for r in filtered)
    print(f"✓ Allowed domains: {len(filtered)} results from python.org")
    
    # Blocked domains
    filtered = filter_results(parsed, blocked_domains=['realpython.com'])
    assert not any('realpython.com' in r['metadata']['domain'] for r in filtered)
    print(f"✓ Blocked domains: {len(filtered)} results (realpython.com excluded)")


def test_format_for_llm():
    """Test LLM formatting"""
    print("\nTest 4: Format for LLM")
    
    parsed = parse_results(SAMPLE_RESULTS[:2], 'Python tutorial')
    formatted = format_for_llm(parsed, 'Python tutorial')
    
    assert "Search Results for: 'Python tutorial'" in formatted
    assert "[1]" in formatted
    assert "URL:" in formatted
    assert "Domain:" in formatted
    
    print("✓ LLM format generated")
    print("\nSample output:")
    print(formatted[:200] + "...")


def test_format_for_json():
    """Test JSON formatting"""
    print("\nTest 5: Format for JSON")
    
    parsed = parse_results(SAMPLE_RESULTS[:2], 'Python')
    formatted = format_for_json(parsed, 'Python')
    
    assert 'query' in formatted
    assert 'total_results' in formatted
    assert 'results' in formatted
    assert formatted['total_results'] == 2
    
    print("✓ JSON format generated")
    print(f"  Query: {formatted['query']}")
    print(f"  Total: {formatted['total_results']}")


def test_result_processor():
    """Test complete processor pipeline"""
    print("\nTest 6: ResultProcessor pipeline")
    
    processor = ResultProcessor(
        blocked_domains=['realpython.com'],
        remove_duplicates=True
    )
    
    # JSON format
    result = processor.process(SAMPLE_RESULTS, 'Python', format_type='json')
    assert 'results' in result
    assert len(result['results']) == 2  # 4 - 1 duplicate - 1 blocked
    print(f"✓ JSON pipeline: {len(result['results'])} results")
    
    # LLM format
    result = processor.process(SAMPLE_RESULTS, 'Python', format_type='llm')
    assert isinstance(result, str)
    assert 'Search Results' in result
    print("✓ LLM pipeline: formatted string generated")


def test_empty_results():
    """Test handling of empty results"""
    print("\nTest 7: Empty results")
    
    parsed = parse_results([], 'test query')
    assert len(parsed) == 0
    
    formatted = format_for_llm([], 'test query')
    assert "No results found" in formatted
    
    print("✓ Empty results handled correctly")


def test_metadata():
    """Test metadata inclusion"""
    print("\nTest 8: Metadata")
    
    parsed = parse_results(SAMPLE_RESULTS[:1], 'test')
    result = parsed[0]
    
    assert 'metadata' in result
    assert 'domain' in result['metadata']
    assert 'query' in result['metadata']
    assert 'retrieved_at' in result['metadata']
    
    print("✓ Metadata included:")
    print(f"  Domain: {result['metadata']['domain']}")
    print(f"  Query: {result['metadata']['query']}")


def test_max_results():
    """Test max results limiting"""
    print("\nTest 9: Max results limit")
    
    parsed = parse_results(SAMPLE_RESULTS, 'test')
    formatted = format_for_llm(parsed, 'test', max_results=2)
    
    # Count result entries
    count = formatted.count('[')
    assert count == 2
    
    print(f"✓ Limited to 2 results (from {len(parsed)})")


if __name__ == "__main__":
    print("Result Processor Test Suite\n" + "="*50)
    test_parse_results()
    test_filter_duplicates()
    test_filter_domains()
    test_format_for_llm()
    test_format_for_json()
    test_result_processor()
    test_empty_results()
    test_metadata()
    test_max_results()
    print("\n" + "="*50)
    print("All tests passed!")
