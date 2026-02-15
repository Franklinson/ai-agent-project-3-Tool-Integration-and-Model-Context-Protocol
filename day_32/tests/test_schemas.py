#!/usr/bin/env python3
"""Comprehensive test suite for schema validation."""

import unittest
import sys
import os

# Add validators directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'validators'))
from schema_validator import SchemaValidator

class TestWebSearchInputSchema(unittest.TestCase):
    """Test web search input schema validation."""
    
    def setUp(self):
        self.validator = SchemaValidator()
    
    def test_valid_input_all_parameters(self):
        """Test valid input with all parameters."""
        data = {
            "query": "python programming",
            "num_results": 10,
            "sort_by": "relevance"
        }
        is_valid, error = self.validator.validate_input(data, "web_search_input")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_valid_input_required_only(self):
        """Test valid input with only required parameters."""
        data = {"query": "machine learning"}
        is_valid, error = self.validator.validate_input(data, "web_search_input")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_missing_required_query(self):
        """Test missing required query parameter."""
        data = {"num_results": 5}
        is_valid, error = self.validator.validate_input(data, "web_search_input")
        self.assertFalse(is_valid)
        self.assertIn("query", error)
    
    def test_invalid_type_num_results(self):
        """Test invalid type for num_results."""
        data = {
            "query": "test",
            "num_results": "five"
        }
        is_valid, error = self.validator.validate_input(data, "web_search_input")
        self.assertFalse(is_valid)
        self.assertIn("expected integer", error)
    
    def test_constraint_violation_query_too_long(self):
        """Test query exceeding maximum length."""
        data = {"query": "x" * 501}
        is_valid, error = self.validator.validate_input(data, "web_search_input")
        self.assertFalse(is_valid)
        self.assertIn("too long", error)
    
    def test_constraint_violation_num_results_out_of_range(self):
        """Test num_results outside valid range."""
        data = {
            "query": "test",
            "num_results": 25
        }
        is_valid, error = self.validator.validate_input(data, "web_search_input")
        self.assertFalse(is_valid)
        self.assertIn("too large", error)
    
    def test_invalid_enum_sort_by(self):
        """Test invalid enum value for sort_by."""
        data = {
            "query": "test",
            "sort_by": "popularity"
        }
        is_valid, error = self.validator.validate_input(data, "web_search_input")
        self.assertFalse(is_valid)
        self.assertIn("must be one of", error)
    
    def test_edge_case_minimum_values(self):
        """Test edge case with minimum valid values."""
        data = {
            "query": "ab",  # Minimum valid query matching pattern
            "num_results": 1,
            "sort_by": "date"
        }
        is_valid, error = self.validator.validate_input(data, "web_search_input")
        self.assertTrue(is_valid, f"Should be valid: {error}")

class TestDatabaseQueryInputSchema(unittest.TestCase):
    """Test database query input schema validation."""
    
    def setUp(self):
        self.validator = SchemaValidator()
    
    def test_valid_input_all_parameters(self):
        """Test valid input with all parameters."""
        data = {
            "query": "SELECT * FROM users WHERE active = 1",
            "database": "users_db",
            "timeout": 60
        }
        is_valid, error = self.validator.validate_input(data, "database_query_input")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_valid_input_required_only(self):
        """Test valid input with only required parameters."""
        data = {
            "query": "SELECT COUNT(*) FROM products",
            "database": "products_db"
        }
        is_valid, error = self.validator.validate_input(data, "database_query_input")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_missing_required_query(self):
        """Test missing required query parameter."""
        data = {"database": "users_db"}
        is_valid, error = self.validator.validate_input(data, "database_query_input")
        self.assertFalse(is_valid)
        self.assertIn("query", error)
    
    def test_missing_required_database(self):
        """Test missing required database parameter."""
        data = {"query": "SELECT * FROM users"}
        is_valid, error = self.validator.validate_input(data, "database_query_input")
        self.assertFalse(is_valid)
        self.assertIn("database", error)
    
    def test_invalid_database_enum(self):
        """Test invalid database enum value."""
        data = {
            "query": "SELECT * FROM users",
            "database": "invalid_db"
        }
        is_valid, error = self.validator.validate_input(data, "database_query_input")
        self.assertFalse(is_valid)
        self.assertIn("must be one of", error)
    
    def test_invalid_timeout_type(self):
        """Test invalid timeout type."""
        data = {
            "query": "SELECT * FROM users",
            "database": "users_db",
            "timeout": "30"
        }
        is_valid, error = self.validator.validate_input(data, "database_query_input")
        self.assertFalse(is_valid)
        self.assertIn("expected integer", error)
    
    def test_timeout_out_of_range(self):
        """Test timeout outside valid range."""
        data = {
            "query": "SELECT * FROM users",
            "database": "users_db",
            "timeout": 500
        }
        is_valid, error = self.validator.validate_input(data, "database_query_input")
        self.assertFalse(is_valid)
        self.assertIn("too large", error)

