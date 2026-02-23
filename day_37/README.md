# Day 37: Database Query Tool with Connection Pooling

A complete, production-ready database query tool with connection pooling, secure query execution, and comprehensive error handling.

## Project Structure

```
day_37/
├── connection_pool.py          # Connection pool manager
├── query_executor.py           # Secure query executor
├── database_tool.py            # Complete database tool
├── integration_example.py      # Basic integration example
├── comprehensive_demo.py       # Full feature demonstration
├── test_database_tool.py       # Comprehensive test suite
├── CONNECTION_POOL_README.md   # Connection pool documentation
├── QUERY_EXECUTOR_README.md    # Query executor documentation
└── DATABASE_TOOL_README.md     # Database tool documentation
```

## Components

### 1. Connection Pool (`connection_pool.py`)

Manages a pool of database connections for efficient resource usage.

**Features:**
- Configurable pool size
- Thread-safe operations
- Automatic connection health checks
- Context manager support
- Connection timeout handling

**Usage:**
```python
from connection_pool import ConnectionPool, PooledConnection

with ConnectionPool({"database": "mydb.db"}, pool_size=5) as pool:
    with PooledConnection(pool) as conn:
        cursor = conn.execute("SELECT * FROM users")
        results = cursor.fetchall()
```

### 2. Query Executor (`query_executor.py`)

Executes queries securely with parameterization and validation.

**Features:**
- Parameterized query execution
- SQL injection prevention
- Read-only mode support
- Query validation
- Result formatting as dictionaries

**Usage:**
```python
from query_executor import QueryExecutor

executor = QueryExecutor(connection, read_only=True)
results = executor.execute_query(
    "SELECT * FROM users WHERE age > ?",
    (25,)
)
```

### 3. Database Tool (`database_tool.py`)

Complete tool integrating connection pooling and secure execution.

**Features:**
- Integrated connection pooling
- Secure query execution
- Schema validation
- Performance tracking
- Comprehensive error handling

**Usage:**
```python
from database_tool import DatabaseTool

with DatabaseTool(pool_size=5) as tool:
    result = tool.execute(
        query="SELECT * FROM users WHERE city = ?",
        params=["New York"],
        database="mydb.db"
    )
    
    print(f"Found {result['row_count']} users")
    for row in result['rows']:
        print(row)
```

## Quick Start

### Installation

No external dependencies required - uses Python's built-in `sqlite3` module.

### Basic Example

```python
from database_tool import DatabaseTool

# Create tool with connection pool
with DatabaseTool(pool_size=5) as tool:
    # Execute safe parameterized query
    result = tool.execute(
        query="SELECT * FROM products WHERE price < ?",
        params=[100],
        database="store.db"
    )
    
    # Access results
    print(f"Columns: {result['columns']}")
    print(f"Rows: {result['row_count']}")
    print(f"Time: {result['execution_time_ms']}ms")
    
    for product in result['rows']:
        print(f"{product['name']}: ${product['price']}")
```

## Key Features

### 1. Security

- **SQL Injection Prevention**: Blocks dangerous patterns and enforces parameterization
- **Read-Only Mode**: Restricts to SELECT queries by default
- **Query Validation**: Validates queries before execution

### 2. Performance

- **Connection Pooling**: Reuses connections efficiently
- **Configurable Pool Size**: Adjust based on workload
- **Performance Tracking**: Measures execution time

### 3. Reliability

- **Error Handling**: Comprehensive error messages
- **Connection Health Checks**: Automatically replaces dead connections
- **Resource Cleanup**: Proper cleanup with context managers

### 4. Usability

- **Simple API**: Easy-to-use interface
- **Flexible Parameters**: Supports positional and named parameters
- **Structured Output**: Returns data as dictionaries

## API Reference

### DatabaseTool

**Constructor:**
```python
DatabaseTool(pool_size=5)
```

**Methods:**

- `execute(**kwargs)` - Execute a query
  - `query` (str, required): SQL query with placeholders
  - `params` (list, optional): Query parameters
  - `database` (str, optional): Database file path
  - `read_only` (bool, optional): Execute in read-only mode (default: True)
  - Returns: Dict with `columns`, `rows`, `row_count`, `execution_time_ms`

- `cleanup()` - Close all connection pools

### Input Schema

