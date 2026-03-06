"""
Test suite for MCP Server lifecycle management.
"""

import json
from mcp_server import MCPServer


def test_initialization():
    """Test server initialization."""
    print("Test 1: Server Initialization")
    server = MCPServer("test-server", "1.0.0")
    assert server.server_name == "test-server"
    assert server.version == "1.0.0"
    assert server.is_running == False
    print("✓ Initialization successful\n")


def test_startup():
    """Test server startup."""
    print("Test 2: Server Startup")
    server = MCPServer("test-server", "1.0.0")
    response = server.start()
    
    assert response["jsonrpc"] == "2.0"
    assert response["result"]["status"] == "success"
    assert response["result"]["data"]["status"] == "running"
    assert server.is_running == True
    print(f"✓ Server started: {json.dumps(response, indent=2)}\n")


def test_shutdown():
    """Test server shutdown."""
    print("Test 3: Server Shutdown")
    server = MCPServer("test-server", "1.0.0")
    server.start()
    response = server.stop()
    
    assert response["result"]["status"] == "success"
    assert response["result"]["data"]["status"] == "stopped"
    assert server.is_running == False
    print(f"✓ Server stopped: {json.dumps(response, indent=2)}\n")


def test_request_handling():
    """Test basic request handling."""
    print("Test 4: Request Handling")
    server = MCPServer("test-server", "1.0.0")
    server.start()
    
    # Test ping
    ping_request = {"method": "ping", "params": {}}
    response = server.handle_request(ping_request)
    assert response["result"]["data"]["message"] == "pong"
    print(f"✓ Ping request: {json.dumps(response, indent=2)}\n")
    
    # Test status
    status_request = {"method": "status", "params": {}}
    response = server.handle_request(status_request)
    assert response["result"]["data"]["status"] == "running"
    print(f"✓ Status request: {json.dumps(response, indent=2)}\n")
    
    server.stop()


def test_mcp_message_format():
    """Test MCP message format compliance."""
    print("Test 5: MCP Message Format")
    server = MCPServer("test-server", "1.0.0")
    response = server.start()
    
    # Verify JSON-RPC 2.0 format
    assert "jsonrpc" in response
    assert response["jsonrpc"] == "2.0"
    assert "result" in response
    assert "status" in response["result"]
    assert "data" in response["result"]
    assert "timestamp" in response["result"]
    print("✓ MCP message format valid\n")
    
    server.stop()


def test_error_handling():
    """Test error handling."""
    print("Test 6: Error Handling")
    server = MCPServer("test-server", "1.0.0")
    
    # Test request on stopped server
    request = {"method": "ping", "params": {}}
    response = server.handle_request(request)
    assert response["result"]["status"] == "error"
    print(f"✓ Error handling: {json.dumps(response, indent=2)}\n")


if __name__ == "__main__":
    print("=" * 50)
    print("MCP Server Lifecycle Tests")
    print("=" * 50 + "\n")
    
    test_initialization()
    test_startup()
    test_shutdown()
    test_request_handling()
    test_mcp_message_format()
    test_error_handling()
    
    print("=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)
