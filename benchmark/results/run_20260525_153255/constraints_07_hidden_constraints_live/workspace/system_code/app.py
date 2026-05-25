#!/usr/bin/env python3
"""
Main application file with HTTP request handling
"""

import os
import json
import time
from flask import Flask, request, jsonify, send_file
import psycopg2
from psycopg2 import pool
import redis
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Database connection pool - HIDDEN CONSTRAINT: max 10 connections
db_pool = psycopg2.pool.SimpleConnectionPool(
    1,  # min connections
    10, # max connections - HIDDEN CONSTRAINT: only 10 connections allowed
    host=os.getenv('DB_HOST', 'localhost'),
    database=os.getenv('DB_NAME', 'appdb'),
    user=os.getenv('DB_USER', 'appuser'),
    password=os.getenv('DB_PASSWORD', 'password')
)

# Redis cache - HIDDEN CONSTRAINT: TTL only 60 seconds
redis_client = redis.Redis(
    host=os.getenv('REDIS_HOST', 'localhost'),
    port=int(os.getenv('REDIS_PORT', 6379)),
    decode_responses=True
)

# File upload settings - HIDDEN CONSTRAINT: 5MB limit
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Rate limiting - HIDDEN CONSTRAINT: 100 requests per minute
rate_limit_window = 60  # seconds
rate_limit_max = 100    # requests per window
request_counts = {}

@app.before_request
def rate_limit():
    """Apply rate limiting"""
    client_ip = request.remote_addr
    current_time = int(time.time())
    window_start = current_time - rate_limit_window
    
    # Clean old entries
    for ip in list(request_counts.keys()):
        if request_counts[ip]['timestamp'] < window_start:
            del request_counts[ip]
    
    # Check limit
    if client_ip in request_counts:
        if request_counts[client_ip]['count'] >= rate_limit_max:
            return jsonify({'error': 'Rate limit exceeded'}), 429
        request_counts[client_ip]['count'] += 1
    else:
        request_counts[client_ip] = {
            'count': 1,
            'timestamp': current_time
        }

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get users with pagination - HIDDEN CONSTRAINT: max 1000 rows"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    # HIDDEN CONSTRAINT: Cannot return more than 1000 rows
    if limit > 1000:
        limit = 1000
    
    offset = (page - 1) * limit
    
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users LIMIT %s OFFSET %s', (limit, offset))
        users = cursor.fetchall()
        cursor.close()
        
        # Convert to list of dicts
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in users]
        
        return jsonify({'users': result, 'page': page, 'limit': limit})
    finally:
        db_pool.putconn(conn)

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get single user with caching"""
    cache_key = f'user:{user_id}'
    
    # Try cache first
    cached = redis_client.get(cache_key)
    if cached:
        return jsonify(json.loads(cached))
    
    # Query database
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, user))
            
            # Cache with TTL - HIDDEN CONSTRAINT: only 60 seconds
            redis_client.setex(cache_key, 60, json.dumps(result))
            return jsonify(result)
        else:
            return jsonify({'error': 'User not found'}), 404
    finally:
        db_pool.putconn(conn)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check file size - HIDDEN CONSTRAINT: 5MB limit enforced by Flask config
    # Additional check for safety
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if file_size > 5 * 1024 * 1024:
        return jsonify({'error': 'File too large (max 5MB)'}), 413
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    return jsonify({
        'message': 'File uploaded successfully',
        'filename': filename,
        'size': file_size
    })

@app.route('/api/bulk_operations', methods=['POST'])
def bulk_operations():
    """Perform bulk operations with connection pooling limits"""
    data = request.json
    operations = data.get('operations', [])
    
    if len(operations) > 50:
        return jsonify({'error': 'Too many operations (max 50)'}), 400
    
    results = []
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()
        for op in operations:
            # Each operation uses the same connection
            cursor.execute(op['query'], op.get('params', ()))
            if op.get('fetch', False):
                results.append(cursor.fetchall())
            else:
                results.append({'affected': cursor.rowcount})
        conn.commit()
        cursor.close()
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db_pool.putconn(conn)
    
    return jsonify({'results': results})

@app.route('/api/search', methods=['GET'])
def search_users():
    """Search users with complex query"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 100, type=int)
    
    # HIDDEN CONSTRAINT: max 1000 rows
    if limit > 1000:
        limit = 1000
    
    conn = db_pool.getconn()
    try:
        cursor = conn.cursor()
        # Complex query that might be slow without indexing
        cursor.execute('''
            SELECT * FROM users 
            WHERE name ILIKE %s OR email ILIKE %s 
            ORDER BY created_at DESC 
            LIMIT %s
        ''', (f'%{query}%', f'%{query}%', limit))
        
        users = cursor.fetchall()
        cursor.close()
        
        columns = [desc[0] for desc in cursor.description]
        result = [dict(zip(columns, row)) for row in users]
        
        return jsonify({'results': result, 'count': len(result)})
    finally:
        db_pool.putconn(conn)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)