```python
{
    "query": str,           # Required: SQL query
    "params": list,         # Optional: Query parameters
    "database": str,        # Optional: Database path (default: ":memory:")
    "read_only": bool       # Optional: Read-only mode (default: True)
}
```

### Output Schema

```python
{
    "columns": [str],       # Column names
    "rows": [dict],         # Result rows as dictionaries
    "row_count": int,       # Number of rows
    "execution_time_ms": float  # Execution time in milliseconds
}
```

## Examples

### Simple Query
```python
result = tool.execute(
    query="SELECT * FROM users",
    database="mydb.db"
)
```

### Parameterized Query
```python
result = tool.execute(
    query="SELECT * FROM users WHERE age > ? AND city = ?",
    params=[25, "New York"],
    database="mydb.db"
)
```

### JOIN Query
```python
result = tool.execute(
    query="""
        SELECT u.name, o.total
        FROM users u
        JOIN orders o ON u.id = o.user_id
        WHERE o.date > ?
    """,
    params=["2024-01-01"],
    database="mydb.db"
)
```

### Write Operation
```python
result = tool.execute(
    query="UPDATE products SET price = ? WHERE id = ?",
    params=[99.99, 123],
    database="mydb.db",
    read_only=False  # Required for writes
)
```

## Testing

Run the comprehensive test suite:

```bash
python3 -m unittest test_database_tool.py -v
```

**Test Coverage:**
- ✓ Simple SELECT queries
- ✓ Parameterized queries
- ✓ JOIN and aggregate queries
- ✓ Empty results
- ✓ Read-only mode enforcement
- ✓ Write operations
- ✓ SQL injection prevention
- ✓ Invalid query handling
- ✓ Connection pooling
- ✓ Context manager usage

## Demonstrations

### Run Basic Integration Example
```bash
python3 integration_example.py
```

### Run Comprehensive Demo
```bash
python3 comprehensive_demo.py
```

The comprehensive demo showcases:
- Basic queries
- Advanced queries (JOINs, aggregates, subqueries)
- Write operations
- Security features
- Performance metrics

## Integration with Day 32

Compatible with Day 32 schema validation:

```python
import sys
sys.path.append('../day_32')
from validators.schema_validator import SchemaValidator

validator = SchemaValidator()

# Validate input
input_data = {"query": "SELECT * FROM users", "database": "users_db"}
is_valid, error = validator.validate_input(input_data, "database_query_input")

# Validate output
output_data = {
    "columns": ["id", "name"],
    "rows": [{"id": 1, "name": "Alice"}],
    "row_count": 1,
    "execution_time_ms": 1.5
}
is_valid, error = validator.validate_output(output_data, "database_query_output")
```

## Best Practices

1. **Always use parameterized queries**
   ```python
   # ✅ Good
   tool.execute(query="SELECT * FROM users WHERE id = ?", params=[user_id])
   
   # ❌ Bad - vulnerable to SQL injection
   tool.execute(query=f"SELECT * FROM users WHERE id = {user_id}")
   ```

2. **Use read-only mode by default**
   ```python
   # Safe for production
   tool.execute(query="SELECT * FROM users", database="prod.db")
   ```

3. **Use context managers**
   ```python
   with DatabaseTool() as tool:
       result = tool.execute(query="SELECT * FROM users")
   # Automatic cleanup
   ```

4. **Handle errors appropriately**
   ```python
   try:
       result = tool.execute(query=query, params=params)
   except ValueError as e:
       # Validation error
       log_error(f"Invalid input: {e}")
   except Exception as e:
       # Execution error
       log_error(f"Query failed: {e}")
   ```

## Performance Tips

- Adjust pool size based on concurrent query load
- Use connection pooling for multiple queries
- Monitor execution times for optimization
- Use indexes on frequently queried columns

## Security Considerations

- Never concatenate user input into queries
- Always use parameterized queries
- Use read-only mode for untrusted queries
- Validate and sanitize all inputs
- Monitor for suspicious query patterns

## License

This is a demonstration project for educational purposes.

## Summary

Day 37 delivers a complete, production-ready database query tool that combines:
- Efficient connection pooling
- Secure query execution
- Comprehensive error handling
- Performance tracking
- Easy-to-use API

Perfect for building database-backed applications with security and performance in mind.
