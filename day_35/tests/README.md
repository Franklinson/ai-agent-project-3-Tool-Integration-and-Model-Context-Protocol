# Web Search Tool Tests

## Overview
Comprehensive test suite for the web search tool with 26 tests covering all functionality, error scenarios, and edge cases.

## Running Tests

### Run All Tests
```bash
cd day_35/tests
python3 test_web_search.py
```

### Run with Verbose Output
```bash
python3 test_web_search.py -v
```

### Run Specific Test Class
```python
python3 -m unittest test_web_search.TestWebSearchTool
```

### Run Specific Test
```python
python3 -m unittest test_web_search.TestWebSearchTool.test_successful_search
```

## Test Structure

```
test_web_search.py
├── TestWebSearchTool (15 tests)
│   ├── Successful operations (4 tests)
│   ├── Input validation (6 tests)
│   └── Error handling (5 tests)
├── TestSearchConvenienceFunction (2 tests)
├── TestSearchAPIClient (5 tests)
└── TestEdgeCases (4 tests)
```

## Test Categories

### 1. Successful Operations
- Valid searches with results
- Empty result handling
- Result structure validation
- Default parameter handling

### 2. Input Validation
- Empty query rejection
- Whitespace query rejection
- Invalid num_results (too low/high)
- Missing required fields
- Invalid sort_by parameter
- Query length validation

### 3. Error Handling
- Rate limit errors (ERR_5003)
- Network errors (ERR_5002)
- Timeout errors (ERR_3001)
- API errors (ERR_5001)
- Internal errors (ERR_4001)

### 4. Edge Cases
- Special characters in queries
- Unicode characters
- Maximum query length (500 chars)
- Boundary conditions

## Test Results

```
Ran 26 tests in 0.119s

OK
```

**All tests pass!** ✓

## Error Codes Tested

| Code | Description | Status |
|------|-------------|--------|
| ERR_1004 | Validation Failed | ✓ Tested |
| ERR_3001 | Timeout | ✓ Tested |
| ERR_4001 | Internal Error | ✓ Tested |
| ERR_5001 | External API Error | ✓ Tested |
| ERR_5002 | Network Error | ✓ Tested |
| ERR_5003 | Rate Limit Exceeded | ✓ Tested |

## Mocking

Tests use mocking to:
- Avoid actual API calls
- Simulate error conditions
- Test rate limiting
- Ensure consistent results

```python
@patch('day_35.web_search_tool.SearchAPIClient.search')
def test_successful_search(self, mock_search):
    mock_search.return_value = [...]
    # Test code
```

## Dependencies

- `unittest` - Python standard library
- `unittest.mock` - Mocking framework
- No external test dependencies required

## Test Coverage

### Covered
✓ All error types  
✓ Input validation  
✓ Output validation  
✓ Rate limiting  
✓ Result processing  
✓ Error responses  

### Not Covered
- Live API integration (requires API)
- Network retry (not implemented)
- Caching (not implemented)

## Adding New Tests

1. Add test method to appropriate class
2. Use descriptive name: `test_<what>_<scenario>`
3. Add docstring explaining test purpose
4. Use mocking for external dependencies
5. Assert expected behavior

Example:
```python
@patch('day_35.web_search_tool.SearchAPIClient.search')
def test_new_feature(self, mock_search):
    """Test description"""
    mock_search.return_value = [...]
    
    result = self.tool.execute(params)
    
    self.assertNotIn('error', result)
    self.assertEqual(result['query'], 'test')
```

## Continuous Integration

Tests are CI-ready:
- No external dependencies
- Fast execution (< 1 second)
- Clear failure messages
- Proper exit codes

## Troubleshooting

### Import Errors
Ensure you're running from the correct directory:
```bash
cd day_35/tests
python3 test_web_search.py
```

### Module Not Found
The test file handles path setup automatically. If issues persist:
```python
import sys
sys.path.append('../..')
```

### Mock Issues
Ensure duckduckgo_search is mocked before imports:
```python
sys.modules['duckduckgo_search'] = MagicMock()
```

## Documentation

- `TEST_SUMMARY.md` - Detailed test results and coverage
- Inline docstrings - Each test has description
- This README - Usage and structure

## Next Steps

- Run tests before committing changes
- Add tests for new features
- Maintain 100% pass rate
- Update documentation as needed
