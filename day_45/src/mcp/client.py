"""
Enhanced MCP Client with Caching
Integrates caching layer for tool metadata, discovery, and responses.
"""

import hashlib
import json
from typing import Dict, Any, List, Optional
from cache import MCPCache


class MCPClient:
    """Enhanced MCP Client with caching capabilities"""
    
    def __init__(self, 
                 server_url: str = "http://localhost:8080",
                 cache_config: Optional[Dict[str, Any]] = None):
        self.server_url = server_url
        self.server_id = self._extract_server_id(server_url)
        
        # Initialize cache with config
        config = cache_config or {}
        self.cache = MCPCache(
            tool_metadata_ttl=config.get("tool_metadata_ttl", 600),
            discovery_ttl=config.get("discovery_ttl", 300),
            response_ttl=config.get("response_ttl", 60),
            max_size=config.get("max_size", 1000)
        )
    
    async def discover_tools(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Discover available tools from server
        
        Args:
            force_refresh: Skip cache and fetch from server
            
        Returns:
            List of tool definitions
        """
        # Check cache first
        if not force_refresh:
            cached = self.cache.get_discovery_result(self.server_id)
            if cached is not None:
                return cached
        
        # Fetch from server
        tools = await self._fetch_tools()
        
        # Cache result
        self.cache.set_discovery_result(self.server_id, tools)
        
        # Cache individual tool metadata
        for tool in tools:
            self.cache.set_tool_metadata(tool["name"], self.server_id, tool)
        
        return tools
    
    async def get_tool_schema(self, tool_name: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get tool schema/metadata
        
        Args:
            tool_name: Name of the tool
            force_refresh: Skip cache and fetch from server
            
        Returns:
            Tool schema or None if not found
        """
        # Check cache first
        if not force_refresh:
            cached = self.cache.get_tool_metadata(tool_name, self.server_id)
            if cached is not None:
                return cached
        
        # Fetch from server
        schema = await self._fetch_tool_schema(tool_name)
        
        if schema:
            # Cache result
            self.cache.set_tool_metadata(tool_name, self.server_id, schema)
        
        return schema
    
    async def invoke_tool(self, 
                         tool_name: str, 
                         params: Dict[str, Any],
                         use_cache: bool = True,
                         cache_ttl: Optional[float] = None) -> Dict[str, Any]:
        """
        Invoke a tool with caching support
        
        Args:
            tool_name: Name of the tool to invoke
            params: Tool parameters
            use_cache: Whether to use cached responses
            cache_ttl: Custom TTL for this response
            
        Returns:
            Tool execution result
        """
        # Generate cache key from params
        params_hash = self._hash_params(params)
        
        # Check cache first
        if use_cache:
            cached = self.cache.get_response(tool_name, params_hash)
            if cached is not None:
                cached["from_cache"] = True
                return cached
        
        # Execute tool
        result = await self._execute_tool(tool_name, params)
        
        # Cache successful responses
        if result.get("success"):
            self.cache.set_response(tool_name, params_hash, result, cache_ttl)
        
        result["from_cache"] = False
        return result
    
    def invalidate_tool_cache(self, tool_name: str):
        """Invalidate all cache entries for a specific tool"""
        self.cache.invalidate_tool(tool_name, self.server_id)
    
    def invalidate_all_cache(self):
        """Invalidate all cache entries"""
        self.cache.clear_all()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return self.cache.stats()
    
    # Private methods
    def _extract_server_id(self, url: str) -> str:
        """Extract server ID from URL"""
        return hashlib.md5(url.encode()).hexdigest()[:8]
    
    def _hash_params(self, params: Dict[str, Any]) -> str:
        """Generate hash from parameters for cache key"""
        params_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(params_str.encode()).hexdigest()
    
    async def _fetch_tools(self) -> List[Dict[str, Any]]:
        """Fetch tools from server (mock implementation)"""
        # Mock implementation - replace with actual HTTP call
        return [
            {
                "name": "query_database",
                "description": "Query database",
                "category": "database",
                "parameters": {"query": {"type": "string", "required": True}}
            },
            {
                "name": "web_search",
                "description": "Search the web",
                "category": "search",
                "parameters": {"query": {"type": "string", "required": True}}
            },
            {
                "name": "send_email",
                "description": "Send email",
                "category": "communication",
                "parameters": {
                    "to": {"type": "string", "required": True},
                    "subject": {"type": "string", "required": True},
                    "body": {"type": "string", "required": True}
                }
            }
        ]
    
    async def _fetch_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Fetch tool schema from server (mock implementation)"""
        tools = await self._fetch_tools()
        for tool in tools:
            if tool["name"] == tool_name:
                return tool
        return None
    
    async def _execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool on server (mock implementation)"""
        # Mock implementation - replace with actual HTTP call
        return {
            "success": True,
            "tool": tool_name,
            "result": f"Executed {tool_name} with params: {params}",
            "execution_time": 0.1
        }


class MultiServerMCPClient:
    """MCP Client supporting multiple servers with unified caching"""
    
    def __init__(self, servers: List[str], cache_config: Optional[Dict[str, Any]] = None):
        self.clients = {url: MCPClient(url, cache_config) for url in servers}
        self.primary_server = servers[0] if servers else None
    
    async def discover_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Discover tools from all servers"""
        results = {}
        for url, client in self.clients.items():
            results[url] = await client.discover_tools()
        return results
    
    async def invoke_tool(self, tool_name: str, params: Dict[str, Any], 
                         server_url: Optional[str] = None) -> Dict[str, Any]:
        """Invoke tool on specified server or primary"""
        target_url = server_url or self.primary_server
        if target_url not in self.clients:
            return {"success": False, "error": "Server not found"}
        
        return await self.clients[target_url].invoke_tool(tool_name, params)
    
    def get_all_cache_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get cache statistics from all servers"""
        return {url: client.get_cache_stats() for url, client in self.clients.items()}
    
    def invalidate_all_caches(self):
        """Invalidate caches on all servers"""
        for client in self.clients.values():
            client.invalidate_all_cache()
