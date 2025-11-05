"""
写时复制（Copy-On-Write）引擎
"""

from typing import Any, Dict
import copy


class CopyOnWriteEngine:
    """
    写时复制引擎
    
    用于高效创建数据分支，只在写入时才真正复制数据
    """
    
    def __init__(self):
        self.reference_counts = {}
    
    async def copy_on_write(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        写时复制
        
        Args:
            data: 原始数据
            
        Returns:
            Dict: 数据引用（浅拷贝）
        """
        # 简化实现：创建浅拷贝
        # 实际应该实现真正的 COW 机制
        return {k: v for k, v in data.items()}
    
    def materialize(self, data_ref: Any) -> Any:
        """实例化数据（当需要修改时）"""
        return copy.deepcopy(data_ref)

