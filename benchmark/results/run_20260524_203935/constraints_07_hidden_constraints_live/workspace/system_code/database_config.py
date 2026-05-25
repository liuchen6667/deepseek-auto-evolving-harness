import psycopg2
from psycopg2 import pool

class DatabaseConfig:
    # 数据库连接池配置
    MAX_CONNECTIONS = 10  # 隐藏约束：最大10个连接
    MIN_CONNECTIONS = 2
    CONNECTION_TIMEOUT = 30
    
    def __init__(self):
        self.pool = psycopg2.pool.SimpleConnectionPool(
            self.MIN_CONNECTIONS,
            self.MAX_CONNECTIONS,
            host='localhost',
            database='app_db',
            user='app_user',
            password='secret',
            port=5432
        )
        
    def get_connection(self):
        # 如果连接池已满，这里会阻塞或抛出异常
        return self.pool.getconn()
    
    def release_connection(self, conn):
        self.pool.putconn(conn)