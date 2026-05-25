import psycopg2
from psycopg2 import pool

# Database connection pool configuration
class DatabaseConfig:
    # Hidden constraint: Max 10 connections in pool
    MAX_CONNECTIONS = 10
    MIN_CONNECTIONS = 2
    
    def __init__(self):
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            self.MIN_CONNECTIONS,
            self.MAX_CONNECTIONS,
            host='localhost',
            database='app_db',
            user='app_user',
            password='secret',
            port=5432
        )
    
    def get_connection(self):
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        self.connection_pool.putconn(conn)

# Hidden constraint: Query timeout of 30 seconds
QUERY_TIMEOUT = 30  # seconds

# Hidden constraint: Maximum result set size
MAX_RESULT_ROWS = 1000  # Single query cannot return more than 1000 rows