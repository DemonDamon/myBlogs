# Harness Engineering：一个被过度包装的好想法

> **核心观点**：Harness Engineering 本质上是 Agent 领域的 DevOps——把散乱的运维经验系统化。它确实有效，但远没有各家博客宣传的那么神奇，数据也值得打问号。

## 引言：当三家公司同时讲同一个故事

2026年初，Anthropic、OpenAI、LangChain 几乎同期发文谈 Harness Engineering。三篇文章核心叙事高度一致："不是模型不行，是周围的系统没做好。"

![Anthropic 官方博客截图](images/anthropic_harness_hero.png)
*Anthropic 博客《Effective harnesses for long-running agents》首屏*

![OpenAI 官方博客截图](images/openai_harness_hero.png)
*OpenAI 博客《工程技术：在智能体优先的世界中利用 Codex》首屏*

这个叙事对吗？**部分对，但有明显的利益驱动**。Anthropic 要卖 Claude Agent SDK，OpenAI 要推 Codex，LangChain 要巩固 LangGraph 生态。"模型不是瓶颈"这句话，翻译过来就是：别去换别家模型了，在我们的生态里继续调就行。

但抛开营销话术，Harness Engineering 的底层逻辑确实成立——**模型在单次推理上已经足够聪明，但在长时间、多轮、跨会话的任务中，系统工程才是决定因素**。这不是新发现，这是 DevOps、可靠性工程、分布式系统工程换了个名字出现在 Agent 领域。

## 什么是 Harness Engineering？

### 定义：新瓶装旧酒，但瓶子设计得不错

**Harness Engineering**（驾驭工程）是围绕 LLM 构建的系统工程方法论，通过优化上下文管理、工具编排、状态持久化和验证闭环，试图将模型的概率性输出转化为可控行为。

这个定义听起来很新，但拆开看每个组件都有传统软件工程的对应物：

| Harness 组件 | 传统工程对应物 | 实际上在做什么 |
|------|------|------|
| 上下文管理 | 配置管理 + 缓存系统 | 控制 LLM 看到什么 |
| 状态持久化 | 数据库 + 检查点机制 | 让会话不丢失 |
| 工具编排 | API Gateway + Middleware | 管理工具调用 |
| 验证闭环 | CI/CD + 测试框架 | 确保输出质量 |
| 护栏约束 | 权限系统 + 沙箱 | 防止越界 |

Harness Engineering 的真正贡献不在于发明新概念，而在于**把这些散落的工程经验整合成了一个针对 Agent 场景的系统框架**。

### 五大核心机制

![Harness 五大核心机制架构图](images/harness_five_mechanisms.png)
*Agent Harness 的五大核心机制及其与 LLM 模型的关系*

## 行业实践对比：三种路线，各有盲区

![三家 Harness 方案对比](images/three_companies_comparison.png)
*Anthropic、OpenAI、LangChain 三家方案的核心差异*

### Anthropic：双阶段框架——稳但慢

Anthropic 在《Effective harnesses for long-running agents》中提出了 Initializer Agent + Coding Agent 的双阶段方案。

![Anthropic 双阶段 Agent 流程图](images/anthropic_dual_phase_flow.png)
*Anthropic 的 Initializer Agent 负责奠基，Coding Agent 负责增量循环*

#### 核心机制

**Initializer Agent** 首次运行时建立基础：
- 生成 `feature_list.json`：200+ 可验证功能点
- 创建 `init.sh`：可重复运行的环境脚本
- 建立 `claude-progress.txt`：进度文件
- 执行初始 Git Commit

**Coding Agent** 每次启动执行增量工作循环：
1. 读取 feature_list.json，选择最高优先级未完成项
2. 查看 Git log + 进度文件
3. 运行 init.sh 重启环境
4. 实现一个功能 → E2E 测试 → 通过则更新状态
5. Git commit + 更新进度

![Anthropic 失败模式和解决方案表](images/anthropic_failure_modes_table.png)
*Anthropic 博客中原文的 Agent failure modes and solutions*

#### 需要质疑的点

**问题一：只在全栈 Web App 上验证过。** Anthropic 的内部测试案例是 `claude.ai` 的克隆。Web App 有清晰的页面→功能→测试映射，但在数据管线、分布式系统、底层库开发等场景，这种"每会话一个功能"的拆解未必可行。

**问题二：Puppeteer E2E 测试的局限性。** Anthropic 自己也承认 Claude 无法看到浏览器原生 alert modals。更深层的问题是——对于非 UI 项目（CLI 工具、后端服务、数据处理），E2E 测试的定义和执行完全不同，双阶段框架如何适配？文中没有回答。

**问题三：200+ feature 拆解的质量谁来保证？** Initializer Agent 生成 feature list 本身就依赖模型能力。如果拆解不合理——比如粒度过细导致功能间有大量隐式依赖——后续的 Coding Agent 会不断踩坑。这是个鸡生蛋的问题。

