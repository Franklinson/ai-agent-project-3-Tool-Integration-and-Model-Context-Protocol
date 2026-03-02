# MCP Interaction Diagrams

## 1. Tool Discovery Flow

### Overview
The tool discovery flow allows clients to discover what tools are available on a server.

### Sequence Diagram

```
┌──────┐         ┌──────┐         ┌────────┐         ┌────────┐
│ User │         │ Host │         │ Client │         │ Server │
└──┬───┘         └──┬───┘         └───┬────┘         └───┬────┘
   │                │                 │                   │
   │ Request tools  │                 │                   │
   │───────────────>│                 │                   │
   │                │                 │                   │
   │                │ list_tools()    │                   │
   │                │────────────────>│                   │
   │                │                 │                   │
   │                │                 │ tools/list        │
   │                │                 │──────────────────>│
   │                │                 │ {                 │
   │                │                 │   "jsonrpc": "2.0"│
   │                │                 │   "id": 1,        │
   │                │                 │   "method": "..." │
   │                │                 │ }                 │
   │                │                 │                   │
   │                │                 │                   ├─┐
   │                │                 │                   │ │ Gather
   │                │                 │                   │ │ tool
   │                │                 │                   │ │ definitions
   │                │                 │                   │<┘
   │                │                 │                   │
   │                │                 │    Response       │
   │                │                 │<──────────────────│
   │                │                 │ {                 │
   │                │                 │   "result": {     │
   │                │                 │     "tools": [    │
   │                │                 │       {           │
   │                │                 │         "name": "read_file"│
   │                │                 │         "description": "..."│
   │                │                 │         "inputSchema": {...}│
   │                │                 │       }           │
   │                │                 │     ]             │
   │                │                 │   }               │
   │                │                 │ }                 │
   │                │                 │                   │
   │                │  Tool List      │                   │
   │                │<────────────────│                   │
   │                │                 │                   │
   │                ├─┐               │                   │
   │                │ │ Cache tools   │                   │
   │                │ │ & schemas     │                   │
   │                │<┘               │                   │
   │                │                 │                   │
   │  Display tools │                 │                   │
   │<───────────────│                 │                   │
   │                │                 │                   │
```

### Detailed Steps

1. **User Request**: User requests available tools through UI
2. **Host Processing**: Host calls client's list_tools() method
3. **Client Request**: Client sends JSON-RPC request:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "method": "tools/list"
   }
   ```
4. **Server Processing**: Server gathers all registered tools
5. **Server Response**: Server returns tool definitions:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "tools": [
         {
           "name": "read_file",
           "description": "Read contents of a file",
           "inputSchema": {
             "type": "object",
             "properties": {
               "path": {
                 "type": "string",
                 "description": "File path"
               }
             },
             "required": ["path"]
           }
         }
       ]
     }
   }
   ```
6. **Client Processing**: Client parses and returns tool list
7. **Host Caching**: Host caches tools for future use
8. **User Display**: Tools displayed to user

### State Changes

```
Initial State: No tools known
     │
     ▼
[Request Sent] ──> Waiting for response
     │
     ▼
[Response Received] ──> Parsing tools
     │
     ▼
[Tools Cached] ──> Ready for invocation
```

## 2. Tool Invocation Flow

### Overview
The tool invocation flow executes a specific tool with provided arguments.

### Sequence Diagram

