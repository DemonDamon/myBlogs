# Harness engineering: leveraging Codex in an agent-first world - OpenAI

**URL**: https://openai.com/index/harness-engineering/  
**Published**: February 11, 2026  
**Author**: Ryan Lopopolo, Member of the Technical Staff

---

## 核心实验成果

Over the past five months, our team has been running an experiment: **building and shipping an internal beta of a software product with 0 lines of manually-written code.**

- 5个月，约**100万行代码**
- 零人工编写源码
- 开发时间约为传统方法的**1/10**
- 平均**3.5 PR/工程师/天**，约1500个PR
- 内部用户数百人，包含每日重度使用者

## 核心理念

> **Humans steer. Agents execute.**

工程师的角色转变：**不再是写代码，而是设计环境、明确意图、建立反馈循环**，让 Codex 代理完成可靠工作。

## 工程角色的重新定义

The primary job of our engineering team became **enabling the agents to do useful work**.

In practice, this meant working depth-first:
- Breaking down larger goals into smaller building blocks
- Prompting the agent to construct those blocks
- Using them to unlock more complex tasks

When something failed, the fix was almost never "try harder." Human engineers asked: **"what capability is missing, and how do we make it both legible and enforceable for the agent?"**

## Agent 可理解性 (Agent Legibility)

Our human engineers' goal was **making it possible for an agent to reason about the full business domain directly from the repository itself**.

关键原则：
- Anything the agent can't access in-context **effectively doesn't exist**
- Knowledge in Google Docs/Slchat/人的头脑对系统是不可见的
- Repository-local, versioned artifacts 是 Agent 唯一能看到的东西

## AGENTS.md 与知识管理

### "百科全书"方式的失败

我们尝试了"一个大 AGENTS.md"方法，但失败了：
- **难以验证**：单体手册无法进行机械检查
- **瞬间腐烂**：变成陈规的墓地
- **过度引导等于无引导**：当所有东西都"重要"时，没有东西重要
- **上下文是稀缺资源**：大文件挤占任务空间

### 解决方案：目录式管理

Instead of treating AGENTS.md as the encyclopedia, **we treat it as the table of contents**.

```
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   ├── core-beliefs.md
│   └── ...
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
├── references/
└── ...
```

- AGENTS.md: 约100行，作为地图入口
- docs/ 目录：结构化知识库，系统记录
- 渐进式披露：Agent 从小入口开始，按需深入

## 架构与品味的强制执行

### 机械强制

We enforce this **mechanically**. Dedicated linters and CI jobs validate that:
- Knowledge base is up to date
- Cross-linked and structured correctly
- "Doc-gardening" agent 扫描陈腐文档并自动修复

### 严格的分层架构

Agents are most effective in environments with **strict boundaries and predictable structure**.

每个业务域分为固定的层，严格验证依赖方向：

```
Types → Config → Repo → Service → Runtime → UI
```

跨域关注点（auth, connectors, telemetry）通过单一 Provider 接口进入。

这种架构通常要数百工程师后才实施，但对 Coding Agents 来说是**早期必备**：约束让速度不以衰退为代价。

## 工具与观测性

我们让应用 UI、日志、指标对 Codex 直接可理解：

- Chrome DevTools Protocol 集成到 Agent 运行时
- 技能：DOM 快照、截图、导航
- 可观测性栈：LogQL 查询日志，PromQL 查询指标

示例提示：
- "ensure service startup completes in under 800ms"
- "no span in these four critical user journeys exceeds two seconds"

Codex 可以复现 Bug、验证修复、自主推理 UI 行为。

## 不同级别的自主性

随着开发循环被编码到系统，Codex 可以端到端驱动新功能：

给定单一提示，Agent 可以：
1. 验证代码库当前状态
2. 复现报告的 Bug
3. 录制展示失败的视频
4. 实现修复
5. 录制展示解决方案的视频
6. 通过驱动应用验证修复
7. 响应 Agent 和人类反馈
8. 检测和修复构建失败
9. 仅在需要判断时升级给人类
10. 打开 PR
11. 合并变更

## 熵与垃圾回收

Codex 复制仓库中已存在的模式——包括不均匀或次优的。这会导致漂移。

解决方案：**Golden Principles**（黄金原则）

- 偏好共享工具包而非手卷助手
- 不"YOLO-style"探测数据——验证边界或依赖类型化 SDK
- 定期后台 Codex 任务扫描偏差、更新质量等级、打开重构 PR

像垃圾回收一样工作：技术债务最好**持续小额偿还**，而非累积后痛苦爆发。

## 开放问题

- 完全 Agent 生成系统的架构一致性如何随时间演化？
- 人类判断在哪里最具杠杆效应？
- 如何编码这种判断让它复利增长？
- 随着模型能力提升，系统如何演化？

清晰的是：**构建软件仍然需要纪律，但纪律更多地体现在脚手架而非代码中**。

---
**Source**: https://openai.com/index/harness-engineering/
