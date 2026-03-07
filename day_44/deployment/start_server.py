#!/usr/bin/env python3
"""Quick start script for local MCP server."""

import sys
import json
from pathlib import Path

# Add day_43 to path
day_43_path = Path(__file__).parent.parent.parent / 'day_43'
sys.path.insert(0, str(day_43_path))

from mcp_server import MCPServer


def load_config():
    """Load configuration file."""
    config_path = Path(__file__).parent.parent / 'config' / 'config.local.json'
    
    if not config_path.exists():
        print(f"Config not found: {config_path}")
        return None
    
    with open(config_path) as f:
        return json.load(f)


def main():
    """Start MCP server with configuration."""
    print("=" * 50)
    print("MCP Server - Local Deployment")
    print("=" * 50)
    
    # Load config
    config = load_config()
    if not config:
        print("Using default configuration")
        config = {
            "server": {"name": "local-mcp-server", "version": "1.0.0"}
        }
    
    # Initialize server
    server_name = config['server']['name']
    server_version = config['server']['version']
    
    print(f"\nInitializing {server_name} v{server_version}...")
    server = MCPServer(server_name, server_version)
    
    # Start server
    print("Starting server...")
    response = server.start()
    print(json.dumps(response, indent=2))
    
    # Register example tool
    print("\nRegistering example tool...")
    register_request = {
        "method": "tools/register",
        "params": {
            "tool": {
                "name": "calculator",
                "description": "Basic calculator for arithmetic operations",
                "parameters": {
                    "expression": "string"
                }
            }
        }
    }
    response = server.handle_request(register_request)
    print(json.dumps(response, indent=2))
    
    # Get status
    print("\nServer status:")
    status_request = {"method": "status", "params": {}}
    response = server.handle_request(status_request)
    print(json.dumps(response, indent=2))
    
    print("\n" + "=" * 50)
    print("Server is running!")
    print("=" * 50)
    print("\nPress Ctrl+C to stop the server")
    
    try:
        # Keep server running
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping server...")
        response = server.stop()
        print(json.dumps(response, indent=2))
        print("\nServer stopped.")


if __name__ == "__main__":
    main()
