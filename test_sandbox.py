from sandbox import SandboxExecutor


def test_sandbox():
    print("Test 1: Basic code execution in container")
    with SandboxExecutor() as sandbox:
        code = "print('Hello from Docker container!')"
        result = sandbox.execute_in_container(code)
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print(f"Error: {result['error']}\n")
    
    print("Test 2: Code with calculations")
    with SandboxExecutor() as sandbox:
        code = "import math; print(f'Pi = {math.pi}')"
        result = sandbox.execute_in_container(code)
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}\n")
    
    print("Test 3: Runtime error in container")
    with SandboxExecutor() as sandbox:
        code = "x = 1 / 0"
        result = sandbox.execute_in_container(code)
        print(f"Success: {result['success']}")
        print(f"Error Type: {result['error_type']}")
        print(f"Error: {result['error']}\n")
    
    print("Test 4: Network isolation test")
    with SandboxExecutor() as sandbox:
        code = "import socket; socket.create_connection(('google.com', 80), timeout=2)"
        result = sandbox.execute_in_container(code)
        print(f"Success: {result['success']}")
        print(f"Error Type: {result['error_type']}")
        print(f"Error (network should be blocked): {result['error'][:100]}...\n")
    
    print("Test 5: Multiple executions in same container")
    with SandboxExecutor() as sandbox:
        result1 = sandbox.execute_in_container("print('First execution')")
        result2 = sandbox.execute_in_container("print('Second execution')")
        print(f"First: {result1['output'].strip()}")
        print(f"Second: {result2['output'].strip()}\n")
    
    print("All tests completed. Containers cleaned up automatically.")


if __name__ == "__main__":
    test_sandbox()
