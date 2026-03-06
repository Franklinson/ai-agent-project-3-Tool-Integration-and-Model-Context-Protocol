# Quick Start Guide - MCP Server

## Installation

No external dependencies required! Uses only Python standard library.

## Basic Usage

### 1. Start the Server

```python
from mcp_server import MCPServer

server = MCPServer("my-server", "1.0.0")
server.start()
```

### 2. Register a Tool

```python
server.handle_request({
    "id": 1,
    "method": "tools/register",
    "params": {
        "tool": {
            "name": "calculator",
            "description": "Perform calculations",
            "parameters": {
                "expression": {"type": "string", "required": True}
            }
        }
    }
})
```

### 3. List Tools

```python
response = server.handle_request({
    "id": 2,
    "method": "tools/list",
    "params": {}
})
print(response["result"]["data"]["tools"])
```

### 4. Invoke a Tool

```python
response = server.handle_request({
    "id": 3,
    "method": "tools/invoke",
    "params": {
        "name": "calculator",
        "arguments": {"expression": "2+2"}
    }
})
print(response["result"]["data"])
```

### 5. Stop the Server

```python
server.stop()
```

## Complete Example

```python
from mcp_server import MCPServer

# Initialize
server = MCPServer("demo", "1.0.0")
server.start()

# Register tool
server.handle_request({
    "method": "tools/register",
    "params": {
        "tool": {
            "name": "weather",
            "description": "Get weather",
            "parameters": {
                "location": {"type": "string", "required": True}
            }
        }
    }
})

# Invoke tool
response = server.handle_request({
    "method": "tools/invoke",
    "params": {
        "name": "weather",
        "arguments": {"location": "NYC"}
    }
})

print(response)
server.stop()
```

## Running Tests

```bash
# All tests
python day_43/test_mcp_server.py
python day_43/test_tool_registry.py
python day_43/test_request_handler.py

# Demos
python day_43/integration_example.py
python day_43/request_handler_demo.py
```

## Available Methods

| Method | Purpose |
|--------|---------|
| `ping` | Health check |
| `status` | Server status |
| `tools/register` | Register tool |
| `tools/list` | List tools |
| `tools/invoke` | Invoke tool |
| `tools/remove` | Remove tool |

## Response Format

All responses follow JSON-RPC 2.0:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "status": "success",
    "data": {...},
    "timestamp": "2026-03-06T15:53:01.069353"
  }
}
```

## Error Handling

Errors include proper codes and messages:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "status": "error",
    "data": {
      "error": {
        "code": -32602,
        "message": "Tool 'xyz' not found"
      }
    }
  }
}
```

## Next Steps

1. Review [README.md](README.md) for detailed documentation
2. Check [API_REFERENCE.md](API_REFERENCE.md) for API details
3. Run demos to see it in action
4. Extend with your own tools!
