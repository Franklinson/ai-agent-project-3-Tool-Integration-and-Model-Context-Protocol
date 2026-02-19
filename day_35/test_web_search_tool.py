"""
Test suite for Web Search Tool
"""

from web_search_tool import WebSearchTool, search
import json


def test_valid_search():
    """Test valid search query"""
    print("Test 1: Valid search query")
    tool = WebSearchTool()
    
    params = {
        'query': 'Python programming',
        'num_results': 5
    }
    
    result = tool.execute(params)
    
    if 'error' in result:
        print(f"✗ Failed: {result['error']['message']}")
    else:
        print(f"✓ Success: Found {result['total_results']} results")
        if result['results']:
            print(f"  First result: {result['results'][0]['title']}")


def test_invalid_query():
    """Test empty query validation"""
    print("\nTest 2: Empty query validation")
    tool = WebSearchTool()
    
    params = {'query': ''}
    result = tool.execute(params)
    
    if 'error' in result:
        print(f"✓ Correctly rejected: {result['error']['code']}")
    else:
        print("✗ Should have failed validation")


def test_invalid_num_results():
    """Test invalid num_results"""
    print("\nTest 3: Invalid num_results")
    tool = WebSearchTool()
    
    params = {
        'query': 'test',
        'num_results': 100  # Max is 20
    }
    
    result = tool.execute(params)
    
    if 'error' in result:
        print(f"✓ Correctly rejected: {result['error']['code']}")
    else:
        print("✗ Should have failed validation")


def test_convenience_function():
    """Test convenience search function"""
    print("\nTest 4: Convenience function")
    
    result = search('AI agents', num_results=3)
    
    if 'error' in result:
        print(f"✗ Failed: {result['error']['message']}")
    else:
        print(f"✓ Success: Found {result['total_results']} results")


def test_output_structure():
    """Test output structure compliance"""
    print("\nTest 5: Output structure validation")
    
    result = search('machine learning', num_results=2)
    
    if 'error' in result:
        print(f"✗ Failed: {result['error']['message']}")
        return
    
    # Check required fields
    required_fields = ['results', 'query', 'total_results']
    missing = [f for f in required_fields if f not in result]
    
    if missing:
        print(f"✗ Missing fields: {missing}")
    else:
        print("✓ All required fields present")
        
        # Check result structure
        if result['results']:
            r = result['results'][0]
            result_fields = ['title', 'url', 'snippet']
            missing_result_fields = [f for f in result_fields if f not in r]
            
            if missing_result_fields:
                print(f"✗ Missing result fields: {missing_result_fields}")
            else:
                print("✓ Result structure valid")


def test_various_queries():
    """Test with various query types"""
    print("\nTest 6: Various query types")
    
    queries = [
        'Python tutorial',
        'how to learn AI',
        'best practices REST API'
    ]
    
    for q in queries:
        result = search(q, num_results=3)
        if 'error' in result:
            print(f"✗ '{q}': {result['error']['message']}")
        else:
            print(f"✓ '{q}': {result['total_results']} results")


if __name__ == "__main__":
    print("Web Search Tool Test Suite\n" + "="*50)
    test_valid_search()
    test_invalid_query()
    test_invalid_num_results()
    test_convenience_function()
    test_output_structure()
    test_various_queries()
    print("\n" + "="*50)
    print("Tests completed!")
