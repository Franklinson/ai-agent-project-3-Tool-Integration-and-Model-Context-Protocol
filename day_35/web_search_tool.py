"""
Web Search Tool with schema validation and error handling
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from typing import Dict, Any
from day_35.search_api_client import (
    SearchAPIClient, SearchAPIError, RateLimitError, 
    NetworkError, TimeoutError, InvalidInputError
)
from day_32.validators.schema_validator import SchemaValidator, ValidationError
from day_33.error_handling.error_responses import (
    ErrorCode, create_error_response, validation_error, invalid_input_error
)


class WebSearchTool:
    """Web search tool with validation and error handling"""
    
    def __init__(self):
        self.client = SearchAPIClient(rate_limit_delay=1.0)
        self.validator = SchemaValidator()
    
    def _validate_input(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """Validate input parameters"""
        is_valid, error_msg = self.validator.validate_input(params, 'web_search_input')
        return is_valid, error_msg
    
    def _process_results(self, raw_results: list, query: str) -> Dict[str, Any]:
        """Process and structure search results"""
        results = [
            {
                'title': r['title'],
                'url': r['link'],
                'snippet': r['snippet']
            }
            for r in raw_results
        ]
        
        return {
            'results': results,
            'query': query,
            'total_results': len(results)
        }
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute web search with validation and error handling
        
        Args:
            params: Input parameters (query, num_results, sort_by)
            
        Returns:
            Structured search results or error response
        """
        # Validate input
        is_valid, error_msg = self._validate_input(params)
        if not is_valid:
            return validation_error("Input validation failed", [error_msg])
        
        # Extract parameters
        query = params['query']
        num_results = params.get('num_results', 5)
        
        # Execute search
        try:
            raw_results = self.client.search(query, max_results=num_results)
            output = self._process_results(raw_results, query)
            
            # Validate output
            is_valid, error_msg = self.validator.validate_output(output, 'web_search_output')
            if not is_valid:
                return create_error_response(
                    ErrorCode.INTERNAL_ERROR,
                    "Output validation failed",
                    {'validation_error': error_msg}
                )
            
            return output
            
        except InvalidInputError as e:
            return invalid_input_error(str(e), 'query')
        except RateLimitError as e:
            return create_error_response(
                ErrorCode.RATE_LIMIT_EXCEEDED,
                str(e),
                {'query': query}
            )
        except TimeoutError as e:
            return create_error_response(
                ErrorCode.TIMEOUT,
                str(e),
                {'query': query}
            )
        except NetworkError as e:
            return create_error_response(
                ErrorCode.NETWORK_ERROR,
                str(e),
                {'query': query}
            )
        except SearchAPIError as e:
            return create_error_response(
                ErrorCode.EXTERNAL_API_ERROR,
                str(e),
                {'query': query}
            )
        except Exception as e:
            return create_error_response(
                ErrorCode.INTERNAL_ERROR,
                f"Unexpected error: {str(e)}",
                {'query': query}
            )


def search(query: str, num_results: int = 5, sort_by: str = 'relevance') -> Dict[str, Any]:
    """
    Convenience function for web search
    
    Args:
        query: Search query string
        num_results: Number of results (1-20, default 5)
        sort_by: Sort order ('relevance' or 'date', default 'relevance')
        
    Returns:
        Search results or error response
    """
    tool = WebSearchTool()
    params = {
        'query': query,
        'num_results': num_results,
        'sort_by': sort_by
    }
    return tool.execute(params)
