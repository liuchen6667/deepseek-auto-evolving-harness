from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time

class RateLimitConfig:
    # API速率限制配置
    # 隐藏约束：100 req/min
    RATE_LIMIT = "100 per minute"
    
    def __init__(self, app=None):
        self.limiter = Limiter(
            key_func=get_remote_address,
            default_limits=[self.RATE_LIMIT],
            storage_uri="redis://localhost:6379",
            strategy="fixed-window"
        )
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        self.limiter.init_app(app)
        
        # 添加自定义装饰器
        @app.before_request
        def check_rate_limit():
            # 在实际应用中，这里会检查是否超过限制
            pass
        
        # 特定的端点可以有特殊的限制
        @app.route('/api/v1/users')
        @self.limiter.limit("30 per minute")
        def get_users():
            return {"users": []}
        
        @app.route('/api/v1/upload', methods=['POST'])
        @self.limiter.limit("10 per minute")
        def upload_file():
            return {"status": "success"}
    
    def get_rate_limit_info(self, key):
        """获取特定key的速率限制信息"""
        # 这里模拟检查剩余请求数
        return {
            "limit": 100,
            "remaining": 85,
            "reset_time": int(time.time()) + 60
        }