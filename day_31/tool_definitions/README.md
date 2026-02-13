# Tool Definition Framework

A framework for defining tools with proper structure, naming conventions, and validation.

## Structure

```
tool_definitions/
├── tool_validator.py    # Validation module
├── tool_template.json   # Example tool definition
└── README.md           # This file
```

## Tool Definition Format

Tools must be defined as JSON objects with the following structure:

```json
{
  "name": "tool_name_in_snake_case",
  "description": "Detailed description of at least 50 characters...",
  "parameters": {
    "type": "object",
    "properties": {
      "param_name": {
        "type": "string|number|boolean|array|object",
        "description": "Parameter description"
      }
    },
    "required": ["param_name"]
  }
}
```

## Validation Rules

### Name Requirements
- Must be in `snake_case` format (lowercase letters, numbers, underscores)
- Must be descriptive (not generic like "tool", "function", "execute")
- Minimum 3 characters

### Description Requirements
- Must be at least 50 characters
- Should clearly explain the tool's purpose and behavior

### Parameters Requirements
- Must follow JSON Schema format
- Must have `type: "object"`
- Must include `properties` field
- Each property must have:
  - `type` field
  - `description` field
- `required` array must reference existing properties

## Usage

### Validate a Tool Definition

```python
from tool_validator import validate_tool_definition, validate_tool_file

# From dictionary
tool_def = {...}
errors = validate_tool_definition(tool_def)
if errors:
    for error in errors:
        print(f"Error: {error}")

# From file
try:
    validate_tool_file("my_tool.json")
    print("Tool definition is valid!")
except ValidationError as e:
    print(e)
```

### Run Tests

```bash
python3 tool_validator.py
```

## Example

See `tool_template.json` for a complete example of a valid tool definition.
