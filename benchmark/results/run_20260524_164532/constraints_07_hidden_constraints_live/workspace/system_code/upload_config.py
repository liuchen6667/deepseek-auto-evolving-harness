# File upload configuration
import os
from werkzeug.utils import secure_filename

class UploadConfig:
    # File upload settings
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB in bytes
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
    UPLOAD_FOLDER = '/var/www/uploads'
    
    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in UploadConfig.ALLOWED_EXTENSIONS
    
    @staticmethod
    def check_file_size(file):
        """Check if file size is within limit"""
        # Save current position
        current_pos = file.tell()
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(current_pos)  # Restore position
        
        if file_size > UploadConfig.MAX_FILE_SIZE:
            raise ValueError(f"File size {file_size} exceeds maximum {UploadConfig.MAX_FILE_SIZE}")
        return True
    
    @staticmethod
    def save_uploaded_file(file, user_id):
        """Save uploaded file with constraints"""
        # Check file size
        UploadConfig.check_file_size(file)
        
        # Check filename
        filename = secure_filename(file.filename)
        if not UploadConfig.allowed_file(filename):
            raise ValueError(f"File extension not allowed: {filename}")
        
        # Create user directory if not exists
        user_dir = os.path.join(UploadConfig.UPLOAD_FOLDER, str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        
        # Save file
        file_path = os.path.join(user_dir, filename)
        file.save(file_path)
        
        return file_path

# Additional performance constraints
class PerformanceConfig:
    # Query timeout settings
    QUERY_TIMEOUT = 10  # seconds
    
    # API response timeout
    API_TIMEOUT = 30  # seconds
    
    # Concurrent processing limits
    MAX_CONCURRENT_REQUESTS = 50
    MAX_CONCURRENT_DB_QUERIES = 5
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 100