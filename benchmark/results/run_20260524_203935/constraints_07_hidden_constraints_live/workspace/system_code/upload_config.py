from flask import request
import os

class UploadConfig:
    # 文件上传配置
    UPLOAD_FOLDER = '/var/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
    # 隐藏约束：文件上传大小限制5MB
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        app.config['UPLOAD_FOLDER'] = self.UPLOAD_FOLDER
        app.config['MAX_CONTENT_LENGTH'] = self.MAX_CONTENT_LENGTH
        
        @app.before_request
        def check_content_length():
            # 检查请求体大小是否超过限制
            if request.content_length and request.content_length > self.MAX_CONTENT_LENGTH:
                return 'File too large', 413
    
    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def save_file(self, file):
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.UPLOAD_FOLDER, filename)
            file.save(file_path)
            return file_path
        return None