"""
Comprehensive tests for MCP Communication System
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_communication import MCPCommunicationSystem


async def test_tool_discovery():
    """Test tool discovery integration"""
    print("\n" + "=" * 70)
    print("TEST SUITE: TOOL DISCOVERY")
    print("=" * 70)
    
    system = MCPCommunicationSystem(enable_logging=False)
    
    # Test 1: Discover tools
    print("\nTest 1: Discover tools")
    await system.discovery.discover_tools()
    tools = system.get_available_tools()
    assert len(tools) == 3, f"Expected 3 tools, got {len(tools)}"
    print("✓ Passed")
    
    # Test 2: Filter by category
    print("\nTest 2: Filter by category")
    db_tools = system.get_available_tools(category="database")
    assert len(db_tools) == 1, f"Expected 1 database tool, got {len(db_tools)}"
    assert db_tools[0].name == "query_database"
    print("✓ Passed")
    
    # Test 3: Get tool metadata
    print("\nTest 3: Get tool metadata")
    metadata = await system.discovery.get_tool_metadata("query_database")
    assert metadata is not None
    assert metadata.name == "query_database"
    assert "query" in metadata.inputSchema["properties"]
    print("✓ Passed")
    
    print("\n" + "-" * 70)
    print("TOOL DISCOVERY: ALL TESTS PASSED ✓")
    print("-" * 70)


async def test_tool_invocation():
    """Test tool invocation integration"""
    print("\n" + "=" * 70)
    print("TEST SUITE: TOOL INVOCATION")
    print("=" * 70)
    
    system = MCPCommunicationSystem(enable_logging=False)
    
    # Test 1: Successful invocation
    print("\nTest 1: Successful invocation")
    response = await system.discover_and_invoke("query_database", {
        "query": "SELECT * FROM users"
    })
    assert response["success"] == True
    assert response["metadata"] is not None
    assert response["result"].success == True
    assert response["error"] is None
    print("✓ Passed")
    
    # Test 2: Missing parameter
    print("\nTest 2: Missing parameter error")
    response = await system.discover_and_invoke("send_email", {
        "to": "user@example.com"
    })
    assert response["success"] == False
    assert response["error"] is not None
    assert response["should_retry"] == False
    print("✓ Passed")
    
    # Test 3: Unknown tool
    print("\nTest 3: Unknown tool error")
    response = await system.discover_and_invoke("unknown_tool", {})
    assert response["success"] == False
    assert response["metadata"] is None
    assert response["error"] is not None
    print("✓ Passed")
    
    # Test 4: Multiple invocations
    print("\nTest 4: Multiple invocations")
    response1 = await system.discover_and_invoke("query_database", {"query": "SELECT 1"})
    response2 = await system.discover_and_invoke("web_search", {"query": "test"})
    assert response1["success"] == True
    assert response2["success"] == True
    print("✓ Passed")
    
    print("\n" + "-" * 70)
    print("TOOL INVOCATION: ALL TESTS PASSED ✓")
    print("-" * 70)


async def test_error_handling():
    """Test error handling integration"""
    print("\n" + "=" * 70)
    print("TEST SUITE: ERROR HANDLING")
    print("=" * 70)
    
    system = MCPCommunicationSystem(enable_logging=False)
    
    # Test 1: Parse and handle error
    print("\nTest 1: Parse and handle error")
    response = await system.discover_and_invoke("unknown_tool", {})
    assert response["error"] is not None
    assert response["error"].code == -32601
    assert response["should_retry"] == False
    assert response["action"] == "verify_tool_name"
    print("✓ Passed")
    
    # Test 2: Recoverable error
    print("\nTest 2: Recoverable error detection")
    response = await system.discover_and_invoke("send_email", {"to": "test@example.com"})
    error = response["error"]
    assert error is not None
    assert response["should_retry"] == False  # Invalid params not retryable
    print("✓ Passed")
    
    # Test 3: Error statistics
    print("\nTest 3: Error statistics")
    stats = system.get_statistics()
    assert stats["error_stats"]["total_errors"] > 0
    print("✓ Passed")
    
    # Test 4: Error categorization
    print("\nTest 4: Error categorization")
    response = await system.discover_and_invoke("query_database", {})
    assert response["error"] is not None
    assert response["error"].category.value == "invalid_params"
    print("✓ Passed")
    
    print("\n" + "-" * 70)
    print("ERROR HANDLING: ALL TESTS PASSED ✓")
    print("-" * 70)


async def test_communication_flows():
    """Test complete communication flows"""
    print("\n" + "=" * 70)
    print("TEST SUITE: COMMUNICATION FLOWS")
    print("=" * 70)
    
    system = MCPCommunicationSystem(enable_logging=False)
    
    # Test 1: Discover -> Invoke flow
    print("\nTest 1: Discover -> Invoke flow")
    await system.discovery.discover_tools()
    tools = system.get_available_tools()
    assert len(tools) > 0
    
    response = await system.discover_and_invoke(tools[0].name, {
        "query": "SELECT * FROM users"
    })
    assert response["success"] == True
    print("✓ Passed")
    
    # Test 2: Retry flow
    print("\nTest 2: Retry flow")
    response = await system.invoke_with_retry("query_database", {
        "query": "SELECT 1"
    }, max_retries=2)
    assert response["success"] == True
    assert response["retry_count"] == 0  # Should succeed on first try
    print("✓ Passed")
    
    # Test 3: Batch operations
    print("\nTest 3: Batch operations")
    operations = [
        ("query_database", {"query": "SELECT 1"}),
        ("web_search", {"query": "test"}),
        ("send_email", {"to": "test@example.com", "subject": "Test", "body": "Body"}),
    ]
    results = await system.batch_invoke(operations)
    assert len(results) == 3
    assert results[0]["success"] == True
    assert results[1]["success"] == True
    assert results[2]["success"] == True
    print("✓ Passed")
    
    # Test 4: Error recovery flow
    print("\nTest 4: Error recovery flow")
    # First attempt with missing params
    response = await system.discover_and_invoke("send_email", {"to": "test@example.com"})
    assert response["success"] == False
    assert response["action"] == "validate_parameters"
    
    # Second attempt with correct params
    response = await system.discover_and_invoke("send_email", {
        "to": "test@example.com",
        "subject": "Test",
        "body": "Body"
    })
    assert response["success"] == True
    print("✓ Passed")
    
    # Test 5: Statistics tracking
    print("\nTest 5: Statistics tracking")
    stats = system.get_statistics()
    assert stats["cached_tools"] > 0
    assert stats["request_count"] > 0
    assert stats["error_stats"]["total_errors"] > 0
    print("✓ Passed")
    
    # Test 6: System reset
    print("\nTest 6: System reset")
    system.reset()
    stats = system.get_statistics()
    assert stats["error_stats"]["total_errors"] == 0
    assert stats["request_count"] == 0
    print("✓ Passed")
    
    print("\n" + "-" * 70)
    print("COMMUNICATION FLOWS: ALL TESTS PASSED ✓")
    print("-" * 70)


async def test_edge_cases():
    """Test edge cases and error scenarios"""
    print("\n" + "=" * 70)
    print("TEST SUITE: EDGE CASES")
    print("=" * 70)
    
    system = MCPCommunicationSystem(enable_logging=False)
    
    # Test 1: Empty parameters
    print("\nTest 1: Empty parameters")
    response = await system.discover_and_invoke("query_database", {})
    assert response["success"] == False
    print("✓ Passed")
    
    # Test 2: Invalid parameter types
    print("\nTest 2: Invalid parameter types")
    response = await system.discover_and_invoke("web_search", {
        "query": "test",
        "limit": "not_an_int"
    })
    assert response["success"] == False
    print("✓ Passed")
    
    # Test 3: Batch with mixed results
    print("\nTest 3: Batch with mixed results")
    operations = [
        ("query_database", {"query": "SELECT 1"}),
        ("unknown_tool", {}),
        ("web_search", {"query": "test"}),
    ]
    results = await system.batch_invoke(operations)
    assert len(results) == 3
    assert results[0]["success"] == True
    assert results[1]["success"] == False
    assert results[2]["success"] == True
    print("✓ Passed")
    
    # Test 4: Retry with non-recoverable error
    print("\nTest 4: Retry with non-recoverable error")
    response = await system.invoke_with_retry("unknown_tool", {}, max_retries=3)
    assert response["success"] == False
    assert response["retry_count"] == 0  # Should not retry
    print("✓ Passed")
    
    print("\n" + "-" * 70)
    print("EDGE CASES: ALL TESTS PASSED ✓")
    print("-" * 70)


async def run_all_tests():
    """Run all test suites"""
    print("\n" + "=" * 70)
    print("MCP COMMUNICATION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    try:
        await test_tool_discovery()
        await test_tool_invocation()
        await test_error_handling()
        await test_communication_flows()
        await test_edge_cases()
        
        print("\n" + "=" * 70)
        print("ALL TEST SUITES PASSED! ✓")
        print("=" * 70)
        print("\nSummary:")
        print("  - Tool Discovery: 3/3 tests passed")
        print("  - Tool Invocation: 4/4 tests passed")
        print("  - Error Handling: 4/4 tests passed")
        print("  - Communication Flows: 6/6 tests passed")
        print("  - Edge Cases: 4/4 tests passed")
        print("\n  Total: 21/21 tests passed ✓")
        print("=" * 70)
        
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
