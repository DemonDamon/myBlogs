# 同日双发：GPT-5.3-Codex 与 Opus 4.6 的技术路线分野

> 2026.02.05，OpenAI 与 Anthropic 前后脚发布各自新一代代码模型。这不是一次常规更新，而是两种工程哲学的正面碰撞。本文基于双方官方公告、System Card 及 Anthropic 工程博客一手源进行拆解。

![cover](images/logo.png)

2026 年 2 月 5 日深夜，OpenAI 和 Anthropic 几乎同时发布了各自的新一代代码模型——GPT-5.3-Codex 和 Claude Opus 4.6。媒体称之为"AI 编程战争的升级"，但真正值得拆解的不是"谁先发了几分钟"，而是两款模型背后**截然不同的技术路线选择**。

GPT-5.3-Codex 选择了**效率优先**：同等任务 Token 消耗减半，单 Token 处理速度提升 25%，并首次实现了 AI 模型的自举——模型参与构建和部署自身。Opus 4.6 走的是**深度优先**：100 万 Token 上下文窗口、多 Agent 协作机制（Agent Teams），以及一个足以震撼行业的工程验证——16 个 AI Agent 在 11 天内用 Rust 写出 10 万行 C 编译器代码。

本文从 Benchmark 数据、技术架构、成本结构、适用场景四个维度，拆解这场对决背后的技术逻辑。

## 核心规格：效率 vs 深度

| 维度 | GPT-5.3-Codex | Claude Opus 4.6 |
|:------|:---------------|:-----------------|
| 发布方 / 日期 | OpenAI / 2026.02.05 | Anthropic / 2026.02.05 |
| 核心定位 | 最强交互式高效编程模型 | 长任务 + 复杂协作的最聪明模型 |
| 上下文窗口 | 标准级别（未明确公开） | **100 万 Token**（Beta） |
| 最大输出长度 | 标准 | **128K Token**（新增） |
| Token 效率 | **仅需前代一半** | 标准 |
| 处理速度 | **比前代快 25%** | 支持 4 级 Effort 控制（low/medium/high/max） |
| 杀手级特性 | 自举——帮助构建和部署自身 | Agent Teams——多 Agent 并行协作 |
| API 定价（输入 / 输出） | 未公布 | $5 / $25（每百万 Token）；>200K 上下文 Premium $10 / $37.50 |
| 硬件基座 | NVIDIA GB200 NVL72 | 未公布 |

路线分野一目了然：GPT-5.3-Codex 的核心叙事是 **"更快更省"**，Opus 4.6 的核心叙事是 **"更深更广"**。

## Benchmark 全景

下图是 Anthropic 官方发布的全维度 Benchmark 对比表，涵盖编程、推理、搜索、计算机使用等多个能力维度：

![Anthropic 官方 Benchmark 全维度对比表](images/0dc38cd00e54e1252cbd47450889038f.jpg)

### 核心 Benchmark 对比

直接看数据。下表汇总了两款模型在主流基准测试中的表现（数据来源：双方官方公告 + System Card Appendix）：

| 基准测试 | 测试能力 | GPT-5.3-Codex | Opus 4.6 | 差距 | 胜者 |
|:---------|:---------|:-------------|:---------|:-----|:-----|
| Terminal-Bench 2.0 | 终端多步编程 | **77.3%** | 65.4% | +11.9pp | GPT-5.3 |
| SWE-Bench Pro | 多语言软件工程（4 语言） | **56.8%** | — | — | GPT-5.3 |
| SWE-bench Verified | 标准化软件工程（Python） | 74.5~76% | **80.8%** | ~5pp | Opus 4.6 |
| SWE-Lancer IC Diamond | 真实自由职业编程任务 | **81.4%** | — | — | GPT-5.3 |
| OSWorld-Verified | GUI 操作 / 跨应用 | 64.7% | **72.7%** | -8.0pp | Opus 4.6 |
| Cybersecurity CTF | 安全攻防挑战 | **77.6%** | — | — | GPT-5.3 |
| BrowseComp | 开放网络信息检索 | — | **84.0%** | — | Opus 4.6 |
| ARC-AGI-2 | 新问题泛化推理 | — | **68.8%** | — | Opus 4.6 |
| MRCR v2（1M ctx） | 长上下文检索 | — | **76.0%** | — | Opus 4.6 |
| GDPval-AA | 知识工作 Elo 评分 | 70.9%（wins/ties） | **+144 Elo vs GPT-5.2** | — | Opus 4.6 |
| Humanity's Last Exam | 跨学科复杂推理 | — | **领先所有前沿模型** | — | Opus 4.6 |

