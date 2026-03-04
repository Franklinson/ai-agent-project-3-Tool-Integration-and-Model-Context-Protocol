"""
MCP Error Handling
Comprehensive error handling for MCP communication.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp.error_handler')


class ErrorCategory(Enum):
    """MCP error categories"""
    PARSE_ERROR = "parse_error"
    INVALID_REQUEST = "invalid_request"
    METHOD_NOT_FOUND = "method_not_found"
    INVALID_PARAMS = "invalid_params"
    INTERNAL_ERROR = "internal_error"
    SERVER_ERROR = "server_error"
    TIMEOUT_ERROR = "timeout_error"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class MCPError:
    """MCP error structure"""
    code: int
    message: str
    category: ErrorCategory
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    recoverable: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class ErrorHandler:
    """MCP Error Handler"""
    
    # JSON-RPC 2.0 error codes
    ERROR_CODES = {
        -32700: (ErrorCategory.PARSE_ERROR, "Parse error", False),
        -32600: (ErrorCategory.INVALID_REQUEST, "Invalid Request", False),
        -32601: (ErrorCategory.METHOD_NOT_FOUND, "Method not found", True),
        -32602: (ErrorCategory.INVALID_PARAMS, "Invalid params", True),
        -32603: (ErrorCategory.INTERNAL_ERROR, "Internal error", True),
    }
    
    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.error_count = 0
        self.error_history = []
    
    def parse_error(self, response: Dict[str, Any]) -> Optional[MCPError]:
        """
        Parse error from MCP response
        
        Args:
            response: MCP JSON-RPC response
            
        Returns:
            MCPError if error exists, None otherwise
        """
        if "error" not in response:
            return None
        
        error_data = response["error"]
        code = error_data.get("code", -1)
        message = error_data.get("message", "Unknown error")
        data = error_data.get("data")
        
        category, default_msg, recoverable = self._get_error_info(code)
        
        mcp_error = MCPError(
            code=code,
            message=message or default_msg,
            category=category,
            data=data,
            recoverable=recoverable
        )
        
        self.error_count += 1
        self.error_history.append(mcp_error)
        
        if self.enable_logging:
            self._log_error(mcp_error)
        
        return mcp_error
    
    def categorize_error(self, error: Exception) -> ErrorCategory:
        """
        Categorize Python exception
        
        Args:
            error: Python exception
            
        Returns:
            ErrorCategory
        """
        error_type = type(error).__name__
        
        if "Timeout" in error_type:
            return ErrorCategory.TIMEOUT_ERROR
        elif "Connection" in error_type or "Network" in error_type:
            return ErrorCategory.NETWORK_ERROR
        elif "Validation" in error_type or "ValueError" in error_type:
            return ErrorCategory.VALIDATION_ERROR
        else:
            return ErrorCategory.UNKNOWN_ERROR
    
    def handle_error(self, error: MCPError) -> Tuple[bool, Optional[str]]:
        """
        Handle MCP error and determine recovery action
        
        Args:
            error: MCPError instance
            
        Returns:
            Tuple of (should_retry, recovery_action)
        """
        if error.category == ErrorCategory.METHOD_NOT_FOUND:
            return False, "verify_tool_name"
        
        elif error.category == ErrorCategory.INVALID_PARAMS:
            return False, "validate_parameters"
        
        elif error.category == ErrorCategory.INTERNAL_ERROR:
            return True, "retry_with_backoff"
        
        elif error.category == ErrorCategory.TIMEOUT_ERROR:
            return True, "retry_with_longer_timeout"
        
        elif error.category == ErrorCategory.NETWORK_ERROR:
            return True, "check_connection_and_retry"
        
        elif error.category == ErrorCategory.PARSE_ERROR:
            return False, "check_request_format"
        
        elif error.category == ErrorCategory.INVALID_REQUEST:
            return False, "fix_request_structure"
        
        else:
            return error.recoverable, "manual_intervention"
    
    def _get_error_info(self, code: int) -> Tuple[ErrorCategory, str, bool]:
        """Get error information from code"""
        if code in self.ERROR_CODES:
            return self.ERROR_CODES[code]
        
        # Server errors (-32000 to -32099)
        if -32099 <= code <= -32000:
            return ErrorCategory.SERVER_ERROR, "Server error", True
        
        return ErrorCategory.UNKNOWN_ERROR, "Unknown error", False
    
    def _log_error(self, error: MCPError):
        """Log error"""
        log_msg = f"[{error.category.value}] Code {error.code}: {error.message}"
        
        if error.category in [ErrorCategory.PARSE_ERROR, ErrorCategory.INVALID_REQUEST]:
            logger.error(log_msg)
        elif error.category in [ErrorCategory.INTERNAL_ERROR, ErrorCategory.SERVER_ERROR]:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)
        
        if error.data:
            logger.debug(f"Error data: {error.data}")
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        if not self.error_history:
            return {"total_errors": 0}
        
        category_counts = {}
        for error in self.error_history:
            cat = error.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        return {
            "total_errors": self.error_count,
            "by_category": category_counts,
            "recoverable_count": sum(1 for e in self.error_history if e.recoverable)
        }
    
    def clear_history(self):
        """Clear error history"""
        self.error_history.clear()
        self.error_count = 0


# Convenience functions
def create_error_response(code: int, message: str, data: Optional[Dict] = None) -> Dict[str, Any]:
    """Create MCP error response"""
    return {
        "jsonrpc": "2.0",
        "id": None,
        "error": {
            "code": code,
            "message": message,
            "data": data
        }
    }


def is_recoverable_error(error: MCPError) -> bool:
    """Check if error is recoverable"""
    return error.recoverable


async def main():
    """Demo error handling"""
    handler = ErrorHandler()
    
    print("=== MCP Error Handling Demo ===\n")
    
    # Test 1: Parse error
    print("1. Parse Error")
    response = create_error_response(-32700, "Parse error")
    error = handler.parse_error(response)
    print(f"   Category: {error.category.value}")
    print(f"   Recoverable: {error.recoverable}")
    should_retry, action = handler.handle_error(error)
    print(f"   Action: {action}\n")
    
    # Test 2: Method not found
    print("2. Method Not Found")
    response = create_error_response(-32601, "Tool not found: unknown_tool")
    error = handler.parse_error(response)
    print(f"   Category: {error.category.value}")
    should_retry, action = handler.handle_error(error)
    print(f"   Should retry: {should_retry}")
    print(f"   Action: {action}\n")
    
    # Test 3: Invalid params
    print("3. Invalid Parameters")
    response = create_error_response(-32602, "Missing required parameter: query")
    error = handler.parse_error(response)
    print(f"   Category: {error.category.value}")
    should_retry, action = handler.handle_error(error)
    print(f"   Action: {action}\n")
    
    # Test 4: Internal error
    print("4. Internal Error")
    response = create_error_response(-32603, "Internal server error")
    error = handler.parse_error(response)
    print(f"   Category: {error.category.value}")
    print(f"   Recoverable: {error.recoverable}")
    should_retry, action = handler.handle_error(error)
    print(f"   Should retry: {should_retry}")
    print(f"   Action: {action}\n")
    
    # Test 5: Server error
    print("5. Server Error")
    response = create_error_response(-32000, "Database connection failed")
    error = handler.parse_error(response)
    print(f"   Category: {error.category.value}")
    print(f"   Recoverable: {error.recoverable}\n")
    
    # Test 6: Exception categorization
    print("6. Exception Categorization")
    timeout_error = TimeoutError("Request timed out")
    category = handler.categorize_error(timeout_error)
    print(f"   TimeoutError -> {category.value}")
    
    value_error = ValueError("Invalid value")
    category = handler.categorize_error(value_error)
    print(f"   ValueError -> {category.value}\n")
    
    # Test 7: Error statistics
    print("7. Error Statistics")
    stats = handler.get_error_stats()
    print(f"   Total errors: {stats['total_errors']}")
    print(f"   By category: {stats['by_category']}")
    print(f"   Recoverable: {stats['recoverable_count']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
