"""Secure query executor with parameterized queries and SQL injection prevention."""

import re
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union


class QueryExecutor:
    """Executes database queries securely with parameterization and validation."""

    # SQL keywords that modify data (not allowed in read-only mode)
    WRITE_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 
        'TRUNCATE', 'REPLACE', 'MERGE', 'GRANT', 'REVOKE'
    }

    def __init__(self, connection, read_only: bool = False, allowed_tables: Optional[List[str]] = None):
        """Initialize query executor.
        
        Args:
            connection: Database connection
            read_only: If True, only allow SELECT queries
            allowed_tables: Optional whitelist of allowed table names
        """
        self.connection = connection
        self.read_only = read_only
        self.allowed_tables = set(allowed_tables) if allowed_tables else None

    def validate_query(self, query: str) -> None:
        """Validate query for security and read-only constraints.
        
        Args:
            query: SQL query to validate
            
        Raises:
            ValueError: If query is invalid or violates constraints
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Check for SQL injection patterns
        if '--' in query or '/*' in query or ';' in query.rstrip(';'):
            raise ValueError("Query contains potentially unsafe patterns")
        
        # Check table whitelist if enabled
        if self.allowed_tables:
            self._validate_table_whitelist(query)
        
        # Check read-only constraint
        if self.read_only:
            query_upper = query.upper()
            for keyword in self.WRITE_KEYWORDS:
                if re.search(rf'\b{keyword}\b', query_upper):
                    raise ValueError(f"Write operation '{keyword}' not allowed in read-only mode")
    
    def _validate_table_whitelist(self, query: str) -> None:
        """Validate that query only accesses whitelisted tables.
        
        Args:
            query: SQL query to validate
            
        Raises:
            ValueError: If query accesses non-whitelisted tables
        """
        # Extract table names from query (simple pattern matching)
        query_upper = query.upper()
        
        # Pattern to find table names after FROM and JOIN
        patterns = [
            r'FROM\s+(\w+)',
            r'JOIN\s+(\w+)',
            r'INTO\s+(\w+)',
            r'UPDATE\s+(\w+)',
            r'TABLE\s+(\w+)'
        ]
        
        found_tables = set()
        for pattern in patterns:
            matches = re.findall(pattern, query_upper)
            found_tables.update(matches)
        
        # Check if all found tables are in whitelist
        for table in found_tables:
            if table.upper() not in {t.upper() for t in self.allowed_tables}:
                raise ValueError(f"Table '{table}' is not in the allowed whitelist")

    def execute_query(
        self, 
        query: str, 
        params: Optional[Union[Tuple, Dict]] = None
    ) -> List[Dict[str, Any]]:
        """Execute parameterized query and return formatted results.
        
        Args:
            query: SQL query with placeholders (? or :name)
            params: Query parameters (tuple or dict)
            
        Returns:
            List of dictionaries with column names as keys
            
        Raises:
            ValueError: If query validation fails
            sqlite3.Error: If query execution fails
        """
        self.validate_query(query)
        
        try:
            if params:
                cursor = self.connection.execute(query, params)
            else:
                cursor = self.connection.execute(query)
            
            return self.format_results(cursor)
        
        except sqlite3.Error as e:
            raise sqlite3.Error(f"Query execution failed: {e}")

    def format_results(self, cursor) -> List[Dict[str, Any]]:
        """Format cursor results as list of dictionaries.
        
        Args:
            cursor: Database cursor with results
            
        Returns:
            List of dictionaries with column names as keys
        """
        if not cursor.description:
            return []
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


# Example usage
if __name__ == "__main__":
    # Setup test database
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT, email TEXT)")
    conn.execute("INSERT INTO users VALUES (1, 'Alice', 'alice@example.com')")
    conn.execute("INSERT INTO users VALUES (2, 'Bob', 'bob@example.com')")
    conn.commit()
    
    # Test read-only executor
    executor = QueryExecutor(conn, read_only=True)
    
    # Safe parameterized query
    results = executor.execute_query(
        "SELECT * FROM users WHERE id = ?", 
        (1,)
    )
    print("Parameterized query:", results)
    
    # Test whitelisting
    whitelist_executor = QueryExecutor(conn, allowed_tables=["users"])
    results = whitelist_executor.execute_query("SELECT * FROM users")
    print("Whitelisted query:", results)
    
    # Test SQL injection prevention
    try:
        executor.execute_query("SELECT * FROM users; DROP TABLE users;")
    except ValueError as e:
        print(f"Blocked injection: {e}")
    
    conn.close()
