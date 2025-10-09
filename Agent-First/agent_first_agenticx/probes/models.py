"""
Probe 数据模型
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class QueryStage(str, Enum):
    """查询阶段"""
    METADATA_EXPLORATION = "metadata_exploration"
    SOLUTION_FORMULATION = "solution_formulation"
    FULL_VALIDATION = "full_validation"


class PrecisionLevel(str, Enum):
    """精度级别"""
    APPROXIMATE = "approximate"
    SAMPLE = "sample"
    EXACT = "exact"


class QueryIntent(str, Enum):
    """查询意图"""
    EXPLORE_SCHEMA = "explore_schema"
    FIND_DATA = "find_data"
    AGGREGATE = "aggregate"
    JOIN = "join"
    TRANSFORM = "transform"
    VALIDATE = "validate"


class ProbeRequest(BaseModel):
    """
    Probe 请求
    
    与传统 SQL 不同，Probe 包含丰富的语义信息
    """
    # 核心查询
    natural_query: str = Field(description="自然语言查询")
    sql_query: Optional[str] = Field(default=None, description="SQL 查询（可选）")
    
    # 语义信息
    intent: Optional[QueryIntent] = Field(default=None, description="查询意图")
    stage: QueryStage = Field(default=QueryStage.FULL_VALIDATION, description="查询阶段")
    context: str = Field(default="", description="上下文描述")
    
    # 执行控制
    precision: PrecisionLevel = Field(default=PrecisionLevel.EXACT, description="精度要求")
    timeout: Optional[float] = Field(default=None, description="超时时间（秒）")
    terminate_early: bool = Field(default=False, description="是否允许提前终止")
    max_rows: Optional[int] = Field(default=None, description="最大返回行数")
    
    # 优化提示
    similar_queries: List[str] = Field(default_factory=list, description="相似查询")
    expected_cost: Optional[float] = Field(default=None, description="预期成本")
    
    # 元数据
    request_id: str = Field(default_factory=lambda: f"probe_{datetime.now().timestamp()}")
    agent_id: Optional[str] = Field(default=None, description="Agent ID")
    task_id: Optional[str] = Field(default=None, description="Task ID")


class ProbeResponse(BaseModel):
    """
    Probe 响应
    
    包含查询结果和丰富的元数据
    """
    # 核心结果
    request_id: str = Field(description="对应的请求 ID")
    success: bool = Field(description="是否成功")
    data: Optional[List[Dict[str, Any]]] = Field(default=None, description="查询结果数据")
    
    # 执行信息
    executed_sql: Optional[str] = Field(default=None, description="实际执行的 SQL")
    execution_time: float = Field(default=0.0, description="执行时间（秒）")
    rows_returned: int = Field(default=0, description="返回行数")
    rows_scanned: int = Field(default=0, description="扫描行数")
    
    # 精度和质量
    actual_precision: PrecisionLevel = Field(default=PrecisionLevel.EXACT)
    confidence: float = Field(default=1.0, description="置信度")
    is_approximate: bool = Field(default=False, description="是否近似结果")
    was_cached: bool = Field(default=False, description="是否来自缓存")
    
    # 错误信息
    error: Optional[str] = Field(default=None, description="错误信息")
    error_type: Optional[str] = Field(default=None, description="错误类型")
    
    # 建议和提示
    suggestions: List[str] = Field(default_factory=list, description="系统建议")
    related_tables: List[str] = Field(default_factory=list, description="相关表")
    related_queries: List[str] = Field(default_factory=list, description="相关查询")
    
    # 成本信息
    estimated_cost: float = Field(default=0.0, description="估计成本")
    actual_cost: float = Field(default=0.0, description="实际成本")
    
    # 元数据
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

