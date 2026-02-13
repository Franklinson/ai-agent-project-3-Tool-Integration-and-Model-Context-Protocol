# Day 31: Tool Integration and Model Context Protocol

A comprehensive framework for defining, validating, cataloging, and using tools with proper structure, naming conventions, metadata, and discovery capabilities.

## 📋 Overview

This project provides a complete tool management system including:

- **Tool Definition Framework** - Structured format with validation
- **Tool Metadata System** - Categorization, tagging, and versioning
- **Discovery API** - Search and filter tools by various criteria
- **Comprehensive Documentation** - Usage examples and best practices

## 🗂️ Project Structure

```
day_31/
├── tool_definitions/          # Tool definitions and validation
│   ├── tool_validator.py      # Validation module
│   ├── tool_template.json     # Template structure
│   ├── web_search_tool.json   # Web search tool
│   ├── database_query_tool.json  # Database query tool
│   ├── email_tool.json        # Email sending tool
│   └── README.md              # Definition framework docs
│
├── tool_metadata/             # Tool registry and discovery
│   ├── tool_registry.json     # Central tool catalog
│   ├── tool_discovery.py      # Discovery API
│   ├── demo_discovery.py      # Interactive demo
│   ├── test_discovery.py      # Test suite
│   └── README.md              # Metadata system docs
│
├── examples/                  # Usage examples
│   └── tool_usage_examples.md # Comprehensive examples
│
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Validate a Tool Definition

```python
from tool_definitions.tool_validator import validate_tool_definition

tool_def = {
    "name": "my_tool",
    "description": "A detailed description of at least 50 characters explaining what this tool does.",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param1"]
    }
}

errors = validate_tool_definition(tool_def)
if not errors:
    print("✓ Tool definition is valid!")
```

### 2. Discover Tools

```python
from tool_metadata.tool_discovery import ToolRegistry

registry = ToolRegistry()

# Find tools by category
search_tools = registry.list_tools_by_category("search")

# Filter by capability
readonly_tools = registry.filter_tools_by_tag("read-only")

# Search by name or description
email_tools = registry.search_tools("email")

# Get specific tool metadata
metadata = registry.get_tool_metadata("query_database")
print(f"Version: {metadata['version']}")
print(f"Tags: {metadata['tags']}")
```

### 3. Use Tools

See [examples/tool_usage_examples.md](examples/tool_usage_examples.md) for comprehensive usage examples.

## 🛠️ Available Tools

### web_search (v1.0.0)
**Category**: search  
**Status**: active  
**Tags**: rate-limited, external-api, requires-auth, web

Performs web searches using search engine API with configurable result limits and language support.

**Key Features**:
- Query validation (1-500 characters)
- Configurable result limits (1-20)
- Multi-language support
- Rate limiting protection

**Use Cases**: Finding current information, documentation lookup, research

---

### query_database (v1.0.0)
**Category**: database  
**Status**: active  
**Tags**: read-only, requires-auth, sql, data-access

Executes read-only SQL SELECT queries against databases with parameterization to prevent SQL injection.

**Key Features**:
- SQL injection prevention via parameterized queries
- Multiple database support
- Configurable timeouts (1-30 seconds)
- Result set size limits (max_rows)
- Connection pooling

**Use Cases**: Data retrieval, analytics, reporting

**Security**: Only SELECT statements allowed; all queries use prepared statements

---

### send_email (v1.0.0)
**Category**: communication  
**Status**: active  
**Tags**: rate-limited, requires-auth, smtp, notification

Sends email messages with validation, delivery tracking, and support for HTML/plain text formats.

**Key Features**:
- RFC 5322 email validation
- HTML and plain text support
- CC/BCC support
- Priority levels (low, normal, high)
- Rate limiting (100/hour)
- Bounce tracking

**Use Cases**: Notifications, alerts, reports, automated communications

**Limits**: 50 recipients max, 25MB message size

## 📚 Documentation

### Core Documentation
- [Tool Definitions README](tool_definitions/README.md) - Definition framework and validation
- [Tool Metadata README](tool_metadata/README.md) - Metadata system and discovery
- [Tool Usage Examples](examples/tool_usage_examples.md) - Comprehensive usage examples

### Quick References
- [Tool Metadata Quick Reference](tool_metadata/QUICK_REFERENCE.md) - Common operations
- [Tool Metadata Summary](tool_metadata/SUMMARY.md) - System overview

## 🎯 Tool Definition Framework

### Validation Rules

**Name Requirements**:
- Must be in `snake_case` format
- Must be descriptive (not generic like "tool", "function")
- Minimum 3 characters

**Description Requirements**:
- Must be at least 50 characters
- Should clearly explain purpose and behavior

**Parameters Requirements**:
- Must follow JSON Schema format
- Must have `type: "object"`
- Each property must have `type` and `description`
- Required fields must be marked in `required` array

### Tool Definition Template

```json
{
  "name": "tool_name_in_snake_case",
  "description": "Detailed description of at least 50 characters...",
  "parameters": {
    "type": "object",
    "properties": {
      "param_name": {
        "type": "string",
        "description": "Parameter description"
      }
    },
    "required": ["param_name"]
  },
  "returns": {
    "type": "object",
    "description": "Return value description"
  }
}
```

## 🔍 Discovery System

### Categories
- **search** - Tools for searching and retrieving information
- **database** - Tools for querying and managing databases
- **communication** - Tools for sending messages and notifications

### Tags
- `read-only` - Tool only reads data, does not modify
- `rate-limited` - Tool has usage rate limits
- `requires-auth` - Tool requires authentication credentials
- `external-api` - Tool calls external APIs
- `sql` - Tool executes SQL queries
- `smtp` - Tool uses SMTP protocol
- `web` - Tool interacts with web services
- `data-access` - Tool accesses data sources
- `notification` - Tool sends notifications

### Status Values
- **active** - Production-ready and actively maintained
- **deprecated** - Being phased out, use alternatives
- **experimental** - In testing phase, may have breaking changes

## 🧪 Testing

### Run Tool Validator Tests
```bash
cd tool_definitions
python3 tool_validator.py
```

### Run Discovery System Tests
```bash
cd tool_metadata
python3 test_discovery.py
```

### Run Interactive Demo
```bash
cd tool_metadata
python3 demo_discovery.py
```

## 📖 Usage Examples

### Basic Tool Usage

```python
# Web Search
result = web_search(
    query="Python asyncio tutorial",
    num_results=5
)

