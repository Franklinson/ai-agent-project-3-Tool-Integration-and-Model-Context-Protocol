"""Enhanced tool discovery with comprehensive error handling."""

import json
import logging
import os
from typing import List, Dict, Any, Optional
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from error_handling import (
    create_error_response,
    ErrorCode,
    retry_with_backoff,
    TRANSIENT_ERRORS
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ToolRegistry:
    """Tool registry with comprehensive error handling."""
    
    def __init__(self, registry_path: str = "tool_registry.json", timeout: int = 5):
        self.registry_path = registry_path
        self.timeout = timeout
        self.registry = None
        self.tools = None
        self._load_registry()
    
    @retry_with_backoff(max_retries=2, base_delay=0.5, retry_on=TRANSIENT_ERRORS)
    def _load_registry(self) -> Dict[str, Any]:
        """Load registry with error handling and retry."""
        try:
            if not os.path.exists(self.registry_path):
                error = create_error_response(
                    ErrorCode.NOT_FOUND,
                    f"Registry file not found: {self.registry_path}",
                    {"path": self.registry_path}
                )
                logger.error(f"Registry file not found: {self.registry_path}")
                raise FileNotFoundError(error)
            
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)
            
            if 'tools' not in self.registry:
                error = create_error_response(
                    ErrorCode.INVALID_FORMAT,
                    "Invalid registry format: missing 'tools' key",
                    {"path": self.registry_path}
                )
                logger.error("Invalid registry format")
                raise ValueError(error)
            
            self.tools = self.registry['tools']
            logger.info(f"Successfully loaded {len(self.tools)} tools from registry")
            return self.registry
            
        except json.JSONDecodeError as e:
            error = create_error_response(
                ErrorCode.INVALID_FORMAT,
                f"Invalid JSON in registry file",
                {"path": self.registry_path, "error": str(e)}
            )
            logger.error(f"JSON decode error: {e}")
            raise ValueError(error)
        except IOError as e:
            error = create_error_response(
                ErrorCode.INTERNAL_ERROR,
                f"Failed to read registry file",
                {"path": self.registry_path, "error": str(e)}
            )
            logger.error(f"IO error: {e}")
            raise IOError(error)
    
    def search_tools(self, query: str) -> Dict[str, Any]:
        """Search tools with error handling."""
        try:
            if not query or not query.strip():
                return create_error_response(
                    ErrorCode.INVALID_INPUT,
                    "Search query cannot be empty",
                    {"field": "query"}
                )
            
            if len(query) > 100:
                return create_error_response(
                    ErrorCode.INVALID_INPUT,
                    "Search query too long (max 100 characters)",
                    {"field": "query", "length": len(query)}
                )
            
            query_lower = query.lower().strip()
            results = [
                tool for tool in self.tools
                if query_lower in tool.get('name', '').lower() or 
                   query_lower in tool.get('description', '').lower()
            ]
            
            logger.info(f"Search for '{query}' found {len(results)} results")
            
            return {
                "success": True,
                "query": query,
                "count": len(results),
                "tools": results
            }
            
        except Exception as e:
            logger.error(f"Error searching tools: {e}")
            return create_error_response(
                ErrorCode.OPERATION_FAILED,
                "Failed to search tools",
                {"query": query, "error": str(e)}
            )
    
    def get_tool_metadata(self, name: str) -> Dict[str, Any]:
        """Get tool metadata with error handling."""
        try:
            if not name:
                return create_error_response(
                    ErrorCode.INVALID_INPUT,
                    "Tool name cannot be empty",
                    {"field": "name"}
                )
            
            for tool in self.tools:
                if tool.get('name') == name:
                    logger.info(f"Found metadata for tool '{name}'")
                    return {
                        "success": True,
                        "tool": tool
                    }
            
            logger.warning(f"Tool not found: {name}")
            return create_error_response(
                ErrorCode.NOT_FOUND,
                f"Tool '{name}' not found in registry",
                {"tool_name": name}
            )
            
        except Exception as e:
            logger.error(f"Error getting tool metadata: {e}")
            return create_error_response(
                ErrorCode.OPERATION_FAILED,
                "Failed to get tool metadata",
                {"tool_name": name, "error": str(e)}
            )
