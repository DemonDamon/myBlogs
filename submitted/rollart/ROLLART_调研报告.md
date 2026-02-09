# ROLLART：分离式基础设施如何突破 Agentic RL 的规模化瓶颈

> **论文**：[ROLLART: Scaling Agentic RL Training via Disaggregated Infrastructure](https://arxiv.org/pdf/2512.22560)
> **代码**：[github.com/alibaba/ROLL](https://github.com/alibaba/ROLL)（Apache 2.0）
> **团队**：阿里巴巴淘宝天猫集团 & 阿里巴巴集团

## Agentic RL 的规模化挑战

大模型强化学习正从"给一个 prompt、生成一个回答、打一个分"的简单范式，演进到 **Agentic RL**——模型需要像人类一样与外部环境多轮交互、自主决策、长期规划。典型场景包括代码编写（SWE-bench）、网页浏览（WebArena）、数学推理（GEM-Math）和游戏决策（FrozenLake）。

![Agentic 环境分类](<images/table1: Taxonomy of Adopted Agentic Environments.png>)

然而，Agentic RL 的训练远比标准 RLHF 复杂。它的工作负载高度异构：LLM 推理是 GPU 密集型，环境交互是 CPU/IO 密集型，奖励计算可能调用外部 API 或沙箱——三者的延迟特征完全不同。更棘手的是，环境交互是有状态的（上一轮的 action 决定下一轮的 observation），这使得传统的批量同步范式频繁遭遇"依赖气泡"和长尾阻塞。

ROLLART 针对这些痛点，提出了一个核心思路：**将推理、训练、环境交互、奖励计算拆分到异构硬件上独立运行**，再通过轨迹级异步调度将它们串联起来。下图展示了这一分离式基础设施的全景——训练集群使用计算型 GPU（如 H800），推理集群使用带宽型 GPU（如 H20），环境在 CPU/K8s 集群上运行，奖励计算使用 Serverless 平台：

![分离式基础设施全景](<images/Figure 1: Disaggregated infrastructure for agentic RL training.png>)

下面我们从"问题诊断"出发，逐层拆解 ROLLART 的设计。

## 问题诊断：同步训练为什么撑不住

在深入架构之前，先看两组关键数据。

**第一组：训练步的延迟拆解**。论文对 SWE-bench 任务做了逐阶段计时。正常迭代中 LLM 生成占 54%，但环境一旦出现超时（大约每 10 轮发生 1 次），env.reset 独占 78% 时间，迭代耗时从 366s 飙升到 513s：

![训练步时间拆解](<images/Figure3.png>)

**第二组：同步 vs 异步的 GPU 利用率对比**。下图左半部分是同步训练——Train 和 Rollout 在同一组 GPU 上交替执行，每个阶段必须等上一阶段完成才能开始，斜线阴影区域就是"依赖气泡"，GPU 完全空闲。在分离式部署下，跨集群的权重传输延迟（几秒到几十秒）会进一步放大这些气泡。

![同步 vs 异步训练](<images/Figure 2: Synchronous vs. asynchronous training.png>)

右半部分是异步训练（one-off 模式）：Train 和 Rollout 在独立 GPU 上并行运行。Rollout 不必等当前 Train 完成——它持续使用略旧一个版本的模型权重（如版本 n-1）生成轨迹，Train 同时消费上一批轨迹做梯度更新。代价是引入一定的数据新鲜度损失（staleness），但 GPU 利用率显著提升，依赖气泡被有效消除。ROLLART 通过"异步边界 alpha"来控制新鲜度与吞吐的平衡。

这两组数据清晰地指向同一个结论：**同步训练在 Agentic 场景下不可行，必须走异构分离 + 异步并行的路线**。

## 系统架构总览

ROLLART 的完整系统架构分为三层：

![系统架构](<images/Figure 9: System Architecture of ROLLART.png>)

**顶层：用户配置（User Config）**。用户通过 Hydra 配置文件声明硬件亲和映射、Serverless 注册等信息，系统据此构建训练管线。Hydra 的分层覆盖机制使得同一套代码可以灵活切换 Colocated（共享 GPU）和 Disaggregated（独立 GPU）两种部署模式：

```yaml
# Disaggregated 模式：角色独占 GPU
actor_train:
  device_mapping: list(range(0,4))   # GPUs [0,3]
actor_infer:
  device_mapping: list(range(4,8))   # GPUs [4,7]
critic:
  device_mapping: list(range(8,12))  # GPUs [8,11]
```

**中间层：分布式运行时（Distributed Runtime Layer）**，包含两个核心组件。

**Rollout Scheduler** 管理轨迹的完整生命周期。内含 LLMProxy（网关，负责将进行中的轨迹路由到合适的推理 Worker）和 SampleBuffer（缓存已完成的轨迹，供训练阶段拉取）。

**Pipeline Runner** 编排四类 Cluster，每个 Cluster 管理一组同质 Worker：
- **Environment Cluster** → EnvManager → env strategy（CPU/K8s），负责环境的 reset/step 操作
- **ActorGen Cluster** → Infer Worker → vLLM/SGLang strategy（GPU），负责 LLM 推理生成
- **Reward Cluster** → Reward Worker → FC strategy（Serverless），负责无状态的奖励评估
- **ActorTrain Cluster** → Train Worker → Megatron strategy（计算型 GPU），负责模型参数更新

数据流方面：Environment 发送 Action 给 ActorGen 并接收 feedback；ActorGen 的 Ongoing Trajectory 通过 Transfer Protocol 发往 Reward 获取评分；ActorTrain 通过 Model Update Group 将更新后的权重同步回 ActorGen。

**底层：资源管理器（Resource Manager）**。维护全局资源视图，将异构资源绑定到对应 Worker——CPU Cluster 承载环境容器，APIs 对外暴露 LLM API 和 Reward API 接口，Heterogeneous GPU Clusters 中 H20 节点适合 decode 密集任务、H800 节点适合 prefill 密集任务和训练。

### Ray 多角色分布式架构

整个运行时基于 Ray 构建。`Cluster` 是最核心的抽象，统一管理 Worker 的生命周期和资源分配：

```python
class Cluster:
    def __init__(self, name, worker_cls, resource_manager, worker_config):
        self.cluster_name = name
        self.worker_cls = worker_cls
        self.resource_manager = resource_manager
        self.workers: List[Any] = []
        self.placement_groups = None
```

角色分为五类：**Actor Workers**（策略模型训练和推理）、**Critic Workers**（价值函数估计）、**Reference Workers**（KL 散度计算）、**Reward Workers**（领域特定奖励计算，涵盖数学验证、代码沙箱、LLM-as-Judge、规则匹配等多种模式）、**Environment Workers**（智能体任务环境）。

## 轨迹级异步 Rollout

理解了架构全景后，我们深入 ROLLART 最关键的创新之一：轨迹级异步并行 Rollout。

### 与传统方案的本质区别

传统 Agentic RL 系统采用 Environment-level 并行——所有环境在每个时间步同步执行，统一收集结果后再进入下一步。这意味着最慢的环境决定了整体速度。ROLLART 的做法完全不同：

| 特性 | 传统 Environment-level 并行 | ROLL 轨迹级异步并行 |
|------|-------------------------|------------------|
| **粒度** | 每个时间步同步执行 | 环境级别独立执行 |
| **同步屏障** | 存在同步点 | 无同步屏障 |
| **执行方式** | 同步执行 | 异步执行 |
| **数据收集** | 统一收集 | `rollout_scheduler.get_batch()` 按需收集 |

下图展示了轨迹级 Rollout 的整体流程——每个 EnvManager 独立管理一条轨迹的生命周期，通过 LLMProxy 异步调用推理引擎，彼此之间完全解耦：

![轨迹级 Rollout 概览](<images/Figure 7: Trajectory-Level Rollout Overview.png>)

这种独立性在代码层面通过每个 EnvironmentWorker 管理多个 BaseEnvManager 实例来保证，每个 BaseEnvManager 在单独线程中执行 `run_rollout_loop()`：

```python
class EnvironmentWorker:
    def __init__(self):
        self.env_managers = []
        # 每个 BaseEnvManager 在单独线程中执行 run_rollout_loop()
```

负载均衡方面，ROLLART 设计了 **LoadBalancer**（基于租约系统的"最佳适应"策略）和 **RequestScheduler**（高并发 LLM 生成请求调度），并通过 `max_env_num_per_worker`、`num_env_groups`、`group_size` 三个参数控制并发度。

### 处理长尾延迟

独立执行解决了同步阻塞，但 Agentic 环境本身的延迟仍然是长尾分布的。下图分析了这一问题——env.reset 和 env.step 均呈长尾分布，在批量交互模式下，一个慢环境会拖垮整个批次：

![环境交互分析](<images/Figure 5: The analysis of environment interaction.png>)

ROLLART 的应对策略包括：当 `async_generation_ratio > 0` 时推理提前生成多倍数据，通过 **EnvActivityMonitor**（双时间戳跟踪机制）检测挂起环境，使用 **ReplayBuffer** 实现灵活的样本收集窗口，以及通过冗余环境启动（启动比所需更多的环境，收集够后终止慢环境）来容忍故障和加速训练。

## 异步训练与 GPU 时分复用

轨迹级异步 Rollout 解决了数据生产端的效率问题，但训练端同样需要异步化。

### 异步训练工作流

下图展示了完整的异步训练工作流：EnvManager 持续生成轨迹写入 SampleBuffer，训练阶段通过 `get_batch` 拉取数据，通过 `suspend/resume` 控制 rollout 节奏，`model_update` 同步权重：

![异步训练工作流](<images/Figure 8: Asynchronous Training Workflow.png>)

核心配置只需一个参数：

```yaml
async_generation_ratio: 1  # 异步生成倍数
```

推理过程提前生成 `async_generation_ratio` 倍的数据，训练过程使用预生成的数据进行学习，无需等待当前批次推理完成即可开始下一轮。但这种异步化也带来了挑战：

| 挑战 | 解决方案 |
|------|---------|
| **内存管理** | ReplayBuffer 动态调整 batch_size；GPU 时分复用 |
| **数据新鲜度** | ReplayBuffer.advance_step 推进训练步；垃圾回收过时 prompt |
| **训练收敛性** | async_generation_ratio 控制新鲜度；验证阶段暂停异步生成 |

### GPU 时分复用

在资源受限的场景下，ROLLART 支持 Colocated 模式——推理和训练共享同一组 GPU，通过时间片分配避免冲突。以 Partial GPU Mode 为例：

```python
if train_devices.issubset(infer_devices) and len(train_devices) < len(infer_devices):
    # 进入 partial_gpu_mode
```

执行流程是：推理阶段 actor_infer 在所有分配的 GPU 上执行 → 收缩阶段 actor_infer 从与训练共享的 GPU 上卸载模型 → 训练阶段 actor_train 和 critic 使用释放的 GPU 训练 → 扩展阶段下一迭代重新加载 actor_infer 模型。

为避免内存碎片化，ROLLART 采用了模型状态整体管理（权重和 KV Cache 整体卸载/加载）、vLLM 的 PagedAttention 消除内存碎片、`gc.collect()` + `current_platform.empty_cache()` 主动回收，以及 `state_offload_manager` 上下文管理器简化状态切换。

## 高效训练引擎

### 硬件亲和映射

不同任务对硬件的需求截然不同。FrozenLake（多轮交互、prefill 密集）在计算型 H800 上更快，GEM-Math（少轮、decode 密集）在带宽型 H20 上更快：

![不同任务在 H20/H800 上的 Rollout 时间对比](<images/Figure 4: End-to-end rollout time (seconds) of different tasks on H20 and H800 GPUs across varying batch sizes..png>)

![GPU 硬件规格对比](<images/Table 2: NVIDIA GPU specifications.png>)

ROLLART 的 Resource Manager 根据任务的 prefill/decode 比例，动态将任务路由到最匹配的硬件上，实现硬件亲和映射。

### Megatron-Core 5D 并行

训练端集成了 Megatron-Core 的 5D 并行策略，各策略的适用场景如下：

| 并行策略 | 优势 | 挑战 | 适用场景 |
|---------|------|------|---------|
| **DP（数据并行）** | 易于实现 | 通信开销大 | 小模型、大批次 |
| **TP（张量并行）** | 减少单 GPU 内存 | 层内通信 | 大模型训练 |
| **PP（流水线并行）** | 进一步减少内存 | 气泡时间 | 深层模型 |
| **CP（上下文并行）** | 处理超长序列 | 负载均衡 | 长文本任务 |
| **EP（专家并行）** | 支持 MoE 模型 | 专家路由 | MoE 模型 |

### Sequence Packing 与 Dynamic Batching

Agentic 场景的序列长度方差极大——短轨迹几十 token，长轨迹数万 token。ROLLART 通过两层机制应对。

**Sequence Packing** 的核心思想是消除 padding tokens：将不同长度的序列打包拼接，序列长度必须对齐到 `2 x CP_SIZE x TP_SIZE` 的倍数，从而减少 micro-batch 数量和 PP 气泡时间。启用时需要配合变长序列支持：

```python
if use_sequence_packing and pp_size > 1:
    model.config.variable_seq_lengths = True
```

**Dynamic Batching** 则在 DP Rank 维度根据实际 token 数划分，将长度相似的样本分组，考虑 `max_tokens_per_microbatch` 和 `sequence_length_round` 约束，支持 VPP（虚拟流水线并行）：

```python
if worker_config.use_dynamic_batching_in_infer:
    batch, metrics = dynamic_batching_shard(
        batch,
        worker.dp_size,
        worker_config.max_tokens_per_microbatch_in_infer,
        worker_config.sequence_length_round_in_infer
    )
```

两者协同工作时，Sequence Packing 在训练侧消除 padding，Dynamic Batching 在推理侧优化内存分配。

### PagedAttention 与 KV Cache 管理

推理引擎（vLLM/SGLang）采用 PagedAttention 机制，以类似操作系统内存分页的方式管理 KV Cache：分页存储、支持跨请求共享物理页面、显著降低内存碎片。连续批处理（continuous batching）进一步与 ROLL 的 Dynamic Batching 相辅相成，使得推理吞吐最大化。

### Trajectory Representation

轨迹在系统内的表示由 **TrajEnvManager** 统一管理：

```python
trajectory = {
    'input_ids': concat(prompt_ids, response_ids),
    'attention_mask': concat(prompt_masks, response_masks),
    'infer_logprobs': collected_logprobs
}
# Padding 到 pipeline_config.sequence_length
```

对于多模态场景，**VLTrajEnvManager** 扩展了多模态输入处理能力，通过 `format_messages` 方法处理视觉-语言混合输入，`split_by_token` 和 `token_ids_to_assistant_mask` 精细处理 token 级别的 mask。

Prompt 是 LLM 与环境交互的唯一介质，包含历史对话、动作、奖励等信息，严格遵循 LLM 聊天模板，并通过强制输出格式与最大长度限制来平衡信息量和计算成本。

## RL 算法全景

ROLLART 的一大优势是算法生态丰富，支持 10+ 种 RL 算法，覆盖了从简单到复杂的各类 Agentic 场景。

### 算法对比

**PPO（Proximal Policy Optimization）**：稳定性好、通用性强，但稀疏奖励环境下效率低、长序列信用分配不够精细。适合通用 Agentic 任务。

**GRPO（Group Relative Policy Optimization）**：无需 Critic、计算效率高、对稀疏奖励鲁棒。但 Token 级优化引入高方差，MoE 模型训练不稳定。适合奖励信号明确的任务。

**Reinforce++**：简单易实现、直接优化策略，但高方差、对稀疏奖励鲁棒性差。适合教学演示和简单任务。

**TOPR（Tapered Off-Policy REINFORCE）**：样本效率高、训练稳定性好，但参数调优复杂。适合离策略训练场景。

**RAFT++（Reward rAnked Fine-Tuning）**：基于相对奖励学习、样本利用率高，但依赖奖励函数设计。适合可排序响应的任务。

**GSPO（Group Sequence Policy Optimization）**：序列级优化降低方差、天然支持 MoE 模型，但实现复杂。适合 MoE 模型和需要序列级优化的任务。

**StarPO（State-Thinking-Actions-Reward PO）**：轨迹级信用分配、处理稀疏奖励，但计算成本高。适合多轮交互、长期依赖任务。

**GiGPO（Group-in-Group PO）**：分层优势估计（情节 + 步骤级）、细粒度信用分配、无需 Critic，但需要调优 `step_reward_weight` 和 `episode_reward_weight`。适合复杂多轮交互、需要精细信用分配的任务。

### Agentic 场景下的选择建议

算法选择需要综合考虑三个维度：

**奖励信号密度**：密集奖励倾向 PPO/TOPR，稀疏奖励倾向 GRPO/RAFT++/StarPO。

**信用分配需求**：如果任务需要知道"哪一步决策导致了最终成功或失败"（例如多轮代码调试），选择 GiGPO 或 StarPO；如果只需整体奖励反馈，GRPO/Reinforce++ 即可。

**模型架构**：MoE 模型优先考虑 GSPO/GiGPO（它们在序列级优化上对 MoE 更友好），非 MoE 模型用 PPO/GRPO 即可。

### TrajectoryWise vs StepWise：StarPO 与 GiGPO 的深层对比

这两种范式代表了 Agentic RL 信用分配的两种哲学。

**TrajectoryWise（StarPO）** 将整个多轮交互轨迹视为一个连贯单元，基于完整轨迹累积奖励做梯度估计（REINFORCE），配置为 `adv_estimator: "reinforce"`。优势是概念简洁、对长期依赖建模自然，代价是需要完整轨迹才能优化，长轨迹或稀疏奖励下样本效率较低。

**StepWise（GiGPO）** 实现两层优势估计：情节级别基于完整轨迹组计算宏观相对优势，步骤级别通过锚定状态分组机制追溯构建步骤级组。配置为 `adv_estimator: "gigpo"`。它能更高效地利用样本，在多轮交互和复杂推理任务中表现更好，但算法复杂度更高。

选择原则：如果任务奖励较密集且侧重整体表现，用 TrajectoryWise；如果需要精细控制每步决策或奖励极度稀疏，用 StepWise。

## 多领域训练与能力保持

当同时在代码、数学、网页浏览等多个领域做 RLVR 训练时，如何防止"偏科"和灾难性遗忘？ROLLART 在数据调度和正则化两个层面给出了方案。

### DynamicSamplingScheduler 动态采样调度

每个领域拥有独立的 DynamicSamplingScheduler 实例，关联特定数据集 `domain_datasets[domain]`，并行调用各领域的 `get_batch` 方法。领域批次大小通过 `domain_interleave_probs` 预配置比例分配：

```python
self.domain_batch_size = calculate_domain_batch_sizes(
    domain_interleave_probs,
    rollout_batch_size
)
```

防止领域被忽视的机制包括：预设采样比例确保每个领域占据一定份额、独立数据集避免空领域（空数据集触发断言错误）、`BatchStratifiedSampler` 在数据加载层面实现分层抽样。目前的局限是主要基于预配置比例，尚未实现基于实时性能反馈的动态调整。

### 防止灾难性遗忘

ROLLART 采用多层正则化技术平衡 Agentic 性能和通用能力：

**KL 散度惩罚**——通过 Reference 模型约束策略更新幅度：

```python
kl_loss = compute_kl_divergence(
    current_policy,
    reference_policy
)
# kl_ctrl 自适应调整惩罚系数
```

**优势估计与裁剪**——支持 GAE、GRPO、Reinforce 等多种优势估计器，结合优势裁剪（`advantage_clip`）和优势白化（`whiten_advantages`）降低梯度方差。

**PPO 策略约束**——策略梯度裁剪（`pg_clip`）和双重裁剪损失（`dual_clip_loss`）限制单次更新幅度，防止策略崩溃。梯度累积进一步稳定训练：

```yaml
actor_train:
  training_args:
    per_device_train_batch_size: 2
    gradient_accumulation_steps: 128  # 有效 batch = 2 x 128
```

## 实验评估

论文在 96 x H800 + 32 x H20 集群上，训练 Qwen3-8B/14B/32B 进行了全面评估。

### 端到端性能

下图展示了端到端 time-to-score、归一化吞吐量和资源扩展性对比。ROLLART 比 veRL+ 基线快 2.05x，比 StreamRL 快 1.35x；归一化吞吐达到同步基线的 2.65–4.58x：

![端到端评估结果](<images/Figure 10.png>)

### 设计原则验证

硬件亲和性映射与轨迹级异步的效果验证——混合 H800+H20 配置比纯 H800 快 1.12–1.37x，轨迹级交互在高延迟方差下比批量交互快 2.27x：

![硬件亲和性与轨迹级异步分析](<images/Figure 11&12.png>)

异步边界和 Serverless 奖励的效果——alpha=1 已接近最优平衡点，Serverless 奖励使 GPU 利用率从 6% 飙升至 88%：

![异步边界与 Serverless 奖励分析](<images/Figure 13&14.png>)

## 生态与应用

ROLLART 已在多个大规模场景中得到验证，代表性工作包括：

- **STAgent**：时空理解智能体，分层数据筛选（1:10,000 过滤比例）
- **IPRO**：视频扩散框架，使用 RL 增强身份保持
- **TaoSR-SHE**：淘宝搜索相关性，混合奖励模型 + 离线验证器
- **EARL**：高效 Agentic RL 系统，动态并行度选择器
- **LiveThinking**：实时推理，670B→30B MoE 压缩，30 倍计算减少
- **RecGPT**：下一代推荐系统，用户意图核心

支持的模型系列覆盖 Qwen 全家族（Qwen2/3、Qwen-VL、Qwen3-Omni）、LLaMA、Mixtral、DeepSeek-V3 和 GLM4-MoE。

### 配置调优建议

根据场景特点，推荐以下配置策略：

**异步生成比例**：推理密集型任务设 `async_generation_ratio: 2-3`，训练密集型任务设 `1`，调试阶段设 `0`。

**并行策略**：大模型（>70B）优先 TP+PP，超长序列启用 CP，MoE 模型配置 EP。

**批处理优化**：变长序列多时启用 Sequence Packing，内存受限时启用 Dynamic Batching，推理端配置 vLLM 或 SGLang。

**适用边界**：ROLLART 在大规模 GPU 集群（100+ GPU）、需要高吞吐推理、多领域联合训练的 Agentic RL 场景中优势最大。对于小规模训练（<8 GPU）或简单 SFT 任务，轻量框架可能更合适。

## 总结与展望

ROLLART 通过分离式基础设施这一核心创新，系统性地解决了大规模 Agentic RL 训练的三大瓶颈：异构工作负载的资源竞争、同步执行的依赖气泡、以及有状态环境的长尾延迟。其关键设计原则可以归纳为：

- **分离即解耦**：将推理、训练、环境、奖励拆分到异构硬件，实现真正的异步训练
- **轨迹即粒度**：以轨迹而非批次为调度单位，消除同步屏障和长尾阻塞
- **亲和即效率**：根据任务特征将工作负载路由到最匹配的硬件
- **弹性即资源**：无状态组件（如奖励计算）卸载到 Serverless 平台，按需扩缩

未来方向上，ROLLART 已在开发 FSDP2 Strategy 支持、GPU partial overlapping 和 Ascend NPU 适配。更长远的改进方向包括基于任务特性的自动化配置选择、实时性能反馈驱动的动态资源分配、以及更强的视觉-语言-动作联合训练能力。

## 参考资料

**论文**
- ROLLART 论文：https://arxiv.org/pdf/2512.22560
- ROLL 技术报告：https://arxiv.org/abs/2506.06122
- Let It Flow 报告：https://arxiv.org/abs/2512.24873

**代码与文档**
- 主仓库：https://github.com/alibaba/ROLL
- 文档：https://alibaba.github.io/ROLL/
- DeepWiki：https://deepwiki.com/alibaba/ROLL

**相关论文**
- Tricks or Traps? https://arxiv.org/abs/2508.08221
- ROLL Flash Part I: https://arxiv.org/abs/2510.11345
- Asymmetric PPO: https://arxiv.org/abs/2510.01656
- Attention Illuminates: https://arxiv.org/abs/2510.13554
- RollPacker: https://arxiv.org/abs/2509.21009
- GiGPO: https://arxiv.org/abs/2505.10978
- GSPO: https://arxiv.org/abs/2507.18071
