"""
Tests for MCP Caching Layer
"""

import asyncio
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'mcp'))

from cache import Cache, MCPCache
from client import MCPClient, MultiServerMCPClient
from config import get_cache_config


def test_basic_cache():
    """Test basic cache operations"""
    print("\n=== Test: Basic Cache Operations ===")
    cache = Cache(max_size=3, default_ttl=1)
    
    # Set and get
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1", "Failed to get cached value"
    print("✓ Set and get working")
    
    # TTL expiration
    cache.set("key2", "value2", ttl=0.1)
    time.sleep(0.2)
    assert cache.get("key2") is None, "TTL not working"
    print("✓ TTL expiration working")
    
    # LRU eviction
    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)
    cache.set("d", 4)  # Should evict "a"
    assert cache.get("a") is None, "LRU eviction not working"
    print("✓ LRU eviction working")
    
    # Stats
    stats = cache.stats()
    assert stats["size"] == 3, "Cache size incorrect"
    print(f"✓ Cache stats: {stats}")


def test_mcp_cache():
    """Test MCP-specific cache"""
    print("\n=== Test: MCP Cache ===")
    cache = MCPCache(
        tool_metadata_ttl=1,
        discovery_ttl=1,
        response_ttl=1,
        max_size=100
    )
    
    # Tool metadata
    cache.set_tool_metadata("tool1", "server1", {"name": "tool1", "type": "test"})
    metadata = cache.get_tool_metadata("tool1", "server1")
    assert metadata["name"] == "tool1", "Tool metadata cache failed"
    print("✓ Tool metadata caching working")
    
    # Discovery results
    tools = [{"name": "tool1"}, {"name": "tool2"}]
    cache.set_discovery_result("server1", tools)
    cached_tools = cache.get_discovery_result("server1")
    assert len(cached_tools) == 2, "Discovery cache failed"
    print("✓ Discovery caching working")
    
    # Response cache
    cache.set_response("tool1", "hash123", {"result": "success"})
    response = cache.get_response("tool1", "hash123")
    assert response["result"] == "success", "Response cache failed"
    print("✓ Response caching working")
    
    # Invalidation
    cache.invalidate_tool("tool1", "server1")
    assert cache.get_tool_metadata("tool1", "server1") is None, "Tool invalidation failed"
    print("✓ Cache invalidation working")
    
    # Stats
    stats = cache.stats()
    print(f"✓ MCP cache stats: {stats}")


async def test_mcp_client():
    """Test MCP client with caching"""
    print("\n=== Test: MCP Client ===")
    
    # Create client with custom config
    config = get_cache_config("default")
    client = MCPClient("http://localhost:8080", config)
    
    # Discover tools (first call - cache miss)
    tools = await client.discover_tools()
    assert len(tools) > 0, "Tool discovery failed"
    print(f"✓ Discovered {len(tools)} tools")
    
    # Discover tools again (should hit cache)
    tools2 = await client.discover_tools()
    assert tools == tools2, "Cache not working"
    stats = client.get_cache_stats()
    assert stats["discovery"]["hits"] > 0, "Cache not being used"
    print(f"✓ Cache hit rate: {stats['discovery']['hit_rate']:.2%}")
    
    # Get tool schema
    schema = await client.get_tool_schema("query_database")
    assert schema is not None, "Tool schema fetch failed"
    print(f"✓ Retrieved schema for: {schema['name']}")
    
    # Invoke tool (first call)
    result = await client.invoke_tool("query_database", {"query": "SELECT 1"})
    assert result["success"], "Tool invocation failed"
    assert not result["from_cache"], "Should not be from cache"
    print("✓ Tool invocation successful")
    
    # Invoke same tool again (should hit cache)
    result2 = await client.invoke_tool("query_database", {"query": "SELECT 1"})
    assert result2["from_cache"], "Response cache not working"
    print("✓ Response cache working")
    
    # Cache invalidation
    client.invalidate_tool_cache("query_database")
    result3 = await client.invoke_tool("query_database", {"query": "SELECT 1"})
    assert not result3["from_cache"], "Cache invalidation failed"
    print("✓ Cache invalidation working")
    
    # Final stats
    stats = client.get_cache_stats()
    print(f"✓ Final cache stats:")
    for cache_type, cache_stats in stats.items():
        print(f"  {cache_type}: {cache_stats['hits']} hits, {cache_stats['misses']} misses")


async def test_multi_server_client():
    """Test multi-server MCP client"""
    print("\n=== Test: Multi-Server Client ===")
    
    servers = [
        "http://server1:8080",
        "http://server2:8080",
        "http://server3:8080"
    ]
    
    config = get_cache_config("aggressive")
    client = MultiServerMCPClient(servers, config)
    
    # Discover tools from all servers
    all_tools = await client.discover_all_tools()
    assert len(all_tools) == 3, "Multi-server discovery failed"
    print(f"✓ Discovered tools from {len(all_tools)} servers")
    
    # Invoke tool on specific server
    result = await client.invoke_tool("query_database", {"query": "SELECT 1"}, 
                                      server_url="http://server1:8080")
    assert result["success"], "Multi-server invocation failed"
    print("✓ Multi-server invocation working")
    
    # Get stats from all servers
    all_stats = client.get_all_cache_stats()
    print(f"✓ Cache stats from {len(all_stats)} servers")
    
    # Invalidate all caches
    client.invalidate_all_caches()
    print("✓ All caches invalidated")


def test_cache_configs():
    """Test different cache configurations"""
    print("\n=== Test: Cache Configurations ===")
    
    profiles = ["default", "aggressive", "minimal", "no_response_cache"]
    
    for profile in profiles:
        config = get_cache_config(profile)
        print(f"✓ {profile}: TTL={config['response_ttl']}s, Size={config['max_size']}")


async def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("MCP CACHING LAYER - TEST SUITE")
    print("=" * 70)
    
    try:
        test_basic_cache()
        test_mcp_cache()
        await test_mcp_client()
        await test_multi_server_client()
        test_cache_configs()
        
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
