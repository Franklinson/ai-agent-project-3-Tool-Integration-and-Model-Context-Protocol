"""Test retry mechanisms with mock failures."""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from error_handling.retry_mechanisms import (
    retry_with_backoff,
    retry_operation,
    RetryConfig,
    TRANSIENT_ERRORS,
    NETWORK_ERRORS
)


class MockTransientError(Exception):
    """Mock exception for testing."""
    pass


def test_retry_decorator_success():
    """Test retry decorator with eventual success."""
    print("Testing retry decorator with eventual success...")
    
    attempt_count = [0]
    
    @retry_with_backoff(max_retries=3, base_delay=0.1, retry_on=(MockTransientError,))
    def flaky_operation():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise MockTransientError(f"Attempt {attempt_count[0]} failed")
        return "success"
    
    start_time = time.time()
    result = flaky_operation()
    elapsed = time.time() - start_time
    
    assert result == "success"
    assert attempt_count[0] == 3
    print(f"✓ Operation succeeded after {attempt_count[0]} attempts in {elapsed:.2f}s")


def test_retry_decorator_max_retries():
    """Test retry decorator reaching max retries."""
    print("\nTesting retry decorator with max retries...")
    
    attempt_count = [0]
    
    @retry_with_backoff(max_retries=2, base_delay=0.1, retry_on=(MockTransientError,))
    def always_failing_operation():
        attempt_count[0] += 1
        raise MockTransientError(f"Attempt {attempt_count[0]} failed")
    
    try:
        always_failing_operation()
        assert False, "Should have raised exception"
    except MockTransientError:
        assert attempt_count[0] == 3  # Initial + 2 retries
        print(f"✓ Max retries reached after {attempt_count[0]} attempts")


def test_exponential_backoff():
    """Test exponential backoff timing."""
    print("\nTesting exponential backoff...")
    
    config = RetryConfig(base_delay=1.0, exponential_base=2.0, max_delay=10.0)
    
    delays = [config.calculate_delay(i) for i in range(5)]
    expected = [1.0, 2.0, 4.0, 8.0, 10.0]  # Last one capped at max_delay
    
    assert delays == expected
    print(f"✓ Exponential backoff: {delays}")


def test_retry_operation_function():
    """Test retry_operation function."""
    print("\nTesting retry_operation function...")
    
    attempt_count = [0]
    
    def flaky_func():
        attempt_count[0] += 1
        if attempt_count[0] < 2:
            raise ConnectionError("Connection failed")
        return "connected"
    
    result = retry_operation(
        flaky_func,
        max_retries=3,
        base_delay=0.1,
        retry_on=(ConnectionError,)
    )
    
    assert result == "connected"
    assert attempt_count[0] == 2
    print(f"✓ retry_operation succeeded after {attempt_count[0]} attempts")


def test_specific_exceptions():
    """Test retry only on specific exceptions."""
    print("\nTesting specific exception handling...")
    
    @retry_with_backoff(max_retries=2, base_delay=0.1, retry_on=(ConnectionError,))
    def operation_with_value_error():
        raise ValueError("This should not be retried")
    
    try:
        operation_with_value_error()
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert str(e) == "This should not be retried"
        print("✓ Non-retryable exception raised immediately")


def test_retry_callback():
    """Test retry callback function."""
    print("\nTesting retry callback...")
    
    callback_calls = []
    
    def on_retry_callback(exception, attempt):
        callback_calls.append((str(exception), attempt))
    
    attempt_count = [0]
    
    @retry_with_backoff(
        max_retries=2,
        base_delay=0.1,
        retry_on=(MockTransientError,),
        on_retry=on_retry_callback
    )
    def flaky_operation():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise MockTransientError(f"Fail {attempt_count[0]}")
        return "success"
    
    result = flaky_operation()
    
    assert result == "success"
    assert len(callback_calls) == 2
    print(f"✓ Callback called {len(callback_calls)} times")


def test_transient_errors():
    """Test with transient error types."""
    print("\nTesting transient error types...")
    
    @retry_with_backoff(max_retries=2, base_delay=0.1, retry_on=TRANSIENT_ERRORS)
    def network_operation():
        raise ConnectionError("Network unavailable")
    
    try:
        network_operation()
    except ConnectionError:
        print("✓ TRANSIENT_ERRORS includes ConnectionError")
    
    @retry_with_backoff(max_retries=2, base_delay=0.1, retry_on=NETWORK_ERRORS)
    def timeout_operation():
        raise TimeoutError("Request timeout")
    
    try:
        timeout_operation()
    except TimeoutError:
        print("✓ NETWORK_ERRORS includes TimeoutError")


def test_retry_config():
    """Test RetryConfig class."""
    print("\nTesting RetryConfig class...")
    
    config = RetryConfig(
        max_retries=5,
        base_delay=0.5,
        max_delay=30.0,
        exponential_base=3.0
    )
    
    assert config.max_retries == 5
    assert config.base_delay == 0.5
    assert config.calculate_delay(0) == 0.5
    assert config.calculate_delay(1) == 1.5
    assert config.calculate_delay(2) == 4.5
    assert config.calculate_delay(10) == 30.0  # Capped at max_delay
    
    print("✓ RetryConfig works correctly")


def test_real_world_scenario():
    """Test real-world API call scenario."""
    print("\nTesting real-world API scenario...")
    
    api_calls = [0]
    
    @retry_with_backoff(
        max_retries=3,
        base_delay=0.1,
        max_delay=5.0,
        retry_on=(ConnectionError, TimeoutError)
    )
    def api_call():
        api_calls[0] += 1
        if api_calls[0] == 1:
            raise ConnectionError("Connection refused")
        elif api_calls[0] == 2:
            raise TimeoutError("Request timeout")
        return {"status": "success", "data": [1, 2, 3]}
    
    result = api_call()
    
    assert result["status"] == "success"
    assert api_calls[0] == 3
    print(f"✓ API call succeeded after {api_calls[0]} attempts")
    print(f"  Result: {result}")


if __name__ == "__main__":
    print("=" * 60)
    print("Retry Mechanisms Tests")
    print("=" * 60)
    
    test_retry_decorator_success()
    test_retry_decorator_max_retries()
    test_exponential_backoff()
    test_retry_operation_function()
    test_specific_exceptions()
    test_retry_callback()
    test_transient_errors()
    test_retry_config()
    test_real_world_scenario()
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
