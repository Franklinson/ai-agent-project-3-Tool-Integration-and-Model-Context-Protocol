"""
MCP Agent - Complete agent with intelligent tool selection
Integrates server manager, caching, and conversation state.
"""

import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Conversation message"""
    role: str  # user, assistant, tool
    content: str
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ConversationState:
    """Maintains conversation state"""
    messages: List[Message] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, **kwargs):
        """Add message to conversation"""
        msg = Message(role=role, content=content, **kwargs)
        self.messages.append(msg)
        return msg
    
    def get_recent_context(self, n: int = 5) -> List[Message]:
        """Get recent messages for context"""
        return self.messages[-n:]


class MCPAgent:
    """Complete MCP agent with intelligent tool selection"""
    
    def __init__(self, server_manager):
        self.server_manager = server_manager
        self.state = ConversationState()
        self.available_tools = {}
    
    async def initialize(self):
        """Initialize agent by discovering tools"""
        logger.info("Initializing agent...")
        tools = await self.server_manager.discover_tools()
        self.available_tools = tools
        logger.info(f"Discovered {len(tools)} unique tools")
    
    async def process_message(self, user_message: str) -> str:
        """Process user message and generate response"""
        # Add user message to state
        self.state.add_message("user", user_message)
        
        # Analyze message and select tools
        selected_tools = self._select_tools(user_message)
        
        if not selected_tools:
            response = self._generate_response(user_message)
            self.state.add_message("assistant", response)
            return response
        
        # Execute tools
        results = await self._execute_tools(selected_tools)
        
        # Generate response from results
        response = self._generate_response_from_results(user_message, results)
        self.state.add_message("assistant", response, tool_results=results)
        
        return response
    
    def _select_tools(self, message: str) -> List[Dict[str, Any]]:
        """Intelligent tool selection based on message context"""
        message_lower = message.lower()
        selected = []
        
        # Database queries
        if any(kw in message_lower for kw in ["query", "database", "select", "sql"]):
            if "query_database" in self.available_tools:
                selected.append({
                    "name": "query_database",
                    "params": self._extract_query_params(message)
                })
        
        # Web search
        if any(kw in message_lower for kw in ["search", "find", "look up", "google"]):
            if "web_search" in self.available_tools:
                selected.append({
                    "name": "web_search",
                    "params": {"query": message}
                })
        
        # Email
        if any(kw in message_lower for kw in ["email", "send", "mail"]):
            if "send_email" in self.available_tools:
                selected.append({
                    "name": "send_email",
                    "params": self._extract_email_params(message)
                })
        
        return selected
    
    async def _execute_tools(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute selected tools with error handling"""
        results = []
        
        for tool_spec in tools:
            try:
                result = await self.server_manager.invoke_tool(
                    tool_spec["name"],
                    tool_spec["params"]
                )
                results.append({
                    "tool": tool_spec["name"],
                    "success": result.get("success", False),
                    "result": result.get("result"),
                    "error": result.get("error")
                })
            except Exception as e:
                logger.error(f"Tool execution failed: {e}")
                results.append({
                    "tool": tool_spec["name"],
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def execute_chain(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute tool chain with context passing"""
        results = []
        context = {}
        
        for step in steps:
            # Inject context from previous steps
            params = step["params"].copy()
            if "use_context" in step and step["use_context"]:
                params.update(context)
            
            result = await self.server_manager.invoke_tool(step["name"], params)
            results.append(result)
            
            # Update context for next step
            if result.get("success"):
                context[f"{step['name']}_result"] = result.get("result")
        
        return results
    
    def _generate_response(self, message: str) -> str:
        """Generate response without tool execution"""
        return f"I understand you said: '{message}'. How can I help you with that?"
    
    def _generate_response_from_results(self, message: str, results: List[Dict[str, Any]]) -> str:
        """Generate response from tool execution results"""
        if not results:
            return self._generate_response(message)
        
        response_parts = []
        for result in results:
            if result["success"]:
                response_parts.append(f"✓ {result['tool']}: {result['result']}")
            else:
                response_parts.append(f"✗ {result['tool']}: {result.get('error', 'Failed')}")
        
        return "\n".join(response_parts)
    
    def _extract_query_params(self, message: str) -> Dict[str, Any]:
        """Extract database query parameters"""
        # Simple extraction - in production, use NLP
        if "SELECT" in message.upper():
            return {"query": message}
        return {"query": "SELECT * FROM users LIMIT 10"}
    
    def _extract_email_params(self, message: str) -> Dict[str, Any]:
        """Extract email parameters"""
        return {
            "to": "user@example.com",
            "subject": "Message from agent",
            "body": message
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "tool_calls": len(msg.tool_calls),
                "tool_results": len(msg.tool_results)
            }
            for msg in self.state.messages
        ]
    
    def clear_conversation(self):
        """Clear conversation state"""
        self.state = ConversationState()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        return {
            "messages": len(self.state.messages),
            "tools_available": len(self.available_tools),
            "servers": len(self.server_manager.servers),
            "server_stats": self.server_manager.get_stats()
        }
