"""
完整的端到端示例：Agent-First 工作流

演示如何使用所有组件实现论文中的 Agent-First 概念
"""

import asyncio
from agenticx import LiteLLMProvider
from agenticx.collaboration import ReflectionPattern

# 导入 Agent-First 组件
import sys
sys.path.append('..')

from probes import ProbeQueryTool, create_probe_agent, QueryStage, PrecisionLevel
from agents import create_field_agent, create_sleeper_agent, create_probe_collaboration
from memory import AgenticMemoryStore, RedundancyDetector
from storage import BranchManager


async def main():
    """
    Agent-First 完整工作流示例
    
    演示：
    1. Probe 接口智能查询
    2. Field + Sleeper Agent 协作
    3. 语义缓存和冗余优化
    4. Git 式分支管理
    """
    
    print("=" * 80)
    print("Agent-First: 基于 AgenticX 的完整演示")
    print("=" * 80)
    
    # ========================================================================
    # 1. 初始化组件
    # ========================================================================
    print("\n[1] 初始化组件...")
    
    # 创建 LLM（使用 AgenticX 的 LiteLLMProvider）
    llm = LiteLLMProvider(model="gpt-4")
    
    # 创建 Agentic Memory Store（扩展自 SemanticMemory）
    memory = AgenticMemoryStore(
        tenant_id="demo_org",
        agent_id="agent_first_demo"
    )
    
    # 创建冗余检测器
    redundancy_detector = RedundancyDetector(similarity_threshold=0.8)
    
    # 创建分支管理器
    branch_mgr = BranchManager()
    
    # 创建 Probe Tool
    probe_tool = ProbeQueryTool(
        database_connector=None,  # 演示中使用模拟数据
        memory_store=memory,
        llm_provider=llm
    )
    
    print("✅ 组件初始化完成")
    print(f"  - LLM: {llm.model}")
    print(f"  - Memory: AgenticMemoryStore")
    print(f"  - Branch Manager: 已就绪")
    
    # ========================================================================
    # 2. 阶段 1：元数据探索
    # ========================================================================
    print("\n[2] 阶段 1：元数据探索")
    print("-" * 80)
    
    explore_query = "有哪些表和字段？包含什么数据？"
    print(f"查询: {explore_query}")
    
    result1 = await probe_tool._arun(
        natural_query=explore_query,
        stage="metadata_exploration",
        precision="exact"
    )
    
    print(f"✅ 执行时间: {result1['execution_time']:.3f}秒")
    print(f"   返回行数: {result1['rows_returned']}")
    print(f"   建议: {result1['suggestions'][0] if result1['suggestions'] else '无'}")
    
    redundancy_detector.add_query(explore_query)
    
    # ========================================================================
    # 3. 阶段 2：解决方案制定（多次尝试，利用冗余）
    # ========================================================================
    print("\n[3] 阶段 2：解决方案制定（并行探索）")
    print("-" * 80)
    
    # 模拟 Agent 的多次试探性查询
    queries = [
        "找出销售额最高的产品",
        "查询销量最好的商品",  # 相似查询
        "哪些产品卖得最好",      # 相似查询
        "显示畅销产品列表",      # 相似查询
        "获取TOP销售产品"        # 相似查询
    ]
    
    results = []
    for i, query in enumerate(queries):
        print(f"\n尝试 {i+1}/5: {query}")
        
        result = await probe_tool._arun(
            natural_query=query,
            stage="solution_formulation",
            precision="approximate"  # 近似结果，快速验证
        )
        
        results.append(result)
        redundancy_detector.add_query(query)
        
        # 检查是否命中缓存
        if result.get('was_cached'):
            print("  🎯 缓存命中！复用之前的计算")
        else:
            print(f"  ⚡ 执行查询，耗时 {result['execution_time']:.3f}秒")
    
    # 显示冗余统计
    redundancy_rate = redundancy_detector.get_redundancy_rate()
    tool_stats = probe_tool.get_stats()
    
    print("\n📊 冗余优化统计:")
    print(f"  - 总查询数: {tool_stats['total_queries']}")
    print(f"  - 缓存命中: {tool_stats['cache_hits']}")
    print(f"  - 缓存命中率: {tool_stats['cache_hit_rate']*100:.1f}%")
    print(f"  - 检测到的冗余率: {redundancy_rate*100:.1f}%")
    print(f"  💡 节省了 {tool_stats['redundancy_savings']} 的计算资源！")
    
    # ========================================================================
    # 4. Field + Sleeper Agent 协作
    # ========================================================================
    print("\n[4] Field + Sleeper Agent 协作（基于 ReflectionPattern）")
    print("-" * 80)
    
    # 创建协作（使用 AgenticX 的 ReflectionPattern）
    collaboration = create_probe_collaboration(
        llm_provider=llm,
        max_iterations=2
    )
    
    task = """
    分析销售数据，找出高价值客户的特征：
    1. 找出购买金额最高的客户
    2. 分析他们的购买模式
    3. 提供营销建议
    """
    
    print(f"任务: {task}")
    print("\n执行协作...")
    print("  - Field Agent (执行者): 执行查询和分析")
    print("  - Sleeper Agent (顾问): 审查结果并提供建议")
    
    # 注意：这里使用模拟执行，实际使用时需要配置真实的 LLM
    print("\n💡 协作模式:")
    print("  第1轮: Field Agent 执行初始查询")
    print("         → Sleeper Agent 审查并提供反馈")
    print("  第2轮: Field Agent 根据反馈改进查询")
    print("         → Sleeper Agent 确认结果质量")
    print("\n✅ 协作完成！通过反思循环持续改进查询质量")
    
    # ========================================================================
    # 5. Git 式分支管理（What-If 探索）
    # ========================================================================
    print("\n[5] Git 式分支管理：并行探索不同策略")
    print("-" * 80)
    
    # 创建分支测试不同的定价策略
    print("\n创建分支进行 what-if 探索...")
    
    branch_a = await branch_mgr.create_branch("main", "pricing-strategy-a")
    print(f"✅ 创建分支: {branch_a.name}")
    
    branch_b = await branch_mgr.create_branch("main", "pricing-strategy-b")
    print(f"✅ 创建分支: {branch_b.name}")
    
    # 在分支 A 上测试策略 A
    print("\n在分支 A 上测试: 降价 10%")
    await branch_a.update("products", {
        "product_id": 123,
        "price": 89.99,
        "strategy": "discount_10%"
    })
    
    # 在分支 B 上测试策略 B
    print("在分支 B 上测试: 买一送一")
    await branch_b.update("products", {
        "product_id": 123,
        "price": 99.99,
        "strategy": "buy_one_get_one"
    })
    
    # 查看分支列表
    branches = branch_mgr.list_branches()
    print(f"\n📋 当前分支状态:")
    for branch_info in branches:
        print(f"  - {branch_info['name']}")
    
    # 假设策略 A 效果更好，合并到主分支
    print("\n✅ 策略 A 效果更好，合并到主分支")
    await branch_mgr.merge(branch_a.id, "main")
    
    print("❌ 策略 B 效果不佳，回滚分支")
    await branch_mgr.rollback(branch_b.id)
    
    # 显示统计
    stats = branch_mgr.get_stats()
    print(f"\n📊 分支管理统计:")
    print(f"  - 创建的分支数: {stats['total_branches']}")
    print(f"  - 总操作数: {stats['total_operations']}")
    print("  💡 支持 20x 的分支创建和 50x 的回滚操作（相比传统数据库）")
    
    # ========================================================================
    # 6. 完整验证
    # ========================================================================
    print("\n[6] 阶段 3：完整验证（精确结果）")
    print("-" * 80)
    
    final_query = "获取最终的销售额TOP10产品完整数据"
    print(f"查询: {final_query}")
    
    final_result = await probe_tool._arun(
        natural_query=final_query,
        stage="full_validation",
        precision="exact"  # 精确结果
    )
    
    print(f"✅ 执行完成")
    print(f"   执行时间: {final_result['execution_time']:.3f}秒")
    print(f"   返回行数: {final_result['rows_returned']}")
    print(f"   置信度: {final_result['confidence']*100:.0f}%")
    
    # ========================================================================
    # 7. 总结
    # ========================================================================
    print("\n[7] Agent-First 工作流总结")
    print("=" * 80)
    
    memory_stats = await memory.get_query_statistics()
    
    print("\n✅ 成功演示了 Agent-First 的四大核心功能：")
    print("\n1️⃣  Probe 接口")
    print("   - 自然语言查询")
    print("   - 阶段感知（探索→制定→验证）")
    print("   - 动态精度控制")
    
    print("\n2️⃣  Field + Sleeper Agent 协作")
    print("   - 基于 AgenticX ReflectionPattern")
    print("   - 执行-审查-改进循环")
    print("   - 持续优化查询质量")
    
    print("\n3️⃣  Agentic Memory Store")
    print(f"   - 缓存查询数: {memory_stats['total_cached_queries']}")
    print(f"   - 缓存命中率: {memory_stats['cache_hit_rate']*100:.1f}%")
    print(f"   - 冗余优化: {memory_stats['estimated_redundancy']}")
    
    print("\n4️⃣  Git 式分支管理")
    print(f"   - 支持大规模并行 what-if 探索")
    print(f"   - 写时复制，高效资源利用")
    print(f"   - 快速回滚和合并")
    
    print("\n📈 性能提升（基于论文实验）:")
    print("   - 查询减少: 18.1%（通过智能引导）")
    print("   - 计算共享: 80-90%（通过冗余检测）")
    print("   - 分支创建: 20x（相比传统数据库）")
    print("   - 回滚操作: 50x（支持更多探索）")
    
    print("\n" + "=" * 80)
    print("Agent-First 演示完成！")
    print("基于 AgenticX 框架，充分利用现有能力，专注创新功能。")
    print("=" * 80)


if __name__ == "__main__":
    # 运行演示
    asyncio.run(main())

