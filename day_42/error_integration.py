"""
Integration: Tool Invocation with Error Handling
Demonstrates complete workflow with comprehensive error handling
"""

import asyncio
from tool_invocation import ToolInvocationClient
from error_handling import ErrorHandler, create_error_response


class EnhancedInvocationClient(ToolInvocationClient):
    """Tool invocation client with integrated error handling"""
    
    def __init__(self, timeout: float = 30.0):
        super().__init__(timeout)
        self.error_handler = ErrorHandler(enable_logging=True)
    
    async def invoke_with_error_handling(self, tool_name: str, params: dict):
        """Invoke tool with comprehensive error handling"""
        result = await self.invoke_tool(tool_name, params)
        
        if not result.success and result.error:
            # Create error response for handler
            if "not found" in result.error.lower():
                code = -32601
            elif "required parameter" in result.error.lower():
                code = -32602
            elif "timed out" in result.error.lower():
                code = -32000
            else:
                code = -32603
            
            response = create_error_response(code, result.error)
            mcp_error = self.error_handler.parse_error(response)
            
            should_retry, action = self.error_handler.handle_error(mcp_error)
            
            return {
                "result": result,
                "error": mcp_error,
                "should_retry": should_retry,
                "action": action
            }
        
        return {"result": result, "error": None}
    
    def get_error_stats(self):
        """Get error statistics"""
        return self.error_handler.get_error_stats()


async def main():
    """Demo integration"""
    client = EnhancedInvocationClient(timeout=5.0)
    
    print("=" * 70)
    print("TOOL INVOCATION WITH ERROR HANDLING")
    print("=" * 70)
    
    # Test 1: Successful invocation
    print("\n[Test 1] Successful Invocation")
    print("-" * 70)
    response = await client.invoke_with_error_handling("query_database", {
        "query": "SELECT * FROM users"
    })
    print(f"Success: {response['result'].success}")
    print(f"Error: {response['error']}")
    
    # Test 2: Missing parameter
    print("\n[Test 2] Missing Parameter Error")
    print("-" * 70)
    response = await client.invoke_with_error_handling("send_email", {
        "to": "user@example.com"
    })
    print(f"Success: {response['result'].success}")
    print(f"Error category: {response['error'].category.value}")
    print(f"Should retry: {response['should_retry']}")
    print(f"Recommended action: {response['action']}")
    
    # Test 3: Unknown tool
    print("\n[Test 3] Unknown Tool Error")
    print("-" * 70)
    response = await client.invoke_with_error_handling("unknown_tool", {})
    print(f"Success: {response['result'].success}")
    print(f"Error category: {response['error'].category.value}")
    print(f"Should retry: {response['should_retry']}")
    print(f"Recommended action: {response['action']}")
    
    # Test 4: Timeout error
    print("\n[Test 4] Timeout Error")
    print("-" * 70)
    short_client = EnhancedInvocationClient(timeout=0.5)
    response = await short_client.invoke_with_error_handling("slow_tool", {})
    print(f"Success: {response['result'].success}")
    print(f"Error category: {response['error'].category.value}")
    print(f"Should retry: {response['should_retry']}")
    print(f"Recommended action: {response['action']}")
    
    # Test 5: Error statistics
    print("\n[Test 5] Error Statistics")
    print("-" * 70)
    stats = client.get_error_stats()
    print(f"Total errors: {stats['total_errors']}")
    print(f"Recoverable errors: {stats['recoverable_count']}")
    print(f"By category:")
    for category, count in stats.get('by_category', {}).items():
        print(f"  - {category}: {count}")
    
    # Test 6: Retry logic simulation
    print("\n[Test 6] Retry Logic Simulation")
    print("-" * 70)
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        print(f"Attempt {retry_count + 1}...")
        response = await client.invoke_with_error_handling("query_database", {
            "query": "SELECT * FROM users"
        })
        
        if response['result'].success:
            print("✓ Success!")
            break
        
        if response.get('should_retry'):
            retry_count += 1
            print(f"  Error: {response['error'].message}")
            print(f"  Action: {response['action']}")
            if retry_count < max_retries:
                print(f"  Retrying...")
                await asyncio.sleep(0.5)
        else:
            print(f"  Non-recoverable error: {response['error'].message}")
            break
    
    print("\n" + "=" * 70)
    print("INTEGRATION DEMO COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
