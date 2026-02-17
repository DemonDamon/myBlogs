# mHC：流形约束超连接 — 技术细节与数学公式推导

> 来源：arXiv:2512.24880 — mHC: Manifold-Constrained Hyper-Connections  
> DeepSeek-AI，2025年12月

## 1. 背景：残差连接范式

### 1.1 标准残差连接（ResNet）

单层传播公式：

$$\mathbf{x}_{l+1} = \mathbf{x}_{l} + \mathcal{F}(\mathbf{x}_{l}, \mathcal{W}_{l})$$

其中 $\mathbf{x}_{l}$、$\mathbf{x}_{l+1}$ 分别为第 $l$ 层的输入和输出，$\mathcal{F}$ 为残差函数。

递归扩展到多层：

$$\mathbf{x}_{L} = \mathbf{x}_{l} + \sum_{i=l}^{L-1} \mathcal{F}(\mathbf{x}_{i}, \mathcal{W}_{i})$$

**恒等映射（Identity Mapping）**：$\mathbf{x}_{l}$ 项确保浅层信号无损传递到深层，梯度也能无损回传，是深度网络稳定的关键。

### 1.2 超连接（Hyper-Connections, HC）

HC 将残差流宽度从 $C$ 扩展到 $n \times C$，单层传播：

$$\mathbf{x}_{l+1} = \mathcal{H}_{l}^{\mathrm{res}} \mathbf{x}_{l} + \mathcal{H}_{l}^{\mathrm{post}\top} \mathcal{F}(\mathcal{H}_{l}^{\mathrm{pre}} \mathbf{x}_{l}, \mathcal{W}_{l})$$

其中：
- $\mathcal{H}_{l}^{\mathrm{res}} \in \mathbb{R}^{n \times n}$：残差流内特征混合
- $\mathcal{H}_{l}^{\mathrm{pre}} \in \mathbb{R}^{1 \times n}$：将 $nC$ 维流聚合为 $C$ 维层输入
- $\mathcal{H}_{l}^{\mathrm{post}} \in \mathbb{R}^{1 \times n}$：将层输出映射回流

多层递归：

$$\mathbf{x}_{L} = \left(\prod_{i=1}^{L-l} \mathcal{H}_{L-i}^{\mathrm{res}}\right) \mathbf{x}_{l} + \sum_{i=l}^{L-1} \left(\prod_{j=1}^{L-1-i} \mathcal{H}_{L-j}^{\mathrm{res}}\right) \mathcal{H}_{i}^{\mathrm{post}\top} \mathcal{F}(\mathcal{H}_{i}^{\mathrm{pre}} \mathbf{x}_{i}, \mathcal{W}_{i})$$

**HC 的问题**：复合映射 $\prod_{i=1}^{L-l} \mathcal{H}_{L-i}^{\mathrm{res}}$ 无法保持特征均值守恒，导致信号放大或衰减，训练不稳定。实验显示 27B 模型中 Amax Gain Magnitude 峰值可达 **3000**，存在梯度爆炸风险。

## 2. mHC 核心：流形约束

### 2.1 双随机矩阵流形（Birkhoff 多面体）

将 $\mathcal{H}_{l}^{\mathrm{res}}$ 约束到双随机矩阵流形 $\mathcal{M}^{\mathrm{res}}$：

$$\mathcal{P}_{\mathcal{M}^{\mathrm{res}}}(\mathcal{H}_{l}^{\mathrm{res}}) \coloneq \left\{ \mathcal{H}_{l}^{\mathrm{res}} \in \mathbb{R}^{n \times n} \mid \mathcal{H}_{l}^{\mathrm{res}} \mathbf{1}_{n} = \mathbf{1}_{n},\ \mathbf{1}_{n}^{\top} \mathcal{H}_{l}^{\mathrm{res}} = \mathbf{1}_{n}^{\top},\ \mathcal{H}_{l}^{\mathrm{res}} \geq 0 \right\}$$

即：行和、列和均为 1，且非负。

### 2.2 理论性质

1. **范数保持**：$\|\mathcal{H}_{l}^{\mathrm{res}}\|_2 \leq 1$，非扩张映射，抑制梯度爆炸
2. **乘法闭包**：双随机矩阵对乘法封闭，$\prod \mathcal{H}_{L-i}^{\mathrm{res}}$ 仍为双随机
3. **几何解释**：Birkhoff 多面体是置换矩阵的凸包，$\mathcal{H}_{l}^{\mathrm{res}} \mathbf{x}_{l}$ 是输入的凸组合

### 2.3 Sinkhorn-Knopp 投影

给定原始矩阵 $\tilde{\mathcal{H}}_{l}^{\mathrm{res}}$，投影到双随机矩阵：

$$\mathbf{M}^{(0)} = \exp(\tilde{\mathcal{H}}_{l}^{\mathrm{res}})$$

迭代归一化（行列交替）：

$$\mathbf{M}^{(t)} = \mathcal{T}_{r}\left(\mathcal{T}_{c}(\mathbf{M}^{(t-1)})\right)$$

其中 $\mathcal{T}_{r}$、$\mathcal{T}_{c}$ 分别为行、列归一化。当 $t_{\max} \to \infty$ 收敛到双随机矩阵。实践中取 $t_{\max} = 20$。

### 2.4 完整参数化

$$\begin{cases}
\tilde{\mathbf{x}}_{l} = \text{RMSNorm}(\mathbf{x}_{l}) \\
\tilde{\mathcal{H}}_{l}^{\mathrm{pre}} = \alpha_{l}^{\mathrm{pre}} \cdot (\vec{\mathbf{x}}_{l}' \varphi_{l}^{\mathrm{pre}}) + \mathbf{b}_{l}^{\mathrm{pre}} \\
\tilde{\mathcal{H}}_{l}^{\mathrm{post}} = \alpha_{l}^{\mathrm{post}} \cdot (\vec{\mathbf{x}}_{l}' \varphi_{l}^{\mathrm{post}}) + \mathbf{b}_{l}^{\mathrm{post}} \\
\tilde{\mathcal{H}}_{l}^{\mathrm{res}} = \alpha_{l}^{\mathrm{res}} \cdot \text{mat}(\vec{\mathbf{x}}_{l}' \varphi_{l}^{\mathrm{res}}) + \mathbf{b}_{l}^{\mathrm{res}}
\end{cases}$$

最终约束映射：

$$\begin{cases}
\mathcal{H}_{l}^{\mathrm{pre}} = \sigma(\tilde{\mathcal{H}}_{l}^{\mathrm{pre}}) \\
\mathcal{H}_{l}^{\mathrm{post}} = 2\sigma(\tilde{\mathcal{H}}_{l}^{\mathrm{post}}) \\
\mathcal{H}_{l}^{\mathrm{res}} = \text{Sinkhorn-Knopp}(\tilde{\mathcal{H}}_{l}^{\mathrm{res}})
\end{cases}$$

其中 $\sigma$ 为 Sigmoid，对 pre/post 施加非负约束，避免正负系数叠加造成信号抵消。

## 3. 工程优化

- **核融合**：RMSNorm 与矩阵乘重排序，混合精度（TileLang）
- **选择性重计算**：降低显存占用
- **DualPipe 流水线**：重叠通信与计算
- **扩展率**：$n=4$ 时，训练时间开销仅 **6.7%**

## 4. 参考文献

- arXiv:2512.24880 — mHC: Manifold-Constrained Hyper-Connections
- Hyper-Connections (HC) — 字节豆包 Foundation 团队，NeurIPS 2023
