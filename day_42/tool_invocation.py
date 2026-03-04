"""
MCP Tool Invocation Client
Implements tool invocation through MCP protocol.
"""

import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time


@dataclass
class InvocationResult:
    """Tool invocation result"""
    success: bool
    content: Any
    error: Optional[str] = None
    execution_time: float = 0.0


class ToolInvocationClient:
    """MCP Tool Invocation Client"""
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self._request_id = 0
    
    async def invoke_tool(self, tool_name: str, params: Dict[str, Any]) -> InvocationResult:
        """
        Invoke a tool through MCP protocol
        
        Args:
            tool_name: Name of the tool to invoke
            params: Tool parameters
            
        Returns:
            InvocationResult with success status and content
        """
        start_time = time.time()
        
        # Validate parameters
        validation_error = self._validate_params(tool_name, params)
        if validation_error:
            return InvocationResult(
                success=False,
                content=None,
                error=validation_error,
                execution_time=time.time() - start_time
            )
        
        # Build MCP request
        self._request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        # Send request with timeout
        try:
            response = await asyncio.wait_for(
                self._send_request(request),
                timeout=self.timeout
            )
            
            # Parse response
            result = self._parse_response(response)
            result.execution_time = time.time() - start_time
            return result
            
        except asyncio.TimeoutError:
            return InvocationResult(
                success=False,
                content=None,
                error=f"Tool invocation timed out after {self.timeout}s",
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return InvocationResult(
                success=False,
                content=None,
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def _validate_params(self, tool_name: str, params: Dict[str, Any]) -> Optional[str]:
        """Validate tool parameters"""
        if not tool_name:
            return "Tool name is required"
        
        if not isinstance(params, dict):
            return "Parameters must be a dictionary"
        
        # Tool-specific validation
        schemas = {
            "query_database": {
                "required": ["query"],
                "properties": {"query": str}
            },
            "send_email": {
                "required": ["to", "subject", "body"],
                "properties": {"to": str, "subject": str, "body": str}
            },
            "web_search": {
                "required": ["query"],
                "properties": {"query": str, "limit": int}
            }
        }
        
        if tool_name in schemas:
            schema = schemas[tool_name]
            
            # Check required fields
            for field in schema["required"]:
                if field not in params:
                    return f"Missing required parameter: {field}"
            
            # Check types
            for field, expected_type in schema["properties"].items():
                if field in params and not isinstance(params[field], expected_type):
                    return f"Invalid type for {field}: expected {expected_type.__name__}"
        
        return None
    
    def _parse_response(self, response: Dict[str, Any]) -> InvocationResult:
        """Parse MCP response"""
        if "error" in response:
            return InvocationResult(
                success=False,
                content=None,
                error=response["error"].get("message", "Unknown error")
            )
        
        if "result" in response:
            result_data = response["result"]
            
            # Check for tool execution errors
            if isinstance(result_data, dict) and result_data.get("isError"):
                return InvocationResult(
                    success=False,
                    content=result_data.get("content"),
                    error="Tool execution failed"
                )
            
            return InvocationResult(
                success=True,
                content=result_data.get("content") if isinstance(result_data, dict) else result_data
            )
        
        return InvocationResult(
            success=False,
            content=None,
            error="Invalid response format"
        )
    
    async def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to server (mock implementation)"""
        tool_name = request["params"]["name"]
        arguments = request["params"]["arguments"]
        
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Mock tool responses
        if tool_name == "query_database":
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "content": [
                        {"id": 1, "name": "Alice", "email": "alice@example.com"},
                        {"id": 2, "name": "Bob", "email": "bob@example.com"}
                    ]
                }
            }
        
        elif tool_name == "send_email":
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "content": {
                        "status": "sent",
                        "message_id": "msg_12345",
                        "to": arguments["to"]
                    }
                }
            }
        
        elif tool_name == "web_search":
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "content": [
                        {"title": "Result 1", "url": "https://example.com/1"},
                        {"title": "Result 2", "url": "https://example.com/2"}
                    ]
                }
            }
        
        elif tool_name == "slow_tool":
            await asyncio.sleep(2)
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {"content": "Completed"}
            }
        
        else:
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "error": {
                    "code": -32601,
                    "message": f"Tool not found: {tool_name}"
                }
            }


async def main():
    """Demo usage"""
    client = ToolInvocationClient(timeout=5.0)
    
    print("=== Tool Invocation Demo ===\n")
    
    # 1. Query database
    print("1. Query Database")
    result = await client.invoke_tool("query_database", {"query": "SELECT * FROM users"})
    print(f"   Success: {result.success}")
    print(f"   Content: {result.content}")
    print(f"   Time: {result.execution_time:.3f}s\n")
    
    # 2. Send email
    print("2. Send Email")
    result = await client.invoke_tool("send_email", {
        "to": "user@example.com",
        "subject": "Test",
        "body": "Hello!"
    })
    print(f"   Success: {result.success}")
    print(f"   Content: {result.content}")
    print(f"   Time: {result.execution_time:.3f}s\n")
    
    # 3. Web search
    print("3. Web Search")
    result = await client.invoke_tool("web_search", {"query": "MCP protocol", "limit": 5})
    print(f"   Success: {result.success}")
    print(f"   Content: {result.content}")
    print(f"   Time: {result.execution_time:.3f}s\n")
    
    # 4. Missing parameter
    print("4. Missing Parameter (Error)")
    result = await client.invoke_tool("send_email", {"to": "user@example.com"})
    print(f"   Success: {result.success}")
    print(f"   Error: {result.error}\n")
    
    # 5. Unknown tool
    print("5. Unknown Tool (Error)")
    result = await client.invoke_tool("unknown_tool", {})
    print(f"   Success: {result.success}")
    print(f"   Error: {result.error}\n")


if __name__ == "__main__":
    asyncio.run(main())
