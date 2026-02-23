"""
Resource Limiter Implementation Demo
Shows how CPU, memory, and time limits are enforced
"""

print("=" * 70)
print("RESOURCE LIMITER IMPLEMENTATION")
print("=" * 70)

print("\n1. RESOURCE LIMITER CLASS")
print("-" * 70)
print("""
ResourceLimiter provides static methods for:
- set_cpu_limit(container, cpu_quota): Limit CPU usage (0.0-1.0)
- set_memory_limit(container, limit_mb): Limit memory in MB
- monitor_resources(container): Get current CPU/memory usage
- enforce_time_limit(func, timeout, *args): Execute with timeout
""")

print("\n2. CPU LIMIT IMPLEMENTATION")
print("-" * 70)
print("""
Uses Docker's cpu_quota and cpu_period:
- cpu_quota: Amount of CPU time in microseconds
- cpu_period: Period length (100000 microseconds = 100ms)
- Example: 50% CPU = cpu_quota=50000, cpu_period=100000

Container creation with CPU limit:
  cpu_quota=int(0.5 * 100000)  # 50% CPU
  cpu_period=100000
""")

print("\n3. MEMORY LIMIT IMPLEMENTATION")
print("-" * 70)
print("""
Uses Docker's mem_limit parameter:
- Specified in bytes, KB, MB, or GB
- Example: mem_limit="128m" for 128MB
- Container killed if exceeds limit

Container creation with memory limit:
  mem_limit="128m"
  
Dynamic update:
  container.update(mem_limit="256m")
""")

print("\n4. TIME LIMIT IMPLEMENTATION")
print("-" * 70)
print("""
Two approaches:
1. Docker exec_run timeout parameter (used in sandbox)
2. Signal-based timeout (in ResourceLimiter)

Sandbox implementation:
  container.exec_run(cmd, timeout=30)
  
Raises exception if execution exceeds timeout.
""")

print("\n5. RESOURCE MONITORING")
print("-" * 70)
print("""
Uses container.stats() to get real-time metrics:

CPU calculation:
  cpu_delta = current_usage - previous_usage
  system_delta = current_system - previous_system
  cpu_percent = (cpu_delta / system_delta) * 100

Memory calculation:
  memory_usage = stats['memory_stats']['usage']
  memory_limit = stats['memory_stats']['limit']
  memory_percent = (usage / limit) * 100
""")

print("\n6. INTEGRATION WITH SANDBOX")
print("-" * 70)
print("""
SandboxExecutor now accepts resource parameters:

  sandbox = SandboxExecutor(
      memory_limit_mb=128,  # 128MB memory
      cpu_limit=0.5,        # 50% CPU
      timeout=30            # 30 second timeout
  )

Methods added:
- get_resource_usage(): Monitor current usage
- update_limits(memory_mb, cpu_limit): Change limits dynamically
""")

print("\n7. EXAMPLE USAGE")
print("-" * 70)
print("""
# Create sandbox with limits
with SandboxExecutor(memory_limit_mb=64, cpu_limit=0.5, timeout=10) as sandbox:
    # Execute code
    result = sandbox.execute_in_container("print('Hello')")
    
    # Monitor resources
    usage = sandbox.get_resource_usage()
    print(f"CPU: {usage['cpu_percent']}%")
    print(f"Memory: {usage['memory_mb']} MB")
    
    # Update limits
    sandbox.update_limits(memory_mb=128, cpu_limit=0.8)
""")

print("\n8. TEST SCENARIOS")
print("-" * 70)
print("""
Test 1: Memory limit enforcement
  → Try to allocate more than limit
  → Expect MemoryError or container kill

Test 2: CPU limit enforcement
  → Run CPU-intensive task
  → Verify CPU usage stays within limit

Test 3: Time limit enforcement
  → Run code that sleeps longer than timeout
  → Expect timeout error

Test 4: Dynamic limit updates
  → Change limits on running container
  → Verify new limits applied

Test 5: Resource monitoring
  → Execute code and monitor usage
  → Verify accurate CPU/memory reporting
""")

print("\n9. FILES CREATED")
print("-" * 70)
print("""
✓ resource_limiter.py - ResourceLimiter class
✓ sandbox.py - Updated with resource limit integration
✓ test_resource_limits.py - Comprehensive test suite
""")

print("\n10. TO RUN TESTS")
print("-" * 70)
print("""
1. Start Docker Desktop
2. Activate virtual environment: source venv/bin/activate
3. Run: python3 test_resource_limits.py
""")

print("\n" + "=" * 70)
print("Resource limiter implementation complete!")
print("=" * 70)
