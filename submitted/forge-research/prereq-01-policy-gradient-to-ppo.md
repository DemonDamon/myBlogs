# 前置一：从策略梯度到 PPO——重要性采样裁剪的数学直觉

> **阅读目标**：理解策略梯度 → 基线方差缩减 → 重要性采样 → PPO Clip 的完整推导链，为阅读 Forge 博客中 CISPO 算法（§4）做准备。
>
> **前置要求**：熟悉 PyTorch 基本操作，了解梯度下降和概率论基础。

## 1. REINFORCE：最朴素的策略梯度

### 1.1 核心思想

强化学习的目标是找到一个策略 $\pi_\theta$（由参数 $\theta$ 决定的动作选择规则），使期望累积回报最大：

$$J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=0}^{T} R_t \right]$$

其中 $\tau = (s_0, a_0, r_0, s_1, a_1, r_1, \dots)$ 是一条完整的交互轨迹。

**问题**：$J(\theta)$ 包含对轨迹的期望，轨迹由环境动态和策略共同决定，无法直接对 $\theta$ 求导。

### 1.2 策略梯度定理

通过"对数导数技巧"（log-derivative trick）：$\nabla_\theta \pi_\theta = \pi_\theta \nabla_\theta \log \pi_\theta$，可以推导出：

$$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=0}^{T} \nabla_\theta \log \pi_\theta(a_t | s_t) \cdot R(\tau)\right]$$

**直觉**：这个公式的含义异常简单——如果一条轨迹的总回报 $R(\tau)$ 很高，就**增大**轨迹中每个动作的出现概率；反之则减小。

### 1.3 推导过程

轨迹的概率为：

$$P(\tau | \theta) = \rho(s_0) \prod_{t=0}^{T} \pi_\theta(a_t|s_t) \cdot P(s_{t+1}|s_t, a_t)$$

对 $J(\theta)$ 求梯度：

$$\nabla_\theta J = \nabla_\theta \int P(\tau|\theta) R(\tau) d\tau = \int \nabla_\theta P(\tau|\theta) R(\tau) d\tau$$

利用 $\nabla_\theta P = P \cdot \nabla_\theta \log P$：

$$= \int P(\tau|\theta) \nabla_\theta \log P(\tau|\theta) R(\tau) d\tau = \mathbb{E}_{\tau \sim \pi_\theta}\left[\nabla_\theta \log P(\tau|\theta) \cdot R(\tau)\right]$$

取对数后，环境动态项 $P(s_{t+1}|s_t,a_t)$ 和初始分布 $\rho(s_0)$ 与 $\theta$ 无关，消去后只剩策略项：

$$\nabla_\theta \log P(\tau|\theta) = \sum_{t=0}^{T} \nabla_\theta \log \pi_\theta(a_t|s_t)$$

### 1.4 几何直觉

![策略梯度的几何直觉](images/prereq_01_policy_gradient_landscape.png)
*策略参数空间中的回报地形：梯度箭头指向高回报区域，对比 REINFORCE（高方差）、+Baseline（方差缩减）、PPO Clip（步长受限）三种方法的梯度估计稳定性*
<!-- 🎨 用 vis-prompts/prereq_01_policy_gradient_landscape.txt 生成后替换 -->

### 1.4 最小实现

```python
import torch
import torch.nn as nn
import torch.optim as optim
import gymnasium as gym
import numpy as np

class Policy(nn.Module):
    def __init__(self, obs_dim, act_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 64), nn.ReLU(),
            nn.Linear(64, act_dim),
        )

    def forward(self, x):
        return torch.softmax(self.net(x), dim=-1)

def reinforce(env_name="CartPole-v1", episodes=500, gamma=0.99, lr=1e-2):
    env = gym.make(env_name)
    policy = Policy(env.observation_space.shape[0], env.action_space.n)
    optimizer = optim.Adam(policy.parameters(), lr=lr)

    for ep in range(episodes):
        obs, _ = env.reset()
        log_probs, rewards = [], []

        # --- 采集一条完整轨迹 ---
        done = False
        while not done:
            probs = policy(torch.FloatTensor(obs))
            dist = torch.distributions.Categorical(probs)
            action = dist.sample()
            log_probs.append(dist.log_prob(action))  # log π_θ(a|s)
            obs, reward, term, trunc, _ = env.step(action.item())
            rewards.append(reward)
            done = term or trunc

        # --- 计算折扣回报 R(τ) ---
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + gamma * G
            returns.insert(0, G)
        returns = torch.FloatTensor(returns)

        # --- REINFORCE 更新：∇θ J ≈ Σ log π_θ(a|s) · R(τ) ---
        loss = -torch.stack(log_probs) @ returns  # 负号因为 optimizer 做梯度下降
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
```

