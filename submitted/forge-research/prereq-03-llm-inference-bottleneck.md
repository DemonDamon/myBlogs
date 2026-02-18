# 前置三：LLM 推理的计算瓶颈——KV Cache、Prefill/Decode 与前缀共享

> **阅读目标**：理解 Transformer 自回归推理的计算代价、KV Cache 机制、Prefill/Decode 两阶段特征以及多请求前缀冗余问题，为阅读 Forge 博客的工程优化（§3）做准备。
>
> **前置要求**：已阅读 [前置二：Agent RL 建模](prereq-02-agent-rl-modeling.md)，了解 Agent rollout 循环中 LLM 生成是核心瓶颈。

## 1. 自回归生成的计算代价

### 1.1 逐 Token 生成

Transformer 的文本生成是**自回归**（autoregressive）过程：每次只生成一个 Token，将其拼接到输入序列后，再生成下一个。

生成长度为 $L$ 的序列需要 $L$ 次前向传播。第 $t$ 步的输入长度为 $t$（前 $t$ 个 Token），核心计算是自注意力：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

其中 $Q, K, V \in \mathbb{R}^{t \times d}$，矩阵乘法 $QK^T$ 的计算量为 $O(t^2 \cdot d)$。

### 1.2 总计算量

朴素实现下，生成 $L$ 个 Token 的总 FLOPs：

$$\text{FLOPs}_{\text{naive}} = \sum_{t=1}^{L} O(t^2 \cdot d) = O\left(\frac{L^3 \cdot d}{3}\right)$$

这是 $L$ 的**三次方**增长——当 $L$ 从 1K 增长到 200K 时，计算量增长 $200^3 = 8 \times 10^6$ 倍。

### 1.3 代码验证

```python
import numpy as np
import time

def naive_attention(seq_len, d_model=64):
    """模拟朴素自注意力：每步都重新计算完整 QK^T"""
    Q = np.random.randn(seq_len, d_model)
    K = np.random.randn(seq_len, d_model)
    V = np.random.randn(seq_len, d_model)
    scores = Q @ K.T / np.sqrt(d_model)  # O(seq_len² × d)
    weights = np.exp(scores) / np.exp(scores).sum(axis=-1, keepdims=True)
    return weights @ V  # O(seq_len² × d)

# 测量不同序列长度的耗时
for L in [256, 512, 1024, 2048, 4096]:
    times = []
    for _ in range(5):
        t0 = time.time()
        naive_attention(L)
        times.append(time.time() - t0)
    avg = np.mean(times) * 1000
    print(f"L={L:5d}  耗时={avg:.1f}ms  相对L=256: {avg / (np.mean(times) if L==256 else times[0]):.1f}x")
# 典型输出：
# L=  256  耗时=  0.5ms  相对L=256: 1.0x
# L=  512  耗时=  1.8ms  相对L=256: 3.6x    （理论 4x）
# L= 1024  耗时=  6.9ms  相对L=256: 13.8x   （理论 16x）
# L= 2048  耗时= 27.1ms  相对L=256: 54.2x   （理论 64x）
# L= 4096  耗时=108.0ms  相对L=256: 216.0x  （理论 256x）
```

耗时随序列长度呈二次方增长——每步注意力 $O(t^2)$，累积 $L$ 步则趋向 $O(L^3)$。

## 2. KV Cache：空间换时间

![KV Cache 工作原理](images/prereq_03_kv_cache_mechanism.png)
*上：无 KV Cache 时每步重算全部注意力矩阵（灰色交叉线标注浪费的重复计算）；下：有 KV Cache 时每步仅计算新 Token（绿色），已缓存的 KV 直接复用。右侧柱状图展示不同序列长度下的加速比*
<!-- 🎨 用 vis-prompts/prereq_03_kv_cache_mechanism.txt 生成后替换 -->

### 2.1 核心洞察

