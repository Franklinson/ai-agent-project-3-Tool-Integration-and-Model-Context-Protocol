"""
Server Manager for MCP
Handles multiple servers with load balancing, failover, and conflict resolution.
"""

import time
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServerInfo:
    """Server information and health status"""
    url: str
    priority: int = 0
    healthy: bool = True
    last_check: float = field(default_factory=time.time)
    failure_count: int = 0
    request_count: int = 0
    response_time: float = 0.0
    
    def mark_failure(self):
        """Mark server as failed"""
        self.failure_count += 1
        if self.failure_count >= 3:
            self.healthy = False
    
    def mark_success(self, response_time: float):
        """Mark successful request"""
        self.healthy = True
        self.failure_count = 0
        self.request_count += 1
        self.response_time = response_time


@dataclass
class ToolInfo:
    """Tool information with server mapping"""
    name: str
    server_url: str
    priority: int
    metadata: Dict[str, Any]


class ServerManager:
    """Manages multiple MCP servers with load balancing and failover"""
    
    def __init__(self, health_check_interval: float = 30.0):
        self.servers: Dict[str, ServerInfo] = {}
        self.tools: Dict[str, List[ToolInfo]] = defaultdict(list)
        self.health_check_interval = health_check_interval
        self._health_check_task = None
    
    def add_server(self, url: str, priority: int = 0):
        """Add server to manager"""
        self.servers[url] = ServerInfo(url=url, priority=priority)
        logger.info(f"Added server: {url} (priority: {priority})")
    
    def remove_server(self, url: str):
        """Remove server from manager"""
        if url in self.servers:
            del self.servers[url]
            # Remove tools from this server
            for tool_name in list(self.tools.keys()):
                self.tools[tool_name] = [t for t in self.tools[tool_name] if t.server_url != url]
            logger.info(f"Removed server: {url}")
    
    async def discover_tools(self) -> Dict[str, List[ToolInfo]]:
        """Discover tools from all healthy servers"""
        self.tools.clear()
        
        for url, server in self.servers.items():
            if not server.healthy:
                continue
            
            try:
                tools = await self._fetch_tools(url)
                for tool in tools:
                    tool_info = ToolInfo(
                        name=tool["name"],
                        server_url=url,
                        priority=server.priority,
                        metadata=tool
                    )
                    self.tools[tool["name"]].append(tool_info)
                
                logger.info(f"Discovered {len(tools)} tools from {url}")
            except Exception as e:
                logger.error(f"Failed to discover tools from {url}: {e}")
                server.mark_failure()
        
        # Log conflicts
        self._log_conflicts()
        return dict(self.tools)
    
    def get_tool(self, tool_name: str) -> Optional[ToolInfo]:
        """Get tool with conflict resolution (priority-based)"""
        if tool_name not in self.tools:
            return None
        
        # Filter healthy servers
        available = [t for t in self.tools[tool_name] 
                    if self.servers[t.server_url].healthy]
        
        if not available:
            return None
        
        # Sort by priority (higher first), then by server health
        available.sort(key=lambda t: (
            -t.priority,
            -self.servers[t.server_url].request_count
        ))
        
        return available[0]
    
    def select_server(self, tool_name: Optional[str] = None) -> Optional[str]:
        """Select server using load balancing"""
        healthy = [s for s in self.servers.values() if s.healthy]
        
        if not healthy:
            return None
        
        # If tool specified, use tool-specific selection
        if tool_name:
            tool = self.get_tool(tool_name)
            return tool.server_url if tool else None
        
        # Round-robin: select server with least requests
        selected = min(healthy, key=lambda s: s.request_count)
        return selected.url
    
    async def invoke_tool(self, tool_name: str, params: Dict[str, Any], 
                         max_retries: int = 2) -> Dict[str, Any]:
        """Invoke tool with failover"""
        tool = self.get_tool(tool_name)
        
        if not tool:
            return {"success": False, "error": f"Tool not found: {tool_name}"}
        
        primary_server = tool.server_url
        
        # Try primary server
        result = await self._try_invoke(tool.server_url, tool_name, params)
        if result["success"]:
            return result
        
        # Failover to other servers
        alternatives = [t for t in self.tools[tool_name] 
                       if t.server_url != primary_server 
                       and self.servers[t.server_url].healthy]
        
        for alt in alternatives[:max_retries]:
            logger.info(f"Failing over to {alt.server_url}")
            result = await self._try_invoke(alt.server_url, tool_name, params)
            if result["success"]:
                result["failover"] = True
                return result
        
        return {"success": False, "error": "All servers failed"}
    
    async def _try_invoke(self, server_url: str, tool_name: str, 
                         params: Dict[str, Any]) -> Dict[str, Any]:
        """Try to invoke tool on specific server"""
        server = self.servers[server_url]
        start = time.time()
        
        try:
            result = await self._execute_tool(server_url, tool_name, params)
            elapsed = time.time() - start
            server.mark_success(elapsed)
            result["server"] = server_url
            return result
        except Exception as e:
            logger.error(f"Invocation failed on {server_url}: {e}")
            server.mark_failure()
            return {"success": False, "error": str(e)}
    
    async def check_health(self):
        """Check health of all servers"""
        for url, server in self.servers.items():
            try:
                start = time.time()
                await self._ping_server(url)
                elapsed = time.time() - start
                server.mark_success(elapsed)
                server.last_check = time.time()
            except Exception as e:
                logger.warning(f"Health check failed for {url}: {e}")
                server.mark_failure()
    
    def start_health_monitoring(self):
        """Start continuous health monitoring"""
        if self._health_check_task is None:
            self._health_check_task = asyncio.create_task(self._health_monitor_loop())
    
    async def _health_monitor_loop(self):
        """Continuous health monitoring loop"""
        while True:
            await asyncio.sleep(self.health_check_interval)
            await self.check_health()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            "servers": {
                url: {
                    "healthy": s.healthy,
                    "requests": s.request_count,
                    "failures": s.failure_count,
                    "avg_response_time": s.response_time
                }
                for url, s in self.servers.items()
            },
            "tools": {
                name: len(tools) for name, tools in self.tools.items()
            },
            "conflicts": self._get_conflicts()
        }
    
    def _log_conflicts(self):
        """Log tool conflicts"""
        conflicts = self._get_conflicts()
        for tool_name, servers in conflicts.items():
            logger.warning(f"Tool conflict: '{tool_name}' available on {len(servers)} servers: {servers}")
    
    def _get_conflicts(self) -> Dict[str, List[str]]:
        """Get tools available on multiple servers"""
        return {
            name: [t.server_url for t in tools]
            for name, tools in self.tools.items()
            if len(tools) > 1
        }
    
    # Mock implementations (replace with actual HTTP calls)
    async def _fetch_tools(self, url: str) -> List[Dict[str, Any]]:
        """Fetch tools from server"""
        await asyncio.sleep(0.01)  # Simulate network delay
        return [
            {"name": "query_database", "description": "Query database"},
            {"name": "web_search", "description": "Search web"},
            {"name": f"tool_{url.split(':')[-1]}", "description": f"Server-specific tool"}
        ]
    
    async def _execute_tool(self, url: str, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool on server"""
        await asyncio.sleep(0.05)  # Simulate execution
        return {
            "success": True,
            "result": f"Executed {tool_name} on {url}",
            "params": params
        }
    
    async def _ping_server(self, url: str):
        """Ping server for health check"""
        await asyncio.sleep(0.01)
