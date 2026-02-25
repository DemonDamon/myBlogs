# UI-Venus-1.5：蚂蚁集团如何用四阶段训练打造 SOTA 级 GUI Agent

> 蚂蚁集团 Venus Team（InclusionAI）开源的端到端 GUI 智能体，在 ScreenSpot-Pro、VenusBench-GD、AndroidWorld 等多个权威基准上刷新 SOTA。本文基于官方技术报告深度解读其核心创新：Mid-Training、Online RL 与 Model Merging。

## 一、GUI Agent 为什么重要？

想象一个场景：你对手机说"帮我在淘宝上搜一下这款耳机的价格，加购最便宜的那家"，然后 AI 就像一个真人一样，打开淘宝、搜索、比价、点击加购。这就是 **GUI Agent**（图形界面智能体）要做的事情——让 AI 直接操作屏幕界面，替你完成各种繁琐的数字化操作。

与传统 API 自动化不同，GUI Agent 的核心难度在于：它只能"看"到屏幕截图，必须像人一样理解界面上的按钮、文本框、图标，然后精准地点击、滑动、输入。这要求模型同时具备**视觉感知**（看懂界面）、**语义理解**（理解用户意图）和**动作执行**（精准操作）三重能力。

**UI-Venus-1.5** 正是蚂蚁集团 Venus Team 给出的答案。

## 二、系统概览：端到端的统一设计

UI-Venus-1.5 采用纯端到端架构：用户发出自然语言指令，模型直接解读屏幕截图，输出具体操作（点击坐标、滑动方向、输入文本等），然后在真实环境中执行，循环往复直到任务完成。

![UI-Venus-1.5 系统概览与轨迹实例](images/paper_figure_2.png)
*图：UI-Venus-1.5 系统总览。上方展示端到端架构——用户指令经模型理解后，通过 ADB/Playwright 在移动端和 Web 端执行操作。下方展示两个真实任务轨迹：中文 QQ 音乐操作和英文菜谱搜索。*

### 模型家族

| 模型 | 参数量 | 类型 | 定位 |
|------|--------|------|------|
| UI-Venus-1.5-2B | 2B | Dense | 端侧轻量部署 |
| UI-Venus-1.5-8B | 8B | Dense | 性价比之选 |
| UI-Venus-1.5-30B-A3B | 30B（激活 3B） | MoE | 旗舰性能 |

三个模型均基于 **Qwen3-VL** 系列，覆盖从端侧到云端的全场景部署需求。其中 MoE 变体 30B-A3B 以仅 3B 的激活参数达到 30B 级性能，推理效率极高。

### 统一动作空间

![UI-Venus-1.5 动作空间定义](images/paper_table_8.png)
*表：完整动作空间。在 1.0 基础上新增 Hover、DoubleClick、Hotkey 三个 Web 专用动作，统一覆盖移动端和 Web 端。*

## 三、四阶段训练流程

UI-Venus-1.5 的训练过程可以概括为一条清晰的流水线：从通用视觉大模型出发，经过四个阶段逐步注入 GUI 专业能力。

![四阶段训练流水线](images/paper_figure_3.png)
*图：四阶段训练流程。Qwen3-VL → Mid-Training → Offline-RL（Grounding/Mobile/Web 三路并行）→ Online-RL（Mobile/Web 在真实环境中强化）→ Model Merge 合成最终统一模型。*

每个阶段解决一个核心问题：

| 阶段 | 核心目标 | 关键方法 |
|------|----------|----------|
| **Mid-Training** | 注入 GUI 领域知识 | 10B tokens, 30+ 数据集 |
| **Offline-RL** | 任务特定优化 | 分领域奖励函数设计 |
| **Online-RL** | 真实环境导航增强 | GRPO + DaaS 全轨迹 rollout |
| **Model Merge** | 统一单模型 | TIES-Merge 多专家融合 |

下面逐一拆解。

## 四、Mid-Training：给大模型装上 GUI 的"眼睛"

### 4.1 为什么需要 Mid-Training？

通用视觉大模型（如 Qwen3-VL）虽然"看得见"，但并不真正"看得懂" GUI。它缺少对按钮、文本框、下拉菜单等界面元素的细粒度结构化理解。如果直接进入强化学习阶段，模型连基本的界面元素都定位不了，奖励信号极其稀疏，策略优化根本无法启动。

Mid-Training 的作用就是在通用预训练和强化学习之间架一座桥——用大规模 GUI 专业数据注入领域知识。

### 4.2 数据构成

