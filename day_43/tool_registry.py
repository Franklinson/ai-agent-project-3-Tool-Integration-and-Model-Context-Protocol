"""
Tool Registry - Dynamic tool registration and management system.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class ToolRegistry:
    """Registry for managing tool registration and metadata."""
    
    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, Dict[str, Any]] = {}
        logger.info("Tool registry initialized")
    
    def register_tool(self, tool: Dict[str, Any]) -> Dict[str, Any]:
        """Register a tool with metadata.
        
        Args:
            tool: Tool definition with name, description, and parameters
            
        Returns:
            Registration result
        """
        name = tool.get("name")
        if not name:
            return {"success": False, "error": "Tool name required"}
        
        if name in self._tools:
            return {"success": False, "error": f"Tool '{name}' already registered"}
        
        self._tools[name] = {
            **tool,
            "registered_at": datetime.now().isoformat()
        }
        logger.info(f"Registered tool: {name}")
        return {"success": True, "tool": name}
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools.
        
        Returns:
            List of tool metadata
        """
        return list(self._tools.values())
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool metadata or None
        """
        return self._tools.get(name)
    
    def remove_tool(self, name: str) -> Dict[str, Any]:
        """Remove a tool from registry.
        
        Args:
            name: Tool name
            
        Returns:
            Removal result
        """
        if name not in self._tools:
            return {"success": False, "error": f"Tool '{name}' not found"}
        
        del self._tools[name]
        logger.info(f"Removed tool: {name}")
        return {"success": True, "tool": name}
    
    def count(self) -> int:
        """Get number of registered tools."""
        return len(self._tools)


if __name__ == "__main__":
    # Test registry
    registry = ToolRegistry()
    
    # Register tools
    tool1 = {
        "name": "calculator",
        "description": "Perform calculations",
        "parameters": {"expression": "string"}
    }
    print("Registering tool:", registry.register_tool(tool1))
    
    tool2 = {
        "name": "weather",
        "description": "Get weather info",
        "parameters": {"location": "string"}
    }
    print("Registering tool:", registry.register_tool(tool2))
    
    # List tools
    print("\nRegistered tools:", registry.list_tools())
    
    # Get tool
    print("\nGet calculator:", registry.get_tool("calculator"))
    
    # Remove tool
    print("\nRemove weather:", registry.remove_tool("weather"))
    print("Tool count:", registry.count())
