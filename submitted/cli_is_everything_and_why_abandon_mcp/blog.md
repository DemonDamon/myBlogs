# MCP 已死？全面拥抱 CLI？—— 一份给 toB 团队的辩证指南

> 2026 年 3 月，Perplexity CTO 宣布弃用 MCP，转投 API 和 CLI；港科大开源的 CLI-Anything 拿下 11.7k Star。"MCP 已死"的声浪甚嚣尘上——但真相远比口号复杂。本文用 Benchmark 数据、源码分析和 B2B 生产案例，给出一份不站队、只解题的技术选型指南。

## 1. 一场 AI Agent 接口之争正在上演

2026 年 3 月 11 日，Perplexity CTO Denis Yarats 在 Ask 2026 大会上投下一颗炸弹：**公司内部正在放弃 MCP ，全面转向 API 和 CLI**。他给出的理由简单直接——上下文窗口消耗过大，认证流程摩擦太高。

几乎同一时间，Y Combinator 总裁 Garry Tan 也不留情面地给出三个字的评价：**"MCP sucks"**。他自己选择了构建 CLI 来完成工作，理由是更快、更可靠。

讽刺的是，这可能是 MCP 自 2024 年 11 月发布以来声量最高的时刻——一个"周年纪念"在寂静中度过，却在"宣告死亡"时获得了空前关注。

但问题远没有这么简单。MCP 真的该死吗？CLI 能一统天下吗？如果你是一个 toB 团队的技术负责人，面对的不是个人开发效率而是企业级生产环境，答案会怎样？

![AI Agent 工具接口选型决策树](images/decision_tree_cli_vs_mcp.png)

*图 1：本文的核心结论——选型取决于"你的 Agent 为谁服务"，而非 CLI 或 MCP 的绝对优劣*

## 2. MCP 的原罪：不可承受之"重"

### 2.1 线性上下文成本——最致命的问题

MCP 的工作模式是：定义一组带 Schema 的工具函数，注入 Agent 上下文，然后让 Agent 调用。这个设计有一个根本性问题——**每添加一个 MCP 工具，它的名称、描述、参数 Schema 和示例都会占用 Agent 的上下文窗口**。

Scalekit 团队对 GitHub 的 Copilot MCP Server 做了严格的 Benchmark（75 次测试运行，Claude Sonnet 4，相同任务、相同 Prompt，仅工具接口不同）。结果令人震惊：

![Token 消耗对比](images/24ce739d19b6fc29ea1a6841b8c85afd.png)

*图 2：Scalekit Benchmark 数据——同一任务下 CLI vs MCP 的 Token 消耗对比*

| 任务 | CLI（tokens） | MCP（tokens） | 倍率 |
|------|------------|-------------|------|
| 获取仓库语言和许可证 | 1,365 | 44,026 | **32×** |
| PR 详情和评审状态 | 1,648 | 32,279 | 20× |
| 仓库元数据 | 9,386 | 82,835 | 9× |
| 合并 PR 按贡献者统计 | 5,010 | 33,712 | 7× |
| 最新发布和依赖 | 8,750 | 37,402 | 4× |

最简单的任务——"这个仓库用什么语言写的？"——CLI Agent 只需 1,365 个 token，MCP Agent 需要 44,026 个。差距几乎完全来自 **schema 膨胀**：GitHub MCP Server 暴露 43 个工具的定义被全量注入每次对话，而 Agent 实际只用其中 1~2 个。

按 Claude Sonnet 4 的定价（$3/M input，$15/M output），每月运行 10,000 次操作：**CLI 约 $3.20，MCP 约 $55.20——17 倍的成本差距**。

### 2.2 可靠性之痛

成本高还能忍，不可靠就要命了。

![MCP 失败率](images/4b31692e9583d62c8369b38e9a4a708d.png)

*图 3：MCP 28% 的连接超时失败率 vs CLI 100% 可靠性*

在 Scalekit 的 25 次 MCP 测试中，**7 次失败**，失败率 28%。每次都是 TCP 级别的超时——远程 MCP Server 根本没有响应。不是协议错误，不是参数错误，纯粹是连接失败。而 CLI Agent 25 次全部成功，因为 `gh` 命令在本地运行，没有远程服务器可以超时。

除了连接问题，日常使用中 MCP 的摩擦还包括：

