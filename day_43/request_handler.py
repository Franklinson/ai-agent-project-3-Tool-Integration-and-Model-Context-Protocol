"""
Request Handler - Processes and routes MCP requests.
"""

import logging
from typing import Dict, Any, Optional, Callable
from datetime import datetime


logger = logging.getLogger(__name__)


class RequestHandler:
    """Handles MCP request parsing, routing, and response generation."""
    
    def __init__(self, tool_registry=None):
        """Initialize request handler.
        
        Args:
            tool_registry: ToolRegistry instance for tool operations
        """
        self.tool_registry = tool_registry
        self.routes: Dict[str, Callable] = {}
        self._register_routes()
    
    def _register_routes(self):
        """Register method routes."""
        self.routes = {
            "tools/list": self._handle_tools_list,
            "tools/invoke": self._handle_tools_invoke
        }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP request.
        
        Args:
            request: MCP request with method and params
            
        Returns:
            MCP-formatted response
        """
        try:
            parsed = self.parse_request(request)
            if "error" in parsed:
                return self.generate_response(
                    request.get("id"),
                    None,
                    parsed["error"]
                )
            
            method = parsed["method"]
            params = parsed["params"]
            request_id = parsed.get("id")
            
            result = self.route_method(method, params)
            return self.generate_response(request_id, result)
            
        except Exception as e:
            logger.error(f"Request handling error: {e}")
            return self.generate_response(
                request.get("id"),
                None,
                {"code": -32603, "message": f"Internal error: {str(e)}"}
            )
    
    def parse_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate request.
        
        Args:
            request: Raw request
            
        Returns:
            Parsed request or error
        """
        if not isinstance(request, dict):
            return {"error": {"code": -32600, "message": "Invalid request format"}}
        
        method = request.get("method")
        if not method:
            return {"error": {"code": -32600, "message": "Method required"}}
        
        params = request.get("params", {})
        if not isinstance(params, dict):
            return {"error": {"code": -32602, "message": "Invalid params"}}
        
        return {
            "method": method,
            "params": params,
            "id": request.get("id")
        }
    
    def route_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Route method to appropriate handler.
        
        Args:
            method: Method name
            params: Method parameters
            
        Returns:
            Handler result
        """
        handler = self.routes.get(method)
        if not handler:
            return {
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
        
        return handler(params)
    
    def generate_response(
        self,
        request_id: Optional[Any],
        result: Optional[Dict[str, Any]],
        error: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate MCP-formatted response.
        
        Args:
            request_id: Request ID
            result: Result data
            error: Error data
            
        Returns:
            MCP response
        """
        response = {"jsonrpc": "2.0"}
        
        if request_id is not None:
            response["id"] = request_id
        
        if error:
            response["error"] = error
        else:
            response["result"] = {
                "status": "success" if not result.get("error") else "error",
                "data": result,
                "timestamp": datetime.now().isoformat()
            }
        
        return response
    
    def _handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request.
        
        Args:
            params: Request parameters
            
        Returns:
            List of tools
        """
        if not self.tool_registry:
            return {"error": {"code": -32603, "message": "Tool registry not available"}}
        
        tools = self.tool_registry.list_tools()
        return {"tools": tools, "count": len(tools)}
    
    def _handle_tools_invoke(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/invoke request.
        
        Args:
            params: Request parameters with tool name and arguments
            
        Returns:
            Tool invocation result
        """
        if not self.tool_registry:
            return {"error": {"code": -32603, "message": "Tool registry not available"}}
        
        tool_name = params.get("name")
        if not tool_name:
            return {"error": {"code": -32602, "message": "Tool name required"}}
        
        tool = self.tool_registry.get_tool(tool_name)
        if not tool:
            return {"error": {"code": -32602, "message": f"Tool '{tool_name}' not found"}}
        
        arguments = params.get("arguments", {})
        
        # Validate required parameters
        tool_params = tool.get("parameters", {})
        for param_name, param_spec in tool_params.items():
            if isinstance(param_spec, dict) and param_spec.get("required"):
                if param_name not in arguments:
                    return {
                        "error": {
                            "code": -32602,
                            "message": f"Required parameter '{param_name}' missing"
                        }
                    }
        
        # Simulate tool execution (actual execution would be implemented separately)
        return {
            "tool": tool_name,
            "arguments": arguments,
            "result": "Tool execution simulated",
            "executed_at": datetime.now().isoformat()
        }


if __name__ == "__main__":
    from tool_registry import ToolRegistry
    
    # Test request handler
    registry = ToolRegistry()
    registry.register_tool({
        "name": "calculator",
        "description": "Perform calculations",
        "parameters": {
            "expression": {"type": "string", "required": True}
        }
    })
    
    handler = RequestHandler(registry)
    
    # Test tools/list
    print("Test 1: tools/list")
    request = {"id": 1, "method": "tools/list", "params": {}}
    response = handler.handle_request(request)
    print(response)
    
    # Test tools/invoke
    print("\nTest 2: tools/invoke")
    request = {
        "id": 2,
        "method": "tools/invoke",
        "params": {
            "name": "calculator",
            "arguments": {"expression": "2+2"}
        }
    }
    response = handler.handle_request(request)
    print(response)
    
    # Test error handling
    print("\nTest 3: Invalid method")
    request = {"id": 3, "method": "invalid/method", "params": {}}
    response = handler.handle_request(request)
    print(response)
