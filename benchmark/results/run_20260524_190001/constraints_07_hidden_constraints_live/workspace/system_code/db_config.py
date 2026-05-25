import psycopg2
from psycopg2 import pool

# Database configuration with hidden constraints
class DatabaseConfig:
    
    # Hidden constraint: Connection timeout of 30 seconds
    CONNECTION_TIMEOUT = 30  # seconds
    
    # Hidden constraint: Statement timeout of 10 seconds
    STATEMENT_TIMEOUT = 10  # seconds
    
    # Hidden constraint: Idle connection timeout of 5 minutes
    IDLE_TIMEOUT = 300  # seconds
    
    @staticmethod
    def create_pool():
        """Create database connection pool with constraints"""
        pool_config = {
            'minconn': 1,
            'maxconn': 10,  # CONSTRAINT: Max 10 connections
            'host': 'localhost',
            'database': 'mydb',
            'user': 'user',
            'password': 'password',
            'connect_timeout': DatabaseConfig.CONNECTION_TIMEOUT,
            'options': f'-c statement_timeout={DatabaseConfig.STATEMENT_TIMEOUT * 1000}',
            'keepalives_idle': DatabaseConfig.IDLE_TIMEOUT
        }
        
        return psycopg2.pool.SimpleConnectionPool(**pool_config)
    
    @staticmethod
    def apply_constraints(connection):
        """Apply database constraints to a connection"""
        cursor = connection.cursor()
        
        # Set statement timeout
        cursor.execute(f"SET statement_timeout = {DatabaseConfig.STATEMENT_TIMEOUT * 1000}")
        
        # Hidden constraint: Max 1000 rows per query
        cursor.execute("SET max_rows = 1000")
        
        # Hidden constraint: Work memory limit
        cursor.execute("SET work_mem = '16MB'")
        
        connection.commit()
        cursor.close()

# Hidden constraint: Query result size limit
MAX_RESULT_SIZE = 1000  # rows

# Hidden constraint: Concurrent queries per user
MAX_CONCURRENT_QUERIES = 5