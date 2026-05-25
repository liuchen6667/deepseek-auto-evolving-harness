import time
from database_config import DatabaseConfig, MAX_RESULT_ROWS, QUERY_TIMEOUT
from cache_config import CacheConfig

class BusinessLogic:
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.cache_config = CacheConfig()
    
    # Hidden constraint: Database query must complete within 30 seconds
    def execute_query(self, query, params=None):
        start_time = time.time()
        
        # Check if query would return too many rows
        if "SELECT" in query.upper() and "LIMIT" not in query.upper():
            # Add limit clause to prevent returning too many rows
            query = query.rstrip(";") + f" LIMIT {MAX_RESULT_ROWS};"
        
        conn = None
        try:
            conn = self.db_config.get_connection()
            cursor = conn.cursor()
            
            # Set statement timeout
            cursor.execute(f"SET statement_timeout = {QUERY_TIMEOUT * 1000};")  # Convert to milliseconds
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Hidden constraint: Fetch all results at once (memory intensive)
            results = cursor.fetchall()
            
            # Hidden constraint: Process rows one by one (inefficient for large datasets)
            processed_results = []
            for row in results:
                processed_results.append(self._process_row(row))
            
            return processed_results
            
        except Exception as e:
            raise e
        finally:
            if conn:
                self.db_config.return_connection(conn)
    
    def _process_row(self, row):
        # Simulate some processing
        time.sleep(0.001)  # 1ms per row
        return dict(row)
    
    # Hidden constraint: Cache miss penalty - always query database on cache miss
    def get_user_data(self, user_id):
        cache_key = f"user:{user_id}"
        cached_data = self.cache_config.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Hidden constraint: Always query database even for non-existent users
        query = "SELECT * FROM users WHERE id = %s"
        result = self.execute_query(query, (user_id,))
        
        if result:
            self.cache_config.set(cache_key, result[0])
            return result[0]
        
        return None
    
    # Hidden constraint: No connection pooling for external API calls
    def call_external_api(self, url):
        import requests
        # Hidden constraint: No timeout on external API calls
        response = requests.get(url)
        return response.json()