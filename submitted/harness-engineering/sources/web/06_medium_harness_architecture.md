# The Agent Harness Is the Architecture (and Your Model Is Not the Bottleneck) - Medium

**URL**: https://medium.com/@epappas/the-agent-harness-is-the-architecture-and-your-model-is-not-the-bottleneck-5ae5fd067bb2  
**Author**: Evangelos Pappas  
**Published**: Feb 24, 2026

---

## 核心论点

> **Agent harness engineering — the design of context management, tool selection, error recovery, and state persistence — is the primary determinant of agent reliability, not model capability.**

My hypothesis: Past a capability threshold, improving the harness yields better returns than swapping the model.

## tl;dr 关键发现

- **Verdict**: 假设成立，有一个重要条件——仅适用于模型能力基础线以上。低于该线，没有 Harness 能补偿不足。
- **OpenAI, Anthropic, Manus** 都独立得出相同结论：simpler harnesses plus better models beat complex orchestration
- **Manus** 重建框架4次，最大收益来自移除用户可见复杂性，同时添加针对性基础设施（上下文压缩、logit masking）。平均每任务约50次工具调用，使用文件系统作为外部记忆。
- **Vercel** 移除80%的工具（15→2），5查询基准准确率从80%→100%，Token降低37%，速度提升3.5x。
- **APEX-Agents benchmark**: 最佳 pass@1: 24.0%，pass@8: ~40%。失败主要是编排问题，而非知识缺口。

## Agent Harness 定义

An agent harness is the infrastructure layer that wraps a foundation model and controls five things:

1. **External memory** — how information is stored and retrieved beyond the context window
2. **State management** — how the agent persists progress across turns, sessions, and context window boundaries
3. **Error recovery** — how the system handles failed tool calls, reasoning dead-ends, and retry logic
4. **Tool selection** — which capabilities the model can invoke, and how those interfaces are designed
5. **Context management** — what enters the model's context window, in what order, and what gets evicted

> Think of the model as the engine and the harness as the car. The industry has spent years arguing about who has the best engine. Almost nobody has been building a car that can stay on the road.

## APEX-Agents Benchmark 的关键发现

APEX-Agents 测试真实专业工作（投资银行分析师、管理顾问、公司律师的任务），不是编程谜题。

**Results**:
- pass@1: 最佳 24.0%
- pass@8: ~40%
- 零分率：40%-62%（失败所有评分标准）
- 超时率（超过250步）：高达30%

**Critical finding**: 这些失败主要不是知识失败。模型有信息，能在隔离中推理问题。失败是执行和编排问题——Agent 在太多步骤后迷失、循环回到失败方法、任务中途丢失目标。

这正是 Harness Engineering 解决的失败模式：上下文管理（丢失跟踪）、错误恢复（失败循环）、状态管理（忘记目标）。

## Vercel 的反直觉发现：更少工具，更好结果

### 旧架构：15个专用工具

`GetEntityJoins`, `LoadCatalog`, `RecallContext`, `LoadEntityDetails`, `SearchCatalog`, `ClarifyIntent`, `SearchSchema`, `GenerateAnalysisPlan`, `FinalizeQueryPlan`, `FinalizeNoData`, `JoinPathFinder`, `SyntaxValidator`, `FinalizeBuild`, `ExecuteSQL`, `FormatResults`

成功率：80% (4/5 on their benchmark)

### 新架构：2个工具

1. **ExecuteSQL** — direct query execution
2. **ExecuteCommand** — bash access in a Vercel Sandbox

Agent 现在使用 `grep`, `cat`, `find`, `ls` 探索 Cube 语义层的 YAML、Markdown、JSON 文件。

### 结果对比

| 指标 | 旧架构（失败） | 新架构（成功） |
|------|---------------|---------------|
| 时间 | 724秒 | 141秒 |
| Tokens | 145,463 | 67,483 |
| 步骤 | 100步 | 19步 |
| 结果 | 失败 | 成功 |

**改进**: 速度提升5x，Token降低53%，步骤减少80%

> The best agents might be the ones with the fewest tools.

### 为什么有效

洞察不是工具不好。而是当模型已有足够能力使用通用接口时，**专用工具成为瓶颈**。每个专用工具是一个约束点——模型必须学习其模式、处理其错误、决定何时使用它 versus 替代方案。有15个工具时，模型花费更多Tokens选择而非执行。