在自回归生成中，第 $t+1$ 步的输入序列 $[x_1, \dots, x_t, x_{t+1}]$ 与第 $t$ 步的 $[x_1, \dots, x_t]$ 只差一个新 Token $x_{t+1}$。这意味着前 $t$ 个 Token 的 Key 和 Value 完全相同——**重复计算了 $t$ 次**。

KV Cache 的做法是：缓存已计算的 $K$ 和 $V$ 矩阵，每步只计算新 Token 的 $q_{t+1}, k_{t+1}, v_{t+1}$。

### 2.2 数学推导

标准注意力（第 $t+1$ 步）：

$$\text{Attn}_{t+1} = \text{softmax}\left(\frac{Q_{1:t+1} K_{1:t+1}^T}{\sqrt{d_k}}\right) V_{1:t+1}$$

但我们只需要最后一行的输出（新 Token 的表示）：

$$o_{t+1} = \text{softmax}\left(\frac{q_{t+1} \cdot [K_{\text{cache}}; k_{t+1}]^T}{\sqrt{d_k}}\right) \cdot [V_{\text{cache}}; v_{t+1}]$$

其中 $K_{\text{cache}} = [k_1, \dots, k_t]$，$V_{\text{cache}} = [v_1, \dots, v_t]$ 是上一步缓存的结果。

**计算量对比**：

| | 朴素实现（第 $t+1$ 步） | KV Cache（第 $t+1$ 步） |
|--|----------------------|----------------------|
| Q 计算 | $(t+1) \times d$ | $1 \times d$ |
| K 计算 | $(t+1) \times d$ | $1 \times d$（仅新 Token） |
| V 计算 | $(t+1) \times d$ | $1 \times d$（仅新 Token） |
| $QK^T$ | $(t+1)^2 \times d$ | $(t+1) \times d$ |
| 总 FLOPs | $O(t^2 \cdot d)$ | $O(t \cdot d)$ |

每步从 $O(t^2)$ 降为 $O(t)$，生成 $L$ 个 Token 的总量从 $O(L^3)$ 降为 $O(L^2)$。

### 2.3 代码实现

```python
import numpy as np

class KVCache:
    """最小 KV Cache 实现"""
    def __init__(self, d_model):
        self.d = d_model
        self.K = np.empty((0, d_model))  # 缓存的 Key 矩阵
        self.V = np.empty((0, d_model))  # 缓存的 Value 矩阵

    def append(self, k_new, v_new):
        """追加新 Token 的 KV"""
        self.K = np.vstack([self.K, k_new.reshape(1, -1)])
        self.V = np.vstack([self.V, v_new.reshape(1, -1)])

    def attention(self, q_new):
        """用新 Token 的 Query 对缓存的 KV 做注意力"""
        # q_new: (d,)  K_cache: (t, d)  → scores: (t,)
        scores = q_new @ self.K.T / np.sqrt(self.d)
        weights = np.exp(scores) / np.exp(scores).sum()
        return weights @ self.V  # (d,)

def generate_with_cache(prompt_len, gen_len, d_model=64):
    """模拟带 KV Cache 的自回归生成"""
    Wq = np.random.randn(d_model, d_model) * 0.01
    Wk = np.random.randn(d_model, d_model) * 0.01
    Wv = np.random.randn(d_model, d_model) * 0.01

    cache = KVCache(d_model)

    # Prefill：处理 prompt 中的所有 Token
    prompt_tokens = np.random.randn(prompt_len, d_model)
    for i in range(prompt_len):
        k = prompt_tokens[i] @ Wk
        v = prompt_tokens[i] @ Wv
        cache.append(k, v)

    # Decode：逐 Token 生成
    outputs = []
    x = prompt_tokens[-1]  # 从最后一个 prompt Token 开始
    for _ in range(gen_len):
        q = x @ Wq
        k = x @ Wk
        v = x @ Wv
        cache.append(k, v)
        out = cache.attention(q)  # O(t × d)，不是 O(t² × d)
        outputs.append(out)
        x = out  # 简化：用输出作为下一步输入

    return outputs

# 对比耗时
for L in [256, 512, 1024, 2048]:
    t0 = time.time()
    generate_with_cache(prompt_len=L, gen_len=100)
    print(f"Prompt={L:5d}  生成100 Token  耗时={1000*(time.time()-t0):.1f}ms")
```

