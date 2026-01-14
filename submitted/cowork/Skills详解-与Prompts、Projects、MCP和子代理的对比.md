# Skills explained: How Skills compares to prompts, Projects, MCP, and subagents

> 来源：https://claude.com/blog/skills-explained
> 
> Skills是创建自定义AI工作流程和代理的越来越强大的工具，但它们在Claude堆栈中的位置是什么？我们解释何时使用什么工具——以及它们如何协同工作。

- **分类**: Agents
- **产品**: Claude apps, Claude Developer Platform
- **日期**: November 13, 2025
- **阅读时间**: 5分钟

---

自引入Skills以来，人们一直有兴趣了解Claude代理生态系统的各个组件如何协同工作。

无论你是在Claude Code中构建复杂的工作流程，使用API创建企业解决方案，还是在Claude.ai上最大化你的生产力，知道何时使用什么工具——以及何时使用——可以改变你与Claude的工作方式。

本指南分解了每个构建块，解释了何时使用什么，并向你展示如何将它们组合起来创建强大的代理工作流程。

## 理解你的代理构建块

### 什么是Skills？

Skills是包含指令、脚本和资源的文件夹，Claude在任务相关时发现并动态加载它们。将它们视为专业培训手册，为Claude提供特定领域的专业知识——从使用Excel电子表格到遵循你组织的品牌指南。

**Skills如何工作：** 当Claude遇到任务时，它扫描可用的Skills以找到相关匹配。Skills使用渐进式披露：首先加载元数据（~100 tokens），提供足够的信息让Claude知道何时Skill是相关的。需要时加载完整指令（<5k tokens），捆绑的文件或脚本仅在需要时加载。

**何时使用Skills：** 当你需要Claude一致且高效地执行专业任务时，选择Skills。它们非常适合：

* **组织工作流程**：品牌指南、合规程序、文档模板
* **领域专业知识**：Excel公式、PDF操作、数据分析
* **个人偏好**：笔记系统、编码模式、研究方法

**示例：** 创建一个品牌指南Skill，包括你公司的调色板、排版规则和布局规范。当Claude创建演示文稿或文档时，它会自动应用这些标准，而无需你每次都解释它们。

