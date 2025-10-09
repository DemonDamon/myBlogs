# Agent-First：基于 AgenticX 的实现

将 Berkeley Agent-First 论文概念与 AgenticX 框架无缝集成，不重复造轮子！

## 🎯 核心理念

Agent-First 提出数据库应该为 AI Agent 设计，而不是为人类设计。本项目**基于 AgenticX 框架**实现了论文中的四大核心功能：

1. **Probe 接口** - 基于 AgenticX 的 `Agent` + `Tool`
2. **Field & Sleeper Agent** - 基于 AgenticX 的 `ReflectionPattern`
3. **Agentic Memory Store** - 扩展 AgenticX 的 `SemanticMemory`
4. **Git 式分支管理** - 扩展 AgenticX 的 `BaseStorage`

## 🏗️ 设计原则

### ✅ 充分利用 AgenticX
- 使用 `Agent`、`Task`、`Tool` 等核心抽象
- 使用 `ReflectionPattern`、`MasterSlavePattern` 等协作模式
- 扩展 `SemanticMemory` 而非重写
- 扩展 `BaseStorage` 添加分支能力

### ❌ 避免重复造轮子
- 不重新实现 Agent 系统
- 不重新实现 LLM 调用
- 不重新实现记忆系统基础
- 只扩展 Agent-First 特有功能

## 📦 快速开始

### 方式 1: 直接运行 Demo（推荐）

```bash
# 进入项目目录
cd agent_first_agenticx

# 直接运行（无需安装）
python demo.py
```

**就这么简单！** 查看 `RUN.md` 了解更多。

### 方式 2: 安装后使用

```bash
# 1. 确保已安装 AgenticX
pip install agenticx

# 2. 安装 Agent-First 扩展
cd agent_first_agenticx
pip install -e .
```

## 🚀 快速开始

### 1. 使用 Probe 接口查询

```python
from agenticx import Agent, LiteLLMProvider
from agent_first_agenticx.probes import ProbeQueryTool, create_probe_agent

# 创建 LLM
llm = LiteLLMProvider(model="gpt-4")

# 创建 Probe Agent
probe_agent = create_probe_agent(llm=llm)

# 创建 Probe Tool
probe_tool = ProbeQueryTool(
    database_connector=your_db,  # 你的数据库连接
    memory_store=None  # 可选：添加记忆存储
)

# 使用自然语言查询
result = await probe_tool.execute(
    natural_query="找出销售额最高的前10个产品",
    stage="exploration",  # 探索阶段
    precision="approximate"  # 近似结果即可
)

print(f"查询结果: {result}")
```

### 2. 使用 Field + Sleeper Agent 协作

```python
from agenticx import LiteLLMProvider
from agenticx.collaboration import ReflectionPattern
from agent_first_agenticx.agents import create_field_agent, create_sleeper_agent

# 创建 LLM
llm = LiteLLMProvider(model="gpt-4")

# 创建 Field Agent (执行查询)
field_agent = create_field_agent(llm=llm)

# 创建 Sleeper Agent (提供建议)
sleeper_agent = create_sleeper_agent(llm=llm)

# 使用 AgenticX 的 ReflectionPattern 协作
collaboration = ReflectionPattern(
    executor_agent=field_agent,
    reviewer_agent=sleeper_agent,
    llm_provider=llm
)

# 执行协作任务
task = "分析用户购买行为，找出高价值客户"
result = collaboration.execute(task)

print(f"Field Agent 执行: {result.result}")
print(f"Sleeper Agent 建议: {result.metadata['suggestions']}")
```

### 3. 使用 Agentic Memory Store 缓存查询

```python
from agent_first_agenticx.memory import AgenticMemoryStore

# 创建 Memory Store（扩展自 AgenticX 的 SemanticMemory）
memory = AgenticMemoryStore(
    tenant_id="your_org",
    agent_id="probe_agent_001"
)

# 缓存 Probe 查询结果
await memory.cache_probe_result(
    probe_request={
        "natural_query": "找出最畅销产品",
        "sql": "SELECT * FROM products ORDER BY sales DESC LIMIT 10",
        "stage": "exploration"
    },
    probe_response={
        "data": [...],
        "execution_time": 0.25
    }
)

# 查找相似查询（利用 80-90% 的冗余）
similar = await memory.find_similar_probes(
    natural_query="查询销量最好的商品",
    threshold=0.8
)

if similar:
    print(f"找到相似查询，直接使用缓存！节省 {similar.execution_time} 秒")
```

