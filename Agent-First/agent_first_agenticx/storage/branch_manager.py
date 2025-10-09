"""
Git 式分支管理器 - 扩展 AgenticX Storage

支持大规模并行的 what-if 探索
"""

from typing import Any, Dict, Optional
from datetime import datetime
from .cow_engine import CopyOnWriteEngine


class Branch:
    """数据分支"""
    
    def __init__(self, branch_id: str, parent: Optional[str], name: str):
        self.id = branch_id
        self.parent = parent
        self.name = name
        self.created_at = datetime.now()
        self.data_snapshot = {}
        self.operations = []
    
    async def update(self, table: str, data: Dict[str, Any]):
        """在分支上更新数据"""
        if table not in self.data_snapshot:
            self.data_snapshot[table] = []
        
        self.data_snapshot[table].append(data)
        self.operations.append({
            "type": "update",
            "table": table,
            "data": data,
            "timestamp": datetime.now()
        })
    
    async def query(self, sql: str) -> Dict[str, Any]:
        """在分支上查询数据"""
        # 简化实现
        return {
            "success": True,
            "data": self.data_snapshot,
            "branch_id": self.id
        }


class BranchManager:
    """
    分支管理器
    
    支持：
    - 创建分支（写时复制）
    - 并行探索
    - 快速回滚
    - 分支合并
    """
    
    def __init__(self, storage=None):
        self.storage = storage
        self.branches = {"main": Branch("main", None, "main")}
        self.cow_engine = CopyOnWriteEngine()
        self.branch_counter = 0
    
    async def create_branch(
        self,
        parent: str = "main",
        name: Optional[str] = None
    ) -> Branch:
        """
        创建新分支（写时复制）
        
        Args:
            parent: 父分支
            name: 分支名称
            
        Returns:
            Branch: 新分支
        """
        if parent not in self.branches:
            raise ValueError(f"父分支不存在: {parent}")
        
        # 生成分支 ID
        self.branch_counter += 1
        branch_id = f"branch_{self.branch_counter}"
        branch_name = name or f"branch-{self.branch_counter}"
        
        # 创建分支（写时复制，不立即复制数据）
        new_branch = Branch(branch_id, parent, branch_name)
        
        # 复制父分支的数据引用（COW）
        parent_branch = self.branches[parent]
        new_branch.data_snapshot = await self.cow_engine.copy_on_write(
            parent_branch.data_snapshot
        )
        
        self.branches[branch_id] = new_branch
        
        return new_branch
    
    async def merge(self, source: str, target: str = "main"):
        """
        合并分支
        
        Args:
            source: 源分支
            target: 目标分支
        """
        if source not in self.branches or target not in self.branches:
            raise ValueError("分支不存在")
        
        source_branch = self.branches[source]
        target_branch = self.branches[target]
        
        # 应用源分支的所有操作到目标分支
        for operation in source_branch.operations:
            if operation["type"] == "update":
                await target_branch.update(
                    operation["table"],
                    operation["data"]
                )
    
    async def rollback(self, branch_id: str):
        """
        回滚分支
        
        Args:
            branch_id: 分支 ID
        """
        if branch_id in self.branches:
            del self.branches[branch_id]
    
    def get_branch(self, branch_id: str) -> Optional[Branch]:
        """获取分支"""
        return self.branches.get(branch_id)
    
    def list_branches(self) -> list:
        """列出所有分支"""
        return [
            {
                "id": branch.id,
                "name": branch.name,
                "parent": branch.parent,
                "created_at": branch.created_at
            }
            for branch in self.branches.values()
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_branches": len(self.branches),
            "active_branches": len([b for b in self.branches.values() if b.parent]),
            "total_operations": sum(len(b.operations) for b in self.branches.values())
        }

