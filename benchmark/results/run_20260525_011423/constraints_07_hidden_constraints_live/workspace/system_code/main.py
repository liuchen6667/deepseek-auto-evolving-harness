#!/usr/bin/env python3
"""
系统主文件 - 包含隐藏的性能约束
"""

import os
import time
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
import psycopg2
from psycopg2 import pool
import redis
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 隐藏约束 1: 数据库连接池限制 - 最大 10 个连接 (第 15 行)
DB_POOL = psycopg2.pool.SimpleConnectionPool(
    1,  # 最小连接数
    10, # 最大连接数 - 隐藏约束！
    host="localhost",
    database="app_db",
    user="app_user",
    password="password"
)

# 隐藏约束 2: Redis 缓存 TTL 只有 60 秒 (第 23 行)
REDIS_CLIENT = redis.Redis(host='localhost', port=6379, db=0)
CACHE_TTL = 60  # 秒 - 隐藏约束！

# 隐藏约束 3: 文件上传大小限制 5MB (第 27 行)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB - 隐藏约束！
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# 隐藏约束 4: API rate limit 是 100 req/min (第 31 行)
RATE_LIMIT = 100  # 每分钟请求数 - 隐藏约束！
rate_limit_counter = {}

# 隐藏约束 5: 单个查询不能返回超过 1000 行 (第 35 行)
MAX_QUERY_ROWS = 1000  # 隐藏约束！

def check_rate_limit(client_ip: str) -> bool:
    """检查速率限制"""
    current_minute = int(time.time() / 60)
    key = f"{client_ip}:{current_minute}"
    
    if key not in rate_limit_counter:
        rate_limit_counter[key] = 0
    
    rate_limit_counter[key] += 1
    return rate_limit_counter[key] <= RATE_LIMIT

def get_db_connection():
    """从连接池获取数据库连接"""
    try:
        return DB_POOL.getconn()
    except Exception as e:
        app.logger.error(f"无法获取数据库连接: {e}")
        return None

def release_db_connection(conn):
    """释放数据库连接回连接池"""
    if conn:
        DB_POOL.putconn(conn)

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取用户列表 - 演示查询行数限制"""
    client_ip = request.remote_addr
    
    # 检查速率限制
    if not check_rate_limit(client_ip):
        return jsonify({"error": "速率限制超出"}), 429
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "数据库连接失败"}), 500
    
    try:
        cursor = conn.cursor()
        
        # 应用行数限制
        cursor.execute("SELECT * FROM users LIMIT %s", (MAX_QUERY_ROWS + 1,))
        users = cursor.fetchmany(MAX_QUERY_ROWS)  # 最多获取 1000 行
        
        if len(users) == MAX_QUERY_ROWS:
            app.logger.warning(f"查询达到行数限制: {MAX_QUERY_ROWS}")
        
        return jsonify({"users": users, "count": len(users)})
    finally:
        release_db_connection(conn)

@app.route('/api/cache/<key>', methods=['GET'])
def get_cached_data(key):
    """获取缓存数据 - 演示 TTL 限制"""
    cached = REDIS_CLIENT.get(key)
    if cached:
        # 自动续期 TTL
        REDIS_CLIENT.expire(key, CACHE_TTL)
        return jsonify({"data": cached.decode(), "cached": True})
    
    # 模拟数据库查询
    data = f"data_for_{key}"
    REDIS_CLIENT.setex(key, CACHE_TTL, data)  # 使用 60 秒 TTL
    
    return jsonify({"data": data, "cached": False})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传 - 演示文件大小限制"""
    if 'file' not in request.files:
        return jsonify({"error": "没有文件"}), 400
    
    file = request.files['file']
    
    # 检查文件大小
    file.seek(0, 2)  # 移动到文件末尾
    file_size = file.tell()
    file.seek(0)  # 重置位置
    
    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": f"文件太大，最大 {MAX_FILE_SIZE} 字节"}), 413
    
    filename = secure_filename(file.filename)
    # 保存文件逻辑...
    
    return jsonify({"message": "文件上传成功", "filename": filename})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取系统统计信息"""
    stats = {
        "db_pool_size": DB_POOL.maxconn,  # 10
        "cache_ttl": CACHE_TTL,  # 60
        "max_file_size": MAX_FILE_SIZE,  # 5242880
        "rate_limit": RATE_LIMIT,  # 100
        "max_query_rows": MAX_QUERY_ROWS  # 1000
    }
    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True, port=5000)