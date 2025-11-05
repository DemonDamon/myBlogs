#!/usr/bin/env python3
"""
Agent-First Demo 演示程序

直接运行，无需安装！

使用方法：
    python demo.py
"""

import sys
import asyncio
from pathlib import Path

# 添加 AgenticX 到路径
agenticx_path = Path("/Users/damon/myWork/AgenticX")
if agenticx_path.exists():
    sys.path.insert(0, str(agenticx_path))

# 导入 AgenticX
try:
    from agenticx import Agent, Task
    from agenticx.llms import LiteLLMProvider
    from agenticx.collaboration import ReflectionPattern
    print("✅ AgenticX 导入成功")
except ImportError as e:
    print(f"❌ 无法导入 AgenticX: {e}")
    print("请确保 AgenticX 已安装或路径正确")
    sys.exit(1)

# 导入本地模块
from probes.models import ProbeRequest, QueryStage, PrecisionLevel
from probes.probe_tool_simple import ProbeQueryTool  # 使用简化版本
from probes.probe_agent import create_probe_agent
from agents.field_agent import create_field_agent
from agents.sleeper_agent import create_sleeper_agent
from memory.agentic_memory import AgenticMemoryStore
from memory.redundancy import RedundancyDetector
from storage.branch_manager import BranchManager


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_subsection(title: str):
    """打印小节标题"""
    print(f"\n{title}")
    print("-" * 80)


async def demo_basic_probe():
    """演示 1: 基础 Probe 查询"""
    print_section("演示 1: Probe 接口 - 智能化数据库查询")
    
    # 创建 Probe Tool（不需要真实数据库）
    probe_tool = ProbeQueryTool(
        database_connector=None,  # 使用模拟数据
        memory_store=None,
        llm_provider=None
    )
    
    # 1. 元数据探索
    print_subsection("阶段 1: 元数据探索")
    result1 = await probe_tool.aexecute(
        natural_query="有哪些表和字段？",
        stage="metadata_exploration",
        precision="exact"
    )
    print(f"✅ 查询: {result1['request_id']}")
    print(f"   耗时: {result1['execution_time']:.3f}秒")
    print(f"   返回: {result1['rows_returned']}行")
    print(f"   建议: {result1['suggestions'][0] if result1['suggestions'] else '无'}")
    
    # 2. 解决方案制定（近似查询）
    print_subsection("阶段 2: 解决方案制定（近似查询，快速验证）")
    result2 = await probe_tool.aexecute(
        natural_query="找出销售额最高的前10个产品",
        stage="solution_formulation",
        precision="approximate"
    )
    print(f"✅ 查询: {result2['request_id']}")
    print(f"   耗时: {result2['execution_time']:.3f}秒")
    print(f"   精度: {result2['actual_precision']} (近似结果)")
    print(f"   置信度: {result2['confidence']*100:.0f}%")
    
    # 3. 完整验证（精确查询）
    print_subsection("阶段 3: 完整验证（精确查询）")
    result3 = await probe_tool.aexecute(
        natural_query="获取最终的TOP10产品完整数据",
        stage="full_validation",
        precision="exact"
    )
    print(f"✅ 查询: {result3['request_id']}")
    print(f"   耗时: {result3['execution_time']:.3f}秒")
    print(f"   精度: {result3['actual_precision']} (精确结果)")
    print(f"   返回数据: {len(result3['data'])}条记录")


async def demo_memory_caching():
    """演示 2: 语义缓存和冗余优化"""
    print_section("演示 2: Agentic Memory Store - 语义缓存（80-90%冗余优化）")
    
    # 创建 Memory Store
    memory = AgenticMemoryStore(
        tenant_id="demo_org",
        agent_id="demo_agent"
    )
    
    # 创建 Probe Tool（带缓存）
    probe_tool = ProbeQueryTool(
        database_connector=None,
        memory_store=memory,
        llm_provider=None
    )
    
    # 创建冗余检测器
    redundancy = RedundancyDetector(similarity_threshold=0.8)
    
    # 模拟 Agent 的多次相似查询（80-90%冗余）
    queries = [
        "找出销售额最高的产品",
        "查询销量最好的商品",    # 相似
        "哪些产品卖得最好",       # 相似
        "显示畅销产品列表",       # 相似
        "获取TOP销售产品"         # 相似
    ]
    
    print_subsection("执行 5 次相似查询...")
    
    for i, query in enumerate(queries, 1):
        print(f"\n查询 {i}/5: {query}")
        
        result = await probe_tool.aexecute(
            natural_query=query,
            stage="solution_formulation",
            precision="approximate"
        )
        
        redundancy.add_query(query)
        
        if result.get('was_cached'):
            print("  🎯 缓存命中！直接复用之前的计算")
        else:
            print(f"  ⚡ 新查询，耗时 {result['execution_time']:.3f}秒")
    
    # 统计
    stats = probe_tool.get_stats()
    redundancy_rate = redundancy.get_redundancy_rate()
    
    print_subsection("统计结果")
    print(f"📊 总查询数: {stats['total_queries']}")
    print(f"📊 缓存命中: {stats['cache_hits']}")
    print(f"📊 缓存命中率: {stats['cache_hit_rate']*100:.1f}%")
    print(f"📊 检测到的冗余: {redundancy_rate*100:.1f}%")
    print(f"\n💡 节省了 {stats['redundancy_savings']} 的计算资源！")
    print("   （论文实验显示 Agent 查询有 80-90% 的冗余）")


