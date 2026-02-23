"""Database connection pool manager with connection pooling support."""

import queue
import sqlite3
import threading
from typing import Any, Dict, Optional


class ConnectionPool:
    """Manages a pool of database connections."""

    def __init__(self, config: Dict[str, Any], pool_size: int = 5):
        """
        Initialize connection pool.
        
        Args:
            config: Database configuration (e.g., {'database': 'db.sqlite'})
            pool_size: Maximum number of connections in pool
        """
        self.config = config
        self.pool_size = pool_size
        self._pool = queue.Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._closed = False
        
        # Pre-populate pool
        for _ in range(pool_size):
            self._pool.put(self._create_connection())

    def _create_connection(self):
        """Create a new database connection."""
        try:
            return sqlite3.connect(**self.config, check_same_thread=False)
        except Exception as e:
            raise ConnectionError(f"Failed to create connection: {e}")

    def get_connection(self, timeout: float = 5.0):
        """
        Get a connection from the pool.
        
        Args:
            timeout: Maximum time to wait for a connection
            
        Returns:
            Database connection
            
        Raises:
            ConnectionError: If pool is closed or timeout occurs
        """
        if self._closed:
            raise ConnectionError("Connection pool is closed")
        
        try:
            conn = self._pool.get(timeout=timeout)
            # Verify connection is alive
            try:
                conn.execute("SELECT 1")
                return conn
            except Exception:
                # Connection is dead, create new one
                conn.close()
                return self._create_connection()
        except queue.Empty:
            raise ConnectionError("Connection pool timeout")

    def return_connection(self, conn):
        """
        Return a connection to the pool.
        
        Args:
            conn: Database connection to return
        """
        if self._closed:
            conn.close()
            return
        
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            conn.close()

    def cleanup(self):
        """Close all connections and cleanup the pool."""
        with self._lock:
            if self._closed:
                return
            
            self._closed = True
            while not self._pool.empty():
                try:
                    conn = self._pool.get_nowait()
                    conn.close()
                except queue.Empty:
                    break

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()


class PooledConnection:
    """Wrapper for automatic connection return to pool."""

    def __init__(self, pool: ConnectionPool, timeout: float = 5.0):
        self.pool = pool
        self.conn = pool.get_connection(timeout)

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.return_connection(self.conn)


# Example usage
if __name__ == "__main__":
    # Create pool
    config = {"database": ":memory:"}
    pool = ConnectionPool(config, pool_size=3)
    
    try:
        # Get connection manually
        conn = pool.get_connection()
        cursor = conn.execute("SELECT 1")
        print(f"Manual: {cursor.fetchone()}")
        pool.return_connection(conn)
        
        # Use context manager
        with PooledConnection(pool) as conn:
            cursor = conn.execute("SELECT 2")
            print(f"Context manager: {cursor.fetchone()}")
    finally:
        pool.cleanup()
