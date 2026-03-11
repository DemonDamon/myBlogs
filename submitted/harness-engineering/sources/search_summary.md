# Harness Engineering - 搜索结果汇总

## 搜索时间
2026-03-11

## 搜索Query列表
1. Anthropic Harness Engineering long-running agents 2026
2. OpenAI Harness Engineering agent scaffolding
3. LangChain Deep Agents harness engineering implementation
4. LangGraph checkpointing persistence state management agents
5. Claude Code agent harness implementation architecture
6. Terminal Bench 2.0 LangChain Deep Agents benchmark results
7. AGENTS.md documentation anthropic agent scaffolding
8. feature list json agent progress tracking anthropic

---

## 高价值页面列表（已筛选，需爬取）

### 官方文档/博客（必读）
1. ✅ **Anthropic - Effective harnesses for long-running agents**
   - URL: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
   - 类型: 官方博客，定义 Harness Engineering 核心方法论
   - 价值: ⭐⭐⭐⭐⭐ - Anthropic 官方定义，Initializer + Coding Agent 双阶段框架

2. ✅ **OpenAI - Harness engineering: leveraging Codex in an agent-first world**
   - URL: https://openai.com/index/harness-engineering/
   - 类型: 官方博客，OpenAI Harness Engineering 方法论
   - 价值: ⭐⭐⭐⭐⭐ - 百万行代码零人工编写实验，Agent 脚手架完整定义

3. ✅ **LangChain - Improving Deep Agents with harness engineering**
   - URL: https://blog.langchain.com/improving-deep-agents-with-harness-engineering/
   - 类型: 官方博客，LangChain 的 Harness 工程实践
   - 价值: ⭐⭐⭐⭐⭐ - Terminal Bench 2.0 从30+冲到Top 5的实战案例

4. ✅ **LangChain - Evaluating Deep Agents CLI on Terminal Bench 2.0**
   - URL: https://www.blog.langchain.com/evaluating-deepagents-cli-on-terminal-bench-2-0/
   - 类型: 官方博客，Benchmark 结果详解
   - 价值: ⭐⭐⭐⭐ - 66.5% vs 52.8% 性能提升数据

5. ✅ **OpenAI - AGENTS.md Guide**
   - URL: https://developers.openai.com/codex/guides/agents-md/
   - 类型: 官方文档，AGENTS.md 规范
   - 价值: ⭐⭐⭐⭐⭐ - 脚手架核心配置文件规范

6. ✅ **LangChain - Deep Agents 官方页面**
   - URL: https://www.langchain.com/deep-agents
   - 类型: 产品官网
   - 价值: ⭐⭐⭐⭐ - 产品定位与功能介绍

### 架构分析文章（深度阅读）
7. ✅ **Medium - The Agent Harness Is the Architecture**
   - URL: https://medium.com/@epappas/the-agent-harness-is-the-architecture-and-your-model-is-not-the-bottleneck-5ae5fd067bb2
   - 类型: 行业分析文章
   - 价值: ⭐⭐⭐⭐ - "Harness > Model" 核心观点阐述

8. ✅ **DEV Community - The secret isn't the model. It's the harness.**
   - URL: https://dev.to/n_asuy/the-secret-isnt-the-model-its-the-harness-587a
   - 类型: 社区技术文章
   - 价值: ⭐⭐⭐⭐ - 工程师角色转变分析

9. ✅ **Towards AI - Persistence in LangGraph Deep Practical Guide**
   - URL: https://pub.towardsai.net/persistence-in-langgraph-deep-practical-guide-36dc4c452c3b
   - 类型: 技术教程
   - 价值: ⭐⭐⭐⭐ - Checkpointing 实现细节

10. ✅ **Medium - Agent Harness: Understanding Claude Code's Superpower Engine**
    - URL: https://medium.com/@fruitful2007/agent-harness-understanding-claude-codes-superpower-engine-85e35a7ec764
    - 类型: 技术分析
    - 价值: ⭐⭐⭐⭐ - Claude Code Harness 架构详解

### GitHub 仓库（需 Clone 分析）
11. ✅ **langchain-ai/deepagents**
    - URL: https://github.com/langchain-ai/deepagents
    - 类型: 开源实现
    - 价值: ⭐⭐⭐⭐⭐ - Harness Engineering 开源落地代码

12. ✅ **agentsmd/agents.md**
    - URL: https://github.com/agentsmd/agents.md
    - 类型: 规范仓库
    - 价值: ⭐⭐⭐⭐ - AGENTS.md 标准规范

### Benchmark/数据页面
13. ✅ **Terminal Bench 2.0 Leaderboard**
    - URL: https://www.tbench.ai/leaderboard/terminal-bench/2.0
    - 类型: Benchmark 排行榜
    - 价值: ⭐⭐⭐⭐ - 客观性能数据对比

14. ✅ **InfoQ - OpenAI Harness Engineering 报道**
    - URL: https://www.infoq.com/news/2026/02/openai-harness-engineering-codex/
    - 类型: 技术媒体报道
    - 价值: ⭐⭐⭐ - 行业动态汇总

---

## PDF 链接识别（需下载）

**搜索结果中未发现直接 PDF 链接**，需通过 MCP 工具 `user-mineru-docparser` 或网页爬取时识别 PDF。

潜在 PDF 来源:
- 论文预印本平台 (arXiv)
- 白皮书下载链接
- 会议 slides

---

## 关键发现摘要

### 1. 术语定义
- **Harness Engineering**: 通过优化围绕 LLM 的系统和工具，而非模型本身，来提升 Agent 性能的系统工程方法论
- **Agent Harness**: 让模型成为可执行任务智能体的系统（处理输入、编排工具调用、返回结果）
- **中文译名**: 驾驭工程 / 代理驾驭工程

### 2. 核心痛点
- 一次做太多、过早宣布完成
- 上下文丢失、进度不可见
- 环境脏、无状态、无法接力
- 无验证就提交、错误扩散

### 3. 五大核心机制
1. **上下文管理** - 控制窗口内容、顺序、淘汰策略
2. **状态持久化** - 跨轮次、跨会话保存进度
3. **工具编排** - 统一接口、权限、重试、错误恢复
4. **任务拆解与验证** - 大任务拆成可验证小单元
5. **护栏与约束** - 行为边界、权限沙箱

### 4. Anthropic 双阶段框架
- **Initializer Agent**: 首轮奠基，生成 feature_list.json、init.sh、进度文件
- **Coding Agent**: 持续执行，每轮只读一个未完成功能，验证通过才更新状态

### 5. LangChain 实现性能
- Terminal Bench 2.0: 52.8% → 66.5% (+13.7 点)
- 排名: 30+ → Top 5
- 方法: 仅调整 harness，模型不变 (GPT-5.2-Codex)

### 6. OpenAI 实验成果
- 5个月，100万行代码
- 零人工编写源码
- 开发时间缩减为传统方法的 1/10
- 3.5 PR/工程师/天

### 7. 关键文件规范
- **AGENTS.md**: 约100行，Agent 上下文地图
- **feature_list.json**: 200+ 可验证功能点，带 passes 状态
- **claude-progress.txt**: 进度追踪日志
- **init.sh**: 环境初始化脚本

---

## 下一步行动
- [ ] 爬取上述 14 个高价值页面
- [ ] Clone GitHub 仓库: langchain-ai/deepagents
- [ ] Clone GitHub 仓库: agentsmd/agents.md
- [ ] 官方页面截图 (Anthropic/OpenAI/LangChain)
- [ ] 识别并下载 PDF 文件
- [ ] 完成 10 问工程落地分析
