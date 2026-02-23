"""Comprehensive tests for database tool with security and connection handling."""

import os
import sqlite3
import sys
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database_tool import DatabaseTool
from query_executor import QueryExecutor
from connection_pool import ConnectionPool


class TestDatabaseToolQueries(unittest.TestCase):
    """Test successful query execution."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test database."""
        cls.test_db = "test_queries.db"
        conn = sqlite3.connect(cls.test_db)
        conn.execute("CREATE TABLE users (id INTEGER, name TEXT, age INTEGER)")
        conn.executemany(
            "INSERT INTO users VALUES (?, ?, ?)",
            [(1, "Alice", 30), (2, "Bob", 25), (3, "Charlie", 35)]
        )
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
        self.assertIn('id', result['columns'])
        self.assertIn('name', result['columns'])
    
    def test_select_with_where(self):
        """Test SELECT with WHERE clause."""
        result = self.tool.execute(
            query="SELECT name FROM users WHERE age > 30",
            database=self.test_db
        )
        self.assertEqual(result['row_count'], 1)
        self.assertEqual(result['rows'][0]['name'], 'Charlie')
    
    def test_aggregate_query(self):
        """Test aggregate functions."""
        result = self.tool.execute(
            query="SELECT COUNT(*) as count, AVG(age) as avg_age FROM users",
            database=self.test_db
        )
        self.assertEqual(result['rows'][0]['count'], 3)
        self.assertEqual(result['rows'][0]['avg_age'], 30.0)
    
    def test_empty_result(self):
        """Test query returning no rows."""
        result = self.tool.execute(
            query="SELECT * FROM users WHERE age > 100",
            database=self.test_db
        )
        self.assertEqual(result['row_count'], 0)
        self.assertEqual(result['rows'], [])


class TestParameterizedQueries(unittest.TestCase):
    """Test parameterized query execution."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test database."""
        cls.test_db = "test_params.db"
        conn = sqlite3.connect(cls.test_db)
        conn.execute("CREATE TABLE products (id INTEGER, name TEXT, price REAL)")
        conn.executemany(
            "INSERT INTO products VALUES (?, ?, ?)",
            [(1, "Laptop", 999.99), (2, "Mouse", 29.99), (3, "Keyboard", 79.99)]
        )
        conn.commit()
        conn.close()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup test database."""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
    
    def setUp(self):
        """Setup tool for each test."""
        self.tool = DatabaseTool()
    
    def tearDown(self):
        """Cleanup tool after each test."""
        self.tool.cleanup()
    
    def test_single_parameter(self):
        """Test query with single parameter."""
        result = self.tool.execute(
            query="SELECT * FROM products WHERE id = ?",
            params=[1],
            database=self.test_db
        )
        self.assertEqual(result['row_count'], 1)
        self.assertEqual(result['rows'][0]['name'], 'Laptop')
    
    def test_multiple_parameters(self):
        """Test query with multiple parameters."""
        result = self.tool.execute(
            query="SELECT * FROM products WHERE price >= ? AND price <= ?",
            params=[50, 100],
            database=self.test_db
        )
        self.assertEqual(result['row_count'], 1)
        self.assertEqual(result['rows'][0]['name'], 'Keyboard')
    
    def test_string_parameter(self):
        """Test query with string parameter."""
        result = self.tool.execute(
            query="SELECT * FROM products WHERE name = ?",
            params=["Mouse"],
            database=self.test_db
        )
        self.assertEqual(result['row_count'], 1)
        self.assertEqual(result['rows'][0]['price'], 29.99)
    
    def test_parameter_prevents_injection(self):
        """Test that parameters prevent SQL injection."""
        malicious_input = "1 OR 1=1"
        result = self.tool.execute(
            query="SELECT * FROM products WHERE id = ?",
            params=[malicious_input],
            database=self.test_db
        )
        # Should return 0 rows since "1 OR 1=1" is treated as literal string
        self.assertEqual(result['row_count'], 0)


class TestSQLInjectionPrevention(unittest.TestCase):
    """Test SQL injection prevention mechanisms."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test database."""
        cls.test_db = "test_injection.db"
        conn = sqlite3.connect(cls.test_db)
        conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
        conn.execute("INSERT INTO users VALUES (1, 'Alice')")
        conn.commit()
        conn.close()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup test database."""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
    
    def setUp(self):
        """Setup tool for each test."""
        self.tool = DatabaseTool()
    
    def tearDown(self):
        """Cleanup tool after each test."""
        self.tool.cleanup()
    
    def test_block_multiple_statements(self):
        """Test blocking multiple SQL statements."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(
                query="SELECT * FROM users; DROP TABLE users;",
                database=self.test_db
            )
        self.assertIn("unsafe patterns", str(context.exception))
    
    def test_block_sql_comments(self):
        """Test blocking SQL comments."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(
                query="SELECT * FROM users -- comment",
                database=self.test_db
            )
        self.assertIn("unsafe patterns", str(context.exception))
    
    def test_block_block_comments(self):
        """Test blocking block comments."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(
                query="SELECT * FROM users /* comment */",
                database=self.test_db
            )
        self.assertIn("unsafe patterns", str(context.exception))
    
    def test_union_injection_attempt(self):
        """Test UNION-based injection attempt."""
        # This should be safe with parameterized queries
        result = self.tool.execute(
            query="SELECT * FROM users WHERE id = ?",
            params=["1 UNION SELECT * FROM passwords"],
            database=self.test_db
        )
        # Query executes but treats input as literal, returns 0 rows
        self.assertEqual(result['row_count'], 0)
    
    def test_read_only_blocks_insert(self):
        """Test read-only mode blocks INSERT."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(
                query="INSERT INTO users VALUES (1, 'hacker')",
                database=self.test_db,
                read_only=True
            )
        self.assertIn("not allowed in read-only mode", str(context.exception))
    
    def test_read_only_blocks_update(self):
        """Test read-only mode blocks UPDATE."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(
                query="UPDATE users SET name = 'hacker'",
                database=self.test_db,
                read_only=True
            )
        self.assertIn("not allowed in read-only mode", str(context.exception))
    
    def test_read_only_blocks_delete(self):
        """Test read-only mode blocks DELETE."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(
                query="DELETE FROM users",
                database=self.test_db,
                read_only=True
            )
        self.assertIn("not allowed in read-only mode", str(context.exception))
    
    def test_read_only_blocks_drop(self):
        """Test read-only mode blocks DROP."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(
                query="DROP TABLE users",
                database=self.test_db,
                read_only=True
            )
        self.assertIn("not allowed in read-only mode", str(context.exception))


