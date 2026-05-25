from api import app
from database import Database
from cache import Cache
import logging
from logging.handlers import RotatingFileHandler
import os

# 配置日志
log_handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
log_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
log_handler.setFormatter(formatter)

app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

# 初始化组件
db = Database()
cache = Cache()

@app.before_request
def log_request():
    app.logger.info(f"Request: {request.method} {request.path}")

@app.after_request
def log_response(response):
    app.logger.info(f"Response: {response.status_code}")
    return response

if __name__ == '__main__':
    # 确保日志目录存在
    os.makedirs('logs', exist_ok=True)
    
    # 记录启动信息
    app.logger.info("Starting application...")
    app.logger.info(f"Database max connections: 10")
    app.logger.info(f"Cache TTL: 60 seconds")
    app.logger.info(f"Max upload size: 5MB")
    app.logger.info(f"Rate limit: 100 requests per minute")
    app.logger.info(f"Query max rows: 1000")
    
    app.run(host='0.0.0.0', port=5000, debug=False)