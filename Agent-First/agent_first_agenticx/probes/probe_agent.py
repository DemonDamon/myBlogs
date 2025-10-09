"""
创建专门的 Probe Agent
"""

from agenticx import Agent


def create_probe_agent(
    llm=None,
    organization_id: str = "default",
    **kwargs
) -> Agent:
    """
    创建 Probe Agent
    
    Args:
        llm: LLM 配置
        organization_id: 组织 ID
        **kwargs: 其他参数
        
    Returns:
        Agent: 配置好的 Probe Agent
    """
    return Agent(
        name="ProbeAgent",
        role="database_query_agent",
        goal="执行智能化的数据库查询，理解查询意图、阶段和精度需求",
        backstory="""
        我是专门为 AI Agent 设计的数据库查询智能体。
        我理解自然语言查询意图，能够根据查询阶段（元数据探索/解决方案制定/完整验证）
        选择合适的执行策略，并提供优化建议。
        
        我的特点：
        - 理解查询语义和意图
        - 感知查询阶段，动态调整精度
        - 利用语义缓存，识别 80-90% 的查询冗余
        - 主动提供优化建议和相关推荐
        """,
        llm=llm,
        organization_id=organization_id,
        tool_names=["probe_query"],  # 使用 ProbeQueryTool
        **kwargs
    )

