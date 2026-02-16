# Qwen3.5 代码仓库分析

## 研究基础
- 代码版本: 最新 main 分支 (shallow clone)
- 研究时间: 2026-02-16
- 仓库地址: https://github.com/QwenLM/Qwen3.5

## 目录结构

```
Qwen3.5/
├── .github/          # GitHub 配置（Issue/PR 模板等）
├── LICENSE           # Apache 2.0 开源协议
└── README.md         # 项目说明（核心文档，包含架构、部署、评测信息）
```

**注意**: Qwen3.5 仓库是一个**信息聚合仓库**（类似 Qwen2、Qwen3 的模式），不包含模型训练代码或推理代码。模型权重托管在 Hugging Face Hub 和 ModelScope 上，推理和部署依赖第三方框架。

## 核心信息提取（来自 README.md）

### 模型规格
- **模型名称**: Qwen3.5-397B-A17B
- **总参数**: 3970 亿 (397B)
- **激活参数**: 170 亿 (A17B) — 每次前向传播仅激活不到 5%
- **架构**: 混合架构 — Gated Delta Networks (线性注意力) + 稀疏 MoE
- **上下文窗口**: 262K（原生），1M（API 版本 Qwen3.5-Plus）
- **开源协议**: Apache 2.0
- **论文标题**: "Qwen3.5: Towards Native Multimodal Agents"

### 五大核心技术创新
1. **统一视觉-语言基座 (Unified Vision-Language Foundation)**
   - 在数万亿多模态 token 上进行早期融合训练
   - 跨代持平：与 Qwen3 纯文本能力相当，同时超越 Qwen3-VL 视觉模型

2. **高效混合架构 (Efficient Hybrid Architecture)**
   - Gated Delta Networks + 稀疏 MoE
   - 高吞吐推理，低延迟和低成本

3. **可扩展 RL 泛化 (Scalable RL Generalization)**
   - 百万级 Agent 环境中进行强化学习
   - 渐进式复杂任务分布，增强真实世界适应性

4. **全球语言覆盖 (Global Linguistic Coverage)**
   - 201 种语言和方言（从 119 种扩展）
   - 词表从 15 万扩展到 25 万

5. **下一代训练基础设施 (Next-Generation Training Infrastructure)**
   - 多模态训练效率接近 100%（对比纯文本训练）
   - 异步 RL 框架支持大规模 Agent 脚手架

### 部署支持的框架
| 框架 | 用途 | 备注 |
|------|------|------|
| Hugging Face Transformers | 推理/训练/服务 | `transformers serve --port 8000` |
| SGLang | 高性能推理服务 | TP=8, 262K 上下文 |
| vLLM | 高吞吐推理 | TP=8, 262K 上下文 |
| llama.cpp | 轻量级本地推理 | 支持 GGUF 格式 |
| MLX | Apple Silicon | mlx-lm (文本) / mlx-vlm (视觉) |

### 微调框架支持
- UnSloth
- Swift (ModelScope)
- LLaMA-Factory
- 支持 SFT, DPO, GRPO 等训练范式

### API 调用方式
- **Qwen3.5-Plus**: 通过阿里云百炼 (Alibaba Cloud Model Studio)
- 兼容 OpenAI API 规范和 Anthropic API 规范
- 支持 `enable_thinking`（链式思考）和 `enable_search`（联网搜索 + Code Interpreter）

### 生态工具
- **Qwen Chat**: Web UI / 桌面 / 移动端应用
- **Qwen Code**: 终端 AI 编程 Agent（类 Cursor/Claude Code）
- **Qwen Agent**: 开源 Agent 框架（指令跟随、工具调用、规划、记忆）

## 关键代码引用

由于仓库本身不含模型代码，关键技术实现分布在以下位置：
- **模型定义**: `transformers` 库中的 Qwen3.5 模型类
- **模型权重**: `Qwen/Qwen3.5-397B-A17B` (Hugging Face Hub / ModelScope)
- **推理优化**: SGLang / vLLM 中的适配代码
- **Agent 框架**: `github.com/QwenLM/Qwen-Agent`
- **编码工具**: `github.com/QwenLM/qwen-code`

## 架构细节总结（来自官方博客 + 社区解读）

### 层级结构
- **总层数**: 60 层
- **专家数量**: 512 个专家，每次激活 10 个路由专家 + 1 个共享专家
- **隐藏层组织**: 15 组 × (3 层 Gated DeltaNet→MoE + 1 层 Gated Attention→MoE)
- **注意力**: Gated DeltaNet (线性注意力) + Gated Attention (标准注意力)
- **词表**: 250,000 tokens

### 训练基础设施
- 异构基础设施：视觉与语言组件解耦并行策略
- 原生 FP8 流水线：激活显存降低 ~50%，加速 >10%
- 异步 RL 框架：训推分离，动态负载均衡，细粒度故障恢复
- 端到端加速: 3×–5×