通用工具（bash、文件访问）直接映射到模型训练方式。大多数前沿模型在训练数据中见过大量 shell 交互。他们知道怎么用 `grep`。他们不知道怎么调用 `GetEntityJoins` 并带正确参数。

## Manus: 四次重建和 $2B 的教训

Manus 在2025年初作为通用AI Agent 走红。然后他们做了大多数公司避免的事情：发布他们的错误。

2025年12月，Meta 以约 $2 billion 收购 Manus。

### 移除的内容

每次重建遵循模式：移除似乎必要但正在降低性能的用户可见复杂性，同时投资于针对性内部基础设施。

- 每个操作的专用工具 → 替换为通用 shell 执行
- 专用子代理之间的复杂路由逻辑 → 替换为结构化交接
- 复杂文档检索系统 → 替换为直接文件访问

### 保留和精炼的内容

**Filesystem-as-memory**: 不将所有内容塞进上下文窗口，Agent 将关键信息写入文件并在需要时读取。文件是"unlimited in size, persistent by nature, and directly operable by the agent"。

**Todo-list mechanism**: Agent 维护持久进度文件，在上下文末尾复述其目标，对抗"lost-in-the-middle"注意力退化。

**Context compaction**: 输入输出比约100:1，他们实现压缩层次结构：
1. Raw context (preferred) — 完整工具输出
2. Compaction — 交换完整结果为压缩版本，保留恢复路径
3. Summarization (last resort) — 仅当压缩不再产生足够空间时

**KV-cache optimization**: 通过维护稳定提示前缀、仅追加上下文、确定性序列化，在缓存Token上实现10x成本节省 ($0.30/MTok vs $3/MTok uncached with Claude Sonnet)。

**Tool management via logits masking**: 不通过提示动态添加和移除工具，而是使用通过 logit 级 masking 约束工具选择的上下文感知状态机。三种模式：Auto（模型选择）、Required（无约束）、Specified（通过 prefilling 子集选择）。

### 生产规模

他们的Agent平均每任务约50次工具调用。即使有大的上下文窗口（200k+ tokens），性能超过阈值后也会下降——不是因为模型"忘记"了早期内容，而是因为上下文窗口中的信噪比崩溃。开头的重要指令被埋在数百个中间工具结果下。

这与 Liu et al. 的"Lost in the Middle"研究一致，证明 LLM 表现出 U 形注意力模式——他们强烈关注上下文的开头和结尾，但对中间关注不佳。

## 三种架构，一种趋同

三个生产测试最多的 Agent Harness：OpenAI Codex、Claude Code、Manus。由不同团队独立建造，不同理念。他们在相同核心洞察上趋同。

### OpenAI Codex: Harness Engineering as a Discipline

OpenAI 发布"Harness Engineering"和"Unlocking the Codex Harness"——描述小团队如何在5个月内使用 Codex Agent 建造和发布百万行生产系统。

他们的架构强制执行严格的分层依赖模型：

```
Types → Config → Repo → Service → Runtime → UI
```

代码只能通过这些层向前依赖。跨域关注点（auth, connectors, telemetry, feature flags）通过单一显式接口进入：Providers。

### Claude Code: Minimal Tools, Maximum Model Intelligence

Anthropic 的 Claude Code 方法故意最小化。核心工具集：
- Search (grep/glob)
- Run bash commands
- Write/Edit a file
- Read a file

大多数智能存在于模型中。可扩展性通过 MCP (Model Context Protocol) 和项目级指令（`CLAUDE.md` 文件）实现。

Anthropic 推荐双代理模式：
1. **Coding Agent** — 处理增量工作，会话开始时读取进度文件
2. **Initializer Agent** — 首次运行时设置环境（init.sh、进度文件、功能跟踪）

关键状态管理工件：init.sh 脚本用于可复现环境、claude-progress.txt 文件用于工作日志、git 用于版本控制和回滚。约束：每会话一个功能，增量进度，保持代码可合并状态。

---
**Source**: https://medium.com/@epappas/the-agent-harness-is-the-architecture-and-your-model-is-not-the-bottleneck-5ae5fd067bb2
