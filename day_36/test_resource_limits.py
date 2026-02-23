from sandbox import SandboxExecutor
import time


def test_resource_limits():
    print("=" * 60)
    print("RESOURCE LIMIT TESTS")
    print("=" * 60)
    
    # Test 1: Memory limit enforcement
    print("\nTest 1: Memory limit (64MB)")
    print("-" * 60)
    with SandboxExecutor(memory_limit_mb=64, cpu_limit=0.5, timeout=10) as sandbox:
        # Try to allocate more memory than limit
        code = """
import sys
try:
    # Try to allocate 100MB
    data = bytearray(100 * 1024 * 1024)
    print('Allocated 100MB')
except MemoryError:
    print('MemoryError: Allocation failed (limit enforced)')
"""
        result = sandbox.execute_in_container(code)
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        
        # Monitor resources
        usage = sandbox.get_resource_usage()
        if usage['success']:
            print(f"Memory usage: {usage['memory_mb']} MB ({usage['memory_percent']}%)")
    
    # Test 2: CPU limit enforcement
    print("\nTest 2: CPU limit (50%)")
    print("-" * 60)
    with SandboxExecutor(memory_limit_mb=128, cpu_limit=0.5, timeout=10) as sandbox:
        code = """
import time
start = time.time()
# CPU intensive task
for i in range(10000000):
    _ = i * i
elapsed = time.time() - start
print(f'Task completed in {elapsed:.2f} seconds')
"""
        result = sandbox.execute_in_container(code)
        print(f"Success: {result['success']}")
        print(f"Output: {result['output']}")
        
        # Monitor resources
        usage = sandbox.get_resource_usage()
        if usage['success']:
            print(f"CPU usage: {usage['cpu_percent']}%")
    
    # Test 3: Time limit enforcement
    print("\nTest 3: Time limit (5 seconds)")
    print("-" * 60)
    with SandboxExecutor(memory_limit_mb=128, cpu_limit=1.0, timeout=5) as sandbox:
        code = """
import time
print('Starting long task...')
time.sleep(10)
print('This should not print')
"""
        result = sandbox.execute_in_container(code)
        print(f"Success: {result['success']}")
        print(f"Error Type: {result['error_type']}")
        print(f"Error: {result['error'][:100] if result['error'] else None}")
    
    # Test 4: Dynamic limit updates
    print("\nTest 4: Dynamic limit updates")
    print("-" * 60)
    with SandboxExecutor(memory_limit_mb=128, cpu_limit=0.5) as sandbox:
        print("Initial limits: 128MB memory, 50% CPU")
        
        # Update limits
        update_result = sandbox.update_limits(memory_mb=256, cpu_limit=0.8)
        print(f"Update success: {update_result['success']}")
        print("New limits: 256MB memory, 80% CPU")
        
        code = "print('Running with updated limits')"
        result = sandbox.execute_in_container(code)
        print(f"Execution: {result['output'].strip()}")
    
    # Test 5: Resource monitoring
    print("\nTest 5: Resource monitoring")
    print("-" * 60)
    with SandboxExecutor(memory_limit_mb=128, cpu_limit=1.0) as sandbox:
        code = """
# Create some data
data = [i for i in range(100000)]
print(f'Created list with {len(data)} elements')
"""
        result = sandbox.execute_in_container(code)
        print(f"Output: {result['output'].strip()}")
        
        usage = sandbox.get_resource_usage()
        if usage['success']:
            print(f"CPU: {usage['cpu_percent']}%")
            print(f"Memory: {usage['memory_mb']} MB ({usage['memory_percent']}%)")
        else:
            print(f"Monitoring error: {usage['error']}")
    
    print("\n" + "=" * 60)
    print("All resource limit tests completed")
    print("=" * 60)


if __name__ == "__main__":
    test_resource_limits()
