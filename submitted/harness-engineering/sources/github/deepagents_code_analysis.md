# Deep Agents 代码分析

**仓库**: https://github.com/langchain-ai/deepagents  
**分析时间**: 2026-03-11

---

## 1. 仓库结构总览

```
deepagents/
├── libs/
│   ├── deepagents/      # SDK - 核心 Agent Harness
│   ├── cli/             # CLI工具 - 终端交互界面
│   ├── harbor/          # 评估/基准测试框架
│   ├── acp/             # Agent Context Protocol支持
│   └── partners/        # 集成包(Daytona等)
├── AGENTS.md            # 开发规范(约250行)
└── README.md
```

## 2. 核心架构分析

### 2.1 SDK 核心 (libs/deepagents/)

**入口点**: `deepagents/__init__.py`

```python
from deepagents.graph import create_deep_agent
from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.memory import MemoryMiddleware
from deepagents.middleware.subagents import CompiledSubAgent, SubAgent, SubAgentMiddleware
```

**核心组件**:
- `create_deep_agent()` - 创建 Deep Agent 的主入口
- `FilesystemMiddleware` - 文件系统中间件
- `MemoryMiddleware` - 记忆/状态中间件
- `SubAgentMiddleware` - 子代理中间件

### 2.2 Middleware 系统

位于 `deepagents/middleware/`，是 Harness Engineering 的核心实现：

#### SubAgent Middleware (subagents.py)

提供通过 `task` 工具创建子代理的能力：

```python
class SubAgent(TypedDict):
    """Specification for an agent."""
    name: str                    # 唯一标识
    description: str             # 功能描述
    system_prompt: str           # 系统提示
    tools: NotRequired[Sequence[BaseTool]]  # 工具列表
    model: NotRequired[str | BaseChatModel] # 模型覆盖
    middleware: NotRequired[list[AgentMiddleware]]  # 额外中间件
    interrupt_on: NotRequired[dict]  # 人机交互配置
    skills: NotRequired[list[str]]   # 技能路径
```

**关键特性**:
- 子代理自动继承默认中间件栈
- 支持隔离上下文窗口
- 结果压缩回传主代理

#### Filesystem Middleware (filesystem.py)

文件系统访问中间件，提供工具：
- `read_file` - 读取文件
- `write_file` - 写入文件
- `edit_file` - 编辑文件
- `ls` - 列出目录
- `glob` - 模式匹配
- `grep` - 文本搜索

#### Memory Middleware (memory.py)

记忆管理中间件：
- 跨会话状态持久化
- 自动摘要压缩
- 大输出保存到文件

#### Skills Middleware (skills.py)

技能系统中间件，支持自定义 slash 命令。

#### Summarization Middleware (summarization.py)

上下文摘要中间件：
- 长对话自动摘要
- 提示缓存优化
- Token 成本控制

### 2.3 后端系统 (backends/)

```python
# 核心后端类型
- LocalShellBackend      # 本地 shell 执行
- FilesystemBackend      # 文件系统后端
- CompositeBackend       # 组合后端
- SandboxBackend         # 沙箱后端(Remote)
```

### 2.4 CLI 实现 (libs/cli/)

**核心文件**:
- `agent.py` - Agent 创建和管理
- `app.py` - TUI 应用主入口
- `tools.py` - 工具定义
- `hooks.py` - Agent 执行钩子
- `sessions.py` - 会话管理
- `subagents.py` - 子代理管理

**Agent 创建流程** (agent.py):

```python
def create_agent_for_session(...) -> Pregel:
    # 1. 创建后端组合
    backend = CompositeBackend([
        FilesystemBackend(),
        LocalShellBackend(),
        # ... 其他后端
    ])
    
    # 2. 配置中间件
    middleware = [
        MemoryMiddleware(),      # 记忆管理
        SkillsMiddleware(),      # 技能系统
        FilesystemMiddleware(),  # 文件系统
        # ... 其他中间件
    ]
    
    # 3. 创建 Agent
    agent = create_deep_agent(
        model=model,
        tools=tools,
        middleware=middleware,
        checkpointer=checkpointer,  # 状态检查点
    )
    return agent
```

## 3. Harness Engineering 关键实现

### 3.1 状态持久化 (Checkpointing)

使用 LangGraph 的 checkpoint 系统：

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

# 内存检查点(开发/测试)
checkpointer = InMemorySaver()

