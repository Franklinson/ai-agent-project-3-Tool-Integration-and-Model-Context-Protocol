"""
Test suite for Tool Registry and MCP Server integration.
"""

import json
from tool_registry import ToolRegistry
from mcp_server import MCPServer


def test_registry_registration():
    """Test tool registration."""
    print("Test 1: Tool Registration")
    registry = ToolRegistry()
    
    tool = {
        "name": "calculator",
        "description": "Perform calculations",
        "parameters": {"expression": "string"}
    }
    result = registry.register_tool(tool)
    assert result["success"] == True
    assert registry.count() == 1
    print(f"✓ Tool registered: {result}\n")


def test_registry_listing():
    """Test tool listing."""
    print("Test 2: Tool Listing")
    registry = ToolRegistry()
    
    registry.register_tool({"name": "tool1", "description": "First tool"})
    registry.register_tool({"name": "tool2", "description": "Second tool"})
    
    tools = registry.list_tools()
    assert len(tools) == 2
    assert tools[0]["name"] == "tool1"
    print(f"✓ Listed {len(tools)} tools\n")


def test_registry_lookup():
    """Test tool lookup."""
    print("Test 3: Tool Lookup")
    registry = ToolRegistry()
    
    tool = {"name": "weather", "description": "Get weather"}
    registry.register_tool(tool)
    
    found = registry.get_tool("weather")
    assert found is not None
    assert found["name"] == "weather"
    
    not_found = registry.get_tool("nonexistent")
    assert not_found is None
    print("✓ Tool lookup working\n")


def test_registry_removal():
    """Test tool removal."""
    print("Test 4: Tool Removal")
    registry = ToolRegistry()
    
    registry.register_tool({"name": "temp", "description": "Temporary"})
    assert registry.count() == 1
    
    result = registry.remove_tool("temp")
    assert result["success"] == True
    assert registry.count() == 0
    print(f"✓ Tool removed: {result}\n")


def test_server_integration():
    """Test server integration with registry."""
    print("Test 5: Server Integration")
    server = MCPServer("test-server", "1.0.0")
    server.start()
    
    # Register tool via server
    request = {
        "method": "tools/register",
        "params": {
            "tool": {
                "name": "calculator",
                "description": "Math operations",
                "parameters": {"expr": "string"}
            }
        }
    }
    response = server.handle_request(request)
    assert response["result"]["status"] == "success"
    print(f"✓ Tool registered via server: {json.dumps(response, indent=2)}\n")
    
    server.stop()


def test_server_list_tools():
    """Test listing tools via server."""
    print("Test 6: Server List Tools")
    server = MCPServer("test-server", "1.0.0")
    server.start()
    
    # Register multiple tools
    server.handle_request({
        "method": "tools/register",
        "params": {"tool": {"name": "tool1", "description": "First"}}
    })
    server.handle_request({
        "method": "tools/register",
        "params": {"tool": {"name": "tool2", "description": "Second"}}
    })
    
    # List tools
    response = server.handle_request({"method": "tools/list", "params": {}})
    assert response["result"]["status"] == "success"
    assert response["result"]["data"]["count"] == 2
    print(f"✓ Listed tools: {json.dumps(response, indent=2)}\n")
    
    server.stop()


def test_server_get_tool():
    """Test getting specific tool via server."""
    print("Test 7: Server Get Tool")
    server = MCPServer("test-server", "1.0.0")
    server.start()
    
    # Register tool
    server.handle_request({
        "method": "tools/register",
        "params": {"tool": {"name": "weather", "description": "Weather info"}}
    })
    
    # Get tool
    response = server.handle_request({
        "method": "tools/get",
        "params": {"name": "weather"}
    })
    assert response["result"]["status"] == "success"
    assert response["result"]["data"]["tool"]["name"] == "weather"
    print(f"✓ Got tool: {json.dumps(response, indent=2)}\n")
    
    server.stop()


def test_server_remove_tool():
    """Test removing tool via server."""
    print("Test 8: Server Remove Tool")
    server = MCPServer("test-server", "1.0.0")
    server.start()
    
    # Register and remove
    server.handle_request({
        "method": "tools/register",
        "params": {"tool": {"name": "temp", "description": "Temporary"}}
    })
    
    response = server.handle_request({
        "method": "tools/remove",
        "params": {"name": "temp"}
    })
    assert response["result"]["status"] == "success"
    print(f"✓ Removed tool: {json.dumps(response, indent=2)}\n")
    
    server.stop()


def test_dynamic_registration():
    """Test dynamic registration during runtime."""
    print("Test 9: Dynamic Registration")
    server = MCPServer("test-server", "1.0.0")
    server.start()
    
    # Register tools dynamically
    tools = [
        {"name": "search", "description": "Search tool"},
        {"name": "translate", "description": "Translation tool"},
        {"name": "summarize", "description": "Summary tool"}
    ]
    
    for tool in tools:
        response = server.handle_request({
            "method": "tools/register",
            "params": {"tool": tool}
        })
        assert response["result"]["status"] == "success"
    
    # Verify count in status
    status = server.handle_request({"method": "status", "params": {}})
    assert status["result"]["data"]["registered_tools"] == 3
    print(f"✓ Dynamic registration: {status['result']['data']['registered_tools']} tools\n")
    
    server.stop()


if __name__ == "__main__":
    print("=" * 60)
    print("Tool Registry Tests")
    print("=" * 60 + "\n")
    
    test_registry_registration()
    test_registry_listing()
    test_registry_lookup()
    test_registry_removal()
    test_server_integration()
    test_server_list_tools()
    test_server_get_tool()
    test_server_remove_tool()
    test_dynamic_registration()
    
    print("=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
