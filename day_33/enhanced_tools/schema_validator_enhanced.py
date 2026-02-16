"""Enhanced schema validator with comprehensive error handling."""

import json
import os
import logging
from typing import Dict, Any, Tuple, Optional
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from error_handling import (
    create_error_response,
    ErrorCode,
    retry_with_backoff,
    TRANSIENT_ERRORS
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ValidationError(Exception):
    """Custom validation error."""
    pass


class SchemaValidator:
    """Schema validator with comprehensive error handling."""
    
    def __init__(self, schema_base_path: str = None, timeout: int = 5):
        self.schema_base_path = schema_base_path or os.path.join(
            os.path.dirname(__file__), '..', '..', 'day_32', 'schemas'
        )
        self.timeout = timeout
        self._schema_cache = {}
        logger.info(f"SchemaValidator initialized with path: {self.schema_base_path}")
    
    @retry_with_backoff(max_retries=2, base_delay=0.5, retry_on=TRANSIENT_ERRORS)
    def load_schema(self, file_path: str) -> Dict[str, Any]:
        """Load schema with error handling and retry."""
        try:
            if file_path in self._schema_cache:
                logger.debug(f"Schema loaded from cache: {file_path}")
                return self._schema_cache[file_path]
            
            if not os.path.exists(file_path):
                error = create_error_response(
                    ErrorCode.NOT_FOUND,
                    f"Schema file not found: {file_path}",
                    {"path": file_path}
                )
                logger.error(f"Schema file not found: {file_path}")
                raise FileNotFoundError(error)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            self._schema_cache[file_path] = schema
            logger.info(f"Schema loaded successfully: {file_path}")
            return schema
            
        except json.JSONDecodeError as e:
            error = create_error_response(
                ErrorCode.INVALID_FORMAT,
                f"Invalid JSON in schema file",
                {"path": file_path, "error": str(e), "line": e.lineno}
            )
            logger.error(f"JSON decode error in {file_path}: {e}")
            raise ValidationError(error)
        except IOError as e:
            error = create_error_response(
                ErrorCode.INTERNAL_ERROR,
                f"Failed to read schema file",
                {"path": file_path, "error": str(e)}
            )
            logger.error(f"IO error reading {file_path}: {e}")
            raise IOError(error)
    
    def _validate_type(self, value: Any, expected_type: str, field_name: str = "") -> None:
        """Validate type with error handling."""
        try:
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
                raise ValidationError(
                    f"Field '{field_name}': expected {expected_type}, got {type(value).__name__}"
                )
        except Exception as e:
            logger.error(f"Type validation error for field '{field_name}': {e}")
            raise
    
    def _validate_constraints(self, value: Any, constraints: Dict[str, Any], field_name: str = "") -> None:
        """Validate constraints with error handling."""
        try:
            if isinstance(value, str):
                if 'minLength' in constraints and len(value) < constraints['minLength']:
                    raise ValidationError(
                        f"Field '{field_name}': string too short (min {constraints['minLength']})"
                    )
                if 'maxLength' in constraints and len(value) > constraints['maxLength']:
                    raise ValidationError(
                        f"Field '{field_name}': string too long (max {constraints['maxLength']})"
                    )
            
            if isinstance(value, (int, float)):
                if 'minimum' in constraints and value < constraints['minimum']:
                    raise ValidationError(
                        f"Field '{field_name}': value too small (min {constraints['minimum']})"
                    )
                if 'maximum' in constraints and value > constraints['maximum']:
                    raise ValidationError(
                        f"Field '{field_name}': value too large (max {constraints['maximum']})"
                    )
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Constraint validation error for field '{field_name}': {e}")
            raise ValidationError(f"Constraint validation failed: {e}")
    
    def _validate_object(self, data: Dict[str, Any], schema: Dict[str, Any], path: str = "") -> None:
        """Validate object with error handling."""
        try:
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            for field in required:
                if field not in data:
                    raise ValidationError(
                        f"Missing required field: {path}.{field}" if path else field
                    )
            
            for field, value in data.items():
                field_path = f"{path}.{field}" if path else field
                if field in properties:
                    self._validate_field(value, properties[field], field_path)
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Object validation error at path '{path}': {e}")
            raise ValidationError(f"Object validation failed: {e}")
    
    def _validate_field(self, value: Any, field_schema: Dict[str, Any], field_name: str = "") -> None:
        """Validate field with error handling."""
        try:
            field_type = field_schema.get('type')
            
            if field_type:
                self._validate_type(value, field_type, field_name)
            
            self._validate_constraints(value, field_schema, field_name)
            
            if field_type == 'object':
                self._validate_object(value, field_schema, field_name)
            elif field_type == 'array' and 'items' in field_schema:
                for i, item in enumerate(value):
                    self._validate_field(item, field_schema['items'], f"{field_name}[{i}]")
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Field validation error for '{field_name}': {e}")
            raise ValidationError(f"Field validation failed: {e}")
    
    def validate_input(self, data: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
        """Validate input with comprehensive error handling."""
        try:
            if not data:
                return create_error_response(
                    ErrorCode.INVALID_INPUT,
                    "Input data cannot be empty",
                    {"schema": schema_name}
                )
            
            if not isinstance(data, dict):
                return create_error_response(
                    ErrorCode.INVALID_INPUT,
                    "Input data must be a dictionary",
                    {"schema": schema_name, "type": type(data).__name__}
                )
            
            schema_path = os.path.join(self.schema_base_path, 'input_schemas', f'{schema_name}.json')
            schema = self.load_schema(schema_path)
            self._validate_object(data, schema)
            
            logger.info(f"Input validation successful for schema '{schema_name}'")
            return {
                "success": True,
                "schema": schema_name,
                "message": "Validation passed"
            }
            
        except ValidationError as e:
            logger.warning(f"Validation failed for schema '{schema_name}': {e}")
            return create_error_response(
                ErrorCode.VALIDATION_FAILED,
                str(e),
                {"schema": schema_name}
            )
        except FileNotFoundError as e:
            return create_error_response(
                ErrorCode.NOT_FOUND,
                f"Schema not found: {schema_name}",
                {"schema": schema_name}
            )
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            return create_error_response(
                ErrorCode.INTERNAL_ERROR,
                "Validation failed due to internal error",
                {"schema": schema_name, "error": str(e)}
            )
    
    def validate_output(self, data: Dict[str, Any], schema_name: str) -> Dict[str, Any]:
        """Validate output with comprehensive error handling."""
        try:
            if not data:
                return create_error_response(
                    ErrorCode.INVALID_INPUT,
                    "Output data cannot be empty",
                    {"schema": schema_name}
                )
            
            schema_path = os.path.join(self.schema_base_path, 'output_schemas', f'{schema_name}.json')
            schema = self.load_schema(schema_path)
            self._validate_object(data, schema)
            
            logger.info(f"Output validation successful for schema '{schema_name}'")
            return {
                "success": True,
                "schema": schema_name,
                "message": "Validation passed"
            }
            
        except ValidationError as e:
            logger.warning(f"Output validation failed for schema '{schema_name}': {e}")
            return create_error_response(
                ErrorCode.VALIDATION_FAILED,
                str(e),
                {"schema": schema_name}
            )
        except Exception as e:
            logger.error(f"Unexpected output validation error: {e}")
            return create_error_response(
                ErrorCode.INTERNAL_ERROR,
                "Output validation failed",
                {"schema": schema_name, "error": str(e)}
            )
