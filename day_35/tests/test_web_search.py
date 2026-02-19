"""
Comprehensive test suite for Web Search Tool
Tests successful searches, error scenarios, edge cases, and rate limiting
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

import unittest
from unittest.mock import Mock, patch, MagicMock

# Mock duckduckgo_search before importing our modules
sys.modules['duckduckgo_search'] = MagicMock()

from day_35.web_search_tool import WebSearchTool, search
from day_35.search_api_client import (
    SearchAPIClient, SearchAPIError, RateLimitError,
    NetworkError, TimeoutError, InvalidInputError
)


class TestWebSearchTool(unittest.TestCase):
    """Test cases for WebSearchTool"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.tool = WebSearchTool()
        self.sample_results = [
            {'title': 'Test 1', 'link': 'https://test1.com', 'snippet': 'Snippet 1'},
            {'title': 'Test 2', 'link': 'https://test2.com', 'snippet': 'Snippet 2'},
        ]
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_successful_search(self, mock_search):
        """Test successful search with valid input"""
        mock_search.return_value = self.sample_results
        
        params = {'query': 'Python tutorial', 'num_results': 5}
        result = self.tool.execute(params)
        
        self.assertNotIn('error', result)
        self.assertIn('results', result)
        self.assertIn('query', result)
        self.assertIn('total_results', result)
        self.assertEqual(result['query'], 'Python tutorial')
        self.assertEqual(len(result['results']), 2)
    
    def test_invalid_empty_query(self):
        """Test error handling for empty query"""
        params = {'query': ''}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_1004')
    
    def test_invalid_query_whitespace(self):
        """Test error handling for whitespace-only query"""
        params = {'query': '   '}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_1004')
    
    def test_invalid_num_results_too_low(self):
        """Test error handling for num_results < 1"""
        params = {'query': 'test', 'num_results': 0}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_1004')
    
    def test_invalid_num_results_too_high(self):
        """Test error handling for num_results > 20"""
        params = {'query': 'test', 'num_results': 21}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_1004')
    
    def test_missing_required_field(self):
        """Test error handling for missing query field"""
        params = {'num_results': 5}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_1004')
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_rate_limit_error(self, mock_search):
        """Test rate limit error handling"""
        mock_search.side_effect = RateLimitError("Rate limit exceeded")
        
        params = {'query': 'test query', 'num_results': 5}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_5003')
        self.assertIn('Rate limit', result['error']['message'])
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_network_error(self, mock_search):
        """Test network error handling"""
        mock_search.side_effect = NetworkError("Network connection failed")
        
        params = {'query': 'test query', 'num_results': 5}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_5002')
        self.assertIn('Network', result['error']['message'])
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_timeout_error(self, mock_search):
        """Test timeout error handling"""
        mock_search.side_effect = TimeoutError("Request timed out")
        
        params = {'query': 'test query', 'num_results': 5}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_3001')
        self.assertIn('timed out', result['error']['message'].lower())
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_api_error(self, mock_search):
        """Test general API error handling"""
        mock_search.side_effect = SearchAPIError("API error occurred")
        
        params = {'query': 'test query', 'num_results': 5}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_5001')
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_unexpected_error(self, mock_search):
        """Test unexpected error handling"""
        mock_search.side_effect = Exception("Unexpected error")
        
        params = {'query': 'test query', 'num_results': 5}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_4001')
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_result_processing(self, mock_search):
        """Test result processing and structure"""
        mock_search.return_value = self.sample_results
        
        params = {'query': 'test', 'num_results': 5}
        result = self.tool.execute(params)
        
        self.assertNotIn('error', result)
        self.assertEqual(len(result['results']), 2)
        
        # Check result structure
        for r in result['results']:
            self.assertIn('title', r)
            self.assertIn('url', r)
            self.assertIn('snippet', r)
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_empty_results(self, mock_search):
        """Test handling of empty results"""
        mock_search.return_value = []
        
        params = {'query': 'test', 'num_results': 5}
        result = self.tool.execute(params)
        
        self.assertNotIn('error', result)
        self.assertEqual(result['total_results'], 0)
        self.assertEqual(len(result['results']), 0)
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_default_num_results(self, mock_search):
        """Test default num_results value"""
        mock_search.return_value = self.sample_results
        
        params = {'query': 'test'}
        result = self.tool.execute(params)
        
        self.assertNotIn('error', result)
        # Default is 5, but we only have 2 results
        self.assertEqual(len(result['results']), 2)
    
    def test_invalid_sort_by(self):
        """Test invalid sort_by parameter"""
        params = {'query': 'test', 'sort_by': 'invalid'}
        result = self.tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_1004')