```
┌──────┐    ┌──────┐    ┌────────┐    ┌────────┐    ┌─────────┐
│ User │    │ Host │    │ Client │    │ Server │    │ Backend │
└──┬───┘    └──┬───┘    └───┬────┘    └───┬────┘    └────┬────┘
   │           │            │              │              │
   │ Execute   │            │              │              │
   │ tool      │            │              │              │
   │──────────>│            │              │              │
   │           │            │              │              │
   │           ├─┐          │              │              │
   │           │ │ Validate │              │              │
   │           │ │ input    │              │              │
   │           │<┘          │              │              │
   │           │            │              │              │
   │           │ call_tool()│              │              │
   │           │───────────>│              │              │
   │           │            │              │              │
   │           │            │ tools/call   │              │
   │           │            │─────────────>│              │
   │           │            │ {            │              │
   │           │            │   "name": "read_file"       │
   │           │            │   "arguments": {            │
   │           │            │     "path": "/file.txt"     │
   │           │            │   }          │              │
   │           │            │ }            │              │
   │           │            │              │              │
   │           │            │              ├─┐            │
   │           │            │              │ │ Validate   │
   │           │            │              │ │ arguments  │
   │           │            │              │<┘            │
   │           │            │              │              │
   │           │            │              │ Execute      │
   │           │            │              │─────────────>│
   │           │            │              │              │
   │           │            │              │              ├─┐
   │           │            │              │              │ │ Perform
   │           │            │              │              │ │ operation
   │           │            │              │              │<┘
   │           │            │              │              │
   │           │            │              │   Result     │
   │           │            │              │<─────────────│
   │           │            │              │              │
   │           │            │   Response   │              │
   │           │            │<─────────────│              │
   │           │            │ {            │              │
   │           │            │   "content": [              │
   │           │            │     {        │              │
   │           │            │       "type": "text"        │
   │           │            │       "text": "..."         │
   │           │            │     }        │              │
   │           │            │   ]          │              │
   │           │            │ }            │              │
   │           │            │              │              │
   │           │   Result   │              │              │
   │           │<───────────│              │              │
   │           │            │              │              │
   │           ├─┐          │              │              │
   │           │ │ Process  │              │              │
   │           │ │ result   │              │              │
   │           │<┘          │              │              │
   │           │            │              │              │
   │  Display  │            │              │              │
   │<──────────│            │              │              │
   │           │            │              │              │
```

### Detailed Steps

1. **User Action**: User triggers tool execution
2. **Host Validation**: Host validates input against tool schema
3. **Client Request**: Client sends tool call:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 2,
     "method": "tools/call",
     "params": {
       "name": "read_file",
       "arguments": {
         "path": "/path/to/file.txt"
       }
     }
   }
   ```
4. **Server Validation**: Server validates arguments against schema
5. **Backend Execution**: Server delegates to backend for actual operation
6. **Backend Processing**: Backend performs the operation
7. **Server Response**: Server formats and returns result:
   ```json
   {
     "jsonrpc": "2.0",
     "id": 2,
     "result": {
       "content": [
         {
           "type": "text",
           "text": "File contents here..."
         }
       ]
     }
   }
   ```
8. **Client Processing**: Client parses response
9. **Host Processing**: Host processes result for display
10. **User Display**: Result shown to user

### With Progress Updates

```
┌──────┐    ┌────────┐    ┌────────┐
│ Host │    │ Client │    │ Server │
└──┬───┘    └───┬────┘    └───┬────┘
   │            │              │
   │ call_tool()│              │
   │───────────>│              │
   │            │ tools/call   │
   │            │─────────────>│
   │            │              │
   │            │              ├─┐ Start
   │            │              │ │ execution
   │            │              │<┘
   │            │              │
   │            │  Progress 1  │
   │            │<─────────────│
   │  Progress  │ {            │
   │<───────────│   "progress": 25│
   │            │   "total": 100  │
   │            │ }            │
   │            │              │
   │            │  Progress 2  │
   │            │<─────────────│
   │  Progress  │              │
   │<───────────│              │
   │            │              │
   │            │   Result     │
   │            │<─────────────│
   │   Result   │              │
   │<───────────│              │
   │            │              │
```

## 3. Error Handling Flow

### Overview
Error handling ensures graceful degradation and clear error communication.

### Error at Server Level

```
┌──────┐    ┌────────┐    ┌────────┐    ┌─────────┐
│ Host │    │ Client │    │ Server │    │ Backend │
└──┬───┘    └───┬────┘    └───┬────┘    └────┬────┘
   │            │              │              │
   │ call_tool()│              │              │
   │───────────>│              │              │
   │            │ tools/call   │              │
   │            │─────────────>│              │
   │            │              │              │
   │            │              │ Execute      │
   │            │              │─────────────>│
   │            │              │              │
   │            │              │              ├─┐
   │            │              │              │ │ Error!
   │            │              │              │ │ File not
   │            │              │              │ │ found
   │            │              │              │<┘
   │            │              │              │
   │            │              │   Exception  │
   │            │              │<─────────────│
   │            │              │              │
   │            │              ├─┐            │
   │            │              │ │ Catch &    │
   │            │              │ │ format     │
   │            │              │ │ error      │
   │            │              │<┘            │
   │            │              │              │
   │            │  Error       │              │
   │            │<─────────────│              │
   │            │ {            │              │
   │            │   "error": { │              │
   │            │     "code": -32602          │
   │            │     "message": "File not found"│
   │            │     "data": {...}           │
   │            │   }          │              │
   │            │ }            │              │
   │            │              │              │
   │            ├─┐            │              │
   │            │ │ Parse      │              │
   │            │ │ error      │              │
   │            │<┘            │              │
   │            │              │              │
   │   Error    │              │              │
   │<───────────│              │              │
   │            │              │              │
   ├─┐          │              │              │
   │ │ Handle   │              │              │
   │ │ error    │              │              │
   │<┘          │              │              │
   │            │              │              │