**问题**：REINFORCE 的梯度方差极大。想象两条轨迹，回报分别是 100 和 102——两者都是正数，都会增大所有动作的概率，但实际上只有第二条轨迹略优。$R(\tau)$ 的绝对值大小"淹没"了轨迹之间的相对差异。

## 2. 基线与方差缩减

### 2.1 引入基线

将 $R(\tau)$ 替换为 $R(\tau) - b$，其中 $b$ 是一个不依赖于动作的基线（通常取回报均值或价值函数估计）：

$$\nabla_\theta J = \mathbb{E}_{\tau}\left[\sum_t \nabla_\theta \log \pi_\theta(a_t|s_t)(R_t - b)\right]$$

### 2.2 为什么基线不引入偏差

需证明 $\mathbb{E}_\tau[\nabla_\theta \log \pi_\theta(a_t|s_t) \cdot b] = 0$：

$$\mathbb{E}_{a_t \sim \pi_\theta}\left[\nabla_\theta \log \pi_\theta(a_t|s_t) \cdot b\right] = b \sum_{a} \pi_\theta(a|s_t) \frac{\nabla_\theta \pi_\theta(a|s_t)}{\pi_\theta(a|s_t)} = b \nabla_\theta \underbrace{\sum_a \pi_\theta(a|s_t)}_{= 1} = 0$$

基线将回报"居中"——好于平均的动作概率增大，差于平均的减小。回报从 100/102 变成 -1/+1，信号清晰得多。

### 2.3 实践中最常用的基线：状态价值函数

用一个可学习的价值网络 $V_\phi(s)$ 估计 $\mathbb{E}[R_t | s_t]$，则：

$$\hat{A}_t = R_t - V_\phi(s_t)$$

$\hat{A}_t$ 称为**优势函数**（Advantage）：正值意味着该动作好于平均，负值意味着差于平均。

```python
class ValueNet(nn.Module):
    def __init__(self, obs_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 64), nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)

# 在训练循环中加入基线
returns = torch.FloatTensor(returns)
values = value_net(torch.FloatTensor(observations))
advantages = returns - values.detach()  # detach: 基线不参与策略梯度

policy_loss = -(torch.stack(log_probs) * advantages).mean()
value_loss = nn.functional.mse_loss(values, returns)  # 训练价值网络逼近真实回报
```

## 3. 重要性采样：用旧数据更新新策略

### 3.1 问题：数据效率

REINFORCE 是 **on-policy** 算法——每次更新策略后，之前采集的数据就"过期"了，因为它们来自旧策略 $\pi_{\theta_\text{old}}$，而非当前策略 $\pi_\theta$。

这在 Agent 场景中尤其致命：一次 rollout 可能耗时数分钟甚至数小时，用完即弃代价极高。

### 3.2 重要性采样恒等式

期望可以在不同分布间转换：

$$\mathbb{E}_{x \sim p}[f(x)] = \mathbb{E}_{x \sim q}\left[\frac{p(x)}{q(x)} f(x)\right]$$

应用到策略梯度：用旧策略 $\pi_{\theta_\text{old}}$ 的数据来估计新策略 $\pi_\theta$ 的梯度，只需乘上**似然比**（importance ratio）：

$$r_t(\theta) = \frac{\pi_\theta(a_t | s_t)}{\pi_{\theta_\text{old}}(a_t | s_t)}$$

离策略目标函数变为：

$$J^{\text{IS}}(\theta) = \mathbb{E}_{a_t \sim \pi_{\theta_\text{old}}}\left[r_t(\theta) \cdot \hat{A}_t\right]$$

### 3.3 重要性权重爆炸

当新旧策略差异较大时，$r_t(\theta)$ 可能变得极大或极小，导致梯度估计的方差飙升：

```python
# 演示：策略微小变化导致重要性权重爆炸
old_prob = 0.01   # 旧策略下某动作概率 1%
new_prob = 0.10   # 新策略下该动作概率 10%
ratio = new_prob / old_prob  # = 10.0 —— 权重放大 10 倍

# 在长序列中，每步的 ratio 相乘：
seq_len = 20
cumulative_ratio = ratio ** seq_len  # = 10^20 ≈ 无穷大
```

这就是为什么需要对 $r_t(\theta)$ 做裁剪。

## 4. PPO Clip：信任域的工程化近似

### 4.1 核心公式

PPO（Proximal Policy Optimization）的裁剪目标函数：

$$L^{\text{CLIP}}(\theta) = \mathbb{E}_t\left[\min\left(r_t(\theta) \hat{A}_t, \;\text{clip}(r_t(\theta),\; 1-\epsilon,\; 1+\epsilon) \hat{A}_t\right)\right]$$

