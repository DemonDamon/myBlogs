# Engram：条件记忆 — 技术细节与数学公式推导

> 来源：Conditional Memory via Scalable Lookup (DeepSeek × 北大)  
> GitHub: https://github.com/deepseek-ai/Engram

## 1. 动机：MoE 之外的稀疏轴

| 稀疏维度 | 代表方案 | 激活方式 | 瓶颈 |
|----------|----------|----------|------|
| **参数稀疏** | MoE | Top-k 路由 | 动态路由开销 + 显存碎片 |
| **记忆稀疏** | Engram | 哈希查表 O(1) | 如何与计算耦合？ |

语言信号 = **动态推理** + **静态知识**。MoE 只解决「算得少」，但 BERT/GPT 仍被迫用前若干层「硬记」实体/短语。Engram 把「死记」交给可扩展查表，让算力留给真正的推理。

## 2. 架构：N-Gram 查找式记忆

### 2.1 三步流水线

**Step 1：Tokenizer 压缩**

- NFKC + 小写归一化
- 128K 词表 → 98K 有效词表（约 23% 压缩）
- 提升 N-gram 覆盖密度与泛化效率

**Step 2：多头哈希检索**

- 2-gram、3-gram 各 8 个哈希头
- 输入 token 序列切分为重叠 N-gram 片段
- 通过哈希函数映射到嵌入表对应槽位
- **O(1) 时间复杂度**，与模型规模无关

**Step 3：上下文门控 + 轻卷积**

- 以当前隐藏态为 Query，检索所得嵌入为 Key/Value
- 可学习门控单元抑制无关噪声
- 1-D 深度因果卷积（SiLU）增强非线性

### 2.2 数学形式（概念）

设输入序列 $x_{1:T}$，N-gram 片段集合 $\mathcal{G}$，嵌入表 $\mathcal{E}$：

$$\text{lookup}(g) = \mathcal{E}[\text{hash}(g) \mod |\mathcal{E}|]$$

$$\text{retrieved} = \bigoplus_{g \in \mathcal{G}(x)} \text{lookup}(g)$$

门控融合：

$$\text{output} = \sigma(W_g [h_t; \text{retrieved}]) \odot \text{retrieved} + \text{Conv1d}(h_t)$$

其中 $h_t$ 为当前隐状态，$\sigma$ 为 sigmoid，$\odot$ 为逐元素乘。

### 2.3 与 mHC 集成

Engram 与 DeepSeek mHC（M=4 分支）共用 Value 矩阵，各分支独立 Key，实现多分支集成。

## 3. 稀疏分配：U 形扩展律

论文通过**稀疏分配问题**形式化 MoE 与 Engram 的权衡，发现：

- **20%–25%** 参数预算分配给 Engram 时，模型性能最佳
- 呈现 **U 形**扩展规律
- Engram-27B 在等参数、等 FLOPs 下优于纯 MoE-27B

## 4. 系统效率

- **确定性寻址**：支持将大规模嵌入表卸载到主机内存（DRAM/SSD）
- 100 亿参数 Engram 表完全卸载到 DRAM 时，**端到端吞吐下降 < 3%**
- 分层存储：高频 → HBM，低频 → SSD
- 训练期 All-to-All 切片；推理期整表放 CPU 内存，PCIe 预取与计算重叠

## 5. 与 RAG 对比

| 维度 | RAG | Engram |
|------|-----|--------|
| 记忆来源 | 外部向量库 | 模型内部参数（预训练） |
| 检索方式 | 向量相似度 | 稀疏查表 O(1) |
| 端到端延迟 | 依赖外部服务 | 内嵌，吞吐下降 <3% |
| 知识更新 | 需重新索引 | 微调更新 |

## 6. 实验结论（Engram-27B）

- 通用知识：+3.4%
- 中文知识：+4.0%
- 复杂推理：+5.0%
- 数学：+2.4%
- HumanEval 代码：+3.0%
- 长上下文检索能力显著提升

## 7. 参考文献

- Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models
- GitHub: deepseek-ai/Engram
