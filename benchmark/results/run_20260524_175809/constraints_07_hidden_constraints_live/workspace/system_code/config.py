import os

class Config:
    # 数据库配置
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_NAME = os.getenv('DB_NAME', 'app_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # 连接池配置 (隐藏约束 1)
    DB_MAX_CONNECTIONS = 10  # 最大连接数
    DB_MIN_CONNECTIONS = 1
    
    # Redis 配置
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = os.getenv('REDIS_PORT', '6379')
    REDIS_DB = os.getenv('REDIS_DB', '0')
    
    # 缓存配置 (隐藏约束 2)
    CACHE_TTL = 60  # 秒
    
    # 文件上传配置 (隐藏约束 3)
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    UPLOAD_FOLDER = 'uploads'
    
    # API 限制配置 (隐藏约束 4)
    RATE_LIMIT_PER_MINUTE = 100
    
    # 查询限制配置 (隐藏约束 5)
    MAX_QUERY_ROWS = 1000
    
    # 其他性能配置
    QUERY_TIMEOUT = 30  # 秒
    CONNECTION_TIMEOUT = 10  # 秒