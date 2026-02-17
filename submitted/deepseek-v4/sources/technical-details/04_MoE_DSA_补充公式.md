# MoE 与 DSA — 补充公式与机制

> 来源：DeepSeek-V3 技术报告、DSA 相关解读

## 1. MoE（混合专家）核心公式

### 1.1 门控路由

$$G(x) = \text{Softmax}(W_g \cdot x + b)$$

Top-k 选择：$\text{TopK}(G(x), k)$，取概率最高的 $k$ 个专家（DeepSeek-V3：$k=8$）。

### 1.2 专家前馈

$$y = \sum_{i \in \text{TopK}} G(x)_i \cdot E_i(x)$$

其中 $E_i$ 为第 $i$ 个专家网络（FFN）。

### 1.3 DeepSeekMoE 配置（V3）

- 1 个共享专家 + 256 个路由专家
- 每 token 激活 8 个专家
- 最多路由至 4 个节点
- 无辅助损耗负载均衡：可学习偏置项动态调整路由

### 1.4 负载均衡偏置

$$\gamma_{\text{前 14.3T}} = 0.001, \quad \gamma_{\text{后 500B}} = 0.0$$

序列级平衡损失，避免专家负载不均。

## 2. DSA（DeepSeek Sparse Attention）

### 2.1 思路

将注意力复杂度从 $O(L^2)$ 降至 $O(L \cdot k)$，$k \ll L$。

### 2.2 两阶段

**Lightning Indexer**：轻量 index score，快速判断哪些 token 可能相关

$$I_i = f_{\text{index}}(q_t, k_i)$$

**Top-k Token Selection**：对每个 query，选取 top-k 的 key-value token，仅在这些 token 上计算注意力

$$\text{Attn}(q_t) = \text{Softmax}\left(\frac{q_t K_{\text{top-k}}^\top}{\sqrt{d}}\right) V_{\text{top-k}}$$

### 2.3 效果

- 输出价格降低 **75%**（V3.2-Exp）
- 几乎不影响输出质量

## 3. 四维稀疏协同

```
输入 Token
    ↓
[门控] → MoE 条件计算（8/671B 专家）
    ↓
[低秩投影] → MLA 压缩 KV Cache
    ↓
[稀疏查表] → Engram 检索静态知识
    ↓
[DSA Top-k] → 细粒度稀疏注意力（可选）
    ↓
输出
```

## 4. 参考文献

- DeepSeek-V3 Technical Report
- 腾讯新闻：DeepSeek 新模型上线实测 — DSA 与 mHC 解析
