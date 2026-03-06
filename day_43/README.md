# MCP Server - Day 43

Basic MCP (Model Context Protocol) server skeleton with initialization, lifecycle management, dynamic tool registration, and request handling.

## Features

- Server initialization with configurable name and version
- Lifecycle management (start/stop)
- **Request handler with parsing, routing, and validation**
- Basic request handling with MCP message format
- Dynamic tool registration system
- Tool metadata storage and management
- **Tool invocation with parameter validation**
- JSON-RPC 2.0 compliant responses
- Comprehensive error handling
- Built-in ping and status methods

## Usage

### Basic Example

```python
from mcp_server import MCPServer

# Initialize server
server = MCPServer("my-server", "1.0.0")

# Start server
response = server.start()

# Register a tool
request = {
    "method": "tools/register",
    "params": {
        "tool": {
            "name": "calculator",
            "description": "Perform calculations",
            "parameters": {"expression": "string"}
        }
    }
}
response = server.handle_request(request)

# List tools
response = server.handle_request({"method": "tools/list", "params": {}})

# Stop server
response = server.stop()
```

### MCP Message Format

**Request Format:**
```json
{
  "method": "ping",
  "params": {}
}
```

**Response Format:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "data": {
      "message": "pong"
    },
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

## Supported Methods

### Server Methods
- `ping` - Health check, returns "pong"
- `status` - Returns server status, uptime, and tool count

### Tool Management Methods
- `tools/register` - Register a new tool with metadata
- `tools/list` - List all registered tools (via RequestHandler)
- `tools/invoke` - Invoke a tool with arguments (via RequestHandler)
- `tools/remove` - Remove a tool from registry

## Testing

Run the built-in tests:

```bash
# Test server lifecycle
python day_43/test_mcp_server.py

# Test tool registration
python day_43/test_tool_registry.py

# Test request handler
python day_43/test_request_handler.py

# Run integration examples
python day_43/integration_example.py
python day_43/request_handler_demo.py
```

## Server Lifecycle

1. **Initialization** - Create server instance with name and version
2. **Start** - Activate server and begin accepting requests
3. **Handle Requests** - Process incoming MCP-formatted requests
4. **Stop** - Gracefully shutdown server

## Implementation Details

- Uses JSON-RPC 2.0 protocol
- Timestamps all responses
- Tracks server uptime
- Validates server state before operations
- Dynamic tool registration at runtime
- Tool metadata includes registration timestamp
- Prevents duplicate tool registration
- Request handler with method routing
- Parameter validation for tool invocation
- Comprehensive error handling with JSON-RPC error codes
