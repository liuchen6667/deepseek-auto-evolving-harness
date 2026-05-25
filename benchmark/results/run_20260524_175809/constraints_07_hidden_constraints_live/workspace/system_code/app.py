from flask import Flask, request, jsonify
from database import Database
from cache import Cache
from upload import FileUpload
import time

app = Flask(__name__)
db = Database()
cache = Cache()
upload_handler = FileUpload()

# 隐藏约束 4: API rate limit 是 100 req/min (在 cache.py 中实现)
@app.before_request
def check_rate_limit():
    user_id = request.headers.get('X-User-ID', 'anonymous')
    if not cache.increment_rate_limit(user_id):
        return jsonify({'error': 'Rate limit exceeded. Maximum 100 requests per minute.'}), 429

@app.route('/api/data', methods=['GET'])
def get_data():
    query = request.args.get('query', 'SELECT * FROM users')
    
    # 尝试从缓存获取
    cache_key = f"query:{hash(query)}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return jsonify({'data': cached_result, 'source': 'cache'})
    
    # 从数据库查询
    start_time = time.time()
    result = db.execute_query(query)
    query_time = time.time() - start_time
    
    # 缓存结果
    cache.set(cache_key, result)
    
    return jsonify({'data': result, 'source': 'database', 'query_time': query_time})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    return upload_handler.handle_upload()

@app.route('/api/stats', methods=['GET'])
def get_stats():
    # 模拟一些统计查询
    stats_query = """
    SELECT user_id, COUNT(*) as count 
    FROM activities 
    GROUP BY user_id 
    ORDER BY count DESC
    """
    
    result = db.execute_query(stats_query)
    return jsonify({'stats': result})

if __name__ == '__main__':
    app.run(debug=True)