# Agent-First 基于 AgenticX 的实现设计

## 设计理念

本项目基于 [AgenticX](https://github.com/YourRepo/AgenticX) 框架，实现 Berkeley Agent-First 论文中的核心概念，**不重复造轮子**，充分利用 AgenticX 的现有能力。

## 架构映射

### 1. Probe 接口系统 → AgenticX Agent + Tool

**AgenticX 现有能力：**
- `Agent`: 包含 role, goal, LLM配置
- `Task`: 任务描述和输出要求
- `BaseTool`: 工具抽象
- `AgentExecutor`: 执行器

**Agent-First 实现：**
```python
# 创建专门的 ProbeAgent
probe_agent = Agent(
    name="ProbeAgent",
    role="database_query_agent",
    goal="执行智能化的数据库查询，理解查询意图和阶段",
    backstory="专门为 Agent 设计的查询接口智能体"
)

# Probe 查询作为特殊的 Tool
class ProbeTool(BaseTool):
    """Probe 查询工具，支持自然语言查询意图"""
    def execute(self, natural_query, stage, precision, ...):
        # 解析意图
        # 生成 SQL
        # 执行查询
        pass
```

### 2. Field Agent & Sleeper Agent → ReflectionPattern

**AgenticX 现有能力：**
- `ReflectionPattern`: 执行者 + 审查者的反思协作
- `Agent`: 可以创建不同角色的智能体
- `AgentExecutor`: 执行和反馈循环

**Agent-First 实现：**
```python
# Field Agent - 执行查询
field_agent = Agent(
    name="FieldAgent",
    role="query_executor",
    goal="解析和执行 Probe 查询"
)

# Sleeper Agent - 提供建议
sleeper_agent = Agent(
    name="SleeperAgent", 
    role="query_advisor",
    goal="提供查询优化建议和主动推荐"
)

# 使用 ReflectionPattern 协作
reflection = ReflectionPattern(
    executor_agent=field_agent,
    reviewer_agent=sleeper_agent
)
```

### 3. Agentic Memory Store → 扩展 SemanticMemory

**AgenticX 现有能力：**
- `SemanticMemory`: 语义记忆、概念提取、知识图谱
- `BaseMemory`: search/add/update 接口
- 已有 tenant_id 隔离、metadata 过滤

**Agent-First 实现：**
```python
class AgenticMemoryStore(SemanticMemory):
    """扩展 SemanticMemory，添加 Probe 查询缓存"""
    
    async def cache_probe_result(self, probe_request, probe_response):
        """缓存 Probe 查询结果"""
        # 使用 SemanticMemory 的 add_knowledge
        await self.add_knowledge(
            content=probe_request.natural_query,
            knowledge_type="probe_result",
            metadata={
                "sql": probe_request.sql_query,
                "stage": probe_request.stage,
                "precision": probe_request.precision,
                "result": probe_response.data,
                "execution_time": probe_response.execution_time
            }
        )
    
    async def find_similar_probes(self, probe_request, threshold=0.8):
        """查找相似的 Probe 查询（利用冗余）"""
        # 使用 SemanticMemory 的 search
        results = await self.search(
            query=probe_request.natural_query,
            limit=10,
            metadata_filter={"knowledge_type": "probe_result"}
        )
        return results
```

### 4. Git 式分支管理 → 扩展 BaseStorage

**AgenticX 现有能力：**
- `BaseStorage`: 存储抽象，支持 session/document/query
- `BaseVectorStorage`: 向量存储
- 完整的CRUD操作

**Agent-First 实现：**
```python
class BranchStorage(BaseStorage):
    """扩展 BaseStorage，添加 Git 式分支管理"""
    
    def __init__(self, base_storage):
        self.base_storage = base_storage
        self.branches = {}  # branch_id -> branch_metadata
        self.branch_data = {}  # branch_id -> data_snapshot
    
    async def create_branch(self, parent_branch, branch_name):
        """创建新分支（写时复制）"""
        # 实现 copy-on-write
        pass
    
    async def merge_branch(self, source_branch, target_branch):
        """合并分支"""
        pass
    
    async def rollback_branch(self, branch_id):
        """回滚分支"""
        pass
```

## 实现优势

### ✅ 充分利用 AgenticX 现有能力

1. **Agent 系统**
   - 直接使用 `Agent` 类创建 ProbeAgent/FieldAgent/SleeperAgent
   - 利用 `AgentExecutor` 执行任务
   - 支持 LLM 配置和工具集成

2. **协作模式**
   - 使用 `ReflectionPattern` 实现 Field + Sleeper 协作
   - 可以结合其他模式（如 `MasterSlavePattern`, `DebatePattern`）

3. **记忆系统**
   - 扩展 `SemanticMemory` 而不是重写
   - 继承概念提取、语义搜索、知识图谱能力
   - 复用 tenant isolation 和 metadata filter

4. **存储系统**
   - 扩展 `BaseStorage` 添加分支管理
   - 可以与现有的向量存储、图存储集成

### ✅ 避免重复造轮子

- **不需要重新实现** Agent、Task、Memory 的基础能力
- **不需要重新实现** LLM 调用、工具系统
- **不需要重新实现** 协作模式、通信机制
- **只需要扩展** 特定的 Agent-First 功能

### ✅ 与 AgenticX 生态集成

- 可以使用 AgenticX 的所有 LLM Provider
- 可以使用 AgenticX 的工具系统
- 可以使用 AgenticX 的可观测性系统
- 可以与其他 AgenticX 应用集成

## 核心扩展点

### 1. ProbeQueryTool
```python
from agenticx import BaseTool

class ProbeQueryTool(BaseTool):
    """Probe 查询工具"""
    name: str = "probe_query"
    description: str = "执行智能化的数据库查询，理解查询意图和阶段"
    
    def __init__(self, memory_store, database_connector):
        self.memory_store = memory_store
        self.database = database_connector
    
    async def execute(self, **kwargs):
        # 1. 检查缓存
        # 2. 解析意图
        # 3. 生成 SQL
        # 4. 执行查询
        # 5. 缓存结果
        pass
```

### 2. AgenticMemoryStore
```python
from agenticx.memory import SemanticMemory

class AgenticMemoryStore(SemanticMemory):
    """扩展语义记忆，支持 Probe 缓存和冗余优化"""
    
    def __init__(self, tenant_id, agent_id):
        super().__init__(tenant_id, agent_id)
        self.probe_cache = {}
        self.redundancy_detector = RedundancyDetector()
```

### 3. BranchManager
```python
from agenticx.storage import BaseStorage

class BranchManager:
    """Git 式分支管理器"""
    
    def __init__(self, storage: BaseStorage):
        self.storage = storage
        self.cow_engine = CopyOnWriteEngine()
```

## 目录结构

```
agent_first_agenticx/
├── __init__.py
├── DESIGN.md                    # 本设计文档
├── README.md                    # 使用说明
│
├── probes/                      # Probe 系统
│   ├── __init__.py
│   ├── probe_tool.py            # ProbeQueryTool（基于 BaseTool）
│   ├── probe_agent.py           # ProbeAgent 创建和配置
│   └── models.py                # Probe 相关数据模型
│
├── agents/                      # Agent 系统
│   ├── __init__.py
│   ├── field_agent.py           # FieldAgent 配置
│   ├── sleeper_agent.py         # SleeperAgent 配置
│   └── collaboration.py         # 基于 ReflectionPattern 的协作
│
├── memory/                      # 记忆扩展
│   ├── __init__.py
│   ├── agentic_memory.py        # AgenticMemoryStore（扩展 SemanticMemory）
│   ├── query_cache.py           # 查询缓存管理
│   └── redundancy.py            # 冗余检测和优化
│
├── storage/                     # 存储扩展
│   ├── __init__.py
│   ├── branch_manager.py        # 分支管理器
│   ├── cow_engine.py            # 写时复制引擎
│   └── branch_storage.py        # 分支存储实现
│
└── examples/                    # 示例
    ├── basic_probe.py           # 基础 Probe 使用
    ├── field_sleeper_collab.py  # Field + Sleeper 协作
    ├── memory_caching.py        # 语义缓存示例
    ├── branching.py             # 分支管理示例
    └── end_to_end.py            # 完整端到端示例
```

## 实现步骤

1. ✅ **设计架构方案** - 当前步骤
2. ⏭️ **实现 Probe 系统** - 创建 ProbeQueryTool 和 ProbeAgent
3. ⏭️ **实现 Agent 协作** - 配置 FieldAgent 和 SleeperAgent
4. ⏭️ **扩展 Memory** - 实现 AgenticMemoryStore
5. ⏭️ **扩展 Storage** - 实现 BranchManager
6. ⏭️ **创建示例** - 编写完整的使用示例

## 依赖关系

```
Agent-First (本项目)
    ↓ 依赖
AgenticX (已有框架)
    ├── core (Agent, Task, Tool)
    ├── collaboration (ReflectionPattern, MasterSlavePattern)
    ├── memory (SemanticMemory, BaseMemory)
    ├── storage (BaseStorage, BaseVectorStorage)
    ├── llms (BaseLLMProvider)
    └── tools (BaseTool, ToolExecutor)
```

## 安装和使用

```bash
# 1. 安装 AgenticX
pip install agenticx

# 2. 安装 Agent-First 扩展
cd agent_first_agenticx
pip install -e .

# 3. 使用
from agent_first_agenticx import ProbeQueryTool, FieldAgent, SleeperAgent, AgenticMemoryStore
```

## 与论文对应关系

| Agent-First 论文概念 | AgenticX 实现 | 扩展内容 |
|---------------------|--------------|---------|
| Probe 接口 | Agent + Tool | ProbeQueryTool |
| Field Agent | Agent + AgentExecutor | 专门的 FieldAgent 配置 |
| Sleeper Agent | Agent + ReflectionPattern | 专门的 SleeperAgent 配置 |
| Agentic Memory Store | SemanticMemory | 查询缓存、冗余检测 |
| Git 式分支 | BaseStorage | BranchManager、COW 引擎 |
| Multi-query 优化 | SemanticMemory.search | 相似查询检测 |
| 语义缓存 | SemanticMemory.add_knowledge | Probe 结果缓存 |

## 总结

通过基于 AgenticX 实现，我们：
1. **避免重复造轮子** - 充分利用现有的 Agent、Memory、Storage 能力
2. **保持一致性** - 与 AgenticX 生态无缝集成
3. **专注创新** - 只实现 Agent-First 特有的功能
4. **易于维护** - 跟随 AgenticX 更新和改进
5. **可扩展** - 可以轻松添加更多 Agent-First 功能

这个设计方案充分体现了"站在巨人肩膀上"的思想，让我们能够快速实现 Agent-First 的核心概念，同时享受 AgenticX 的强大能力。

