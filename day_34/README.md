# Day 34: Tool Usage Examples and Validation

Comprehensive usage examples for tool integration with automated validation.

## Overview

This module provides:
1. **Comprehensive Examples** - Real-world usage examples for 3 tools
2. **Example Validator** - Automated validation of example completeness and correctness
3. **Test Suite** - Unit tests for validator functionality

## Structure

```
day_34/
├── examples/
│   ├── email_tool_examples.json
│   ├── database_query_examples.json
│   ├── web_search_examples.json
│   └── README.md
├── example_validator.py
├── test_example_validator.py
└── README.md
```

## Example Files

### Coverage
Each tool has examples for:
- **Common use cases** (4 examples) - Basic, everyday scenarios
- **Advanced use cases** (2 examples) - Complex scenarios with multiple parameters
- **Edge cases** (2 examples) - Boundary conditions and limits
- **Error cases** (4 examples) - Invalid inputs and failure scenarios

### Tools Covered
1. **send_email** - Email sending with SMTP
2. **query_database** - Database queries with SQL
3. **web_search** - Web search via API

## Example Validator

### Features

The `example_validator.py` validates:

1. **Structure Validation**
   - Required fields: name, description, input, output
   - Correct data types for each field
   - Complete example structure

2. **Input Validation**
   - Matches tool schema from day_31
   - Required parameters present
   - Correct data types
   - Value constraints (min/max, patterns, enums)
   - Skips validation for error cases (intentionally invalid)

3. **Output Validation**
   - Success cases have valid output
   - Error cases contain 'error' field
   - Appropriate structure for response type

### Usage

```bash
# Validate all example files
python3 day_34/example_validator.py

# Use in code
from example_validator import ExampleValidator

validator = ExampleValidator("day_31/tool_definitions")
is_valid, errors = validator.validate_examples_file("path/to/examples.json")

if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

### Validation Functions

```python
# Validate example structure
errors = validator.validate_example_structure(example, category)

# Validate input against tool schema
errors = validator.validate_example_input(tool_name, input_data, is_error_case)

# Validate output format
errors = validator.validate_example_output(output_data, is_error)

# Validate entire file
is_valid, errors = validator.validate_examples_file(file_path)
```

## Test Suite

Run tests with:
```bash
python3 day_34/test_example_validator.py
```

### Test Coverage
- Structure validation (valid and invalid)
- Input validation (types, ranges, required fields)
- Output validation (success and error cases)
- File validation (JSON parsing, missing fields)
- Tool-specific validation (email, database, web_search)

## Validation Results

All example files pass validation:
```
✓ email_tool_examples.json - Valid
✓ database_query_examples.json - Valid
✓ web_search_examples.json - Valid
```

## Key Features

1. **Schema-based Validation** - Uses tool definitions from day_31
2. **Clear Error Messages** - Specific error locations and descriptions
3. **Error Case Handling** - Skips input validation for intentionally invalid examples
4. **Type Checking** - Validates strings, integers, booleans, arrays
5. **Constraint Validation** - Checks min/max, patterns, enums
6. **Complete Coverage** - Tests all validation functions

## Integration

The validator integrates with:
- **day_31** - Tool definitions and schemas
- **day_32** - Schema validation patterns
- **day_33** - Error handling mechanisms

## Benefits

1. **Quality Assurance** - Ensures examples are correct and complete
2. **Documentation** - Examples serve as living documentation
3. **Testing** - Examples can be used for integration tests
4. **Consistency** - All examples follow the same format
5. **Maintainability** - Automated validation catches errors early