class TestEmailInputSchema(unittest.TestCase):
    """Test email input schema validation."""
    
    def setUp(self):
        self.validator = SchemaValidator()
    
    def test_valid_input_all_parameters(self):
        """Test valid input with all parameters."""
        data = {
            "to": "recipient@example.com",
            "subject": "Test Email",
            "body": "This is a test email message.",
            "cc": ["cc1@example.com", "cc2@example.com"]
        }
        is_valid, error = self.validator.validate_input(data, "email_input")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_valid_input_required_only(self):
        """Test valid input with only required parameters."""
        data = {
            "to": "user@company.com",
            "subject": "Important Update",
            "body": "Please review the attached document."
        }
        is_valid, error = self.validator.validate_input(data, "email_input")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_missing_required_to(self):
        """Test missing required to parameter."""
        data = {
            "subject": "Test",
            "body": "Test message"
        }
        is_valid, error = self.validator.validate_input(data, "email_input")
        self.assertFalse(is_valid)
        self.assertIn("to", error)
    
    def test_missing_required_subject(self):
        """Test missing required subject parameter."""
        data = {
            "to": "user@example.com",
            "body": "Test message"
        }
        is_valid, error = self.validator.validate_input(data, "email_input")
        self.assertFalse(is_valid)
        self.assertIn("subject", error)
    
    def test_subject_too_long(self):
        """Test subject exceeding maximum length."""
        data = {
            "to": "user@example.com",
            "subject": "x" * 201,
            "body": "Test message"
        }
        is_valid, error = self.validator.validate_input(data, "email_input")
        self.assertFalse(is_valid)
        self.assertIn("too long", error)
    
    def test_body_too_long(self):
        """Test body exceeding maximum length."""
        data = {
            "to": "user@example.com",
            "subject": "Test",
            "body": "x" * 10001
        }
        is_valid, error = self.validator.validate_input(data, "email_input")
        self.assertFalse(is_valid)
        self.assertIn("too long", error)
    
    def test_duplicate_cc_addresses(self):
        """Test duplicate CC addresses."""
        data = {
            "to": "user@example.com",
            "subject": "Test",
            "body": "Test message",
            "cc": ["same@example.com", "same@example.com"]
        }
        is_valid, error = self.validator.validate_input(data, "email_input")
        self.assertFalse(is_valid)
        self.assertIn("unique", error)
    
    def test_too_many_cc_addresses(self):
        """Test too many CC addresses."""
        data = {
            "to": "user@example.com",
            "subject": "Test",
            "body": "Test message",
            "cc": [f"user{i}@example.com" for i in range(11)]
        }
        is_valid, error = self.validator.validate_input(data, "email_input")
        self.assertFalse(is_valid)
        self.assertIn("too many items", error)

class TestWebSearchOutputSchema(unittest.TestCase):
    """Test web search output schema validation."""
    
    def setUp(self):
        self.validator = SchemaValidator()
    
    def test_valid_output(self):
        """Test valid output structure."""
        data = {
            "results": [
                {
                    "title": "Python Tutorial",
                    "url": "https://python.org/tutorial",
                    "snippet": "Learn Python programming basics"
                }
            ],
            "query": "python tutorial",
            "total_results": 1
        }
        is_valid, error = self.validator.validate_output(data, "web_search_output")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_missing_required_results(self):
        """Test missing required results field."""
        data = {
            "query": "test",
            "total_results": 0
        }
        is_valid, error = self.validator.validate_output(data, "web_search_output")
        self.assertFalse(is_valid)
        self.assertIn("results", error)
    
    def test_invalid_result_structure(self):
        """Test invalid result object structure."""
        data = {
            "results": [
                {
                    "title": "Test",
                    "url": "https://example.com"
                    # Missing snippet
                }
            ],
            "query": "test",
            "total_results": 1
        }
        is_valid, error = self.validator.validate_output(data, "web_search_output")
        self.assertFalse(is_valid)
        self.assertIn("snippet", error)
    
    def test_invalid_total_results_type(self):
        """Test invalid total_results type."""
        data = {
            "results": [],
            "query": "test",
            "total_results": "zero"
        }
        is_valid, error = self.validator.validate_output(data, "web_search_output")
        self.assertFalse(is_valid)
        self.assertIn("expected integer", error)

