"""
MCP Communication System
Integrates tool discovery, invocation, and error handling.
"""

import asyncio
from typing import Dict, Any, List, Optional
from tool_discovery import ToolDiscoveryClient, ToolMetadata
from tool_invocation import ToolInvocationClient, InvocationResult
from error_handling import ErrorHandler, MCPError, create_error_response


class MCPCommunicationSystem:
    """Complete MCP communication system"""
    
    def __init__(self, timeout: float = 30.0, enable_logging: bool = True):
        self.discovery = ToolDiscoveryClient()
        self.invocation = ToolInvocationClient(timeout=timeout)
        self.error_handler = ErrorHandler(enable_logging=enable_logging)
        self.server_id = "default"
    
    async def discover_and_invoke(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Discover tool metadata and invoke with error handling
        
        Returns:
            Dict with result, error, and metadata
        """
        # Discover tool
        metadata = await self.discovery.get_tool_metadata(tool_name, self.server_id)
        
        if not metadata:
            error_response = create_error_response(-32601, f"Tool not found: {tool_name}")
            error = self.error_handler.parse_error(error_response)
            should_retry, action = self.error_handler.handle_error(error)
            
            return {
                "success": False,
                "metadata": None,
                "result": None,
                "error": error,
                "should_retry": should_retry,
                "action": action
            }
        
        # Invoke tool
        result = await self.invocation.invoke_tool(tool_name, params)
        
        if not result.success:
            # Handle error
            error_code = self._map_error_code(result.error)
            error_response = create_error_response(error_code, result.error)
            error = self.error_handler.parse_error(error_response)
            should_retry, action = self.error_handler.handle_error(error)
            
            return {
                "success": False,
                "metadata": metadata,
                "result": result,
                "error": error,
                "should_retry": should_retry,
                "action": action
            }
        
        return {
            "success": True,
            "metadata": metadata,
            "result": result,
            "error": None
        }
    
    async def invoke_with_retry(self, tool_name: str, params: Dict[str, Any], 
                                max_retries: int = 3) -> Dict[str, Any]:
        """Invoke tool with automatic retry on recoverable errors"""
        retry_count = 0
        
        while retry_count <= max_retries:
            response = await self.discover_and_invoke(tool_name, params)
            
            if response["success"]:
                response["retry_count"] = retry_count
                return response
            
            if response.get("should_retry") and retry_count < max_retries:
                retry_count += 1
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
            else:
                response["retry_count"] = retry_count
                return response
        
        return response
    
    async def batch_invoke(self, operations: List[tuple]) -> List[Dict[str, Any]]:
        """Execute multiple tool invocations"""
        results = []
        for tool_name, params in operations:
            result = await self.discover_and_invoke(tool_name, params)
            results.append(result)
        return results
    
    def get_available_tools(self, category: Optional[str] = None) -> List[ToolMetadata]:
        """Get available tools, optionally filtered by category"""
        if category:
            return self.discovery.filter_tools({"category": category}, self.server_id)
        return self.discovery._cache.get(self.server_id, [])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        return {
            "error_stats": self.error_handler.get_error_stats(),
            "cached_tools": len(self.discovery._cache.get(self.server_id, [])),
            "request_count": self.invocation._request_id
        }
    
    def reset(self):
        """Reset system state"""
        self.discovery.clear_cache()
        self.error_handler.clear_history()
        self.invocation._request_id = 0
    
    def _map_error_code(self, error_msg: str) -> int:
        """Map error message to MCP error code"""
        if "not found" in error_msg.lower():
            return -32601
        elif "required parameter" in error_msg.lower() or "invalid type" in error_msg.lower():
            return -32602
        elif "timed out" in error_msg.lower():
            return -32000
        else:
            return -32603


async def main():
    """Demo MCP communication system"""
    system = MCPCommunicationSystem(timeout=5.0)
    
    print("=" * 70)
    print("MCP COMMUNICATION SYSTEM DEMO")
    print("=" * 70)
    
    # Test 1: Discover and invoke
    print("\n[Test 1] Discover and Invoke")
    print("-" * 70)
    response = await system.discover_and_invoke("query_database", {
        "query": "SELECT * FROM users"
    })
    print(f"Success: {response['success']}")
    print(f"Tool: {response['metadata'].name if response['metadata'] else 'N/A'}")
    print(f"Result: {response['result'].content if response['result'] else 'N/A'}")
    
    # Test 2: Error handling
    print("\n[Test 2] Error Handling")
    print("-" * 70)
    response = await system.discover_and_invoke("send_email", {"to": "user@example.com"})
    print(f"Success: {response['success']}")
    print(f"Error: {response['error'].message if response['error'] else 'N/A'}")
    print(f"Action: {response.get('action', 'N/A')}")
    
    # Test 3: Retry logic
    print("\n[Test 3] Invoke with Retry")
    print("-" * 70)
    response = await system.invoke_with_retry("query_database", {
        "query": "SELECT COUNT(*) FROM users"
    })
    print(f"Success: {response['success']}")
    print(f"Retry count: {response['retry_count']}")
    
    # Test 4: Batch operations
    print("\n[Test 4] Batch Operations")
    print("-" * 70)
    operations = [
        ("query_database", {"query": "SELECT 1"}),
        ("web_search", {"query": "MCP protocol"}),
    ]
    results = await system.batch_invoke(operations)
    print(f"Executed {len(results)} operations")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Success: {result['success']}")
    
    # Test 5: Get available tools
    print("\n[Test 5] Available Tools")
    print("-" * 70)
    await system.discovery.discover_tools()
    tools = system.get_available_tools()
    print(f"Total tools: {len(tools)}")
    
    db_tools = system.get_available_tools(category="database")
    print(f"Database tools: {len(db_tools)}")
    
    # Test 6: Statistics
    print("\n[Test 6] System Statistics")
    print("-" * 70)
    stats = system.get_statistics()
    print(f"Error count: {stats['error_stats']['total_errors']}")
    print(f"Cached tools: {stats['cached_tools']}")
    print(f"Request count: {stats['request_count']}")
    
    print("\n" + "=" * 70)
    print("DEMO COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
