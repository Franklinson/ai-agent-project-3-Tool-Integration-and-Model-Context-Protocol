"""
Connection Pool for MCP Servers
Manages reusable connections with health checks and monitoring.
"""

import asyncio
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from collections import deque
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Connection:
    """MCP server connection"""
    server_url: str
    connection_id: str
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)
    use_count: int = 0
    healthy: bool = True
    
    def mark_used(self):
        """Mark connection as used"""
        self.last_used = time.time()
        self.use_count += 1
    
    def is_stale(self, max_idle: float = 300) -> bool:
        """Check if connection is stale"""
        return time.time() - self.last_used > max_idle


class ConnectionPool:
    """Connection pool for a single server"""
    
    def __init__(self, server_url: str, min_size: int = 2, max_size: int = 10):
        self.server_url = server_url
        self.min_size = min_size
        self.max_size = max_size
        self._available: deque[Connection] = deque()
        self._in_use: Dict[str, Connection] = {}
        self._total_created = 0
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> Connection:
        """Acquire connection from pool"""
        async with self._lock:
            # Try to get available connection
            while self._available:
                conn = self._available.popleft()
                
                # Check if connection is healthy and not stale
                if conn.healthy and not conn.is_stale():
                    self._in_use[conn.connection_id] = conn
                    conn.mark_used()
                    return conn
            
            # Create new connection if under max size
            if len(self._in_use) + len(self._available) < self.max_size:
                conn = await self._create_connection()
                self._in_use[conn.connection_id] = conn
                conn.mark_used()
                return conn
            
            # Wait for connection to become available
            logger.warning(f"Pool exhausted for {self.server_url}, waiting...")
            await asyncio.sleep(0.1)
            return await self.acquire()
    
    async def release(self, connection: Connection):
        """Release connection back to pool"""
        async with self._lock:
            if connection.connection_id in self._in_use:
                del self._in_use[connection.connection_id]
                
                if connection.healthy and not connection.is_stale():
                    self._available.append(connection)
                else:
                    logger.info(f"Discarding unhealthy/stale connection: {connection.connection_id}")
    
    async def _create_connection(self) -> Connection:
        """Create new connection"""
        self._total_created += 1
        conn = Connection(
            server_url=self.server_url,
            connection_id=f"{self.server_url}:{self._total_created}"
        )
        logger.info(f"Created connection: {conn.connection_id}")
        return conn
    
    async def health_check(self):
        """Check health of all connections"""
        async with self._lock:
            # Check available connections
            healthy_conns = []
            for conn in self._available:
                if await self._check_connection_health(conn):
                    healthy_conns.append(conn)
            self._available = deque(healthy_conns)
            
            # Check in-use connections
            for conn in self._in_use.values():
                await self._check_connection_health(conn)
    
    async def _check_connection_health(self, conn: Connection) -> bool:
        """Check if connection is healthy"""
        try:
            # Mock health check - replace with actual ping
            await asyncio.sleep(0.01)
            conn.healthy = True
            return True
        except Exception as e:
            logger.error(f"Health check failed for {conn.connection_id}: {e}")
            conn.healthy = False
            return False
    
    def stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            "server": self.server_url,
            "available": len(self._available),
            "in_use": len(self._in_use),
            "total": len(self._available) + len(self._in_use),
            "max_size": self.max_size,
            "total_created": self._total_created
        }


class ConnectionPoolManager:
    """Manages connection pools for multiple servers"""
    
    def __init__(self, min_size: int = 2, max_size: int = 10, health_check_interval: float = 60):
        self.min_size = min_size
        self.max_size = max_size
        self.health_check_interval = health_check_interval
        self._pools: Dict[str, ConnectionPool] = {}
        self._health_check_task = None
    
    def add_server(self, server_url: str):
        """Add server to pool manager"""
        if server_url not in self._pools:
            self._pools[server_url] = ConnectionPool(
                server_url,
                min_size=self.min_size,
                max_size=self.max_size
            )
            logger.info(f"Added connection pool for {server_url}")
    
    def remove_server(self, server_url: str):
        """Remove server from pool manager"""
        if server_url in self._pools:
            del self._pools[server_url]
            logger.info(f"Removed connection pool for {server_url}")
    
    async def acquire(self, server_url: str) -> Connection:
        """Acquire connection for server"""
        if server_url not in self._pools:
            self.add_server(server_url)
        
        return await self._pools[server_url].acquire()
    
    async def release(self, connection: Connection):
        """Release connection back to pool"""
        if connection.server_url in self._pools:
            await self._pools[connection.server_url].release(connection)
    
    async def health_check_all(self):
        """Health check all pools"""
        for pool in self._pools.values():
            await pool.health_check()
    
    def start_health_monitoring(self):
        """Start continuous health monitoring"""
        if self._health_check_task is None:
            self._health_check_task = asyncio.create_task(self._health_monitor_loop())
    
    async def _health_monitor_loop(self):
        """Continuous health monitoring loop"""
        while True:
            await asyncio.sleep(self.health_check_interval)
            await self.health_check_all()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all pools"""
        return {
            "pools": {url: pool.stats() for url, pool in self._pools.items()},
            "total_servers": len(self._pools)
        }
    
    async def close_all(self):
        """Close all connections"""
        for pool in self._pools.values():
            pool._available.clear()
            pool._in_use.clear()
        logger.info("Closed all connection pools")
