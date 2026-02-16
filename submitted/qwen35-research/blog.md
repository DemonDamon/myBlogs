# Qwen3.5 深度解析：397B 参数只激活 17B，如何用「小模型成本」打出「大模型质量」？

![Qwen3.5 Banner](images/qwen35_banner.png)

*2026 年除夕夜，阿里通义千问团队发布了 Qwen3.5 系列的首款模型 Qwen3.5-397B-A17B，Apache 2.0 完全开源。*

## 1. 为什么 Qwen3.5 值得关注？

大模型领域正在经历一场深刻的范式转变：**从「堆参数」到「提效率」**。

GPT-5.2、Claude 4.5 Opus、Gemini-3 Pro 等闭源模型不断刷新性能天花板，但动辄数十美元/百万 token 的 API 定价让大规模落地成为奢望。开源社区迫切需要一款**性能接近闭源第一梯队、成本降低一个数量级**的模型。

Qwen3.5-397B-A17B 给出了一个激进的答案：总参数 3970 亿，但每次推理**仅激活 170 亿**——不到 5% 的算力调动全部知识储备。结果是：

- **性能与超万亿参数的 Qwen3-Max 持平**，多项指标超越 GPT-5.2
- **推理吞吐提升 8.6-19 倍**，部署成本降低 60%
- **API 定价 0.8 元/百万 token**，是 GPT-5.2 的 1/15

更关键的是，这不是一个「追赶型」的开源模型，而是在多个维度上实现了**差异化领先**。

## 2. 架构总览：四项技术叠加的「效率革命」

Qwen3.5 的性能跃升来自四项技术的协同作用，而非单一改进。

![Qwen3.5 架构总览](images/Qwen3.5混合架构总览.png)
*图 1：Qwen3.5 混合架构总览（Gated DeltaNet + MoE + 原生多模态 + 多 Token 预测）*
<!-- 🎨 视觉描述提示词: visual-prompts/Qwen3.5混合架构总览.txt → 请在 lovart.ai 用 NanoBanana Pro 生成后替换 -->

### 2.1 Gated Delta Networks：线性注意力的工程化突破

> 完整技术推导见独立文档 [gated_delta_networks.md](gated_delta_networks.md)，包含三篇核心论文的公式推导和伪代码。

