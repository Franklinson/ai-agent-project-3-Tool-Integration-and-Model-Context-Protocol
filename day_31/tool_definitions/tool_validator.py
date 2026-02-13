import re
import json
from typing import Dict, List, Any


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_tool_definition(tool_def: Dict[str, Any]) -> List[str]:
    """
    Validates a tool definition against required standards.
    
    Args:
        tool_def: Dictionary containing the tool definition
        
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Validate name
    if "name" not in tool_def:
        errors.append("Tool definition must include a 'name' field")
    else:
        errors.extend(_validate_name(tool_def["name"]))
    
    # Validate description
    if "description" not in tool_def:
        errors.append("Tool definition must include a 'description' field")
    else:
        errors.extend(_validate_description(tool_def["description"]))
    
    # Validate parameters
    if "parameters" not in tool_def:
        errors.append("Tool definition must include a 'parameters' field")
    else:
        errors.extend(_validate_parameters(tool_def["parameters"]))
    
    return errors


def _validate_name(name: str) -> List[str]:
    """Validates tool name format and quality."""
    errors = []
    
    # Check snake_case format
    if not re.match(r'^[a-z][a-z0-9_]*$', name):
        errors.append(f"Tool name '{name}' must be in snake_case format (lowercase letters, numbers, and underscores only)")
    
    # Check for generic names
    generic_names = {"tool", "function", "method", "action", "do", "execute", "run"}
    if name in generic_names:
        errors.append(f"Tool name '{name}' is too generic. Use a descriptive name that indicates the tool's purpose")
    
    # Check minimum length
    if len(name) < 3:
        errors.append(f"Tool name '{name}' is too short. Use a descriptive name with at least 3 characters")
    
    return errors


def _validate_description(description: str) -> List[str]:
    """Validates tool description quality."""
    errors = []
    
    if not isinstance(description, str):
        errors.append("Description must be a string")
        return errors
    
    if len(description.strip()) < 50:
        errors.append(f"Description must be at least 50 characters (current: {len(description.strip())}). Provide a detailed explanation of the tool's purpose and behavior")
    
    return errors


def _validate_parameters(parameters: Dict[str, Any]) -> List[str]:
    """Validates parameters schema structure."""
    errors = []
    
    if not isinstance(parameters, dict):
        errors.append("Parameters must be a dictionary")
        return errors
    
    # Check JSON Schema structure
    if "type" not in parameters:
        errors.append("Parameters schema must include a 'type' field")
    elif parameters["type"] != "object":
        errors.append("Parameters schema type must be 'object'")
    
    if "properties" not in parameters:
        errors.append("Parameters schema must include a 'properties' field")
    else:
        if not isinstance(parameters["properties"], dict):
            errors.append("Parameters 'properties' must be a dictionary")
        else:
            # Validate each property
            for prop_name, prop_def in parameters["properties"].items():
                if not isinstance(prop_def, dict):
                    errors.append(f"Property '{prop_name}' must be a dictionary")
                    continue
                
                if "type" not in prop_def:
                    errors.append(f"Property '{prop_name}' must include a 'type' field")
                
                if "description" not in prop_def:
                    errors.append(f"Property '{prop_name}' must include a 'description' field")
    
    # Validate required fields
    if "required" in parameters:
        if not isinstance(parameters["required"], list):
            errors.append("Parameters 'required' field must be a list")
        else:
            # Check that required fields exist in properties
            if "properties" in parameters:
                for req_field in parameters["required"]:
                    if req_field not in parameters["properties"]:
                        errors.append(f"Required field '{req_field}' not found in properties")
    
    return errors


def validate_tool_file(filepath: str) -> bool:
    """
    Validates a tool definition from a JSON file.
    
    Args:
        filepath: Path to the JSON file containing tool definition
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If validation fails with detailed error messages
    """
    try:
        with open(filepath, 'r') as f:
            tool_def = json.load(f)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {e}")
    except FileNotFoundError:
        raise ValidationError(f"File not found: {filepath}")
    
    errors = validate_tool_definition(tool_def)
    
    if errors:
        error_msg = "Tool definition validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
        raise ValidationError(error_msg)
    
    return True


if __name__ == "__main__":
    # Test with valid example
    valid_tool = {
        "name": "calculate_distance",
        "description": "Calculates the distance between two geographic coordinates using the Haversine formula. Returns the distance in kilometers or miles.",
        "parameters": {
            "type": "object",
            "properties": {
                "lat1": {"type": "number", "description": "Latitude of first location"},
                "lon1": {"type": "number", "description": "Longitude of first location"}
            },
            "required": ["lat1", "lon1"]
        }
    }
    
    # Test with invalid examples
    invalid_tools = [
        {"name": "Tool", "description": "A tool", "parameters": {}},
        {"name": "calculate-distance", "description": "Calculates distance between coordinates", "parameters": {"type": "object"}},
        {"name": "calc", "description": "Short", "parameters": {"type": "object", "properties": {}}}
    ]
    
    print("Testing valid tool definition:")
    errors = validate_tool_definition(valid_tool)
    print(f"  Valid: {len(errors) == 0}\n")
    
    print("Testing invalid tool definitions:")
    for i, tool in enumerate(invalid_tools, 1):
        errors = validate_tool_definition(tool)
        print(f"  Test {i}: {len(errors)} errors found")
        for error in errors:
            print(f"    - {error}")
        print()
