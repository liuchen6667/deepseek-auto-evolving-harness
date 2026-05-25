from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

app = Flask(__name__)

# Hidden constraint: API rate limit is 100 requests per minute
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

# Hidden constraint: File upload size limit 5MB
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE

# Hidden constraint: Request timeout
REQUEST_TIMEOUT = 30  # seconds

# Hidden constraint: Maximum concurrent requests
MAX_CONCURRENT_REQUESTS = 50

@app.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")  # Additional constraint: Upload endpoint more restricted
def upload_file():
    # File upload handling
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_UPLOAD_SIZE:
        return jsonify({'error': f'File too large. Max size is {MAX_UPLOAD_SIZE} bytes'}), 413
    
    return jsonify({'message': 'File uploaded successfully', 'size': file_size})

@app.route('/data', methods=['GET'])
@limiter.limit("50 per minute")  # Data endpoint has different rate limit
def get_data():
    # Data retrieval logic
    return jsonify({'data': 'sample data'})

if __name__ == '__main__':
    app.run(debug=True)