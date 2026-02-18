import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple

class ExampleValidator:
    def __init__(self, tool_schemas_dir: str):
        self.tool_schemas = self._load_tool_schemas(tool_schemas_dir)
    
    def _load_tool_schemas(self, schemas_dir: str) -> Dict[str, Dict]:
        schemas = {}
        schema_path = Path(schemas_dir)
        for file in schema_path.glob("*.json"):
            with open(file) as f:
                schema = json.load(f)
                schemas[schema['name']] = schema
        return schemas
    
    def validate_example_structure(self, example: Dict, category: str) -> List[str]:
        errors = []
        required_fields = ['name', 'description', 'input', 'output']
        
        for field in required_fields:
            if field not in example:
                errors.append(f"Missing required field: {field}")
        
        if 'name' in example and not isinstance(example['name'], str):
            errors.append("Field 'name' must be a string")
        
        if 'description' in example and not isinstance(example['description'], str):
            errors.append("Field 'description' must be a string")
        
        if 'input' in example and not isinstance(example['input'], dict):
            errors.append("Field 'input' must be an object")
        
        if 'output' in example and not isinstance(example['output'], (dict, list)):
            errors.append("Field 'output' must be an object or array")
        
        return errors
    
    def validate_example_input(self, tool_name: str, input_data: Dict, is_error_case: bool = False) -> List[str]:
        errors = []
        
        if tool_name not in self.tool_schemas:
            return [f"Unknown tool: {tool_name}"]
        
        schema = self.tool_schemas[tool_name]
        params = schema['parameters']['properties']
        required = schema['parameters'].get('required', [])
        
        # For error cases, skip validation as they intentionally have invalid input
        if is_error_case:
            return errors
        
        # Check required fields
        for field in required:
            if field not in input_data:
                errors.append(f"Missing required parameter: {field}")
        
        # Validate each input field
        for field, value in input_data.items():
            if field not in params:
                errors.append(f"Unknown parameter: {field}")
                continue
            
            field_schema = params[field]
            field_errors = self._validate_field(field, value, field_schema)
            errors.extend(field_errors)
        
        return errors
    
    def _validate_field(self, field_name: str, value: Any, schema: Dict) -> List[str]:
        errors = []
        field_type = schema.get('type')
        
        # Type validation
        if field_type == 'string':
            if not isinstance(value, str):
                errors.append(f"{field_name}: expected string, got {type(value).__name__}")
            else:
                if 'minLength' in schema and len(value) < schema['minLength']:
                    errors.append(f"{field_name}: length {len(value)} < minimum {schema['minLength']}")
                if 'maxLength' in schema and len(value) > schema['maxLength']:
                    errors.append(f"{field_name}: length {len(value)} > maximum {schema['maxLength']}")
                if 'pattern' in schema and not re.match(schema['pattern'], value):
                    errors.append(f"{field_name}: does not match pattern {schema['pattern']}")
                if 'enum' in schema and value not in schema['enum']:
                    errors.append(f"{field_name}: value '{value}' not in allowed values {schema['enum']}")
        
        elif field_type == 'integer':
            if not isinstance(value, int) or isinstance(value, bool):
                errors.append(f"{field_name}: expected integer, got {type(value).__name__}")
            else:
                if 'minimum' in schema and value < schema['minimum']:
                    errors.append(f"{field_name}: value {value} < minimum {schema['minimum']}")
                if 'maximum' in schema and value > schema['maximum']:
                    errors.append(f"{field_name}: value {value} > maximum {schema['maximum']}")
        
        elif field_type == 'boolean':
            if not isinstance(value, bool):
                errors.append(f"{field_name}: expected boolean, got {type(value).__name__}")
        
        elif field_type == 'array':
            if not isinstance(value, list):
                errors.append(f"{field_name}: expected array, got {type(value).__name__}")
            else:
                if 'minItems' in schema and len(value) < schema['minItems']:
                    errors.append(f"{field_name}: array length {len(value)} < minimum {schema['minItems']}")
                if 'maxItems' in schema and len(value) > schema['maxItems']:
                    errors.append(f"{field_name}: array length {len(value)} > maximum {schema['maxItems']}")
        
        return errors
    
    def validate_example_output(self, output_data: Any, is_error: bool = False) -> List[str]:
        errors = []
        
        if is_error:
            if not isinstance(output_data, dict):
                errors.append("Error output must be an object")
            elif 'error' not in output_data:
                errors.append("Error output must contain 'error' field")
        else:
            if output_data is None:
                errors.append("Output cannot be None for success case")
        
        return errors
    
    def validate_examples_file(self, file_path: str) -> Tuple[bool, List[str]]:
        all_errors = []
        
        try:
            with open(file_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON: {e}"]
        except FileNotFoundError:
            return False, [f"File not found: {file_path}"]
        
        if 'tool_name' not in data:
            all_errors.append("Missing 'tool_name' field")
            return False, all_errors
        
        tool_name = data['tool_name']
        
        if 'examples' not in data:
            all_errors.append("Missing 'examples' field")
            return False, all_errors
        
        examples = data['examples']
        categories = ['common_use_cases', 'advanced_use_cases', 'edge_cases', 'error_cases']
        
        for category in categories:
            if category not in examples:
                all_errors.append(f"Missing category: {category}")
                continue
            
            if not isinstance(examples[category], list):
                all_errors.append(f"{category} must be an array")
                continue
            
            for idx, example in enumerate(examples[category]):
                example_path = f"{category}[{idx}]"
                
                # Validate structure
                struct_errors = self.validate_example_structure(example, category)
                for err in struct_errors:
                    all_errors.append(f"{example_path}: {err}")
                
                if struct_errors:
                    continue
                
                # Validate input
                is_error = category == 'error_cases'
                input_errors = self.validate_example_input(tool_name, example['input'], is_error)
                for err in input_errors:
                    all_errors.append(f"{example_path}.input: {err}")
                
                # Validate output
                output_errors = self.validate_example_output(example['output'], is_error)
                for err in output_errors:
                    all_errors.append(f"{example_path}.output: {err}")
        
        return len(all_errors) == 0, all_errors


def main():
    tool_schemas_dir = "day_31/tool_definitions"
    examples_dir = "day_34/examples"
    
    validator = ExampleValidator(tool_schemas_dir)
    
    example_files = [
        f"{examples_dir}/email_tool_examples.json",
        f"{examples_dir}/database_query_examples.json",
        f"{examples_dir}/web_search_examples.json"
    ]
    
    print("Validating example files...\n")
    
    all_valid = True
    for file_path in example_files:
        print(f"Validating: {file_path}")
        is_valid, errors = validator.validate_examples_file(file_path)
        
        if is_valid:
            print("✓ Valid\n")
        else:
            print(f"✗ Found {len(errors)} error(s):")
            for error in errors:
                print(f"  - {error}")
            print()
            all_valid = False
    
    if all_valid:
        print("All examples are valid!")
    else:
        print("Some examples have validation errors.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
