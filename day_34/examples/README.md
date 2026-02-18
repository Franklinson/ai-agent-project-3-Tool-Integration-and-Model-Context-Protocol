# Tool Usage Examples

Comprehensive usage examples for tool integration, covering common scenarios, advanced use cases, edge cases, and error handling.

## Overview

This directory contains detailed examples for 3 tools:
- **send_email** - Email sending tool with SMTP support
- **query_database** - Database query tool for read-only SQL operations
- **web_search** - Web search tool using search engine APIs

## Example Structure

Each tool example file includes:

### 1. Common Use Cases (3-5 examples)
Basic, everyday scenarios that represent typical tool usage:
- Simple operations with minimal parameters
- Standard workflows
- Most frequent use patterns

### 2. Advanced Use Cases (1-2 examples)
Complex scenarios demonstrating full tool capabilities:
- Multiple parameters and options
- Complex data structures
- Integration patterns

### 3. Edge Cases (1-2 examples)
Boundary conditions and unusual but valid scenarios:
- Maximum/minimum parameter values
- Empty results
- Limit testing

### 4. Error Cases (1-2 examples)
Invalid inputs and failure scenarios:
- Validation errors
- Connection failures
- Rate limiting
- Permission issues

## Example Format

Each example includes:
```json
{
  "name": "Example name",
  "description": "What this example demonstrates",
  "input": {
    "parameter1": "value1",
    "parameter2": "value2"
  },
  "output": {
    "result": "expected output"
  }
}
```

## Tool Examples

### send_email
**File:** `email_tool_examples.json`

Examples cover:
- Plain text and HTML emails
- Single and multiple recipients
- CC and BCC functionality
- Priority levels
- Rate limiting
- Validation errors

### query_database
**File:** `database_query_examples.json`

Examples cover:
- Simple SELECT queries
- JOINs and aggregations
- Parameterized queries
- Timeout handling
- Result set limits
- Security validation

### web_search
**File:** `web_search_examples.json`

Examples cover:
- Basic search queries
- Result count customization
- Language-specific searches
- Empty results
- Rate limiting
- Query validation

## Usage

These examples serve as:
1. **Documentation** - Understanding tool capabilities
2. **Testing** - Validating tool implementations
3. **Integration Guide** - Reference for developers
4. **Troubleshooting** - Common error patterns and solutions

## Notes

- All examples use realistic data and scenarios
- Error cases include proper error codes and messages
- Examples are organized by complexity
- Each example is self-contained and runnable
