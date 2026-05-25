# Database configuration
import psycopg2
from psycopg2 import pool

class DatabaseConfig:
    # Connection pool settings
    MAX_CONNECTIONS = 10  # Maximum connections in pool
    MIN_CONNECTIONS = 2   # Minimum connections in pool
    CONNECTION_TIMEOUT = 30  # Connection timeout in seconds
    
    @staticmethod
    def create_connection_pool():
        """Create a connection pool with max 10 connections"""
        return psycopg2.pool.SimpleConnectionPool(
            DatabaseConfig.MIN_CONNECTIONS,
            DatabaseConfig.MAX_CONNECTIONS,
            host="localhost",
            database="app_db",
            user="app_user",
            password="secret",
            port=5432
        )

    # Query constraints
    MAX_ROWS_PER_QUERY = 1000  # Maximum rows returned per query
    
    @staticmethod
    def execute_query_with_limit(cursor, query, params=None):
        """Execute query with row limit"""
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Apply row limit
        rows = cursor.fetchall()
        if len(rows) > DatabaseConfig.MAX_ROWS_PER_QUERY:
            print(f"Warning: Query returned {len(rows)} rows, limiting to {DatabaseConfig.MAX_ROWS_PER_QUERY}")
            return rows[:DatabaseConfig.MAX_ROWS_PER_QUERY]
        return rows