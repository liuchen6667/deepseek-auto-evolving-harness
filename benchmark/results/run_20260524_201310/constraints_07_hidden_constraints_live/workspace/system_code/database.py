import psycopg2
from psycopg2 import pool
import os

class Database:
    def __init__(self):
        # 数据库连接池配置 - 隐藏约束1：最大10个连接
        self.pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,  # 这里限制了最大连接数
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'app_db'),
            user=os.getenv('DB_USER', 'app_user'),
            password=os.getenv('DB_PASSWORD', 'password')
        )
    
    def get_connection(self):
        return self.pool.getconn()
    
    def release_connection(self, conn):
        self.pool.putconn(conn)
    
    def execute_query(self, query, params=None):
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                # 隐藏约束5：单个查询不能返回超过1000行
                rows = cursor.fetchmany(1000)  # 这里限制了最大返回行数
                return rows
        finally:
            self.release_connection(conn)