- **初始化不稳定**：MCP Server 作为子进程启动，经常需要重启 Claude Code 才能恢复
- **无休止的重认证**：每个 MCP 工具都需要单独走一遍认证流程
- **权限全有或全无**：无法限制为只读，无法约束参数范围

### 2.3 Eric Holmes 的一线观察

最早系统性批评 MCP 的是 Eric Holmes，他在 2026 年 2 月的博文 *"MCP is dead. Long live the CLI"* 中指出了三个 MCP 无法匹敌 CLI 的核心优势：

**可组合性**。分析一个大型 Terraform plan：

```bash
terraform show -json plan.out | jq '[.resource_changes[] | select(.change.actions[0] == "no-op" | not)] | length'
```

用 MCP？要么把整个 plan dump 进上下文（昂贵且通常不可行），要么在 MCP Server 端构建自定义过滤逻辑。CLI 用的是现成的、文档齐全的工具，人和 Agent 都能理解。

**可调试性**。当 Agent 对 Jira 做了意料之外的操作，用 CLI 你可以运行同一个 `jira issue view` 命令看到 Agent 看到的内容——输入一致，输出一致，没有谜团。用 MCP，你得翻 JSON transport log。

**Auth 已有成熟体系**。`aws` 用 profiles 和 SSO，`gh` 用 `gh auth login`，`kubectl` 用 kubeconfig。这些都是经过多年考验的认证流程，人类和 Agent 用法一致。

## 3. CLI 的文艺复兴：港科大 CLI-Anything 的启示

如果说 Eric Holmes 的博文是 CLI 路线的理论宣言，那么港科大数据科学实验室（HKUDS）开源的 **CLI-Anything** 项目就是这一路线的工程实证。

### 3.1 项目定位：一条命令让任意软件变成 Agent 原生工具

CLI-Anything 的核心理念清晰有力：**"Today's Software Serves Humans. Tomorrow's Users will be Agents."**

![CLI-Anything Teaser](images/6d311563391e3cd575b90b4390d42664.png)

*图 4：CLI-Anything 的愿景——让所有软件都变成 Agent 可控的 CLI 工具*

它要解决的问题是：AI Agent 擅长推理但无法操作真实的专业软件（GIMP、Blender、LibreOffice 等）。现有方案——GUI 自动化（脆弱）、有限 API（覆盖不足）、简化重实现（丢失 90% 功能）——都有严重缺陷。

CLI-Anything 的解法是：**给任意开源 GUI 软件自动生成一套 CLI harness，让 Agent 通过命令行操控真实软件后端**。

### 3.2 7阶段Pipeline：从源码到生产级 CLI

CLI-Anything 本质上是一个 **Prompt 驱动的方法论框架**（这一点很关键——它不是一个可执行的 Python pipeline 引擎，而是一份由 AI Agent 读取并自主执行的 SOP 文档 `HARNESS.md`）。

![CLI-Anything 架构](images/b98e5b2a94fa9d89fee50b69c32651cc.png)

*图 5：CLI-Anything 的 7 阶段自动化流水线架构*

7 个阶段的执行由 Agent 自主完成：

1. **Analyze** — 扫描源码，识别后端引擎、GUI-API 映射、数据模型
2. **Design** — 设计命令组、状态模型、输出格式
3. **Implement** — 构建 Click CLI，含 REPL 模式、JSON 输出、undo/redo
4. **Plan Tests** — 创建 TEST.md 测试计划
5. **Write Tests** — 实现单元测试和 E2E 测试
6. **Document** — 更新测试文档和结果
7. **Publish** — 生成 `setup.py`，`pip install -e .` 安装到 PATH

项目已覆盖 **11 个专业软件**（GIMP、Blender、Inkscape、Audacity、LibreOffice、OBS Studio、Kdenlive、Shotcut、Zoom、Draw.io、AnyGen），**1,508 个测试全部通过**，涵盖 1,073 个单元测试和 435 个端到端测试。

### 3.3 关键设计细节

深入 CLI-Anything 的源码，几个设计决策值得关注：

**Click CLI + REPL 双模式**。入口函数使用 `@click.group(invoke_without_command=True)`——有子命令时执行子命令，无子命令时自动进入交互式 REPL：