class TestDatabaseQueryOutputSchema(unittest.TestCase):
    """Test database query output schema validation."""
    
    def setUp(self):
        self.validator = SchemaValidator()
    
    def test_valid_output(self):
        """Test valid output structure."""
        data = {
            "rows": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ],
            "row_count": 2,
            "execution_time_ms": 45.2
        }
        is_valid, error = self.validator.validate_output(data, "database_query_output")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_empty_rows_valid(self):
        """Test valid output with empty rows."""
        data = {
            "rows": [],
            "row_count": 0,
            "execution_time_ms": 12.1
        }
        is_valid, error = self.validator.validate_output(data, "database_query_output")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_missing_required_row_count(self):
        """Test missing required row_count field."""
        data = {
            "rows": [],
            "execution_time_ms": 10.0
        }
        is_valid, error = self.validator.validate_output(data, "database_query_output")
        self.assertFalse(is_valid)
        self.assertIn("row_count", error)
    
    def test_invalid_execution_time_type(self):
        """Test invalid execution_time_ms type."""
        data = {
            "rows": [],
            "row_count": 0,
            "execution_time_ms": "fast"
        }
        is_valid, error = self.validator.validate_output(data, "database_query_output")
        self.assertFalse(is_valid)
        self.assertIn("expected number", error)

class TestEmailOutputSchema(unittest.TestCase):
    """Test email output schema validation."""
    
    def setUp(self):
        self.validator = SchemaValidator()
    
    def test_valid_output_sent(self):
        """Test valid output with sent status."""
        data = {
            "message_id": "msg-123-abc",
            "status": "sent",
            "sent_at": "2024-01-15T10:30:00Z"
        }
        is_valid, error = self.validator.validate_output(data, "email_output")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_valid_output_failed(self):
        """Test valid output with failed status."""
        data = {
            "message_id": "msg-456-def",
            "status": "failed",
            "sent_at": "2024-01-15T10:30:00Z"
        }
        is_valid, error = self.validator.validate_output(data, "email_output")
        self.assertTrue(is_valid, f"Should be valid: {error}")
    
    def test_missing_required_message_id(self):
        """Test missing required message_id field."""
        data = {
            "status": "sent",
            "sent_at": "2024-01-15T10:30:00Z"
        }
        is_valid, error = self.validator.validate_output(data, "email_output")
        self.assertFalse(is_valid)
        self.assertIn("message_id", error)
    
    def test_invalid_status_enum(self):
        """Test invalid status enum value."""
        data = {
            "message_id": "msg-123",
            "status": "pending",
            "sent_at": "2024-01-15T10:30:00Z"
        }
        is_valid, error = self.validator.validate_output(data, "email_output")
        self.assertFalse(is_valid)
        self.assertIn("must be one of", error)

class TestErrorResponseSchema(unittest.TestCase):
    """Test error response schema validation."""
    
    def setUp(self):
        self.validator = SchemaValidator()
    
    def test_valid_error_with_details(self):
        """Test valid error response with details."""
        data = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed",
                "details": {"field": "query", "issue": "too short"}
            }
        }
        schema_path = os.path.join(self.validator.schema_base_path, 'output_schemas', 'error_response.json')
        schema = self.validator.load_schema(schema_path)
        try:
            self.validator._validate_object(data, schema)
            result = True
        except Exception:
            result = False
        self.assertTrue(result, "Should be valid")
    
    def test_valid_error_without_details(self):
        """Test valid error response without details."""
        data = {
            "error": {
                "code": "NOT_FOUND",
                "message": "Resource not found"
            }
        }
        schema_path = os.path.join(self.validator.schema_base_path, 'output_schemas', 'error_response.json')
        schema = self.validator.load_schema(schema_path)
        try:
            self.validator._validate_object(data, schema)
            result = True
        except Exception:
            result = False
        self.assertTrue(result, "Should be valid")
    
    def test_missing_required_message(self):
        """Test missing required message field."""
        data = {
            "error": {
                "code": "ERROR_CODE"
            }
        }
        schema_path = os.path.join(self.validator.schema_base_path, 'output_schemas', 'error_response.json')
        schema = self.validator.load_schema(schema_path)
        try:
            self.validator._validate_object(data, schema)
            result = True
        except Exception as e:
            result = False
            error_msg = str(e)
        self.assertFalse(result)
        self.assertIn("message", error_msg)

if __name__ == '__main__':
    unittest.main(verbosity=2)