### 4. 使用 Git 式分支进行 What-If 探索

```python
from agent_first_agenticx.storage import BranchManager

# 创建分支管理器
branch_mgr = BranchManager(storage=your_storage)

# 创建新分支测试不同的定价策略
branch1 = await branch_mgr.create_branch(
    parent="main",
    name="test-pricing-strategy-a"
)

# 在分支上进行修改
await branch1.update("products", {
    "product_id": 123,
    "price": 99.99  # 测试新价格
})

# 查询分支上的数据
result = await branch1.query("SELECT SUM(revenue) FROM orders")

# 如果满意就合并，否则回滚
if result["revenue"] > target_revenue:
    await branch_mgr.merge(branch1.id, "main")
    print("新定价策略效果好，已合并到主分支！")
else:
    await branch_mgr.rollback(branch1.id)
    print("新定价策略效果不佳，已回滚。")
```

## 📊 完整示例：端到端 Agent-First 工作流

```python
import asyncio
from agenticx import Agent, Task, LiteLLMProvider
from agenticx.collaboration import ReflectionPattern
from agent_first_agenticx import (
    ProbeQueryTool,
    create_field_agent,
    create_sleeper_agent,
    AgenticMemoryStore,
    BranchManager
)

async def agent_first_workflow():
    # 1. 初始化组件
    llm = LiteLLMProvider(model="gpt-4")
    memory = AgenticMemoryStore(tenant_id="demo", agent_id="main")
    branch_mgr = BranchManager(storage=your_storage)
    
    # 2. 创建 Field + Sleeper Agent 协作
    field_agent = create_field_agent(llm=llm)
    sleeper_agent = create_sleeper_agent(llm=llm)
    collaboration = ReflectionPattern(field_agent, sleeper_agent, llm)
    
    # 3. 元数据探索阶段
    print("阶段1：元数据探索")
    probe_tool = ProbeQueryTool(database=db, memory_store=memory)
    schema_info = await probe_tool.execute(
        natural_query="有哪些表和字段？",
        stage="metadata_exploration",
        precision="exact"
    )
    
    # 4. 解决方案制定阶段（多次尝试，利用冗余优化）
    print("阶段2：解决方案制定")
    attempts = []
    for i in range(5):  # 并行探索多个方案
        result = await probe_tool.execute(
            natural_query=f"尝试方案{i}: 分析用户购买模式",
            stage="solution_formulation",
            precision="approximate"  # 近似结果，快速验证
        )
        attempts.append(result)
    
    # Memory Store 会自动识别 80-90% 的冗余，共享计算
    print(f"5次尝试，但只执行了 {memory.actual_queries} 次查询（冗余优化）")
    
    # 5. 在分支上测试最佳方案
    print("阶段3：分支测试")
    best_solution = max(attempts, key=lambda x: x.confidence)
    test_branch = await branch_mgr.create_branch("main", "test-solution")
    
    # 在分支上应用方案
    branch_result = await test_branch.apply_solution(best_solution)
    
    # 6. 完整验证
    print("阶段4：完整验证")
    if branch_result.success:
        final_result = await probe_tool.execute(
            natural_query=best_solution.query,
            stage="full_validation",
            precision="exact"  # 精确结果
        )
        
        # 合并成功的分支
        await branch_mgr.merge(test_branch.id, "main")
        print("✅ 方案验证成功并已合并！")
    else:
        await branch_mgr.rollback(test_branch.id)
        print("❌ 方案验证失败，已回滚。")
    
    # 7. Sleeper Agent 提供最终建议
    advice = await sleeper_agent.execute_task(
        Task(
            description="基于以上探索过程，提供优化建议",
            context={"history": attempts, "final_result": final_result}
        )
    )
    print(f"💡 Sleeper Agent 建议: {advice}")

# 运行工作流
asyncio.run(agent_first_workflow())
```

## 📁 项目结构