其中 $\epsilon$ 通常取 0.2。

### 4.2 分段行为分析

**当 $\hat{A}_t > 0$**（好动作，希望增大概率）：

$$L = \min\left(r_t \hat{A}_t, \;\min(r_t, 1+\epsilon) \hat{A}_t\right) = \min(r_t, 1+\epsilon) \cdot \hat{A}_t$$

$r_t$ 增大到 $1+\epsilon$ 后被截断——即使新策略认为这个动作好得多，也不允许概率增加超过 $\epsilon$ 幅度。

**当 $\hat{A}_t < 0$**（坏动作，希望减小概率）：

$$L = \min\left(r_t \hat{A}_t, \;\max(r_t, 1-\epsilon) \hat{A}_t\right) = \max(r_t, 1-\epsilon) \cdot \hat{A}_t$$

$r_t$ 减小到 $1-\epsilon$ 后被截断——不允许概率减少超过 $\epsilon$ 幅度。

这实现了一个**对称信任域**：新策略与旧策略的偏离不超过 $\epsilon$。

### 4.3 PPO 核心 Loss 实现

```python
def ppo_clip_loss(
    log_probs_new,     # 新策略下各动作的 log 概率, shape [B, T]
    log_probs_old,     # 旧策略下各动作的 log 概率, shape [B, T]（detached）
    advantages,        # 优势估计, shape [B, T]
    epsilon=0.2,       # 裁剪范围
):
    # 计算重要性权重 r_t(θ) = π_θ(a|s) / π_θ_old(a|s)
    ratio = torch.exp(log_probs_new - log_probs_old)

    # 未裁剪目标：r_t * A_t
    surr1 = ratio * advantages

    # 裁剪目标：clip(r_t, 1-ε, 1+ε) * A_t
    surr2 = torch.clamp(ratio, 1.0 - epsilon, 1.0 + epsilon) * advantages

    # 取两者的较小值——悲观估计，防止过度更新
    loss = -torch.min(surr1, surr2).mean()
    return loss
```

### 4.4 完整 PPO 训练循环

```python
def ppo_update(policy, value_net, buffer, epochs=4, batch_size=64, epsilon=0.2):
    """一次 PPO 更新：用同一批旧数据做多轮 mini-batch 更新"""
    obs, actions, old_log_probs, returns, advantages = buffer.get()

    # 归一化优势——实践中至关重要，稳定训练
    advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

    for _ in range(epochs):  # 同一批数据复用多轮
        for idx in range(0, len(obs), batch_size):
            batch = slice(idx, idx + batch_size)
            # 用当前策略重新计算 log_prob
            probs = policy(obs[batch])
            dist = torch.distributions.Categorical(probs)
            new_log_probs = dist.log_prob(actions[batch])

            # PPO clip loss
            ratio = torch.exp(new_log_probs - old_log_probs[batch])
            surr1 = ratio * advantages[batch]
            surr2 = torch.clamp(ratio, 1 - epsilon, 1 + epsilon) * advantages[batch]
            policy_loss = -torch.min(surr1, surr2).mean()

            # 价值函数 loss
            value_loss = nn.functional.mse_loss(
                value_net(obs[batch]), returns[batch]
            )

            # 熵奖励——鼓励探索
            entropy = dist.entropy().mean()

            loss = policy_loss + 0.5 * value_loss - 0.01 * entropy
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(policy.parameters(), 0.5)  # 梯度裁剪
            optimizer.step()
```

## 5. 从 PPO 到 CISPO：非对称裁剪

### 5.1 PPO 裁剪的局限

PPO 使用**对称**裁剪区间 $[1-\epsilon, 1+\epsilon]$，这在短时序、密集奖励的游戏场景中效果出色。但在 Agent 场景中：

| 特征 | 游戏场景 | Agent 场景 |
|------|---------|-----------|
| 轨迹长度 | 数百步 | 数千~数万步 |
| 奖励密度 | 每步有奖励 | 大多为 0，仅末尾有信号 |
| 动作空间 | 固定、小（跳/不跳） | 可变、大（Token 生成） |
| 好动作占比 | 相对均衡 | 极其稀疏 |

对称裁剪的下界 $1-\epsilon$ 在 Agent 场景中**过于保守**：它限制了降低"坏动作"概率的幅度，而 Agent 场景中需要快速远离大量无效动作。

### 5.2 CISPO 的非对称设计

![PPO 对称裁剪 vs CISPO 非对称裁剪](images/prereq_01_ppo_clip_function.png)
*左图 PPO：对称区间 [1-ε, 1+ε] 双向限制更新幅度；右图 CISPO：非对称区间 [0, 1+ε_high]，允许完全抑制坏动作，只限制好动作增幅*
<!-- 🎨 用 vis-prompts/prereq_01_ppo_clip_function.txt 生成后替换 -->

