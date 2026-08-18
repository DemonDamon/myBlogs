# Polymarket Agents 技术博客 - 大纲

## 标题
Polymarket Agents: 2300+ Stars 的预测市场 AI Agent 开发框架深度解析

## 摘要
Polymarket Agents 是 Polymarket 官方开源的完整开发者框架，专门用于构建预测市场的 AI Agent。本文深度解析这个 2300+ Stars、99.6% Python 写成的开源项目，从架构设计、核心模块到工程实现细节全方位剖析。

---

## 1. 背景与项目概览 (配图: cli.png)
- 什么是 Polymarket？预测市场的价值
- Polymarket Agents 的定位：AI Agent 开发者框架
- 项目数据：2300+ Stars，547 Forks，23 Watchers，MIT 许可证
- 代码构成：99.6% Python

## 2. 架构总览
- 模块化设计理念
- 核心层次结构：
  - APIs 层（Polymarket API、Gamma API、Chroma DB）
  - Connectors 层（数据接入）
  - Application 层（Agent 执行逻辑）
  - Scripts 层（用户交互接口）

## 3. 核心模块深度解析

### 3.1 Trader 类 (agents/application/trade.py)
- `one_best_trade()` 策略工作流
- 交易执行流程：事件筛选 → 市场映射 → 交易计算
- 代码片段解析

### 3.2 Executor 类 (agents/application/executor.py)
- Agent 智能体核心执行器
- LLM 集成与 prompt 管理
- 分块处理逻辑（处理大上下文）
- RAG 事件/市场筛选
- Superforecaster 预测模块
- 代码片段解析

### 3.3 Prompter 类 (agents/application/prompts.py)
- Prompt 工程设计
- Superforecaster 系统提示词
- 交易生成提示词
- 代码片段解析

### 3.4 PolymarketRAG 类 (agents/connectors/chroma.py)
- 向量数据库集成（Chroma + OpenAI Embeddings）
- 事件向量化与检索
- 市场向量化与检索
- 代码片段解析

### 3.5 Polymarket API 客户端 (agents/polymarket/polymarket.py)
- Web3.py 集成与 Polygon 链交互
- CLOB（Central Limit Order Book）客户端
- 订单构建与签名
- 市场订单执行
- 代码片段解析

## 4. 核心工作流详解
- 完整的 one_best_trade 执行链路
- 数据流向图
- LLM 调用时机与作用

## 5. 工程要点与创新点
- Token 分块处理策略（解决大上下文限制）
- RAG + Superforecasting 组合预测方法
- 区块链钱包集成与安全设计
- Prompt 工程最佳实践

## 6. 快速上手实战
- 环境配置步骤
- 最小化运行示例
- 自定义策略开发指南

## 7. 局限与展望
- 当前版本的限制
- 可扩展方向
- 社区贡献机会

---

## 图文配对方案
| 章节 | 配图 | 说明 |
|------|------|------|
| 1. 背景与项目概览 | cli.png | Polymarket Agents CLI 界面 |
| 2. 架构总览 | 架构图（待生成） | 模块关系图 |
| 4. 核心工作流详解 | 流程图（待生成） | one_best_trade 执行链路 |
