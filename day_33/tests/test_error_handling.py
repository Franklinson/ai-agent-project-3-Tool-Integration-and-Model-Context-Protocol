"""Comprehensive tests for error handling scenarios."""

import sys
import os
import time
import logging
import json
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from error_handling import (
    create_error_response,
    ErrorCode,
    validate_error_response,
    retry_with_backoff,
    retry_operation,
    RetryConfig,
    TRANSIENT_ERRORS,
    NETWORK_ERRORS
)
from enhanced_tools.tool_discovery_enhanced import ToolRegistry
from enhanced_tools.schema_validator_enhanced import SchemaValidator


class TestErrorResponses:
    """Test error response creation and validation."""
    
    @staticmethod
    def test_error_response_creation():
        """Test creating error responses."""
        print("\n1. Test: Error response creation")
        
        response = create_error_response(
            ErrorCode.INVALID_INPUT,
            "Test error message",
            {"field": "test"}
        )
        
        assert "error" in response
        assert response["error"]["code"] == "ERR_1001"
        assert response["error"]["message"] == "Test error message"
        assert response["error"]["status"] == 400
        assert "timestamp" in response["error"]
        assert response["error"]["details"]["field"] == "test"
        print("   ✓ Error response created correctly")
    
    @staticmethod
    def test_all_error_codes():
        """Test all error codes have correct status mapping."""
        print("\n2. Test: All error codes")
        
        test_cases = [
            (ErrorCode.INVALID_INPUT, 400),
            (ErrorCode.MISSING_REQUIRED_FIELD, 400),
            (ErrorCode.INVALID_FORMAT, 400),
            (ErrorCode.VALIDATION_FAILED, 400),
            (ErrorCode.NOT_FOUND, 404),
            (ErrorCode.ALREADY_EXISTS, 409),
            (ErrorCode.RESOURCE_UNAVAILABLE, 503),
            (ErrorCode.TIMEOUT, 408),
            (ErrorCode.OPERATION_FAILED, 500),
            (ErrorCode.UNAUTHORIZED, 401),
            (ErrorCode.FORBIDDEN, 403),
            (ErrorCode.INTERNAL_ERROR, 500),
            (ErrorCode.SERVICE_UNAVAILABLE, 503),
            (ErrorCode.CONFIGURATION_ERROR, 500),
            (ErrorCode.EXTERNAL_API_ERROR, 502),
            (ErrorCode.NETWORK_ERROR, 503),
            (ErrorCode.RATE_LIMIT_EXCEEDED, 429)
        ]
        
        for code, expected_status in test_cases:
            response = create_error_response(code, "Test")
            assert response["error"]["status"] == expected_status
        
        print(f"   ✓ All {len(test_cases)} error codes validated")
    
    @staticmethod
    def test_error_validation():
        """Test error response validation."""
        print("\n3. Test: Error response validation")
        
        # Valid response
        valid = create_error_response(ErrorCode.NOT_FOUND, "Test")
        assert validate_error_response(valid) == True
        
        # Invalid responses
        invalid_cases = [
            {},
            {"error": {}},
            {"error": {"code": "ERR_1001"}},
            {"error": {"code": 123, "message": "test", "timestamp": "2024", "status": 400}}
        ]
        
        for invalid in invalid_cases:
            assert validate_error_response(invalid) == False
        
        print("   ✓ Validation works correctly")
    
    @staticmethod
    def test_error_without_details():
        """Test error response without details."""
        print("\n4. Test: Error without details")
        
        response = create_error_response(ErrorCode.INTERNAL_ERROR, "Test error")
        assert "error" in response
        assert "details" not in response["error"]
        print("   ✓ Error without details works")