CISPO 的裁剪函数：

$$\hat{r}_{i,t}(\theta) = \text{clip}(r_{i,t}(\theta), \;0, \;1 + \epsilon_{\text{high}}^{IS})$$

对比：

| | 下界 | 上界 | 效果 |
|--|------|------|------|
| PPO | $1-\epsilon$ | $1+\epsilon$ | 双向限制幅度 |
| CISPO | $0$ | $1+\epsilon_{\text{high}}^{IS}$ | 允许完全抑制坏动作，只限制好动作增幅 |

**下界为 0 的含义**：如果新策略认为某个 Token 概率应该极低（$r_t \to 0$），CISPO 不阻拦——在稀疏奖励下，快速远离错误路径比保守更新更重要。

**上界限制好动作**：防止模型因偶然获得高奖励就过度"押注"某一条轨迹。

### 5.3 Reward-to-go vs 全局回报

PPO 常用 GAE（Generalized Advantage Estimation）。CISPO 采用更直接的 **Reward-to-go** 形式：

$$\hat{A}_{i,t} = \sum_{p=t}^{T}(r_p^{\text{speed}} + r_p^{\text{perf}}) - B_i$$

从时步 $t$ 向后累积到轨迹末尾，再减去轨迹基线 $B_i$。这比全局回报（从时步 0 累积）信号更精确：时步 $t$ 的动作只对未来负责，不受过去的"牵连"。

```python
def compute_reward_to_go(rewards, baseline):
    """Reward-to-go: 每个时步的未来累积奖励减基线"""
    T = len(rewards)
    rtg = torch.zeros(T)
    running = 0.0
    for t in reversed(range(T)):
        running += rewards[t]
        rtg[t] = running
    return rtg - baseline  # baseline 通常为同 batch 内轨迹回报的均值

def cispo_clip(ratio, epsilon_high=0.2):
    """CISPO 非对称裁剪：下界 0，上界 1+ε"""
    return torch.clamp(ratio, 0.0, 1.0 + epsilon_high)
```

## 6. 工程实践要点

### 6.1 超参数敏感性

| 超参数 | 典型范围 | 过大的后果 | 过小的后果 |
|--------|---------|-----------|-----------|
| $\epsilon$（裁剪范围） | 0.1 ~ 0.3 | 更新过大，策略震荡 | 更新过保守，收敛慢 |
| mini-batch epochs | 3 ~ 10 | 过拟合旧数据 | 数据利用不充分 |
| 学习率 | 1e-4 ~ 3e-4 | 训练不稳定 | 收敛极慢 |
| 梯度裁剪阈值 | 0.5 ~ 1.0 | 梯度仍可能爆炸 | 截断过多有效信号 |

### 6.2 GAE 在实践中更稳定

纯 Reward-to-go 在长时序任务中仍然方差较高。GAE（$\lambda$-return）通过指数加权混合不同步长的 TD 误差来平衡偏差与方差：

$$\hat{A}_t^{\text{GAE}} = \sum_{l=0}^{T-t}(\gamma\lambda)^l \delta_{t+l}, \quad \delta_t = r_t + \gamma V(s_{t+1}) - V(s_t)$$

$\lambda = 0$ 退化为 TD(0)（低方差高偏差），$\lambda = 1$ 退化为 Reward-to-go（高方差低偏差）。实践中 $\lambda = 0.95$ 效果最佳。

### 6.3 常见陷阱

- **优势不归一化**：不同 batch 的优势量级可能差异巨大，必须做标准化
- **忘记 detach 旧策略**：`old_log_probs` 必须在采集时 `.detach()` 保存，否则计算图会指数膨胀
- **熵奖励系数过大**：策略退化为均匀随机
- **学习率没有 warmup**：初期梯度方向不稳定，大学习率直接带飞

---

> **桥接 → Forge 正文 §4**：理解了 PPO 的对称裁剪 $[1-\epsilon, 1+\epsilon]$ 后，Forge 的 CISPO 算法就是将其改为非对称裁剪 $[0, 1+\epsilon_{\text{high}}^{IS}]$，配合 Reward-to-go（含速度奖励和性能奖励）替代 GAE，再加上 stop-gradient 算子和 Token 级归一化——每一项在本文中都已有对应的基础概念。接下来可直接阅读 [Forge 正文](blog.md) 的第 4 节。
>
> **下一篇 → [前置二：Agent RL 建模](prereq-02-agent-rl-modeling.md)**：PPO/CISPO 解决的是"怎么优化策略"，但 Agent 场景中"状态/动作/奖励"长什么样？脚手架和上下文管理又如何影响 MDP 建模？
