import redis
import json
import os

class Cache:
    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
    
    def get(self, key):
        return self.client.get(key)
    
    def set(self, key, value):
        # 隐藏约束2：Redis缓存TTL只有60秒
        return self.client.setex(key, 60, value)  # TTL固定为60秒
    
    def set_with_ttl(self, key, value, ttl):
        # 这个方法允许自定义TTL，但主代码中没有使用
        return self.client.setex(key, ttl, value)