![Mid-Training 数据分布与迭代精炼流程](images/paper_figure_4.png)
*图：(a) Mid-Training 语料分布——内环为功能分类（GUI-VQA 22.1%、Grounding 24.8%、Perception 20.8% 等），外环为数据来源与目标平台；(b) 迭代数据精炼流程：教师模型评分 → 高分直接入库 / 中分重写 / 低分丢弃或重建。*

这一阶段用了 **30+ 数据集、10B tokens**，涵盖四大监督目标：

- **导航与定位**：指令到动作的对齐
- **推理链**：高层目标分解为中间步骤（CoT）
- **GUI-VQA**：界面组件的语义理解
- **细粒度感知**：图标识别、控件状态检测、OCR-free 密集描述

数据质量是关键。团队使用 Qwen3-VL-235B-A22B 作为"教师模型"，对训练数据打分（0-10 分），高分（≥7）直接进入"黄金池"，中分（4-6）送入重写引擎修正，低分（0-3）丢弃或完全重建。经过迭代精炼，**高保真样本比例从 69.7% 提升至 89.7%**。

### 4.3 DaaS 数据生成循环

![DaaS 数据生成循环](images/paper_figure_5.png)
*图：基于 DaaS 的真实设备数据生成循环。种子指令 → MLLM 生成候选任务 → 语义去重 → GUI Agent 在云设备上执行 → 轨迹抓取与验证 → 反馈循环迭代。最终轨迹生成成功率从 17.9% 提升到 70%+。*

静态数据集不够用，团队还构建了一套**真实设备交互数据生成管道**。通过 DaaS（Device-as-a-Service）系统，在云端设备上自动执行任务、录制轨迹、验证质量，并将成功轨迹反馈给 MLLM 作为 In-context 示例，形成迭代进化循环。最终产出超过 **30,000 条验证通过的交互轨迹**。

### 4.4 Mid-Training 的效果

Mid-Training 到底有没有用？看一组直观的可视化：

![潜在空间可视化对比](images/paper_figure_8.png)
*图：t-SNE 潜在空间可视化。(a) 原始基座模型——GUI 领域数据（蓝色）与通用感知数据（灰色）混杂在一起；(b) Mid-Training 后——GUI 领域聚类明显分离，模型建立了专属的 GUI 语义表示。*

左图中 GUI 数据和通用数据混在一起，模型分不清界面元素和普通图像。右图经过 Mid-Training 后，GUI 领域聚类清晰分离——模型真正学会了"看懂"界面。

## 五、强化学习：从"纸上谈兵"到"实战演练"

### 5.1 Offline-RL：奠定基础

Offline-RL 阶段分三路并行训练 Grounding、Mobile、Web 三个专家模型，各自使用针对性的奖励函数：

- **Grounding 奖励**：格式正确性 + point-in-box 定位精度
- **Navigation 奖励**：格式奖励 + 动作奖励（动作类型匹配 + 内容/坐标精度）

特别值得注意的是 **Refusal 能力**：当指令要求的元素在屏幕上不存在时，模型输出 `[-1, -1]` 拒绝操作，而不是随意猜一个坐标。这大幅减少了实际使用中的幻觉问题。

### 5.2 Step 与 Trace 的"剪刀差"

Offline-RL 的一个关键发现直接推动了 Online-RL 的引入：

![Step 与 Trace 准确率的"剪刀差"](images/paper_figure_6.png)
*图：Offline-RL 训练过程中，Step-level 准确率持续上升（蓝色），但 Trace-level 准确率在达到峰值后开始下降（红色）。这一"剪刀差"在 Mobile 和 Web 场景均存在。*

**每一步都做对了，但连起来任务就失败了**——这就是 Step-Trace 准确率不匹配问题。Offline-RL 只优化单步奖励，无法保证多步骤的端到端任务完成。

### 5.3 Online-RL：在真实设备上练兵

为了解决"剪刀差"，团队引入了 Online-RL——在真实设备环境中进行**全轨迹 rollout**，优化轨迹级别的奖励。

核心算法是 **GRPO（Group Relative Policy Optimization）**：对同一任务生成多条轨迹，计算轨迹级优势，相对排名优化策略。

Online-RL 的基础设施是 **DaaS 平台**：

![DaaS 平台架构](images/paper_figure_7.png)
*图：DaaS 平台工程架构。左侧为多语言 SDK（Python/Java/Http/RPC），中间是 GCGW 网关层（二级 Hash 路由、零拷贝 I/O、协程并发），右侧通过 CDP/ADB/SSH 协议连接 Chrome/Mobile/Desktop 三类设备集群。*

