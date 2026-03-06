# MCP Server - Complete Workflow

## Request Flow Diagram

```
Client Request
     |
     v
┌─────────────────────────────────────────────┐
│         MCPServer.handle_request()          │
│  - Check if server is running               │
│  - Extract method and params                │
│  - Log request                              │
└─────────────────────────────────────────────┘
     |
     v
┌─────────────────────────────────────────────┐
│         Method Routing Decision             │
│                                             │
│  Is it a server method?                     │
│  ├─ ping → return pong                      │
│  ├─ status → return server status           │
│  ├─ tools/register → register tool          │
│  └─ tools/remove → remove tool              │
│                                             │
│  Is it a tools/* method?                    │
│  └─ Delegate to RequestHandler             │
└─────────────────────────────────────────────┘
     |
     v
┌─────────────────────────────────────────────┐
│    RequestHandler.handle_request()          │
│  - Parse request (validate format)          │
│  - Extract method, params, id               │
│  - Route to appropriate handler             │
└─────────────────────────────────────────────┘
     |
     v
┌─────────────────────────────────────────────┐
│         Method-Specific Handler             │
│                                             │
│  tools/list:                                │
│  └─ ToolRegistry.list_tools()              │
│     └─ Return all registered tools          │
│                                             │
│  tools/invoke:                              │
│  ├─ Validate tool exists                    │
│  ├─ Validate required parameters            │
│  ├─ Execute tool (simulated)                │
│  └─ Return execution result                 │
└─────────────────────────────────────────────┘
     |
     v
┌─────────────────────────────────────────────┐
│    RequestHandler.generate_response()       │
│  - Create JSON-RPC 2.0 response             │
│  - Include request ID if provided           │
│  - Add timestamp                            │
│  - Format result or error                   │
└─────────────────────────────────────────────┘
     |
     v
   Response to Client
```

## Component Interaction

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │
       │ 1. Send Request
       v
┌──────────────────────────────────────┐
│          MCPServer                   │
│  ┌────────────────────────────────┐ │
│  │  handle_request()              │ │
│  │  - Validate server state       │ │
│  │  - Route request               │ │
│  └────────┬───────────────────────┘ │
│           │                          │
│           │ 2. Delegate              │
│           v                          │
│  ┌────────────────────────────────┐ │
│  │    RequestHandler              │ │
│  │  - Parse request               │ │
│  │  - Route method                │ │
│  │  - Validate params             │ │
│  └────────┬───────────────────────┘ │
│           │                          │
│           │ 3. Access Tools          │
│           v                          │
│  ┌────────────────────────────────┐ │
│  │    ToolRegistry                │ │
│  │  - Store tools                 │ │
│  │  - Provide tool info           │ │
│  └────────┬───────────────────────┘ │
│           │                          │
│           │ 4. Return Data           │
│           v                          │
│  ┌────────────────────────────────┐ │
│  │  Generate Response             │ │
│  │  - Format JSON-RPC 2.0         │ │
│  │  - Add metadata                │ │
│  └────────────────────────────────┘ │
└──────────────┬───────────────────────┘
               │
               │ 5. Return Response
               v
        ┌──────────────┐
        │   Client     │
        └──────────────┘
```

## Lifecycle Flow

```
1. INITIALIZATION
   ├─ Create MCPServer instance
   ├─ Initialize ToolRegistry
   ├─ Initialize RequestHandler
   └─ Link components together

2. STARTUP
   ├─ Call server.start()
   ├─ Set is_running = True
   ├─ Record start_time
   └─ Return success response

3. OPERATION
   ├─ Register tools
   │  ├─ Validate tool definition
   │  ├─ Check for duplicates
   │  ├─ Store in registry
   │  └─ Add timestamp
   │
   ├─ Handle requests
   │  ├─ Parse request
   │  ├─ Route to handler
   │  ├─ Execute operation
   │  └─ Return response
   │
   └─ Manage tools
      ├─ List all tools
      ├─ Invoke tools
      └─ Remove tools

4. SHUTDOWN
   ├─ Call server.stop()
   ├─ Calculate uptime
   ├─ Set is_running = False
   └─ Return shutdown response
```

## Error Handling Flow

```
Request Received
     |
     v
┌─────────────────────┐
│  Parse Request      │
│  Valid? ────No───┐  │
│    │             │  │
│   Yes            │  │
└────┼─────────────┼──┘
     │             │
     v             v
┌─────────────┐  ┌──────────────────┐
│ Route       │  │ Return Error     │
│ Method      │  │ Code: -32600     │
│ Found?──No──┤  │ Invalid Request  │
│    │        │  └──────────────────┘
│   Yes       │
└────┼────────┘
     │
     v
┌─────────────────────┐
│ Validate Params     │
│ Valid? ────No───┐   │
│    │            │   │
│   Yes           │   │
└────┼────────────┼───┘
     │            │
     v            v
┌─────────────┐  ┌──────────────────┐
│ Execute     │  │ Return Error     │
│ Handler     │  │ Code: -32602     │
│ Success?─No─┤  │ Invalid Params   │
│    │        │  └──────────────────┘
│   Yes       │
└────┼────────┘
     │
     v
┌─────────────────────┐
│ Generate Response   │
│ Return Success      │
└─────────────────────┘
```

## Data Flow Example

### Register and Invoke Tool

```
Step 1: Register Tool
─────────────────────
Request:
{
  "method": "tools/register",
  "params": {
    "tool": {
      "name": "calculator",
      "parameters": {"expr": {"required": true}}
    }
  }
}
    ↓
Server → ToolRegistry.register_tool()
    ↓
Registry stores: {
  "calculator": {
    "name": "calculator",
    "parameters": {...},
    "registered_at": "2026-03-06T15:53:01"
  }
}
    ↓
Response: {"success": true, "tool": "calculator"}


Step 2: List Tools
──────────────────
Request:
{
  "method": "tools/list",
  "params": {}
}
    ↓
Server → RequestHandler → ToolRegistry.list_tools()
    ↓
Response: {
  "tools": [{"name": "calculator", ...}],
  "count": 1
}


Step 3: Invoke Tool
───────────────────
Request:
{
  "method": "tools/invoke",
  "params": {
    "name": "calculator",
    "arguments": {"expr": "2+2"}
  }
}
    ↓
Server → RequestHandler
    ↓
Validate tool exists
    ↓
Validate required params
    ↓
Execute tool (simulated)
    ↓
Response: {
  "tool": "calculator",
  "arguments": {"expr": "2+2"},
  "result": "Tool execution simulated"
}
```

## Summary

This workflow demonstrates:
1. Clear separation of concerns
2. Proper request routing
3. Comprehensive validation
4. Error handling at each step
5. Clean data flow
6. Extensible architecture