[了解更多关于Skills](https://claude.com/blog/skills)并查看我们不断增长的[Skills库](https://github.com/anthropics/agent-skills)。

### 什么是Prompts？

Prompts是你在对话期间以自然语言提供给Claude的指令。它们是短暂的、对话式的和反应式的——你在当下提供上下文和方向。

**何时使用Prompts：** 使用Prompts用于：

* 一次性请求："总结这篇文章"
* 对话式改进："让那个语气更专业"
* 即时上下文："分析这些数据并识别趋势"
* 临时指令："将其格式化为项目符号列表"

**示例：**

```
请对此代码进行全面安全审查。我正在寻找：

1. 常见漏洞，包括：
   - 注入缺陷（SQL、命令、XSS等）
   - 身份验证和授权问题
   - 敏感数据暴露
   - 安全配置错误
   - 访问控制破坏
   - 加密失败
   - 输入验证问题
   - 错误处理和日志记录问题

2. 对于你发现的每个问题，请提供：
   - 严重程度级别（严重/高/中/低）
   - 代码中的位置（行号或函数名）
   - 解释为什么它是安全风险以及如何被利用
   - 具体的修复建议，尽可能提供代码示例
   - 防止类似问题的最佳实践指导

3. 代码上下文：[描述代码的作用、语言/框架及其运行环境 - 例如，"这是一个处理用户身份验证和处理支付数据的Node.js REST API"]

4. 其他考虑因素：
   - 是否存在任何OWASP Top 10漏洞？
   - 代码是否遵循[特定框架/语言]的安全最佳实践？
   - 是否有已知漏洞的依赖项？

请按严重程度和潜在影响对发现进行优先级排序。
```

**专业提示：** Prompts是你与Claude交互的主要方式，但它们不会在对话之间持续存在。对于重复的工作流程或专业知识，考虑将Prompts捕获为Skills或项目指令。

**何时使用Skill代替：** 如果你发现自己跨多个对话重复输入相同的提示，是时候创建Skill了。将重复的指令（如"使用OWASP标准审查此代码的安全漏洞"或"将此分析格式化为执行摘要、关键发现和建议"）转换为Skills。这可以节省你每次重新解释程序的时间，并确保一致的执行。

查看我们的[提示库](https://claude.com/resources/prompts)、[提示最佳实践](https://docs.anthropic.com/en/docs/prompt-engineering)，或我们的[智能提示制作器](https://claude.com/resources/prompt-maker)开始使用。

### 什么是Projects？

Projects在所有付费Claude计划中可用，是具有自己的聊天历史记录和知识库的自包含工作空间。每个项目包括一个200K上下文窗口，你可以在其中上传文档、提供上下文并设置适用于该项目内所有对话的自定义指令。

**Projects如何工作：** 你上传到项目知识库的所有内容在该项目内的所有聊天中都可用。Claude自动使用此上下文来提供更明智、更相关的响应。当你的项目知识接近上下文限制时，Claude无缝启用检索增强生成（RAG）模式，将容量扩展最多10倍。

**何时使用Projects：** 当你需要时选择Projects：

* **持久上下文**：应该为每次对话提供信息的背景知识
* **工作空间组织**：不同计划的独立上下文
* **团队协作**：共享知识和对话历史（在Team和Enterprise计划上）
* **自定义指令**：项目特定的语气、观点或方法

**示例：** 创建一个"Q4产品发布"项目，包含市场研究、竞争对手分析和产品规格。此项目中的每次聊天都可以访问这些知识，而无需你重新上传或重新解释上下文。

**何时使用Skill代替：** Projects为特定工作主体（你公司的代码库、研究计划、正在进行的客户参与）为Claude提供持久上下文。Skills教Claude如何做某事。Project可能包含你产品发布的所有背景，而Skill可以教你团队的写作标准或代码审查流程。如果你发现自己跨多个Projects复制相同的指令，这是创建Skill的信号。

[了解更多关于Projects](https://claude.com/resources/projects)。

### 什么是Subagents？

Subagents是具有自己的上下文窗口、自定义系统提示和特定工具权限的专业AI助手。在Claude Code和Claude Agent SDK中可用，Subagents独立处理离散任务并将结果返回给主代理。

**Subagents如何工作：** 每个Subagent使用自己的配置运行——你定义它做什么、它如何解决问题以及它可以访问哪些工具。Claude根据它们的描述自动将任务委托给适当的Subagents，或者你可以明确请求特定的Subagent。

**何时使用Subagents：** 使用Subagents用于：

* **任务专业化**：代码审查、测试生成、安全审计
* **上下文管理**：保持主对话专注，同时卸载专业工作
* **并行处理**：多个Subagents可以同时处理不同方面
* **工具限制**：将特定Subagents限制为安全操作（例如，只读访问）

**示例：**

```plaintext
创建一个代码审查Subagent，可以访问Read、Grep和Glob工具，但不能访问Write或Edit。当你修改代码时，Claude自动委托给此Subagent进行质量和安全审查，而不会冒意外代码更改的风险。
```

**何时使用Skill代替：** 如果多个代理或对话需要相同的专业知识——如安全审查程序或数据分析方法——创建Skill而不是将该知识构建到各个Subagents中。Skills是可移植和可重用的，而Subagents是为特定工作流程构建的。使用Skills来教授任何代理都可以应用的专业知识；当你需要具有特定工具权限和上下文隔离的独立任务执行时，使用Subagents。

[了解更多关于Subagents](https://docs.anthropic.com/en/docs/claude-code/subagents)。

### 什么是MCP？

MCP在AI应用程序和你现有的工具和数据源之间创建通用连接层。

模型上下文协议（MCP）是一个开放标准，用于将AI助手连接到数据所在的外部系统——内容存储库、业务工具、数据库和开发环境。

**MCP如何工作：** MCP提供了一种标准化方式将Claude连接到你的工具和数据源。不是为每个数据源构建自定义集成，而是针对单个协议构建。MCP服务器公开数据和功能；MCP客户端（如Claude）连接到这些服务器。

**何时使用MCP：** 当你需要Claude时选择MCP：

* 访问外部数据：Google Drive、Slack、GitHub、数据库
* 使用业务工具：CRM系统、项目管理平台
* 连接到开发环境：本地文件、IDE、版本控制
* 与自定义系统集成：你的专有工具和数据源

**示例：** 通过MCP将Claude连接到你公司的Google Drive。现在Claude可以搜索文档、读取文件并引用内部知识，而无需手动上传——连接持续存在并自动更新。

**何时使用Skill代替：** MCP将Claude连接到数据；Skills教Claude如何处理该数据。如果你正在解释如何使用工具或遵循程序——如"查询我们的数据库时，始终首先按日期范围过滤"或"使用这些特定公式格式化Excel报告"——那是Skill。如果你需要Claude首先访问数据库或Excel文件，那是MCP。一起使用两者：MCP用于连接，Skills用于程序知识。

[了解更多关于MCP](https://docs.anthropic.com/en/docs/build-with-claude/mcp)并查看[如何构建MCP服务器](https://modelcontextprotocol.io/)的文档。

## 它们如何协同工作

真正的力量出现在你将这些构建块组合在一起时。每个都有不同的目的，它们一起创建复杂的代理工作流程。

### 对比：选择正确的工具

| 功能              | Skills                       | Prompts                       | Projects             | Subagents         | MCP                   |
| ----------------- | ---------------------------- | ----------------------------- | -------------------- | ----------------- | --------------------- |
| **它提供什么**    | 程序知识                     | 即时指令                       | 背景知识             | 任务委托           | 工具连接               |
| **持久性**        | 跨对话                       | 单次对话                       | 项目内               | 跨会话             | 持续连接               |
| **包含**          | 指令 + 代码 + 资源           | 自然语言                       | 文档 + 上下文        | 完整代理逻辑       | 工具定义               |
| **何时加载**      | 动态，按需                   | 每次轮次                       | 始终在项目中         | 调用时             | 始终可用              |
| **可以包含代码**  | 是                           | 否                            | 否                   | 是                 | 是                    |
| **最适合**        | 专业知识                     | 快速请求                       | 集中上下文           | 专业任务           | 数据访问              |

### 示例代理工作流程：研究代理

让我们构建一个结合多个构建块的综合研究代理。此示例展示如何组装和激活用于竞争分析的代理。

**步骤1：设置你的Project**

创建一个"竞争情报"项目并上传：

* 行业报告和市场分析
* 竞争对手产品文档
* 来自你CRM的客户反馈
* 以前的研究摘要

添加项目指令：

```
通过我们产品战略的视角分析竞争对手。专注于差异化机会和新兴市场趋势。用具体证据和可操作建议呈现发现。
```

**步骤2：通过MCP连接数据源**

启用MCP服务器用于：

* Google Drive（访问共享研究文档）
* GitHub（审查竞争对手开源存储库）
* Web搜索（实时市场信息）

**步骤3：创建专业Skills**

创建一个"competitive-analysis" skill：

```plaintext
# My Company GDrive Navigation Skill

## Overview
针对Meridian Tech的Google Drive结构优化的搜索和检索策略。使用此skill高效定位内部文档、研究和战略材料。

## Drive Organization

**顶级结构：**
- `/Strategy & Planning/` - OKRs、季度计划、董事会演示
- `/Product/` - PRD、路线图、技术规格
- `/Research/` - 市场研究、竞争情报、用户研究
- `/Sales & Marketing/` - 案例研究、演示文稿、活动材料
- `/Customer Success/` - 实施指南、成功指标
- `/Company Ops/` - 政策、组织架构、团队目录

**命名约定：**
- 格式：`YYYY-MM-DD_DocumentName_vX`
- 最终版本标记为`_FINAL`
- 草稿包括`_DRAFT`或`_WIP`

## Search Best Practices

1. **先广泛，然后过滤** - 使用文件夹上下文 + 关键词
2. **定位文档所有者** - 来自Sales/的销售材料，不是根目录
3. **检查最近性** - 优先考虑过去6个月的文档以获取当前战略
4. **寻找"真相来源"** - 带有`_FINAL`、`_APPROVED`的文件，或在`/Archives/Official/`中

## Research Agent Workflow

1. 识别主题类别（产品、市场、客户）
2. 使用目标关键词搜索相关文件夹
3. 检索3-5个最新/相关文档
4. 与`/Strategy & Planning/`交叉引用以获取上下文
5. 引用来源，包括文件名和日期
```

**步骤4：配置Subagents（仅Claude Code/SDK）**

创建专业Subagents：

`market-researcher` Subagent：

```plaintext
name: market-researcher
description: 研究市场趋势、行业报告和竞争格局数据。主动用于竞争分析。
tools: Read, Grep, Web-search
---
你是一位专门从事竞争情报的市场研究分析师。

研究时：
1. 识别权威来源（Gartner、Forrester、行业报告）
2. 收集定量数据（市场份额、增长率、融资）
3. 分析定性见解（分析师意见、客户评论）
4. 综合趋势和模式

用引用和置信度水平呈现发现。
```

`technical-analyst` Subagent：

```plaintext
name: technical-analyst
description: 分析技术架构、实施方法和工程决策。用于技术竞争分析。
tools: Read, Bash, Grep
---
你是一位分析竞争对手技术选择的技术架构师。

分析时：
1. 审查公共存储库和技术文档
2. 评估架构模式和技术栈
3. 评估可扩展性和性能方法
4. 识别技术优势和局限性

专注于可操作的技术见解，为我们的产品决策提供信息。
```

**步骤5：激活你的研究代理**

现在当你问Claude："分析我们前三大竞争对手如何定位他们的新AI功能，并识别我们可以利用的差距"

以下是发生的事情：

1. **Project上下文加载**：Claude访问你上传的研究文档并遵循项目指令
2. **MCP连接激活**：Claude搜索你的Google Drive以获取最近的竞争对手简报并拉取GitHub数据
3. **Skills参与**：competitive-analysis Skill提供分析框架
4. **Subagents执行**（在Claude Code中）：market-researcher收集行业数据，而technical-analyst审查技术实施
5. **Prompts细化**：你提供对话指导："特别关注医疗保健领域的企业客户"

**结果：** 一个全面的竞争分析，从多个数据源提取，遵循你的分析框架，利用专业知识，并在整个研究项目中保持上下文。

## 常见问题

#### Skills如何工作？

Skills使用渐进式披露来保持Claude的效率。在处理任务时，Claude首先扫描Skill元数据（描述和摘要）以识别相关匹配。如果Skill匹配，Claude加载完整指令。最后，如果Skill包含可执行代码或参考文件，这些仅在需要时加载。

这种架构意味着你可以拥有许多可用的Skills，而不会使Claude的上下文窗口过载。Claude在需要时准确访问它需要的内容。

#### Skills vs. Subagents：何时使用什么

**使用Skills当：** 你想要任何Claude实例都可以加载和使用的功能。Skills就像培训材料——它们使Claude在所有对话中更好地执行特定任务。

**使用Subagents当：** 你需要为特定目的设计的完整、自包含的代理，独立处理工作流程。Subagents就像具有自己上下文和工具权限的专业员工。

**一起使用它们当：** 你想要具有专业知识的Subagents。例如，代码审查Subagent可以使用Skills获取特定语言的最佳实践，将Subagent的独立性与Skills的可移植专业知识相结合。

#### Skills vs. Prompts：何时使用什么

**使用Prompts当：** 你提供一次性指令、提供即时上下文或进行对话式来回。Prompts是反应式和短暂的。

**使用Skills当：** 你有需要重复的程序或专业知识。Skills是主动的——Claude知道何时应用它们——并在对话之间持续存在。

**一起使用它们：** Prompts和Skills自然互补。使用Skills提供基础专业知识，然后使用Prompts为每个任务提供特定上下文和细化。

#### Skills vs. Projects：何时使用什么

**使用Projects当：** 你需要应该为特定计划的所有对话提供信息的背景知识和上下文。Projects提供始终加载的静态参考材料。

**使用Skills当：** 你需要仅在相关时激活的程序知识和可执行代码。Skills提供按需加载的动态专业知识，节省你的上下文窗口。

**一起使用它们当：** 你想要持久上下文和专业功能。例如，一个"产品开发"项目包含产品规格和用户研究，结合Skills用于创建技术文档和分析用户反馈数据。

**关键区别：** Projects说"这是你需要知道的。"Skills说"这是如何做事的。"Projects提供你工作的知识库。Skills提供在任何地方工作的功能——任何对话、任何项目。

#### Subagents可以使用Skills吗？

是的。在Claude Code和Agent SDK中，Subagents可以像主代理一样访问和使用Skills。这创建了强大的组合，其中专业Subagents利用可移植的专业知识。

例如，你的python-developer Subagent可以使用pandas-analysis Skill来执行遵循你团队约定的数据转换，而你的documentation-writer Subagent使用technical-writing skill来一致地格式化API文档。

## 开始使用

准备好使用Skills构建了吗？以下是如何开始：

**Claude.ai用户：**

* 在设置 → 功能中启用Skills
* 在claude.ai/projects创建你的第一个项目
* 尝试将项目知识与Skills结合用于你的下一个分析任务

**API开发者：**

* 在[文档](https://docs.anthropic.com/en/docs/build-with-skills)中探索Skills端点
* 查看我们的[skills cookbook](https://github.com/anthropics/agent-skills)

**Claude Code用户：**

* 通过插件市场安装Skills
* 查看我们的[skills cookbook](https://github.com/anthropics/agent-skills)

---

## 相关文章

- [Cowork: Claude Code for the rest of your work](https://claude.com/blog/cowork-claude-code-for-the-rest-of-your-work) (Jan 12, 2026)
- [How to create Skills: Key steps, limitations, and examples](https://claude.com/blog/how-to-create-skills) (Nov 19, 2025)
- [Extending Claude's capabilities with skills and MCP servers](https://claude.com/blog/extending-claudes-capabilities-with-skills-and-mcp-servers) (Dec 19, 2025)
- [Skills for organizations, partners, the ecosystem](https://claude.com/blog/skills-for-organizations-partners-the-ecosystem) (Dec 18, 2025)
