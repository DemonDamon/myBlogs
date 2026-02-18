# MiniMax Forge：破解 Agent RL 的不可能三角

> MiniMax 于 2026 年 2 月 13 日发布了 Forge——一套面向大规模 Agent 强化学习的异步训练框架。本文深入解析其系统架构、调度策略、训练加速方案与 CISPO 算法的数学原理。

### 前置阅读

本文涉及策略梯度算法、Agent MDP 建模和 LLM 推理优化三方面的基础知识。建议按顺序阅读以下三篇前置模块后再进入正文：

1. **[从策略梯度到 PPO](prereq-01-policy-gradient-to-ppo.md)** — REINFORCE → 基线方差缩减 → 重要性采样 → PPO Clip → CISPO 非对称裁剪（对应正文 §4）
2. **[Agent RL 建模](prereq-02-agent-rl-modeling.md)** — MDP 映射 → Agent Rollout 循环 → 脚手架 → 白盒/黑盒 → 上下文管理即动作（对应正文 §2）
3. **[LLM 推理的计算瓶颈](prereq-03-llm-inference-bottleneck.md)** — KV Cache → Prefill/Decode 分离 → 前缀冗余 → Prefix Tree（对应正文 §3）

---

## 1. 问题定义：三重困境

大规模 Agent RL 面临一个结构性三难困境（trilemma）：**系统吞吐量**、**训练稳定性**与 **Agent 灵活性**三者相互制约。Forge 将优化目标形式化为最大化 **Effective Agent Training Yield**：

![优化目标公式](images/f8204646c615656692c0bfd75bde784d.jpg)

即：

$$\max_{\theta} J(\theta) = \text{Throughput}(\mathcal{A}) \times \text{Sample Efficiency}(\mathcal{A})$$

约束条件包含三项：

| 约束 | 含义 | 代理指标 |
|------|------|----------|
| $\forall \mathcal{A} \in \Omega_{\text{agent}}$ | 对任意 Agent 架构均成立 | Agent 灵活性 |
| $\mathbb{E}[\text{Update Variance}] < \delta$ | 梯度更新方差有界 | 训练稳定性 |
| $\mathbb{E}[\|J^{(T)} - J^*\|] < \epsilon$ | 收敛至最优值邻域 | 收敛保证 |

其中 **Throughput** 受 rollout、training、数据处理和 I/O 四个环节瓶颈限制；**Sample Efficiency** 由数据分布、数据质量、算法效率和 off-policy 程度共同决定。最大化 $J$ 面临三类结构性挑战：

**挑战一：Agent 灵活性的"玻璃天花板"。** 传统框架将 Agent 视为白盒函数，Agent 与训练器共享状态，无法建模动态上下文管理（CM）和多 Agent 协作等复杂认知架构。TITO（Token-In-Token-Out）架构强制 Agent 与底层 Token 逻辑深度耦合，在复杂 CM 下维持推理抽象与训练表示的一致性代价过高。

**挑战二：系统效率与计算冗余。** Agent rollout 耗时从秒级（简单 API 调用）到小时级（复杂推理链）不等。严格 FIFO 调度受"拖尾效应"（Straggler Effect）影响——单个高延迟任务阻塞整个集群（HoL Blocking）；贪心调度虽然吞吐高，但造成严重的数据分布偏移（先处理大量"简单"样本，后期聚集"困难"样本），导致梯度震荡。

**挑战三：信用分配与优化稳定性。** Agent 任务通常是超长时序（200K 上下文），奖励稀疏，在数千个动作中精确归因困难，信噪比低、梯度方差大。传统 RL 目标仅关注正确性，忽略 wall-clock 执行成本，导致 Agent "功能正确但实际缓慢"。

## 2. 系统架构：三层解耦

Forge 采用三层模块化架构，将 Agent 逻辑与训推引擎彻底解耦：

![Forge 三层系统架构](images/88d02f39b2d7d5db1d28da7b972d7e41.jpg)

**Agent 层（顶层）**：抽象白盒与黑盒两类 Agent 及其运行环境。Agent 作为纯轨迹生产者，专注于核心业务逻辑（上下文管理、推理链），对底层训推机制无感知。