# PostgreSQL检查点(生产)
checkpointer = PostgresSaver.from_conn_string(DB_URI)
```

**线程(thread)概念**：
- 每个 checkpoint 有唯一 thread_id
- 支持跨会话状态恢复
- 时间旅行调试

### 3.2 上下文管理

**LocalContextMiddleware** (local_context.py):

```python
# 启动时注入上下文
- 映射当前工作目录(cwd)
- 发现父目录和子目录
- 查找可用工具(Python等)
- 减少错误搜索空间
```

**Summarization 策略**：
- Raw context (首选) - 完整工具输出
- Compaction - 压缩版本，保留恢复路径
- Summarization (最后手段) - 仅当空间不足

### 3.3 工具编排

**统一工具接口**：
- 所有工具通过 `BaseTool` 抽象
- 工具运行时 (`ToolRuntime`)
- 权限和沙箱控制

**内置工具列表**:
1. `read_file` / `write_file` / `edit_file`
2. `execute` - shell 命令执行
3. `task` - 子代理委派
4. `write_todos` - 任务规划
5. `web_search` - 网络搜索 (CLI)
6. MCP 工具集成

### 3.4 验证与护栏

**Human-in-the-loop**:
```python
interrupt_on: dict[str, bool | InterruptOnConfig]
# 配置特定工具需要人工确认
```

**PreCompletionChecklistMiddleware**:
- 退出前强制验证
- 对比任务规范检查完成度
- Ralph Wiggum Loop 模式

## 4. 与 Anthropic/OpenAI 方案的对比

| 特性 | Deep Agents (LangChain) | Anthropic Claude Code | OpenAI Codex |
|------|------------------------|----------------------|--------------|
| **定位** | 开源通用 Harness | 产品内置 Harness | 方法论+产品 |
| **状态持久化** | LangGraph Checkpoint | Git + 进度文件 | Git + AGENTS.md |
| **子代理** | 原生 `task` 工具 | 双代理模式 | 多代理架构 |
| **上下文管理** | Middleware 系统 | claude-progress.txt | Progressive disclosure |
| **验证机制** | PreCompletionChecklist | E2E测试强制 | CI + 自定义 linter |
| **目标用户** | 开发者自建 | Claude 用户 | Codex 用户 |
| **可定制性** | 高(开源) | 中(通过MCP) | 中(通过AGENTS.md) |

## 5. 关键代码片段

### 5.1 创建 Agent 的核心代码

```python
# deepagents/graph.py (推断结构)
def create_deep_agent(
    model: BaseChatModel,
    tools: Sequence[BaseTool] | None = None,
    middleware: Sequence[AgentMiddleware] | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
    **kwargs
) -> CompiledGraph:
    """Create a Deep Agent with batteries included.
    
    Args:
        model: Language model to use
        tools: Additional tools beyond defaults
        middleware: Custom middleware stack
        checkpointer: State persistence backend
        
    Returns:
        Compiled LangGraph agent
    """
    # 默认工具: filesystem, shell, todos, task
    default_tools = [...]
    
    # 默认中间件栈
    default_middleware = [
        TodoListMiddleware(),        # 任务追踪
        FilesystemMiddleware(),      # 文件操作
        SummarizationMiddleware(),   # 上下文压缩
    ]
    
    # 构建 Agent 图
    builder = StateGraph(AgentState)
    # ... 添加节点和边
    
    return builder.compile(checkpointer=checkpointer)
```

### 5.2 子代理执行流程

```python
# subagents.py - 核心逻辑
async def run_subagent(
    parent_state: AgentState,
    subagent_spec: SubAgent,
    task_input: str
) -> ToolMessage:
    """Execute a subagent with isolated context.
    
    1. 创建隔离的 Agent 实例
    2. 运行任务
    3. 压缩结果回传父代理
    """
    # 隔离上下文
    subagent = create_agent_for_subtask(subagent_spec)
    
    # 运行任务
    result = await subagent.ainvoke({"messages": [HumanMessage(content=task_input)]})
    
    # 提取最终消息作为结果
    final_message = result["messages"][-1]
    return ToolMessage(content=final_message.content, tool_call_id=...)
```

## 6. 性能数据验证

### Terminal Bench 2.0 结果

| 配置 | 得分 | 排名 |
|------|------|------|
| 基线 (默认 harness) | 52.8% | 30+ |
| 优化后 (Harness Engineering) | 66.5% | Top 5 |
| **提升** | **+13.7** | **显著** |

### 关键优化点

1. **Build & Self-Verify**: 强制测试循环
2. **Time Budgeting**: 时间预算警告
3. **Directory Context**: 本地上下文注入
4. **Loop Detection**: 防止死循环编辑
5. **Reasoning Sandwich**: xhigh-high-xhigh 推理预算分配

## 7. 总结

Deep Agents 是 Harness Engineering 的**完整开源实现**，通过以下机制解决长运行 Agent 问题：

1. **状态持久化** - LangGraph Checkpoint 系统
2. **上下文管理** - Middleware 堆栈(摘要、压缩、隔离)
3. **工具编排** - 统一接口 + 权限控制
4. **任务拆解** - 子代理 + Todo 列表
5. **验证闭环** - PreCompletionChecklist + HITL

其核心优势是**可定制性**和**模型无关性**，支持任何支持工具调用的 LLM。

---
*分析基于仓库代码结构，部分实现细节根据公开文档推断*
