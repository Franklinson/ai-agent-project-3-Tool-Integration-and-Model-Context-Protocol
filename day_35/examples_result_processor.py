"""
Result Processor Usage Examples
"""

from result_processor import (
    parse_results, filter_results, format_for_llm,
    format_for_json, ResultProcessor
)
import json


# Sample API response
SAMPLE_API_RESPONSE = [
    {'title': 'Python Tutorial - Official', 'link': 'https://python.org/tutorial', 'snippet': 'Learn Python programming'},
    {'title': 'Python Documentation', 'link': 'https://docs.python.org', 'snippet': 'Official Python docs'},
    {'title': 'Real Python Tutorials', 'link': 'https://realpython.com/tutorials', 'snippet': 'Python tutorials and guides'},
    {'title': 'Python on Wikipedia', 'link': 'https://en.wikipedia.org/wiki/Python', 'snippet': 'Python programming language'},
]


def example_basic_parsing():
    """Basic result parsing"""
    print("Example 1: Basic Parsing\n" + "-"*50)
    
    parsed = parse_results(SAMPLE_API_RESPONSE, 'Python tutorial')
    
    for result in parsed[:2]:
        print(f"Rank: {result['rank']}")
        print(f"Title: {result['title']}")
        print(f"URL: {result['url']}")
        print(f"Domain: {result['metadata']['domain']}")
        print()


def example_filtering():
    """Result filtering"""
    print("\nExample 2: Filtering Results\n" + "-"*50)
    
    parsed = parse_results(SAMPLE_API_RESPONSE, 'Python')
    
    # Filter by allowed domains
    filtered = filter_results(parsed, allowed_domains=['python.org', 'docs.python.org'])
    print(f"Allowed domains filter: {len(filtered)} results")
    for r in filtered:
        print(f"  - {r['metadata']['domain']}")
    
    # Filter by blocked domains
    filtered = filter_results(parsed, blocked_domains=['wikipedia.org'])
    print(f"\nBlocked domains filter: {len(filtered)} results")
    for r in filtered:
        print(f"  - {r['metadata']['domain']}")


def example_llm_formatting():
    """LLM-friendly formatting"""
    print("\nExample 3: LLM Formatting\n" + "-"*50)
    
    parsed = parse_results(SAMPLE_API_RESPONSE, 'Python tutorial')
    formatted = format_for_llm(parsed, 'Python tutorial', max_results=3)
    
    print(formatted)


def example_json_formatting():
    """JSON formatting"""
    print("\nExample 4: JSON Formatting\n" + "-"*50)
    
    parsed = parse_results(SAMPLE_API_RESPONSE[:2], 'Python')
    formatted = format_for_json(parsed, 'Python')
    
    print(json.dumps(formatted, indent=2))


def example_complete_pipeline():
    """Complete processing pipeline"""
    print("\nExample 5: Complete Pipeline\n" + "-"*50)
    
    # Create processor with filters
    processor = ResultProcessor(
        allowed_domains=['python.org', 'realpython.com'],
        remove_duplicates=True
    )
    
    # Process for JSON
    result = processor.process(SAMPLE_API_RESPONSE, 'Python tutorial', format_type='json')
    print(f"JSON output: {result['total_results']} results")
    
    # Process for LLM
    result = processor.process(SAMPLE_API_RESPONSE, 'Python tutorial', format_type='llm')
    print(f"\nLLM output:\n{result}")


def example_integration_with_api():
    """Integration with search API client"""
    print("\nExample 6: Integration with API Client\n" + "-"*50)
    
    # Simulating API client response
    api_results = [
        {'title': 'Result 1', 'link': 'https://example.com/1', 'snippet': 'First result'},
        {'title': 'Result 2', 'link': 'https://example.com/2', 'snippet': 'Second result'},
    ]
    
    # Process results
    processor = ResultProcessor()
    processed = processor.process(api_results, 'example query', format_type='json')
    
    print(f"Query: {processed['query']}")
    print(f"Results: {processed['total_results']}")
    print(f"Processed at: {processed['processed_at']}")


def example_custom_filtering():
    """Custom filtering scenarios"""
    print("\nExample 7: Custom Filtering\n" + "-"*50)
    
    parsed = parse_results(SAMPLE_API_RESPONSE, 'Python')
    
    # Only official Python sites
    official = filter_results(parsed, allowed_domains=['python.org'])
    print(f"Official sites only: {len(official)} results")
    
    # Exclude wikis
    no_wiki = filter_results(parsed, blocked_domains=['wikipedia.org', 'wiki'])
    print(f"No wikis: {len(no_wiki)} results")
    
    # Multiple filters
    filtered = filter_results(
        parsed,
        allowed_domains=['python.org', 'realpython.com'],
        remove_duplicates=True
    )
    print(f"Multiple filters: {len(filtered)} results")


if __name__ == "__main__":
    print("Result Processor Examples\n" + "="*50)
    example_basic_parsing()
    example_filtering()
    example_llm_formatting()
    example_json_formatting()
    example_complete_pipeline()
    example_integration_with_api()
    example_custom_filtering()
