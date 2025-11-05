"""
Field Agent - 查询执行者（基于 AgenticX Agent）
"""

from agenticx import Agent


def create_field_agent(
    llm=None,
    organization_id: str = "default",
    **kwargs
) -> Agent:
    """
    创建 Field Agent (查询执行者)
    
    Field Agent 负责：
    - 解析 Probe 请求
    - 生成 SQL 查询
    - 执行查询
    - 返回结果
    
    Args:
        llm: LLM 配置
        organization_id: 组织 ID
        **kwargs: 其他参数
        
    Returns:
        Agent: 配置好的 Field Agent
    """
    return Agent(
        name="FieldAgent",
        role="query_executor",
        goal="解析和执行 Probe 查询，将自然语言转换为SQL并执行",
        backstory="""
        我是 Field Agent，专门负责执行数据库查询。
        
        我的职责：
        1. 理解自然语言查询意图
        2. 将查询转换为优化的 SQL
        3. 根据查询阶段选择执行策略
        4. 执行查询并返回结果
        5. 分析结果质量和完整性
        
        我追求高效和准确，会根据查询阶段动态调整执行策略：
        - 元数据探索：快速返回结构信息
        - 解决方案制定：平衡速度和准确性
        - 完整验证：提供精确的完整结果
        """,
        llm=llm,
        organization_id=organization_id,
        tool_names=["probe_query"],
        **kwargs
    )