### 关键洞察

**GPT-5.3-Codex 在终端编程上拉开了断层级差距。** 77.3% 的 Terminal-Bench 得分比前代 GPT-5.2-Codex（64.0%）提升了 13.3pp，领先 Opus 4.6 将近 12pp。值得注意的是，OpenAI 还新增了 SWE-Bench Pro（多语言、抗污染）和 SWE-Lancer IC Diamond（真实自由职业任务报酬衡量）两个更严格的评测，GPT-5.3-Codex 均拿下最高分。

![Anthropic 官方 Terminal-Bench 2.0 对比图](images/29715d396f5462ed52036e2c2593295c.jpg)

**GPT-5.3-Codex 在 OSWorld 上实现了跨代飞跃。** 官方 Appendix 显示 GPT-5.3-Codex（64.7%）vs GPT-5.2-Codex（38.2%），**+26.5pp 的代际提升**——这是所有 Benchmark 中单项代际提升最大的。虽然仍落后 Opus 4.6（72.7%），但 OpenAI 在计算机操作能力上的追赶速度惊人。

**Opus 4.6 的优势更分散但更全面。** 在 GUI 操作（OSWorld）、信息检索（BrowseComp）、泛化推理（ARC-AGI-2）上均领先。尤其 BrowseComp 从前代的 67.8% 跃升至 84.0%（+16.2pp），在"研究型 Agent 行为"——搜索、筛选、组合信息——上实现了质变。在 GDPval-AA 知识工作评估中，Opus 4.6 以 +144 Elo 领先 GPT-5.2，进一步印证了其在推理密集型任务上的全面统治力。

![Anthropic 官方 GDPval-AA 知识工作对比图](images/83e10e51b155ea4c70d6b97a9138e81d.jpg)

**长上下文是 Opus 4.6 的杀手级优势。** MRCR v2 测试中，在 100 万 Token、8-needle 条件下，Opus 4.6 拿到 76%，而 Sonnet 4.5 仅 18.5%。57.5pp 的差距不是"好一点差一点"，而是 **"能用"和"不能用"** 的本质区别。Anthropic 将此称为解决了"上下文腐烂"（context rot）——超长上下文中信息不再随距离衰减至不可用。
![Opus 4.6 长上下文检索能力对比](images/d62fcbe8157b3c82258b994b6d7d72b7.jpg)


### 代际提升对比

| 模型系列 | 基准 | 前代 → 新代 | 提升幅度 |
|:---------|:------|:------------|:---------|
| GPT 系列 | Terminal-Bench | 64.0% → 77.3% | **+13.3pp** |
| GPT 系列 | OSWorld-Verified | 38.2% → 64.7% | **+26.5pp** |
| GPT 系列 | Cybersecurity CTF | 67.4% → 77.6% | **+10.2pp** |
| Opus 系列 | Terminal-Bench | 59.8% → 65.4% | +5.6pp |
| Opus 系列 | OSWorld | 66.3% → 72.7% | +6.4pp |
| Opus 系列 | BrowseComp | 67.8% → 84.0% | **+16.2pp** |
| Opus 系列 | MRCR v2（vs Sonnet 4.5） | 18.5% → 76.0% | **+57.5pp** |

