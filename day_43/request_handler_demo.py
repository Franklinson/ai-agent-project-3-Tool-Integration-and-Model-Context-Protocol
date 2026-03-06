"""
Integration example demonstrating request handler with MCP server.
"""

import json
from mcp_server import MCPServer


def print_response(title, response):
    """Pretty print response."""
    print(f"\n{title}")
    print("-" * 60)
    print(json.dumps(response, indent=2))


def main():
    print("=" * 60)
    print("MCP Server Request Handler Demo")
    print("=" * 60)
    
    # Initialize and start server
    server = MCPServer("demo-server", "1.0.0")
    server.start()
    print("\n✓ Server started")
    
    # Register tools
    print("\n" + "=" * 60)
    print("1. Registering Tools")
    print("=" * 60)
    
    tools = [
        {
            "name": "calculator",
            "description": "Perform mathematical calculations",
            "parameters": {
                "expression": {"type": "string", "required": True}
            }
        },
        {
            "name": "weather",
            "description": "Get weather information",
            "parameters": {
                "location": {"type": "string", "required": True},
                "units": {"type": "string", "required": False}
            }
        }
    ]
    
    for tool in tools:
        response = server.handle_request({
            "id": 1,
            "method": "tools/register",
            "params": {"tool": tool}
        })
        print(f"  ✓ Registered: {tool['name']}")
    
    # List tools using request handler
    print("\n" + "=" * 60)
    print("2. Listing Tools (via Request Handler)")
    print("=" * 60)
    
    response = server.handle_request({
        "id": 2,
        "method": "tools/list",
        "params": {}
    })
    print_response("Response:", response)
    
    # Invoke calculator tool
    print("\n" + "=" * 60)
    print("3. Invoking Calculator Tool")
    print("=" * 60)
    
    response = server.handle_request({
        "id": 3,
        "method": "tools/invoke",
        "params": {
            "name": "calculator",
            "arguments": {"expression": "10 + 5 * 2"}
        }
    })
    print_response("Response:", response)
    
    # Invoke weather tool
    print("\n" + "=" * 60)
    print("4. Invoking Weather Tool")
    print("=" * 60)
    
    response = server.handle_request({
        "id": 4,
        "method": "tools/invoke",
        "params": {
            "name": "weather",
            "arguments": {
                "location": "San Francisco",
                "units": "celsius"
            }
        }
    })
    print_response("Response:", response)
    
    # Test error handling - missing required parameter
    print("\n" + "=" * 60)
    print("5. Error Handling - Missing Required Parameter")
    print("=" * 60)
    
    response = server.handle_request({
        "id": 5,
        "method": "tools/invoke",
        "params": {
            "name": "calculator",
            "arguments": {}  # Missing required 'expression'
        }
    })
    print_response("Response:", response)
    
    # Test error handling - tool not found
    print("\n" + "=" * 60)
    print("6. Error Handling - Tool Not Found")
    print("=" * 60)
    
    response = server.handle_request({
        "id": 6,
        "method": "tools/invoke",
        "params": {
            "name": "nonexistent_tool",
            "arguments": {}
        }
    })
    print_response("Response:", response)
    
    # Test error handling - invalid method
    print("\n" + "=" * 60)
    print("7. Error Handling - Invalid Method")
    print("=" * 60)
    
    response = server.handle_request({
        "id": 7,
        "method": "invalid/method",
        "params": {}
    })
    print_response("Response:", response)
    
    # Server status
    print("\n" + "=" * 60)
    print("8. Server Status")
    print("=" * 60)
    
    response = server.handle_request({
        "id": 8,
        "method": "status",
        "params": {}
    })
    print_response("Response:", response)
    
    # Stop server
    print("\n" + "=" * 60)
    server.stop()
    print("✓ Server stopped")
    print("=" * 60)


if __name__ == "__main__":
    main()