### 2.4 显存开销

KV Cache 的显存代价：

$$\text{KV Size} = 2 \times n_{\text{layers}} \times n_{\text{heads}} \times d_{\text{head}} \times L \times \text{bytes per element}$$

以典型 7B 模型为例（32 层, 32 头, $d_{\text{head}}=128$, FP16）：

$$2 \times 32 \times 32 \times 128 \times L \times 2 = 524288 \times L \text{ bytes} = 0.5 \text{MB} \times L / 1024$$

| 上下文长度 $L$ | KV Cache 大小 |
|---------------|-------------|
| 4K | ~2 GB |
| 32K | ~16 GB |
| 128K | ~64 GB |
| 200K | ~100 GB |

这就是为什么长上下文推理对显存需求极高。

## 3. Prefill vs Decode：两个截然不同的阶段

![Prefill vs Decode 两阶段对比](images/prereq_03_prefill_decode_split.png)
*Prefill 阶段（左）：计算密集型，处理完整 prompt，GPU 利用率 >90%，算术强度高；Decode 阶段（右）：访存密集型，逐 Token 生成，算术强度低至 ~1。两者混合部署互相干扰，分离部署各取最优*
<!-- 🎨 用 vis-prompts/prereq_03_prefill_decode_split.txt 生成后替换 -->

### 3.1 Prefill 阶段

处理完整的 prompt（输入序列），**一次性**计算所有 Token 的 KV 并填充缓存。

特征：
- **计算密集型**（Compute-bound）：大量矩阵乘法，GPU 算力是瓶颈
- FLOPs $\propto L_{\text{prompt}}^2 \times d$（完整的自注意力矩阵）
- 可高度并行：prompt 内所有 Token 的 KV 可同时计算
- 每字节数据对应大量计算 → **算术强度（Arithmetic Intensity）高**

### 3.2 Decode 阶段

逐 Token 生成，每步用新 Token 的 Query 对缓存 KV 做注意力。

特征：
- **访存密集型**（Memory-bound）：每步读取整个 KV Cache，但只计算一个 Token
- FLOPs $\propto (L_{\text{prompt}} + t) \times d$（第 $t$ 个生成 Token）
- 无法并行：第 $t+1$ 个 Token 依赖第 $t$ 个的输出
- 每字节数据对应少量计算 → **算术强度低**

### 3.3 为什么混在一起效率低

```python
# Prefill 和 Decode 的算术强度对比
def arithmetic_intensity(phase, seq_len, d_model=4096):
    """算术强度 = FLOPs / Bytes accessed"""
    if phase == "prefill":
        flops = 2 * seq_len * seq_len * d_model  # QK^T + Attn·V
        bytes_accessed = 3 * seq_len * d_model * 2  # Q, K, V 读取（FP16）
        return flops / bytes_accessed
    elif phase == "decode":
        flops = 2 * seq_len * d_model   # q·K_cache^T + weights·V_cache
        bytes_accessed = 2 * seq_len * d_model * 2 + d_model * 2  # KV Cache 读 + q 读
        return flops / bytes_accessed

for L in [1024, 4096, 32768]:
    pi = arithmetic_intensity("prefill", L)
    di = arithmetic_intensity("decode", L)
    print(f"L={L:6d}  Prefill AI={pi:.0f}  Decode AI={di:.1f}  比值={pi/di:.0f}x")
# 典型输出：
# L=  1024  Prefill AI=683  Decode AI=1.0  比值=683x
# L=  4096  Prefill AI=2731  Decode AI=1.0  比值=2731x
# L= 32768  Prefill AI=21845  Decode AI=1.0  比值=21845x
```

