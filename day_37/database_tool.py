"""Complete database query tool with connection pooling and secure execution."""

import time
from typing import Any, Dict, List, Optional
from connection_pool import ConnectionPool, PooledConnection
from query_executor import QueryExecutor


class DatabaseTool:
    """Database query tool with connection pooling and secure execution."""
    
    # Tool metadata
    NAME = "database_query"
    DESCRIPTION = "Execute SQL queries with connection pooling and security"
    
    # Input schema
    INPUT_SCHEMA = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SQL query to execute",
                "minLength": 1
            },
            "params": {
                "type": "array",
                "description": "Query parameters for parameterized queries",
                "items": {"type": ["string", "number", "boolean", "null"]},
                "default": []
            },
            "database": {
                "type": "string",
                "description": "Database file path",
                "default": ":memory:"
            },
            "read_only": {
                "type": "boolean",
                "description": "Execute in read-only mode (SELECT only)",
                "default": True
            }
        },
        "required": ["query"]
    }
    
    # Output schema
    OUTPUT_SCHEMA = {
        "type": "object",
        "properties": {
            "columns": {
                "type": "array",
                "description": "Column names",
                "items": {"type": "string"}
            },
            "rows": {
                "type": "array",
                "description": "Query result rows as objects",
                "items": {"type": "object"}
            },
            "row_count": {
                "type": "integer",
                "description": "Number of rows returned",
                "minimum": 0
            },
            "execution_time_ms": {
                "type": "number",
                "description": "Query execution time in milliseconds",
                "minimum": 0
            }
        },
        "required": ["columns", "rows", "row_count", "execution_time_ms"]
    }
    
    def __init__(self, pool_size: int = 5, allowed_tables: Optional[List[str]] = None):
        """Initialize database tool with connection pool.
        
        Args:
            pool_size: Size of connection pool
            allowed_tables: Optional whitelist of allowed table names
        """
        self.pool_size = pool_size
        self.allowed_tables = allowed_tables
        self._pools: Dict[str, ConnectionPool] = {}
    
    def _get_pool(self, database: str) -> ConnectionPool:
        """Get or create connection pool for database."""
        if database not in self._pools:
            config = {"database": database}
            self._pools[database] = ConnectionPool(config, self.pool_size)
        return self._pools[database]
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute database query tool.
        
        Args:
            query: SQL query string
            params: Optional list of parameters
            database: Database file path (default: :memory:)
            read_only: Execute in read-only mode (default: True)
            
        Returns:
            Dictionary with columns, rows, row_count, and execution_time_ms
            
        Raises:
            ValueError: If input validation fails
            Exception: If query execution fails
        """
        # Extract and validate inputs
        query = kwargs.get("query")
        if not query:
            raise ValueError("Query is required")
        
        params = kwargs.get("params", [])
        database = kwargs.get("database", ":memory:")
        read_only = kwargs.get("read_only", True)
        
        # Convert params list to tuple for sqlite
        params_tuple = tuple(params) if params else None
        
        # Get connection pool
        pool = self._get_pool(database)
        
        # Execute query with timing
        start_time = time.time()
        
        try:
            with PooledConnection(pool) as conn:
                executor = QueryExecutor(conn, read_only=read_only, allowed_tables=self.allowed_tables)
                results = executor.execute_query(query, params_tuple)
                
                # Commit if not read-only
                if not read_only:
                    conn.commit()
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Extract columns from results
            columns = list(results[0].keys()) if results else []
            
            # Format output
            return {
                "columns": columns,
                "rows": results,
                "row_count": len(results),
                "execution_time_ms": round(execution_time_ms, 2)
            }
        
        except Exception as e:
            raise Exception(f"Query execution failed: {e}")
    
    def cleanup(self):
        """Cleanup all connection pools."""
        for pool in self._pools.values():
            pool.cleanup()
        self._pools.clear()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


# Example usage
if __name__ == "__main__":
    import sqlite3
    
    # Setup test database
    conn = sqlite3.connect("test_db.db")
    conn.execute("DROP TABLE IF EXISTS employees")
    conn.execute("""
        CREATE TABLE employees (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            salary REAL
        )
    """)
    conn.execute("INSERT INTO employees VALUES (1, 'Alice', 'Engineering', 95000)")
    conn.execute("INSERT INTO employees VALUES (2, 'Bob', 'Sales', 75000)")
    conn.execute("INSERT INTO employees VALUES (3, 'Charlie', 'Engineering', 85000)")
    conn.execute("INSERT INTO employees VALUES (4, 'Diana', 'HR', 70000)")
    conn.commit()
    conn.close()
    
    # Use database tool
    with DatabaseTool(pool_size=3) as tool:
        # Query with parameters
        result = tool.execute(
            query="SELECT * FROM employees WHERE department = ?",
            params=["Engineering"],
            database="test_db.db",
            read_only=True
        )
        
        print("Query Results:")
        print(f"Columns: {result['columns']}")
        print(f"Row count: {result['row_count']}")
        print(f"Execution time: {result['execution_time_ms']}ms")
        print("\nRows:")
        for row in result['rows']:
            print(f"  {row}")
        
        # Query with salary filter
        result = tool.execute(
            query="SELECT name, salary FROM employees WHERE salary > ?",
            params=[80000],
            database="test_db.db"
        )
        
        print(f"\nEmployees with salary > 80000:")
        for row in result['rows']:
            print(f"  {row['name']}: ${row['salary']}")
        
        # Test read-only enforcement
        try:
            tool.execute(
                query="DELETE FROM employees WHERE id = 1",
                database="test_db.db",
                read_only=True
            )
        except Exception as e:
            print(f"\nRead-only protection: {e}")
    
    # Cleanup
    import os
    os.remove("test_db.db")