```
agent_first_agenticx/
├── __init__.py              # 主入口
├── DESIGN.md                # 详细设计文档
├── README.md                # 本文件
│
├── probes/                  # Probe 系统
│   ├── probe_tool.py        # ProbeQueryTool（基于 BaseTool）
│   ├── probe_agent.py       # ProbeAgent 创建函数
│   └── models.py            # Probe 数据模型
│
├── agents/                  # Agent 系统
│   ├── field_agent.py       # FieldAgent 配置
│   ├── sleeper_agent.py     # SleeperAgent 配置
│   └── collaboration.py     # 协作辅助函数
│
├── memory/                  # 记忆扩展
│   ├── agentic_memory.py    # AgenticMemoryStore
│   ├── query_cache.py       # 查询缓存
│   └── redundancy.py        # 冗余检测
│
├── storage/                 # 存储扩展
│   ├── branch_manager.py    # 分支管理器
│   ├── cow_engine.py        # 写时复制引擎
│   └── branch_storage.py    # 分支存储
│
└── examples/                # 示例代码
    ├── basic_probe.py
    ├── field_sleeper_collab.py
    ├── memory_caching.py
    ├── branching.py
    └── end_to_end.py
```

## 🎓 核心概念

### Probe vs SQL

**传统 SQL:**
```sql
SELECT * FROM products WHERE category='electronics' ORDER BY sales DESC LIMIT 10;
```

**Probe 方式:**
```python
# 更智能：理解意图、阶段、精度需求
result = await probe_tool.execute(
    natural_query="找出最畅销的电子产品",
    stage="exploration",        # 我在探索阶段
    precision="approximate",    # 近似结果即可
    context="了解产品趋势"
)
```

系统会：
- ✅ 理解你的查询意图
- ✅ 根据阶段选择执行策略
- ✅ 提供相关建议和优化
- ✅ 与其他查询共享计算（80-90% 冗余）

### Field Agent vs Sleeper Agent

| Feature | Field Agent | Sleeper Agent |
|---------|-------------|---------------|
| 角色 | 查询执行者 | 智能顾问 |
| 职责 | 解析并执行查询 | 提供建议和推荐 |
| 模式 | 主动执行 | 被动观察，主动建议 |
| 输出 | 查询结果 | 优化建议、相关推荐 |

通过 AgenticX 的 `ReflectionPattern`，两者形成**执行-反思-改进**的闭环。

### 语义缓存 vs 传统缓存

**传统缓存：**
- 精确匹配查询语句
- 命中率低（Agent 每次查询都略有不同）

**语义缓存（基于 AgenticX SemanticMemory）：**
- 理解查询语义
- 识别相似查询（如"最畅销产品" vs "销量最高商品"）
- 80-90% 的 Agent 查询可以共享计算
- 自动概念提取和知识图谱

## 🔬 性能优化

基于论文实验结果，Agent-First 实现了：

- ✅ **18.1% 查询减少** - 通过 Sleeper Agent 的智能引导
- ✅ **80-90% 计算共享** - 通过语义缓存和冗余检测
- ✅ **20x 分支创建** - 相比传统数据库的事务
- ✅ **50x 回滚操作** - 支持更多的 what-if 探索

## 🤝 与 AgenticX 集成

Agent-First 完全基于 AgenticX，可以：

1. **使用所有 LLM Provider**
   - OpenAI, Anthropic, Ollama, Kimi 等

2. **使用所有工具**
   - MCP 工具、远程工具、自定义工具

3. **使用所有协作模式**
   - Reflection, MasterSlave, Debate, GroupChat 等

4. **使用可观测性**
   - 轨迹跟踪、性能监控、实时仪表板

## 📖 学习资源

- [Agent-First 论文](https://arxiv.org/abs/2501.02655)
- [AgenticX 文档](https://github.com/YourRepo/AgenticX)
- [设计文档](./DESIGN.md)
- [博客文章](../blog.md)

## 🤝 贡献

欢迎贡献！请确保：
1. 遵循"基于 AgenticX，不重复造轮子"的原则
2. 扩展而非重写 AgenticX 的功能
3. 添加完整的测试和文档

## 📄 许可证

MIT License

---

**核心思想：站在 AgenticX 的肩膀上，专注实现 Agent-First 的创新功能！**

