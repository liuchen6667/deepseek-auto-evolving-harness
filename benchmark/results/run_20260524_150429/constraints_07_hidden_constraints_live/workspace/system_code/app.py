import psycopg2
from redis import Redis
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Database connection pool configuration
DB_POOL_SIZE = 10  # Maximum 10 connections
DB_CONN_TIMEOUT = 30

# Redis cache configuration
REDIS_TTL = 60  # Cache expires after 60 seconds

# File upload configuration
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB

# API rate limiting
RATE_LIMIT = 100  # 100 requests per minute

# Query limits
MAX_QUERY_ROWS = 1000  # Maximum rows per query

# Initialize database connection pool
def init_db_pool():
    return psycopg2.pool.SimpleConnectionPool(
        1, DB_POOL_SIZE,
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'mydb'),
        user=os.getenv('DB_USER', 'user'),
        password=os.getenv('DB_PASSWORD', 'password')
    )

db_pool = init_db_pool()
redis_client = Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=6379)

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    Fetch data from database with pagination
    """
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    # Enforce query limit
    if limit > MAX_QUERY_ROWS:
        limit = MAX_QUERY_ROWS
    
    offset = (page - 1) * limit
    
    # Try to get from cache first
    cache_key = f'data:{page}:{limit}'
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return jsonify({'data': cached_data.decode(), 'source': 'cache'})
    
    # Get connection from pool
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM data LIMIT %s OFFSET %s', (limit, offset))
        rows = cursor.fetchall()
        
        # Cache the result
        redis_client.setex(cache_key, REDIS_TTL, str(rows))
        
        return jsonify({'data': rows, 'source': 'database'})
    finally:
        db_pool.putconn(conn)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle file uploads
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > MAX_UPLOAD_SIZE:
        return jsonify({'error': f'File too large. Maximum size is {MAX_UPLOAD_SIZE} bytes'}), 413
    
    # Process file...
    return jsonify({'message': 'File uploaded successfully', 'size': file_size})

@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Get user list with rate limiting
    """
    user_id = request.args.get('user_id')
    
    # Rate limiting logic
    rate_key = f'rate:{user_id}'
    current_count = redis_client.get(rate_key)
    if current_count and int(current_count) >= RATE_LIMIT:
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    # Increment rate counter
    redis_client.incr(rate_key)
    redis_client.expire(rate_key, 60)  # Reset after 60 seconds
    
    # Query logic...
    return jsonify({'users': []})

if __name__ == '__main__':
    app.run(debug=True)