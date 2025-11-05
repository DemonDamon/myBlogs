"""
Probe Query Tool - 简化版本

直接使用函数，不继承复杂的 BaseTool
"""

import time
from typing import Any, Dict, Optional
from .models import ProbeRequest, ProbeResponse, QueryStage, PrecisionLevel


class ProbeQueryTool:
    """
    Probe 查询工具（简化版本）
    
    不继承 AgenticX BaseTool，直接实现功能
    """
    
    def __init__(
        self,
        database_connector=None,
        memory_store=None,
        llm_provider=None
    ):
        """初始化 Probe Tool"""
        self.name = "probe_query"
        self.description = "执行智能化的数据库查询，理解查询意图和阶段"
        self.database = database_connector
        self.memory_store = memory_store
        self.llm_provider = llm_provider
        self.query_count = 0
        self.cache_hits = 0
    
    async def aexecute(
        self,
        natural_query: str,
        stage: str = "full_validation",
        precision: str = "exact",
        context: str = "",
        **kwargs
    ) -> Dict[str, Any]:
        """
        异步执行 Probe 查询
        
        Args:
            natural_query: 自然语言查询
            stage: 查询阶段
            precision: 精度级别
            context: 查询上下文
            
        Returns:
            Dict: 查询结果
        """
        start_time = time.time()
        
        # 创建 Probe 请求
        probe_request = ProbeRequest(
            natural_query=natural_query,
            stage=QueryStage(stage),
            precision=PrecisionLevel(precision),
            context=context
        )
        
        try:
            # 1. 检查语义缓存
            if self.memory_store:
                cached = await self._check_semantic_cache(probe_request)
                if cached:
                    self.cache_hits += 1
                    cached.was_cached = True
                    cached.execution_time = time.time() - start_time
                    return cached.model_dump()
            
            # 2. 根据阶段优化查询
            probe_request = self._optimize_for_stage(probe_request)
            
            # 3. 执行查询
            response = await self._execute_query(probe_request)
            
            # 4. 生成建议
            response = self._generate_suggestions(response, probe_request)
            
            # 5. 缓存结果
            if self.memory_store and response.success:
                await self._cache_result(probe_request, response)
            
            self.query_count += 1
            response.execution_time = time.time() - start_time
            
            return response.model_dump()
            
        except Exception as e:
            # 错误处理
            execution_time = time.time() - start_time
            return ProbeResponse(
                request_id=probe_request.request_id,
                success=False,
                error=str(e),
                error_type=type(e).__name__,
                execution_time=execution_time,
                suggestions=self._generate_error_suggestions(e)
            ).model_dump()
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """同步执行"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.aexecute(**kwargs))
    
    async def _check_semantic_cache(self, request: ProbeRequest) -> Optional[ProbeResponse]:
        """检查语义缓存"""
        if not self.memory_store:
            return None
        
        similar_queries = await self.memory_store.find_similar_probes(
            request.natural_query,
            threshold=0.8
        )
        
        if similar_queries:
            return similar_queries[0]
        
        return None
    
    def _optimize_for_stage(self, request: ProbeRequest) -> ProbeRequest:
        """根据查询阶段优化请求"""
        if request.stage == QueryStage.METADATA_EXPLORATION:
            request.terminate_early = True
            request.max_rows = request.max_rows or 10
            if request.precision == PrecisionLevel.EXACT:
                request.precision = PrecisionLevel.SAMPLE
        
        elif request.stage == QueryStage.SOLUTION_FORMULATION:
            request.max_rows = request.max_rows or 100
            if request.precision == PrecisionLevel.EXACT:
                request.precision = PrecisionLevel.APPROXIMATE
        
        return request
    
    async def _execute_query(self, request: ProbeRequest) -> ProbeResponse:
        """执行查询（使用模拟数据）"""
        # 模拟数据
        mock_data = [
            {"id": 1, "name": "Product A", "sales": 150},
            {"id": 2, "name": "Product B", "sales": 200},
            {"id": 3, "name": "Product C", "sales": 100},
        ]
        
        rows = 3 if request.precision == PrecisionLevel.SAMPLE else 10
        if request.max_rows:
            rows = min(rows, request.max_rows)
        
        return ProbeResponse(
            request_id=request.request_id,
            success=True,
            data=mock_data[:rows],
            executed_sql=request.sql_query or "SELECT * FROM mock_table",
            rows_returned=len(mock_data[:rows]),
            rows_scanned=100,
            actual_precision=request.precision,
            confidence=0.95 if request.precision != PrecisionLevel.EXACT else 1.0,
            is_approximate=request.precision != PrecisionLevel.EXACT
        )
    
    def _generate_suggestions(self, response: ProbeResponse, request: ProbeRequest) -> ProbeResponse:
        """生成建议"""
        suggestions = []
        
        if request.stage == QueryStage.METADATA_EXPLORATION:
            suggestions.append("✅ 元数据探索完成，可以开始制定解决方案")
        
        elif request.stage == QueryStage.SOLUTION_FORMULATION:
            suggestions.append("💡 建议进行完整验证以获取精确结果")
        
        if request.precision != PrecisionLevel.EXACT:
            suggestions.append(f"⚠️ 当前使用{request.precision.value}精度，如需精确结果请使用 exact 精度")
        
        response.suggestions = suggestions
        return response
    
    def _generate_error_suggestions(self, error: Exception) -> list:
        """生成错误建议"""
        return ["查询执行失败，请检查查询语句和数据库连接"]
    
    async def _cache_result(self, request: ProbeRequest, response: ProbeResponse):
        """缓存查询结果"""
        if not self.memory_store:
            return
        
        await self.memory_store.cache_probe_result(
            probe_request=request.model_dump(),
            probe_response=response.model_dump()
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """获取工具统计信息"""
        return {
            "total_queries": self.query_count,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": self.cache_hits / self.query_count if self.query_count > 0 else 0,
            "redundancy_savings": f"{(self.cache_hits / self.query_count * 100):.1f}%" if self.query_count > 0 else "0%"
        }

