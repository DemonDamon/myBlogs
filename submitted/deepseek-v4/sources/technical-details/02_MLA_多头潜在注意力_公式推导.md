# MLA：多头潜在注意力 — 技术细节与数学公式推导

> 来源：DeepSeek-V2/V3 Technical Report、知乎/CSDN 技术解读

## 1. 问题：KV Cache 瓶颈

传统 Transformer 自回归推理时，KV Cache 随序列长度线性增长：

- **MHA**：每 token 存储 $n_h \times (d_k + d_v)$ 维 KV
- **GQA/MQA**：减少 head 数，但带来性能损失
- **MLA**：通过低秩压缩 KV 维度，**既减小 Cache 又提升性能**

DeepSeek-V2 数据：KV cache 降低 **93.3%**，训练成本节省 **42.5%**，生成吞吐提升 **5.76×**。

## 2. 核心思想：KV 低秩联合压缩

### 2.1 符号定义

| 符号 | 含义 |
|------|------|
| $d$ | 隐藏维度（如 5120） |
| $n_h$ | 注意力头数 |
| $d_h$ | 每头原始维度（Q/K/V） |
| $d_c$ | KV 联合压缩后维度，$d_c \ll d_h n_h$ |
| $d_c'$ | Query 压缩后维度 |
| $d_r$ | 解耦 Key 头维度（RoPE 部分） |

### 2.2 压缩流程

**Step 1：KV 联合压缩**

$$c_t^{KV} = W_{DKV} \cdot h_t$$

其中 $W_{DKV} \in \mathbb{R}^{d_c \times d}$ 为压缩矩阵，$h_t$ 为第 $t$ 个 token 的隐藏状态。**仅缓存 $c_t^{KV}$**，维度远小于原始 K、V。

**Step 2：解压缩 K、V**

$$K_t = W_{UK} \cdot c_t^{KV}, \quad V_t = W_{UV} \cdot c_t^{KV}$$

$W_{UK}$、$W_{UV}$ 为解压缩矩阵，将 $c_t^{KV}$ 还原为多头 K、V。

**Step 3：Query 压缩与解耦 RoPE**

为解决 RoPE 与低秩 KV 的兼容问题，MLA 采用**解耦 RoPE**：
- Query 也经压缩 $W_{DQ}$、解压 $W_{UQ}$
- 位置编码仅作用于 Query 的独立维度 $d_r$，与压缩部分分离

$$q = W_{UQ}(W_{DQ} \cdot h_t), \quad q = [q_{nope}, q_{pe}]$$

其中 $q_{pe}$ 携带 RoPE，$q_{nope}$ 为无位置部分。

### 2.3 注意力计算等价形式

传统注意力：

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^\top}{\sqrt{d_k}}\right) V$$

MLA 通过数学等价变换，将 $K$、$V$ 用 $C^{KV}$ 表示，实现：
- 所有 head 共享同一个 $C$ Cache（类似 MQA）
- 计算时按需从 $C$ 解压出 K、V
- 矩阵乘重排序优化解码阶段计算量

## 3. DeepSeek-V3 配置

| 参数 | 值 |
|------|-----|
| KV 压缩维度 $d_c$ | 512 |
| Query 压缩维度 $d_c'$ | 1536 |
| 解耦 Key 头维度 $d_r$ | 64 |

## 4. 与 MHA/GQA/MQA 对比

| 方法 | KV Cache 大小 | 性能 |
|------|---------------|------|
| MHA | 100% | 基线 |
| GQA | ~25% | 有损失 |
| MQA | ~6% | 有损失 |
| MLA | ~14%（Small MoE）/ ~4%（Large MoE） | **优于 MHA** |

## 5. 关联工作：MTLA（时序潜在注意力）

arXiv:2505.13544 提出 **Multi-head Temporal Latent Attention**，在 MLA 基础上沿**时间维度**进一步压缩 KV Cache：
- 超网络动态合并相邻时间步的 KV 向量
- Stride-aware causal mask 保证训练与推理一致
- 英德语音翻译任务：**5.3× 加速**，GPU 显存降低 **8.3×**

## 6. 参考文献

- DeepSeek-V2/V3 Technical Report
- arXiv:2505.13544 — Multi-head Temporal Latent Attention
- 知乎：手撕 DeepSeek-MLA、DeepSeek-v2 MLA 低秩分解
