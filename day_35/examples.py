"""
Web Search Tool Usage Examples
"""

from web_search_tool import search, WebSearchTool
import json


def example_basic_search():
    """Basic search example"""
    print("Example 1: Basic Search\n" + "-"*40)
    
    result = search('Python programming')
    
    if 'error' in result:
        print(f"Error: {result['error']['message']}")
    else:
        print(f"Query: {result['query']}")
        print(f"Total results: {result['total_results']}\n")
        
        for i, r in enumerate(result['results'][:3], 1):
            print(f"{i}. {r['title']}")
            print(f"   {r['url']}")
            print(f"   {r['snippet'][:100]}...\n")


def example_custom_parameters():
    """Search with custom parameters"""
    print("\nExample 2: Custom Parameters\n" + "-"*40)
    
    result = search(
        query='machine learning tutorials',
        num_results=3,
        sort_by='relevance'
    )
    
    if 'error' not in result:
        print(f"Found {result['total_results']} results")
        for r in result['results']:
            print(f"- {r['title']}")


def example_error_handling():
    """Error handling example"""
    print("\nExample 3: Error Handling\n" + "-"*40)
    
    # Invalid query
    result = search('')
    
    if 'error' in result:
        error = result['error']
        print(f"Error Code: {error['code']}")
        print(f"Message: {error['message']}")
        print(f"Status: {error['status']}")


def example_tool_class():
    """Using the tool class directly"""
    print("\nExample 4: Using Tool Class\n" + "-"*40)
    
    tool = WebSearchTool()
    
    params = {
        'query': 'REST API design',
        'num_results': 5,
        'sort_by': 'relevance'
    }
    
    result = tool.execute(params)
    
    if 'error' not in result:
        print(f"Query: {result['query']}")
        print(f"Results: {result['total_results']}")


def example_json_output():
    """JSON formatted output"""
    print("\nExample 5: JSON Output\n" + "-"*40)
    
    result = search('AI agents', num_results=2)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    print("Web Search Tool Examples\n" + "="*50)
    example_basic_search()
    example_custom_parameters()
    example_error_handling()
    example_tool_class()
    example_json_output()
