"""
Test suite for Request Handler.
"""

import json
from request_handler import RequestHandler
from tool_registry import ToolRegistry
from mcp_server import MCPServer


def test_parse_request():
    """Test request parsing."""
    print("Test 1: Request Parsing")
    handler = RequestHandler()
    
    # Valid request
    request = {"method": "test", "params": {"key": "value"}}
    parsed = handler.parse_request(request)
    assert parsed["method"] == "test"
    assert parsed["params"]["key"] == "value"
    
    # Invalid request
    invalid = handler.parse_request("not a dict")
    assert "error" in invalid
    print("✓ Request parsing working\n")


def test_route_method():
    """Test method routing."""
    print("Test 2: Method Routing")
    registry = ToolRegistry()
    handler = RequestHandler(registry)
    
    # Valid route
    result = handler.route_method("tools/list", {})
    assert "tools" in result
    
    # Invalid route
    result = handler.route_method("invalid/method", {})
    assert "error" in result
    print("✓ Method routing working\n")


def test_generate_response():
    """Test response generation."""
    print("Test 3: Response Generation")
    handler = RequestHandler()
    
    # Success response
    response = handler.generate_response(1, {"data": "test"})
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert response["result"]["status"] == "success"
    
    # Error response
    response = handler.generate_response(2, None, {"code": -32600, "message": "Error"})
    assert "error" in response
    print("✓ Response generation working\n")


def test_tools_list():
    """Test tools/list handler."""
    print("Test 4: tools/list Handler")
    registry = ToolRegistry()
    registry.register_tool({"name": "tool1", "description": "First"})
    registry.register_tool({"name": "tool2", "description": "Second"})
    
    handler = RequestHandler(registry)
    request = {"id": 1, "method": "tools/list", "params": {}}
    response = handler.handle_request(request)
    
    assert response["result"]["status"] == "success"
    assert response["result"]["data"]["count"] == 2
    print(f"✓ tools/list: {response['result']['data']['count']} tools\n")


def test_tools_invoke():
    """Test tools/invoke handler."""
    print("Test 5: tools/invoke Handler")
    registry = ToolRegistry()
    registry.register_tool({
        "name": "calculator",
        "description": "Calculate",
        "parameters": {
            "expression": {"type": "string", "required": True}
        }
    })
    
    handler = RequestHandler(registry)
    request = {
        "id": 1,
        "method": "tools/invoke",
        "params": {
            "name": "calculator",
            "arguments": {"expression": "2+2"}
        }
    }
    response = handler.handle_request(request)
    
    assert response["result"]["status"] == "success"
    assert response["result"]["data"]["tool"] == "calculator"
    print(f"✓ tools/invoke: {response['result']['data']['tool']}\n")


def test_parameter_validation():
    """Test parameter validation."""
    print("Test 6: Parameter Validation")
    registry = ToolRegistry()
    registry.register_tool({
        "name": "test_tool",
        "description": "Test",
        "parameters": {
            "required_param": {"type": "string", "required": True}
        }
    })
    
    handler = RequestHandler(registry)
    
    # Missing required parameter
    request = {
        "id": 1,
        "method": "tools/invoke",
        "params": {
            "name": "test_tool",
            "arguments": {}
        }
    }
    response = handler.handle_request(request)
    assert "error" in response["result"]["data"]
    print("✓ Parameter validation working\n")


def test_error_handling():
    """Test error handling."""
    print("Test 7: Error Handling")
    handler = RequestHandler()
    
    # Missing method
    request = {"params": {}}
    response = handler.handle_request(request)
    assert "error" in response
    
    # Invalid params
    request = {"method": "test", "params": "not a dict"}
    response = handler.handle_request(request)
    assert "error" in response
    
    # Tool not found
    registry = ToolRegistry()
    handler = RequestHandler(registry)
    request = {
        "method": "tools/invoke",
        "params": {"name": "nonexistent", "arguments": {}}
    }
    response = handler.handle_request(request)
    assert "error" in response["result"]["data"]
    print("✓ Error handling working\n")


def test_server_integration():
    """Test server integration with request handler."""
    print("Test 8: Server Integration")
    server = MCPServer("test-server", "1.0.0")
    server.start()
    
    # Register tool
    server.handle_request({
        "method": "tools/register",
        "params": {
            "tool": {
                "name": "search",
                "description": "Search tool",
                "parameters": {"query": {"type": "string", "required": True}}
            }
        }
    })
    
    # List tools via request handler
    response = server.handle_request({"method": "tools/list", "params": {}})
    assert response["result"]["status"] == "success"
    assert response["result"]["data"]["count"] == 1
    
    # Invoke tool via request handler
    response = server.handle_request({
        "method": "tools/invoke",
        "params": {
            "name": "search",
            "arguments": {"query": "test"}
        }
    })
    assert response["result"]["status"] == "success"
    print("✓ Server integration working\n")
    
    server.stop()


def test_request_id_handling():
    """Test request ID handling."""
    print("Test 9: Request ID Handling")
    registry = ToolRegistry()
    handler = RequestHandler(registry)
    
    # With ID
    request = {"id": 123, "method": "tools/list", "params": {}}
    response = handler.handle_request(request)
    assert response["id"] == 123
    
    # Without ID
    request = {"method": "tools/list", "params": {}}
    response = handler.handle_request(request)
    assert "id" not in response or response.get("id") is None
    print("✓ Request ID handling working\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Request Handler Tests")
    print("=" * 60 + "\n")
    
    test_parse_request()
    test_route_method()
    test_generate_response()
    test_tools_list()
    test_tools_invoke()
    test_parameter_validation()
    test_error_handling()
    test_server_integration()
    test_request_id_handling()
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
