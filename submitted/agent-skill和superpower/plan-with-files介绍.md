# Planning with Files（planning-with-files skill）要点汇总

本文基于以下 3 份本地抓取的微信 HTML 内容整理，目标是把“Planning with Files / 三文件模式”的核心概念、工作流和使用方法汇总成一份可快速上手的说明。

## 一句话结论

把文件系统当作 AI 的外部记忆，把复杂任务变成“可恢复、可追踪、可交付”的流程：用 `task_plan.md` 管目标与进度，用 `notes.md` 管材料与中间产物，用 `[deliverable].md` 管最终交付物。

## 它解决什么问题（AI Agent 四大缺陷）

来自文章《Planning with Files，将Manus的核心工作流模式完整实现》的归纳：

- 易失性记忆（Volatile Memory）：上下文重置后信息丢失，下一次从零开始。
- 目标漂移（Goal Drift）：执行步数多了后忘记最初目标，陷入细节。
- 隐藏错误（Hidden Errors）：失败没被记录与追踪，重复踩坑、浪费 token。
- 上下文填塞（Context Stuffing）：所有材料都塞进上下文，窗口被快速耗尽，重点被淹没。

## Manus 的六大上下文工程原则（文章内原文要点）

来自文章《CC直接用，Manus核心Context技术被人做成了Skills》的整理（该文章引用项目 `reference.md`）：

1. 文件系统作为外部记忆（Filesystem as External Memory）  
   不依赖易失的 Context Window，把磁盘当作“外挂内存”，只在 Context 中保留文件路径/指针。
2. 通过重复进行注意力操纵（Attention Manipulation Through Repetition）  
   对抗 “Lost in the Middle”，在关键决策前反复读取计划文件，刷新注意力权重。
3. 保留失败痕迹（Keep Failure Traces）  
   显式记录失败尝试，让模型通过“反思”避免死循环，而不是掩盖错误。
4. 避免少样本过拟合（Avoid Few-Shot Overfitting）  
   在重复性任务中引入受控变体，避免机械式幻觉。
5. 稳定前缀优化缓存（Stable Prefixes for Cache Optimization）  
   固定文件结构与前置指令，提高 KV-Cache 命中率，降低 token 成本。
6. 只增不改的上下文（Append-Only Context）  
   尽量用追加而非修改的方式更新信息，维护上下文连贯性。

## 三文件模式（协议与职责分工）

Planning with Files 会强制在当前工作目录维护三个核心文件（来自两篇文章的共同描述）：

- `task_plan.md`（任务计划书 / 指挥塔）  
  - 作用：定义目标、拆解阶段、追踪进度、记录错误与状态。  
  - 机制：每一次关键行动前先读它，确保“我在哪、下一步干什么”。
- `notes.md`（笔记 / 外部存储器）  
  - 作用：存放调研材料、网页摘要、关键参数、代码片段、临时想法。  
  - 机制：Store, Don’t Stuff——材料落盘，不把大段信息塞进对话上下文。
- `[deliverable].md`（最终交付物）  
  - 作用：最终输出的产物（报告/方案/代码/清单等）。  
  - 机制：把“思考过程”和“最终结果”物理隔离，便于复用与交付。

### 一个实用的文件模板（可按需修改）

`task_plan.md`（示例结构）

```md
# Goal
- （一句话目标）

# Status
- Current phase: Phase 0

# Phases
- [ ] Phase 0: 初始化与澄清范围
- [ ] Phase 1: 调研与资料沉淀（写入 notes.md）
- [ ] Phase 2: 方案/实现与验证（持续更新）
- [ ] Phase 3: 交付整理（写入 deliverable）

# Decisions
- （关键决策与原因）

# Failure Traces
- （失败尝试、报错、复盘要点）
```

`notes.md`（建议分区）

```md
# Sources
- （链接、截图、引用、数据来源）

# Findings
- （提炼后的要点与结论）

# Drafts
- （临时草稿、片段、可复用段落/代码）
```

`[deliverable].md`（最终交付）

```md
# TL;DR
- （最终结果摘要）

# Deliverable
（正文/清单/方案/代码）
```

## 工作流机制（把“文件”变成状态机）

来自文章《CC直接用，Manus核心Context技术被人做成了Skills》的描述，可理解为一个 File-Based State Machine：

- 协议握手与初始化：识别复杂任务后创建 `task_plan.md`，把目标、阶段、状态写成“程序计数器”。
- Read-Before-Decide：每次行动前读取 `task_plan.md`，对抗遗忘与目标漂移。
- Data Offloading：大量资料先提炼后写入 `notes.md`，对话里只保留“已写入 notes”的指针。
- State Commit：完成一个阶段后更新 `task_plan.md`（例如把 `[ ]` 改成 `[x]`，推进当前状态）。

## 示例：用三文件把“复杂项目”变成可控交付

来自文章《用planning-with-files skill多步骤推理来实现设计高效机房项目方案》的案例要点：

- 场景：设计以系统能效为核心，结合高效设备与 BMS 智能控制的中央空调冷源系统，目标优化全年综合能效比（SCOP）并降低机房全年总耗电。
- 做法：把项目拆成计划（`task_plan.md`）、资料与计算/选型依据（`notes.md`）、最终方案文档（`[deliverable].md`），由 AI 按阶段推进并持续“写盘”。

## 安装与使用（文章给出的路径信息）

来自文章《CC直接用，Manus核心Context技术被人做成了Skills》的安装描述：

- 自动方式：把仓库放进 Claude Code skills 路径（例如 `~/.claude/skills` 或你的自定义 skills 路径），然后克隆：`https://github.com/OthmanAdi/planning-with-files`
- 手动方式：下载/复制 `planning-with-files` 文件夹到：
  - macOS/Linux: `~/.claude/skills/`
  - Windows: `%USERPROFILE%\\.claude\\skills\\`

## 参考来源（原文 + 本地 HTML）

- 《CC直接用，Manus核心Context技术被人做成了Skills》  
  - 原文：https://mp.weixin.qq.com/s/vn8ybmLmKvjnPKtRj9v9iw  
  - 本地：[8e507b062403d6b2f4f88a8cf80181be.html](file:///Users/damon/myWork/myBlog/agent-skill%E5%92%8Csuperpower/.cache/8e507b062403d6b2f4f88a8cf80181be.html)
- 《Planning with Files，将Manus的核心工作流模式完整实现》  
  - 原文：https://mp.weixin.qq.com/s/XNjfEjFRzAowC_h5hdiEkA  
  - 本地：[d1a559f6332a0693983261772dfa9bd8.html](file:///Users/damon/myWork/myBlog/agent-skill%E5%92%8Csuperpower/.cache/d1a559f6332a0693983261772dfa9bd8.html)
- 《用planning-with-files skill多步骤推理来实现设计高效机房项目方案》  
  - 原文：https://mp.weixin.qq.com/s/QmzGeK8Yi6WgEhS4xmBmhA  
  - 本地：[09479c9db03e1413dcdc544682be5a15.html](file:///Users/damon/myWork/myBlog/agent-skill%E5%92%8Csuperpower/.cache/09479c9db03e1413dcdc544682be5a15.html)