**中间件层（桥梁）**：物理隔离 Agent 层与引擎层，包含两个核心组件：
- **Gateway Server**：标准化通信网关，处理 Agent 与 LLM 之间的 completion 请求，屏蔽底层模型复杂性
- **Data Pool**：分布式数据存储，异步收集 rollout 轨迹与奖励信号（含 outcome 和 process 两类），作为生成与训练之间的缓冲区

**引擎层（底层）**：
- **Rollout Engine**：高吞吐 Token 生成，响应中间件转发的请求
- **Train Engine**：消费 Data Pool 中的 Token 序列更新策略，与 Rollout Engine 同步权重（`sync weights`），确保探索使用最新策略分布

这一架构实现了引擎与 Agent 的完全解耦。在 M2.5 的构建过程中，Forge 集成了数百种脚手架类型和数千种工具调用格式，日处理百万级样本。

### 2.1 白盒 Agent RL：上下文管理即动作

长时序任务中存在"上下文腐化"（Context Rot）问题：随交互轮次增加，中间推理步骤和冗余观测累积，产生"注意力稀释"效应，模型在绝对上下文窗口内也会丢失关键信息。

更棘手的是推理-训练分布失配：若仅在推理时使用上下文管理，会引入严重的分布偏移，模型被迫在线适应未见过的上下文结构。

Forge 的解法是**将 CM 建模为显式 Agent 动作**，嵌入 RL 交互循环：
- 状态转移 $S_t \to S_{t+1}$ 隐式包含上下文切换逻辑，CM 直接折叠进训练目标
- 策略 $\pi$ 在此框架下优化，学会内化分布偏移，涌现出优先关注"状态关键"Token 的推理模式
- 模型在 RL 生成过程中主动预判 CM 操作，保留任务关键信息、剪除无关噪声

### 2.2 黑盒 Agent RL：跨架构泛化

实际部署中大量用户使用私有或复杂 Agent 架构（"黑盒"）。Forge 对 Agent 内部实现完全无感：Agent 只需将请求路由至 Gateway，框架自动完成数据收集和训练。这意味着 Forge 原生支持任意上下文操作（记忆压缩、历史重写）和复杂 Agent Loop（Deep Think、Multi-Agent）。

实验验证了这一泛化能力——从依赖 Sandbox/MCP 的代码 Agent（如 OpenCode Agent 完全黑盒训练），到使用激进上下文截断策略的 Agent（如 Truncate BC），黑盒系统上均获得稳定提升：

![Black Box Agent RL 训练曲线](images/1463665922be4c42d41908a45d33172c.jpg)

上图展示黑盒 Agent 在约 55 小时训练中 Reward 从 ~0.51 持续上升至 ~0.64，波动幅度可控，验证了 Forge 在完全不透明系统上的稳定优化能力。

## 3. 工程优化

### 3.1 Windowed FIFO 调度

为调和吞吐量与分布一致性的矛盾，Forge 提出 **Windowed FIFO**——介于严格同步与贪心异步之间的折中策略。

![Windowed FIFO 调度示意](images/01a8283b67cf351e193c25d3d59a80af.jpg)

核心机制：设生成队列为 $Q = [T_0, T_1, \dots, T_{N-1}]$，当前队头索引为 $i$，训练调度器的可见窗口大小为 $W$（例如 $W = 0.3N$）。

| 规则 | 行为 |
|------|------|
| **窗口内贪心** | 在 $[T_i, T_{i+W-1}]$ 范围内，调度器可立即获取任何已完成轨迹，缓解 HoL 阻塞 |
| **窗口外严格阻塞** | 即使窗口外的任务 $T_j$（$j > i+W$）已完成，也禁止提取 |
| **窗口滑动** | 仅当队头任务被消费后，窗口才前移 $i \to i+1$ |

如上图示例：Generation Batch = 8，Window Size = 4。初始状态所有数据来自模型版本 0。当任务 0~10 中除 7 外均完成训练后，窗口锚定在最老的活跃条目 7，剩余窗口容量为 1，最大乱序容忍度为 3（= 4-1），最大 Off-Policy 滞后为 10（= 8+3-1）。

这一设计强制调度器等待窗口内的"拖尾者"（复杂长时序任务），防止训练分布漂移至"快速简单"样本。

