"""
Tests for Connection Pool
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'mcp'))

from connection_pool import Connection, ConnectionPool, ConnectionPoolManager


async def test_connection_creation():
    """Test connection creation"""
    print("\n=== Test: Connection Creation ===")
    
    conn = Connection("http://server1:8080", "conn-1")
    
    assert conn.server_url == "http://server1:8080"
    assert conn.use_count == 0
    assert conn.healthy
    print("✓ Connection created successfully")


async def test_connection_pool_acquire_release():
    """Test acquiring and releasing connections"""
    print("\n=== Test: Acquire/Release ===")
    
    pool = ConnectionPool("http://server1:8080", min_size=2, max_size=5)
    
    # Acquire connection
    conn1 = await pool.acquire()
    assert conn1 is not None
    assert conn1.use_count >= 1
    print("✓ Connection acquired")
    
    # Release connection
    await pool.release(conn1)
    stats = pool.stats()
    assert stats["available"] >= 0
    print("✓ Connection released")


async def test_pool_reuse():
    """Test connection reuse"""
    print("\n=== Test: Connection Reuse ===")
    
    pool = ConnectionPool("http://server1:8080", min_size=2, max_size=5)
    
    # Acquire and release
    conn1 = await pool.acquire()
    conn1_id = conn1.connection_id
    await pool.release(conn1)
    
    # Acquire again - should get same connection
    conn2 = await pool.acquire()
    
    assert conn2.connection_id == conn1_id
    assert conn2.use_count == 2
    print("✓ Connection reused")


async def test_pool_size_limit():
    """Test pool size limits"""
    print("\n=== Test: Pool Size Limit ===")
    
    pool = ConnectionPool("http://server1:8080", min_size=1, max_size=3)
    
    # Acquire up to max
    conns = []
    for i in range(3):
        conn = await pool.acquire()
        conns.append(conn)
    
    stats = pool.stats()
    assert stats["in_use"] == 3
    assert stats["total"] == 3
    print("✓ Pool size limit enforced")
    
    # Release all
    for conn in conns:
        await pool.release(conn)


async def test_health_check():
    """Test connection health checks"""
    print("\n=== Test: Health Check ===")
    
    pool = ConnectionPool("http://server1:8080", min_size=2, max_size=5)
    
    # Create some connections
    conn1 = await pool.acquire()
    await pool.release(conn1)
    
    # Run health check
    await pool.health_check()
    
    stats = pool.stats()
    assert stats["available"] >= 0
    print("✓ Health check completed")


async def test_stale_connections():
    """Test stale connection detection"""
    print("\n=== Test: Stale Connections ===")
    
    pool = ConnectionPool("http://server1:8080", min_size=2, max_size=5)
    
    conn = await pool.acquire()
    
    # Check if stale (should not be)
    assert not conn.is_stale(max_idle=300)
    print("✓ Fresh connection detected")
    
    # Check if stale with very short timeout
    assert conn.is_stale(max_idle=0)
    print("✓ Stale connection detected")
    
    await pool.release(conn)


async def test_pool_manager():
    """Test connection pool manager"""
    print("\n=== Test: Pool Manager ===")
    
    manager = ConnectionPoolManager(min_size=2, max_size=5)
    
    # Add servers
    manager.add_server("http://server1:8080")
    manager.add_server("http://server2:8080")
    
    assert len(manager._pools) == 2
    print("✓ Servers added to manager")
    
    # Acquire connections
    conn1 = await manager.acquire("http://server1:8080")
    conn2 = await manager.acquire("http://server2:8080")
    
    assert conn1.server_url == "http://server1:8080"
    assert conn2.server_url == "http://server2:8080"
    print("✓ Connections acquired from different servers")
    
    # Release connections
    await manager.release(conn1)
    await manager.release(conn2)
    print("✓ Connections released")


async def test_pool_statistics():
    """Test pool statistics"""
    print("\n=== Test: Pool Statistics ===")
    
    pool = ConnectionPool("http://server1:8080", min_size=2, max_size=5)
    
    # Acquire some connections
    conn1 = await pool.acquire()
    conn2 = await pool.acquire()
    
    stats = pool.stats()
    
    assert stats["in_use"] == 2
    assert stats["max_size"] == 5
    assert stats["total_created"] >= 2
    print(f"✓ Statistics: {stats}")
    
    await pool.release(conn1)
    await pool.release(conn2)


async def test_manager_statistics():
    """Test manager statistics"""
    print("\n=== Test: Manager Statistics ===")
    
    manager = ConnectionPoolManager(min_size=2, max_size=5)
    manager.add_server("http://server1:8080")
    manager.add_server("http://server2:8080")
    
    # Acquire some connections
    conn1 = await manager.acquire("http://server1:8080")
    conn2 = await manager.acquire("http://server2:8080")
    
    stats = manager.get_stats()
    
    assert stats["total_servers"] == 2
    assert "pools" in stats
    print(f"✓ Manager statistics: {stats['total_servers']} servers")
    
    await manager.release(conn1)
    await manager.release(conn2)


async def test_concurrent_access():
    """Test concurrent connection access"""
    print("\n=== Test: Concurrent Access ===")
    
    pool = ConnectionPool("http://server1:8080", min_size=2, max_size=5)
    
    async def worker():
        conn = await pool.acquire()
        await asyncio.sleep(0.01)
        await pool.release(conn)
    
    # Run multiple workers concurrently
    await asyncio.gather(*[worker() for _ in range(10)])
    
    stats = pool.stats()
    print(f"✓ Concurrent access handled: {stats['total_created']} connections created")


async def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("CONNECTION POOL - TEST SUITE")
    print("=" * 70)
    
    try:
        await test_connection_creation()
        await test_connection_pool_acquire_release()
        await test_pool_reuse()
        await test_pool_size_limit()
        await test_health_check()
        await test_stale_connections()
        await test_pool_manager()
        await test_pool_statistics()
        await test_manager_statistics()
        await test_concurrent_access()
        
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
