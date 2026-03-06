"""
MCP Server - Basic skeleton with initialization and lifecycle management.
Implements Model Context Protocol message format.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from tool_registry import ToolRegistry
from request_handler import RequestHandler


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServer:
    """Basic MCP Server with lifecycle management."""
    
    def __init__(self, server_name: str = "mcp-server", version: str = "1.0.0"):
        """Initialize the MCP server.
        
        Args:
            server_name: Name of the server
            version: Server version
        """
        self.server_name = server_name
        self.version = version
        self.is_running = False
        self.start_time = None
        self.registry = ToolRegistry()
        self.request_handler = RequestHandler(self.registry)
        logger.info(f"Initialized {server_name} v{version}")
    
    def start(self) -> Dict[str, Any]:
        """Start the MCP server.
        
        Returns:
            MCP-formatted response message
        """
        if self.is_running:
            return self._create_response("error", {"message": "Server already running"})
        
        self.is_running = True
        self.start_time = datetime.now()
        logger.info(f"Server {self.server_name} started at {self.start_time}")
        
        return self._create_response("success", {
            "server": self.server_name,
            "version": self.version,
            "status": "running",
            "start_time": self.start_time.isoformat()
        })
    
    def stop(self) -> Dict[str, Any]:
        """Stop the MCP server.
        
        Returns:
            MCP-formatted response message
        """
        if not self.is_running:
            return self._create_response("error", {"message": "Server not running"})
        
        uptime = (datetime.now() - self.start_time).total_seconds()
        self.is_running = False
        logger.info(f"Server {self.server_name} stopped after {uptime:.2f}s")
        
        return self._create_response("success", {
            "server": self.server_name,
            "status": "stopped",
            "uptime_seconds": uptime
        })
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests.
        
        Args:
            request: MCP-formatted request message
            
        Returns:
            MCP-formatted response message
        """
        if not self.is_running:
            return self._create_response("error", {"message": "Server not running"})
        
        method = request.get("method")
        params = request.get("params", {})
        
        logger.info(f"Handling request: {method}")
        
        # Handle server methods
        if method == "ping":
            return self._create_response("success", {"message": "pong"})
        elif method == "status":
            return self._get_status()
        elif method == "tools/register":
            return self._register_tool(params)
        elif method == "tools/remove":
            return self._remove_tool(params)
        # Use request handler for other tools/* methods
        elif method and method.startswith("tools/"):
            return self.request_handler.handle_request(request)
        else:
            return self._create_response("error", {
                "message": f"Unknown method: {method}"
            })
    
    def _get_status(self) -> Dict[str, Any]:
        """Get server status.
        
        Returns:
            MCP-formatted status response
        """
        uptime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return self._create_response("success", {
            "server": self.server_name,
            "version": self.version,
            "status": "running" if self.is_running else "stopped",
            "uptime_seconds": uptime,
            "registered_tools": self.registry.count()
        })
    
    def _register_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Register a tool."""
        tool = params.get("tool")
        if not tool:
            return self._create_response("error", {"message": "Tool definition required"})
        
        result = self.registry.register_tool(tool)
        status = "success" if result["success"] else "error"
        return self._create_response(status, result)
    
    def _remove_tool(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove a tool."""
        name = params.get("name")
        if not name:
            return self._create_response("error", {"message": "Tool name required"})
        
        result = self.registry.remove_tool(name)
        status = "success" if result["success"] else "error"
        return self._create_response(status, result)
    
    def _create_response(self, status: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create MCP-formatted response message.
        
        Args:
            status: Response status (success/error)
            data: Response data
            
        Returns:
            MCP-formatted response
        """
        return {
            "jsonrpc": "2.0",
            "result": {
                "status": status,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
        }


if __name__ == "__main__":
    # Test server lifecycle
    server = MCPServer("test-server", "1.0.0")
    
    # Start server
    print("Starting server...")
    response = server.start()
    print(json.dumps(response, indent=2))
    
    # Handle requests
    print("\nSending ping request...")
    ping_request = {"method": "ping", "params": {}}
    response = server.handle_request(ping_request)
    print(json.dumps(response, indent=2))
    
    print("\nSending status request...")
    status_request = {"method": "status", "params": {}}
    response = server.handle_request(status_request)
    print(json.dumps(response, indent=2))
    
    # Stop server
    print("\nStopping server...")
    response = server.stop()
    print(json.dumps(response, indent=2))
