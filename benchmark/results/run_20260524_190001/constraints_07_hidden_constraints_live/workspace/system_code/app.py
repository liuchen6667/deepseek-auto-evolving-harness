from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import psycopg2
from psycopg2 import pool
import redis
import os

app = Flask(__name__)

# Database connection pool - hidden constraint: max 10 connections
db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,  # min, max connections - CONSTRAINT: max 10 connections
    host='localhost',
    database='mydb',
    user='user',
    password='password'
)

# Redis cache - hidden constraint: TTL only 60 seconds
redis_client = redis.Redis(host='localhost', port=6379, db=0)
REDIS_TTL = 60  # CONSTRAINT: TTL只有60秒

# Rate limiting - hidden constraint: 100 req/min
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]  # CONSTRAINT: API rate limit是100 req/min
)

# File upload configuration - hidden constraint: 5MB limit
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # CONSTRAINT: 文件上传大小限制5MB

@app.route('/users', methods=['GET'])
@limiter.limit("100 per minute")
def get_users():
    """Get users with pagination"""
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 100))
    
    # Hidden constraint: single query cannot return more than 1000 rows
    if limit > 1000:
        limit = 1000  # CONSTRAINT: 单个查询不能返回超过1000行
    
    offset = (page - 1) * limit
    
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        
        # Check cache first
        cache_key = f"users:{page}:{limit}"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            return jsonify({'from_cache': True, 'data': eval(cached_data)})
        
        # Query database
        cursor.execute("SELECT * FROM users ORDER BY id LIMIT %s OFFSET %s", (limit, offset))
        users = cursor.fetchall()
        
        # Cache with 60 second TTL
        redis_client.setex(cache_key, REDIS_TTL, str(users))
        
        db_pool.putconn(conn)
        
        return jsonify({'from_cache': False, 'data': users, 'count': len(users)})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload file endpoint"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # File size check
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > 5 * 1024 * 1024:
        return jsonify({'error': 'File size exceeds 5MB limit'}), 400
    
    # Save file
    filename = file.filename
    file.save(f'uploads/{filename}')
    
    return jsonify({'message': 'File uploaded successfully', 'filename': filename})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    # Another hidden constraint: complex query timeout
    try:
        conn = db_pool.getconn()
        cursor = conn.cursor()
        
        # This query might be slow but has no explicit timeout
        cursor.execute("""
            SELECT user_id, COUNT(*) as count 
            FROM activities 
            WHERE created_at > NOW() - INTERVAL '1 day'
            GROUP BY user_id
            ORDER BY count DESC
        """)
        
        stats = cursor.fetchall()
        db_pool.putconn(conn)
        
        return jsonify({'stats': stats})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)