```python
# gimp/agent-harness/cli_anything/gimp/gimp_cli.py
@click.group(invoke_without_command=True)
@click.option('--json', '_json_output', is_flag=True)
@click.option('--project', type=click.Path())
def cli(ctx, _json_output, project):
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl)
```

**`--json` flag 全局可用**。Agent 获取结构化 JSON 用于编程消费，人类看到格式化表格用于调试——同一工具，双模输出。

**PEP 420 命名空间包**。`cli_anything/` 目录没有 `__init__.py`，这是 Python 命名空间包的标准做法，允许 `cli-anything-gimp`、`cli-anything-blender` 等多个独立包无冲突共存。

**Backend Wrapper 调用真实引擎**。CLI 生成的不是软件功能的"重实现"，而是调用真实软件后端——LibreOffice 真的生成 PDF，Blender 真的渲染 3D 场景。`HARNESS.md` 甚至特别强调"不信任退出码为 0"，要求验证输出文件的 magic bytes、ZIP 结构和像素分析。

### 3.4 CLI-Anything 证明了什么？

CLI-Anything 用 11.7k Star 和 1,508 个测试回答了一个关键问题：**CLI 是 LLM 的"母语"**。

LLM 在海量的 man pages、Stack Overflow 回答和 GitHub shell 脚本上训练过。给它一个 CLI 和 `--help`，它就能自发现、自使用。零 schema 注入开销，零发现步骤延迟。生成的 CLI 可组合（pipe/jq/grep）、可调试（人机一致的输入输出）、即装即用（`pip install -e .`）。

这正是 CLI 路线的最有力论证。

## 4. 且慢——MCP 真的一无是处吗？

如果文章到这里结束，结论就是"全面拥抱 CLI，抛弃 MCP"。但我们是工程师，不是布道者。让我们换一个角度看问题。

### 4.1 Inner Loop vs Outer Loop

CircleCI 在他们的技术博客中提出了一个非常实用的分析框架：**内循环（Inner Loop）和外循环（Outer Loop）**。

![Inner Loop vs Outer Loop](images/f296730b5e1c27260aab86557dd029ea.png)

*图 6：CircleCI 的内外循环框架——CLI 赢在内循环，MCP 赢在外循环*

**内循环**是开发者主动工作的地方：写代码、调试、在功能分支上快速迭代。反馈周期以秒到分钟计。在这里，CLI 完胜——零 schema 开销、训练数据熟悉度高、原生可组合。

**外循环**是代码从开发者手中走向生产的过程：CI/CD 流水线、代码审查、部署、安全检查、合规门控。在这里，Agent 需要跨越它不控制的系统——需要认证、需要结构化响应、需要可发现性、需要会话状态。CLI 在这些场景下的表现并不理想。

### 4.2 Scalekit 的灵魂拷问：你的 Agent 为谁服务？

Scalekit 团队在给出了令人信服的 Benchmark 数据之后，笔锋一转，提出了一个被大多数 "MCP is dead" 讨论忽略的关键问题：

> **"问题不是 CLI 还是 MCP，而是——你的 Agent 在为谁操作？"**

所有 CLI vs MCP 的 Benchmark（包括 Scalekit 自己的），测试的都是同一个场景：**单个开发者自动化自己的工作流**。在这个世界里，CLI 赢。显然的。

但绝大多数 AI 产品在生产中不是这样的。如果你在构建 B2B SaaS——一个项目管理工具、一个客服平台、一个代码审查助手——**你的 Agent 不是以"你"的身份行动，而是以客户的员工身份，在客户的组织里，触及客户控制的跨服务数据**。

想象一个场景：Acme Corp 的用户说"从这个 GitHub PR 创建一个 Jira ticket 并通知 Slack 团队"。你的 Agent 需要同时解析三层身份：

- **Agent 身份** — 哪个 Agent 在发起请求？（速率限制、滥用防范、审计追溯）
- **用户身份** — 哪个用户授权了这个操作？（Agent 只能做该用户能做的事）
- **租户身份** — 该用户属于哪个组织？（Acme 的仓库绝不能出现在 Globex 的 Jira 中）

现在试试用 `gh auth login` 解决这个问题——你的 Agent 继承的是你个人的 token。一个凭证，一个用户。乘以三个组织、几十个用户、每人在 GitHub/Jira/Slack 上有不同权限级别……**你相当于从零开始重建了半个 OAuth 体系**。

