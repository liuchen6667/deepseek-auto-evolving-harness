# Redis cache configuration
import redis
import json

class CacheConfig:
    # Redis connection settings
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_PASSWORD = None
    
    # Cache TTL settings
    DEFAULT_TTL = 60  # Default TTL in seconds (1 minute)
    USER_SESSION_TTL = 3600  # User session TTL (1 hour)
    API_RESPONSE_TTL = 30  # API response cache TTL
    
    @staticmethod
    def get_redis_client():
        """Get Redis client connection"""
        return redis.Redis(
            host=CacheConfig.REDIS_HOST,
            port=CacheConfig.REDIS_PORT,
            db=CacheConfig.REDIS_DB,
            password=CacheConfig.REDIS_PASSWORD,
            decode_responses=True
        )
    
    @staticmethod
    def set_with_ttl(key, value, ttl=None):
        """Set cache value with TTL"""
        client = CacheConfig.get_redis_client()
        if ttl is None:
            ttl = CacheConfig.DEFAULT_TTL
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        client.setex(key, ttl, value)
        
    @staticmethod
    def get(key):
        """Get cache value"""
        client = CacheConfig.get_redis_client()
        value = client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

# Rate limiting configuration
class RateLimitConfig:
    # API rate limits
    REQUESTS_PER_MINUTE = 100  # Max 100 requests per minute per IP
    REQUESTS_PER_HOUR = 1000   # Max 1000 requests per hour per IP
    
    @staticmethod
    def check_rate_limit(ip_address):
        """Check if IP is within rate limits"""
        # Implementation would check Redis for request counts
        # This is a simplified version
        cache_key = f"rate_limit:{ip_address}:minute"
        client = CacheConfig.get_redis_client()
        
        current_count = client.get(cache_key)
        if current_count and int(current_count) >= RateLimitConfig.REQUESTS_PER_MINUTE:
            return False
        return True