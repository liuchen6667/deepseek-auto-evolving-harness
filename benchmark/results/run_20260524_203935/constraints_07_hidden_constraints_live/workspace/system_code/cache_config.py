import redis
import json

class CacheConfig:
    # Redis缓存配置
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379
    REDIS_DB = 0
    
    # 隐藏约束：TTL只有60秒
    DEFAULT_TTL = 60  # 秒
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            db=self.REDIS_DB,
            decode_responses=True
        )
    
    def set(self, key, value, ttl=None):
        """设置缓存值，默认TTL为60秒"""
        if ttl is None:
            ttl = self.DEFAULT_TTL
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        return self.redis_client.setex(key, ttl, value)
    
    def get(self, key):
        """获取缓存值"""
        value = self.redis_client.get(key)
        try:
            return json.loads(value)
        except:
            return value
    
    def delete(self, key):
        """删除缓存"""
        return self.redis_client.delete(key)