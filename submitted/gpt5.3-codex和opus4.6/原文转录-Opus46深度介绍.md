# "16个Agent组队，两周干翻37年GCC！"最强编码模型Claude Opus 4.6首秀，10万行Rust版C编译器震撼业界

> 来源：InfoQ（微信公众号）
> 作者：Tina
> 链接：https://mp.weixin.qq.com/s/_WNbBA6ThPXHw-2GJhzuEA
> 日期：2026年2月

---

## 概述

Anthropic 正在升级它"最聪明的模型"。随着新一代旗舰模型 **Claude Opus 4.6** 的发布，Anthropic 释放出的信号十分明确：这并不是一次常规的性能小修小补，而是一轮围绕**长任务、复杂工作，以及智能体（agent）如何真正干活**展开的系统性升级。

---

## 核心成果：用 Agent 团队构建 C 编译器

### 项目规模

在这次发布之前，Anthropic 内部和部分早期用户已经开始让 Opus 4.6 参与一项持续时间很长的工程任务：

**目标**：从零开始，用 Rust 编写一个完整的 C 编译器，并要求它能够编译 Linux 内核。

**时间周期**：约两周（11天）

**资源投入**：
- 运行近 **2,000 次** Claude Code 会话
- 累计消耗约 **20 亿输入 token**
- 生成约 **1.4 亿输出 token**
- API 成本略低于 **2 万美元**

**产出成果**：
- 约 **10 万行代码**的 C 编译器（用 Rust 编写）
- 能够在 **x86、ARM 和 RISC-V** 架构上构建 Linux 6.9
- 可以编译 **QEMU、FFmpeg、Redis、PostgreSQL**
- 通过了 **GCC 自身 99%** 的 torture test
- 能够成功编译并运行 **Doom**

### 对比数据

**网友对比**：
> GCC 的开发从 1987 年开始，历经 37 年，投入过数以千计的工程师。
> 而这一次，是一名研究者加上 16 个 AI 智能体，在短短数周内完成了一个能够通过大量 GCC 测试集、并编译真实大型项目的编译器。

---

## Opus 4.6 的核心能力提升

### 1. 最强的编码模型定位

Anthropic 对 Opus 4.6 的定位，并不只是"更会写代码"。他们强调，新模型在编程能力上的提升，已经从单纯的代码生成，扩展到：

- **更前置的任务规划**
- **更后置的代码审查与调试流程**

这种变化，使模型能够在大型代码库中更稳定地工作，也直接决定了它是否有能力脱离短对话模式，持续参与多阶段、长周期的工程任务。

### 2. 基准测试成绩

#### Terminal-Bench 2.0（终端 agentic 编程）
- **Opus 4.6**: 65.4%
- **GPT-5.2**: 64.7%
- **Gemini 3 Pro**: 56.2%
- **Sonnet 4.5**: 51.0%

#### SWE-bench Verified（Agentic coding）
- **Opus 4.6**: 80.8%
- **Opus 4.5**: 80.9%
- **GPT-5.2**: 80.0%

#### OSWorld（Agentic computer use）
- **Opus 4.6**: 72.7%（相比 Opus 4.5 的 66.3% 有明显提升）
- **Sonnet 4.5**: 61.4%

#### BrowseComp（Agentic search）
- **Opus 4.6**: 84.0%
- **GPT-5.2 Pro**: 77.9%
- **Opus 4.5**: 67.8%

#### Humanity's Last Exam（跨学科推理）
- **Opus 4.6**: 明显领先

#### ARC-AGI-2（新问题解决）
- **Opus 4.6**: 68.8%
- **GPT-5.2 Pro**: 54.2%
- **Gemini 3 Pro**: 45.1%

### 3. 长上下文能力

#### 上下文窗口
新模型在 Beta 阶段提供 **100 万 token** 的上下文长度，与该公司现有的 Sonnet（4 和 4.5 版本）相当。

#### 解决"上下文腐烂"问题

Anthropic 特别强调，Opus 4.6 的提升并不是"能塞更多 token"，而是"塞进去之后还能用"。

