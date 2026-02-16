# Error Response System

A structured error response system with standardized error codes, messages, and context, plus retry mechanisms with exponential backoff.

## Features

### Error Responses
- **Standardized Error Codes**: Organized by category (1xxx-5xxx)
- **Consistent Format**: All errors follow the same structure
- **HTTP Status Mapping**: Automatic HTTP status code assignment
- **Validation**: Built-in error response validation
- **Convenience Functions**: Quick error creation for common scenarios

### Retry Mechanisms
- **Exponential Backoff**: Automatically increases delay between retries
- **Configurable Retries**: Set max attempts, delays, and backoff rates
- **Selective Retry**: Retry only on specific exception types
- **Decorator & Function**: Use as decorator or function call
- **Retry Callbacks**: Hook into retry events for logging/monitoring

## Error Code Categories

- **1xxx**: Input/Validation Errors
- **2xxx**: Resource Errors
- **3xxx**: Operation Errors
- **4xxx**: System Errors
- **5xxx**: External Errors

## Usage

### Basic Error Response

```python
from error_handling import create_error_response, ErrorCode

response = create_error_response(
    ErrorCode.INVALID_INPUT,
    "Invalid email format",
    {"field": "email", "value": "invalid@"}
)
```

### Convenience Functions

```python
from error_handling.error_responses import (
    invalid_input_error,
    not_found_error,
    timeout_error,
    validation_error,
    internal_error
)

# Invalid input
error = invalid_input_error("Invalid email format", field="email")

# Resource not found
error = not_found_error("User", "12345")

# Operation timeout
error = timeout_error("database_query", timeout_seconds=30)

# Validation errors
error = validation_error("Validation failed", [
    {"field": "email", "error": "invalid format"},
    {"field": "age", "error": "must be positive"}
])

# Internal error
error = internal_error("Database connection failed")
```

## Error Response Structure

```json
{
  "error": {
    "code": "ERR_1001",
    "message": "Invalid parameter value",
    "status": 400,
    "timestamp": "2024-01-01T12:00:00.000000Z",
    "details": {
      "field": "email",
      "value": "invalid@"
    }
  }
}
```

## Available Error Codes

| Code | Name | HTTP Status | Description |
|------|------|-------------|-------------|
| ERR_1001 | INVALID_INPUT | 400 | Invalid input data |
| ERR_1002 | MISSING_REQUIRED_FIELD | 400 | Required field missing |
| ERR_1003 | INVALID_FORMAT | 400 | Invalid data format |
| ERR_1004 | VALIDATION_FAILED | 400 | Validation failed |
| ERR_2001 | NOT_FOUND | 404 | Resource not found |
| ERR_2002 | ALREADY_EXISTS | 409 | Resource already exists |
| ERR_2003 | RESOURCE_UNAVAILABLE | 503 | Resource unavailable |
| ERR_3001 | TIMEOUT | 408 | Operation timeout |
| ERR_3002 | OPERATION_FAILED | 500 | Operation failed |
| ERR_3003 | UNAUTHORIZED | 401 | Unauthorized access |
| ERR_3004 | FORBIDDEN | 403 | Forbidden access |
| ERR_4001 | INTERNAL_ERROR | 500 | Internal system error |
| ERR_4002 | SERVICE_UNAVAILABLE | 503 | Service unavailable |
| ERR_4003 | CONFIGURATION_ERROR | 500 | Configuration error |
| ERR_5001 | EXTERNAL_API_ERROR | 502 | External API error |
| ERR_5002 | NETWORK_ERROR | 503 | Network error |
| ERR_5003 | RATE_LIMIT_EXCEEDED | 429 | Rate limit exceeded |

## Validation

```python
from error_handling import validate_error_response

response = create_error_response(ErrorCode.NOT_FOUND, "User not found")
is_valid = validate_error_response(response)  # Returns True
```

## Testing

Run the test suite:

```bash
cd day_33
python3 test_error_responses.py
python3 test_retry_mechanisms.py
```

Run practical examples:

```bash
python3 example_retry_usage.py
```

## Documentation

- [Error Responses](README.md) - This file
- [Retry Mechanisms](RETRY_MECHANISMS.md) - Detailed retry documentation

## Quick Start

### Error Responses

```python
from error_handling import create_error_response, ErrorCode

error = create_error_response(
    ErrorCode.INVALID_INPUT,
    "Invalid email format",
    {"field": "email"}
)
```

### Retry Mechanisms

```python
from error_handling import retry_with_backoff

@retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    retry_on=(ConnectionError, TimeoutError)
)
def api_call():
    # Your code here
    pass
```