GPT-5.3-Codex 在 OSWorld 上的 +26.5pp 是所有单项中最大的代际跃升；Opus 4.6 在 BrowseComp 和 MRCR v2 上实现了质变级进步。两条路线各自在核心赛道上狂飙。

## Agent Teams：16 个对等 Agent、11 天、10 万行 C 编译器

Opus 4.6 最具说服力的不是 Benchmark 数字，而是那个 C 编译器项目。以下分析基于 Anthropic 研究员 **Nicholas Carlini** 发布的[工程博客一手源](https://www.anthropic.com/engineering/building-c-compiler)。

> "This project was designed as a capability benchmark. I am interested in stress-testing the limits of what LLMs can *barely* achieve today in order to help us prepare for what models will reliably achieve in the future."
> — Nicholas Carlini

### 项目投入与产出

| 维度 | 数据 |
|:------|:------|
| 目标 | 从零用 Rust 编写完整 C 编译器，能编译 Linux 内核 |
| 耗时 | ~11 天（两周） |
| 人力投入 | 1 名人类研究者 + 16 个并行 AI Agent |
| 会话数 | ~2,000 次 Claude Code 会话 |
| Token 消耗 | ~20 亿输入 + ~1.4 亿输出 |
| API 成本 | ~$20,000 |
| 代码产出 | ~10 万行 Rust 代码 |

### 能力矩阵与边界

| 能力项 | 状态 | 备注 |
|:-------|:------|:------|
| 目标架构 | ✅ x86 / ARM / RISC-V | 三架构完整支持 |
| 编译 Linux 6.9 内核 | ✅ | 可构建可启动 |
| 编译大型项目 | ✅ | QEMU / FFmpeg / Redis / PostgreSQL / SQLite |
| GCC torture test 通过率 | ✅ | ~99% |
| 编译并运行 Doom | ✅ | 开发者终极试金石 |
| Clean-room 实现 | ✅ | 全程无互联网访问，仅依赖 Rust 标准库 |
| 16 位 x86 编译 | ❌ | 输出代码超 60KB（Linux 限制 32KB），需调用 GCC |
| Assembler / Linker | ❌ | 开始自动化但仍不稳定，演示视频使用 GCC 的 |
| 生成代码效率 | ❌ | 全部优化开启仍低于 GCC 全部优化禁用 |
| Rust 代码质量 | ❌ | 尚可，远不及专家级 |

### 架构拆解：扁平对等，无调度层

这是理解 Agent Teams 最关键的一点。**项目不存在"主导 Agent"或"调度层"**——Nicholas Carlini 在一手源中明确写道：

> "I don't use an orchestration agent. Instead, I leave it up to each Claude agent to decide how to act."

实际架构如下：
![](images/image.png)

每个 Agent 运行在独立 Docker 容器中，挂载到同一个 **Git 裸仓库**（`/upstream`）。所有 Agent 读同一份 `AGENT_PROMPT.md`，自主决定"下一个最明显的问题"是什么。协调完全依赖 Git 语义——不存在中间调度服务。

### 三个关键工程决策

**1. 文件锁 + Git 冲突作为分布式协调。** Agent 通过在 `current_tasks/` 下写文本文件"锁定"任务。若两个 Agent 认领同一任务，Git push 的冲突机制迫使后来者改选。完成后推送改动、移除锁。这是一个极其朴素但有效的方案——不依赖任何外部协调服务。合并冲突频繁发生，但"Claude is smart enough to figure that out"。

**2. GCC Oracle 策略解决 Agent 拥塞。** 当任务池收缩到只剩"编译 Linux 内核"这一个巨型任务时，所有 Agent 命中同一 Bug，互相覆盖修复——16 个 Agent 跑着跟 1 个没区别。解决方案是用 GCC 作为"已知正确编译器 Oracle"：随机用 GCC 编译大部分内核文件，只让少量文件走 Claude 编译器。如果内核能启动，说明 Claude 的那部分没问题；如果崩溃，就进一步缩小范围。这让每个 Agent 能并行修复不同文件中的不同 Bug。

**3. 围绕 LLM 固有限制设计测试框架。** 两类限制需要工程应对：
- **上下文窗口污染**：测试框架最多打印几行输出，详细信息写文件；日志用 `ERROR` 标记便于 grep；预计算汇总统计避免原始数据进入上下文。
- **时间盲**：LLM 无法感知时间，会"快乐地花几小时跑测试"。`--fast` 选项默认只跑 1%~10% 随机子样本。子样本对单 Agent 确定性可复现，跨 Agent 随机分散——既保证调试可重复，又通过多 Agent 提高整体覆盖率。

### 跨代能力演进

一手源透露了一个重要背景：C 编译器项目并非 Opus 4.6 的一次性展示，而是**跨整个 Claude 4 系列的持续性能力基准**：

| Claude 版本 | 编译器能力 |
|:------------|:-----------|
| 早期 Opus 4.x | 几乎无法产出功能性编译器 |
| **Opus 4.5** | 首次跨过门槛：能通过大型测试集，但无法编译真实项目 |
| **Opus 4.6** | 10 万行代码，编译 Linux 内核 + 多个大型开源项目 |

这个渐进过程说明：Agent Teams 的成功不仅靠协作机制，更根本的前提是**单 Agent 能力的代际跃升**。

## 自举突破：模型参与构建自身

GPT-5.3-Codex 的核心叙事是一个更抽象但同样意义深远的概念——**自举（Bootstrapping）**。OpenAI 官方公告明确描述了自举的具体场景：

> "The Codex team used early versions to debug its own training, manage its own deployment, and diagnose test results and evaluations—our team was blown away by how much Codex was able to accelerate its own development."

这不是笼统的"模型帮忙写代码"，而是 GPT-5.3-Codex 的早期版本参与了自身后续版本的四类核心工作：

| 自举场景 | 具体内容 |
|:---------|:---------|
| **训练调试** | 监控并调试当前 release 的训练 run，追踪训练全程行为模式 |
| **部署管理** | 动态扩展 GPU 集群以应对流量高峰，保持延迟稳定 |
| **评测诊断** | 深度分析交互质量，对比不同版本的行为差异 |
| **工程加速** | 识别 context rendering bug、定位缓存命中率低的根因、构建可视化分析应用 |

一个具体案例：alpha 测试期间，一位研究员想了解 GPT-5.3-Codex 每轮对话的增量工作量和生产力差异。GPT-5.3-Codex 自己设计了多个 regex 分类器来估算澄清频率、正负反馈、任务进展，然后大规模运行在所有会话日志上，3 分钟内生成分析报告。

| 指标 | GPT-5.2-Codex | GPT-5.3-Codex | 变化 |
|:------|:-------------|:-------------|:------|
| Terminal-Bench | 64.0% | 77.3% | **+13.3pp** |
| OSWorld-Verified | 38.2% | 64.7% | **+26.5pp** |
| Cybersecurity CTF | 67.4% | 77.6% | **+10.2pp** |
| SWE-Lancer IC Diamond | 76.0% | 81.4% | **+5.4pp** |
| Token 效率 | 基线 | 仅需一半 | **-50% Token** |
| 处理速度 | 基线 | +25% | **+25%** |
| 自举能力 | 无 | ✅ | **首次实现** |
| 硬件平台 | — | NVIDIA GB200 NVL72 | 联合设计 |

自举的远期含义：如果每一代模型都能让下一代更容易诞生，AI 模型开发的边际成本将持续下降。这不是终点，而是一个正反馈循环的起点。

## Opus 4.6 新增 API 能力

除了 Agent Teams，Opus 4.6 同时发布了多项开发者平台升级，直接影响实际工程使用：

| 新特性 | 说明 | 工程意义 |
|:-------|:-----|:---------|
| **Adaptive Thinking** | 模型自主判断是否需要深度推理，不再是 extended thinking 的二选一 | 简单任务自动跳过深度思考，降低成本和延迟 |
| **Effort 4 级控制** | low / medium / high（默认）/ max | 开发者可根据任务复杂度精细调节智能 vs 速度 vs 成本 |
| **Context Compaction**（Beta） | 接近上下文窗口阈值时自动摘要并替换旧上下文 | 长时间运行的 Agent 不再撞墙 |
| **1M Token 上下文**（Beta） | Opus 系列首次支持 | >200K Token 触发 Premium 定价 |
| **128K 输出 Token** | 最大输出长度翻倍 | 大型输出任务无需拆分请求 |

其中 **Adaptive Thinking + Effort 控制** 是一个值得注意的组合：模型默认在 `high` effort 下自主决定是否启用 extended thinking，开发者还可以通过 `/effort` 参数进一步调节。这意味着 Opus 4.6 在"思考深度"这个维度上第一次实现了**连续可调**，而不是之前的开/关二态。

## 成本结构：API 经济学

对于实际使用者，成本结构往往比 Benchmark 数字更有决策价值。

### 定价对比

> ⚠️ **重要修正**：此前网络流传的 Opus 4.6 定价 "$15/$75" 为错误信息。Anthropic 官方公告原文为："Pricing remains the same at $5/$25 per million tokens"。

| 模型 | 输入（$/1M tokens） | 输出（$/1M tokens） | 相对 GPT-5.2 成本 |
|:------|:-------------------|:-------------------|:-----------------|
| GPT-5 Mini | $0.025 | $2.00 | **0.01x**（极低） |
| GPT-5.2 | $1.75 | $14.00 | 1x（基线） |
| GPT-5.3-Codex | 未公布 | 未公布 | 等效 ~**0.5x**（效率推算） |
| Claude Sonnet 4.5 | $3.00 | $15.00 | ~1.7x（输入端） |
| **Claude Opus 4.6** | **$5.00** | **$25.00** | **2.9x（输入端）** |
| Opus 4.6 Premium（>200K ctx） | $10.00 | $37.50 | 5.7x（输入端） |

修正后的成本比远没有之前 "8.6x" 那么夸张。Opus 4.6 标准定价仅为 GPT-5.2 的 ~2.9 倍（输入端），配合 GPT-5.3-Codex 的 50% Token 效率提升，两者的实际使用成本差距进一步缩小。

### 典型场景成本估算

| 场景 | Token 规模 | GPT-5.2 | GPT-5.3（估） | Sonnet 4.5 | Opus 4.6 |
|:------|:-----------|:--------|:-----------|:----------|:---------|
| 代码审查（10 万行） | 50 万 in + 5 万 out | **$1.58** | ~$0.79 | $2.25 | $3.75 |
| 日常编程（月度） | 220 万 in + 110 万 out | $19.25 | ~**$9.63** | $23.10 | $38.50 |
| 大型项目重构（C 编译器级） | 20 亿 in + 1.4 亿 out | $5,460 | ~$2,730 | — | ~**$20,000**（实际） |

最后一行需要注意：按标准定价计算，Opus 4.6 的理论成本应为 $13,500（$10,000 输入 + $3,500 输出）。实际 $20,000 的差额来自 >200K 上下文触发的 Premium 定价（$10/$37.50）。对于重度 Agent 场景，长上下文 Premium 溢价是成本规划中不可忽视的因素。

## 场景选型：何时选谁

| 决策维度 | GPT-5.3-Codex | Opus 4.6 |
|:---------|:--------------|:----------|
| 月预算 < $30 | ✅ 首选 | △ 标准定价下可用 |
| 终端环境编程 | ✅ Terminal-Bench **77.3%** | △ 65.4% |
| 快速迭代 / 原型开发 | ✅ 速度 +25%，Token -50% | △ 可用 Effort low/medium 降低成本 |
| 多语言软件工程 | ✅ SWE-Bench Pro **56.8%** | — 无对比数据 |
| 安全攻防 / CTF | ✅ Cybersecurity **77.6%** | — |
| 长上下文需求（>100K） | ❌ 标准上下文 | ✅ **1M Token 窗口 + MRCR 76%** |
| 多 Agent 协作 | ❌ 无此能力 | ✅ **Agent Teams** |
| GUI 操作自动化 | △ 64.7%（但代际提升巨大） | ✅ OSWorld **72.7%** |
| 大型代码库全局理解 | ❌ | ✅ 1M 上下文 + Context Compaction |
| 研究型信息检索 | — | ✅ BrowseComp **84.0%** |
| 泛化推理 / 新问题解决 | — | ✅ ARC-AGI-2 **68.8%** |
| 思考深度可调 | ❌ | ✅ **Adaptive Thinking + Effort 4 级** |

理想策略是**混合使用**：简单任务、高频交互用 GPT-5.3-Codex 保持低成本和快响应；复杂项目、长周期自主运行、多 Agent 协作用 Opus 4.6 发挥深度优势。

## 路线展望

这两款模型代表了 AI 编程领域当前的两条主要技术路线：

**效率路线**（GPT-5.3-Codex）的核心逻辑是让同等任务消耗更少资源、让模型参与自身迭代。适合 IDE 实时补全、代码审查、Bug 修复等高频交互场景，以及 Token 预算受限的大规模部署和需要低延迟的生产系统。OpenAI 的自举叙事指向一个正反馈循环：模型越强 → 开发下一代越高效 → 下一代更强。

**深度路线**（Opus 4.6）的核心逻辑是让模型理解更多上下文、让多个模型协作完成复杂任务、让 Agent 能够自主运行更长时间。C 编译器项目证明了扁平对等的多 Agent 架构在大型工程中的可行性——16 个 Docker 容器 + Git 裸仓库 + 文件锁，没有调度层、没有花哨的通信协议，就完成了 10 万行代码。Adaptive Thinking 和 Effort 控制则在 API 层面给开发者提供了成本-智能-速度的连续调节能力。

值得注意的是，两条路线并非互斥。在 SWE-bench 上顶级模型分数已趋于一致（80% 水位线），暗示着在标准化编程任务上模型能力正在收敛。未来的差异化将更多体现在上层能力——Agent 协作、自主运行时长、系统集成深度——而非底层编码质量本身。

**GPT-5.3-Codex 回答的问题是**：如何让 AI 编程更高效、更便宜、能自我迭代？

**Opus 4.6 回答的问题是**：如何让 AI 编程处理更大的系统、更复杂的任务、实现多 Agent 协作？

这不是零和博弈。两种路线的同时推进，意味着 AI 编程工具的 Pareto 前沿正在同时向"更快"和"更深"两个方向扩展——开发者是最大的受益者。

---

**参考资料**

- [Introducing GPT-5.3-Codex — OpenAI](https://openai.com/index/introducing-gpt-5-3-codex/)
- [Introducing Claude Opus 4.6 — Anthropic](https://www.anthropic.com/news/claude-opus-4-6)
- [Building a C compiler with a team of parallel Claudes — Anthropic Engineering](https://www.anthropic.com/engineering/building-c-compiler)
- [GPT-5.3-Codex System Card (PDF)](https://cdn.openai.com/pdf/23eca107-a9b1-4d2c-b156-7deb4fbc697c/GPT-5-3-Codex-System-Card-02.pdf)
- [Claude Opus 4.6 System Card (PDF)](https://www-cdn.anthropic.com/0dd865075ad3132672ee0ab40b05a53f14cf5288.pdf)
- [Claude's C Compiler — GitHub](https://github.com/anthropics/claudes-c-compiler)
- [SWE-bench Leaderboards](https://www.swebench.com/)
