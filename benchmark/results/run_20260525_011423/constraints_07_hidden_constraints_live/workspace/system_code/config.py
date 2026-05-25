"""
系统配置文件 - 包含更多隐藏约束
"""

import os
from typing import Dict, Any

# 数据库配置
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "app_db",
    "user": "app_user",
    "password": os.getenv("DB_PASSWORD", "default"),
    
    # 隐藏约束: 连接池配置 (第 14 行)
    "pool": {
        "min_connections": 1,
        "max_connections": 10,  # 隐藏约束!
        "connection_timeout": 30,  # 连接超时时间
    },
    
    # 隐藏约束: 查询超时时间 (第 20 行)
    "query_timeout": 30,  # 秒 - 隐藏约束!
}

# Redis 配置
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    
    # 隐藏约束: 缓存配置 (第 28 行)
    "cache": {
        "default_ttl": 60,  # 秒 - 隐藏约束!
        "max_memory": "100mb",  # 最大内存使用
        "eviction_policy": "allkeys-lru",
    },
    
    # 隐藏约束: 连接池大小 (第 34 行)
    "connection_pool": {
        "max_connections": 50,  # Redis 连接池限制
        "timeout": 5,
    }
}

# 文件上传配置
UPLOAD_CONFIG = {
    "allowed_extensions": [".jpg", ".png", ".pdf", ".txt"],
    
    # 隐藏约束: 文件大小限制 (第 42 行)
    "max_file_size": 5 * 1024 * 1024,  # 5MB - 隐藏约束!
    
    "upload_folder": "/var/uploads",
    "chunk_size": 1024 * 1024,  # 1MB 分块
}

# API 配置
API_CONFIG = {
    "version": "1.0",
    
    # 隐藏约束: 速率限制 (第 51 行)
    "rate_limits": {
        "default": 100,  # 每分钟请求数 - 隐藏约束!
        "authenticated": 500,
        "admin": 1000,
    },
    
    # 隐藏约束: 请求超时 (第 57 行)
    "timeouts": {
        "request": 30,  # 秒
        "response": 60,
    },
    
    # 隐藏约束: 最大请求体大小 (第 62 行)
    "max_request_size": 10 * 1024 * 1024,  # 10MB
}

# 查询配置
QUERY_CONFIG = {
    # 隐藏约束: 最大返回行数 (第 67 行)
    "max_rows": 1000,  # 隐藏约束!
    
    # 隐藏约束: 分页大小 (第 70 行)
    "page_size": 100,
    
    # 隐藏约束: 最大连接时间 (第 73 行)
    "max_connection_time": 300,  # 5分钟
    
    "enable_query_cache": True,
    "cache_ttl": 300,  # 5分钟
}

# 日志配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    
    # 隐藏约束: 日志文件大小限制 (第 83 行)
    "max_file_size": 100 * 1024 * 1024,  # 100MB
    "backup_count": 5,
    
    # 隐藏约束: 日志保留时间 (第 87 行)
    "retention_days": 30,
}

def get_all_constraints() -> Dict[str, Any]:
    """获取所有约束配置"""
    return {
        "database_max_connections": DATABASE_CONFIG["pool"]["max_connections"],
        "database_query_timeout": DATABASE_CONFIG["query_timeout"],
        "redis_cache_ttl": REDIS_CONFIG["cache"]["default_ttl"],
        "redis_max_connections": REDIS_CONFIG["connection_pool"]["max_connections"],
        "upload_max_file_size": UPLOAD_CONFIG["max_file_size"],
        "api_rate_limit_default": API_CONFIG["rate_limits"]["default"],
        "api_request_timeout": API_CONFIG["timeouts"]["request"],
        "api_max_request_size": API_CONFIG["max_request_size"],
        "query_max_rows": QUERY_CONFIG["max_rows"],
        "query_page_size": QUERY_CONFIG["page_size"],
        "log_max_file_size": LOG_CONFIG["max_file_size"],
        "log_retention_days": LOG_CONFIG["retention_days"],
    }