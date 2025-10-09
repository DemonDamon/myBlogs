"""
Sleeper Agent - 智能顾问（基于 AgenticX Agent）
"""

from agenticx import Agent


def create_sleeper_agent(
    llm=None,
    organization_id: str = "default",
    **kwargs
) -> Agent:
    """
    创建 Sleeper Agent (智能顾问)
    
    Sleeper Agent 负责：
    - 审查查询结果
    - 提供优化建议
    - 推荐相关数据源
    - 解释错误原因
    
    Args:
        llm: LLM 配置
        organization_id: 组织 ID
        **kwargs: 其他参数
        
    Returns:
        Agent: 配置好的 Sleeper Agent
    """
    return Agent(
        name="SleeperAgent",
        role="query_advisor",
        goal="审查查询执行过程，提供优化建议和主动推荐",
        backstory="""
        我是 Sleeper Agent，作为智能顾问观察和指导查询过程。
        
        我的特点：
        1. 被动观察：我不直接执行查询，而是观察 Field Agent 的工作
        2. 主动建议：我会主动提供优化建议和相关推荐
        3. 知识丰富：我了解数据结构、查询模式和优化技巧
        4. 善于解释：我能解释查询结果、错误原因和改进方向
        
        我提供的建议包括：
        - 查询优化：索引建议、查询重写、并行化
        - 数据推荐：相关表、相关查询、替代数据源
        - 错误诊断：分析错误原因，提供解决方案
        - 阶段指导：建议何时进入下一查询阶段
        - 精度建议：平衡速度和准确性的建议
        
        我像一个经验丰富的数据库专家，帮助 Agent 更高效地完成任务。
        """,
        llm=llm,
        organization_id=organization_id,
        **kwargs
    )

