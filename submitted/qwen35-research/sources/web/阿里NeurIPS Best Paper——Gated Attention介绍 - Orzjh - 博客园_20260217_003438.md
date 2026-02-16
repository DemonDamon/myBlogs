# 阿里NeurIPS Best Paper——Gated Attention介绍 - Orzjh - 博客园

原文链接: https://www.cnblogs.com/Orzjh/p/19299950

[![返回主页](/skins/custom/images/logo.gif)](images/5f9620b87fafb2b6e69cbfeeb80556af.jpg)

# [Orzjh's Blog](https://www.cnblogs.com/Orzjh)

##

* [博客园](https://www.cnblogs.com/)
* [首页](https://www.cnblogs.com/Orzjh/)
* [新随笔](https://i.cnblogs.com/EditPosts.aspx?opt=1)
* [联系](https://msg.cnblogs.com/send/Orzjh)
* [订阅](javascript:void(0))
* [管理](https://i.cnblogs.com/)

# [阿里NeurIPS Best Paper——Gated Attention介绍](https://www.cnblogs.com/Orzjh/p/19299950 "发布于 2025-12-03 02:03")

**Gated Attention for Large Language Models: Non-linearity, Sparsity, and Attention-Sink-Free**

https://hjfy.top/arxiv/2505.06708

**TL; DR**

这篇论文提出了一种 **Gated Attention (门控注意力)** 机制，即在标准 Multi-Head Attention 的 SDPA（缩放点积注意力）输出之后，插入一个**依赖于输入且 Head-Specific 的 Sigmoid 门控**，用于动态调节每个 Head 的信息流。

![](images/c9f87578d1297532f3f622b27aca5f78.png)

**Method**

该方法并没有改变 Attention 的根本计算逻辑（QKV 计算），而是在 Value 被加权求和之后、进入最终线性层之前，做了一次“过滤”。

**计算 Gate Score**: 利用输入 （通常是 Pre-norm 后的 Hidden States），通过一个轻量级的线性层 变换，再经过 **Sigmoid** 激活函数，得到**门控分数**。

**执行 Modulation**: 将 SDPA 的输出 与门控分数进行 **Element-wise Product (逐元素相乘)**。

**Head-Specific**: 每个 Attention Head 都有自己独立的门控参数，而不是所有 Head 共享一个。

**这是论文中最关键的公式：**

: 标准 Scaled Dot-Product Attention 的输出结果。

: 当前层的输入 Hidden States（作为 Gate 的控制信号）。

: **Sigmoid 函数**。注意：这里选 Sigmoid 而不是 SiLU 是关键，因为 Sigmoid 能输出 ，从而允许门控值接近 0（产生稀疏性）。

: 逐元素乘法。

gemini解释: 这个公式是在做**“基于上下文的噪声过滤”**。 是注意力提取出的原始特征， 就像一个过滤器。如果 ，说明模型认为这部分注意力提取的信息对于当前 Query 是无效的（例如 Attention Sink 产生的垃圾值），直接丢弃。

**gemini给出的数据流向（单头）**

|  |
| --- |
| Plain Text Input (X)   ├──> [Linear Projections] -> Q, K, V  │ │  │ [SDPA: softmax(Q@K.T) @ V] -> Attention Output (Y)  │ │  └──> [Gate Proj: Sigmoid(X @ W\_gate)] -> Gate Score (G)  │  **[Modulation: Y \* G]** <────────────┘ (G1 Position)  │  v  [Output Projection W\_o] -> Final Output |

**gemini给出的数据流向（多头）**

|  |
| --- |
| C++ Input (X) Shape: [B, L, D]  │  │ ┌─── (支路 A: Attention 计算) ─────────────────────────────┐  │ │ │  ├──> [Linear Projections Q, K, V] │  │ Shape: [B, L, D] │  │ │ │  │ [Reshape & Split Heads] │  │ Shape: [B, L, h, d\_k] │  │ │ │  │ [SDPA: softmax(Q@K.T) @ V] │  │ Shape: [B, L, h, d\_k] │  │ │ │  │ [Attention Output (Y)] │  │ Shape: [B, L, h, d\_k] │  │ │ │  │ │ │  │ ┌─── (支路 B: Gate 计算) ──────────|───────────────────────┘  │ │ │  └──> [Gate Proj: Linear(X @ W\_gate)] │  Shape: [B, L, D] │  │ │  [Activation: Sigmoid] │  Shape: [B, L, D] │  │ │  [Reshape to Heads] │ (关键: 为了和 Y 对齐)  Shape: [B, L, h, d\_k] │  │ │  [Gate Score (G)] │  Shape: [B, L, h, d\_k] │  │  │  [Modulation: Y \* G] <────────────┘ (逐元素相乘 Element-wise)  Shape: [B, L, h, d\_k]  │  │  v  [Concat Heads / Flatten]  Shape: [B, L, D]  │  │  v  [Output Projection W\_o] ───────> Final Output  Shape: [B, L, D] Shape: [B, L, D] |

**Result**

感兴趣的可以看看论文中的实验，做的还挺solid的。

**性能提升**: PPL 降低了约 0.2，优于增加参数量的 Baseline。

**训练极稳**: 彻底消除了 Loss Spikes，支持更大的学习率训练。

**Sink 消除**: First Token 的注意力占比从 ~46% 降至 ~4.8%。

**Analysis**

**消除了低秩瓶颈 (Low-Rank Bottleneck):** 在标准 Attention 中，Value 投影矩阵 ( ) 和 Output 投影矩阵 ( ) 是连续相乘的线性层。从数学上看，两个连续的线性层本质上可以坍缩为一个低秩映射，这限制了模型在 这一步的非线性表达能力。

![](images/a0f3c313c781cab8de97db1c0b5e8873.png)

Gating 的第一个作用就是充当了“激活函数”。 通过引入 Gating，在 和 之间强行插入了非线性操作，增加了线性变换的秩和表达能力。

**引入了输入依赖的稀疏性 (Input-Dependent Sparsity):** Sigmoid 产生的 Gate Score 具有很强的稀疏性，能够过滤掉无关的上下文信息。而且其不仅过滤了噪声，更关键的是消除了必须关注某个 Token（如首 Token）的刚性约束（Attention Sink）。

![](images/3542434438ea8d7e0b060e2c173ccc7e.png)

**消除了注意力陷阱(Attention Sink):** 由于标准 Softmax 中所有值加起来必须为1，导致在当前 Query 无法在上下文中找到相关信息（即缺乏匹配的 Key）时，模型倾向于将大量注意力分数分配给第一个 Token（作为“垃圾桶”来存放多余的注意力权重），这不仅破坏了语义分布，也严重影响了长文本外推能力。

![](images/627d97df285225e0e969f92993d9cf69.png)

posted @
2025-12-03 02:03
[Orzjh](https://www.cnblogs.com/Orzjh)
阅读(685)
评论(0)

[收藏](javascript:void(0))
[举报](javascript:void(0))

[刷新页面](#)[返回顶部](#top)

[![](images/e5df06f95189e0b7ee4fcf63b30c1628.jpg)](https://dis.chatdesks.cn/chatdesk/jmcnblogs.html)

### 公告

[博客园](https://www.cnblogs.com/)
  ©  2004-2026

[![](images/9cc3128655f9ed3b7637356f49069fc5.png)浙公网安备 33010602011771号](images/4082a8cb1e24bb41648ee3e764134e54.jpg)
[浙ICP备2021040463号-3](https://beian.miit.gov.cn)