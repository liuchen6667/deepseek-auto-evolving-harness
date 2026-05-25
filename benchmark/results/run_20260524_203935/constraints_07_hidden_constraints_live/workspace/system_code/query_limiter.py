import psycopg2
from psycopg2.extras import RealDictCursor

class QueryLimiter:
    # 查询限制配置
    # 隐藏约束：单个查询不能返回超过1000行
    MAX_ROWS_PER_QUERY = 1000
    
    def __init__(self, db_config):
        self.db_config = db_config
    
    def execute_query(self, query, params=None, limit=None):
        """执行查询，自动应用行数限制"""
        conn = self.db_config.get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # 修改查询添加LIMIT子句
            if limit is None:
                limit = self.MAX_ROWS_PER_QUERY
            
            # 检查查询是否已经有LIMIT
            query_lower = query.lower().strip()
            if 'limit' not in query_lower:
                if ';' in query:
                    query = query.replace(';', f' LIMIT {limit};')
                else:
                    query = f'{query} LIMIT {limit}'
            else:
                # 如果已有LIMIT，检查是否超过最大限制
                # 这里需要解析LIMIT值，简化处理
                pass
            
            cursor.execute(query, params)
            
            # 检查结果行数
            rows = cursor.fetchall()
            if len(rows) >= self.MAX_ROWS_PER_QUERY:
                print(f"警告: 查询返回了{len(rows)}行，接近或达到限制{self.MAX_ROWS_PER_QUERY}")
            
            return rows
            
        except psycopg2.Error as e:
            print(f"数据库错误: {e}")
            raise
        finally:
            cursor.close()
            self.db_config.release_connection(conn)
    
    def paginated_query(self, query, params=None, page=1, page_size=100):
        """分页查询"""
        offset = (page - 1) * page_size
        limited_query = f"{query} LIMIT {page_size} OFFSET {offset}"
        return self.execute_query(limited_query, params, limit=page_size)