# Day 35: Search API Integration

## Overview
Integration with DuckDuckGo search API - a free, no-authentication-required search provider.

## Files
- `search_api_client.py` - Main API client implementation
- `test_search_client.py` - Test suite for the client

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. No API Key Required
DuckDuckGo search is free and requires no authentication or API keys.

## Usage

### Basic Search
```python
from search_api_client import SearchAPIClient

client = SearchAPIClient()
results = client.search("Python programming", max_results=10)

for result in results:
    print(f"Title: {result['title']}")
    print(f"Link: {result['link']}")
    print(f"Snippet: {result['snippet']}")
```

### With Custom Rate Limiting
```python
# Set custom delay between requests (in seconds)
client = SearchAPIClient(rate_limit_delay=2.0)
results = client.search("AI agents")
```

### Error Handling
```python
from search_api_client import SearchAPIClient, SearchAPIError, RateLimitError

client = SearchAPIClient()

try:
    results = client.search("query")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e}")
except SearchAPIError as e:
    print(f"Search error: {e}")
```

## Testing

Run the test suite:
```bash
cd day_35
python test_search_client.py
```

## Features

### ✓ No Authentication Required
- Free to use
- No API key setup needed
- No registration required

### ✓ Error Handling
- Custom exceptions for different error types
- Empty query validation
- Network error handling

### ✓ Rate Limiting
- Configurable delay between requests
- Automatic rate limit enforcement
- Rate limit error detection

### ✓ Clean API
- Simple, intuitive interface
- Structured result format
- Type hints for better IDE support

## API Client Class

### SearchAPIClient

**Constructor:**
- `rate_limit_delay` (float): Delay between requests in seconds (default: 1.0)

**Methods:**
- `search(query: str, max_results: int = 10)`: Perform web search
  - Returns: List of dicts with 'title', 'link', 'snippet'
  - Raises: SearchAPIError, RateLimitError

**Exceptions:**
- `SearchAPIError`: Base exception for search errors
- `RateLimitError`: Raised when rate limit is exceeded

## Advantages of DuckDuckGo

1. **No Authentication** - Start using immediately
2. **Free** - No costs or quotas
3. **Privacy-Focused** - No tracking
4. **Simple** - Minimal setup required
5. **Reliable** - Good search quality

## Limitations

- Lower rate limits compared to paid APIs
- Fewer advanced features than Google/Bing
- No official API (uses web scraping library)

## Next Steps

- Integrate with MCP server
- Add caching layer
- Implement retry logic with exponential backoff
- Add more search parameters (region, time range, etc.)


---

## Web Search Tool

### Overview
Complete web search tool with schema validation, error handling, and structured result processing.

### Files
- `web_search_tool.py` - Main tool implementation
- `test_web_search_tool.py` - Comprehensive test suite
- `examples.py` - Usage examples

### Features

#### ✓ Schema Validation
- Input validation using Day 32 schemas
- Output validation for structured results
- Automatic error responses for invalid data

#### ✓ Error Handling
- Integration with Day 33 error response system
- Structured error codes (ERR_1004, ERR_5001, ERR_5003)
- Detailed error messages with context

#### ✓ Result Processing
- Structured output format (title, url, snippet)
- Query metadata included
- Total results count

### Usage

#### Quick Start
```python
from web_search_tool import search

# Simple search
result = search('Python programming')

if 'error' not in result:
    for r in result['results']:
        print(f"{r['title']}: {r['url']}")
```

#### With Parameters
```python
result = search(
    query='AI agents',
    num_results=10,
    sort_by='relevance'
)
```

#### Using Tool Class
```python
from web_search_tool import WebSearchTool

tool = WebSearchTool()
params = {
    'query': 'machine learning',
    'num_results': 5
}
result = tool.execute(params)
```

### Input Schema

```json
{
  "query": "string (required, 1-500 chars)",
  "num_results": "integer (optional, 1-20, default: 5)",
  "sort_by": "string (optional, 'relevance'|'date', default: 'relevance')"
}
```

