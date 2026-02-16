"""Test error response system."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from error_handling.error_responses import (
    create_error_response,
    ErrorCode,
    validate_error_response,
    invalid_input_error,
    not_found_error,
    timeout_error,
    validation_error,
    internal_error
)


def test_create_error_response():
    """Test basic error response creation."""
    print("Testing create_error_response...")
    
    response = create_error_response(
        ErrorCode.INVALID_INPUT,
        "Invalid parameter value",
        {"parameter": "user_id", "value": "abc"}
    )
    
    assert "error" in response
    assert response["error"]["code"] == "ERR_1001"
    assert response["error"]["message"] == "Invalid parameter value"
    assert response["error"]["status"] == 400
    assert "timestamp" in response["error"]
    assert response["error"]["details"]["parameter"] == "user_id"
    
    print("✓ Basic error response creation works")


def test_error_codes():
    """Test all error codes."""
    print("\nTesting error codes...")
    
    codes = [
        (ErrorCode.INVALID_INPUT, 400),
        (ErrorCode.NOT_FOUND, 404),
        (ErrorCode.TIMEOUT, 408),
        (ErrorCode.UNAUTHORIZED, 401),
        (ErrorCode.INTERNAL_ERROR, 500),
        (ErrorCode.RATE_LIMIT_EXCEEDED, 429)
    ]
    
    for code, expected_status in codes:
        response = create_error_response(code, "Test message")
        assert response["error"]["status"] == expected_status
        print(f"✓ {code.value} -> HTTP {expected_status}")


def test_validate_error_response():
    """Test error response validation."""
    print("\nTesting error response validation...")
    
    # Valid response
    valid_response = create_error_response(ErrorCode.NOT_FOUND, "Resource not found")
    assert validate_error_response(valid_response) == True
    print("✓ Valid response passes validation")
    
    # Invalid responses
    invalid_responses = [
        {},
        {"error": {}},
        {"error": {"code": "ERR_1001"}},
        {"error": {"code": 123, "message": "test", "timestamp": "2024-01-01", "status": 400}}
    ]
    
    for invalid in invalid_responses:
        assert validate_error_response(invalid) == False
    print("✓ Invalid responses fail validation")


def test_convenience_functions():
    """Test convenience error functions."""
    print("\nTesting convenience functions...")
    
    # Invalid input error
    response = invalid_input_error("Invalid email format", "email")
    assert response["error"]["code"] == ErrorCode.INVALID_INPUT.value
    assert response["error"]["details"]["field"] == "email"
    print("✓ invalid_input_error works")
    
    # Not found error
    response = not_found_error("User", "12345")
    assert response["error"]["code"] == ErrorCode.NOT_FOUND.value
    assert response["error"]["details"]["resource_id"] == "12345"
    print("✓ not_found_error works")
    
    # Timeout error
    response = timeout_error("database_query", 30)
    assert response["error"]["code"] == ErrorCode.TIMEOUT.value
    assert response["error"]["details"]["timeout_seconds"] == 30
    print("✓ timeout_error works")
    
    # Validation error
    errors = [{"field": "email", "error": "invalid format"}]
    response = validation_error("Validation failed", errors)
    assert response["error"]["code"] == ErrorCode.VALIDATION_FAILED.value
    assert len(response["error"]["details"]["validation_errors"]) == 1
    print("✓ validation_error works")
    
    # Internal error
    response = internal_error()
    assert response["error"]["code"] == ErrorCode.INTERNAL_ERROR.value
    print("✓ internal_error works")


def test_error_response_structure():
    """Test complete error response structure."""
    print("\nTesting error response structure...")
    
    response = create_error_response(
        ErrorCode.EXTERNAL_API_ERROR,
        "Failed to connect to external service",
        {
            "service": "payment_gateway",
            "endpoint": "/api/v1/charge",
            "retry_after": 60
        }
    )
    
    print(f"\nSample error response:")
    import json
    print(json.dumps(response, indent=2))
    
    assert validate_error_response(response)
    print("\n✓ Complete error response structure is valid")


if __name__ == "__main__":
    print("=" * 60)
    print("Error Response System Tests")
    print("=" * 60)
    
    test_create_error_response()
    test_error_codes()
    test_validate_error_response()
    test_convenience_functions()
    test_error_response_structure()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
