"""Integration example: Connection pool with secure query executor."""

from connection_pool import ConnectionPool, PooledConnection
from query_executor import QueryExecutor


def main():
    # Setup database with connection pool
    config = {"database": "test.db"}
    
    with ConnectionPool(config, pool_size=3) as pool:
        # Initialize database schema
        with PooledConnection(pool) as conn:
            conn.execute("DROP TABLE IF EXISTS products")
            conn.execute("CREATE TABLE products (id INTEGER, name TEXT, price REAL)")
            conn.execute("INSERT INTO products VALUES (1, 'Laptop', 999.99)")
            conn.execute("INSERT INTO products VALUES (2, 'Mouse', 29.99)")
            conn.execute("INSERT INTO products VALUES (3, 'Keyboard', 79.99)")
            conn.commit()
        
        # Execute safe queries with read-only executor
        with PooledConnection(pool) as conn:
            executor = QueryExecutor(conn, read_only=True)
            
            # Query with parameters
            results = executor.execute_query(
                "SELECT * FROM products WHERE price < ?",
                (100,)
            )
            print("Products under $100:")
            for product in results:
                print(f"  {product['name']}: ${product['price']}")
            
            # Named parameters
            results = executor.execute_query(
                "SELECT * FROM products WHERE name LIKE :pattern",
                {"pattern": "%top%"}
            )
            print("\nProducts matching 'top':")
            for product in results:
                print(f"  {product['name']}: ${product['price']}")
        
        # Write operations with non-read-only executor
        with PooledConnection(pool) as conn:
            executor = QueryExecutor(conn, read_only=False)
            
            # Safe update with parameters
            executor.execute_query(
                "UPDATE products SET price = ? WHERE id = ?",
                (899.99, 1)
            )
            conn.commit()
            
            # Verify update
            results = executor.execute_query("SELECT * FROM products WHERE id = 1")
            print(f"\nUpdated price: ${results[0]['price']}")


if __name__ == "__main__":
    main()
