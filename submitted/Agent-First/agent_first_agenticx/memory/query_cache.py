"""
查询缓存管理
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta


class QueryCache:
    """简单的查询缓存管理器"""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache = {}
        self.ttl = timedelta(seconds=ttl_seconds)
    
    def set(self, key: str, value: Any, metadata: Optional[Dict] = None):
        """设置缓存"""
        self.cache[key] = {
            "value": value,
            "metadata": metadata or {},
            "created_at": datetime.now()
        }
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if datetime.now() - entry["created_at"] > self.ttl:
            del self.cache[key]
            return None
        
        return entry["value"]
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()

