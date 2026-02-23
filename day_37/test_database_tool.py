"""Tests for database tool."""

import os
import sqlite3
import unittest
from database_tool import DatabaseTool


class TestDatabaseTool(unittest.TestCase):
    """Test cases for DatabaseTool."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test database."""
        cls.test_db = "test_database.db"
        conn = sqlite3.connect(cls.test_db)
        
        # Create test tables
        conn.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                email TEXT,
                age INTEGER
            )
        """)
        
        conn.execute("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                product TEXT,
                amount REAL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        
        # Insert test data
        users = [
            (1, "alice", "alice@example.com", 30),
            (2, "bob", "bob@example.com", 25),
            (3, "charlie", "charlie@example.com", 35)
        ]
        conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", users)
        
        orders = [
            (1, 1, "Laptop", 999.99),
            (2, 1, "Mouse", 29.99),
            (3, 2, "Keyboard", 79.99),
            (4, 3, "Monitor", 299.99)
        ]
        conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
        
        conn.commit()
        conn.close()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup test database."""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
    
    def setUp(self):
        """Setup tool for each test."""
        self.tool = DatabaseTool(pool_size=3)
    
    def tearDown(self):
        """Cleanup tool after each test."""
        self.tool.cleanup()
    
    def test_simple_select(self):
        """Test simple SELECT query."""
        result = self.tool.execute(
            query="SELECT * FROM users",
            database=self.test_db
        )
        
        self.assertEqual(result['row_count'], 3)
        self.assertEqual(result['columns'], ['id', 'username', 'email', 'age'])
        self.assertGreater(result['execution_time_ms'], 0)
    
    def test_parameterized_query(self):
        """Test parameterized query with positional parameters."""
        result = self.tool.execute(
            query="SELECT * FROM users WHERE age > ?",
            params=[30],
            database=self.test_db
        )
        
        self.assertEqual(result['row_count'], 1)
        self.assertEqual(result['rows'][0]['username'], 'charlie')
    
    def test_multiple_parameters(self):
        """Test query with multiple parameters."""
        result = self.tool.execute(
            query="SELECT * FROM users WHERE age >= ? AND age <= ?",
            params=[25, 30],
            database=self.test_db
        )
        
        self.assertEqual(result['row_count'], 2)
    
    def test_join_query(self):
        """Test JOIN query."""
        result = self.tool.execute(
            query="""
                SELECT u.username, o.product, o.amount
                FROM users u
                JOIN orders o ON u.id = o.user_id
                WHERE u.username = ?
            """,
            params=["alice"],
            database=self.test_db
        )
        
        self.assertEqual(result['row_count'], 2)
        self.assertEqual(result['columns'], ['username', 'product', 'amount'])
    
    def test_aggregate_query(self):
        """Test aggregate query."""
        result = self.tool.execute(
            query="SELECT COUNT(*) as count, SUM(amount) as total FROM orders",
            database=self.test_db
        )
        
        self.assertEqual(result['row_count'], 1)
        self.assertEqual(result['rows'][0]['count'], 4)
        self.assertAlmostEqual(result['rows'][0]['total'], 1409.96, places=2)
    
    def test_empty_result(self):
        """Test query with no results."""
        result = self.tool.execute(
            query="SELECT * FROM users WHERE age > ?",
            params=[100],
            database=self.test_db
        )
        
        self.assertEqual(result['row_count'], 0)
        self.assertEqual(result['rows'], [])
        self.assertEqual(result['columns'], [])
    
    def test_read_only_mode(self):
        """Test read-only mode blocks write operations."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(
                query="DELETE FROM users WHERE id = 1",
                database=self.test_db,
                read_only=True
            )
        
        self.assertIn("not allowed in read-only mode", str(context.exception))
    
    def test_write_mode(self):
        """Test write operations in non-read-only mode."""
        # Create temporary database for write test
        temp_db = "temp_write_test.db"
        conn = sqlite3.connect(temp_db)
        conn.execute("CREATE TABLE test (id INTEGER, value TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'original')")
        conn.commit()
        conn.close()
        
        try:
            # Update in write mode
            result = self.tool.execute(
                query="UPDATE test SET value = ? WHERE id = ?",
                params=["updated", 1],
                database=temp_db,
                read_only=False
            )
            
            # Verify update
            verify_result = self.tool.execute(
                query="SELECT value FROM test WHERE id = 1",
                database=temp_db
            )
            
            self.assertEqual(verify_result['rows'][0]['value'], 'updated')
        finally:
            self.tool.cleanup()
            if os.path.exists(temp_db):
                os.remove(temp_db)
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        with self.assertRaises(Exception):
            self.tool.execute(
                query="SELECT * FROM users; DROP TABLE users;",
                database=self.test_db
            )
    
    def test_invalid_query(self):
        """Test handling of invalid SQL."""
        with self.assertRaises(Exception):
            self.tool.execute(
                query="INVALID SQL QUERY",
                database=self.test_db
            )
    
    def test_missing_query(self):
        """Test error when query is missing."""
        with self.assertRaises(ValueError) as context:
            self.tool.execute(database=self.test_db)
        
        self.assertIn("Query is required", str(context.exception))
    
    def test_connection_pooling(self):
        """Test that connection pooling works."""
        # Execute multiple queries
        for i in range(10):
            result = self.tool.execute(
                query="SELECT * FROM users WHERE id = ?",
                params=[1],
                database=self.test_db
            )
            self.assertEqual(result['row_count'], 1)
    
    def test_context_manager(self):
        """Test context manager usage."""
        with DatabaseTool() as tool:
            result = tool.execute(
                query="SELECT * FROM users",
                database=self.test_db
            )
            self.assertEqual(result['row_count'], 3)


if __name__ == "__main__":
    unittest.main()
