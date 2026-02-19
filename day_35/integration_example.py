"""
Complete Integration Example: Search API + Result Processor
"""

# Note: This example shows the integration pattern
# Actual execution requires duckduckgo-search to be installed

from result_processor import ResultProcessor


def example_complete_workflow():
    """Complete workflow from search to formatted results"""
    print("Complete Workflow Example\n" + "="*60)
    
    # Simulated API response (in real usage, this comes from SearchAPIClient)
    simulated_api_response = [
        {'title': 'Python Tutorial', 'link': 'https://python.org/tutorial', 'snippet': 'Learn Python basics'},
        {'title': 'Python Docs', 'link': 'https://docs.python.org', 'snippet': 'Official documentation'},
        {'title': 'Python Guide', 'link': 'https://realpython.com/guide', 'snippet': 'Real Python guide'},
        {'title': 'Python Wiki', 'link': 'https://wiki.python.org', 'snippet': 'Python wiki'},
        {'title': 'Python Tutorial', 'link': 'https://python.org/tutorial', 'snippet': 'Duplicate'},
    ]
    
    query = 'Python programming tutorial'
    
    print(f"Query: '{query}'")
    print(f"Raw results: {len(simulated_api_response)}\n")
    
    # Scenario 1: Process for AI agent (LLM format, filtered)
    print("Scenario 1: AI Agent Consumption\n" + "-"*60)
    processor = ResultProcessor(
        allowed_domains=['python.org', 'docs.python.org'],
        remove_duplicates=True
    )
    
    llm_output = processor.process(simulated_api_response, query, format_type='llm')
    print(llm_output)
    
    # Scenario 2: Process for JSON API (structured data)
    print("\nScenario 2: JSON API Response\n" + "-"*60)
    processor = ResultProcessor(remove_duplicates=True)
    json_output = processor.process(simulated_api_response, query, format_type='json')
    
    print(f"Query: {json_output['query']}")
    print(f"Total Results: {json_output['total_results']}")
    print(f"Processed At: {json_output['processed_at']}")
    print("\nResults:")
    for r in json_output['results']:
        print(f"  [{r['rank']}] {r['title']} - {r['metadata']['domain']}")
    
    # Scenario 3: Trusted sources only
    print("\n\nScenario 3: Trusted Sources Only\n" + "-"*60)
    processor = ResultProcessor(
        allowed_domains=['python.org', 'docs.python.org', 'realpython.com'],
        blocked_domains=['wiki'],
        remove_duplicates=True
    )
    
    trusted_output = processor.process(simulated_api_response, query, format_type='json')
    print(f"Filtered to {trusted_output['total_results']} trusted sources:")
    for r in trusted_output['results']:
        print(f"  - {r['metadata']['domain']}")


def example_with_real_api():
    """Example showing integration with real API client"""
    print("\n\nIntegration with Real API Client\n" + "="*60)
    
    print("""
# Real usage pattern:

from search_api_client import SearchAPIClient
from result_processor import ResultProcessor

# Step 1: Search
client = SearchAPIClient(rate_limit_delay=1.0)
raw_results = client.search('Python tutorial', max_results=10)

# Step 2: Process
processor = ResultProcessor(
    allowed_domains=['python.org', 'realpython.com'],
    remove_duplicates=True
)

# Step 3: Format for LLM
llm_output = processor.process(raw_results, 'Python tutorial', format_type='llm')
print(llm_output)

# Or format as JSON
json_output = processor.process(raw_results, 'Python tutorial', format_type='json')
""")


def example_use_cases():
    """Different use case examples"""
    print("\n\nCommon Use Cases\n" + "="*60)
    
    print("""
Use Case 1: Research Assistant
------------------------------
processor = ResultProcessor(
    allowed_domains=['edu', 'gov', 'org'],  # Academic/official sources
    remove_duplicates=True
)
results = processor.process(raw_results, query, format_type='llm')

Use Case 2: News Aggregator
----------------------------
processor = ResultProcessor(
    allowed_domains=['reuters.com', 'bbc.com', 'apnews.com'],
    remove_duplicates=True
)
results = processor.process(raw_results, query, format_type='json')

Use Case 3: Developer Documentation Search
------------------------------------------
processor = ResultProcessor(
    allowed_domains=['docs.python.org', 'stackoverflow.com', 'github.com'],
    blocked_domains=['spam.com', 'ads.com'],
    remove_duplicates=True
)
results = processor.process(raw_results, query, format_type='llm')

Use Case 4: General Web Search (No Filtering)
---------------------------------------------
processor = ResultProcessor(remove_duplicates=True)
results = processor.process(raw_results, query, format_type='json')
""")


if __name__ == "__main__":
    example_complete_workflow()
    example_with_real_api()
    example_use_cases()
    
    print("\n" + "="*60)
    print("Integration examples completed!")