### Output Schema

```json
{
  "results": [
    {
      "title": "string",
      "url": "string (URI)",
      "snippet": "string"
    }
  ],
  "query": "string",
  "total_results": "integer"
}
```

### Error Responses

```json
{
  "error": {
    "code": "ERR_1004",
    "message": "Input validation failed",
    "status": 400,
    "timestamp": "2024-01-01T00:00:00Z",
    "details": {
      "validation_errors": ["..."]
    }
  }
}
```

### Error Codes
- `ERR_1004` - Validation failed
- `ERR_5001` - External API error
- `ERR_5003` - Rate limit exceeded
- `ERR_4001` - Internal error

### Testing

```bash
cd day_35
python test_web_search_tool.py
```

### Examples

```bash
python examples.py
```

### Integration Points

1. **Day 32 Schemas** - Input/output validation
2. **Day 33 Error Handling** - Structured error responses
3. **Task 35.1 API Client** - DuckDuckGo search integration

### Architecture

```
WebSearchTool
├── Input Validation (Day 32 SchemaValidator)
├── API Client (SearchAPIClient)
├── Result Processing
├── Output Validation
└── Error Handling (Day 33 ErrorCode)
```


---

## Result Processor

### Overview
Structures and formats search results for agent/LLM consumption with parsing, filtering, and formatting capabilities.

### Files
- `result_processor.py` - Main processor implementation
- `test_result_processor.py` - Comprehensive test suite
- `examples_result_processor.py` - Usage examples

### Features

#### ✓ Result Parsing
- Extract title, URL, snippet
- Add rank information
- Include metadata (domain, query, timestamp)

#### ✓ Result Filtering
- Filter by allowed domains
- Block specific domains
- Remove duplicate URLs
- Configurable filtering pipeline

#### ✓ Result Formatting
- LLM-friendly text format
- Structured JSON format
- Metadata inclusion
- Max results limiting

### Usage

#### Basic Parsing
```python
from result_processor import parse_results

raw_results = [
    {'title': 'Example', 'link': 'https://example.com', 'snippet': 'Description'}
]

parsed = parse_results(raw_results, 'search query')
# Returns: [{'rank': 1, 'title': '...', 'url': '...', 'snippet': '...', 'metadata': {...}}]
```

#### Filtering
```python
from result_processor import filter_results

# Filter by allowed domains
filtered = filter_results(
    parsed,
    allowed_domains=['python.org', 'docs.python.org']
)

# Block domains
filtered = filter_results(
    parsed,
    blocked_domains=['spam.com']
)

# Remove duplicates
filtered = filter_results(parsed, remove_duplicates=True)
```

#### LLM Formatting
```python
from result_processor import format_for_llm

formatted = format_for_llm(parsed, 'Python tutorial', max_results=5)
print(formatted)
# Output:
# Search Results for: 'Python tutorial'
# Total Results: 5
#
# [1] Python Tutorial
# URL: https://python.org/tutorial
# Domain: python.org
# Snippet: Learn Python basics
```

#### JSON Formatting
```python
from result_processor import format_for_json

formatted = format_for_json(parsed, 'Python tutorial')
# Returns: {'query': '...', 'total_results': 5, 'results': [...], 'processed_at': '...'}
```

#### Complete Pipeline
```python
from result_processor import ResultProcessor

processor = ResultProcessor(
    allowed_domains=['python.org'],
    blocked_domains=['spam.com'],
    remove_duplicates=True
)

# JSON output
result = processor.process(raw_results, 'query', format_type='json')

# LLM output
result = processor.process(raw_results, 'query', format_type='llm')
```

### API Reference

#### parse_results(raw_results, query)
Parse raw API results into structured format.

**Returns:** List of dicts with rank, title, url, snippet, metadata

#### filter_results(results, allowed_domains=None, blocked_domains=None, remove_duplicates=True)
Filter results based on criteria.

**Returns:** Filtered list of results

