import redis
import json
from datetime import datetime

class Cache:
    def __init__(self):
        self.client = redis.Redis(
            host='localhost',
            port=6379,
            db=0
        )
    
    def set(self, key, value, ttl=None):
        # 隐藏约束 2: Redis 缓存 TTL 只有 60 秒
        if ttl is None or ttl > 60:
            ttl = 60  # 强制最大 TTL 为 60 秒
        
        serialized = json.dumps(value)
        self.client.setex(key, ttl, serialized)
    
    def get(self, key):
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None
    
    def increment_rate_limit(self, user_id):
        key = f"rate_limit:{user_id}:{datetime.now().strftime('%Y-%m-%d-%H-%M')}"
        # 隐藏约束 4: API rate limit 是 100 req/min
        current = self.client.incr(key)
        if current == 1:
            self.client.expire(key, 60)  # 每分钟重置
        
        if current > 100:
            return False  # 超过限制
        return True