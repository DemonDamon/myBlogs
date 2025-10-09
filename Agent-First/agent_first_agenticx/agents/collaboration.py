"""
Field + Sleeper Agent 协作 - 基于 AgenticX ReflectionPattern
"""

from agenticx.collaboration import ReflectionPattern
from .field_agent import create_field_agent
from .sleeper_agent import create_sleeper_agent


def create_probe_collaboration(
    llm_provider,
    organization_id: str = "default",
    max_iterations: int = 3,
    **kwargs
):
    """
    创建 Field + Sleeper Agent 协作
    
    使用 AgenticX 的 ReflectionPattern 实现：
    - Field Agent 作为执行者（executor）
    - Sleeper Agent 作为审查者（reviewer）
    - 通过反思循环不断改进查询
    
    Args:
        llm_provider: LLM 提供者
        organization_id: 组织 ID
        max_iterations: 最大反思迭代次数
        **kwargs: 其他参数
        
    Returns:
        ReflectionPattern: 配置好的协作模式
    """
    # 创建 Field Agent (执行者)
    field_agent = create_field_agent(
        llm=llm_provider,
        organization_id=organization_id
    )
    
    # 创建 Sleeper Agent (审查者)
    sleeper_agent = create_sleeper_agent(
        llm=llm_provider,
        organization_id=organization_id
    )
    
    # 使用 AgenticX 的 ReflectionPattern
    collaboration = ReflectionPattern(
        executor_agent=field_agent,
        reviewer_agent=sleeper_agent,
        llm_provider=llm_provider,
        config={
            "max_iterations": max_iterations,
            "mode": "reflection"
        },
        **kwargs
    )
    
    return collaboration


def execute_probe_with_reflection(
    collaboration: ReflectionPattern,
    natural_query: str,
    stage: str = "full_validation",
    precision: str = "exact",
    context: str = ""
):
    """
    使用 Reflection 模式执行 Probe 查询
    
    工作流程：
    1. Field Agent 执行初始查询
    2. Sleeper Agent 审查结果并提供反馈
    3. Field Agent 根据反馈改进查询
    4. 重复 2-3 直到满意或达到最大迭代次数
    
    Args:
        collaboration: ReflectionPattern 实例
        natural_query: 自然语言查询
        stage: 查询阶段
        precision: 精度级别
        context: 查询上下文
        
    Returns:
        CollaborationResult: 协作结果
    """
    task_description = f"""
    执行以下 Probe 查询：
    
    查询: {natural_query}
    阶段: {stage}
    精度: {precision}
    上下文: {context}
    
    请：
    1. 分析查询意图
    2. 生成优化的 SQL
    3. 执行查询
    4. 返回结果
    5. 根据反馈不断改进
    """
    
    # 执行协作
    result = collaboration.execute(task=task_description)
    
    return result

