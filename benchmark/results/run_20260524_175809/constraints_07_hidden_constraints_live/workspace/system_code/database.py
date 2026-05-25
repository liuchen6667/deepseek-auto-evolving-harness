import psycopg2
from psycopg2 import pool
import os

class Database:
    def __init__(self):
        # 隐藏约束 1: 数据库连接池限制为 10 个连接
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,  # 最大连接数限制为 10
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'app_db'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
    
    def get_connection(self):
        return self.connection_pool.getconn()
    
    def release_connection(self, conn):
        self.connection_pool.putconn(conn)
    
    def execute_query(self, query, params=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # 隐藏约束 5: 单个查询不能返回超过 1000 行
            rows = cursor.fetchall()
            if len(rows) > 1000:
                # 记录警告
                print(f"警告: 查询返回 {len(rows)} 行，超过 1000 行限制")
                rows = rows[:1000]  # 截断结果
            
            return rows
        finally:
            self.release_connection(conn)