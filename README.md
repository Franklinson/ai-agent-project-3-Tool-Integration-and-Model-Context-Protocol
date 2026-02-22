# Code Execution Tool with Sandboxing and Resource Limits

Complete implementation of a secure code execution system with syntax validation, Docker sandboxing, and resource management.

## Quick Start

```python
from code_execution_tool import CodeExecutionTool

# Basic execution
tool = CodeExecutionTool(use_sandbox=False)
result = tool.execute("print('Hello, World!')")
print(result['output'])

# Sandboxed execution with resource limits
tool = CodeExecutionTool(
    use_sandbox=True,
    memory_limit_mb=128,
    cpu_limit=0.5,
    timeout=30
)
result = tool.execute("print('Secure execution')")
```

## Components

### 1. CodeExecutionTool (code_execution_tool.py)
Integrated tool combining all components.

**Features:**
- Unified interface for all execution modes
- Automatic syntax validation
- Optional sandboxing
- Resource monitoring
- Dynamic limit updates

**Usage:**
```python
from code_execution_tool import CodeExecutionTool

tool = CodeExecutionTool(
    use_sandbox=True,
    memory_limit_mb=128,
    cpu_limit=0.5,
    timeout=30
)

# Execute code
result = tool.execute("print('Hello')")

# Execute with monitoring
result = tool.execute_with_monitoring("data = [i for i in range(1000)]")

# Update limits
tool.update_limits(memory_mb=256, cpu_limit=0.8)
```

### 2. Code Executor (code_executor.py)
Basic code execution with syntax validation and error handling.

**Features:**
- Syntax validation using AST parsing
- Code execution via subprocess
- Error handling (syntax, runtime, timeout)
- Configurable timeout (default: 30 seconds)

**Usage:**
```python
from code_executor import CodeExecutor

executor = CodeExecutor(default_timeout=30)
result = executor.execute("print('Hello, World!')")
print(result['output'])
```

### 3. Sandbox Executor (sandbox.py)
Docker-based isolated code execution environment.

**Features:**
- Docker container isolation
- Network isolation (network_mode="none")
- Configurable memory and CPU limits
- Automatic container cleanup
- Context manager support

**Usage:**
```python
from sandbox import SandboxExecutor

with SandboxExecutor(memory_limit_mb=128, cpu_limit=0.5) as sandbox:
    result = sandbox.execute_in_container("print('Hello')")
    print(result['output'])
```

### 4. Resource Limiter (resource_limiter.py)
Resource management and monitoring for containers.

**Features:**
- CPU limit enforcement (0.0-1.0 = 0%-100%)
- Memory limit enforcement (in MB)
- Real-time resource monitoring
- Dynamic limit updates

**Usage:**
```python
from resource_limiter import ResourceLimiter

# Monitor resources
usage = ResourceLimiter.monitor_resources(container)
print(f"CPU: {usage['cpu_percent']}%")
print(f"Memory: {usage['memory_mb']} MB")

# Update limits
ResourceLimiter.set_cpu_limit(container, 0.8)  # 80% CPU
ResourceLimiter.set_memory_limit(container, 256)  # 256MB
```

## Installation

1. Install Docker Desktop
2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Security Features

### Isolation
- **Process isolation**: Code runs in separate Docker containers
- **Network isolation**: No external network access
- **Filesystem isolation**: Limited container filesystem access

### Resource Limits
- **Memory**: Configurable limit (default: 128MB)
- **CPU**: Configurable quota (default: 50%)
- **Time**: Execution timeout (default: 30 seconds)

### Error Handling
- Syntax validation before execution
- Runtime error capture
- Timeout protection
- Container cleanup on errors

## Testing

### Test Files
- `tests/test_code_execution.py` - Comprehensive integration tests
- `test_code_executor.py` - Basic execution tests
- `test_sandbox.py` - Sandbox isolation tests
- `test_resource_limits.py` - Resource limit enforcement tests

### Run Tests
```bash
# Start Docker Desktop first (for sandbox tests)
source venv/bin/activate

# Run comprehensive test suite (recommended)
python3 tests/test_code_execution.py

# Run individual component tests
python3 test_code_executor.py
python3 test_sandbox.py
python3 test_resource_limits.py
```

