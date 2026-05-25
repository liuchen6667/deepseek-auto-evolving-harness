#!/usr/bin/env python3
"""
Database configuration and connection management
"""

import os
import psycopg2
from psycopg2 import pool
import time
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self):
        # HIDDEN CONSTRAINT: Connection pool with max 10 connections
        self.pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,  # MAXIMUM 10 CONNECTIONS
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'appdb'),
            user=os.getenv('DB_USER', 'appuser'),
            password=os.getenv('DB_PASSWORD', 'password'),
            port=os.getenv('DB_PORT', 5432)
        )
        
        # HIDDEN CONSTRAINT: Connection timeout of 30 seconds
        self.connection_timeout = 30
        
        # HIDDEN CONSTRAINT: Statement timeout of 10 seconds
        self.statement_timeout = 10000  # milliseconds
        
    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool"""
        conn = None
        start_time = time.time()
        
        # HIDDEN CONSTRAINT: Wait for connection with timeout
        while not conn and time.time() - start_time < self.connection_timeout:
            try:
                conn = self.pool.getconn(timeout=5)
            except psycopg2.pool.PoolError:
                time.sleep(0.1)
        
        if not conn:
            raise TimeoutError("Could not get database connection within timeout")
        
        try:
            # Set statement timeout
            with conn.cursor() as cur:
                cur.execute(f"SET statement_timeout = {self.statement_timeout}")
            
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self):
        """Get a cursor from a connection"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query with proper resource management"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params or ())
            
            if fetch:
                # HIDDEN CONSTRAINT: Maximum fetch size of 1000 rows
                rows = cursor.fetchmany(1000)
                if cursor.fetchone() is not None:
                    raise RuntimeError("Query returned more than 1000 rows")
                return rows
            else:
                return cursor.rowcount
    
    def get_pool_status(self):
        """Get connection pool status"""
        return {
            'min_connections': 1,
            'max_connections': 10,
            'available': self.pool._used + self.pool._rused,
            'used': len(self.pool._used),
            'waiting': len(self.pool._waiting) if hasattr(self.pool, '_waiting') else 0
        }
    
    def close_all(self):
        """Close all connections in the pool"""
        self.pool.closeall()

# Global database manager instance
db_manager = DatabaseManager()

# Query templates with constraints
QUERIES = {
    'get_user': 'SELECT * FROM users WHERE id = %s LIMIT 1',
    'get_users_paginated': 'SELECT * FROM users ORDER BY id LIMIT %s OFFSET %s',
    'search_users': '''
        SELECT * FROM users 
        WHERE name ILIKE %s OR email ILIKE %s 
        ORDER BY created_at DESC 
        LIMIT %s
    ''',
    'count_users': 'SELECT COUNT(*) FROM users',
    
    # HIDDEN CONSTRAINT: Complex join with performance implications
    'get_user_with_orders': '''
        SELECT u.*, COUNT(o.id) as order_count, SUM(o.amount) as total_spent
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id
        WHERE u.id = %s
        GROUP BY u.id
        LIMIT 1
    ''',
    
    # HIDDEN CONSTRAINT: Window function that can be heavy
    'get_user_ranking': '''
        SELECT id, name, email,
               RANK() OVER (ORDER BY created_at) as join_rank,
               ROW_NUMBER() OVER (ORDER BY id) as user_number
        FROM users
        WHERE id = %s
        LIMIT 1
    '''
}

def create_tables():
    """Create necessary tables with constraints"""
    create_queries = [
        '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id),
            amount DECIMAL(10, 2) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''',
        '''
        CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
        ''',
        '''
        CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
        ''',
        '''
        CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
        '''
    ]
    
    with db_manager.get_cursor() as cursor:
        for query in create_queries:
            cursor.execute(query)