import unittest
import json
import tempfile
import os
from example_validator import ExampleValidator


class TestExampleValidator(unittest.TestCase):
    def setUp(self):
        self.validator = ExampleValidator("day_31/tool_definitions")
    
    def test_validate_structure_valid(self):
        example = {
            "name": "Test example",
            "description": "Test description",
            "input": {"query": "test"},
            "output": {"results": []}
        }
        errors = self.validator.validate_example_structure(example, "common_use_cases")
        self.assertEqual(errors, [])
    
    def test_validate_structure_missing_fields(self):
        example = {"name": "Test"}
        errors = self.validator.validate_example_structure(example, "common_use_cases")
        self.assertIn("Missing required field: description", errors)
        self.assertIn("Missing required field: input", errors)
        self.assertIn("Missing required field: output", errors)
    
    def test_validate_input_valid(self):
        input_data = {
            "query": "test query",
            "num_results": 5
        }
        errors = self.validator.validate_example_input("web_search", input_data)
        self.assertEqual(errors, [])
    
    def test_validate_input_missing_required(self):
        input_data = {"num_results": 5}
        errors = self.validator.validate_example_input("web_search", input_data)
        self.assertIn("Missing required parameter: query", errors)
    
    def test_validate_input_invalid_type(self):
        input_data = {
            "query": "test",
            "num_results": "five"
        }
        errors = self.validator.validate_example_input("web_search", input_data)
        self.assertTrue(any("expected integer" in e for e in errors))
    
    def test_validate_input_out_of_range(self):
        input_data = {
            "query": "test",
            "num_results": 25
        }
        errors = self.validator.validate_example_input("web_search", input_data)
        self.assertTrue(any("maximum" in e for e in errors))
    
    def test_validate_input_error_case_skipped(self):
        input_data = {"query": ""}
        errors = self.validator.validate_example_input("web_search", input_data, is_error_case=True)
        self.assertEqual(errors, [])
    
    def test_validate_output_success(self):
        output = {"results": [], "count": 0}
        errors = self.validator.validate_example_output(output, is_error=False)
        self.assertEqual(errors, [])
    
    def test_validate_output_error_missing_field(self):
        output = {"message": "Error occurred"}
        errors = self.validator.validate_example_output(output, is_error=True)
        self.assertIn("Error output must contain 'error' field", errors)
    
    def test_validate_examples_file_valid(self):
        is_valid, errors = self.validator.validate_examples_file(
            "day_34/examples/web_search_examples.json"
        )
        self.assertTrue(is_valid)
        self.assertEqual(errors, [])
    
    def test_validate_examples_file_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{invalid json")
            temp_file = f.name
        
        try:
            is_valid, errors = self.validator.validate_examples_file(temp_file)
            self.assertFalse(is_valid)
            self.assertTrue(any("Invalid JSON" in e for e in errors))
        finally:
            os.unlink(temp_file)
    
    def test_validate_examples_file_missing_tool_name(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"examples": {}}, f)
            temp_file = f.name
        
        try:
            is_valid, errors = self.validator.validate_examples_file(temp_file)
            self.assertFalse(is_valid)
            self.assertIn("Missing 'tool_name' field", errors)
        finally:
            os.unlink(temp_file)
    
    def test_email_validation(self):
        input_data = {
            "to": ["user@example.com"],
            "subject": "Test",
            "body": "Test body"
        }
        errors = self.validator.validate_example_input("send_email", input_data)
        self.assertEqual(errors, [])
    
    def test_database_validation(self):
        input_data = {
            "query": "SELECT * FROM users",
            "database": "production",
            "parameters": []
        }
        errors = self.validator.validate_example_input("query_database", input_data)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
