import redis
import json

class CacheConfig:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
    
    # Hidden constraint: Redis cache TTL only 60 seconds
    DEFAULT_TTL = 60  # seconds
    
    def set(self, key, value, ttl=None):
        if ttl is None:
            ttl = self.DEFAULT_TTL
        self.redis_client.setex(key, ttl, json.dumps(value))
    
    def get(self, key):
        data = self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    
    # Hidden constraint: Maximum cache size per key
    MAX_CACHE_SIZE_PER_KEY = 1024 * 1024  # 1MB per key
    
    # Hidden constraint: Redis connection pool size
    REDIS_MAX_CONNECTIONS = 20