```

### Error Response Format

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "parameter": "path",
      "reason": "File not found: /invalid/path.txt"
    }
  }
}
```

### Error Code Categories

```
┌─────────────────────────────────────────┐
│         JSON-RPC Error Codes            │
├─────────────────────────────────────────┤
│ -32700  Parse error                     │
│ -32600  Invalid request                 │
│ -32601  Method not found                │
│ -32602  Invalid params                  │
│ -32603  Internal error                  │
├─────────────────────────────────────────┤
│         MCP-Specific Errors             │
├─────────────────────────────────────────┤
│ -32000  Server error                    │
│ -32001  Resource not found              │
│ -32002  Permission denied               │
│ -32003  Rate limit exceeded             │
└─────────────────────────────────────────┘
```

### Error Handling Strategy

```
Error Occurs
     │
     ▼
┌─────────────────┐
│ Catch Exception │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│ Retryable?      │─Yes─>│ Retry Logic  │
└────────┬────────┘      └──────┬───────┘
         │                      │
         No                     │
         │                      │
         ▼                      ▼
┌─────────────────┐      ┌──────────────┐
│ Format Error    │      │ Success?     │
│ Response        │      └──────┬───────┘
└────────┬────────┘             │
         │                      No
         │                      │
         ▼                      ▼
┌─────────────────┐      ┌──────────────┐
│ Log Error       │<─────│ Give Up      │
└────────┬────────┘      └──────────────┘
         │
         ▼
┌─────────────────┐
│ Return to       │
│ Client          │
└─────────────────┘
```

### Connection Error Flow

```
┌────────┐                    ┌────────┐
│ Client │                    │ Server │
└───┬────┘                    └───┬────┘
    │                             │
    │  Request                    │
    │────────────────────────────>│
    │                             X (Connection lost)
    │                             
    ├─┐ Timeout
    │ │ detected
    │<┘
    │
    ├─┐ Attempt
    │ │ reconnect
    │<┘
    │
    │  Reconnect
    │────────────────────────────>│
    │                             │
    │         Connected           │
    │<────────────────────────────│
    │                             │
    │  Retry Request              │
    │────────────────────────────>│
    │                             │
    │         Response            │
    │<────────────────────────────│
    │                             │
```

## 4. Lifecycle Management Flow

### Complete Lifecycle