OpenClaw 已经用惨痛教训验证了这一点：10,000+ 暴露实例泄漏凭证和 API key，12% 的社区 Skills 被发现是恶意的（注入代码、窃取数据、建立持久化后门），770,000 个 Agent 因漏洞可被远程劫持。这些不是 OpenClaw 代码的 bug——**而是"shell 访问 + 环境凭证 + 零授权边界"这种架构模式在跨用户场景下的必然结果**。

### 4.3 MCP 的三个不可替代价值

MCP 让你付出的"协议税"换来了三样 CLI 无法提供的东西：

1. **Per-user 授权**。基于 OAuth 2.1 + PKCE，每个用户单独授权，可查看授权内容、可撤销。你的应用永远不碰用户凭证——这是通过企业安全审计的前提。

2. **显式工具边界**。Agent 只能调用声明的工具。没有任意 shell 命令，没有"Agent 自己发现了如何 `curl` 内部 API"的情况。每个操作有类型、有 scope、可预期——这是防止 OpenClaw 式失控的机制。

3. **结构化审计日志**。每个工具调用产生类型化记录：谁授权的、请求了什么、返回了什么。不是 shell history，而是结构化、可查询、可归因到特定用户和租户的审计数据——这是企业合规的硬性要求。

## 5. toB 落地的务实解法：CLI 为矛，MCP Gateway 为盾

讨论到这里，答案已经清晰：**CLI 和 MCP 解决的是不同层次的问题，toB 团队需要的不是二选一，而是分层选型**。

### 5.1 分层架构

![MCP Gateway 架构](images/a63ac20fc788477931f5ecd356a3d712.png)

*图 7：MCP Gateway——在 Agent 和上游 MCP Server 之间插入一个智能中间层*

**MCP Gateway** 是连接两个世界的桥梁，它解决了直连 MCP Server 的三大问题：

- **Schema 过滤**：不注入全部 43 个工具定义，只返回当前任务相关的 2~3 个。token 开销从 44,000 降到 ~3,000——逼近 CLI 效率。减少约 90%。
- **连接池**：不是每个 Agent 会话都建立自己的 TCP 连接，而是维护持久连接、吸收瞬态故障。28% 失败率降到 ~1%。
- **集中认证**：不是每个 Agent 自己管理 OAuth token，而是由 Gateway 统一处理 token 刷新、scope 执行和审计日志。单一认证边界，按租户隔离。

### 5.2 选型矩阵

| 场景 | 推荐方案 | Token 效率 | 可靠性 | 认证 | 月成本（10K ops） |
|------|---------|-----------|--------|------|----------------|
| 开发者自用/内部工具 | **CLI + Skills** | 最优 | 100% | 本人凭证 | ~$3 |
| SaaS 产品（代客户操作） | **MCP + Gateway** | ~CLI 范围 | ~99% | OAuth 2.1 + SSO | ~$5 |
| 多租户企业级 | **MCP Gateway + 策略引擎** | ~CLI 范围 | ~99% | 策略驱动 | ~$5+ |

![决策框架](images/6fe5500b842df9d06f92ca609e25be66.png)

*图 8：Scalekit 的决策框架——按部署场景匹配接口模态*

### 5.3 CLI-Anything 在 toB 中的具体落地路径

结合 CLI-Anything 的能力，一个 toB 团队可以这样落地：

**第一步：为内部专业软件生成 CLI harness。** 用 CLI-Anything 的 `/cli-anything` 命令，自动分析源码、生成 CLI、测试和打包。内循环中直接使用——开发者和 Agent 都通过同一个 CLI 操作，零学习成本。

**第二步：在 CI/CD 等内循环中直接调用 CLI。** 测试、构建、部署脚本中用 CLI 子进程调用，token 效率最高、可靠性 100%。配合 800 token 的 Skills tips 文件，进一步优化 Agent 的 CLI 使用效率（Scalekit 数据显示这比裸 CLI 减少三分之一的工具调用和延迟）。

**第三步：在面向客户的外循环中，通过 MCP Gateway 包装。** 当 Agent 需要代替客户操作外部系统时，不直接暴露 shell 权限，而是通过 MCP Gateway 提供受控的工具集——Schema 过滤、Per-user OAuth、租户隔离、审计日志一应俱全。