class TestSearchConvenienceFunction(unittest.TestCase):
    """Test cases for search() convenience function"""
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_search_function(self, mock_search):
        """Test search convenience function"""
        mock_search.return_value = [
            {'title': 'Test', 'link': 'https://test.com', 'snippet': 'Snippet'}
        ]
        
        result = search('test query', num_results=5)
        
        self.assertNotIn('error', result)
        self.assertEqual(result['query'], 'test query')
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_search_function_defaults(self, mock_search):
        """Test search function with default parameters"""
        mock_search.return_value = []
        
        result = search('test')
        
        self.assertNotIn('error', result)


class TestSearchAPIClient(unittest.TestCase):
    """Test cases for SearchAPIClient"""
    
    def test_invalid_input_empty_query(self):
        """Test InvalidInputError for empty query"""
        client = SearchAPIClient()
        
        with self.assertRaises(InvalidInputError):
            client.search('')
    
    def test_invalid_input_whitespace_query(self):
        """Test InvalidInputError for whitespace query"""
        client = SearchAPIClient()
        
        with self.assertRaises(InvalidInputError):
            client.search('   ')
    
    def test_invalid_input_max_results_low(self):
        """Test InvalidInputError for max_results < 1"""
        client = SearchAPIClient()
        
        with self.assertRaises(InvalidInputError):
            client.search('test', max_results=0)
    
    def test_invalid_input_max_results_high(self):
        """Test InvalidInputError for max_results > 50"""
        client = SearchAPIClient()
        
        with self.assertRaises(InvalidInputError):
            client.search('test', max_results=51)
    
    def test_rate_limit_delay(self):
        """Test rate limiting delay"""
        import time
        client = SearchAPIClient(rate_limit_delay=0.1)
        
        # Mock the search to avoid actual API calls
        with patch('day_35.search_api_client.DDGS') as mock_ddgs:
            mock_instance = MagicMock()
            mock_instance.__enter__.return_value.text.return_value = []
            mock_ddgs.return_value = mock_instance
            
            start = time.time()
            client.search('test1', max_results=1)
            client.search('test2', max_results=1)
            elapsed = time.time() - start
            
            # Should take at least 0.1 seconds due to rate limiting
            self.assertGreaterEqual(elapsed, 0.1)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases"""
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_special_characters_in_query(self, mock_search):
        """Test query with special characters"""
        mock_search.return_value = []
        
        tool = WebSearchTool()
        params = {'query': 'test @#$% query', 'num_results': 5}
        result = tool.execute(params)
        
        self.assertNotIn('error', result)
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_unicode_in_query(self, mock_search):
        """Test query with unicode characters"""
        mock_search.return_value = []
        
        tool = WebSearchTool()
        params = {'query': 'Python 编程 tutorial', 'num_results': 5}
        result = tool.execute(params)
        
        self.assertNotIn('error', result)
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_very_long_query(self, mock_search):
        """Test very long query (should fail validation)"""
        tool = WebSearchTool()
        long_query = 'a' * 501  # Max is 500
        params = {'query': long_query, 'num_results': 5}
        result = tool.execute(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error']['code'], 'ERR_1004')
    
    @patch('day_35.web_search_tool.SearchAPIClient.search')
    def test_max_valid_query_length(self, mock_search):
        """Test maximum valid query length"""
        mock_search.return_value = []
        
        tool = WebSearchTool()
        max_query = 'a' * 500  # Max is 500
        params = {'query': max_query, 'num_results': 5}
        result = tool.execute(params)
        
        self.assertNotIn('error', result)


def run_tests():
    """Run all tests and print results"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestWebSearchTool))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchConvenienceFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchAPIClient))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