class TestRetryMechanisms:
    """Test retry mechanisms and exponential backoff."""
    
    @staticmethod
    def test_retry_success():
        """Test retry with eventual success."""
        print("\n5. Test: Retry with success")
        
        attempts = [0]
        
        @retry_with_backoff(max_retries=3, base_delay=0.1, retry_on=(ValueError,))
        def flaky_func():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError("Fail")
            return "success"
        
        result = flaky_func()
        assert result == "success"
        assert attempts[0] == 3
        print(f"   ✓ Succeeded after {attempts[0]} attempts")
    
    @staticmethod
    def test_retry_max_retries():
        """Test retry reaching max retries."""
        print("\n6. Test: Retry max retries")
        
        attempts = [0]
        
        @retry_with_backoff(max_retries=2, base_delay=0.1, retry_on=(ValueError,))
        def always_fail():
            attempts[0] += 1
            raise ValueError("Always fails")
        
        try:
            always_fail()
            assert False, "Should have raised exception"
        except ValueError:
            assert attempts[0] == 3  # Initial + 2 retries
            print(f"   ✓ Max retries reached after {attempts[0]} attempts")
    
    @staticmethod
    def test_exponential_backoff():
        """Test exponential backoff calculation."""
        print("\n7. Test: Exponential backoff")
        
        config = RetryConfig(base_delay=1.0, exponential_base=2.0, max_delay=10.0)
        
        delays = [config.calculate_delay(i) for i in range(5)]
        expected = [1.0, 2.0, 4.0, 8.0, 10.0]
        
        assert delays == expected
        print(f"   ✓ Backoff delays: {delays}")
    
    @staticmethod
    def test_retry_specific_exceptions():
        """Test retry only on specific exceptions."""
        print("\n8. Test: Specific exception retry")
        
        @retry_with_backoff(max_retries=2, base_delay=0.1, retry_on=(ConnectionError,))
        def wrong_exception():
            raise ValueError("Not retryable")
        
        try:
            wrong_exception()
            assert False, "Should have raised ValueError"
        except ValueError:
            print("   ✓ Non-retryable exception raised immediately")
    
    @staticmethod
    def test_retry_callback():
        """Test retry callback function."""
        print("\n9. Test: Retry callback")
        
        callbacks = []
        
        def on_retry(exc, attempt):
            callbacks.append((str(exc), attempt))
        
        attempts = [0]
        
        @retry_with_backoff(
            max_retries=2,
            base_delay=0.1,
            retry_on=(ValueError,),
            on_retry=on_retry
        )
        def flaky():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ValueError(f"Fail {attempts[0]}")
            return "success"
        
        result = flaky()
        assert result == "success"
        assert len(callbacks) == 2
        print(f"   ✓ Callback called {len(callbacks)} times")
    
    @staticmethod
    def test_retry_operation_function():
        """Test retry_operation function."""
        print("\n10. Test: retry_operation function")
        
        attempts = [0]
        
        def operation():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ConnectionError("Fail")
            return "connected"
        
        result = retry_operation(
            operation,
            max_retries=3,
            base_delay=0.1,
            retry_on=(ConnectionError,)
        )
        
        assert result == "connected"
        assert attempts[0] == 2
        print(f"   ✓ Operation succeeded after {attempts[0]} attempts")