**需要注意的工程风险**：CLI-Anything 方案并非银弹。源码分析显示几个落地时必须评估的点：

- **依赖强模型**：7-Phase Pipeline 依赖 Claude Opus 4.6 / GPT-5.4 等前沿模型驱动。弱模型生成的 CLI 可能不完整，需要多轮 `/refine` 才能达到生产质量。
- **要求开源源码**：CLI-Anything 通过分析源码生成 CLI，闭源二进制软件不在覆盖范围内。toB 场景中如果涉及商业软件集成，需要另寻出路（如直接封装 REST API）。
- **Rendering Gap 陷阱**：GUI 软件在渲染时才应用效果。CLI 操作项目文件但渲染必须调用原生引擎（如 `libreoffice --headless`、`blender --background`），部署环境必须安装目标软件。
- **测试验证成本**：1,508 个测试的 100% 通过率是在特定环境下实现的，跨平台部署（尤其是容器化场景）需要重新验证。

这些风险可控但不可忽视，建议在 PoC 阶段充分验证后再大规模推广。

**核心原则：不要在"CLI vs MCP"之间做信仰之争，而是在正确的层选正确的工具。**

## 6. 总结：不要站队，要解题

回到文章开头的问题：MCP 已死？CLI 一统天下？

**"MCP 已死"是情绪，不是事实。"CLI 一统天下"是愿景，不是现实。**

让我们回归工程师的本分，看数据说话：

- CLI 在 token 效率上碾压 MCP（4~32 倍差距），在可靠性上完胜（100% vs 72%），在成本上优势巨大（$3 vs $55/月）
- 但当 Agent 从"服务开发者自己"跨越到"代替客户操作"时，CLI 的环境凭证、零隔离、无审计成为架构级风险
- CLI-Anything 证明了 CLI 路线在内循环中的可行性和优越性——11 个专业软件，1,508 个测试，100% 通过
- MCP 的价值不在于协议本身，而在于它强制实施的治理框架——Per-user OAuth、工具边界、审计日志
- MCP Gateway 是弥合两者的关键基础设施——以 CLI 的效率运行，以 MCP 的治理框架保护

**toB 团队的正确姿势**：CLI 为 default（内循环、开发者工具、成本敏感场景），MCP Gateway 为桥梁（外循环、多租户、合规要求）。不二选一，而是分层选型。

最后，借用 Eric Holmes 的话作为结尾：

> **"最好的工具是人类和机器都好用的工具。CLI 经历了几十年的设计迭代。它们可组合、可调试，依附于已有的认证体系。MCP 试图构建一个更好的抽象层——但事实证明，我们已经拥有一个足够好的了。"**

关键在于：在那些 CLI"足够好"的地方全力拥抱它，在那些 CLI 力不从心的地方理性引入 MCP Gateway。这不是妥协，而是工程上的正解。

**参考资料**

1. Eric Holmes. *MCP is dead. Long live the CLI.* (2026-02-28) — [ejholmes.github.io](https://ejholmes.github.io/2026/02/28/mcp-is-dead-long-live-the-cli.html)
2. Scalekit. *MCP is up to 32× more expensive than CLI. Here's why we still use it.* (2026-03-11) — [scalekit.com](https://www.scalekit.com/blog/mcp-vs-cli-use)
3. CircleCI. *MCP vs. CLI for AI-native development.* (2026-03-11) — [circleci.com](https://circleci.com/blog/mcp-vs-cli/)
4. AwesomeAgents. *Perplexity CTO Moves Away from MCP Toward APIs and CLIs.* (2026-03-11) — [awesomeagents.ai](https://awesomeagents.ai/news/perplexity-agent-api-mcp-shift/)
5. Runlayer. *MCP vs CLI Tools: Which is best for production applications?* (2026-01-25) — [runlayer.com](https://www.runlayer.com/blog/mcp-vs-cli-for-ai-agents-choosing-the-right-interface)
6. HKUDS. *CLI-Anything: Making ALL Software Agent-Native.* — [github.com/HKUDS/CLI-Anything](https://github.com/HKUDS/CLI-Anything)
7. AITNT. *MCP已死，CLI当立！Perplexity首先放弃使用MCP，全网赞成.* (2026-03-13) — [aitntnews.com](https://www.aitntnews.com/newDetail.html?newId=23086)