### 3.2 Prefix Tree Merging：40 倍训练加速

多轮 Agent 训练中，样本存在大量结构性重叠：多个 completion 共享相同的历史前缀，在不同 CM 策略下（丢弃中间结果、自总结）也存在大量公共前缀。传统方法将每个样本独立处理，重复计算这些前缀，造成巨大的 TFLOPS 浪费。

![Prefix Tree Merging 原理](images/05c7e3f65d4a4b0a892bcdf64623fe9e.jpg)

Forge 的方案是**将线性处理转化为树结构处理**：

上图展示了核心思路。上半部分是传统方式：三个 completion 各自包含相同的 `long common context`，分别拼接 `seq 1`、`seq 2`、`seq 2 + seq 3`，前缀被重复计算三次。下半部分经 Prefix Tree Merge 后，公共前缀只计算一次，`seq 1`、`seq 2`、`seq 3` 作为分支共享前缀计算结果。

实现要点：
- 利用注意力原语（如 Magi Attention）保证树结构前向传播与标准前向传播在逻辑上严格一致
- 前向传播后依据元数据解构前缀树，正常计算 loss
- **严格数学等价**：对 loss 计算和指标零影响

效果：**训练加速约 40 倍**，显著降低显存开销，支持更长序列和更大 batch size。

### 3.3 推理加速三板斧

**MTP 投机解码**：使用 Multi-Token Prediction 头（通过 Top-K KL loss 持续微调）替代静态草稿模型，保证与不断演进的 RL 策略对齐，维持高接受率。

**异构 PD 分离**：解耦 Prefill 和 Decode 阶段，消除 MoE 混合调度中的 PD 干扰，各阶段独立并行策略，同时最大化全局吞吐和优化长时序任务的尾延迟。

**Global L3 KV Cache Pool**：DFS 后端的全局 L3 缓存，配合 cost-aware 调度器，权衡排队延迟与缓存迁移成本，最大化前缀缓存命中率，避免多轮 Agent RL 中的冗余 prefill。

## 4. CISPO 算法与复合奖励

### 4.1 CISPO 算法详解

Forge 的核心算法为 **CISPO**（Constrained Importance Sampling with Policy Optimization），其目标函数为：

![CISPO 目标函数](images/600325ff0e795616142335b3c7614b33.jpg)

$$\mathcal{J}_{\text{CISPO}}(\theta) = \mathbb{E}_{(q,a)\sim\mathcal{D},\{o_i\}_{i=1}^G\sim\pi_{\theta_{\text{old}}}(\cdot|q)} \left[ \frac{1}{\sum_{i=1}^G |o_i|} \sum_{i=1}^G \sum_{t=1}^{|o_i|} \text{sg}(\hat{r}_{i,t}(\theta)) \hat{A}_{i,t} \log \pi_\theta(o_{i,t} \mid q, o_{i,<t}) \right]$$

其中关键量的定义：

![CISPO 辅助定义](images/8ec8f677330427be1476a9af939aa9b1.jpg)

$$\hat{r}_{i,t}(\theta) = \text{clip}\left(r_{i,t}(\theta),\; 0,\; 1 + \epsilon_{\text{high}}^{IS}\right)$$

$$\hat{A}_{i,t} = \sum_{p=t}^{T} (r_p^{\text{speed}} + r_p^{\text{perf}}) - B_i$$

逐项解读：

**目标函数结构**：外层期望对训练数据分布 $\mathcal{D}$ 中的查询-动作对 $(q,a)$ 和旧策略 $\pi_{\theta_{\text{old}}}$ 生成的 $G$ 条轨迹 $\{o_i\}$ 采样。内层是按 Token 归一化的加权策略梯度——每个 Token $o_{i,t}$ 的贡献由截断重要性权重 $\hat{r}_{i,t}$ 和优势估计 $\hat{A}_{i,t}$ 共同调制。$\text{sg}(\cdot)$ 为 stop-gradient 算子，确保重要性权重不参与梯度回传。