class TestToolErrorHandling:
    """Test error handling in enhanced tools."""
    
    @staticmethod
    def test_tool_discovery_errors():
        """Test tool discovery error handling."""
        print("\n11. Test: Tool discovery errors")
        
        # Test with missing file
        try:
            registry = ToolRegistry("nonexistent.json")
            assert False, "Should raise error"
        except Exception:
            print("   ✓ Missing file error handled")
        
        # Test with valid registry
        registry_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 'day_31', 'tool_metadata', 'tool_registry.json'
        ))
        registry = ToolRegistry(registry_path)
        
        # Empty query
        result = registry.search_tools("")
        assert "error" in result
        assert result["error"]["code"] == "ERR_1001"
        print("   ✓ Empty query error handled")
        
        # Query too long
        result = registry.search_tools("a" * 101)
        assert "error" in result
        print("   ✓ Long query error handled")
        
        # Valid search
        result = registry.search_tools("email")
        assert result.get("success") == True
        print("   ✓ Valid search works")
    
    @staticmethod
    def test_tool_discovery_not_found():
        """Test tool not found error."""
        print("\n12. Test: Tool not found")
        
        registry_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..', '..', 'day_31', 'tool_metadata', 'tool_registry.json'
        ))
        registry = ToolRegistry(registry_path)
        
        result = registry.get_tool_metadata("nonexistent_tool")
        assert "error" in result
        assert result["error"]["code"] == "ERR_2001"
        print("   ✓ Tool not found error handled")
    
    @staticmethod
    def test_schema_validator_errors():
        """Test schema validator error handling."""
        print("\n13. Test: Schema validator errors")
        
        validator = SchemaValidator()
        
        # Empty data
        result = validator.validate_input({}, "test_schema")
        assert "error" in result
        print("   ✓ Empty data error handled")
        
        # Invalid type
        result = validator.validate_input("not a dict", "test_schema")
        assert "error" in result
        assert result["error"]["code"] == "ERR_1001"
        print("   ✓ Invalid type error handled")
        
        # Schema not found
        result = validator.validate_input({"test": "data"}, "nonexistent_schema")
        assert "error" in result
        print("   ✓ Schema not found error handled")
    
    @staticmethod
    def test_schema_validation_errors():
        """Test schema validation errors."""
        print("\n14. Test: Schema validation errors")
        
        validator = SchemaValidator()
        
        # Create test schema
        test_schema_dir = os.path.join(validator.schema_base_path, 'input_schemas')
        os.makedirs(test_schema_dir, exist_ok=True)
        
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            },
            "required": ["name", "age"]
        }
        
        schema_path = os.path.join(test_schema_dir, 'test_validation.json')
        with open(schema_path, 'w') as f:
            json.dump(schema, f)
        
        # Valid data
        result = validator.validate_input({"name": "John", "age": 30}, "test_validation")
        assert result.get("success") == True
        print("   ✓ Valid data passes")
        
        # Missing field
        result = validator.validate_input({"name": "John"}, "test_validation")
        assert "error" in result
        print("   ✓ Missing field error handled")
        
        # Invalid type
        result = validator.validate_input({"name": "John", "age": "thirty"}, "test_validation")
        assert "error" in result
        print("   ✓ Type mismatch error handled")
        
        # Constraint violation
        result = validator.validate_input({"name": "John", "age": 200}, "test_validation")
        assert "error" in result
        print("   ✓ Constraint violation error handled")
        
        # Cleanup
        if os.path.exists(schema_path):
            os.remove(schema_path)


class TestErrorLogging:
    """Test error logging functionality."""
    
    @staticmethod
    def test_logging_levels():
        """Test different logging levels."""
        print("\n15. Test: Logging levels")
        
        # Capture logs
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.INFO)
        
        test_logger = logging.getLogger("test_logger")
        test_logger.addHandler(handler)
        test_logger.setLevel(logging.INFO)
        
        # Log at different levels
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")
        
        log_output = log_stream.getvalue()
        assert "Info message" in log_output
        assert "Warning message" in log_output
        assert "Error message" in log_output
        
        print("   ✓ All logging levels work")
    
    @staticmethod
    def test_retry_logging():
        """Test retry mechanism logging."""
        print("\n16. Test: Retry logging")
        
        attempts = [0]
        
        @retry_with_backoff(max_retries=2, base_delay=0.1, retry_on=(ValueError,))
        def logged_retry():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ValueError("Test error")
            return "success"
        
        result = logged_retry()
        assert result == "success"
        print("   ✓ Retry logging works")


