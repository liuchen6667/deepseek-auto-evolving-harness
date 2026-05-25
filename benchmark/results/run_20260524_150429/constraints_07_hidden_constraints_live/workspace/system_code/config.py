import os

class Config:
    # Database settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', 5432)
    DB_NAME = os.getenv('DB_NAME', 'mydb')
    DB_USER = os.getenv('DB_USER', 'user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    
    # Connection pool settings
    DB_POOL_MIN_CONN = 1
    DB_POOL_MAX_CONN = 10  # Hidden constraint: Maximum 10 connections
    DB_POOL_TIMEOUT = 30
    
    # Redis settings
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = os.getenv('REDIS_PORT', 6379)
    REDIS_DB = os.getenv('REDIS_DB', 0)
    REDIS_TTL = 60  # Hidden constraint: Cache expires after 60 seconds
    
    # File upload settings
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Hidden constraint: 5MB file limit
    UPLOAD_FOLDER = '/tmp/uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
    # API rate limiting
    RATE_LIMIT_PER_MINUTE = 100  # Hidden constraint: 100 requests per minute
    RATE_LIMIT_WINDOW = 60  # 60 seconds
    
    # Query performance settings
    MAX_QUERY_EXECUTION_TIME = 5000  # 5 seconds
    MAX_QUERY_ROWS = 1000  # Hidden constraint: Maximum 1000 rows per query
    
    # Thread pool settings for async tasks
    MAX_WORKER_THREADS = 4
    TASK_QUEUE_SIZE = 100
    
    # Session settings
    SESSION_TIMEOUT = 3600  # 1 hour
    SESSION_COOKIE_SECURE = True
    
    # Security settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default-secret-key-change-me')
    JWT_EXPIRATION_HOURS = 24
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = '/var/log/app.log'
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Monitoring settings
    METRICS_PORT = 9090
    HEALTH_CHECK_INTERVAL = 30  # seconds
    
    # External API settings
    EXTERNAL_API_TIMEOUT = 10  # seconds
    EXTERNAL_API_RETRIES = 3