#### format_for_llm(results, query, max_results=None)
Format results for LLM consumption.

**Returns:** Formatted string

#### format_for_json(results, query)
Format results as structured JSON.

**Returns:** JSON-serializable dict

#### ResultProcessor(allowed_domains=None, blocked_domains=None, remove_duplicates=True)
Complete processing pipeline.

**Methods:**
- `process(raw_results, query, format_type='json')` - Full pipeline

### Result Structure

#### Parsed Result
```python
{
    'rank': 1,
    'title': 'Page Title',
    'url': 'https://example.com',
    'snippet': 'Page description',
    'metadata': {
        'domain': 'example.com',
        'query': 'search query',
        'retrieved_at': '2024-01-01T00:00:00Z'
    }
}
```

#### JSON Output
```python
{
    'query': 'search query',
    'total_results': 5,
    'results': [...],
    'processed_at': '2024-01-01T00:00:00Z'
}
```

### Testing

```bash
cd day_35
python test_result_processor.py
```

### Examples

```bash
python examples_result_processor.py
```

### Integration Example

```python
from search_api_client import SearchAPIClient
from result_processor import ResultProcessor

# Search
client = SearchAPIClient()
raw_results = client.search('Python tutorial', max_results=10)

# Process
processor = ResultProcessor(
    allowed_domains=['python.org', 'realpython.com'],
    remove_duplicates=True
)

# Get LLM-formatted output
formatted = processor.process(raw_results, 'Python tutorial', format_type='llm')
print(formatted)
```

### Use Cases

1. **Agent Consumption** - Format results for AI agents to process
2. **Domain Filtering** - Restrict results to trusted sources
3. **Duplicate Removal** - Clean up redundant results
4. **Metadata Tracking** - Track query and retrieval information
5. **LLM Integration** - Provide clean, structured input for language models


---

## Enhanced Error Handling

### Error Types

The system includes comprehensive error handling with specific error types:

#### SearchAPIClient Errors
- `SearchAPIError` - Base exception for all search errors
- `InvalidInputError` - Invalid input parameters (empty query, invalid max_results)
- `RateLimitError` - Rate limit exceeded
- `NetworkError` - Network connection failures
- `TimeoutError` - Request timeout

#### Error Code Mapping

| Error Type | Error Code | HTTP Status | Description |
|------------|------------|-------------|-------------|
| InvalidInputError | ERR_1001 | 400 | Invalid input parameters |
| Validation Failed | ERR_1004 | 400 | Schema validation failed |
| TimeoutError | ERR_3001 | 408 | Request timed out |
| Internal Error | ERR_4001 | 500 | Unexpected internal error |
| SearchAPIError | ERR_5001 | 502 | External API error |
| NetworkError | ERR_5002 | 503 | Network connection error |
| RateLimitError | ERR_5003 | 429 | Rate limit exceeded |

### Error Response Format

All errors return a structured response:

```json
{
  "error": {
    "code": "ERR_5003",
    "message": "Rate limit exceeded: ...",
    "status": 429,
    "timestamp": "2024-01-01T00:00:00Z",
    "details": {
      "query": "search query"
    }
  }
}
```

### Error Handling Examples

#### Handle Specific Errors
```python
from web_search_tool import search

result = search('query')

if 'error' in result:
    error = result['error']
    
    if error['code'] == 'ERR_5003':
        # Rate limit - wait and retry
        time.sleep(60)
        result = search('query')
    elif error['code'] == 'ERR_5002':
        # Network error - check connection
        print("Network error:", error['message'])
    elif error['code'] == 'ERR_3001':
        # Timeout - retry with smaller request
        result = search('query', num_results=5)
    else:
        # Other errors
        print(f"Error {error['code']}: {error['message']}")
```

