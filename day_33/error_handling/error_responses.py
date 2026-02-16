"""Structured error response system with error codes and validation."""

from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for the system."""
    
    # Input/Validation Errors (1xxx)
    INVALID_INPUT = "ERR_1001"
    MISSING_REQUIRED_FIELD = "ERR_1002"
    INVALID_FORMAT = "ERR_1003"
    VALIDATION_FAILED = "ERR_1004"
    
    # Resource Errors (2xxx)
    NOT_FOUND = "ERR_2001"
    ALREADY_EXISTS = "ERR_2002"
    RESOURCE_UNAVAILABLE = "ERR_2003"
    
    # Operation Errors (3xxx)
    TIMEOUT = "ERR_3001"
    OPERATION_FAILED = "ERR_3002"
    UNAUTHORIZED = "ERR_3003"
    FORBIDDEN = "ERR_3004"
    
    # System Errors (4xxx)
    INTERNAL_ERROR = "ERR_4001"
    SERVICE_UNAVAILABLE = "ERR_4002"
    CONFIGURATION_ERROR = "ERR_4003"
    
    # External Errors (5xxx)
    EXTERNAL_API_ERROR = "ERR_5001"
    NETWORK_ERROR = "ERR_5002"
    RATE_LIMIT_EXCEEDED = "ERR_5003"


# Error code to HTTP status mapping
ERROR_STATUS_MAP = {
    ErrorCode.INVALID_INPUT: 400,
    ErrorCode.MISSING_REQUIRED_FIELD: 400,
    ErrorCode.INVALID_FORMAT: 400,
    ErrorCode.VALIDATION_FAILED: 400,
    ErrorCode.NOT_FOUND: 404,
    ErrorCode.ALREADY_EXISTS: 409,
    ErrorCode.RESOURCE_UNAVAILABLE: 503,
    ErrorCode.TIMEOUT: 408,
    ErrorCode.OPERATION_FAILED: 500,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.INTERNAL_ERROR: 500,
    ErrorCode.SERVICE_UNAVAILABLE: 503,
    ErrorCode.CONFIGURATION_ERROR: 500,
    ErrorCode.EXTERNAL_API_ERROR: 502,
    ErrorCode.NETWORK_ERROR: 503,
    ErrorCode.RATE_LIMIT_EXCEEDED: 429,
}


def create_error_response(
    code: ErrorCode,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a structured error response.
    
    Args:
        code: Error code from ErrorCode enum
        message: Human-readable error message
        details: Optional additional context and details
    
    Returns:
        Structured error response dictionary
    """
    response = {
        "error": {
            "code": code.value if isinstance(code, ErrorCode) else code,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    # Add HTTP status code
    status = ERROR_STATUS_MAP.get(code, 500)
    response["error"]["status"] = status
    
    # Add details if provided
    if details:
        response["error"]["details"] = details
    
    return response


def validate_error_response(response: Dict[str, Any]) -> bool:
    """
    Validate error response structure.
    
    Args:
        response: Error response dictionary to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(response, dict):
        return False
    
    if "error" not in response:
        return False
    
    error = response["error"]
    
    # Check required fields
    required_fields = ["code", "message", "timestamp", "status"]
    if not all(field in error for field in required_fields):
        return False
    
    # Validate types
    if not isinstance(error["code"], str):
        return False
    if not isinstance(error["message"], str):
        return False
    if not isinstance(error["status"], int):
        return False
    
    # Validate details if present
    if "details" in error and not isinstance(error["details"], dict):
        return False
    
    return True


# Convenience functions for common errors
def invalid_input_error(message: str, field: Optional[str] = None) -> Dict[str, Any]:
    """Create invalid input error response."""
    details = {"field": field} if field else None
    return create_error_response(ErrorCode.INVALID_INPUT, message, details)


def not_found_error(resource_type: str, resource_id: str) -> Dict[str, Any]:
    """Create not found error response."""
    return create_error_response(
        ErrorCode.NOT_FOUND,
        f"{resource_type} not found",
        {"resource_type": resource_type, "resource_id": resource_id}
    )


def timeout_error(operation: str, timeout_seconds: int) -> Dict[str, Any]:
    """Create timeout error response."""
    return create_error_response(
        ErrorCode.TIMEOUT,
        f"Operation '{operation}' timed out",
        {"operation": operation, "timeout_seconds": timeout_seconds}
    )


def validation_error(message: str, errors: list) -> Dict[str, Any]:
    """Create validation error response."""
    return create_error_response(
        ErrorCode.VALIDATION_FAILED,
        message,
        {"validation_errors": errors}
    )


def internal_error(message: str = "An internal error occurred") -> Dict[str, Any]:
    """Create internal error response."""
    return create_error_response(ErrorCode.INTERNAL_ERROR, message)
