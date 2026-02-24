"""HTTP API request tool with comprehensive error handling and rate limiting."""

import json
import time
from typing import Any, Dict, Optional, Union
from enum import Enum
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError


class HTTPMethod(str, Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class APIRequestTool:
    """Tool for making HTTP API requests with proper error handling."""
    
    def __init__(self, rate_limit_delay: float = 0.0):
        """Initialize API request tool.
        
        Args:
            rate_limit_delay: Delay in seconds between requests (for rate limiting)
        """
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0.0
    
    def _apply_rate_limit(self) -> None:
        """Apply rate limiting delay if configured."""
        if self.rate_limit_delay > 0:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _prepare_headers(
        self, 
        headers: Optional[Dict[str, str]] = None,
        auth_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_key_header: str = "X-API-Key"
    ) -> Dict[str, str]:
        """Prepare request headers with authentication.
        
        Args:
            headers: Custom headers
            auth_token: Bearer token for authentication
            api_key: API key for authentication
            api_key_header: Header name for API key
            
        Returns:
            Prepared headers dictionary
        """
        prepared_headers = headers.copy() if headers else {}
        
        if auth_token:
            prepared_headers["Authorization"] = f"Bearer {auth_token}"
        
        if api_key:
            prepared_headers[api_key_header] = api_key
        
        return prepared_headers
    
    def _prepare_body(
        self, 
        body: Optional[Union[Dict, str]] = None,
        content_type: Optional[str] = None
    ) -> tuple[Optional[Union[Dict, str]], Dict[str, str]]:
        """Prepare request body and update headers.
        
        Args:
            body: Request body (dict or string)
            content_type: Content type override
            
        Returns:
            Tuple of (prepared_body, additional_headers)
        """
        if body is None:
            return None, {}
        
        additional_headers = {}
        
        if isinstance(body, dict):
            if content_type == "application/x-www-form-urlencoded":
                return body, {"Content-Type": content_type}
            else:
                # Default to JSON for dict bodies
                additional_headers["Content-Type"] = "application/json"
                return body, additional_headers
        
        # String body
        if content_type:
            additional_headers["Content-Type"] = content_type
        
        return body, additional_headers
    
    def make_request(
        self,
        url: str,
        method: HTTPMethod = HTTPMethod.GET,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[Union[Dict, str]] = None,
        timeout: int = 30,
        auth_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_key_header: str = "X-API-Key",
        content_type: Optional[str] = None,
        verify_ssl: bool = True
    ) -> Dict[str, Any]:
        """Make HTTP API request with comprehensive error handling.
        
        Args:
            url: Request URL (required)
            method: HTTP method (GET, POST, PUT, DELETE)
            headers: Optional request headers
            body: Optional request body (dict or string)
            timeout: Request timeout in seconds (default: 30)
            auth_token: Optional Bearer token
            api_key: Optional API key
            api_key_header: Header name for API key (default: X-API-Key)
            content_type: Content type override
            verify_ssl: Verify SSL certificates (default: True)
            
        Returns:
            Dictionary containing:
                - success (bool): Whether request succeeded
                - status_code (int): HTTP status code
                - headers (dict): Response headers
                - body (dict/str): Response body
                - error (str): Error message if failed
        """
        # Apply rate limiting
        self._apply_rate_limit()
        
        # Prepare headers
        prepared_headers = self._prepare_headers(headers, auth_token, api_key, api_key_header)
        
        # Prepare body
        prepared_body, body_headers = self._prepare_body(body, content_type)
        prepared_headers.update(body_headers)
        
        try:
            # Make request based on method
            if method == HTTPMethod.GET:
                response = requests.get(
                    url, 
                    headers=prepared_headers, 
                    timeout=timeout,
                    verify=verify_ssl
                )
            elif method == HTTPMethod.POST:
                if isinstance(prepared_body, dict) and "application/json" in prepared_headers.get("Content-Type", ""):
                    response = requests.post(
                        url, 
                        json=prepared_body, 
                        headers=prepared_headers, 
                        timeout=timeout,
                        verify=verify_ssl
                    )
                else:
                    response = requests.post(
                        url, 
                        data=prepared_body, 
                        headers=prepared_headers, 
                        timeout=timeout,
                        verify=verify_ssl
                    )
            elif method == HTTPMethod.PUT:
                if isinstance(prepared_body, dict) and "application/json" in prepared_headers.get("Content-Type", ""):
                    response = requests.put(
                        url, 
                        json=prepared_body, 
                        headers=prepared_headers, 
                        timeout=timeout,
                        verify=verify_ssl
                    )
                else:
                    response = requests.put(
                        url, 
                        data=prepared_body, 
                        headers=prepared_headers, 
                        timeout=timeout,
                        verify=verify_ssl
                    )
            elif method == HTTPMethod.DELETE:
                response = requests.delete(
                    url, 
                    headers=prepared_headers, 
                    timeout=timeout,
                    verify=verify_ssl
                )
            else:
                return {
                    "success": False,
                    "status_code": 0,
                    "headers": {},
                    "body": None,
                    "error": f"Unsupported HTTP method: {method}"
                }
            
            # Parse response body
            response_body = self._parse_response(response)
            
            # Check for HTTP errors
            response.raise_for_status()
            
            return {
                "success": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response_body,
                "error": None
            }
        
        except Timeout:
            return {
                "success": False,
                "status_code": 0,
                "headers": {},
                "body": None,
                "error": f"Request timed out after {timeout} seconds"
            }
        
        except ConnectionError as e:
            return {
                "success": False,
                "status_code": 0,
                "headers": {},
                "body": None,
                "error": f"Connection error: {str(e)}"
            }
        
        except HTTPError as e:
            # HTTP error occurred (4xx, 5xx)
            response = e.response
            response_body = self._parse_response(response)
            
            return {
                "success": False,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "body": response_body,
                "error": f"HTTP {response.status_code}: {response.reason}"
            }
        
        except RequestException as e:
            return {
                "success": False,
                "status_code": 0,
                "headers": {},
                "body": None,
                "error": f"Request failed: {str(e)}"
            }
        
        except Exception as e:
            return {
                "success": False,
                "status_code": 0,
                "headers": {},
                "body": None,
                "error": f"Unexpected error: {str(e)}"
            }
    
    def _parse_response(self, response) -> Union[Dict, str, None]:
        """Parse response body based on content type.
        
        Args:
            response: requests Response object
            
        Returns:
            Parsed response body (dict, string, or None)
        """
        if not response.content:
            return None
        
        content_type = response.headers.get("Content-Type", "")
        
        if "application/json" in content_type:
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
        
        return response.text


# Example usage and tests
if __name__ == "__main__":
    # Initialize API tool
    api_tool = APIRequestTool(rate_limit_delay=0.5)
    
    print("=== Testing with JSONPlaceholder API ===\n")
    
    # Test 1: GET request
    print("1. GET request:")
    result = api_tool.make_request(
        url="https://jsonplaceholder.typicode.com/posts/1",
        method=HTTPMethod.GET
    )
    print(f"Success: {result['success']}")
    print(f"Status: {result['status_code']}")
    print(f"Body: {result['body']}\n")
    
    # Test 2: POST request with JSON body
    print("2. POST request with JSON:")
    result = api_tool.make_request(
        url="https://jsonplaceholder.typicode.com/posts",
        method=HTTPMethod.POST,
        body={
            "title": "Test Post",
            "body": "This is a test",
            "userId": 1
        }
    )
    print(f"Success: {result['success']}")
    print(f"Status: {result['status_code']}")
    print(f"Body: {result['body']}\n")
    
    # Test 3: PUT request
    print("3. PUT request:")
    result = api_tool.make_request(
        url="https://jsonplaceholder.typicode.com/posts/1",
        method=HTTPMethod.PUT,
        body={
            "id": 1,
            "title": "Updated Post",
            "body": "Updated content",
            "userId": 1
        }
    )
    print(f"Success: {result['success']}")
    print(f"Status: {result['status_code']}")
    print(f"Body: {result['body']}\n")
    
    # Test 4: DELETE request
    print("4. DELETE request:")
    result = api_tool.make_request(
        url="https://jsonplaceholder.typicode.com/posts/1",
        method=HTTPMethod.DELETE
    )
    print(f"Success: {result['success']}")
    print(f"Status: {result['status_code']}\n")
    
    print("=== Testing with httpbin.org ===\n")
    
    # Test 5: GET with headers
    print("5. GET with custom headers:")
    result = api_tool.make_request(
        url="https://httpbin.org/headers",
        method=HTTPMethod.GET,
        headers={"Custom-Header": "TestValue"}
    )
    print(f"Success: {result['success']}")
    print(f"Status: {result['status_code']}")
    print(f"Body: {result['body']}\n")
    
    # Test 6: Bearer token authentication
    print("6. Bearer token authentication:")
    result = api_tool.make_request(
        url="https://httpbin.org/bearer",
        method=HTTPMethod.GET,
        auth_token="test-token-123"
    )
    print(f"Success: {result['success']}")
    print(f"Status: {result['status_code']}")
    print(f"Body: {result['body']}\n")
    
    # Test 7: Error handling - timeout
    print("7. Timeout handling:")
    result = api_tool.make_request(
        url="https://httpbin.org/delay/5",
        method=HTTPMethod.GET,
        timeout=2
    )
    print(f"Success: {result['success']}")
    print(f"Error: {result['error']}\n")
    
    # Test 8: Error handling - 404
    print("8. HTTP error handling (404):")
    result = api_tool.make_request(
        url="https://jsonplaceholder.typicode.com/posts/999999",
        method=HTTPMethod.GET
    )
    print(f"Success: {result['success']}")
    print(f"Status: {result['status_code']}")
    print(f"Error: {result['error']}\n")
    
    # Test 9: Form data
    print("9. POST with form data:")
    result = api_tool.make_request(
        url="https://httpbin.org/post",
        method=HTTPMethod.POST,
        body={"key1": "value1", "key2": "value2"},
        content_type="application/x-www-form-urlencoded"
    )
    print(f"Success: {result['success']}")
    print(f"Status: {result['status_code']}")
    print(f"Body: {result['body']}\n")
