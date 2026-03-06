"""
Comprehensive integration tests for complete MCP server.
Tests all components working together: Server, Registry, and Request Handler.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_server import MCPServer


class TestMCPServer:
    """Comprehensive test suite for integrated MCP server."""
    
    def test_server_lifecycle(self):
        """Test 1: Server Lifecycle - initialization, start, stop."""
        print("Test 1: Server Lifecycle")
        
        # Initialize
        server = MCPServer("test-server", "1.0.0")
        assert server.server_name == "test-server"
        assert server.version == "1.0.0"
        assert server.is_running == False
        
        # Start
        response = server.start()
        assert response["result"]["status"] == "success"
        assert server.is_running == True
        
        # Stop
        response = server.stop()
        assert response["result"]["status"] == "success"
        assert server.is_running == False
        
        print("✓ Server lifecycle working\n")
    
    def test_tool_registration(self):
        """Test 2: Tool Registration - register, duplicate check."""
        print("Test 2: Tool Registration")
        
        server = MCPServer("test-server", "1.0.0")
        server.start()
        
        # Register tool
        response = server.handle_request({
            "method": "tools/register",
            "params": {
                "tool": {
                    "name": "calculator",
                    "description": "Math operations",
                    "parameters": {"expr": {"type": "string", "required": True}}
                }
            }
        })
        assert response["result"]["status"] == "success"
        assert response["result"]["data"]["tool"] == "calculator"
        
        # Duplicate registration
        response = server.handle_request({
            "method": "tools/register",
            "params": {
                "tool": {"name": "calculator", "description": "Duplicate"}
            }
        })
        assert response["result"]["status"] == "error"
        
        server.stop()
        print("✓ Tool registration working\n")
    
    def test_tool_discovery(self):
        """Test 3: Tool Discovery - list tools, get tool details."""
        print("Test 3: Tool Discovery")
        
        server = MCPServer("test-server", "1.0.0")
        server.start()
        
        # Register multiple tools
        tools = [
            {"name": "calculator", "description": "Math"},
            {"name": "weather", "description": "Weather info"},
            {"name": "translator", "description": "Translate text"}
        ]
        
        for tool in tools:
            server.handle_request({
                "method": "tools/register",
                "params": {"tool": tool}
            })
        
        # List tools
        response = server.handle_request({
            "method": "tools/list",
            "params": {}
        })
        assert response["result"]["status"] == "success"
        assert response["result"]["data"]["count"] == 3
        assert len(response["result"]["data"]["tools"]) == 3
        
        # Verify tool names
        tool_names = [t["name"] for t in response["result"]["data"]["tools"]]
        assert "calculator" in tool_names
        assert "weather" in tool_names
        assert "translator" in tool_names
        
        server.stop()
        print("✓ Tool discovery working\n")
    
    def test_tool_invocation(self):
        """Test 4: Tool Invocation - invoke with valid/invalid params."""
        print("Test 4: Tool Invocation")
        
        server = MCPServer("test-server", "1.0.0")
        server.start()
        
        # Register tool
        server.handle_request({
            "method": "tools/register",
            "params": {
                "tool": {
                    "name": "calculator",
                    "description": "Calculate",
                    "parameters": {
                        "expression": {"type": "string", "required": True}
                    }
                }
            }
        })
        
        # Valid invocation
        response = server.handle_request({
            "method": "tools/invoke",
            "params": {
                "name": "calculator",
                "arguments": {"expression": "2+2"}
            }
        })
        assert response["result"]["status"] == "success"
        assert response["result"]["data"]["tool"] == "calculator"
        assert response["result"]["data"]["arguments"]["expression"] == "2+2"
        
        # Missing required parameter
        response = server.handle_request({
            "method": "tools/invoke",
            "params": {
                "name": "calculator",
                "arguments": {}
            }
        })
        assert response["result"]["status"] == "error"
        assert "error" in response["result"]["data"]
        
        # Non-existent tool
        response = server.handle_request({
            "method": "tools/invoke",
            "params": {
                "name": "nonexistent",
                "arguments": {}
            }
        })
        assert response["result"]["status"] == "error"
        
        server.stop()
        print("✓ Tool invocation working\n")
    
    def test_error_handling(self):
        """Test 5: Error Handling - various error scenarios."""
        print("Test 5: Error Handling")
        
        server = MCPServer("test-server", "1.0.0")
        server.start()
        
        # Unknown method
        response = server.handle_request({
            "method": "unknown/method",
            "params": {}
        })
        assert response["result"]["status"] == "error"
        
        # Invalid tool registration (missing name)
        response = server.handle_request({
            "method": "tools/register",
            "params": {"tool": {"description": "No name"}}
        })
        assert response["result"]["status"] == "error"
        
        # Tool removal - non-existent
        response = server.handle_request({
            "method": "tools/remove",
            "params": {"name": "nonexistent"}
        })
        assert response["result"]["status"] == "error"
        
        # Request on stopped server
        server.stop()
        response = server.handle_request({
            "method": "ping",
            "params": {}
        })
        assert response["result"]["status"] == "error"
        assert "not running" in response["result"]["data"]["message"].lower()
        
        print("✓ Error handling working\n")
    
    def test_complete_workflow(self):
        """Test 6: Complete Workflow - end-to-end scenario."""
        print("Test 6: Complete Workflow")
        
        server = MCPServer("workflow-server", "1.0.0")
        
        # Start server
        response = server.start()
        assert response["result"]["status"] == "success"
        
        # Register tools
        tools = [
            {
                "name": "search",
                "description": "Search tool",
                "parameters": {"query": {"type": "string", "required": True}}
            },
            {
                "name": "summarize",
                "description": "Summarize text",
                "parameters": {"text": {"type": "string", "required": True}}
            }
        ]
        
        for tool in tools:
            response = server.handle_request({
                "method": "tools/register",
                "params": {"tool": tool}
            })
            assert response["result"]["status"] == "success"
        
        # Check status
        response = server.handle_request({
            "method": "status",
            "params": {}
        })
        assert response["result"]["data"]["registered_tools"] == 2
        
        # List tools
        response = server.handle_request({
            "method": "tools/list",
            "params": {}
        })
        assert response["result"]["data"]["count"] == 2
        
        # Invoke first tool
        response = server.handle_request({
            "method": "tools/invoke",
            "params": {
                "name": "search",
                "arguments": {"query": "test query"}
            }
        })
        assert response["result"]["status"] == "success"
        
        # Invoke second tool
        response = server.handle_request({
            "method": "tools/invoke",
            "params": {
                "name": "summarize",
                "arguments": {"text": "long text"}
            }
        })
        assert response["result"]["status"] == "success"
        
        # Remove one tool
        response = server.handle_request({
            "method": "tools/remove",
            "params": {"name": "search"}
        })
        assert response["result"]["status"] == "success"
        
        # Verify removal
        response = server.handle_request({
            "method": "tools/list",
            "params": {}
        })
        assert response["result"]["data"]["count"] == 1
        
        # Stop server
        response = server.stop()
        assert response["result"]["status"] == "success"
        
        print("✓ Complete workflow working\n")
    
    def test_request_id_handling(self):
        """Test 7: Request ID Handling - with and without IDs."""
        print("Test 7: Request ID Handling")
        
        server = MCPServer("test-server", "1.0.0")
        server.start()
        
        # Register tool
        server.handle_request({
            "method": "tools/register",
            "params": {"tool": {"name": "test", "description": "Test"}}
        })
        
        # Request with ID
        response = server.handle_request({
            "id": 123,
            "method": "tools/list",
            "params": {}
        })
        assert response["id"] == 123
        
        # Request without ID
        response = server.handle_request({
            "method": "tools/list",
            "params": {}
        })
        # Should not have ID or ID is None
        assert "id" not in response or response.get("id") is None
        
        server.stop()
        print("✓ Request ID handling working\n")
    
    def test_concurrent_operations(self):
        """Test 8: Concurrent Operations - multiple operations in sequence."""
        print("Test 8: Concurrent Operations")
        
        server = MCPServer("test-server", "1.0.0")
        server.start()
        
        # Register multiple tools rapidly
        for i in range(5):
            response = server.handle_request({
                "method": "tools/register",
                "params": {
                    "tool": {
                        "name": f"tool_{i}",
                        "description": f"Tool {i}"
                    }
                }
            })
            assert response["result"]["status"] == "success"
        
        # List all
        response = server.handle_request({
            "method": "tools/list",
            "params": {}
        })
        assert response["result"]["data"]["count"] == 5
        
        # Remove all
        for i in range(5):
            response = server.handle_request({
                "method": "tools/remove",
                "params": {"name": f"tool_{i}"}
            })
            assert response["result"]["status"] == "success"
        
        # Verify empty
        response = server.handle_request({
            "method": "tools/list",
            "params": {}
        })
        assert response["result"]["data"]["count"] == 0
        
        server.stop()
        print("✓ Concurrent operations working\n")
    
    def test_parameter_validation(self):
        """Test 9: Parameter Validation - comprehensive validation tests."""
        print("Test 9: Parameter Validation")
        
        server = MCPServer("test-server", "1.0.0")
        server.start()
        
        # Register tool with multiple parameters
        server.handle_request({
            "method": "tools/register",
            "params": {
                "tool": {
                    "name": "complex_tool",
                    "description": "Complex tool",
                    "parameters": {
                        "required_param": {"type": "string", "required": True},
                        "optional_param": {"type": "string", "required": False}
                    }
                }
            }
        })
        
        # Valid with all params
        response = server.handle_request({
            "method": "tools/invoke",
            "params": {
                "name": "complex_tool",
                "arguments": {
                    "required_param": "value",
                    "optional_param": "optional"
                }
            }
        })
        assert response["result"]["status"] == "success"
        
        # Valid with only required param
        response = server.handle_request({
            "method": "tools/invoke",
            "params": {
                "name": "complex_tool",
                "arguments": {"required_param": "value"}
            }
        })
        assert response["result"]["status"] == "success"
        
        # Invalid - missing required param
        response = server.handle_request({
            "method": "tools/invoke",
            "params": {
                "name": "complex_tool",
                "arguments": {"optional_param": "value"}
            }
        })
        assert response["result"]["status"] == "error"
        
        server.stop()
        print("✓ Parameter validation working\n")
    
    def test_json_rpc_compliance(self):
        """Test 10: JSON-RPC 2.0 Compliance - verify protocol compliance."""
        print("Test 10: JSON-RPC 2.0 Compliance")
        
        server = MCPServer("test-server", "1.0.0")
        server.start()
        
        # Register tool
        server.handle_request({
            "method": "tools/register",
            "params": {"tool": {"name": "test", "description": "Test"}}
        })
        
        # Check response format
        response = server.handle_request({
            "id": 1,
            "method": "tools/list",
            "params": {}
        })
        
        # Verify JSON-RPC 2.0 structure
        assert "jsonrpc" in response
        assert response["jsonrpc"] == "2.0"
        assert "id" in response
        assert "result" in response
        assert "status" in response["result"]
        assert "data" in response["result"]
        assert "timestamp" in response["result"]
        
        server.stop()
        print("✓ JSON-RPC 2.0 compliance verified\n")


def run_all_tests():
    """Run all integration tests."""
    print("=" * 60)
    print("MCP Server - Comprehensive Integration Tests")
    print("=" * 60 + "\n")
    
    test_suite = TestMCPServer()
    
    tests = [
        test_suite.test_server_lifecycle,
        test_suite.test_tool_registration,
        test_suite.test_tool_discovery,
        test_suite.test_tool_invocation,
        test_suite.test_error_handling,
        test_suite.test_complete_workflow,
        test_suite.test_request_id_handling,
        test_suite.test_concurrent_operations,
        test_suite.test_parameter_validation,
        test_suite.test_json_rpc_compliance
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}\n")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}\n")
            failed += 1
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! ✓")
        return True
    else:
        print(f"❌ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