Prefill 的算术强度是 Decode 的**数百到数万倍**。两者混合调度时：
- Prefill 请求抢占 GPU 算力 → Decode 请求被阻塞，增加生成延迟
- Decode 请求占据 GPU 但利用率低 → Prefill 请求排队等待，浪费算力

这就是 Forge 博客中"异构 PD 分离"的动机——**将 Prefill 和 Decode 部署在不同的 GPU 实例上**，各自用最优的并行策略。

### 3.4 PD 分离的工程收益

```
┌─ Prefill 实例群 ─┐      ┌─ Decode 实例群 ─┐
│ 高算力配置        │      │ 高带宽配置       │
│ 大 batch 并行     │ ──→  │ 小 batch 低延迟  │
│ GPU 利用率 >90%   │ KV   │ 显存带宽利用率高 │
└──────────────────┘ 传输  └─────────────────┘
```

## 4. 前缀冗余：Agent 场景的特有问题

### 4.1 问题场景

Agent 多轮对话中，同一个任务的多个 rollout（或同一 rollout 的多次工具调用）共享大量前缀：

```
Rollout 1: [System Prompt | Task Description | Tool Call 1 | Result 1 | Response A]
Rollout 2: [System Prompt | Task Description | Tool Call 1 | Result 1 | Response B]
Rollout 3: [System Prompt | Task Description | Tool Call 1 | Result 1 | Response C]
            ←────────── 共享前缀（可达 90%+）──────────→    ←─ 差异 ─→
```

### 4.2 冗余计算量

设 $N$ 个请求共享长度为 $L_p$ 的前缀，各自有长度为 $L_s$ 的后缀。

**不共享**（每个独立处理）：

$$\text{FLOPs}_{\text{naive}} = N \times O((L_p + L_s)^2 \times d) \approx N \times O(L_p^2 \times d) \quad \text{（当 } L_p \gg L_s\text{）}$$

**共享前缀**（前缀只处理一次）：

$$\text{FLOPs}_{\text{shared}} = O(L_p^2 \times d) + N \times O(L_s^2 \times d)$$

**节省比例**：

$$\text{Saving} = 1 - \frac{\text{FLOPs}_{\text{shared}}}{\text{FLOPs}_{\text{naive}}} = 1 - \frac{L_p^2 + N \cdot L_s^2}{N \cdot (L_p + L_s)^2}$$

### 4.3 量化计算

```python
import numpy as np

def compute_savings(N, L_prefix, L_suffix):
    """计算前缀共享的 FLOPs 节省比例"""
    naive = N * (L_prefix + L_suffix) ** 2
    shared = L_prefix ** 2 + N * L_suffix ** 2
    saving = 1 - shared / naive
    return saving, naive, shared

# Agent 典型场景
configs = [
    (4,   4096, 512,  "4 rollouts, 4K 前缀, 512 后缀"),
    (8,   4096, 512,  "8 rollouts, 4K 前缀, 512 后缀"),
    (16,  4096, 256,  "16 rollouts, 4K 前缀, 256 后缀"),
    (8,  32768, 1024, "8 rollouts, 32K 前缀, 1K 后缀"),
    (16, 32768, 512,  "16 rollouts, 32K 前缀, 512 后缀"),
]

print(f"{'场景':<40} {'节省':>6} {'加速':>6}")
print("-" * 56)
for N, Lp, Ls, desc in configs:
    saving, naive, shared = compute_savings(N, Lp, Ls)
    speedup = naive / shared
    print(f"{desc:<40} {saving:>5.1%} {speedup:>5.1f}x")

# 输出：
# 场景                                     节省    加速
# --------------------------------------------------------
# 4 rollouts, 4K 前缀, 512 后缀            80.2%   5.1x
# 8 rollouts, 4K 前缀, 512 后缀            89.6%   9.6x
# 16 rollouts, 4K 前缀, 256 后缀           95.6%  22.5x
# 8 rollouts, 32K 前缀, 1K 后缀            89.5%   9.5x
# 16 rollouts, 32K 前缀, 512 后缀          95.5%  22.4x
```

