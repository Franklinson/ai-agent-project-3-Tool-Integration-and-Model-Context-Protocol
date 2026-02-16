"""Retry mechanisms with exponential backoff for transient failures."""

import time
import functools
from typing import Callable, Tuple, Type, Optional, Any
import logging

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for retrying operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff calculation
        retry_on: Tuple of exception types to retry on
        on_retry: Optional callback function called on each retry
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(f"Max retries ({max_retries}) reached for {func.__name__}")
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1)
                    
                    time.sleep(delay)
            
            # Should not reach here, but raise last exception if it does
            if last_exception:
                raise last_exception
        
        return wrapper
    return decorator


def retry_operation(
    operation: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: Tuple[Type[Exception], ...] = (Exception,)
) -> Any:
    """
    Retry an operation with exponential backoff (function version).
    
    Args:
        operation: Function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff calculation
        retry_on: Tuple of exception types to retry on
    
    Returns:
        Result of the operation
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except retry_on as e:
            last_exception = e
            
            if attempt == max_retries:
                logger.error(f"Max retries ({max_retries}) reached")
                raise
            
            delay = min(base_delay * (exponential_base ** attempt), max_delay)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s...")
            time.sleep(delay)
    
    if last_exception:
        raise last_exception


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number."""
        return min(
            self.base_delay * (self.exponential_base ** attempt),
            self.max_delay
        )


# Common exception groups for retry
TRANSIENT_ERRORS = (ConnectionError, TimeoutError)
NETWORK_ERRORS = (ConnectionError, TimeoutError, OSError)
