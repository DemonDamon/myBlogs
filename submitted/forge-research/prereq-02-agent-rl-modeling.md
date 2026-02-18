# 前置二：Agent RL 建模——LLM 如何变成会用工具的 Agent

> **阅读目标**：理解 Agent 场景下的 MDP 映射、rollout 循环、脚手架概念和上下文管理，为阅读 Forge 博客的系统架构（§2）做准备。
>
> **前置要求**：已阅读 [前置一：从策略梯度到 PPO](prereq-01-policy-gradient-to-ppo.md)。

## 1. 经典 MDP 回顾

### 1.1 五元组定义

马尔可夫决策过程（MDP）由五元组 $(S, A, P, R, \gamma)$ 定义：

| 符号 | 含义 | 举例（迷宫） |
|------|------|------------|
| $S$ | 状态空间 | 所有格子位置 |
| $A$ | 动作空间 | {上, 下, 左, 右} |
| $P(s'|s,a)$ | 状态转移概率 | 往右走 → 80% 到右格, 10% 不动, 10% 滑到上格 |
| $R(s,a)$ | 奖励函数 | 到达终点 +1, 掉坑 -1, 其他 0 |
| $\gamma$ | 折扣因子 | 0.99（远期奖励略打折） |

**马尔可夫性**：$P(s_{t+1}|s_t, a_t)$ 只依赖当前状态，不依赖历史——"未来只取决于现在"。

### 1.2 贝尔曼方程

状态价值函数 $V^\pi(s)$ 满足递归关系：

$$V^\pi(s) = \mathbb{E}_{a \sim \pi}\left[R(s, a) + \gamma \sum_{s'} P(s'|s,a) V^\pi(s')\right]$$

直觉：当前状态的价值 = 立即奖励 + 折扣后的未来价值期望。

### 1.3 最小实现：值迭代

```python
import numpy as np

# 三状态 MDP：S0 --(a0)--> S1 --(a0)--> S2(终态, 奖励+1)
#                --(a1)--> S0(原地, 奖励0)
states = ["S0", "S1", "S2"]
gamma = 0.9

# 转移表：transitions[s][a] = [(prob, next_state, reward)]
transitions = {
    "S0": {"go": [(1.0, "S1", 0.0)], "stay": [(1.0, "S0", 0.0)]},
    "S1": {"go": [(1.0, "S2", 1.0)], "stay": [(1.0, "S0", 0.0)]},
    "S2": {"go": [(1.0, "S2", 0.0)], "stay": [(1.0, "S2", 0.0)]},  # 终态
}

# 值迭代：反复更新 V(s) = max_a Σ p(s'|s,a)[r + γV(s')]
V = {s: 0.0 for s in states}
for _ in range(100):
    for s in states:
        if s == "S2":
            continue  # 终态价值为 0
        V[s] = max(
            sum(p * (r + gamma * V[s_]) for p, s_, r in transitions[s][a])
            for a in transitions[s]
        )
# V = {'S0': 0.81, 'S1': 0.9, 'S2': 0.0}
# 解读：S0 价值 0.81 = γ² × 1.0，即两步到达终态的折扣奖励
```

## 2. Agent 场景的 MDP 映射

传统 RL（如 Atari 游戏）的状态是像素、动作是按键。当 LLM 变成 Agent，MDP 的每个元素都发生了根本性变化：

![经典 MDP 到 Agent RL 的映射对照](images/prereq_02_agent_mdp_mapping.png)
*左：经典 RL（Atari）的固定像素状态、离散按键动作、密集奖励；右：Agent RL（LLM）的变长 Token 状态、序列生成动作、稀疏奖励——五元组的每个元素都发生了质变*
<!-- 🎨 用 vis-prompts/prereq_02_agent_mdp_mapping.txt 生成后替换 -->

### 2.1 映射对照

| MDP 元素 | 传统 RL（Atari） | Agent RL（LLM） |
|----------|----------------|----------------|
| **状态 $S_t$** | 游戏画面（固定尺寸像素矩阵） | 当前上下文窗口（变长 Token 序列，可达 200K） |
| **动作 $A_t$** | 离散按键（~18 种） | 一段 Token 生成（可能是文本回复、代码、工具调用指令） |
| **转移 $P$** | 游戏引擎确定性更新 | 环境返回观测（工具执行结果、网页内容、API 响应） |
| **奖励 $R$** | 每帧得分变化 | 通常极稀疏——仅任务完成时有信号 |
| **时间步** | 固定帧率，每步 ~33ms | 极不均匀——几秒到几小时 |
| **Episode 长度** | 数百~数千帧 | 数十~数百轮交互（Token 数可达数万） |

### 2.2 关键差异

**状态空间爆炸**：传统 RL 的状态维度固定（如 84×84 像素），Agent 的状态是变长 Token 序列，随交互轮次单调增长。第 $t$ 轮的状态是之前所有交互的拼接：

$$S_t = [\text{system\_prompt}; q; a_1; o_1; a_2; o_2; \dots; a_{t-1}; o_{t-1}]$$

其中 $q$ 是用户查询，$a_i$ 是 LLM 的第 $i$ 次输出，$o_i$ 是环境的第 $i$ 次观测。

**动作空间的双层结构**：LLM 的"动作"是一段 Token 序列，但这段序列可能包含：
- 纯文本推理（思考过程）
- 工具调用指令（如 `<tool_call>search("query")</tool_call>`）
- 最终回答

这使得单个"动作"内部就有复杂的决策结构。

**转移的外部性**：传统 RL 的环境是确定性模拟器，但 Agent 的"环境"是真实世界——网络请求可能超时、API 可能返回错误、工具执行时间不可预测。

## 3. Agent Rollout 循环

![Agent Rollout 循环流程](images/prereq_02_agent_rollout_loop.png)
*完整的 Agent Rollout 循环：LLM 生成 → 动作解析 → 工具执行（耗时秒级~小时级）→ 环境反馈 → 上下文更新 → CM 检查。底部对比白盒（全链路可观测）与黑盒（仅观察 API 请求）的可见性差异*
<!-- 🎨 用 vis-prompts/prereq_02_agent_rollout_loop.txt 生成后替换 -->

### 3.1 核心流程

一次 Agent rollout（轨迹采集）的完整流程：

```
初始化：上下文 = [系统提示 + 用户查询]
循环：
    1. LLM 根据上下文生成一段输出
    2. 解析输出：是最终回答？还是工具调用？
    3. 如果是工具调用：
       a. 执行工具，获取结果
       b. 将工具结果追加到上下文
       c. 回到步骤 1
    4. 如果是最终回答：
       a. 评估答案质量，计算奖励
       b. 结束 rollout
```

### 3.2 完整实现

```python
from dataclasses import dataclass
from typing import Optional
import time
import re

@dataclass
class Trajectory:
    """一条完整的 Agent 交互轨迹"""
    context_snapshots: list[str]  # 每步的上下文快照
    actions: list[str]            # 每步 LLM 的输出
    observations: list[str]       # 每步环境的返回
    rewards: list[float]          # 每步的奖励
    wall_times: list[float]       # 每步的耗时（秒）

def parse_action(llm_output: str) -> tuple[str, Optional[str]]:
    """解析 LLM 输出：区分工具调用和最终回答"""
    tool_match = re.search(r"<tool_call>(.+?)</tool_call>", llm_output, re.DOTALL)
    if tool_match:
        return "tool_call", tool_match.group(1)
    return "final_answer", None

def agent_rollout(llm, tools, query: str, max_turns: int = 20) -> Trajectory:
    """
    执行一次完整的 Agent rollout。

    Args:
        llm: 语言模型（策略 π_θ），接受上下文返回生成文本
        tools: 工具集合，tool_name -> callable
        query: 用户查询
        max_turns: 最大交互轮次
    """
    context = f"[System] You are a helpful agent.\n[User] {query}\n"
    traj = Trajectory([], [], [], [], [])

    for turn in range(max_turns):
        traj.context_snapshots.append(context)

        # --- 步骤 1: LLM 生成（策略采样 a_t ~ π_θ(·|s_t)） ---
        t0 = time.time()
        llm_output = llm.generate(context)
        gen_time = time.time() - t0
        traj.actions.append(llm_output)

        # --- 步骤 2: 解析动作类型 ---
        action_type, tool_cmd = parse_action(llm_output)

        if action_type == "final_answer":
            # 任务完成，计算终局奖励
            reward = evaluate_answer(llm_output, query)
            traj.observations.append("[END]")
            traj.rewards.append(reward)
            traj.wall_times.append(gen_time)
            break

        # --- 步骤 3: 执行工具调用（环境交互） ---
        t0 = time.time()
        try:
            tool_result = execute_tool(tools, tool_cmd, timeout=60)
        except TimeoutError:
            tool_result = "[ERROR] Tool execution timed out"
        except Exception as e:
            tool_result = f"[ERROR] {e}"
        tool_time = time.time() - t0

        # --- 步骤 4: 更新上下文（状态转移 s_t → s_{t+1}） ---
        observation = f"[Tool Result] {tool_result}"
        context += f"[Assistant] {llm_output}\n{observation}\n"
        traj.observations.append(observation)
        traj.rewards.append(0.0)  # 中间步骤通常无奖励（稀疏奖励）
        traj.wall_times.append(gen_time + tool_time)

    return traj
```

### 3.3 耗时方差问题

上面代码中 `wall_times` 的分布极不均匀：

```python
# 典型的耗时分布（秒）
wall_times_example = [
    0.8,    # 第 1 步：纯文本推理
    2.1,    # 第 2 步：简单 API 查询
    0.5,    # 第 3 步：纯文本推理
    180.0,  # 第 4 步：执行复杂代码（编译+运行+测试）
    0.3,    # 第 5 步：总结回答
]
# 总耗时 ~183 秒，但第 4 步占 98%
```

这种极端方差直接导致了 Forge 博客中提到的调度难题：如果同步等待所有 rollout 完成，整个集群的 GPU 利用率受最慢 rollout 支配。

## 4. 脚手架（Scaffold）

### 4.1 定义

**脚手架**是围绕 LLM 的编排逻辑——决定了 LLM 如何接收输入、如何路由工具调用、如何管理记忆。同一个 LLM 在不同脚手架下表现可能截然不同。

```python
class SimpleScaffold:
    """最简脚手架：直接拼接所有历史"""
    def build_context(self, history):
        return "\n".join(history)

    def route_tool(self, tool_call):
        return execute_tool(tool_call)  # 直接执行

class AdvancedScaffold:
    """高级脚手架：带记忆压缩和并行工具调用"""
    def __init__(self, max_context_len=8192):
        self.max_len = max_context_len
        self.memory = []

    def build_context(self, history):
        context = "\n".join(history)
        if len(context) > self.max_len:
            # 上下文管理：摘要压缩旧历史
            summary = self.summarize(history[:-3])
            context = summary + "\n" + "\n".join(history[-3:])
        return context

    def route_tool(self, tool_calls):
        # 并行执行多个工具调用
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            results = list(pool.map(execute_tool, tool_calls))
        return results

    def summarize(self, history):
        return llm.generate(f"Summarize: {history}")
```

### 4.2 白盒 vs 黑盒

| 特征 | 白盒 Agent | 黑盒 Agent |
|------|-----------|-----------|
| 内部状态 | 完全可观察 | 不可观察 |
| 典型例子 | MiniMax 自研脚手架 | 第三方 Agent 框架、OpenCode Agent |
| 训练方式 | 可直接优化脚手架中的决策 | 只能通过 LLM 输出间接优化 |
| CM 策略 | 可纳入训练目标 | 对训练系统透明 |
| 接入成本 | 需要适配 RL 系统接口 | 仅需路由请求到 Gateway |

**白盒**：训练系统能看到 Agent 的每一步决策、每一次上下文变换。这意味着可以：
- 对中间步骤给过程奖励
- 将上下文管理操作纳入策略优化
- 精确追踪状态转移

**黑盒**：训练系统只看到 Agent 发出的 LLM 请求和最终结果。内部的记忆压缩、Multi-Agent 协作等逻辑完全不透明。训练系统需要在这种"零可观测性"下仍能稳定优化模型。

这正是 Forge 三层架构存在的理由——中间件层通过标准化协议同时兼容两类 Agent。

## 5. 上下文管理为什么是"动作"

### 5.1 Context Rot 问题

多轮交互中，上下文状态的演化为：

$$S_{t+1} = S_t \oplus A_t \oplus O_t$$

其中 $\oplus$ 表示拼接。随 $t$ 增大，$S_t$ 单调增长，引发两个问题：

1. **物理限制**：超过上下文窗口长度（如 200K Token）
2. **注意力稀释**：即使在窗口内，关键信息被大量中间步骤"淹没"，模型注意力分散

### 5.2 上下文管理操作

常见 CM 操作及其数学表示：

| CM 操作 | 数学表示 | 说明 |
|---------|---------|------|
| 截断（Truncate） | $S_{t+1} = \text{tail}_k(S_t \oplus A_t \oplus O_t)$ | 只保留最近 $k$ 个 Token |
| 摘要（Summarize） | $S_{t+1} = \text{LLM}_{\text{sum}}(S_t) \oplus A_t \oplus O_t$ | 将历史压缩为摘要 |
| 选择性保留 | $S_{t+1} = \text{filter}(S_t) \oplus A_t \oplus O_t$ | 按重要性筛选保留 |

带 CM 的状态转移变为：

$$S_{t+1} = \text{CM}(S_t \oplus A_t \oplus O_t)$$

### 5.3 训练-推理分布偏移

**问题**：如果 CM 仅在推理时使用，而训练时不使用，会产生什么后果？

设训练时的状态分布为 $\mu_{\text{train}}$（完整上下文），推理时为 $\mu_{\text{infer}}$（经 CM 压缩后的上下文）。两者之间存在分布偏移：

$$D_{\text{KL}}(\mu_{\text{infer}} \| \mu_{\text{train}}) > 0$$

具体地，模型在训练时从未见过"上下文中间被截断"的状态，推理时突然遇到这种断裂结构，被迫在线适应。这会导致：

- 训练时学到的注意力模式失效（期望的上下文位置突然消失）
- 工具调用历史断裂，模型重复调用已执行过的工具
- 推理链逻辑不连贯

### 5.4 Forge 的解法：CM 即动作

Forge 将 CM 建模为 MDP 中的显式动作，而非推理时的后处理。CM 操作直接嵌入 RL 训练循环：

```python
def agent_rollout_with_cm(llm, tools, query, cm_strategy):
    """带上下文管理的 rollout——CM 是训练过程的一部分"""
    context = init_context(query)

    for turn in range(max_turns):
        # LLM 生成（可能包含 CM 决策）
        output = llm.generate(context)
        action_type, payload = parse_action(output)

        if action_type == "context_manage":
            # CM 操作也是 Agent 的动作，参与策略优化
            context = cm_strategy.apply(context, payload)
            # 这一步的 log_prob 会进入策略梯度计算
            continue

        if action_type == "tool_call":
            result = execute_tool(tools, payload)
            context = context + output + result
            # 应用 CM（如果上下文过长）
            if len(context) > threshold:
                context = cm_strategy.auto_compress(context)

        if action_type == "final_answer":
            break

    return trajectory
```

因为 CM 在训练时就参与了 rollout，模型从一开始就学会在压缩后的上下文中推理。$\mu_{\text{train}} \approx \mu_{\text{infer}}$，分布偏移被消除。

## 6. 工程实践要点

### 6.1 多 Agent 并发的状态隔离

多个 Agent 实例并行 rollout 时，每个实例的上下文状态必须完全隔离。常见错误：

```python
# 错误：共享可变状态
global_context = []  # 多个 Agent 读写同一个列表 → 竞态条件

# 正确：每个 rollout 独立的状态副本
def rollout(agent_id):
    local_context = []  # 线程/进程内局部状态
```

### 6.2 工具调用的超时与重试

```python
TOOL_TIMEOUT = {
    "web_search": 10,      # 秒
    "code_execute": 300,   # 5 分钟（编译+运行）
    "file_read": 5,
}

def execute_tool_safe(tool_name, args, max_retries=2):
    for attempt in range(max_retries + 1):
        try:
            return execute_tool(
                tool_name, args,
                timeout=TOOL_TIMEOUT.get(tool_name, 30)
            )
        except TimeoutError:
            if attempt == max_retries:
                return f"[TIMEOUT] {tool_name} failed after {max_retries} retries"
        except Exception as e:
            return f"[ERROR] {e}"
```

### 6.3 轨迹长度差异对 batch 效率的影响

Agent 轨迹长度方差极大（1 轮 vs 50 轮），直接 batch 会导致：

| 填充策略 | 问题 |
|---------|------|
| Padding 到最长 | 短轨迹 90%+ 是无效 padding，GPU 利用率极低 |
| 按长度分桶 | 短桶很快完成，长桶仍在运行，GPU 闲置 |
| 异步不等待 | 训练数据分布偏移（Forge 用 Windowed FIFO 解决） |

### 6.4 脚手架版本管理

训练过程中脚手架会迭代更新。需要记录每条轨迹使用的脚手架版本，否则无法复现：

```python
@dataclass
class TrajectoryMeta:
    scaffold_version: str   # "v2.3.1"
    scaffold_config: dict   # 脚手架配置快照
    model_version: str      # "checkpoint-1200"
    timestamp: float
```

---

> **桥接 → Forge 正文 §2**：理解了 Agent rollout 循环的结构后，Forge 的三层架构解决的就是"如何让这个循环大规模并行运行"——Agent 层负责执行 rollout、中间件层做数据缓冲和协议转换、引擎层做高效训推。白盒/黑盒的区分直接对应 §2.1 和 §2.2 两种训练范式。
>
> **下一篇 → [前置三：LLM 推理的计算瓶颈](prereq-03-llm-inference-bottleneck.md)**：Agent rollout 中每次 LLM 生成都需要完整的前向传播。当上下文长达 200K 时，计算量如何分布？KV Cache 如何加速？多轮对话中的前缀冗余又有多严重？