**截断重要性采样权重** $\hat{r}_{i,t}(\theta)$：对新旧策略的似然比 $r_{i,t}(\theta) = \pi_\theta(o_{i,t}|q,o_{i,<t}) / \pi_{\theta_{\text{old}}}(o_{i,t}|q,o_{i,<t})$ 进行单侧截断——下界为 0（忽略极低概率 Token），上界为 $1+\epsilon_{\text{high}}^{IS}$（抑制极高权重的过度更新）。与 PPO 的双侧对称裁剪（$1\pm\epsilon$）不同，CISPO 采用非对称裁剪：保留所有降低概率的方向（下界 0 而非 $1-\epsilon$），只限制增加概率的上界。这更适合 Agent 场景中稀疏奖励下的探索需求。

**优势估计** $\hat{A}_{i,t}$：采用 **Reward-to-go** 形式，从当前时步 $t$ 到轨迹末尾 $T$ 的未来累积奖励减去基线 $B_i$。奖励信号由两部分构成：
- $r_p^{\text{speed}}$：**时效奖励**——基于相对完成时间的效率信号，激励 Agent 利用并行化加速执行
- $r_p^{\text{perf}}$：**性能奖励**——任务正确性和质量信号

$B_i$ 为轨迹级基线（用于方差缩减），Reward-to-go 形式相比全局稀疏奖励显著降低了长时序任务中的梯度方差，提升信用分配精度。

**统一混域训练**：与多阶段 RL（先训推理、再训 Agent）不同，CISPO 采用统一策略同时混合 **Reasoning**、**General QA** 和 **Agent** 三个领域的任务。这避免了多阶段训练中的负迁移和领域间干扰，显著提升模型跨任务泛化能力。

### 4.2 复合奖励框架

针对 200K 超长上下文中的信用分配难题，Forge 设计了三层奖励体系：

| 奖励类型 | 作用 | 示例 |
|----------|------|------|
| **过程奖励** (Process Reward) | 对中间行为提供密集反馈 | 惩罚语言混用、特定工具调用错误 |
| **任务完成时间奖励** (Speed Reward) | 激励并行化和高效工具使用 | 基于相对完成时间的效率信号 |
| **Reward-to-go** | 缩减梯度方差，精确归因 | 从 $t$ 到 $T$ 的未来累积回报 |

过程奖励将反馈从"结局揭晓"前置到每个中间步骤，将稀疏信号转化为密集信号；时间奖励引入 wall-clock 成本维度，使 Agent 不仅"做对"还"做快"；Reward-to-go 配合基线 $B_i$ 实现方差缩减，三者协同解决了超长时序任务中信号微弱、归因模糊的核心难题。

## 5. 生产验证

在 M2.5 的训练中，Forge 系统处理了超过十万种真实 Agent 脚手架和环境，上下文长度达 200K，日处理百万级样本，实现持续 Reward 收敛和模型能力的真实提升。结合 CISPO 算法与复合奖励框架，M2.5 在多项基准上达到旗舰水平：

| Benchmark | M2.5 | Claude Opus 4.6 |
|-----------|------|-----------------|
| SWE-Bench Verified | 80.2% | 80.6% |
| Multi-SWE-Bench | **51.3%**（行业第一） | - |
| BrowseComp | 76.3% | - |

M2.5 采用 229B 总参数的 MoE 架构，推理时仅激活 10B（稀疏度 > 95%），在 100 TPS 的输出速度下，连续运行成本约 $1/小时。极端稀疏性 + 大规模 Agent RL 训练的组合，使其在 10B 激活参数下逼近旗舰级性能。

## 6. 总结

Forge 通过一套系统性方案破解了 Agent RL 的不可能三角：

- **灵活性**：三层解耦架构 + 标准化协议，支持任意白盒/黑盒 Agent 无侵入接入
- **吞吐量**：Windowed FIFO 调度 + Prefix Tree Merging（40 倍加速）+ 推理三板斧（MTP 投机解码、PD 分离、L3 KV Cache）
- **稳定性**：CISPO 算法的非对称截断重要性采样 + 复合奖励（过程奖励 + 时效奖励 + Reward-to-go）解决稀疏信号下的信用分配和梯度方差问题

三者不再相互牺牲，而是在统一框架内协同优化——这正是 Forge 将 $J(\theta) = \text{Throughput} \times \text{Sample Efficiency}$ 从形式化定义推进到工程落地的关键。