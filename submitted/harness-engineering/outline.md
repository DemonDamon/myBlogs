# Harness Engineering 技术博客大纲

## 基本信息
- **字数目标**: 4000-6000字
- **风格**: 中文技术博客，面向一线开发者
- **核心论点**: Harness Engineering > Model Selection

---

## 大纲结构

### H1: 引言：为什么模型不是瓶颈？
- **核心问题**: Agent 无法长期稳定运行的真正原因
- **行业误区**: 过度关注模型能力，忽视系统支撑
- **本文目标**: 揭示 Harness Engineering 的核心价值

### H1: 什么是 Harness Engineering？
- **H2: 定义与翻译**
  - 中文译名：驾驭工程/代理驾驭工程
  - 核心定义：让模型成为可靠Agent的系统工程
- **H2: 核心痛点**
  - 上下文丢失、进度不可见
  - 一次做太多、过早宣布完成
  - 环境脏、无状态、无法接力
- **H2: 五大核心机制**
  - 上下文管理、状态持久化、工具编排、任务拆解与验证、护栏与约束

### H1: 行业实践对比
- **H2: Anthropic 的双阶段框架**
  - Initializer Agent：首轮奠基
  - Coding Agent：持续执行
  - 关键文件：feature_list.json, init.sh, claude-progress.txt
- **H2: OpenAI 的仓库级环境**
  - 百万行代码实验
  - AGENTS.md 规范
  - 机械强制执行架构
- **H2: LangChain 的开源实现**
  - Deep Agents 架构
  - Terminal Bench 2.0 性能提升 (52.8%→66.5%)

### H1: Harness Engineering 核心组件
- **H2: 状态持久化 (State Persistence)**
  - LangGraph Checkpointing
  - 跨会话恢复机制
- **H2: 上下文管理 (Context Management)**
  - 渐进式披露
  - 压缩层次：Raw → Compaction → Summarization
- **H2: 工具编排 (Tool Orchestration)**
  - 从15个工具到2个工具的启示
  - Vercel 案例：准确率80%→100%，速度提升3.5x
- **H2: 验证闭环 (Validation Loop)**
  - PreCompletionChecklistMiddleware
  - 人类在环 (HITL)

### H1: 代码实战：Deep Agents 架构解析
- **H2: 系统架构**
  - SDK/CLI/Harbor 三层结构
  - Middleware 系统核心
- **H2: 关键代码片段**
  - create_deep_agent() 流程
  - SubAgent 执行机制
  - Checkpoint 恢复

### H1: 10问工程落地分析
- **H2: 性能与瓶颈**
  - Token成本优化：10x节省
  - 上下文窗口的实际限制
- **H2: 容错与恢复**
  - 失败模式与恢复策略
- **H2: 成本与部署**
  - 生产部署要素
- **H2: 安全与风险**
  - 沙箱隔离、工具权限
- **H2: 与竞品对比**
  - Deep Agents vs Claude Code vs Codex

### H1: 生产落地建议
- **H2: 渐进式落地策略**
  - 从小范围试点开始
  - 投资观测系统
  - 建立评估基准
- **H2: 团队实践**
  - 编码规范为可执行规则
  - 预留20%时间处理"AI slop"

### H1: 结论与展望
- **核心洞察**: Harness > Model
- **工程师角色转变**: 从写代码到设计环境
- **未来方向**: 多模型协同、自优化Harness

---

## 图文配对方案

| 章节 | 配图方案 | 来源 |
|------|---------|------|
| 五大核心机制 | 表格/列表描述 | 文字 |
| Anthropic 双阶段框架 | 流程图描述 | 文字 |
| Terminal Bench 结果 | 数据表格 | 爬取内容 |
| Vercel 工具优化对比 | 前后对比表 | 爬取内容 |
| Deep Agents 架构 | 模块结构描述 | 代码分析 |
| 竞品对比 | 对比矩阵表 | 综合分析 |

---

## 写作检查清单

- [ ] 引言抓住痛点，提出核心问题
- [ ] 概念解释清晰，中英文对照
- [ ] 案例数据准确，有来源引用
- [ ] 代码片段真实，带注释说明
- [ ] 工程分析深入，10问全覆盖
- [ ] 结论有力，给出行动建议
- [ ] 字数达标 (4000-6000字)
- [ ] 无错别字，术语统一
