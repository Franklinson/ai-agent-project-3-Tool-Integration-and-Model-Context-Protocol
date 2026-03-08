"""
Tests for Server Manager
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'mcp'))

from server_manager import ServerManager, ServerInfo, ToolInfo


async def test_server_management():
    """Test adding and removing servers"""
    print("\n=== Test: Server Management ===")
    manager = ServerManager()
    
    # Add servers
    manager.add_server("http://server1:8080", priority=10)
    manager.add_server("http://server2:8080", priority=5)
    manager.add_server("http://server3:8080", priority=1)
    
    assert len(manager.servers) == 3
    print("✓ Added 3 servers")
    
    # Remove server
    manager.remove_server("http://server3:8080")
    assert len(manager.servers) == 2
    print("✓ Removed server")


async def test_tool_discovery():
    """Test tool discovery from multiple servers"""
    print("\n=== Test: Tool Discovery ===")
    manager = ServerManager()
    
    manager.add_server("http://server1:8080", priority=10)
    manager.add_server("http://server2:8080", priority=5)
    
    # Discover tools
    tools = await manager.discover_tools()
    
    assert len(tools) > 0
    print(f"✓ Discovered {len(tools)} unique tools")
    
    # Check for conflicts
    conflicts = manager._get_conflicts()
    print(f"✓ Found {len(conflicts)} tool conflicts")


async def test_load_balancing():
    """Test load balancing"""
    print("\n=== Test: Load Balancing ===")
    manager = ServerManager()
    
    manager.add_server("http://server1:8080")
    manager.add_server("http://server2:8080")
    manager.add_server("http://server3:8080")
    
    await manager.discover_tools()
    
    # Make multiple requests
    for i in range(9):
        server = manager.select_server()
        manager.servers[server].request_count += 1
    
    # Check distribution
    counts = [s.request_count for s in manager.servers.values()]
    assert max(counts) - min(counts) <= 1  # Should be evenly distributed
    print(f"✓ Load distributed evenly: {counts}")


async def test_failover():
    """Test failover logic"""
    print("\n=== Test: Failover ===")
    manager = ServerManager()
    
    manager.add_server("http://server1:8080", priority=10)
    manager.add_server("http://server2:8080", priority=5)
    
    await manager.discover_tools()
    
    # First invoke should succeed on primary
    result = await manager.invoke_tool("query_database", {"query": "SELECT 1"})
    assert result["success"]
    primary_server = result["server"]
    
    # Mark primary server as unhealthy
    manager.servers[primary_server].healthy = False
    
    # Invoke tool (should failover)
    result = await manager.invoke_tool("query_database", {"query": "SELECT 2"})
    
    assert result["success"]
    # Should use different server or have failover flag
    assert result["server"] != primary_server or result.get("failover") == True
    print("✓ Failover to backup server successful")


async def test_conflict_resolution():
    """Test tool conflict resolution"""
    print("\n=== Test: Conflict Resolution ===")
    manager = ServerManager()
    
    manager.add_server("http://server1:8080", priority=10)
    manager.add_server("http://server2:8080", priority=5)
    
    await manager.discover_tools()
    
    # Get tool (should select higher priority)
    tool = manager.get_tool("query_database")
    
    assert tool is not None
    assert tool.priority == 10  # Higher priority server
    print(f"✓ Selected tool from priority {tool.priority} server")


async def test_health_monitoring():
    """Test health monitoring"""
    print("\n=== Test: Health Monitoring ===")
    manager = ServerManager(health_check_interval=1.0)
    
    manager.add_server("http://server1:8080")
    manager.add_server("http://server2:8080")
    
    # Check health
    await manager.check_health()
    
    healthy_count = sum(1 for s in manager.servers.values() if s.healthy)
    assert healthy_count == 2
    print(f"✓ Health check completed: {healthy_count}/2 healthy")


async def test_statistics():
    """Test statistics collection"""
    print("\n=== Test: Statistics ===")
    manager = ServerManager()
    
    manager.add_server("http://server1:8080")
    manager.add_server("http://server2:8080")
    
    await manager.discover_tools()
    await manager.invoke_tool("query_database", {"query": "SELECT 1"})
    
    stats = manager.get_stats()
    
    assert "servers" in stats
    assert "tools" in stats
    assert "conflicts" in stats
    print(f"✓ Statistics collected: {len(stats['servers'])} servers, {len(stats['tools'])} tools")


async def test_retry_logic():
    """Test retry logic on failure"""
    print("\n=== Test: Retry Logic ===")
    manager = ServerManager()
    
    manager.add_server("http://server1:8080")
    manager.add_server("http://server2:8080")
    manager.add_server("http://server3:8080")
    
    await manager.discover_tools()
    
    # Mark first server as unhealthy
    manager.servers["http://server1:8080"].healthy = False
    
    # Invoke should retry on other servers
    result = await manager.invoke_tool("query_database", {"query": "SELECT 1"}, max_retries=2)
    
    assert result["success"]
    print("✓ Retry logic working")


async def test_server_priority():
    """Test server priority selection"""
    print("\n=== Test: Server Priority ===")
    manager = ServerManager()
    
    manager.add_server("http://low:8080", priority=1)
    manager.add_server("http://high:8080", priority=10)
    manager.add_server("http://medium:8080", priority=5)
    
    await manager.discover_tools()
    
    # Get tool should select highest priority
    tool = manager.get_tool("query_database")
    assert "high" in tool.server_url
    print(f"✓ Selected highest priority server: {tool.server_url}")


async def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("SERVER MANAGER - TEST SUITE")
    print("=" * 70)
    
    try:
        await test_server_management()
        await test_tool_discovery()
        await test_load_balancing()
        await test_failover()
        await test_conflict_resolution()
        await test_health_monitoring()
        await test_statistics()
        await test_retry_logic()
        await test_server_priority()
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✓")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(run_all_tests())