```
┌────────┐                              ┌────────┐
│ Client │                              │ Server │
└───┬────┘                              └───┬────┘
    │                                       │
    │ ═══════════ INITIALIZATION ═══════════
    │                                       │
    │  1. Connect (Transport)               │
    │──────────────────────────────────────>│
    │                                       │
    │         Connection Established        │
    │<──────────────────────────────────────│
    │                                       │
    │  2. initialize                        │
    │──────────────────────────────────────>│
    │  {                                    │
    │    "protocolVersion": "2024-11-05",   │
    │    "capabilities": {...},             │
    │    "clientInfo": {...}                │
    │  }                                    │
    │                                       │
    │                                       ├─┐
    │                                       │ │ Validate
    │                                       │ │ version
    │                                       │<┘
    │                                       │
    │         initialize result             │
    │<──────────────────────────────────────│
    │  {                                    │
    │    "protocolVersion": "2024-11-05",   │
    │    "capabilities": {...},             │
    │    "serverInfo": {...}                │
    │  }                                    │
    │                                       │
    │  3. initialized (notification)        │
    │──────────────────────────────────────>│
    │                                       │
    │                                       ├─┐
    │                                       │ │ Ready
    │                                       │ │ to serve
    │                                       │<┘
    │                                       │
    │ ═══════════ OPERATIONAL ══════════════
    │                                       │
    │  tools/list                           │
    │──────────────────────────────────────>│
    │         tools/list result             │
    │<──────────────────────────────────────│
    │                                       │
    │  tools/call                           │
    │──────────────────────────────────────>│
    │         tools/call result             │
    │<──────────────────────────────────────│
    │                                       │
    │  resources/list                       │
    │──────────────────────────────────────>│
    │         resources/list result         │
    │<──────────────────────────────────────│
    │                                       │
    │         notifications/... (optional)  │
    │<──────────────────────────────────────│
    │                                       │
    │ ═══════════ SHUTDOWN ═════════════════
    │                                       │
    │  shutdown (notification)              │
    │──────────────────────────────────────>│
    │                                       │
    │                                       ├─┐
    │                                       │ │ Cleanup
    │                                       │ │ resources
    │                                       │<┘
    │                                       │
    │  Close Connection                     │
    │──────────────────────────────────────>│
    │                                       │
    │         Connection Closed             │
    │<──────────────────────────────────────│
    │                                       │
```

### State Transitions

```
┌─────────────┐
│ Disconnected│
└──────┬──────┘
       │ connect()
       ▼
┌─────────────┐
│  Connected  │
└──────┬──────┘
       │ initialize()
       ▼
┌─────────────┐
│Initializing │
└──────┬──────┘
       │ initialized notification
       ▼
┌─────────────┐
│    Ready    │◄──┐
└──────┬──────┘   │
       │          │ Continue operations
       │ Operations
       └──────────┘
       │
       │ shutdown()
       ▼
┌─────────────┐
│  Shutting   │
│    Down     │
└──────┬──────┘
       │ cleanup complete
       ▼
┌─────────────┐
│Disconnected │
└─────────────┘
```

### Initialization Details

```
Client                                    Server
  │                                         │
  │  ────── initialize ──────>             │
  │                                         │
  │                                         ├─┐
  │                                         │ │ 1. Validate
  │                                         │ │    protocol version
  │                                         │<┘
  │                                         │
  │                                         ├─┐
  │                                         │ │ 2. Check client
  │                                         │ │    capabilities
  │                                         │<┘
  │                                         │
  │                                         ├─┐
  │                                         │ │ 3. Prepare server
  │                                         │ │    capabilities
  │                                         │<┘
  │                                         │
  │                                         ├─┐
  │                                         │ │ 4. Initialize
  │                                         │ │    resources
  │                                         │<┘
  │                                         │
  │         <────── initialize result ────  │
  │                                         │
  ├─┐                                       │
  │ │ 5. Store server                      │
  │ │    capabilities                      │
  │<┘                                       │
  │                                         │
  ├─┐                                       │
  │ │ 6. Prepare for                       │
  │ │    operations                        │
  │<┘                                       │
  │                                         │
  │  ────── initialized ──────>            │
  │                                         │
  │                                         ├─┐
  │                                         │ │ 7. Mark as ready
  │                                         │<┘
  │                                         │
```

### Graceful Shutdown

```
Host                Client              Server
  │                   │                   │
  │ Shutdown request  │                   │
  │──────────────────>│                   │
  │                   │                   │
  │                   ├─┐                 │
  │                   │ │ 1. Stop         │
  │                   │ │    accepting    │
  │                   │ │    new requests │
  │                   │<┘                 │
  │                   │                   │
  │                   ├─┐                 │
  │                   │ │ 2. Wait for     │
  │                   │ │    pending      │
  │                   │ │    requests     │
  │                   │<┘                 │
  │                   │                   │
  │                   │ shutdown          │
  │                   │──────────────────>│
  │                   │                   │
  │                   │                   ├─┐
  │                   │                   │ │ 3. Cleanup
  │                   │                   │ │    resources
  │                   │                   │<┘
  │                   │                   │
  │                   │                   ├─┐
  │                   │                   │ │ 4. Close
  │                   │                   │ │    connections
  │                   │                   │<┘
  │                   │                   │
  │                   │  Acknowledged     │
  │                   │<──────────────────│
  │                   │                   │
  │                   ├─┐                 │
  │                   │ │ 5. Close        │
  │                   │ │    transport    │
  │                   │<┘                 │
  │                   │                   │
  │  Shutdown complete│                   │
  │<──────────────────│                   │
  │                   │                   │
```