GDN 是**两项独立研究的融合**：DeltaNet（[arXiv:2406.06484](https://arxiv.org/abs/2406.06484)，ICML 2024）提出用 Delta Rule 增强线性注意力的记忆管理能力；Gated Attention（[arXiv:2505.06708](https://arxiv.org/abs/2505.06708)，**NeurIPS 2025 Best Paper**，阿里团队）在注意力输出后加入 Sigmoid 门控消除 Attention Sink。

#### 问题：为什么标准注意力不够用？

标准 Softmax Attention 的复杂度为 $O(n^2 d)$，32K → 256K 上下文计算量暴增 64 倍。同时，Softmax 归一化要求所有权重和为 1，当 Query 找不到相关 Key 时，注意力被迫集中在首个 Token——即 **Attention Sink** 现象（首 Token 注意力占比高达 ~46%）。

#### DeltaNet：可覆盖记忆的线性注意力

线性注意力将复杂度降至 $O(nd^2)$，但它维护的状态矩阵只能做加法更新（$S_t = S_{t-1} + k_t v_t^\top$），**旧记忆无法被覆盖**，导致关联检索混乱。

DeltaNet 的核心创新是引入 **Delta Rule**（源自 Widrow-Hoff 学习规则），实现可覆盖的记忆更新：

$$S_t = \underbrace{(I - \beta_t k_t k_t^\top)}_{\text{擦除旧记忆}} \cdot S_{t-1} + \underbrace{\beta_t k_t v_t^\top}_{\text{写入新记忆}}$$

其中 $\beta_t \in (0, 1]$ 控制更新强度。当 $\beta_t = 1$ 时，在 $k_t$ 方向上完全覆盖旧值为 $v_t$。

#### Gated Attention：Sigmoid 门控消除 Attention Sink

Gated Attention 的改动极其简洁——在 SDPA 输出后加一个 Head-Specific 的 Sigmoid 门控：

$$O_{\text{gated}} = \underbrace{\text{SDPA}(Q, K, V)}_{Y} \odot \underbrace{\sigma(X W_g)}_{G}$$

Sigmoid 门控的三重效果：
1. **消除低秩瓶颈**：在 $W_V$ 和 $W_O$ 之间插入非线性，打破连续线性层的低秩约束
2. **输入依赖的稀疏过滤**：Gate 输出接近 0 时直接过滤无关信息
3. **消除 Attention Sink**：允许注意力"不输出任何东西"，首 Token 注意力占比从 ~46% 降至 ~4.8%

#### GDN 完整公式与混合架构

Qwen3.5 将两者融合为 Gated DeltaNet，完整状态更新公式：

$$S_t = (I - \beta_t k_t k_t^\top) \cdot \text{diag}(\alpha_t) \cdot S_{t-1} + \beta_t k_t v_t^\top$$
$$y_t = (q_t^\top S_t) \odot \sigma(x_t W_g)$$

其中 $\alpha_t \in (0,1)^d$ 是逐通道的遗忘门控。

![GDN 注意力机制对比](images/三种注意力机制对比图表.png)
*图 1b：标准 Softmax Attention vs 线性注意力 vs Gated DeltaNet 的记忆更新机制对比*
<!-- 🎨 视觉描述提示词: visual-prompts/三种注意力机制对比图表.txt → 请在 lovart.ai 用 NanoBanana Pro 生成后替换 -->

60 层模型采用 **3:1 混合比例**（15 组 × 4 层）——75% 的层用高效的 Gated DeltaNet（线性 $O(nd^2)$），25% 的层用精确的 Gated Attention（标准 $O(n^2d)$）做"校准"。3:1 是经大规模实验验证的最优平衡点：1:1 效率优势不明显，7:1 质量下降严重。

![3:1 混合注意力层排布](images/Qwen3.5混合注意力层排布.png)
*图 1d：Qwen3.5 的 3:1 混合注意力层排布——每 4 层中 3 层 Gated DeltaNet（蓝色，高效）+ 1 层 Gated Attention（金色，精确校准），重复 15 组构成 60 层*
<!-- 🎨 视觉描述提示词: visual-prompts/Qwen3.5混合注意力层排布.png.txt → 请在 lovart.ai 用 NanoBanana Pro 生成后替换 -->

最终效果：32K 上下文吞吐量达 Qwen3-Max 的 **8.6 倍**，256K 下 **19 倍**。

#### GDN 关键伪代码

```python
def gated_deltanet_step(q, k, v, beta, alpha, x, W_gate, S_prev):
    """Gated DeltaNet 单步递推"""
    # 1. Delta Rule 状态更新：擦除旧记忆 + 写入新关联
    erase = beta * torch.outer(k, k)          # 擦除矩阵
    S = (torch.eye(d) - erase) @ (alpha * S_prev) + beta * torch.outer(k, v)
    
    # 2. 查询记忆
    o = q @ S
    
    # 3. Sigmoid 门控调制（核心！消除 Attention Sink）
    gate = torch.sigmoid(x @ W_gate)
    y = o * gate    # 逐元素过滤
    
    return y, S
```

![Gated DeltaNet 单层数据流](images/GatedDeltaNet单层数据流.png)
*图 1c：Gated DeltaNet 单层完整数据流——左侧 DeltaNet 线性注意力支路（蓝色）与右侧 Sigmoid 门控支路（金色）在核心门控调制步骤汇合*

### 2.2 极致稀疏 MoE：512 专家只激活 11 个

混合专家（Mixture of Experts, MoE）架构是 Qwen3.5 实现「大模型知识、小模型成本」的核心：

| 参数 | 值 |
|------|------|
| 总专家数 | 512 |
| 每次激活路由专家 | 10 |
| 共享专家 | 1（始终激活） |
| 激活比例 | ~2.1% |
| 总参数 | 397B |
| 激活参数 | 17B |

路由不均匀是 MoE 架构的经典挑战——热门专家过载成为瓶颈，冷门专家浪费容量。Qwen3.5 通过三重机制应对：
1. **共享专家兜底**：每组固定 1 个始终激活的共享专家，保证基础能力
2. **门控机制稳定训练**：注意力门控避免路由塌陷
3. **专家路由初始化**：配合归一化策略确保大规模训练稳定收敛

### 2.3 原生多模态：从预训练第一天开始

这是 Qwen3.5 相比前代最根本的架构变化。

过去的做法是「先训文本基座，再外挂视觉模块」。Qwen3.5 彻底换了路线：**从预训练第一天起就在文本 + 视觉的混合 token 上联合学习**，视觉和语言在同一参数空间从头融合。

工程上有几个关键突破：
- 视觉和语言组件**解耦并行策略**，各走最优路径再在关键节点汇合
- 混合数据训练吞吐**接近 100% 持平纯文本基线**
- 支持 **1M token 上下文**（原生 262K，YaRN 扩展），可处理 2 小时视频
- 词表从 15 万扩展到 **25 万**，覆盖 **201 种语言和方言**

### 2.4 原生多 Token 预测

传统大模型每步只预测下一个 token。Qwen3.5 在训练阶段就学会了对后续多个位置做联合预测，推理时一次输出多个 token，速度接近翻倍。

这不是简单的「批量输出」——模型内部需要同时维护多个预测头，在训练时对多步输出的一致性做优化。

## 3. 性能评测：偏科但强势的尖子生

![Qwen3.5 Benchmark 总览](images/benchmark_score.png)
*图 2：Qwen3.5-397B-A17B 官方 Benchmark 雷达图（来源：Qwen 官方）*

Qwen3.5 的表现像一个「典型的偏科学霸」——多门考满分，但也有明显的提升空间。

### 3.1 领先维度：5 个方向排名第一

| 维度 | Benchmark | Qwen3.5 | 最强对手 | 结论 |
|------|-----------|---------|---------|------|
| 指令遵循 | IFBench | **76.5** | GPT-5.2: 75.4 | 🏆 全模型第一 |
| 搜索 Agent | BrowseComp | **78.6** | GPT-5.2: 65.8 | 🏆 大幅领先 |
| 视觉 STEM | MathVision | **88.6** | Gemini-3: 86.6 | 🏆 第一 |
| 文档 OCR | OmniDocBench | **90.8** | Gemini-3: 88.5 | 🏆 第一 |
| 多语言 | NOVA-63 | **59.1** | Claude/Gemini: 56.7 | 🏆 第一 |

**搜索 Agent 是最大亮点**。BrowseComp 78.6 超过所有闭源模型（GPT-5.2 仅 65.8），说明 Qwen3.5 在自主浏览网页、信息检索和整合方面有显著优势。

### 3.2 追赶维度：竞赛数学和通用 Agent

| 维度 | Benchmark | Qwen3.5 | GPT-5.2 | 差距 |
|------|-----------|---------|---------|------|
| 竞赛数学 | AIME 2026 | 91.3 | **96.7** | -5.4 |
| 竞赛数学 | HMMT Nov | 92.7 | **100** | -7.3 |
| 通用 Agent | MCP-Mark | 46.1 | **57.5** | -11.4 |
| 极端推理 | HLE | 28.7 | **35.5** | -6.8 |
| 代码 Agent | SWE-bench | 76.4 | 80.0 | -3.6 |

竞赛数学和极端推理是与 GPT-5.2 差距最大的领域。HMMT 92.7 vs 100，说明在多步严格推理上仍有提升空间。

### 3.3 效率对比：吞吐量碾压级提升

![推理吞吐量对比](images/inference_throughput.png)
*图 3：Qwen3.5 vs 前代模型推理吞吐量对比（来源：Qwen 官方）*

| 对比对象 | 32K 上下文 | 256K 上下文 |
|----------|-----------|------------|
| vs Qwen3-Max (>1T 参数) | **8.6×** | **19×** |
| vs Qwen3-235B-A22B | **3.5×** | **7.2×** |

部署显存比 Qwen3-Max 降低 **60%**。这意味着过去需要一整个机柜的工作，现在一台 8 卡 H100 服务器就能搞定。

## 4. 强化学习 Scaling：Agent 能力的引擎

![RL Scaling 曲线](images/rl_scaling.png)
*图 4：RL 环境规模扩展带来的 Agent 能力提升（来源：Qwen 官方）*

Qwen3.5 的 Post-training 性能提升核心来源之一是**强化学习环境的全面扩展**。官方强调的不是针对特定 benchmark 刷分，而是 RL 环境的**难度与可泛化性**。

关键设计：
- **百万级 Agent 脚手架与环境编排**：支持大规模并行环境交互
- **训推分离架构**：解耦式设计提升硬件利用率
- **异步 RL 框架**：FP8 训推、投机采样、Rollout 路由回放等技术优化
- **端到端加速 3×–5×**

## 5. 训练基础设施：近 100% 多模态训练效率

![训练基础设施](images/infra_architecture.jpg)
*图 5：Qwen3.5 异构训练基础设施架构（来源：Qwen 官方）*

Qwen3.5 在训练基础设施上实现了多项工程突破：

1. **异构并行**：视觉与语言组件解耦并行策略，利用稀疏激活实现跨模块计算重叠
2. **原生 FP8 流水线**：激活显存降低 ~50%，加速 >10%，稳定扩展至数万亿 token
3. **运行时精度监控**：敏感层自动保持 BF16，非敏感层用 FP8
4. **异步 RL 框架**：动态负载均衡 + 细粒度故障恢复 + 多轮 Rollout 锁定

## 6. 部署与工程实践

### 6.1 部署方式速查

```bash
# SGLang 部署（推荐生产环境）
python -m sglang.launch_server \
    --model-path Qwen/Qwen3.5-397B-A17B \
    --port 8000 \
    --tp-size 8 \
    --context-length 262144 \
    --reasoning-parser qwen3

# vLLM 部署
vllm serve Qwen/Qwen3.5-397B-A17B \
    --port 8000 \
    --tensor-parallel-size 8 \
    --max-model-len 262144 \
    --reasoning-parser qwen3

# Transformers 快速启动
transformers serve --port 8000 --continuous-batching
```

### 6.2 API 调用示例

```python
# 通过阿里云百炼 API 调用 Qwen3.5-Plus
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 开启推理模式（链式思考）+ 联网搜索
completion = client.chat.completions.create(
    model="qwen3.5-plus",
    messages=[{"role": "user", "content": "分析 Qwen3.5 的架构创新"}],
    extra_body={
        "enable_thinking": True,   # 开启链式思考
        "enable_search": True,     # 开启联网搜索 + Code Interpreter
    },
    stream=True
)
```

### 6.3 硬件需求与成本

| 部署方式 | 硬件需求 | 月成本估算 | 适用场景 |
|----------|---------|-----------|---------|
| API (百炼) | 无 | 按量付费 0.8元/M tokens | 快速验证、中小规模 |
| 自部署 FP16 | 8×H100 80GB | ~4-8 万元/月 | 大规模生产、数据安全 |
| 自部署 FP8 | 8×H100 80GB | ~4-8 万元/月 | 更高吞吐 |
| 量化 4-bit | 3-4×A100 | ~2-4 万元/月 | 成本敏感、可接受精度损失 |
| Apple Silicon | M4 Ultra 256GB+ | 一次性购买 | 个人研究（速度慢） |

## 7. 生产落地评估

基于深度分析，以下是将 Qwen3.5 投入生产的关键考量。

### 7.1 最佳适用场景

- **中文 AI 应用**：中文知识和指令遵循能力突出（C-Eval 93.0, IFBench 76.5）
- **文档处理与 OCR**：OmniDocBench 90.8 全场第一，PDF/扫描件理解强
- **搜索增强 Agent**：BrowseComp 78.6 全模型第一，适合构建信息检索系统
- **视觉 STEM 推理**：MathVision 88.6，适合教育、科研辅助
- **多语言服务**：201 种语言覆盖，适合全球化产品
- **高性价比推理服务**：API 定价是 GPT-5.2 的 1/15

### 7.2 不适用场景

- **竞赛级数学推理**：AIME 91.3 vs GPT-5.2 的 96.7，对精度要求极高的数学场景
- **复杂多步工具编排**：MCP-Mark 46.1，复杂工作流不如 GPT-5.2 稳定
- **长上下文精确检索**：LongBench v2 63.2，不如 Claude 4.5 的 64.4 和 Gemini-3 的 68.2

### 7.3 关键风险清单

| 风险维度 | 风险等级 | 说明 |
|----------|---------|------|
| 显存门槛 | 中 | 至少 8×A100/H100，消费级硬件不适合生产 |
| 线性注意力质量损失 | 中 | 超长上下文和极端精度场景有可感知差距 |
| 首发版本成熟度 | 中 | 文档和生态尚不完善，建议 2-4 周后投产 |
| API 供应商单一 | 中 | 阿里云百炼是唯一官方 API 提供商 |
| 多语言安全审核 | 中 | 201 种语言增加内容审核复杂度 |
| 推理框架兼容性 | 低 | SGLang/vLLM/Transformers 均已支持 |
| API 成本 | 低 | 0.8 元/M tokens 极具竞争力 |
| 开源协议 | 低 | Apache 2.0 无使用限制 |

### 7.4 与竞品选型建议

![Qwen3.5 能力对比](images/Qwen3.5能力全景对比.png)
*图 6：Qwen3.5 vs 顶级闭源模型能力全景对比*
<!-- 🎨 视觉描述提示词: visual-prompts/Qwen3.5能力全景对比.txt → 请在 lovart.ai 用 NanoBanana Pro 生成后替换 -->

| 选型维度 | 推荐模型 | 理由 |
|----------|---------|------|
| 综合性价比 | **Qwen3.5** | 1/15 价格，80%+ 能力覆盖 |
| 极端推理/数学 | GPT-5.2 | AIME/HMMT 明显领先 |
| 代码 Agent | Claude 4.5 Opus | SWE-bench 80.9，代码生态最成熟 |
| 多模态理解 | Gemini-3 Pro | MMMU-Pro 81.0，多模态覆盖最广 |
| 中文场景首选 | **Qwen3.5** | C-Eval 93.0 + 中文生态 + 国内合规 |
| 搜索增强应用 | **Qwen3.5** | BrowseComp 78.6 全模型第一 |

## 8. 总结与展望

Qwen3.5 是一次**架构层面的代际升级**，而非简单的参数堆叠。四项技术（GDN 线性注意力、极致稀疏 MoE、原生多模态、多 Token 预测）的协同效应，让 397B 参数的模型以 17B 的计算成本达到了万亿参数的性能水平。

**核心要点回顾：**
- 🏗️ 混合架构（GDN + MoE）实现效率和质量的精妙平衡
- 👁️ 原生多模态从预训练起融合视觉和语言，告别「外挂式」
- 🚀 推理吞吐提升 8.6-19 倍，部署成本降低 60%
- 🏆 指令遵循、搜索 Agent、视觉 STEM、文档 OCR、多语言 5 项全模型第一
- 💰 API 定价 0.8 元/M tokens，是 GPT-5.2 的 1/15

**当前局限：**
- 竞赛数学和极端推理与 GPT-5.2 差距明显
- 通用 Agent 多步编排能力落后闭源第一梯队
- 首发版本文档不完善，技术论文尚未发布
- 397B-A17B 并非系列旗舰，「更大的即将到来」

**未来方向：**
官方明确了下一阶段的重点将从模型规模转向**系统整合**：构建具备跨会话持久记忆的智能体、面向真实世界交互的具身接口、自我改进机制。目标是将以任务为边界的 AI 助手升级为**可持续、可信任的 AI 伙伴**。

## 参考资料

1. [Qwen3.5 官方博客](https://qwen.ai/blog?id=qwen3.5) — Qwen Team, 2026-02-16
2. [Qwen3.5 GitHub 仓库](https://github.com/QwenLM/Qwen3.5) — Apache 2.0 开源
3. [千问3.5全网最详细解读](https://news.qq.com/rain/a/20260216A0602I00)
4. [Qwen3.5 除夕夜炸场](https://news.qq.com/rain/a/20260216A05T0V00)
5. Yang, S. et al. *Parallelizing Linear Transformers with the Delta Rule*. ICML 2024. [arXiv:2406.06484](https://arxiv.org/abs/2406.06484)
6. Qiu, Z. et al. *Gated Attention for LLMs: Non-linearity, Sparsity, and Attention-Sink-Free*. **NeurIPS 2025 Best Paper**. [arXiv:2505.06708](https://arxiv.org/abs/2505.06708)
7. [Qwen3 部署与使用教程](https://doc.damodel.com/profile/best_practice/Qwen3/Qwen3.html)
8. [Qwen 模型应用：微调与部署实践](https://developer.aliyun.com/article/1646767)
9. [GDN 深度解析（完整公式推导与伪代码）](gated_delta_networks.md) — 本文附属技术文档

*本文基于 Qwen3.5 首发版本（2026-02-16）撰写。模型持续更新中，更多尺寸和完整技术报告即将发布。*
