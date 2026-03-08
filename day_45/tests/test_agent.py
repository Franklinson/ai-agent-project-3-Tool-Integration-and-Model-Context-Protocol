"""
Tests for MCP Agent
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'mcp'))

from agent import MCPAgent, ConversationState, Message
from server_manager import ServerManager


async def test_agent_initialization():
    """Test agent initialization"""
    print("\n=== Test: Agent Initialization ===")
    
    manager = ServerManager()
    manager.add_server("http://server1:8080")
    
    agent = MCPAgent(manager)
    await agent.initialize()
    
    assert len(agent.available_tools) > 0
    print(f"✓ Agent initialized with {len(agent.available_tools)} tools")


async def test_conversation_state():
    """Test conversation state management"""
    print("\n=== Test: Conversation State ===")
    
    state = ConversationState()
    state.add_message("user", "Hello")
    state.add_message("assistant", "Hi there!")
    
    assert len(state.messages) == 2
    assert state.messages[0].role == "user"
    print("✓ Conversation state maintained")


async def test_tool_selection():
    """Test intelligent tool selection"""
    print("\n=== Test: Tool Selection ===")
    
    manager = ServerManager()
    manager.add_server("http://server1:8080")
    
    agent = MCPAgent(manager)
    await agent.initialize()
    
    # Test database query selection
    tools = agent._select_tools("Query the database for users")
    assert any(t["name"] == "query_database" for t in tools)
    print("✓ Database tool selected for query")
    
    # Test web search selection
    tools = agent._select_tools("Search for MCP protocol")
    assert any(t["name"] == "web_search" for t in tools)
    print("✓ Web search tool selected")


async def test_message_processing():
    """Test message processing"""
    print("\n=== Test: Message Processing ===")
    
    manager = ServerManager()
    manager.add_server("http://server1:8080")
    
    agent = MCPAgent(manager)
    await agent.initialize()
    
    response = await agent.process_message("Query the database")
    
    assert response is not None
    assert len(agent.state.messages) == 2  # user + assistant
    print("✓ Message processed successfully")


async def test_tool_chaining():
    """Test tool chaining"""
    print("\n=== Test: Tool Chaining ===")
    
    manager = ServerManager()
    manager.add_server("http://server1:8080")
    
    agent = MCPAgent(manager)
    await agent.initialize()
    
    # Define chain: query DB, then send email with results
    chain = [
        {"name": "query_database", "params": {"query": "SELECT * FROM users"}},
        {"name": "send_email", "params": {"to": "admin@example.com"}, "use_context": True}
    ]
    
    results = await agent.execute_chain(chain)
    
    assert len(results) == 2
    print("✓ Tool chain executed")


async def test_error_handling():
    """Test error handling"""
    print("\n=== Test: Error Handling ===")
    
    manager = ServerManager()
    manager.add_server("http://server1:8080")
    
    agent = MCPAgent(manager)
    await agent.initialize()
    
    # Try to execute non-existent tool
    results = await agent._execute_tools([{"name": "nonexistent", "params": {}}])
    
    assert len(results) > 0
    assert not results[0]["success"]
    print("✓ Errors handled gracefully")


async def test_conversation_history():
    """Test conversation history"""
    print("\n=== Test: Conversation History ===")
    
    manager = ServerManager()
    manager.add_server("http://server1:8080")
    
    agent = MCPAgent(manager)
    await agent.initialize()
    
    await agent.process_message("Hello")
    await agent.process_message("Query database")
    
    history = agent.get_conversation_history()
    
    assert len(history) >= 2
    print(f"✓ Conversation history: {len(history)} messages")


async def test_context_awareness():
    """Test context-aware responses"""
    print("\n=== Test: Context Awareness ===")
    
    manager = ServerManager()
    manager.add_server("http://server1:8080")
    
    agent = MCPAgent(manager)
    await agent.initialize()
    
    # First message
    await agent.process_message("Query the database")
    
    # Second message (should have context from first)
    recent = agent.state.get_recent_context(2)
    
    assert len(recent) >= 2
    print("✓ Context maintained across messages")


async def test_statistics():
    """Test agent statistics"""
    print("\n=== Test: Statistics ===")
    
    manager = ServerManager()
    manager.add_server("http://server1:8080")
    
    agent = MCPAgent(manager)
    await agent.initialize()
    
    await agent.process_message("Test message")
    
    stats = agent.get_stats()
    
    assert "messages" in stats
    assert "tools_available" in stats
    assert stats["messages"] >= 2
    print(f"✓ Statistics: {stats['messages']} messages, {stats['tools_available']} tools")


async def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("MCP AGENT - TEST SUITE")
    print("=" * 70)
    
    try:
        await test_agent_initialization()
        await test_conversation_state()
        await test_tool_selection()
        await test_message_processing()
        await test_tool_chaining()
        await test_error_handling()
        await test_conversation_history()
        await test_context_awareness()
        await test_statistics()
        
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
