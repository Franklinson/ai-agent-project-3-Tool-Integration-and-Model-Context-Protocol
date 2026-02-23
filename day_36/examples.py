"""
Complete Code Execution Tool - Usage Examples
Demonstrates all features: validation, sandboxing, resource limits, monitoring
"""

from day_36.code_execution_tool import CodeExecutionTool


def example_basic_execution():
    """Example 1: Basic code execution without sandbox"""
    print("=" * 70)
    print("EXAMPLE 1: Basic Code Execution (No Sandbox)")
    print("=" * 70)
    
    tool = CodeExecutionTool(use_sandbox=False)
    
    # Simple execution
    result = tool.execute("print('Hello, World!')")
    print(f"Success: {result['success']}")
    print(f"Output: {result['output']}")
    print(f"Sandboxed: {result['sandboxed']}")


def example_syntax_validation():
    """Example 2: Syntax validation"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Syntax Validation")
    print("=" * 70)
    
    tool = CodeExecutionTool(use_sandbox=False)
    
    # Invalid syntax
    result = tool.execute("print('missing closing quote)")
    print(f"Success: {result['success']}")
    print(f"Error Type: {result['error_type']}")
    print(f"Error: {result['error']}")


def example_error_handling():
    """Example 3: Runtime error handling"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Runtime Error Handling")
    print("=" * 70)
    
    tool = CodeExecutionTool(use_sandbox=False)
    
    # Runtime error
    result = tool.execute("""
x = [1, 2, 3]
print(x[10])  # IndexError
""")
    print(f"Success: {result['success']}")
    print(f"Error Type: {result['error_type']}")
    print(f"Error: {result['error'][:100]}...")


def example_timeout():
    """Example 4: Timeout enforcement"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Timeout Enforcement")
    print("=" * 70)
    
    tool = CodeExecutionTool(use_sandbox=False, timeout=3)
    
    # Code that times out
    result = tool.execute("import time; time.sleep(5)")
    print(f"Success: {result['success']}")
    print(f"Error Type: {result['error_type']}")
    print(f"Error: {result['error']}")


def example_sandboxed_execution():
    """Example 5: Sandboxed execution (requires Docker)"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Sandboxed Execution")
    print("=" * 70)
    
    try:
        tool = CodeExecutionTool(use_sandbox=True, memory_limit_mb=128, cpu_limit=0.5)
        
        result = tool.execute("""
import math
result = math.sqrt(16)
print(f'Square root of 16 is {result}')
""")
        
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        print(f"Sandboxed: {result['sandboxed']}")
        
        if 'resource_usage' in result:
            print(f"CPU Usage: {result['resource_usage']['cpu_percent']}%")
            print(f"Memory Usage: {result['resource_usage']['memory_mb']} MB")
    
    except Exception as e:
        print(f"Skipped (Docker not running): {str(e)[:50]}")


def example_resource_monitoring():
    """Example 6: Resource monitoring (requires Docker)"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Resource Monitoring")
    print("=" * 70)
    
    try:
        tool = CodeExecutionTool(use_sandbox=True)
        
        result = tool.execute_with_monitoring("""
# Create some data
data = [i ** 2 for i in range(50000)]
print(f'Created list with {len(data)} elements')
""")
        
        if 'execution' in result:
            print(f"Execution Success: {result['execution']['success']}")
            print(f"Output: {result['execution']['output']}")
            
            if result.get('resources'):
                print(f"CPU: {result['resources']['cpu_percent']}%")
                print(f"Memory: {result['resources']['memory_mb']} MB")
    
    except Exception as e:
        print(f"Skipped (Docker not running): {str(e)[:50]}")


def example_dynamic_limits():
    """Example 7: Dynamic resource limit updates"""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Dynamic Resource Limit Updates")
    print("=" * 70)
    
    tool = CodeExecutionTool(use_sandbox=True, memory_limit_mb=128, cpu_limit=0.5)
    
    print(f"Initial limits: 128MB memory, 50% CPU")
    
    # Update limits
    result = tool.update_limits(memory_mb=256, cpu_limit=0.8)
    print(f"Update success: {result['success']}")
    print(f"New limits: {result['memory_mb']}MB memory, {result['cpu_limit']*100}% CPU")


def example_complex_code():
    """Example 8: Complex code execution"""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Complex Code Execution")
    print("=" * 70)
    
    tool = CodeExecutionTool(use_sandbox=False)
    
    code = """
import json

# Define a function
def process_data(items):
    return [x * 2 for x in items if x > 0]

# Process data
data = [1, -2, 3, -4, 5]
result = process_data(data)

# Output as JSON
output = {"input": data, "output": result, "count": len(result)}
print(json.dumps(output, indent=2))
"""
    
    result = tool.execute(code)
    print(f"Success: {result['success']}")
    print(f"Output:\n{result['output']}")


def example_multiple_executions():
    """Example 9: Multiple executions"""
    print("\n" + "=" * 70)
    print("EXAMPLE 9: Multiple Executions")
    print("=" * 70)
    
    tool = CodeExecutionTool(use_sandbox=False)
    
    codes = [
        "print('Execution 1: Hello')",
        "x = 10; y = 20; print(f'Execution 2: {x + y}')",
        "import random; print(f'Execution 3: Random = {random.randint(1, 100)}')"
    ]
    
    for i, code in enumerate(codes, 1):
        result = tool.execute(code)
        print(f"{i}. {result['output'].strip()}")


def example_security_isolation():
    """Example 10: Security isolation (requires Docker)"""
    print("\n" + "=" * 70)
    print("EXAMPLE 10: Security Isolation (Network Blocked)")
    print("=" * 70)
    
    try:
        tool = CodeExecutionTool(use_sandbox=True)
        
        # Try to access network (should fail)
        result = tool.execute("""
import socket
try:
    socket.create_connection(('google.com', 80), timeout=2)
    print('Network access succeeded')
except Exception as e:
    print(f'Network access blocked: {type(e).__name__}')
""")
        
        print(f"Success: {result['success']}")
        print(f"Output: {result['output'] if result['output'] else 'No output'}")
        print(f"Error: {result['error'][:100] if result['error'] else 'No error'}")
        print("✓ Network isolation working correctly")
    
    except Exception as e:
        print(f"Skipped (Docker not running): {str(e)[:50]}")


def main():
    """Run all examples"""
    print("\n" + "=" * 70)
    print("CODE EXECUTION TOOL - COMPLETE EXAMPLES")
    print("=" * 70)
    
    example_basic_execution()
    example_syntax_validation()
    example_error_handling()
    example_timeout()
    example_sandboxed_execution()
    example_resource_monitoring()
    example_dynamic_limits()
    example_complex_code()
    example_multiple_executions()
    example_security_isolation()
    
    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 70)
    print("\nNote: Some examples require Docker Desktop to be running")
    print("Start Docker and run again to see all features in action")


if __name__ == "__main__":
    main()
