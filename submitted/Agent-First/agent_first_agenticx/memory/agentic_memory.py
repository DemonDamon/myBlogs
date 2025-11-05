"""
Agentic Memory Store - 扩展 AgenticX 的 SemanticMemory

添加 Probe 查询缓存和冗余检测功能
"""

from typing import Any, Dict, List, Optional
from agenticx.memory import SemanticMemory, SearchResult


class AgenticMemoryStore(SemanticMemory):
    """
    扩展语义记忆，专为 Agent-First 设计
    
    新增功能：
    - Probe 查询结果缓存
    - 语义相似查询检测（利用 80-90% 冗余）
    - 跨查询计算共享
    """
    
    def __init__(self, tenant_id: str, agent_id: str, **kwargs):
        super().__init__(tenant_id, agent_id, **kwargs)
        self.probe_cache_count = 0
        self.cache_hit_count = 0
    
    async def cache_probe_result(
        self,
        probe_request: Dict[str, Any],
        probe_response: Dict[str, Any]
    ) -> str:
        """
        缓存 Probe 查询结果
        
        Args:
            probe_request: Probe 请求
            probe_response: Probe 响应
            
        Returns:
            str: 记录 ID
        """
        # 使用 SemanticMemory 的 add_knowledge 方法
        record_id = await self.add_knowledge(
            content=probe_request["natural_query"],
            knowledge_type="probe_result",
            category="query_cache",
            metadata={
                # 请求信息
                "sql_query": probe_request.get("sql_query"),
                "stage": probe_request.get("stage"),
                "precision": probe_request.get("precision"),
                "context": probe_request.get("context"),
                
                # 响应信息
                "success": probe_response.get("success"),
                "execution_time": probe_response.get("execution_time"),
                "rows_returned": probe_response.get("rows_returned"),
                "confidence": probe_response.get("confidence"),
                
                # 完整数据（可选，根据数据大小决定）
                "response_data": probe_response.get("data", [])[:10]  # 只缓存前10条
            }
        )
        
        self.probe_cache_count += 1
        return record_id
    
    async def find_similar_probes(
        self,
        natural_query: str,
        threshold: float = 0.8,
        limit: int = 5
    ) -> List[SearchResult]:
        """
        查找相似的 Probe 查询（利用语义相似度）
        
        这是 Agent-First 的核心优化：识别 80-90% 的查询冗余
        
        Args:
            natural_query: 自然语言查询
            threshold: 相似度阈值
            limit: 最大返回数量
            
        Returns:
            List[SearchResult]: 相似查询列表
        """
        # 使用 SemanticMemory 的 search 方法
        results = await self.search(
            query=natural_query,
            limit=limit,
            metadata_filter={"knowledge_type": "probe_result"},
            min_score=threshold
        )
        
        if results:
            self.cache_hit_count += 1
        
        return results
    
    async def get_query_statistics(self) -> Dict[str, Any]:
        """
        获取查询统计信息
        
        Returns:
            Dict: 统计信息
        """
        return {
            "total_cached_queries": self.probe_cache_count,
            "cache_hits": self.cache_hit_count,
            "cache_hit_rate": (
                self.cache_hit_count / self.probe_cache_count 
                if self.probe_cache_count > 0 else 0
            ),
            "estimated_redundancy": f"{(self.cache_hit_count / self.probe_cache_count * 100):.1f}%"
                if self.probe_cache_count > 0 else "0%"
        }
    
    async def find_related_tables(
        self,
        natural_query: str,
        limit: int = 5
    ) -> List[str]:
        """
        根据查询找出相关表
        
        利用 SemanticMemory 的概念提取和关系映射
        """
        # 搜索相关的概念
        concepts = await self.search_concepts(
            query=natural_query,
            limit=limit
        )
        
        # 提取表名
        tables = []
        for concept, _ in concepts:
            if concept.category == "table":
                tables.append(concept.name)
        
        return tables