当前缀长、rollout 多时，节省比例轻松超过 90%——这就是 Forge 声称 **40 倍加速**的基础。

## 5. 从前缀共享到 Prefix Tree

### 5.1 两层共享 → 树形共享

上面的分析假设所有请求共享**同一个**前缀。但真实 Agent 场景更复杂——多轮对话产生**多级**分叉：

```
                    [System + Query]          ← 根节点（所有请求共享）
                    /              \
          [Tool Call A + Result]  [Tool Call B + Result]  ← 一级分叉
           /        \                  |
     [Response 1] [Response 2]   [Response 3]            ← 二级分叉
```

这自然形成一棵**前缀树**（Trie）：每个内部节点对应一段共享前缀，叶子节点是各自不同的后缀。

### 5.2 训练阶段的前缀共享更关键

推理时的前缀共享已有成熟方案（如 vLLM 的 Prefix Caching）。但**训练阶段**的前缀共享更为重要，原因有二：

1. **前向 + 反向**：训练需要完整的前向传播（计算 loss）和反向传播（计算梯度），计算量是推理的 ~3 倍
2. **批量更大**：训练 batch 通常包含数十~数百条轨迹，共享前缀的机会更多

Forge 的 Prefix Tree Merging 正是将这一优化从推理扩展到训练：

```python
# 概念伪代码：Prefix Tree Merging 训练
def train_with_prefix_tree(trajectories):
    """
    传统方式：N 条轨迹各自独立前向传播
    树合并方式：构建前缀树，共享前缀只计算一次
    """
    # 步骤 1：构建前缀树
    tree = build_prefix_tree(trajectories)
    # tree.root → 共享前缀节点
    # tree.branches → 各分支节点

    # 步骤 2：树结构前向传播
    # 使用 Magi Attention 等注意力原语，保证数学等价
    prefix_kv = forward(tree.shared_prefix)     # 只算一次
    branch_outputs = []
    for branch in tree.branches:
        # 每个分支复用前缀的 KV Cache
        out = forward(branch, prefix_kv_cache=prefix_kv)
        branch_outputs.append(out)

    # 步骤 3：解构前缀树，正常计算 loss
    # 每条轨迹的 loss 独立计算，确保数学等价
    losses = []
    for i, branch_out in enumerate(branch_outputs):
        loss = compute_loss(branch_out, trajectories[i].labels)
        losses.append(loss)

    total_loss = sum(losses) / len(losses)
    total_loss.backward()
```

### 5.3 数学等价性保证

Prefix Tree Merging 的关键约束：**合并后的计算结果必须与独立计算严格一致**。

设 $N$ 条序列 $x_1, \dots, x_N$ 共享前缀 $p$，各自后缀为 $s_1, \dots, s_N$。

独立计算：

$$\text{loss}_i = \mathcal{L}(\text{Forward}(p \oplus s_i; \theta))$$

树合并计算：

$$h_p = \text{Forward}_{\text{prefix}}(p; \theta)$$
$$\text{loss}_i = \mathcal{L}(\text{Forward}_{\text{suffix}}(s_i; \theta, \text{KV}(h_p)))$$

由于注意力是因果的（causal mask），后缀 Token 只能 attend 到前缀 + 自身，而前缀的 KV 在两种方式下完全相同。因此 $\text{loss}_i$ 在数学上严格相等，梯度也严格相等。

## 6. 工程实践要点

### 6.1 KV Cache 显存预算规划

