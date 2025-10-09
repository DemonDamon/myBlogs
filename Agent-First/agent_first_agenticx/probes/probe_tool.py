"""
Probe Query Tool - 基于 AgenticX 的 BaseTool

这是 Agent-First 的核心工具，将自然语言查询转换为智能化的数据库查询
"""

import time
from typing import Any, Dict, Optional
from agenticx import BaseTool
from .models import ProbeRequest, ProbeResponse, QueryStage, PrecisionLevel


class ProbeQueryTool(BaseTool):
    """
    Probe 查询工具
    
    基于 AgenticX 的 BaseTool，支持：
    - 自然语言查询
    - 查询阶段感知
    - 动态精度控制
    - 语义缓存
    """
    
    name: str = "probe_query"
    description: str = """
    执行智能化的数据库查询，理解查询意图和阶段。
    
    参数：
    - natural_query: 自然语言查询描述
    - stage: 查询阶段 (metadata_exploration/solution_formulation/full_validation)
    - precision: 精度要求 (approximate/sample/exact)
    - context: 查询上下文
    """
    
    def __init__(
        self,
        database_connector=None,
        memory_store=None,
        llm_provider=None
    ):
        """
        初始化 Probe Tool
        
        Args:
            database_connector: 数据库连接器
            memory_store: AgenticMemoryStore（用于缓存）
            llm_provider: LLM（用于解析自然语言）
        """
        super().__init__()
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
        异步执行 Probe 查询（AgenticX BaseTool 要求的方法）
        
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
            
            # 2. 解析查询意图（如果有 LLM）
            if self.llm_provider and not probe_request.sql_query:
                probe_request = await self._parse_query_intent(probe_request)
            
            # 3. 根据阶段优化查询
            probe_request = self._optimize_for_stage(probe_request)
            
            # 4. 执行查询
            response = await self._execute_query(probe_request)
            
            # 5. 生成建议
            response = self._generate_suggestions(response, probe_request)
            
            # 6. 缓存结果
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
        """
        同步执行 Probe 查询（AgenticX BaseTool 要求的方法）
        
        调用异步版本 aexecute
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.aexecute(**kwargs))
    
    async def _check_semantic_cache(self, request: ProbeRequest) -> Optional[ProbeResponse]:
        """检查语义缓存（利用 80-90% 的查询冗余）"""
        if not self.memory_store:
            return None
        
        # 使用 AgenticMemoryStore 的语义搜索
        similar_queries = await self.memory_store.find_similar_probes(
            request.natural_query,
            threshold=0.8
        )
        
        if similar_queries:
            # 返回最相似的缓存结果
            return similar_queries[0]
        
        return None
    
    async def _parse_query_intent(self, request: ProbeRequest) -> ProbeRequest:
        """使用 LLM 解析查询意图"""
        if not self.llm_provider:
            return request
        
        prompt = f"""
        分析以下自然语言查询，生成对应的 SQL 语句：
        
        查询: {request.natural_query}
        上下文: {request.context}
        精度要求: {request.precision.value}
        
        只返回 SQL 语句，不要有其他说明。
        """
        
        try:
            response = await self.llm_provider.ainvoke(prompt)
            request.sql_query = self._extract_sql(response.content)
        except Exception as e:
            # LLM 失败时使用简单的规则
            request.sql_query = self._generate_simple_sql(request.natural_query)
        
        return request
    
    def _extract_sql(self, llm_response: str) -> str:
        """从 LLM 响应中提取 SQL"""
        import re
        
        # 提取代码块中的 SQL
        sql_match = re.search(r'```sql\n(.*?)\n```', llm_response, re.DOTALL)
        if sql_match:
            return sql_match.group(1).strip()
        
        # 提取普通代码块
        code_match = re.search(r'```\n(.*?)\n```', llm_response, re.DOTALL)
        if code_match:
            return code_match.group(1).strip()
        
        return llm_response.strip()
    
    def _generate_simple_sql(self, natural_query: str) -> str:
        """生成简单的 SQL（fallback）"""
        # 简化实现，实际应该更复杂
        return f"SELECT * FROM table WHERE condition LIMIT 10 -- {natural_query}"
    
    def _optimize_for_stage(self, request: ProbeRequest) -> ProbeRequest:
        """根据查询阶段优化请求"""
        if request.stage == QueryStage.METADATA_EXPLORATION:
            # 元数据探索：快速、近似
            request.terminate_early = True
            request.max_rows = request.max_rows or 10
            if request.precision == PrecisionLevel.EXACT:
                request.precision = PrecisionLevel.SAMPLE
        
        elif request.stage == QueryStage.SOLUTION_FORMULATION:
            # 解决方案制定：平衡速度和准确性
            request.max_rows = request.max_rows or 100
            if request.precision == PrecisionLevel.EXACT:
                request.precision = PrecisionLevel.APPROXIMATE
        
        # FULL_VALIDATION 保持原样
        
        return request
    
    async def _execute_query(self, request: ProbeRequest) -> ProbeResponse:
        """执行查询"""
        if self.database:
            return await self._execute_with_database(request)
        else:
            # 没有数据库连接时，返回模拟结果
            return self._mock_execution(request)
    
    async def _execute_with_database(self, request: ProbeRequest) -> ProbeResponse:
        """使用数据库连接执行查询"""
        try:
            result = await self.database.execute(request.sql_query)
            
            return ProbeResponse(
                request_id=request.request_id,
                success=True,
                data=result.get("data", []),
                executed_sql=request.sql_query,
                rows_returned=result.get("rows_returned", 0),
                rows_scanned=result.get("rows_scanned", 0),
                actual_precision=request.precision
            )
        except Exception as e:
            return ProbeResponse(
                request_id=request.request_id,
                success=False,
                error=str(e),
                error_type=type(e).__name__
            )
    
    def _mock_execution(self, request: ProbeRequest) -> ProbeResponse:
        """模拟执行（用于演示）"""
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
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            return [
                "查询超时，建议：",
                "1. 增加超时时间",
                "2. 使用近似查询（approximate）",
                "3. 添加更多过滤条件"
            ]
        elif "syntax" in error_str:
            return [
                "SQL 语法错误，建议：",
                "1. 使用元数据探索了解数据结构",
                "2. 简化查询语句"
            ]
        else:
            return ["查询执行失败，请检查查询语句和数据库连接"]
    
    async def _cache_result(self, request: ProbeRequest, response: ProbeResponse):
        """缓存查询结果到 AgenticMemoryStore"""
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

