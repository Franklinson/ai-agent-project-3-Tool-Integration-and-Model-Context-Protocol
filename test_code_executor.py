from code_executor import CodeExecutor


def test_code_executor():
    executor = CodeExecutor(default_timeout=30)
    
    # Test 1: Valid Python code
    print("Test 1: Valid Python code")
    valid_code = """
print("Hello, World!")
result = 2 + 2
print(f"2 + 2 = {result}")
"""
    result = executor.execute(valid_code)
    print(f"Success: {result['success']}")
    print(f"Output: {result['output']}")
    print(f"Error: {result['error']}\n")
    
    # Test 2: Invalid syntax
    print("Test 2: Invalid syntax")
    invalid_syntax = """
print("Missing closing parenthesis"
"""
    result = executor.execute(invalid_syntax)
    print(f"Success: {result['success']}")
    print(f"Error Type: {result['error_type']}")
    print(f"Error: {result['error']}\n")
    
    # Test 3: Code that raises runtime error
    print("Test 3: Runtime error")
    runtime_error_code = """
x = 10
y = 0
print(x / y)
"""
    result = executor.execute(runtime_error_code)
    print(f"Success: {result['success']}")
    print(f"Error Type: {result['error_type']}")
    print(f"Error: {result['error']}\n")
    
    # Test 4: Code that times out
    print("Test 4: Timeout (5 second limit)")
    timeout_code = """
import time
time.sleep(10)
print("This won't print")
"""
    result = executor.execute(timeout_code, timeout=5)
    print(f"Success: {result['success']}")
    print(f"Error Type: {result['error_type']}")
    print(f"Error: {result['error']}\n")


if __name__ == "__main__":
    test_code_executor()
