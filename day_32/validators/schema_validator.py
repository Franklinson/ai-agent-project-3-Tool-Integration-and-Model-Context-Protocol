import json
import os
from typing import Dict, Any, Tuple, Optional

class ValidationError(Exception):
    """Custom validation error for schema validation failures."""
    pass

class SchemaValidator:
    """Schema validation system for tool inputs and outputs."""
    
    def __init__(self, schema_base_path: str = None):
        self.schema_base_path = schema_base_path or os.path.join(os.path.dirname(__file__), '..', 'schemas')
        self._schema_cache = {}
    
    def load_schema(self, file_path: str) -> Dict[str, Any]:
        """Load JSON schema from file with caching."""
        if file_path in self._schema_cache:
            return self._schema_cache[file_path]
        
        try:
            with open(file_path, 'r') as f:
                schema = json.load(f)
            self._schema_cache[file_path] = schema
            return schema
        except FileNotFoundError:
            raise ValidationError(f"Schema file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON in schema file {file_path}: {e}")
    
    def _validate_type(self, value: Any, expected_type: str, field_name: str = "") -> None:
        """Validate value type against expected type."""
        type_map = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type and not isinstance(value, expected_python_type):
            raise ValidationError(f"Field '{field_name}': expected {expected_type}, got {type(value).__name__}")
    
    def _validate_constraints(self, value: Any, constraints: Dict[str, Any], field_name: str = "") -> None:
        """Validate value against constraints."""
        if isinstance(value, str):
            if 'minLength' in constraints and len(value) < constraints['minLength']:
                raise ValidationError(f"Field '{field_name}': string too short (min {constraints['minLength']})")
            if 'maxLength' in constraints and len(value) > constraints['maxLength']:
                raise ValidationError(f"Field '{field_name}': string too long (max {constraints['maxLength']})")
            if 'pattern' in constraints:
                import re
                if not re.match(constraints['pattern'], value):
                    raise ValidationError(f"Field '{field_name}': does not match required pattern")
            if 'enum' in constraints and value not in constraints['enum']:
                raise ValidationError(f"Field '{field_name}': must be one of {constraints['enum']}")
        
        if isinstance(value, (int, float)):
            if 'minimum' in constraints and value < constraints['minimum']:
                raise ValidationError(f"Field '{field_name}': value too small (min {constraints['minimum']})")
            if 'maximum' in constraints and value > constraints['maximum']:
                raise ValidationError(f"Field '{field_name}': value too large (max {constraints['maximum']})")
        
        if isinstance(value, list):
            if 'maxItems' in constraints and len(value) > constraints['maxItems']:
                raise ValidationError(f"Field '{field_name}': too many items (max {constraints['maxItems']})")
            if 'uniqueItems' in constraints and constraints['uniqueItems']:
                if len(value) != len(set(str(item) for item in value)):
                    raise ValidationError(f"Field '{field_name}': items must be unique")
    
    def _validate_object(self, data: Dict[str, Any], schema: Dict[str, Any], path: str = "") -> None:
        """Validate object against schema."""
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        # Check required fields
        for field in required:
            if field not in data:
                raise ValidationError(f"Missing required field: {path}.{field}" if path else field)
        
        # Validate each field
        for field, value in data.items():
            field_path = f"{path}.{field}" if path else field
            if field in properties:
                self._validate_field(value, properties[field], field_path)
            elif not schema.get('additionalProperties', True):
                raise ValidationError(f"Additional property not allowed: {field_path}")
    
    def _validate_field(self, value: Any, field_schema: Dict[str, Any], field_name: str = "") -> None:
        """Validate a single field against its schema."""
        field_type = field_schema.get('type')
        
        if field_type:
            self._validate_type(value, field_type, field_name)
        
        self._validate_constraints(value, field_schema, field_name)
        
        if field_type == 'object':
            self._validate_object(value, field_schema, field_name)
        elif field_type == 'array' and 'items' in field_schema:
            for i, item in enumerate(value):
                self._validate_field(item, field_schema['items'], f"{field_name}[{i}]")
    
    def validate_input(self, data: Dict[str, Any], schema_name: str) -> Tuple[bool, Optional[str]]:
        """Validate input data against input schema."""
        try:
            schema_path = os.path.join(self.schema_base_path, 'input_schemas', f'{schema_name}.json')
            schema = self.load_schema(schema_path)
            self._validate_object(data, schema)
            return True, None
        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {e}"
    
    def validate_output(self, data: Dict[str, Any], schema_name: str) -> Tuple[bool, Optional[str]]:
        """Validate output data against output schema."""
        try:
            schema_path = os.path.join(self.schema_base_path, 'output_schemas', f'{schema_name}.json')
            schema = self.load_schema(schema_path)
            self._validate_object(data, schema)
            return True, None
        except ValidationError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {e}"

# Convenience functions
def validate_tool_input(data: Dict[str, Any], tool_name: str) -> Tuple[bool, Optional[str]]:
    """Validate tool input data."""
    validator = SchemaValidator()
    return validator.validate_input(data, f"{tool_name}_input")

def validate_tool_output(data: Dict[str, Any], tool_name: str) -> Tuple[bool, Optional[str]]:
    """Validate tool output data."""
    validator = SchemaValidator()
    return validator.validate_output(data, f"{tool_name}_output")