这套系统支持**数千台异构设备**（手机、浏览器、桌面）的并发管理，百万级日操作请求，毫秒级任务调度。它不仅用于 Online-RL 训练，也支撑数据标注和线上推理评估。

奖励设计采用三重机制：

- **任务完成奖励**：任务是否最终成功
- **无效动作惩罚**：减少无意义操作
- **轨迹长度衰减**：鼓励高效完成任务

## 六、Model Merging：三合一的统一智能体

有了 Grounding、Mobile、Web 三个领域专家，如何合成一个统一模型？

团队对比了两种方案：
- **Linear Merge**：简单加权平均
- **TIES-Merge**：先修剪冗余参数，再解决符号冲突，最后融合

实验证明 TIES-Merge 远优于 Linear Merge，因为它能有效减少不同领域专家之间的参数冲突。

![各阶段消融实验](images/paper_table_7.png)
*表：四阶段消融实验（SS-Pro = ScreenSpot-Pro, AW = AndroidWorld）。每一阶段的增益清晰可见：Offline-RL 大幅提升基础性能，Online-RL 进一步推高 Navigation 成绩（+7.5~14.5%），Model Merge 后 AndroidWorld 反而提升 2.1%。*

关键数据：30B-A3B 模型经过 Model Merge 后，ScreenSpot-Pro 仅下降 1.4%，而 AndroidWorld **反而提升 2.1%**——说明多领域知识的融合产生了正向迁移效果。

## 七、基准测试：全面 SOTA

### 7.1 总览

![多基准 SOTA 表现](images/paper_figure_1.png)
*图：UI-Venus-1.5 在 Grounding（上方雷达图）和 Navigation（下方柱状图）基准上的全面对比。紫色为 UI-Venus-1.5，在绝大多数基准上取得最佳或接近最佳成绩。*

### 7.2 Grounding 基准

![Grounding 基准详细对比](images/paper_table_1.png)
*表：Grounding 基准全面对比。UI-Venus-1.5-30B-A3B 在 VenusBench-GD（75.0%）、ScreenSpot-Pro（69.6%）、OSWorld-G-R（76.4%）、OSWorld-G（70.6%）、UI-Vision（54.7%）上均为 SOTA。*

核心亮点：
- **VenusBench-GD 75.0%**：在这个世界最大规模 GUI 测试基准上遥遥领先
- **ScreenSpot-Pro 69.6%**：超越 MAI-UI-32B（67.9%），成为新 SOTA
- **8B 模型即超越上代 72B**：规模效率惊人

### 7.3 Navigation 基准

![AndroidWorld 基准](images/paper_table_2.png)
*表：AndroidWorld 基准对比。UI-Venus-1.5-30B-A3B 以 77.6% 成功率登顶，超越 Seed1.8（70.7%）、Holo2-30B-A3B（71.6%）、MAI-UI（73.3%）等强基线。*

![AndroidLab 基准](images/paper_table_3.png)
*表：AndroidLab 基准对比。UI-Venus-1.5-8B 以 55.1%（人工验证后 68.1%）成绩领先，超越所有同规模竞品。†号表示人工验证修正后的成绩。*

![VenusBench-Mobile 基准](images/paper_table_4.png)
*表：VenusBench-Mobile 基准。UI-Venus-1.5-30B-A3B 以 21.5% 大幅领先第二名 UI-Venus-1.0-72B（15.4%），提升 39.6%。*

![WebVoyager 基准](images/paper_table_5.png)
*表：WebVoyager 基准。UI-Venus-1.5-30B-A3B 达到 76.0%，与领先的闭源模型 Claude-3.7（84.1%）、OpenAI-CUA（87.0%）差距缩小，在开源模型中表现领先。*

## 八、中文应用生态：40+ 主流 App 深度适配

UI-Venus-1.5 不只是刷基准的"应试选手"。团队配套开源了 **Venus Framework**——完整的 Android 自动化框架，支持：

- 自然语言单任务执行
- 多设备并行批处理
- 轨迹录制与回放
- 智能循环检测（防止 Agent 陷入死循环）

已深度适配 **40+ 主流中文 App**，覆盖日常生活各场景：

| 类别 | 代表 App |
|------|----------|
| 社交 | 微博、小红书、微信 |
| 购物 | 淘宝、京东、美团 |
| 娱乐 | B 站、QQ 音乐、喜马拉雅 |
| 生活 | 支付宝、高德地图、大众点评 |
| 资讯 | 今日头条、知乎 |
| 阅读 | 七猫小说 |