class TestErrorHandling(unittest.TestCase):
    """Test error handling scenarios."""
    
    def setUp(self):
        """Setup tool for each test."""
        self.tool = DatabaseTool()
    
    def tearDown(self):
        """Cleanup tool after each test."""
        self.tool.cleanup()
    
    def test_missing_query(self):
        """Test error when query is missing."""
        with self.assertRaises(ValueError) as context:
            self.tool.execute(database=":memory:")
        self.assertIn("Query is required", str(context.exception))
    
    def test_empty_query(self):
        """Test error when query is empty."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(query="", database=":memory:")
        # Empty string is caught as "Query is required" by the tool
        self.assertTrue(
            "empty" in str(context.exception).lower() or 
            "required" in str(context.exception).lower()
        )
    
    def test_invalid_sql(self):
        """Test error handling for invalid SQL."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(
                query="INVALID SQL SYNTAX",
                database=":memory:"
            )
        self.assertIn("failed", str(context.exception).lower())
    
    def test_nonexistent_table(self):
        """Test error when querying nonexistent table."""
        with self.assertRaises(Exception) as context:
            self.tool.execute(
                query="SELECT * FROM nonexistent_table",
                database=":memory:"
            )
        self.assertIn("failed", str(context.exception).lower())
    
    def test_parameter_mismatch(self):
        """Test error when parameter count doesn't match."""
        with self.assertRaises(Exception):
            self.tool.execute(
                query="SELECT * FROM users WHERE id = ? AND name = ?",
                params=[1],  # Only 1 param, but query needs 2
                database=":memory:"
            )


