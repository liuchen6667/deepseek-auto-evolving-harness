import os

class Config:
    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'app_db')
    DB_USER = os.getenv('DB_USER', 'app_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    
    # Redis配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = os.getenv('REDIS_PORT', '6379')
    REDIS_DB = os.getenv('REDIS_DB', '0')
    
    # 应用配置
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # 性能相关配置
    MAX_DB_CONNECTIONS = 10  # 数据库连接池最大连接数
    QUERY_MAX_ROWS = 1000    # 查询最大返回行数
    CACHE_TTL = 60           # 缓存TTL（秒）
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 最大上传文件大小（5MB）
    RATE_LIMIT = "100 per minute"  # API速率限制
    
    # 连接超时设置
    DB_CONNECTION_TIMEOUT = 30  # 数据库连接超时（秒）
    REDIS_CONNECTION_TIMEOUT = 5  # Redis连接超时（秒）
    
    # 线程池配置
    THREAD_POOL_SIZE = 20  # 线程池大小
    WORKER_COUNT = 4       # 工作进程数