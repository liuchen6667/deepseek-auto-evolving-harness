from flask import Flask, jsonify, request
import logging
from database_config import DatabaseConfig
from cache_config import CacheConfig
from upload_config import UploadConfig
from rate_limit import RateLimitConfig
from query_limiter import QueryLimiter

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 初始化配置
db_config = DatabaseConfig()
cache_config = CacheConfig()
upload_config = UploadConfig(app)
rate_limit_config = RateLimitConfig(app)
query_limiter = QueryLimiter(db_config)

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "healthy",
        "constraints": {
            "max_db_connections": 10,
            "redis_ttl": 60,
            "max_upload_size": "5MB",
            "rate_limit": "100 req/min",
            "max_query_rows": 1000
        }
    })

@app.route('/api/v1/data', methods=['GET'])
def get_data():
    """获取数据端点，演示查询限制"""
    try:
        # 模拟数据库查询
        query = "SELECT * FROM users WHERE active = TRUE ORDER BY created_at DESC"
        results = query_limiter.execute_query(query)
        
        # 使用缓存
        cache_key = "active_users"
        cached_data = cache_config.get(cache_key)
        
        if cached_data:
            return jsonify({"source": "cache", "data": cached_data})
        else:
            # 模拟处理结果
            data = [{"id": i, "name": f"User {i}"} for i in range(min(len(results), 10))]
            cache_config.set(cache_key, data)
            return jsonify({"source": "database", "data": data})
            
    except Exception as e:
        logger.error(f"获取数据失败: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/v1/upload', methods=['POST'])
def upload():
    """文件上传端点"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not upload_config.allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
    
    # 检查文件大小
    file.seek(0, 2)  # 移动到文件末尾
    file_size = file.tell()
    file.seek(0)  # 重置文件指针
    
    if file_size > upload_config.MAX_CONTENT_LENGTH:
        return jsonify({"error": f"File too large. Max size is {upload_config.MAX_CONTENT_LENGTH} bytes"}), 413
    
    saved_path = upload_config.save_file(file)
    if saved_path:
        return jsonify({"status": "success", "path": saved_path})
    else:
        return jsonify({"error": "Failed to save file"}), 500

@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """获取系统统计信息"""
    return jsonify({
        "database": {
            "max_connections": 10,
            "current_connections": 3
        },
        "cache": {
            "default_ttl": 60,
            "keys_count": 42
        },
        "rate_limiting": {
            "limit": 100,
            "window": "minute"
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)