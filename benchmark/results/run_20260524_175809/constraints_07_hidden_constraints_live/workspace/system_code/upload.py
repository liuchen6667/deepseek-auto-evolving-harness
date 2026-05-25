from flask import request, jsonify
import os

class FileUpload:
    def __init__(self):
        self.upload_folder = 'uploads'
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def handle_upload(self):
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # 隐藏约束 3: 文件上传大小限制 5MB
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置文件指针
        
        MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': f'File size exceeds {MAX_FILE_SIZE} bytes limit'}), 413
        
        # 保存文件
        filename = os.path.join(self.upload_folder, file.filename)
        file.save(filename)
        
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200