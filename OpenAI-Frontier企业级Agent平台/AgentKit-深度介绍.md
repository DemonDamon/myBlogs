# AgentKit 深度介绍

> **发布日期**：2026年1月29日
> **官方链接**：[Introducing AgentKit](https://openai.com/index/introducing-agentkit/)
> **产品类型**：开发者工具 + 企业级 Agent 平台

---

## 概述

**AgentKit** 是 OpenAI 推出的一套完整工具，帮助开发者和企业从原型快速过渡到生产环境。AgentKit 解决了以往构建 Agent 时面临的工具碎片化问题，包括复杂的编排（无版本控制）、自定义连接器、手动评估管道、提示词调优，以及发布前数周的前端工作。

---

## 核心组件

### 1. Agent Builder（Agent 构建器）

**可视化画布**：用于创建和版本化管理多 Agent 工作流

- **拖放式节点**：通过拖放节点组合逻辑
- **工具连接**：连接各种工具和服务
- **自定义防护栏**：配置自定义安全防护栏
- **预览运行**：支持预览运行和内联评估配置
- **完整版本控制**：支持完整版本控制，适合快速迭代

#### 客户案例

**Ramp**（金融科技公司）：
> "Agent Builder 将原本需要数月的复杂编排、自定义代码和手动优化工作，在短短几小时内完成。可视化画布让产品、法律和工程团队保持在同一页面上，将迭代周期缩短了 70%，在两个冲刺而非两个季度内就上线了 Agent。"

**LY Corporation**（日本领先的技术和互联网服务公司）：
> "Agent Builder 允许我们以全新的方式编排 Agent，工程师和主题专家在一个界面中协作。我们在不到两小时内构建并运行了第一个多 Agent 工作流，大大加速了创建和部署 Agent 的时间。"

#### 模板系统

- 从空白画布开始
- 使用预构建模板快速开始
- 支持多种节点类型：Agent、Note、File search、Guardrails、MCP、User approval 等

### 2. Connector Registry（连接器注册表）

**企业级数据管理**：跨多个工作空间和组织治理和维护数据

#### 功能特点

- **中央管理面板**：将数据源整合到单个管理面板
- **跨产品统一**：跨 ChatGPT 和 API 统一管理
- **预构建连接器**：
  - Dropbox
  - Google Drive
  - SharePoint
  - Microsoft Teams
- **第三方 MCP 支持**：支持第三方 Model Context Protocol

#### 管理能力

- 管理如何跨 OpenAI 产品连接数据和工具
- 支持全局管理控制台（Global Admin Console）
- 需要全局管理控制台才能启用

### 3. ChatKit（嵌入式聊天工具包）

**嵌入式 Agent 体验**：将基于聊天的 Agent 体验嵌入到产品中

#### 功能特点

- **简单嵌入**：可以嵌入到应用或网站中
- **自定义主题**：可定制以匹配主题或品牌
- **原生体验**：使基于聊天的 Agent 感觉原生

#### 技术能力

- 处理流式响应
- 管理对话线程
- 显示模型思考过程
- 设计吸引人的聊天内体验

#### 使用场景

- 内部知识助手
- 入职指南
- 客户支持
- 研究代理

#### 客户案例

**HubSpot**：使用 ChatKit 驱动其客户支持 Agent

---

## 评估与优化能力

### Evals 功能扩展

构建可靠、生产就绪的 Agent 需要严格的性能评估。OpenAI 在原有 Evals 基础上增加了四个新功能：

#### 1. Datasets（数据集）

- 从零开始快速构建 Agent 评估
- 使用自动评分器和人工注释扩展评估
- 随时间持续改进评估质量

#### 2. Trace Grading（追踪评分）

- 对 Agent 工作流进行端到端评估
- 自动化评分以精确定位不足之处
- 全面了解整个工作流程的性能

#### 3. Automated Prompt Optimization（自动提示词优化）

- 基于人工注释生成改进的提示词
- 基于评分器输出优化提示词
- 减少手动调优工作

#### 4. Third-Party Model Support（第三方模型支持）

- 在 OpenAI Evals 平台内评估其他提供商的模型
- 跨平台模型性能对比
- 灵活的模型选择

### Reinforcement Fine-Tuning（强化微调）

**自定义推理模型**：让开发者自定义 OpenAI 的推理模型

#### 可用状态

- **o4-mini**：正式发布
- **GPT-5**：私人测试版（与数十位客户密切合作）

#### 新增功能

**Custom Tool Calls（自定义工具调用）**：
- 训练模型在正确时间调用正确工具
- 提高推理能力
- 更好的工具使用决策

**Custom Graders（自定义评分器）**：
- 为特定用例设置自定义评估标准
- 针对最重要的指标进行评估
- 优化特定业务目标

---

## Guardrails（安全防护栏）

**开源模块化安全层**：保护 Agent 免受意外或恶意行为的影响

### 功能

- **PII 保护**：屏蔽或标记个人身份信息
- **Jailbreak 检测**：检测越狱尝试
- **其他安全措施**：应用其他安全保护措施

### 部署方式

1. **独立部署**：作为独立组件部署
2. **Python 集成**：通过 Python 的 guardrails 库
3. **JavaScript 集成**：通过 JavaScript 的 guardrails 库

---

## 定价与可用性

### 当前状态

| 功能 | 状态 | 可用性 |
|------|------|--------|
| **ChatKit** | ✅ 正式发布 | 所有开发者 |
| **Evals 功能** | ✅ 正式发布 | 所有开发者 |
| **Agent Builder** | 🔄 Beta 版 | 部分 API 用户 |
| **Connector Registry** | 🔄 Beta 滚动发布 | API、ChatGPT Enterprise 和 Edu 客户 |

### 定价模式

- 所有工具包含在标准 API 模型定价中
- 无需额外订阅费用
- 按使用量计费

### 即将推出

- 独立的 Workflows API
- ChatGPT 中的 Agent 部署选项

---

## 技术架构

### Responses API 和 Agents SDK

AgentKit 建立在以下基础之上：

1. **Responses API**（2025年3月发布）
2. **Agents SDK**（2025年3月发布）

### 客户成功案例

**Klarna**：
- 构建了一个支持 Agent
- 处理三分之二的工单
- 大幅提高客户支持效率

**Clay**：
- 使用销售 Agent
- 增长 10 倍
- AgentKit 帮助更高效、可靠地构建 Agent

---

## 开发工作流

### 传统开发流程

```
需求分析 → 复杂编排 → 自定义代码 → 手动优化 → 测试 → 前端开发 → 部署
（数月时间）
```

### AgentKit 开发流程

```
需求分析 → Agent Builder（可视化设计）→ ChatKit（嵌入）→ 部署
（数小时到数天）
```

---

## 生态系统

### 开放标准

AgentKit 建立在开放标准之上：
- 支持第三方 MCP 协议
- 支持第三方模型评估
- 可扩展的连接器系统

### 开源组件

- **Guardrails**：开源安全层
- **Python/JavaScript 库**：易于集成

---

## 与 OpenAI Frontier 的关系

### AgentKit vs Frontier

| 方面 | AgentKit | Frontier |
|------|----------|----------|
| **目标用户** | 开发者 | 企业 |
| **主要功能** | 构建 Agent | 管理 AI 同事 |
| **重点** | 开发工具 | 业务上下文和治理 |
| **部署** | 集成到应用 | 企业级运行时 |

### 协同效应

- **AgentKit**：帮助开发者快速构建 Agent
- **Frontier**：帮助企业在生产环境中管理和运行这些 Agent
- **整合**：AgentKit 构建的 Agent 可以部署到 Frontier 平台

---

## 资源链接

### 官方资源

- [Introducing AgentKit - 官方公告](https://openai.com/index/introducing-agentkit/)
- [Agent Builder - 文档](https://openai.com/agent-builder/)
- [Connector Registry - 文档](https://openai.com/connector-registry/)
- [ChatKit - 文档](https://openai.com/chatkit/)
- [Evals - 平台](https://openai.com/evals/)

### 技术文档

- [Guardrails (Python)](https://github.com/openai/guardrails-py)
- [Guardrails (JavaScript)](https://github.com/openai/guardrails-js)
- [Responses API - 文档](https://platform.openai.com/docs/guides/responses-api)
- [Agents SDK - 文档](https://platform.openai.com/docs/guides/agents-sdk)

---

## 总结

AgentKit 代表了 OpenAI 在企业级 Agent 开发工具方面的重要进展：

1. **完整性**：从设计到部署的完整工具链
2. **可视化**：降低技术门槛，支持非技术团队
3. **企业级**：内置安全、治理和评估能力
4. **开放性**：基于开放标准，支持生态系统
5. **效率**：将数月的开发周期缩短到数小时

---

**更新日期**：2026年2月6日
**文档版本**：1.0
