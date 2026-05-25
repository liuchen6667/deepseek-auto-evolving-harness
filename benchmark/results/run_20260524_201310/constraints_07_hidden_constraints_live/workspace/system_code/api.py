from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)

# 隐藏约束4：API rate limit是100 req/min
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per minute"]  # 速率限制配置
)

# 隐藏约束3：文件上传大小限制5MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB限制

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")  # 上传接口有更严格的限制
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # 检查文件大小
    file.seek(0, 2)  # 移动到文件末尾
    file_size = file.tell()
    file.seek(0)  # 重置文件指针
    
    if file_size > 5 * 1024 * 1024:
        return jsonify({'error': 'File too large (max 5MB)'}), 413
    
    # 处理文件...
    return jsonify({'message': 'File uploaded successfully'}), 200

@app.route('/data', methods=['GET'])
@limiter.limit("100 per minute")
def get_data():
    # 数据处理逻辑
    return jsonify({'data': 'some data'}), 200

@app.route('/users', methods=['GET'])
def get_users():
    from database import Database
    db = Database()
    # 这里会触发行数限制
    users = db.execute_query("SELECT * FROM users ORDER BY created_at DESC")
    return jsonify({'users': users}), 200