**能力提升**：
- 在大规模文档中检索关键信息的能力显著增强
- 在数十万 token 范围里持续跟踪信息，偏差更小
- 更容易捕捉到埋得很深的细节

**MRCR v2 测试（8-needle、100 万 token）**：
- **Opus 4.6**: **76%**
- **Sonnet 4.5**: 仅 **18.5%**

这并不是简单的"高一点、低一点"，更像两种不同的可用性状态：一个模型在超长上下文中仍然能稳定检索并利用信息，另一个则在任务拉长后迅速失效。

---

## 智能体团队（Agent Teams）功能

### 核心概念

Opus 4.6 最醒目的新增功能，是 Anthropic 所称的"智能体团队"（agent teams）：

> "不再让单个智能体按顺序把任务一路做到底，而是把工作分给多个智能体——每个智能体负责自己的一块，并直接与其他智能体协调。"

### 类比

Anthropic 产品负责人 Scott White 将其类比为"雇了一支很能干的人类团队"，因为职责拆分后，智能体可以并行协作，从而更快完成工作。

### 实验配置

在编译器项目中：
- **16 个并行运行的 Agent**
- 每个 Agent 独立工作
- 使用 Git 进行代码同步
- 使用文件锁机制避免任务冲突

### 技术实现

#### 自主循环
```bash
#!/bin/bash
while true; do
  COMMIT=$(git rev-parse --short=6 HEAD)
  LOGFILE="agent_logs/agent_${COMMIT}.log"
  claude --dangerously-skip-permissions \
         -p "$(cat AGENT_PROMPT.md)" \
         --model claude-opus-X-X-Y &> "$LOGFILE"
done
```

#### 任务锁定机制
- Claude 通过在 `current_tasks/` 下写入一个文本文件来"锁定"某个任务
- 如果两个 agent 试图认领同一任务，Git 的同步机制会迫使第二个 agent 改选另一个任务
- Claude 在任务上工作完成后，会从 upstream 拉取、合并其他 agent 的改动、推送自己的改动，然后移除锁

#### 并行策略

**测试框架设计原则**：
1. 必须围绕语言模型的固有限制来设计系统
2. 应对两类限制：
   - **上下文窗口污染**：测试框架最多只保留几行关键输出
   - **时间盲**：提供默认的 `--fast` 选项，只运行 1% 或 10% 的随机子样本

**角色分工**：
- 一个 agent 负责扫描并合并重复代码
- 一个 agent 聚焦于提升编译器自身的性能
- 第三个 agent 负责改进生成代码的效率
- 另有 agent 从 Rust 开发者的视角审视整个项目的设计
- 还有一个 agent 专注于文档维护

---

## 项目成果与能力边界

### 成功的方面

✅ 完全的 clean-room 实现（开发过程中 Claude 从未获得互联网访问权限）
✅ 约 10 万行代码
✅ 能够在 x86、ARM 和 RISC-V 架构上构建可启动的 Linux 6.9
✅ 可以编译 QEMU、FFmpeg、SQLite、Postgres、Redis
✅ 在大多数编译器测试套件中达到约 99% 的通过率
✅ 可以编译并运行 Doom

### 当前的限制

❌ 缺乏启动 Linux 所需的 16 位 x86 编译能力
❌ 尚未拥有稳定可用的 assembler 与 linker
❌ 并非所有项目都能成功编译
❌ 生成的代码效率不高（即使启用所有优化，其效率也低于禁用所有优化的 GCC 生成的代码）
❌ Rust 代码质量尚可，但远不及 Rust 专家级程序员编写的代码质量

### GitHub 开源

编译器的源码已公开：
**https://github.com/anthropics/claudes-c-compiler**

---

## 参考链接

- [Claude Opus 4.6 官方公告](https://www.anthropic.com/news/claude-opus-4-6)
- [用 Opus 4.6 构建 C 编译器](https://www.anthropic.com/engineering/building-c-compiler)

---

**声明**：本文为 InfoQ 整理，不代表平台观点，未经许可禁止转载。