## 5. Resource Subscription Flow

### Overview
Servers can notify clients when resources change.

```
┌────────┐                              ┌────────┐
│ Client │                              │ Server │
└───┬────┘                              └───┬────┘
    │                                       │
    │  resources/subscribe                  │
    │──────────────────────────────────────>│
    │  {                                    │
    │    "uri": "file:///watch/this.txt"    │
    │  }                                    │
    │                                       │
    │                                       ├─┐
    │                                       │ │ Register
    │                                       │ │ subscription
    │                                       │<┘
    │                                       │
    │         Subscription confirmed        │
    │<──────────────────────────────────────│
    │                                       │
    │                                       │
    │         ... time passes ...           │
    │                                       │
    │                                       ├─┐
    │                                       │ │ Resource
    │                                       │ │ changed!
    │                                       │<┘
    │                                       │
    │  notifications/resources/updated      │
    │<──────────────────────────────────────│
    │  {                                    │
    │    "uri": "file:///watch/this.txt"    │
    │  }                                    │
    │                                       │
    ├─┐                                     │
    │ │ Handle                              │
    │ │ update                              │
    │<┘                                     │
    │                                       │
    │  resources/unsubscribe                │
    │──────────────────────────────────────>│
    │  {                                    │
    │    "uri": "file:///watch/this.txt"    │
    │  }                                    │
    │                                       │
    │                                       ├─┐
    │                                       │ │ Remove
    │                                       │ │ subscription
    │                                       │<┘
    │                                       │
    │         Unsubscribe confirmed         │
    │<──────────────────────────────────────│
    │                                       │
```

## 6. Sampling Request Flow (Server-Initiated)

### Overview
Servers can request LLM completions from the host.

```
┌──────┐    ┌────────┐    ┌────────┐    ┌─────┐
│ Host │    │ Client │    │ Server │    │ LLM │
└──┬───┘    └───┬────┘    └───┬────┘    └──┬──┘
   │            │              │            │
   │            │              ├─┐          │
   │            │              │ │ Need LLM │
   │            │              │ │ help     │
   │            │              │<┘          │
   │            │              │            │
   │            │  sampling/createMessage   │
   │            │<─────────────│            │
   │            │  {           │            │
   │            │    "messages": [          │
   │            │      {       │            │
   │            │        "role": "user"     │
   │            │        "content": "..."   │
   │            │      }       │            │
   │            │    ],        │            │
   │            │    "maxTokens": 1000      │
   │            │  }           │            │
   │            │              │            │
   │  Sampling  │              │            │
   │  request   │              │            │
   │<───────────│              │            │
   │            │              │            │
   │ Call LLM   │              │            │
   │───────────────────────────────────────>│
   │            │              │            │
   │            │              │            ├─┐
   │            │              │            │ │ Generate
   │            │              │            │<┘
   │            │              │            │
   │  Response  │              │            │
   │<───────────────────────────────────────│
   │            │              │            │
   │  Return    │              │            │
   │  result    │              │            │
   │───────────>│              │            │
   │            │              │            │
   │            │  Response    │            │
   │            │─────────────>│            │
   │            │  {           │            │
   │            │    "content": "..."       │
   │            │    "model": "..."         │
   │            │  }           │            │
   │            │              │            │
   │            │              ├─┐          │
   │            │              │ │ Use      │
   │            │              │ │ response │
   │            │              │<┘          │
   │            │              │            │
```

## Summary

These interaction diagrams illustrate:

1. **Tool Discovery**: How clients discover available tools
2. **Tool Invocation**: Complete flow of executing a tool
3. **Error Handling**: How errors propagate and are handled
4. **Lifecycle Management**: Connection, initialization, operation, and shutdown
5. **Resource Subscription**: Real-time updates for resources
6. **Sampling Requests**: Server-initiated LLM requests

Each flow demonstrates the clear separation of concerns between components and the robust communication patterns that make MCP reliable and extensible.