### OpenAI："零人工代码"——数据经不起推敲

OpenAI 在《Harness engineering: leveraging Codex in an agent-first world》中声称：

> 5 个月，100 万行代码，零人工编写源码，1500 个 PR，3.5 PR/工程师/天。

![OpenAI AGENTS.md 部分截图](images/openai_agents_md_section.png)
*OpenAI 博客中关于从空 Git 仓库启动的描述*

#### 核心理念：Humans steer, Agents execute

工程师设计环境、明确意图、建立反馈循环，Agent 负责代码生成。通过 `AGENTS.md`（~100行）作为仓库目录，而非百科全书。

关键机制：
- **渐进式披露**：Agent 从小入口开始，按需深入
- **机械强制执行**：自定义 Linter + CI 检验架构规则
- **分层架构**：`Types → Config → Repo → Service → Runtime → UI`
- **熵管理**：每周自动清理 "AI slop" 的 "doc-gardening agent"

#### 数据的问号

**"零人工编写"到底是什么意思？** 文章原文说的是"没有一行代码是人工编写的"，但同时提到工程师需要"设计环境、明确意图、建立反馈循环"。写 AGENTS.md、设计 Linter 规则、review PR、定义分层架构——这些不是写代码吗？这里的"零人工"实际上是"零人工 *在编辑器里敲应用代码*"，人工成本被转移到了 Harness 设计和 PR Review 上。

**100 万行代码有多少是有效代码？** OpenAI 自己在文中提到需要专门的 agent 每周清理 "AI slop"（AI 生成的冗余/低质量代码）。这暗示了一个严重问题：Agent 生成的代码中有相当比例是需要被清理掉的。100 万行减去 slop，有效代码是多少？文中没说。

**3.5 PR/天的质量如何？** 传统开发中每天 1-2 个高质量 PR 已经很快。3.5 PR/天如果都是高质量的，确实是革命性的。但如果其中大量 PR 是小修补、格式调整、AI slop 清理，这个数字就不那么有说服力了。

**可复现性存疑。** 这是 OpenAI 内部、7 名工程师、使用自家还未公开的工具链完成的实验。外部团队能否复现？在 OpenAI 之外的代码库上效果如何？**目前无法验证。**

### LangChain：Deep Agents——数据最透明，但天花板明显

LangChain 的做法相对诚实：在公开 Benchmark 上做实验，数据可查。

![LangChain Terminal Bench 排行榜截图](images/langchain_terminal_bench_leaderboard.png)
*LangChain Deep Agents 在 Terminal Bench 2.0 排行榜的实际排名*

#### 量化数据

| 阶段 | 得分 | 排名 |
|------|------|------|
| 基线（默认 Harness） | 52.8% | 30+ |
| 优化后 | **66.5%** | **Top 5** |
| **提升** | **+13.7** | |

模型固定为 GPT-5.2-Codex，只调整 Harness。

![LangChain Harness 调优三维度截图](images/langchain_knobs_harness.png)
*LangChain 聚焦 System Prompt、Tools、Middleware 三个调优维度*

#### 关键改进

1. **Build & Self-Verify 循环**：强制 Agent 运行测试、对比 Task Spec（而非自己的代码）
2. **PreCompletionChecklistMiddleware**：拦截退出，强制验证
3. **LoopDetectionMiddleware**：检测同一文件的重复编辑
4. **推理预算分配**：xhigh-high-xhigh "sandwich"

```python
PreCompletionChecklistMiddleware(
    checklist=[
        "Run all tests and verify pass",
        "Compare output against task spec",
        "Check edge cases"
    ]
)
```

#### 但要看到天花板

**Terminal Bench 2.0 只有 89 个任务。** 这是个小样本 benchmark。66.5% 意味着近 30 个任务仍然失败。而且 benchmark 任务有固定的目录结构、工具链和超时——与真实生产环境差距很大。

**Top 5 的含金量存疑。** 看排行榜，Top 10 的分数区间是 63%-75%，差距不大。排名波动很可能跟运行次数和随机性有关（注意 LangChain 的置信区间是 ±3.1）。

**最大限制：只在编码任务上验证。** 这三家公司的 Harness 实验全部集中在代码生成场景。对于研究分析、内容创作、数据处理等 Agent 任务，Harness Engineering 的效果几乎没有数据。

## 核心组件详解：哪些是真正有效的？

### 1. 状态持久化——问题不大，已有成熟方案

LangGraph Checkpointing 提供了跨会话恢复能力：

```python
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(DB_URI)
graph = builder.compile(checkpointer=checkpointer)
```