async def demo_branching():
    """演示 3: Git 式分支管理"""
    print_section("演示 3: Git 式分支管理 - 并行 What-If 探索")
    
    # 创建分支管理器
    branch_mgr = BranchManager()
    
    print_subsection("场景: 测试不同的定价策略")
    
    # 创建分支 A
    print("\n1. 创建分支 A: 降价 10%")
    branch_a = await branch_mgr.create_branch("main", "pricing-discount-10")
    print(f"   ✅ 分支创建: {branch_a.name}")
    
    await branch_a.update("products", {
        "product_id": 123,
        "price": 89.99,
        "strategy": "discount_10%"
    })
    print("   ✅ 应用策略: 价格 $99.99 → $89.99")
    
    # 创建分支 B
    print("\n2. 创建分支 B: 买一送一")
    branch_b = await branch_mgr.create_branch("main", "pricing-bogo")
    print(f"   ✅ 分支创建: {branch_b.name}")
    
    await branch_b.update("products", {
        "product_id": 123,
        "price": 99.99,
        "strategy": "buy_one_get_one"
    })
    print("   ✅ 应用策略: 保持价格，买一送一")
    
    # 列出所有分支
    print_subsection("当前分支状态")
    branches = branch_mgr.list_branches()
    for branch_info in branches:
        print(f"  📁 {branch_info['name']}")
        if branch_info['parent']:
            print(f"     └─ 父分支: {branch_info['parent']}")
    
    # 测试结果
    print_subsection("测试结果")
    print("✅ 分支 A (降价10%): 销售额增长 25%")
    print("❌ 分支 B (买一送一): 销售额增长 8%，但利润下降")
    
    # 合并最佳方案
    print_subsection("决策")
    print("✅ 合并分支 A 到主分支")
    await branch_mgr.merge(branch_a.id, "main")
    
    print("❌ 回滚分支 B")
    await branch_mgr.rollback(branch_b.id)
    
    # 统计
    stats = branch_mgr.get_stats()
    print_subsection("统计")
    print(f"📊 创建的分支: {stats['total_branches']}")
    print(f"📊 总操作数: {stats['total_operations']}")
    print(f"\n💡 支持 20x 的分支创建和 50x 的回滚操作")
    print("   （相比传统数据库）")


def demo_agent_collaboration():
    """演示 4: Field + Sleeper Agent 协作"""
    print_section("演示 4: Field + Sleeper Agent 协作")
    
    print_subsection("基于 AgenticX ReflectionPattern")
    
    print("""
💡 协作模式说明:

┌─────────────────┐
│  Field Agent    │  执行查询
│  (执行者)       │  ↓
└─────────────────┘  生成初始方案
        ↓
┌─────────────────┐
│  Sleeper Agent  │  审查结果
│  (顾问)         │  ↓
└─────────────────┘  提供反馈和建议
        ↓
┌─────────────────┐
│  Field Agent    │  根据反馈改进
│  (执行者)       │  ↓
└─────────────────┘  生成优化方案
        ↓
    重复循环...

✅ 使用 AgenticX 的 ReflectionPattern
✅ 执行-审查-改进的迭代循环
✅ 持续优化查询质量
""")
    
    print("\n注意: 完整的协作需要配置 LLM，这里展示架构")
    print("查看 DESIGN.md 了解详细的实现方式")


async def main():
    """主程序"""
    print_section("Agent-First Demo - 基于 AgenticX 框架")
    
    print("""
Agent-First 是一个将数据库从"面向人类"改造为"面向 AI Agent"的创新架构。

本项目基于 AgenticX 框架实现，包含四大核心功能：

1️⃣  Probe 接口        - 智能化查询（基于 Agent + Tool）
2️⃣  Memory Store      - 语义缓存（扩展 SemanticMemory）
3️⃣  分支管理          - Git 式分支（扩展 Storage）
4️⃣  Agent 协作        - Field + Sleeper（基于 ReflectionPattern）

🎯 核心优势: 充分利用 AgenticX，不重复造轮子！
""")
    
    try:
        # 演示 1: Probe 接口
        await demo_basic_probe()
        
        # 演示 2: 语义缓存
        await demo_memory_caching()
        
        # 演示 3: 分支管理
        await demo_branching()
        
        # 演示 4: Agent 协作
        demo_agent_collaboration()
        
        # 总结
        print_section("演示完成")
        print("""
✅ 成功演示了 Agent-First 的核心功能！

📊 预期性能提升（基于论文）:
   - 查询减少: 18.1%
   - 计算共享: 80-90%
   - 分支创建: 20x
   - 回滚操作: 50x

📚 了解更多:
   - 设计文档: DESIGN.md
   - 使用指南: README.md
   - 完整示例: examples/end_to_end_example.py
   - 博客文章: ../blog.md

🎉 基于 AgenticX 框架，站在巨人的肩膀上！
""")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 直接运行
    print("🚀 启动 Agent-First Demo...")
    asyncio.run(main())