#### Graceful Degradation
```python
def safe_search(query, retries=3):
    """Search with automatic retry on rate limit"""
    for attempt in range(retries):
        result = search(query)
        
        if 'error' not in result:
            return result
        
        if result['error']['code'] == 'ERR_5003':
            time.sleep(2 ** attempt)  # Exponential backoff
            continue
        else:
            return result  # Other errors, don't retry
    
    return {'error': {'message': 'Max retries exceeded'}}
```

---

## Testing

### Test Suite

Comprehensive test suite with **26 tests** covering all functionality.

**Location:** `day_35/tests/test_web_search.py`

### Running Tests

```bash
cd day_35/tests
python3 test_web_search.py
```

**Results:**
```
Ran 26 tests in 0.119s

OK
```

### Test Coverage

#### TestWebSearchTool (15 tests)
- ✓ Successful searches
- ✓ Input validation (6 tests)
- ✓ Error handling (5 tests)
- ✓ Result processing
- ✓ Empty results

#### TestSearchConvenienceFunction (2 tests)
- ✓ Basic function usage
- ✓ Default parameters

#### TestSearchAPIClient (5 tests)
- ✓ Input validation (4 tests)
- ✓ Rate limiting

#### TestEdgeCases (4 tests)
- ✓ Special characters
- ✓ Unicode support
- ✓ Query length limits
- ✓ Boundary conditions

### Error Scenarios Tested

✓ Empty query (ERR_1004)  
✓ Invalid num_results (ERR_1004)  
✓ Missing required fields (ERR_1004)  
✓ Rate limit errors (ERR_5003)  
✓ Network errors (ERR_5002)  
✓ Timeout errors (ERR_3001)  
✓ API errors (ERR_5001)  
✓ Internal errors (ERR_4001)  

### Test Documentation

- `tests/README.md` - Test usage guide
- `tests/TEST_SUMMARY.md` - Detailed test results
- Inline docstrings - Each test documented

### Quick Test Examples

```bash
# Run all tests
python3 test_web_search.py

# Run specific test class
python3 -m unittest test_web_search.TestWebSearchTool

# Run specific test
python3 -m unittest test_web_search.TestWebSearchTool.test_successful_search
```

---

## Production Readiness Checklist

✓ **Error Handling** - Comprehensive error types and codes  
✓ **Input Validation** - Schema-based validation (Day 32)  
✓ **Output Validation** - Structured result validation  
✓ **Rate Limiting** - Configurable rate limit enforcement  
✓ **Testing** - 26 tests, 100% pass rate  
✓ **Documentation** - Complete API and usage docs  
✓ **Type Hints** - Full type annotation coverage  
✓ **Error Responses** - Structured error format (Day 33)  
✓ **Result Processing** - Filtering and formatting for LLMs  
✓ **Edge Cases** - Unicode, special chars, boundaries  

---

## Troubleshooting

### Common Issues

#### Rate Limit Errors
```python
# Increase delay between requests
client = SearchAPIClient(rate_limit_delay=2.0)
```

#### Timeout Errors
```python
# Reduce number of results
result = search('query', num_results=5)
```

#### Network Errors
```python
# Check connection and retry
if 'error' in result and result['error']['code'] == 'ERR_5002':
    time.sleep(5)
    result = search('query')
```

#### Validation Errors
```python
# Check input parameters
if 'error' in result and result['error']['code'] == 'ERR_1004':
    print("Validation error:", result['error']['details'])
```

### Debug Mode

Enable detailed error information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

result = search('query')
```

---

## Performance Considerations

- **Rate Limiting**: 1 second delay between requests (configurable)
- **Max Results**: 1-20 per query (schema enforced)
- **Query Length**: 1-500 characters (schema enforced)
- **Timeout**: Handled gracefully with ERR_3001
- **Caching**: Not implemented (future enhancement)

---

## Security Considerations

✓ **Input Sanitization** - Schema validation prevents injection  
✓ **No Credentials** - DuckDuckGo requires no API keys  
✓ **Error Messages** - No sensitive data in error responses  
✓ **Rate Limiting** - Prevents abuse  
✓ **Validation** - All inputs validated before processing  