Anthropic 的 Git + 进度文件方案更加简单粗暴，但在实际生产中可能反而更可靠——因为 Git 是开发者已经熟悉的工具，不引入新的基础设施依赖。

**辩证看**：状态持久化是已解决的工程问题。数据库、消息队列、文件系统——选哪个取决于场景，不是什么新发明。

### 2. 上下文管理——真正的硬问题

这是 Harness Engineering 中最有技术含量的部分。核心挑战：

**问题的本质**：即使模型有 1M Token 窗口，实际有效上下文远小于此。Manus 的数据表明，超过 50 次工具调用后信噪比急剧下降。

**Manus 的三级压缩策略**：

| 层次 | 策略 | 代价 |
|------|------|------|
| Raw | 完整保留 | 占用窗口空间 |
| Compaction | 压缩 + 保留恢复路径 | 细节丢失 |
| Summarization | 仅保留摘要 | 不可逆信息损失 |

**KV-Cache 优化的经济意义**：
- 缓存价格：$0.30/MTok
- 未缓存价格：$3/MTok

这意味着良好的上下文管理可以带来 **10x 成本差异**。这不是优化，这是能不能用得起的区别。

**但要诚实地说**：上下文管理本质上是 trade-off——你压缩得越多，信息损失越大。没有免费的午餐。当前所有方案都是启发式的，没有理论最优解。

### 3. 工具编排——Vercel 的发现值得深思

Vercel 的 text-to-SQL Agent 实验是最反直觉的发现之一：

| 指标 | 15个专用工具 | 2个通用工具 |
|------|-----------|-----------|
| 准确率 | 80% | **100%** |
| 耗时 | 724秒 | **141秒** |
| Token | 145,463 | **67,483** |
| 步骤 | 100步 | **19步** |

为什么更少的工具反而更好？因为 `bash`、`grep`、`cat` 这些通用工具已经在模型训练数据中被大量见过，模型知道怎么用。专用工具（`GetEntityJoins`、`ClarifyIntent`）需要模型现学，学习成本消耗了大量 Token。

**但别过度推广这个结论。** Vercel 的案例是 SQL 查询——一个高度结构化、模型训练数据丰富的领域。在领域特定场景（如操作特定的内部 API、调用企业私有系统），通用工具未必能替代专用工具。

### 4. 验证闭环——最容易被低估的部分

三家公司不约而同强调了同一个问题：**Agent 倾向于过早宣布任务完成。**

Anthropic 的表述最生动：模型在实现功能后，不运行测试就直接标记 `passes: true`。OpenAI 用自定义 Linter + CI 做机械强制。LangChain 用 PreCompletionChecklistMiddleware 做运行时拦截。

**这揭示了一个根本性问题：当前 LLM 缺乏对"完成"的可靠判断能力。** 它们优化的是"看起来完成"，而非"实际完成"。验证闭环不是优化，而是**必需品**。

## Deep Agents 代码层面：Middleware 驱动的架构

Deep Agents 的核心是 Middleware 系统——一种类似于 Express.js 中间件的模式：

```python
class SubAgent(TypedDict):
    name: str
    description: str
    system_prompt: str
    tools: NotRequired[Sequence[BaseTool]]
    model: NotRequired[str | BaseChatModel]
    middleware: NotRequired[list[AgentMiddleware]]
```

默认 Middleware 栈：

```python
default_middleware = [
    TodoListMiddleware(),        # 任务追踪
    FilesystemMiddleware(),      # 文件操作
    SummarizationMiddleware(),   # 上下文压缩
    SkillsMiddleware(),          # 技能系统
    SubAgentMiddleware(),        # 子代理委派
]
```

Agent 创建流程清晰地体现了 Harness 的分层设计：

```python
async def create_agent_for_session(...):
    backend = CompositeBackend([
        FilesystemBackend(),
        LocalShellBackend(),
        SandboxBackend(...)
    ])
    middleware = [
        MemoryMiddleware(),
        LocalContextMiddleware(),
        SkillsMiddleware(),
    ]
    agent = create_deep_agent(
        model=model,
        tools=tools,
        middleware=middleware,
        checkpointer=checkpointer,
    )
    return agent
```

**设计上的优点**：模块化、可组合、每个组件可独立测试和替换。

**设计上的问题**：Middleware 顺序敏感，调试链路长，多个 Middleware 之间的交互可能产生意想不到的副作用。这和 Express.js 中间件生态的老问题一模一样。

## 适用边界：什么时候 Harness Engineering 不灵？

到目前为止，我们看到的所有成功案例都来自 **编码任务**。但 Agent 的应用远不止写代码。以下是 Harness Engineering 的明确局限：

### 1. 创意型任务

代码有明确的对错（测试通过/不通过），但内容创作、设计、策略规划没有。验证闭环在这里失效——你没法用自动化测试判断一篇文章写得好不好。

### 2. 高度交互型任务