### Test Coverage
- ✓ Successful execution (with and without sandbox)
- ✓ Syntax error detection
- ✓ Runtime error handling
- ✓ Timeout enforcement
- ✓ Memory limit enforcement
- ✓ CPU limit enforcement
- ✓ Security isolation (network blocking)
- ✓ Resource monitoring
- ✓ Dynamic limit updates
- ✓ Multiple executions
- ✓ Complex code execution

## API Reference

### CodeExecutor

**Methods:**
- `validate_syntax(code)` - Validate Python syntax
- `execute(code, timeout=None)` - Execute code with timeout

**Result Format:**
```python
{
    "success": bool,
    "output": str,
    "error": str or None,
    "error_type": str or None
}
```

### SandboxExecutor

**Constructor:**
```python
SandboxExecutor(
    image="python:3.11-slim",
    timeout=30,
    memory_limit_mb=128,
    cpu_limit=0.5
)
```

**Methods:**
- `create_container()` - Create and start container
- `execute_in_container(code)` - Execute code in container
- `get_resource_usage()` - Get current resource usage
- `update_limits(memory_mb, cpu_limit)` - Update resource limits
- `cleanup()` - Stop and remove container

### ResourceLimiter

**Static Methods:**
- `set_cpu_limit(container, cpu_quota)` - Set CPU limit (0.0-1.0)
- `set_memory_limit(container, limit_mb)` - Set memory limit in MB
- `monitor_resources(container)` - Get CPU/memory usage

## Examples

### Example 1: Basic Execution
```python
from code_executor import CodeExecutor

executor = CodeExecutor()
result = executor.execute("print(2 + 2)")
# Output: "4\n"
```

### Example 2: Sandboxed Execution
```python
from sandbox import SandboxExecutor

with SandboxExecutor() as sandbox:
    result = sandbox.execute_in_container("import math; print(math.pi)")
    print(result['output'])
```

### Example 3: Resource Monitoring
```python
from sandbox import SandboxExecutor

with SandboxExecutor(memory_limit_mb=64, cpu_limit=0.5) as sandbox:
    sandbox.execute_in_container("data = [i for i in range(100000)]")
    usage = sandbox.get_resource_usage()
    print(f"Memory: {usage['memory_mb']} MB")
    print(f"CPU: {usage['cpu_percent']}%")
```

### Example 4: Dynamic Limits
```python
from sandbox import SandboxExecutor

with SandboxExecutor(memory_limit_mb=128) as sandbox:
    # Execute with initial limits
    sandbox.execute_in_container("print('Initial')")
    
    # Update limits
    sandbox.update_limits(memory_mb=256, cpu_limit=0.8)
    
    # Execute with new limits
    sandbox.execute_in_container("print('Updated')")
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Code Execution Tool                    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐      ┌────────────────────────┐  │
│  │  CodeExecutor    │      │   SandboxExecutor      │  │
│  │                  │      │                        │  │
│  │ - Syntax check   │      │ - Docker isolation     │  │
│  │ - Subprocess     │      │ - Network isolation    │  │
│  │ - Error handling │      │ - Resource limits      │  │
│  └──────────────────┘      └────────────────────────┘  │
│                                      │                   │
│                                      ▼                   │
│                            ┌────────────────────────┐   │
│                            │  ResourceLimiter       │   │
│                            │                        │   │
│                            │ - CPU limits           │   │
│                            │ - Memory limits        │   │
│                            │ - Resource monitoring  │   │
│                            └────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Requirements

- Python 3.11+
- Docker Desktop
- docker Python SDK (>=7.0.0)

## Files

### Core Components
- `code_execution_tool.py` - Integrated execution tool (main interface)
- `code_executor.py` - Basic code execution
- `sandbox.py` - Docker sandbox implementation
- `resource_limiter.py` - Resource management

### Tests
- `tests/test_code_execution.py` - Comprehensive integration tests
- `test_code_executor.py` - Executor tests
- `test_sandbox.py` - Sandbox tests
- `test_resource_limits.py` - Resource limit tests

### Examples & Documentation
- `examples.py` - Complete usage examples
- `demo_sandbox.py` - Sandbox demonstration
- `demo_resource_limits.py` - Resource limiter demonstration
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Notes

- Docker Desktop must be running for sandbox tests
- Default limits: 128MB memory, 50% CPU, 30s timeout
- Containers are automatically cleaned up
- Network access is blocked in sandboxed execution