以下是三个真实演示任务的动图，展示 Agent 从接收指令到完成任务的全过程：

### 演示 1：喜马拉雅 —— 播放有声书并设置循环

> 任务：打开喜马拉雅FM，播放《疯狂动物城2》，设置列表循环播放

![喜马拉雅演示](images/demo_ximalaya.gif)
*动图：Agent 自主打开喜马拉雅 App → 搜索"疯狂动物城2" → 选择播放 → 进入播放设置 → 切换为列表循环模式。全程无需人工干预。*

### 演示 2：七猫小说 —— 批量加入书架

> 任务：打开七猫免费小说，将脑洞/脑洞榜前三名加入书架

![七猫小说演示](images/demo_qimao.gif)
*动图：Agent 打开七猫小说 → 进入排行榜 → 定位"脑洞"分类 → 依次将前三本小说加入书架。涉及多步骤导航和重复操作。*

### 演示 3：微博 —— 搜索天气并发表评论

> 任务：打开微博，搜索杭州天气，并根据当前天气发表评论

![微博演示](images/demo_weibo.gif)
*动图：Agent 打开微博 → 搜索"杭州天气" → 阅读天气信息 → 根据天气内容自动生成评论并发布。展示了理解语境并生成内容的能力。*

## 九、工程落地评估

### 适用场景

| 场景 | 适用度 | 说明 |
|------|--------|------|
| 企业 RPA | ★★★★★ | 替代重复界面操作，ROI 高 |
| 无障碍辅助 | ★★★★★ | 帮助视障/老年用户操作设备 |
| 自动化测试 | ★★★★☆ | AI 遍历 App 功能，发现 UI Bug |
| 个人助手 | ★★★★☆ | 日常任务自动化（订票、比价、信息聚合） |
| 金融/医疗关键操作 | ★★☆☆☆ | 77.6% 成功率仍有失败风险，需人工兜底 |

### 部署建议

- **端侧场景**：选择 2B 模型，配合量化（如 GPTQ/AWQ）可在旗舰手机上运行
- **云端服务**：选择 30B-A3B MoE 模型，激活参数仅 3B，推理成本可控
- **性价比**：8B 模型在多数基准上已超越上代 72B，推荐作为默认选择

### 当前局限

1. **可靠性**：AndroidWorld 77.6% 意味着约 1/4 任务会失败
2. **隐私**：Agent 需要访问屏幕内容，涉及用户隐私保护
3. **个性化**：当前模型缺乏对用户习惯的自适应能力
4. **纯视觉限制**：不结合 Accessibility API 等辅助信息，部分场景准确率受限

## 十、总结

UI-Venus-1.5 用一条清晰的四阶段技术路线，解决了 GUI Agent 从"能看懂"到"能操作"再到"操作得好"的递进问题：

| 阶段 | 解决问题 | 核心数据 |
|------|----------|----------|
| **Mid-Training** | GUI 知识缺失 | 10B tokens → 聚类分离度提升 34% |
| **Offline-RL** | 基础动作优化 | ScreenSpot-Pro +6.9%（8B） |
| **Online-RL** | 真实环境适配 | AndroidWorld +7.5~14.5% |
| **Model Merge** | 多模型部署复杂 | TIES-Merge → 单模型统一全场景 |

从更宏观的视角看，UI-Venus-1.5 标志着 GUI Agent 领域的几个重要转变：

- **从多专家到统一模型**：Model Merge 让一个 checkpoint 搞定全场景
- **从离线到在线**：Online-RL 在真实设备上训练，直接弥合 sim-to-real gap
- **从英文到中文**：40+ 中文 App 深度适配，真正面向国内生态
- **从追求指标到重视可靠性**：Refusal 能力让模型学会说"我做不到"

虽然离"人人都有 AI 手机助手"的终极目标还有距离，但 UI-Venus-1.5 无疑是当前开源 GUI Agent 中最接近生产可用的方案之一。

## 参考资料

1. UI-Venus-1.5 Technical Report: https://arxiv.org/abs/2602.09082
2. GitHub 仓库: https://github.com/inclusionAI/UI-Venus
3. Hugging Face 模型: https://huggingface.co/collections/inclusionai/ui-venus
4. VenusBench-GD: https://arxiv.org/abs/2512.16501
5. 项目官网: https://ui-venus.github.io/UI-Venus-1.5/

*本文基于 UI-Venus-1.5 官方技术报告（arXiv:2602.09082）进行深度解读，所有数据和图表均来自论文原文。*