当前 Harness 假设 Agent 是自主运行的，人只在开始和结束介入。但客服对话、教学辅导、协作编辑等场景需要频繁的人机交互，Harness 的"批处理"范式不适用。

### 3. 探索性研究任务

Harness Engineering 的前提是"任务可以被提前拆解"。但研究型任务的特点恰恰是"不知道下一步该做什么"。feature_list.json 式的预规划在这里意义有限。

### 4. 跨组织/跨系统集成

三家公司的实验都在单一代码库内完成。当 Agent 需要跨系统操作（连接不同 API、协调多个团队的工作流），Harness 的复杂度会急剧上升。

### 5. 模型能力门槛以下

APEX-Agents benchmark 数据表明：最佳 pass@1 只有 24.0%，零分率 40%-62%。这说明对于真正复杂的专业任务（投资分析、法律研究），**模型本身的能力仍然是瓶颈**，Harness 救不了。Medium 文章作者的原话：

> 仅适用于模型能力基础线以上。低于该线，没有 Harness 能补偿不足。

## 工程落地建议：如果你真的要用

### 投入产出判断

在投入 Harness Engineering 之前，先问自己三个问题：

1. **你的 Agent 任务是否超过 30 分钟？** 短任务不需要复杂 Harness。
2. **你的任务是否可以被拆解为可验证的子任务？** 不能拆解 = Harness 核心机制失效。
3. **你有多少工程资源投入 Harness 维护？** OpenAI 提到需要预留 20% 时间处理 AI slop。

### 如果适合，从哪里开始

| 优先级 | 组件 | 投入 | 收益 |
|--------|------|------|------|
| P0 | 验证闭环 | 低 | 高——直接减少"假完成" |
| P0 | 状态持久化 | 低 | 高——Git + 进度文件即可启动 |
| P1 | 上下文管理 | 中 | 高——KV-cache 有 10x 成本差异 |
| P2 | 工具编排 | 中 | 中——先用少量通用工具 |
| P3 | 子代理委派 | 高 | 看场景——不要过早引入 |

### 容错设计

| 失败类型 | 恢复策略 |
|---------|---------|
| 工具调用失败 | 重试 + 指数退避 |
| 推理死循环 | LoopDetectionMiddleware |
| 上下文溢出 | Compaction → Summarization |
| 代码错误 | Git 回滚 + 恢复工作状态 |

### 成本估算

以 OpenAI 实验为参考（但要加折扣考虑营销因素）：
- KV-cache 优化前：~$3/MTok
- KV-cache 优化后：~$0.30/MTok
- 一个中等规模项目（10万行级别）的 Token 成本：$1,000-$5,000
- 人力成本：Harness 设计和维护约占总工程时间 20-30%

## 结论：好想法，坏营销

### Harness Engineering 真正教给我们的

1. **Agent 可靠性是系统工程问题**，不是模型选择问题——在模型能力达到基础线之后。
2. **验证闭环是最重要的单一组件**。如果你只能做一件事，给 Agent 加上强制验证。
3. **工具设计越简单越好**——至少在模型训练数据覆盖的领域是这样。
4. **状态持久化不难**，别把它想复杂了。Git + 进度文件可能就够了。

### 需要警惕的

1. **不要把特定场景的成功推广为通用方法论。** 代码生成不代表一切。
2. **不要盲信各家公司的数据。** 它们有明确的商业动机。
3. **不要低估 Harness 的维护成本。** 20% 的时间清理 AI slop 不是开玩笑。
4. **不要以为 Harness 能替代模型能力。** APEX-Agents 的数据很清楚。

### 一句话总结

Harness Engineering 是 Agent 领域的**必要基础设施**，但它不是银弹。把它当作汽车的底盘和悬挂——引擎（模型）不行，底盘再好也没用；引擎行了，底盘不好确实跑不远。

## 参考资料

1. [Anthropic - Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)（2025.11）
2. [OpenAI - Harness engineering: leveraging Codex in an agent-first world](https://openai.com/index/harness-engineering/)（2026.02）
3. [LangChain - Improving Deep Agents with harness engineering](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)（2026.02）
4. [Terminal Bench 2.0 Leaderboard](https://www.tbench.ai/leaderboard/terminal-bench/2.0)
5. [Medium - The Agent Harness Is the Architecture](https://medium.com/@epappas/the-agent-harness-is-the-architecture-and-your-model-is-not-the-bottleneck-5ae5fd067bb2)（2026.02）
6. [LangChain Deep Agents GitHub](https://github.com/langchain-ai/deepagents)

*本文基于 Anthropic、OpenAI、LangChain 官方博客、APEX-Agents benchmark 数据、Manus 及 Vercel 工程实践、Deep Agents 开源代码分析整理。作者对各家数据的可信度持保留态度。*