# Database Query
result = query_database(
    query="SELECT * FROM users WHERE active = ?",
    database="production",
    parameters=[True]
)

# Send Email
result = send_email(
    to=["user@example.com"],
    subject="Welcome",
    body="Thank you for signing up!"
)
```

For comprehensive examples including advanced usage, error handling, and best practices, see [examples/tool_usage_examples.md](examples/tool_usage_examples.md).

## 🎓 Best Practices

### Tool Definition
1. Use descriptive, snake_case names
2. Write comprehensive descriptions (4-6 sentences)
3. Document all parameters with types and constraints
4. Include usage examples in definitions
5. Document error scenarios

### Tool Usage
1. Always validate input before calling tools
2. Implement proper error handling with retries
3. Respect rate limits and add throttling
4. Use parameterized queries for database operations
5. Log tool calls for monitoring
6. Test with mock data in development

### Security
1. Never concatenate user input into SQL queries
2. Validate all email addresses before sending
3. Use authentication for all tools
4. Implement rate limiting to prevent abuse
5. Monitor for suspicious activity

## 🔧 Adding New Tools

### Step 1: Create Tool Definition
```bash
cd tool_definitions
# Create your_tool.json following the template
```

### Step 2: Validate Definition
```python
from tool_validator import validate_tool_file

validate_tool_file("your_tool.json")
```

### Step 3: Add to Registry
Edit `tool_metadata/tool_registry.json` and add:
```json
{
  "name": "your_tool",
  "category": "appropriate_category",
  "tags": ["relevant", "tags"],
  "version": "1.0.0",
  "status": "active",
  "description": "Brief description",
  "definition_file": "../tool_definitions/your_tool.json",
  "author": "Your Name",
  "created": "YYYY-MM-DD",
  "dependencies": ["package1", "package2"]
}
```

### Step 4: Test Discovery
```python
from tool_discovery import ToolRegistry

registry = ToolRegistry()
metadata = registry.get_tool_metadata("your_tool")
print(metadata)
```

## 📊 Statistics

- **Total Tools**: 3
- **Categories**: 3
- **Tags**: 9
- **Active Tools**: 3
- **Test Coverage**: 100%

## 🤝 Contributing

When adding new tools:
1. Follow the tool definition template
2. Validate using tool_validator.py
3. Add complete metadata to registry
4. Include usage examples
5. Document error scenarios
6. Add tests

## 📝 License

This project is part of the AI Agent Project series focusing on Tool Integration and Model Context Protocol.

## 🔗 Related Resources

- [JSON Schema Documentation](https://json-schema.org/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Tool Integration Best Practices](examples/tool_usage_examples.md)

---

**Version**: 1.0.0  
**Last Updated**: 2024-01-15  
**Status**: Production Ready ✓
