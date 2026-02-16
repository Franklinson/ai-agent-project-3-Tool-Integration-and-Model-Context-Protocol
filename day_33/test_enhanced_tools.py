"""Test enhanced tools with error scenarios."""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enhanced_tools.tool_discovery_enhanced import ToolRegistry
from enhanced_tools.schema_validator_enhanced import SchemaValidator


def test_tool_discovery_errors():
    """Test tool discovery error scenarios."""
    print("=" * 60)
    print("Testing Tool Discovery Error Handling")
    print("=" * 60)
    
    # Test 1: File not found
    print("\n1. Test: Registry file not found")
    try:
        registry = ToolRegistry("nonexistent.json")
        print("❌ Should have raised error")
    except Exception as e:
        print("✓ Correctly raised error for missing file")
    
    # Test 2: Empty search query
    print("\n2. Test: Empty search query")
    registry_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'day_31', 'tool_metadata', 'tool_registry.json'
    ))
    registry = ToolRegistry(registry_path)
    result = registry.search_tools("")
    if "error" in result:
        print(f"✓ Error response: {result['error']['message']}")
    else:
        print("❌ Should return error for empty query")
    
    # Test 3: Query too long
    print("\n3. Test: Query too long")
    long_query = "a" * 101
    result = registry.search_tools(long_query)
    if "error" in result:
        print(f"✓ Error response: {result['error']['message']}")
    else:
        print("❌ Should return error for long query")
    
    # Test 4: Valid search
    print("\n4. Test: Valid search")
    result = registry.search_tools("email")
    if result.get("success"):
        print(f"✓ Found {result['count']} tools")
    else:
        print(f"❌ Search failed: {result}")
    
    # Test 5: Tool not found
    print("\n5. Test: Tool not found")
    result = registry.get_tool_metadata("nonexistent_tool")
    if "error" in result:
        print(f"✓ Error response: {result['error']['message']}")
    else:
        print("❌ Should return error for nonexistent tool")
    
    # Test 6: Valid tool metadata
    print("\n6. Test: Valid tool metadata")
    result = registry.get_tool_metadata("query_database")
    if result.get("success"):
        print(f"✓ Found tool: {result['tool']['name']}")
    else:
        print(f"❌ Failed to get metadata: {result}")
    
    # Test 7: Empty tool name
    print("\n7. Test: Empty tool name")
    result = registry.get_tool_metadata("")
    if "error" in result:
        print(f"✓ Error response: {result['error']['message']}")
    else:
        print("❌ Should return error for empty name")


def test_schema_validator_errors():
    """Test schema validator error scenarios."""
    print("\n" + "=" * 60)
    print("Testing Schema Validator Error Handling")
    print("=" * 60)
    
    validator = SchemaValidator()
    
    # Test 1: Schema file not found
    print("\n1. Test: Schema file not found")
    result = validator.validate_input({"test": "data"}, "nonexistent_schema")
    if "error" in result:
        print(f"✓ Error response: {result['error']['message']}")
    else:
        print("❌ Should return error for missing schema")
    
    # Test 2: Empty input data
    print("\n2. Test: Empty input data")
    result = validator.validate_input({}, "test_schema")
    if "error" in result:
        print(f"✓ Error response: {result['error']['message']}")
    else:
        print("❌ Should return error for empty data")
    
    # Test 3: Invalid data type
    print("\n3. Test: Invalid data type (not dict)")
    result = validator.validate_input("not a dict", "test_schema")
    if "error" in result:
        print(f"✓ Error response: {result['error']['message']}")
    else:
        print("❌ Should return error for invalid type")
    
    # Test 4: Create test schema and validate
    print("\n4. Test: Valid schema validation")
    
    # Create test schema directory
    test_schema_dir = os.path.join(validator.schema_base_path, 'input_schemas')
    os.makedirs(test_schema_dir, exist_ok=True)
    
    test_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "minLength": 1, "maxLength": 50},
            "age": {"type": "integer", "minimum": 0, "maximum": 150}
        },
        "required": ["name", "age"]
    }
    
    schema_path = os.path.join(test_schema_dir, 'test_user.json')
    with open(schema_path, 'w') as f:
        json.dump(test_schema, f)
    
    # Valid data
    valid_data = {"name": "John", "age": 30}
    result = validator.validate_input(valid_data, "test_user")
    if result.get("success"):
        print(f"✓ Validation passed for valid data")
    else:
        print(f"❌ Should pass validation: {result}")
    
    # Test 5: Missing required field
    print("\n5. Test: Missing required field")
    invalid_data = {"name": "John"}
    result = validator.validate_input(invalid_data, "test_user")
    if "error" in result:
        print(f"✓ Error response: {result['error']['message']}")
    else:
        print("❌ Should return error for missing field")
    
    # Test 6: Invalid type
    print("\n6. Test: Invalid field type")
    invalid_data = {"name": "John", "age": "thirty"}
    result = validator.validate_input(invalid_data, "test_user")
    if "error" in result:
        print(f"✓ Error response: {result['error']['message']}")
    else:
        print("❌ Should return error for invalid type")
    
    # Test 7: Constraint violation
    print("\n7. Test: Constraint violation (age too large)")
    invalid_data = {"name": "John", "age": 200}
    result = validator.validate_input(invalid_data, "test_user")
    if "error" in result:
        print(f"✓ Error response: {result['error']['message']}")
    else:
        print("❌ Should return error for constraint violation")
    
    # Cleanup
    if os.path.exists(schema_path):
        os.remove(schema_path)


def test_error_response_structure():
    """Test error response structure."""
    print("\n" + "=" * 60)
    print("Testing Error Response Structure")
    print("=" * 60)
    
    registry_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'day_31', 'tool_metadata', 'tool_registry.json'
    ))
    registry = ToolRegistry(registry_path)
    
    # Get an error response
    result = registry.search_tools("")
    
    if "error" in result:
        error = result["error"]
        print("\nError Response Structure:")
        print(f"  Code: {error.get('code')}")
        print(f"  Message: {error.get('message')}")
        print(f"  Status: {error.get('status')}")
        print(f"  Timestamp: {error.get('timestamp')}")
        print(f"  Details: {error.get('details')}")
        
        # Validate structure
        required_fields = ["code", "message", "status", "timestamp"]
        if all(field in error for field in required_fields):
            print("\n✓ Error response has all required fields")
        else:
            print("\n❌ Error response missing required fields")
    else:
        print("❌ No error response generated")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Enhanced Tools Error Handling Tests")
    print("=" * 60)
    
    test_tool_discovery_errors()
    test_schema_validator_errors()
    test_error_response_structure()
    
    print("\n" + "=" * 60)
    print("All error handling tests completed! ✓")
    print("=" * 60)
