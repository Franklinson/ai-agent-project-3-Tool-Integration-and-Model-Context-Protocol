"""
MCP Tool Discovery Client
Implements tool discovery mechanism for MCP servers.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ToolMetadata:
    """Tool metadata structure"""
    name: str
    description: str
    inputSchema: Dict[str, Any]
    category: Optional[str] = None
    version: Optional[str] = None


@dataclass
class ServerInfo:
    """Server information"""
    name: str
    version: str
    capabilities: Dict[str, Any] = field(default_factory=dict)


class ToolDiscoveryClient:
    """MCP Tool Discovery Client"""
    
    def __init__(self):
        self._cache: Dict[str, List[ToolMetadata]] = {}
        self._cache_timestamp: Dict[str, datetime] = {}
        self._server_info: Dict[str, ServerInfo] = {}
    
    async def discover_tools(self, server_id: str = "default") -> List[ToolMetadata]:
        """
        Discover available tools from server
        
        Args:
            server_id: Server identifier
            
        Returns:
            List of tool metadata
        """
        # Check cache
        if server_id in self._cache:
            return self._cache[server_id]
        
        # Send MCP tools/list request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
        
        # Simulate server response (in real implementation, send via transport)
        response = await self._send_request(request, server_id)
        
        # Parse tools
        tools = []
        if "result" in response and "tools" in response["result"]:
            for tool_data in response["result"]["tools"]:
                tools.append(ToolMetadata(
                    name=tool_data["name"],
                    description=tool_data["description"],
                    inputSchema=tool_data["inputSchema"],
                    category=tool_data.get("category"),
                    version=tool_data.get("version")
                ))
        
        # Cache results
        self._cache[server_id] = tools
        self._cache_timestamp[server_id] = datetime.now()
        
        return tools
    
    async def get_tool_metadata(self, tool_name: str, server_id: str = "default") -> Optional[ToolMetadata]:
        """
        Get metadata for specific tool
        
        Args:
            tool_name: Name of the tool
            server_id: Server identifier
            
        Returns:
            Tool metadata or None if not found
        """
        tools = await self.discover_tools(server_id)
        
        for tool in tools:
            if tool.name == tool_name:
                return tool
        
        return None
    
    def filter_tools(self, criteria: Dict[str, Any], server_id: str = "default") -> List[ToolMetadata]:
        """
        Filter tools by criteria
        
        Args:
            criteria: Filter criteria (e.g., {"category": "database"})
            server_id: Server identifier
            
        Returns:
            Filtered list of tools
        """
        if server_id not in self._cache:
            return []
        
        tools = self._cache[server_id]
        filtered = []
        
        for tool in tools:
            match = True
            for key, value in criteria.items():
                if key == "category" and tool.category != value:
                    match = False
                    break
                elif key == "name" and value.lower() not in tool.name.lower():
                    match = False
                    break
            
            if match:
                filtered.append(tool)
        
        return filtered
    
    def clear_cache(self, server_id: Optional[str] = None):
        """Clear tool cache"""
        if server_id:
            self._cache.pop(server_id, None)
            self._cache_timestamp.pop(server_id, None)
        else:
            self._cache.clear()
            self._cache_timestamp.clear()
    
    async def _send_request(self, request: Dict[str, Any], server_id: str) -> Dict[str, Any]:
        """
        Send request to server (mock implementation)
        
        Args:
            request: JSON-RPC request
            server_id: Server identifier
            
        Returns:
            JSON-RPC response
        """
        # Mock response for testing
        if request["method"] == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "tools": [
                        {
                            "name": "query_database",
                            "description": "Execute SQL queries",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"}
                                },
                                "required": ["query"]
                            },
                            "category": "database"
                        },
                        {
                            "name": "send_email",
                            "description": "Send email messages",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "to": {"type": "string"},
                                    "subject": {"type": "string"},
                                    "body": {"type": "string"}
                                },
                                "required": ["to", "subject", "body"]
                            },
                            "category": "communication"
                        },
                        {
                            "name": "web_search",
                            "description": "Search the web",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string"},
                                    "limit": {"type": "integer"}
                                },
                                "required": ["query"]
                            },
                            "category": "search"
                        }
                    ]
                }
            }
        
        return {"jsonrpc": "2.0", "id": request["id"], "result": {}}


async def main():
    """Demo usage"""
    client = ToolDiscoveryClient()
    
    # Discover tools
    print("=== Discovering Tools ===")
    tools = await client.discover_tools()
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # Get specific tool metadata
    print("\n=== Tool Metadata ===")
    metadata = await client.get_tool_metadata("query_database")
    if metadata:
        print(f"Name: {metadata.name}")
        print(f"Description: {metadata.description}")
        print(f"Schema: {metadata.inputSchema}")
    
    # Filter tools
    print("\n=== Filtered Tools (database) ===")
    db_tools = client.filter_tools({"category": "database"})
    for tool in db_tools:
        print(f"- {tool.name}")
    
    print("\n=== Filtered Tools (name contains 'email') ===")
    email_tools = client.filter_tools({"name": "email"})
    for tool in email_tools:
        print(f"- {tool.name}")


if __name__ == "__main__":
    asyncio.run(main())