class TestConnectionHandling(unittest.TestCase):
    """Test connection pool and handling."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test database."""
        cls.test_db = "test_connections.db"
        conn = sqlite3.connect(cls.test_db)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.execute("INSERT INTO test VALUES (1)")
        conn.commit()
        conn.close()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup test database."""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
    
    def test_connection_pool_reuse(self):
        """Test connection pool reuses connections."""
        tool = DatabaseTool(pool_size=2)
        
        # Execute multiple queries
        for i in range(10):
            result = tool.execute(
                query="SELECT * FROM test",
                database=self.test_db
            )
            self.assertEqual(result['row_count'], 1)
        
        tool.cleanup()
    
    def test_concurrent_queries(self):
        """Test handling concurrent queries."""
        tool = DatabaseTool(pool_size=3)
        
        results = []
        for i in range(5):
            result = tool.execute(
                query="SELECT * FROM test WHERE id = ?",
                params=[1],
                database=self.test_db
            )
            results.append(result)
        
        # All queries should succeed
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertEqual(result['row_count'], 1)
        
        tool.cleanup()
    
    def test_context_manager_cleanup(self):
        """Test context manager properly cleans up."""
        with DatabaseTool(pool_size=2) as tool:
            result = tool.execute(
                query="SELECT * FROM test",
                database=self.test_db
            )
            self.assertEqual(result['row_count'], 1)
        # Cleanup happens automatically
    
    def test_multiple_databases(self):
        """Test handling multiple databases."""
        # Create second database
        db2 = "test_db2.db"
        conn = sqlite3.connect(db2)
        conn.execute("CREATE TABLE other (value TEXT)")
        conn.execute("INSERT INTO other VALUES ('test')")
        conn.commit()
        conn.close()
        
        try:
            tool = DatabaseTool(pool_size=2)
            
            # Query first database
            result1 = tool.execute(
                query="SELECT * FROM test",
                database=self.test_db
            )
            
            # Query second database
            result2 = tool.execute(
                query="SELECT * FROM other",
                database=db2
            )
            
            self.assertEqual(result1['row_count'], 1)
            self.assertEqual(result2['row_count'], 1)
            
            tool.cleanup()
        finally:
            if os.path.exists(db2):
                os.remove(db2)


class TestQueryExecutorDirect(unittest.TestCase):
    """Test QueryExecutor directly."""
    
    def setUp(self):
        """Setup test database."""
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("CREATE TABLE data (id INTEGER, value TEXT)")
        self.conn.execute("INSERT INTO data VALUES (1, 'test')")
        self.conn.commit()
    
    def tearDown(self):
        """Cleanup connection."""
        self.conn.close()
    
    def test_executor_read_only(self):
        """Test executor in read-only mode."""
        executor = QueryExecutor(self.conn, read_only=True)
        results = executor.execute_query("SELECT * FROM data")
        self.assertEqual(len(results), 1)
    
    def test_executor_write_mode(self):
        """Test executor in write mode."""
        executor = QueryExecutor(self.conn, read_only=False)
        executor.execute_query("INSERT INTO data VALUES (?, ?)", (2, "test2"))
        self.conn.commit()
        
        results = executor.execute_query("SELECT * FROM data")
        self.assertEqual(len(results), 2)
    
    def test_executor_validation(self):
        """Test executor query validation."""
        executor = QueryExecutor(self.conn)
        
        with self.assertRaises(ValueError):
            executor.validate_query("")
        
        with self.assertRaises(ValueError):
            executor.validate_query("SELECT * FROM data; DROP TABLE data;")


class TestConnectionPoolDirect(unittest.TestCase):
    """Test ConnectionPool directly."""
    
    def test_pool_creation(self):
        """Test pool creates connections."""
        pool = ConnectionPool({"database": ":memory:"}, pool_size=3)
        self.assertIsNotNone(pool)
        pool.cleanup()
    
    def test_get_and_return_connection(self):
        """Test getting and returning connections."""
        pool = ConnectionPool({"database": ":memory:"}, pool_size=2)
        
        conn = pool.get_connection()
        self.assertIsNotNone(conn)
        
        pool.return_connection(conn)
        pool.cleanup()
    
    def test_pool_timeout(self):
        """Test pool timeout when exhausted."""
        pool = ConnectionPool({"database": ":memory:"}, pool_size=1)
        
        # Get the only connection
        conn1 = pool.get_connection()
        
        # Try to get another with short timeout
        with self.assertRaises(Exception):
            pool.get_connection(timeout=0.1)
        
        pool.return_connection(conn1)
        pool.cleanup()
    
    def test_pool_context_manager(self):
        """Test pool context manager."""
        with ConnectionPool({"database": ":memory:"}, pool_size=2) as pool:
            conn = pool.get_connection()
            self.assertIsNotNone(conn)
            pool.return_connection(conn)




class TestQueryWhitelisting(unittest.TestCase):
    """Test query whitelisting feature."""
    
    @classmethod
    def setUpClass(cls):
        """Setup test database."""
        cls.test_db = "test_whitelist.db"
        conn = sqlite3.connect(cls.test_db)
        conn.execute("CREATE TABLE allowed_table (id INTEGER, data TEXT)")
        conn.execute("CREATE TABLE forbidden_table (id INTEGER, secret TEXT)")
        conn.execute("INSERT INTO allowed_table VALUES (1, 'public')")
        conn.execute("INSERT INTO forbidden_table VALUES (1, 'secret')")
        conn.commit()
        conn.close()
    
    @classmethod
    def tearDownClass(cls):
        """Cleanup test database."""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
    
    def test_whitelist_allows_permitted_table(self):
        """Test whitelist allows queries to permitted tables."""
        tool = DatabaseTool(allowed_tables=["allowed_table"])
        
        result = tool.execute(
            query="SELECT * FROM allowed_table",
            database=self.test_db
        )
        
        self.assertEqual(result['row_count'], 1)
        tool.cleanup()
    
    def test_whitelist_blocks_forbidden_table(self):
        """Test whitelist blocks queries to non-whitelisted tables."""
        tool = DatabaseTool(allowed_tables=["allowed_table"])
        
        with self.assertRaises(Exception) as context:
            tool.execute(
                query="SELECT * FROM forbidden_table",
                database=self.test_db
            )
        
        self.assertIn("not in the allowed whitelist", str(context.exception))
        tool.cleanup()
    
    def test_whitelist_blocks_join_with_forbidden_table(self):
        """Test whitelist blocks JOIN with non-whitelisted tables."""
        tool = DatabaseTool(allowed_tables=["allowed_table"])
        
        with self.assertRaises(Exception) as context:
            tool.execute(
                query="SELECT * FROM allowed_table JOIN forbidden_table ON allowed_table.id = forbidden_table.id",
                database=self.test_db
            )
        
        self.assertIn("not in the allowed whitelist", str(context.exception))
        tool.cleanup()
    
    def test_whitelist_allows_multiple_tables(self):
        """Test whitelist with multiple allowed tables."""
        tool = DatabaseTool(allowed_tables=["allowed_table", "forbidden_table"])
        
        result = tool.execute(
            query="SELECT * FROM forbidden_table",
            database=self.test_db
        )
        
        self.assertEqual(result['row_count'], 1)
        tool.cleanup()
    
    def test_no_whitelist_allows_all_tables(self):
        """Test that without whitelist, all tables are accessible."""
        tool = DatabaseTool()  # No whitelist
        
        result1 = tool.execute(
            query="SELECT * FROM allowed_table",
            database=self.test_db
        )
        
        result2 = tool.execute(
            query="SELECT * FROM forbidden_table",
            database=self.test_db
        )
        
        self.assertEqual(result1['row_count'], 1)
        self.assertEqual(result2['row_count'], 1)
        tool.cleanup()
    
    def test_whitelist_case_insensitive(self):
        """Test whitelist is case-insensitive."""
        tool = DatabaseTool(allowed_tables=["ALLOWED_TABLE"])
        
        result = tool.execute(
            query="SELECT * FROM allowed_table",
            database=self.test_db
        )
        
        self.assertEqual(result['row_count'], 1)
        tool.cleanup()


# Update run_all_tests to include new test class
def run_all_tests():
    """Run all test suites."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseToolQueries))
    suite.addTests(loader.loadTestsFromTestCase(TestParameterizedQueries))
    suite.addTests(loader.loadTestsFromTestCase(TestSQLInjectionPrevention))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestQueryExecutorDirect))
    suite.addTests(loader.loadTestsFromTestCase(TestConnectionPoolDirect))
    suite.addTests(loader.loadTestsFromTestCase(TestQueryWhitelisting))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()



if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