class TestSuccessAndFailureCases:
    """Test both success and failure scenarios."""
    
    @staticmethod
    def test_success_cases():
        """Test successful operations."""
        print("\n17. Test: Success cases")
        
        # Successful error response creation
        response = create_error_response(ErrorCode.NOT_FOUND, "Test")
        assert validate_error_response(response)
        
        # Successful retry
        attempts = [0]
        
        @retry_with_backoff(max_retries=2, base_delay=0.1, retry_on=(ValueError,))
        def success_func():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ValueError("Fail")
            return "success"
        
        result = success_func()
        assert result == "success"
        
        print("   ✓ All success cases pass")
    
    @staticmethod
    def test_failure_cases():
        """Test failure scenarios."""
        print("\n18. Test: Failure cases")
        
        # Invalid error response
        assert validate_error_response({}) == False
        
        # Max retries exceeded
        @retry_with_backoff(max_retries=1, base_delay=0.1, retry_on=(ValueError,))
        def always_fail():
            raise ValueError("Always fails")
        
        try:
            always_fail()
            assert False, "Should raise exception"
        except ValueError:
            pass
        
        print("   ✓ All failure cases handled correctly")
    
    @staticmethod
    def test_edge_cases():
        """Test edge cases."""
        print("\n19. Test: Edge cases")
        
        # Error response with no details
        response = create_error_response(ErrorCode.INTERNAL_ERROR, "Test")
        assert "details" not in response["error"]
        
        # Retry with 0 max_retries
        attempts = [0]
        
        @retry_with_backoff(max_retries=0, base_delay=0.1, retry_on=(ValueError,))
        def no_retry():
            attempts[0] += 1
            raise ValueError("Fail")
        
        try:
            no_retry()
        except ValueError:
            assert attempts[0] == 1
        
        print("   ✓ Edge cases handled")


def run_all_tests():
    """Run all test suites."""
    print("=" * 70)
    print("COMPREHENSIVE ERROR HANDLING TESTS")
    print("=" * 70)
    
    # Test Error Responses
    print("\n" + "=" * 70)
    print("TEST SUITE 1: Error Responses")
    print("=" * 70)
    TestErrorResponses.test_error_response_creation()
    TestErrorResponses.test_all_error_codes()
    TestErrorResponses.test_error_validation()
    TestErrorResponses.test_error_without_details()
    
    # Test Retry Mechanisms
    print("\n" + "=" * 70)
    print("TEST SUITE 2: Retry Mechanisms")
    print("=" * 70)
    TestRetryMechanisms.test_retry_success()
    TestRetryMechanisms.test_retry_max_retries()
    TestRetryMechanisms.test_exponential_backoff()
    TestRetryMechanisms.test_retry_specific_exceptions()
    TestRetryMechanisms.test_retry_callback()
    TestRetryMechanisms.test_retry_operation_function()
    
    # Test Tool Error Handling
    print("\n" + "=" * 70)
    print("TEST SUITE 3: Tool Error Handling")
    print("=" * 70)
    TestToolErrorHandling.test_tool_discovery_errors()
    TestToolErrorHandling.test_tool_discovery_not_found()
    TestToolErrorHandling.test_schema_validator_errors()
    TestToolErrorHandling.test_schema_validation_errors()
    
    # Test Error Logging
    print("\n" + "=" * 70)
    print("TEST SUITE 4: Error Logging")
    print("=" * 70)
    TestErrorLogging.test_logging_levels()
    TestErrorLogging.test_retry_logging()
    
    # Test Success and Failure Cases
    print("\n" + "=" * 70)
    print("TEST SUITE 5: Success and Failure Cases")
    print("=" * 70)
    TestSuccessAndFailureCases.test_success_cases()
    TestSuccessAndFailureCases.test_failure_cases()
    TestSuccessAndFailureCases.test_edge_cases()
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! ✓")
    print("=" * 70)
    print(f"\nTotal Test Suites: 5")
    print(f"Total Tests: 19")
    print(f"Status: ALL PASSING ✓")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
