# Day 42: MCP Tool Discovery, Invocation & Error Handling

## Overview

Complete MCP tool system with discovery, invocation, and comprehensive error handling:
- **Tool Discovery**: Query and discover available tools from MCP servers
- **Tool Invocation**: Execute tools with parameter validation and timeout handling
- **Error Handling**: Comprehensive error parsing, categorization, and recovery

## Features

### Tool Discovery
- Query available tools from MCP servers
- Parse and structure tool metadata
- Filter tools by category, name, or criteria
- Cache tool information for performance

### Tool Invocation
- Synchronous tool execution
- Parameter validation (required fields, types)
- Response parsing
- Timeout handling

### Error Handling
- Parse MCP JSON-RPC errors
- Categorize errors by type
- Determine recovery strategies
- Error logging and statistics
- Handle all MCP error codes

### MCP Compliance
- Uses JSON-RPC 2.0 message format
- Follows MCP specification

## Quick Start

### Discovery
```python
from tool_discovery import ToolDiscoveryClient

client = ToolDiscoveryClient()
tools = await client.discover_tools()
metadata = await client.get_tool_metadata("query_database")
db_tools = client.filter_tools({"category": "database"})
```

### Invocation
```python
from tool_invocation import ToolInvocationClient

client = ToolInvocationClient(timeout=5.0)
result = await client.invoke_tool("query_database", {
    "query": "SELECT * FROM users"
})

if result.success:
    print(result.content)
else:
    print(result.error)
```

### Error Handling
```python
from error_handling import ErrorHandler

handler = ErrorHandler(enable_logging=True)
error = handler.parse_error(response)
should_retry, action = handler.handle_error(error)

if should_retry:
    # Retry with backoff
else:
    # Handle non-recoverable error
```

### Complete Integration
```python
from tool_invocation import ToolInvocationClient
from error_handling import ErrorHandler

client = ToolInvocationClient()
handler = ErrorHandler()

result = await client.invoke_tool("query_database", params)

if not result.success:
    error = handler.parse_error(error_response)
    should_retry, action = handler.handle_error(error)
    
    if should_retry:
        # Implement retry logic
        pass
```

## API Reference

### ToolDiscoveryClient
- `discover_tools(server_id)` - Discover all tools
- `get_tool_metadata(tool_name, server_id)` - Get tool metadata
- `filter_tools(criteria, server_id)` - Filter tools
- `clear_cache(server_id)` - Clear cache

### ToolInvocationClient
- `invoke_tool(tool_name, params)` - Invoke tool
  - Returns: InvocationResult(success, content, error, execution_time)

### ErrorHandler
- `parse_error(response)` - Parse MCP error
- `categorize_error(exception)` - Categorize exception
- `handle_error(error)` - Get recovery action
- `get_error_stats()` - Get statistics
- `clear_history()` - Clear error history

## Error Handling

### Error Categories
- PARSE_ERROR (-32700)
- INVALID_REQUEST (-32600)
- METHOD_NOT_FOUND (-32601)
- INVALID_PARAMS (-32602)
- INTERNAL_ERROR (-32603)
- SERVER_ERROR (-32000 to -32099)
- TIMEOUT_ERROR
- NETWORK_ERROR
- VALIDATION_ERROR

### Recovery Actions
| Error | Retry | Action |
|-------|-------|--------|
| METHOD_NOT_FOUND | No | verify_tool_name |
| INVALID_PARAMS | No | validate_parameters |
| INTERNAL_ERROR | Yes | retry_with_backoff |
| TIMEOUT_ERROR | Yes | retry_with_longer_timeout |
| SERVER_ERROR | Yes | manual_intervention |

### Example
```python
error = handler.parse_error(response)
should_retry, action = handler.handle_error(error)

if should_retry:
    await asyncio.sleep(2 ** retry_count)  # Exponential backoff
    result = await client.invoke_tool(tool_name, params)
```

## Testing

Run tests:
```bash
source venv/bin/activate
cd day_42

# Test discovery
python test_tool_discovery.py

# Test invocation
python test_tool_invocation.py

# Test error handling
python test_error_handling.py

# Run integration examples
python integration_example.py
python error_integration.py
```

**Test Results:**
- Discovery: 7/7 tests passed ✓
- Invocation: 10/10 tests + 4 scenarios passed ✓
- Error Handling: 10/10 tests + 5 scenarios passed ✓
- **Total: 32 tests, 100% pass rate**

## Architecture

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Tool Discovery  │      │  Tool Invocation │      │  Error Handling  │
│     Client       │      │      Client      │      │     Handler      │
└────────┬─────────┘      └────────┬─────────┘      └────────┬─────────┘
         │                         │                         │
         │    MCP Protocol (JSON-RPC 2.0)                   │
         │                         │                         │
         └────────┬────────────────┴─────────────────────────┘
                  │
         ┌────────▼────────┐
         │   MCP Server    │
         │                 │
         │  ┌───────────┐  │
         │  │   Tools   │  │
         │  └───────────┘  │
         └─────────────────┘
```

## Data Structures

### ToolMetadata
```python
@dataclass
class ToolMetadata:
    name: str
    description: str
    inputSchema: Dict[str, Any]
    category: Optional[str] = None
    version: Optional[str] = None
```

### InvocationResult
```python
@dataclass
class InvocationResult:
    success: bool
    content: Any
    error: Optional[str] = None
    execution_time: float = 0.0
```

### MCPError
```python
@dataclass
class MCPError:
    code: int
    message: str
    category: ErrorCategory
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    recoverable: bool = False
```

## Files

- `tool_discovery.py` - Tool discovery implementation
- `tool_invocation.py` - Tool invocation implementation
- `error_handling.py` - Error handling implementation
- `test_tool_discovery.py` - Discovery tests
- `test_tool_invocation.py` - Invocation tests
- `test_error_handling.py` - Error handling tests
- `integration_example.py` - Discovery + Invocation demo
- `error_integration.py` - Invocation + Error handling demo
- `demo.py` - Discovery demo
- `README.md` - This file
- `TOOL_INVOCATION.md` - Invocation documentation
- `ERROR_HANDLING.md` - Error handling documentation
- `QUICK_REFERENCE.md` - Quick reference guide
- `SUMMARY.md` - Implementation summary

## Documentation

- [Tool Discovery](README.md#tool-discovery)
- [Tool Invocation](TOOL_INVOCATION.md)
- [Error Handling](ERROR_HANDLING.md)
- [Quick Reference](QUICK_REFERENCE.md)
- [Integration Examples](integration_example.py)
- [MCP Specification](https://spec.modelcontextprotocol.io/)

## Future Enhancements

- Real transport layer (stdio, HTTP+SSE)
- Async batch invocations
- Retry logic with exponential backoff
- Cache TTL and auto-refresh
- Progress notifications
- Tool versioning
- Multiple server management
