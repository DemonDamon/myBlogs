# Gated Delta Networks (GDN) 深度解析：从公式到实现

> 本文拆解 Qwen3.5 核心注意力机制——Gated Delta Networks 的数学原理、关键伪代码和工程设计，涵盖三篇核心论文的技术脉络。

## 1. 技术脉络：从 Softmax Attention 到 GDN

Gated Delta Networks 并非凭空而来，而是**三项独立研究的交汇**：

| 论文 | 核心贡献 | 发表 |
|------|---------|------|
| [DeltaNet](https://arxiv.org/abs/2406.06484) — *Parallelizing Linear Transformers with the Delta Rule* | 用 Delta Rule 替代线性注意力的加法更新，提升关联记忆能力 | ICML 2024 |
| [Gated Attention](https://arxiv.org/abs/2505.06708) — *Gated Attention for LLMs: Non-linearity, Sparsity, and Attention-Sink-Free* | 在 SDPA 输出后加 Sigmoid 门控，消除 Attention Sink | NeurIPS 2025 Best Paper |
| Qwen3-Next / Qwen3.5 | 将 Gated DeltaNet + Gated Attention 混合，构建 GDN 混合架构 | 2025-09 / 2026-02 |

**一句话总结**：GDN = DeltaNet（线性注意力 + Delta Rule）+ Gated Attention（Sigmoid 门控）。

---

## 2. 背景：为什么需要替代 Softmax Attention？

### 2.1 标准 Softmax Attention 的瓶颈

标准 Transformer 中的 Scaled Dot-Product Attention (SDPA)：

$$
\text{Attn}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right) V
$$

其中 \(Q, K, V \in \mathbb{R}^{n \times d}\)，\(n\) 为序列长度，\(d\) 为头维度。

**核心问题**：
- **时间复杂度 \(O(n^2 d)\)**：32K → 256K 上下文，计算量暴增 64 倍
- **KV Cache 线性增长**：推理时 KV Cache 随上下文线性增长，显存压力大
- **Attention Sink**：Softmax 归一化要求所有权重和为 1，当 Query 找不到相关 Key 时，注意力被迫集中在首个 Token 上（"垃圾桶效应"）

### 2.2 线性注意力的思路

线性注意力用核函数 \(\phi\) 替代 Softmax，将复杂度降至 \(O(nd^2)\)：

$$
\text{LinearAttn}(Q, K, V) = \phi(Q) \cdot \left(\phi(K)^\top V\right)
$$

关键变化：先算 \(\phi(K)^\top V\)（\(d \times d\) 矩阵），再乘 \(\phi(Q)\)。当 \(d \ll n\) 时，复杂度从 \(O(n^2 d)\) 降到 \(O(n d^2)\)，实现线性。

**但问题是**：线性注意力的表达能力远弱于 Softmax Attention，尤其在**关联记忆/检索任务**上表现很差。

---

## 3. DeltaNet：用 Delta Rule 增强线性注意力

### 3.1 线性注意力的递推视角

将线性注意力写成递推形式（RNN 视角），维护一个 **状态矩阵** \(S_t \in \mathbb{R}^{d \times d}\)：

$$
S_t = S_{t-1} + k_t v_t^\top \quad \text{(加法更新)}
$$
$$
o_t = q_t^\top S_t \quad \text{(查询输出)}
$$

这里 \(k_t, v_t, q_t \in \mathbb{R}^d\) 是第 \(t\) 步的 Key、Value、Query 向量。

**问题**：加法更新 \(S_t = S_{t-1} + k_t v_t^\top\) 只能不断叠加信息，**无法修正或覆盖旧记忆**。当新的 Key-Value 关联出现时，旧的错误关联无法被清除。

### 3.2 Delta Rule：可覆盖的记忆更新

DeltaNet 的核心创新是引入 **Delta Rule**（源自 Widrow-Hoff 学习规则）：

$$
S_t = S_{t-1} + \beta_t k_t \left(v_t - k_t^\top S_{t-1}\right)^\top
$$

展开后等价于：

$$
\boxed{S_t = \left(I - \beta_t k_t k_t^\top\right) S_{t-1} + \beta_t k_t v_t^\top}
$$

其中：
- \(\beta_t \in (0, 1]\)：学习率（标量门控），控制更新强度
- \(I - \beta_t k_t k_t^\top\)：**擦除矩阵**，选择性遗忘旧信息
- \(\beta_t k_t v_t^\top\)：**写入项**，注入新的 Key-Value 关联

**直觉理解**：
- 当 \(\beta_t = 0\) 时：\(S_t = S_{t-1}\)，完全保留旧记忆
- 当 \(\beta_t = 1\) 时：在 \(k_t\) 方向上完全覆盖旧值为 \(v_t\)
- 中间值：部分更新，平滑过渡

**与加法更新的对比**：

| 特性 | 线性注意力（加法） | DeltaNet（Delta Rule） |
|------|-------------------|----------------------|
| 更新公式 | \(S_t = S_{t-1} + k_t v_t^\top\) | \(S_t = (I - \beta k_t k_t^\top) S_{t-1} + \beta k_t v_t^\top\) |
| 记忆管理 | 只增不减，旧信息永不消失 | 可选择性覆盖/遗忘 |
| 关联检索 | 新旧关联混杂，干扰严重 | 新关联覆盖旧关联，检索准确 |
| 计算开销 | \(O(nd^2)\) | \(O(nd^2)\)，额外常数开销 |

### 3.3 并行化：Chunkwise 算法

DeltaNet 递推形式是串行的（每步依赖上一步），但论文提出了 **Chunkwise 并行算法**：

1. 将序列分为大小为 \(C\) 的 chunk
2. **chunk 内**：并行计算（利用矩阵乘法）
3. **chunk 间**：串行传递状态矩阵 \(S\)

这使得 DeltaNet 在训练时可以高效并行，推理时可以用 RNN 模式逐步生成。

---

## 4. Gated Attention：消除 Attention Sink

### 4.1 核心公式

Gated Attention（NeurIPS 2025 Best Paper, 阿里团队）的改动极其简洁：

$$
\boxed{O_{\text{gated}} = \underbrace{\text{SDPA}(Q, K, V)}_{Y} \odot \underbrace{\sigma(X W_g)}_{G}}
$$

其中：
- \(Y = \text{softmax}(QK^\top / \sqrt{d}) \cdot V\)：标准 SDPA 输出
- \(X\)：当前层输入的 Hidden States
- \(W_g\)：Head-Specific 的门控投影矩阵
- \(\sigma\)：**Sigmoid** 激活函数（输出范围 \([0, 1]\)）
- \(\odot\)：逐元素乘法

### 4.2 为什么选 Sigmoid 而不是 SiLU/ReLU？

| 激活函数 | 输出范围 | 稀疏性 | 效果 |
|---------|---------|--------|------|
| Sigmoid | \([0, 1]\) | ✅ 可以接近 0 | **最优**，PPL 最低 |
| SiLU | \((-0.28, +\infty)\) | ❌ 不稀疏 | 次优 |
| ReLU | \([0, +\infty)\) | ✅ 但范围无上界 | 训练不稳定 |

Sigmoid 的关键优势：
1. **输出可接近 0** → 产生稀疏性，有效过滤无关信息
2. **输出有上界 1** → 不会放大信号，训练稳定
3. **平滑可微** → 梯度传播良好

### 4.3 Gated Attention 的三重效果

**效果 1：消除低秩瓶颈**

标准 Attention 中 \(W_V\)（Value 投影）和 \(W_O\)（Output 投影）是连续线性层，数学上可坍缩为单一低秩映射。Sigmoid 门控在其间插入了**非线性变换**，打破了低秩约束，提升表达能力。

**效果 2：输入依赖的稀疏过滤**

Gate Score 具有高度稀疏性——对于无关的上下文信息，Gate 输出接近 0，直接过滤掉噪声。

**效果 3：消除 Attention Sink**

标准 Softmax 要求 \(\sum_j \alpha_{ij} = 1\)。当 Query 找不到相关 Key 时，多余的注意力权重被迫集中到首个 Token 上。Sigmoid 门控允许 Gate ≈ 0，相当于**允许注意力"不输出任何东西"**，彻底消除了 Attention Sink。

实验数据：首 Token 注意力占比从 ~46% 降至 ~4.8%。

---

## 5. Gated Delta Networks (GDN)：二者的融合

### 5.1 Qwen3.5 中的 GDN 架构

Qwen3.5 将 DeltaNet 和 Gated Attention 融合为 **Gated Delta Networks**：

- **Gated DeltaNet 层**：线性注意力 + Delta Rule + Sigmoid 门控
- **Gated Attention 层**：标准 Softmax 注意力 + Sigmoid 门控

在 60 层模型中，采用 **3:1 混合比例**：

```
15 组 × [GDN, GDN, GDN, Gated-Attention]
       ↑  ↑  ↑      ↑
    线性 O(n)    标准 O(n²)
```

### 5.2 Gated DeltaNet 完整公式

结合 DeltaNet 的 Delta Rule 和 Gated Attention 的门控机制：

**状态更新（线性注意力部分）**：

$$
S_t = \left(I - \beta_t k_t k_t^\top\right) \cdot \text{diag}(\alpha_t) \cdot S_{t-1} + \beta_t k_t v_t^\top
$$

**输出计算**：

$$
o_t = q_t^\top S_t
$$

**门控调制**：

$$
\boxed{y_t = o_t \odot \sigma(x_t W_g)}
$$

其中 \(\alpha_t \in (0, 1)^d\) 是逐通道的遗忘门控（衰减因子），控制各维度的记忆保留率。

### 5.3 为什么采用 3:1 混合？

| 层类型 | 复杂度 | 优势 | 劣势 |
|--------|--------|------|------|
| Gated DeltaNet | \(O(nd^2)\) | 处理长序列高效 | 长距离精确匹配弱 |
| Gated Attention | \(O(n^2d)\) | 精确关联检索 | 长序列计算量大 |

3:1 比例意味着 75% 的计算量用高效的线性注意力，25% 用精确的标准注意力做"校准"。这个比例经过大规模实验验证：
- 1:1 比例：计算量太大，效率优势不明显
- 7:1 比例：质量下降明显（长上下文检索变差）
- **3:1 比例**：速度和质量的最优平衡点

---

## 6. 关键伪代码

### 6.1 DeltaNet 递推推理（单步）

```python
def deltanet_step(q_t, k_t, v_t, beta_t, S_prev):
    """
    DeltaNet 单步递推（RNN 模式推理）
    
    Args:
        q_t: Query 向量, shape [d]
        k_t: Key 向量, shape [d] (已归一化)
        v_t: Value 向量, shape [d]
        beta_t: 学习率/更新强度, scalar in (0, 1]
        S_prev: 上一步的状态矩阵, shape [d, d]
    
    Returns:
        o_t: 输出向量, shape [d]
        S_t: 更新后的状态矩阵, shape [d, d]
    """
    # 1. 计算擦除项：选择性遗忘旧信息
    erase = beta_t * torch.outer(k_t, k_t)  # [d, d]
    
    # 2. 计算写入项：注入新的 Key-Value 关联
    write = beta_t * torch.outer(k_t, v_t)  # [d, d]
    
    # 3. Delta Rule 状态更新
    S_t = (torch.eye(d) - erase) @ S_prev + write  # [d, d]
    
    # 4. 查询：读取与 q_t 相关的记忆
    o_t = q_t @ S_t  # [d]
    
    return o_t, S_t
```

### 6.2 Gated Attention 前向传播

```python
def gated_attention_forward(X, W_q, W_k, W_v, W_o, W_gate):
    """
    Gated Attention 完整前向传播
    
    Args:
        X: 输入, shape [B, L, D]
        W_q, W_k, W_v: QKV 投影矩阵
        W_o: 输出投影矩阵
        W_gate: 门控投影矩阵 (Head-Specific)
    """
    B, L, D = X.shape
    
    # 1. 标准 QKV 投影
    Q = X @ W_q  # [B, L, D]
    K = X @ W_k
    V = X @ W_v
    
    # 2. 多头 reshape: [B, L, D] -> [B, h, L, d_k]
    Q = Q.view(B, L, h, d_k).transpose(1, 2)
    K = K.view(B, L, h, d_k).transpose(1, 2)
    V = V.view(B, L, h, d_k).transpose(1, 2)
    
    # 3. 标准 SDPA
    scores = Q @ K.transpose(-2, -1) / math.sqrt(d_k)  # [B, h, L, L]
    attn = torch.softmax(scores, dim=-1)
    Y = attn @ V  # [B, h, L, d_k]
    
    # 4. 计算 Gate Score（关键步骤！）
    G = torch.sigmoid(X @ W_gate)  # [B, L, D]
    G = G.view(B, L, h, d_k).transpose(1, 2)  # [B, h, L, d_k]
    
    # 5. 门控调制：逐元素相乘
    Y_gated = Y * G  # [B, h, L, d_k]  ← 核心操作
    
    # 6. 合并多头 + 输出投影
    Y_gated = Y_gated.transpose(1, 2).contiguous().view(B, L, D)
    output = Y_gated @ W_o  # [B, L, D]
    
    return output
```

### 6.3 GDN 混合层（Qwen3.5 风格）

```python
class GDNHybridBlock(nn.Module):
    """
    Qwen3.5 的 GDN 混合块：3 层 Gated DeltaNet + 1 层 Gated Attention
    """
    def __init__(self, d_model, n_heads, n_experts):
        super().__init__()
        # 3 层 Gated DeltaNet（线性注意力）
        self.gdn_layers = nn.ModuleList([
            GatedDeltaNetLayer(d_model, n_heads) for _ in range(3)
        ])
        # 1 层 Gated Attention（标准注意力）
        self.ga_layer = GatedAttentionLayer(d_model, n_heads)
        # 每层后接 MoE FFN
        self.moe_layers = nn.ModuleList([
            MoEFFN(d_model, n_experts) for _ in range(4)
        ])
    
    def forward(self, x):
        # Layer 1-3: Gated DeltaNet → MoE
        for i in range(3):
            x = x + self.gdn_layers[i](x)   # 线性注意力 O(n)
            x = x + self.moe_layers[i](x)    # MoE FFN
        
        # Layer 4: Gated Attention → MoE
        x = x + self.ga_layer(x)             # 标准注意力 O(n²)
        x = x + self.moe_layers[3](x)        # MoE FFN
        
        return x

# Qwen3.5 完整模型：15 组 GDN 混合块 = 60 层
model = nn.Sequential(*[GDNHybridBlock(...) for _ in range(15)])
```

---

## 7. 关键图解

### 7.1 三种注意力机制对比

![GDN 注意力机制对比](images/03_gdn_attention_comparison.png)
*图 1：标准 Softmax Attention vs 线性注意力 vs Gated DeltaNet 的状态更新机制对比*
<!-- 🎨 视觉描述提示词: visual-prompts/03_gdn_attention_comparison.txt → 请在 lovart.ai 用 NanoBanana Pro 生成后替换 -->

### 7.2 Delta Rule 记忆更新图解

**记忆覆盖 vs 记忆叠加**：

```
加法更新（线性注意力）:                  Delta Rule（DeltaNet）:
                                      
Step 1: S = [A→1]                     Step 1: S = [A→1]
Step 2: S = [A→1, B→2]               Step 2: S = [A→1, B→2]
Step 3: S = [A→1, B→2, A→3]          Step 3: S = [A→3, B→2]  ← A 被覆盖！
                                      
查询 A:                                查询 A:
  结果 = 1 + 3 = 混乱！                 结果 = 3 ✓ 正确！
```

### 7.3 Gated DeltaNet 数据流

![GDN 数据流](images/GatedDeltaNet单层数据流.png)
*图 2：Gated DeltaNet 单层完整数据流*

---

## 8. 工程影响与实际效果

### 8.1 效率提升

| 场景 | Softmax Attention | Gated DeltaNet | 提升倍数 |
|------|------------------|----------------|---------|
| 32K 上下文推理 | baseline | 8.6× 吞吐 | 8.6× |
| 256K 上下文推理 | baseline | 19× 吞吐 | 19× |
| KV Cache 大小 | \(O(n \cdot d)\) | \(O(d^2)\) 固定 | 256K 时 ~100× |
| 训练稳定性 | Loss Spike 常见 | 无 Loss Spike | — |

### 8.2 质量代价

GDN 的混合架构在大部分任务上与纯 Softmax Attention 持平或更优，但在以下场景有可感知的质量差异：

- **长距离精确引用**（如跨 1000+ 行的代码变量引用）：线性注意力的关联检索略弱
- **极端推理链**（如竞赛数学多步证明）：AIME 91.3 vs GPT-5.2 的 96.7
- **长上下文检索**：LongBench v2 63.2，略低于纯 Softmax 模型

3:1 混合比例中，每 4 层有 1 层标准注意力做"校准"，有效缓解但未完全消除这些差距。

---

## 参考文献

1. Yang, S. et al. (2024). *Parallelizing Linear Transformers with the Delta Rule over Sequence Length*. ICML 2024. [arXiv:2406.06484](https://arxiv.org/abs/2406.06484)
2. Qiu, Z. et al. (2025). *Gated Attention for Large Language Models: Non-linearity, Sparsity, and Attention-Sink-Free*. NeurIPS 2025 Best Paper. [arXiv:2505.06708](https://arxiv.org/abs/2505.06708)
3. Qwen Team (2026). *Qwen3.5: Towards Native Multimodal Agents*. [Blog](https://qwen.ai/blog?id=qwen3.5)
4. Zhang, Y. et al. (2024). *Gated Slot Attention for Efficient Linear-Time Sequence Modeling*. [arXiv:2409.07146](https://arxiv.org/abs/2409.07146)
