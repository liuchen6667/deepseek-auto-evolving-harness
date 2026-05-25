import redis
from redis.exceptions import ConnectionError, TimeoutError

class RedisConfig:
    """Redis configuration with hidden constraints"""
    
    # Hidden constraint: Redis connection timeout
    CONNECTION_TIMEOUT = 5  # seconds
    
    # Hidden constraint: Redis socket timeout
    SOCKET_TIMEOUT = 3  # seconds
    
    # Hidden constraint: Max connections to Redis
    MAX_CONNECTIONS = 50
    
    # Hidden constraint: Default TTL for all keys
    DEFAULT_TTL = 60  # seconds - CONSTRAINT: Redis缓存TTL只有60秒
    
    # Hidden constraint: Memory limit
    MAX_MEMORY = "100mb"
    
    # Hidden constraint: Eviction policy
    EVICTION_POLICY = "allkeys-lru"
    
    @staticmethod
    def create_client():
        """Create Redis client with constraints"""
        client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            socket_connect_timeout=RedisConfig.CONNECTION_TIMEOUT,
            socket_timeout=RedisConfig.SOCKET_TIMEOUT,
            max_connections=RedisConfig.MAX_CONNECTIONS,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Test connection
        try:
            client.ping()
        except (ConnectionError, TimeoutError) as e:
            print(f"Redis connection failed: {e}")
            return None
        
        return client
    
    @staticmethod
    def set_with_default_ttl(client, key, value):
        """Set key with default TTL"""
        return client.setex(key, RedisConfig.DEFAULT_TTL, value)

# Hidden constraint: Cache key prefix pattern
CACHE_KEY_PREFIX = "app:"

# Hidden constraint: Cache namespace limits
MAX_KEYS_PER_NAMESPACE = 10000