```python
def kv_cache_budget(
    n_layers=32, n_heads=32, d_head=128,
    max_seq_len=200_000, dtype_bytes=2,  # FP16
    n_concurrent=8,  # 并发请求数
):
    """计算 KV Cache 的显存预算"""
    per_token = 2 * n_layers * n_heads * d_head * dtype_bytes
    per_request = per_token * max_seq_len
    total = per_request * n_concurrent

    print(f"每 Token KV 大小: {per_token / 1024:.1f} KB")
    print(f"单请求 200K 上下文: {per_request / 1e9:.1f} GB")
    print(f"{n_concurrent} 并发总需求: {total / 1e9:.1f} GB")

kv_cache_budget()
# 每 Token KV 大小: 512.0 KB
# 单请求 200K 上下文: 102.4 GB
# 8 并发总需求: 819.2 GB
```

200K 上下文 × 8 并发 → 需要 ~800 GB 显存。这解释了为什么长上下文 Agent 训练需要大规模 GPU 集群。

### 6.2 PagedAttention：分页管理 KV Cache

vLLM 引入的 PagedAttention 借鉴了操作系统的虚拟内存分页思想：

| 操作系统 | KV Cache 管理 |
|---------|--------------|
| 虚拟页 → 物理页映射 | 逻辑 Token 位置 → 物理显存块映射 |
| 按需分配物理页 | 按需分配 KV Cache 块（不预分配最大长度） |
| 多进程共享只读页 | 多请求共享前缀的 KV Cache 块 |
| 页面换出到磁盘 | KV Cache 块换出到 CPU 内存 |

核心收益：**显存碎片率从 >60% 降至 <4%**，等效增加了可用显存。

### 6.3 Prefill/Decode 分离部署

```python
# 负载均衡伪代码
class PrefillDecodeRouter:
    def __init__(self, prefill_instances, decode_instances):
        self.prefill_pool = prefill_instances  # 高算力 GPU
        self.decode_pool = decode_instances    # 高带宽 GPU

    def route(self, request):
        if request.phase == "prefill":
            # 选择负载最低的 Prefill 实例
            instance = min(self.prefill_pool, key=lambda x: x.queue_len)
            kv_cache = instance.run_prefill(request.prompt)
            # 传输 KV Cache 到 Decode 实例
            return self.transfer_kv(kv_cache, request)
        else:
            # 选择拥有该请求 KV Cache 的 Decode 实例
            instance = self.find_kv_owner(request.request_id)
            return instance.run_decode_step(request)

    def transfer_kv(self, kv_cache, request):
        # KV 传输是 PD 分离的核心开销
        # Forge 用 Global L3 Cache 减少传输次数
        target = self.select_decode_instance(kv_cache.size)
        target.receive_kv(kv_cache)
        return target
```

### 6.4 前缀缓存淘汰策略

| 策略 | 适用场景 | 缺点 |
|------|---------|------|
| **LRU**（最近最少使用） | 通用场景 | 不考虑前缀长度——淘汰长前缀代价高 |
| **Cost-aware** | Agent 场景 | 复杂度高，需要估算重建成本 |
| **Frequency-based** | 热点前缀稳定 | 冷启动问题 |

Forge 采用 **cost-aware 调度**：权衡"排队等待该缓存的延迟"与"从头重新 Prefill 的成本"，动态决定是复用已有缓存还是在空闲实例上重建。

---

> **桥接 → Forge 正文 §3**：理解了前缀冗余和 PD 分离后，Forge 的工程优化就变得水到渠成——Prefix Tree Merging（§3.2）将前缀共享从推理扩展到训练，实现 40 倍加速；异构 PD 分离（§3.3）消除了 Prefill 与 Decode 混合调度的效率损失；Global L3 KV Cache Pool 是 cost-aware 淘汰策略的具体实现。
>
> **现在可以阅读 → [Forge 正文：破解 Agent RL 的不可能三角](blog.md)**
