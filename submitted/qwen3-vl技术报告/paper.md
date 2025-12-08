# Qwen3-VL 数据工程与训练流程详解

本文档详细解析了 Qwen3-VL 的数据工程策略（涵盖数据搜集、清洗与合成）以及其多阶段的训练流程。

## 1. 数据工程 (Data Engineering)

Qwen3-VL 的数据工程分为预训练（Pre-Training）和后训练（Post-Training）两个主要部分，通过精细的清洗、合成和标注流程，构建了高质量的多模态数据集。

### 1.1 预训练数据构建 (Pre-Training Data)

预训练数据旨在建立通用的视觉-语言理解能力，涵盖了图像、文档、视频、3D、代码等多个领域。

#### (1) 图像描述与图文交错数据 (Image Caption & Interleaved Data)
*   **图像描述 (Image Caption)**:
    *   **来源**: 从网络收集大规模中英文多语言图文对。
    *   **重构 (Recaptioning)**: 使用专门微调的 Qwen2.5-VL-32B 模型对原始文本进行重写，生成更丰富、流畅、包含细节（如对象属性、空间布局）的描述。
    *   **去重与增强**: 基于语义相似度去重；通过视觉嵌入聚类识别稀疏概念并进行针对性增强。
*   **图文交错数据 (Interleaved Text-Image)**:
    *   **清洗**: 基于 Qwen 模型进行领域分类，过滤广告和低价值内容。
    *   **解析**: 使用 Qwen2.5-VL-7B 精确解析排版，将连续页面合并为长达 256K token 的序列，用于长上下文训练。

#### (2) 知识与实体 (Knowledge)
*   **实体覆盖**: 涵盖动物、植物、地标、食品、日常用品等十多个类别。
*   **平衡采样**: 针对现实世界实体的长尾分布，采用基于重要性的采样策略，平衡高频和低频实体。
*   **描述增强**: 将简短的 alt-text 替换为 LLM 生成的丰富描述，包含视觉属性和交互关系。

#### (3) OCR 与文档理解
*   **OCR**: 收集 3000 万内部数据，覆盖 39 种语言（新增 29 种）。使用“粗到细”的流程，结合专业 OCR 模型和 Qwen2.5-VL 进行伪标签生成。
*   **文档解析**: 收集 300 万 Common Crawl PDF 和 400 万内部文档。构建了统一的标注框架（QwenVL-HTML 和 QwenVL-Markdown）。
*   **长文档**: 合并单页文档构建长序列；合成跨页推理的 VQA 数据。

#### (4) 定位与计数 (Grounding & Counting)
*   **Box/Point Grounding**: 整合开源数据集（COCO, Objects365 等）并使用自动合成管道（Qwen2.5-VL + Grounding DINO）生成大规模注释。
*   **计数**: 构建包含直接计数、Box 计数和点计数的综合数据集。
*   **坐标归一化**: 采用 [0, 1000] 的归一化坐标系。

#### (5) 空间理解与 3D 识别
*   **空间理解**: 构建包含关系注释（如“在...左边”）、功能性标签（如“可抓取”）和动作规划查询的数据集。
*   **3D Grounding**: 将室内外场景数据重构为 VQA 格式，使用 9-DoF 3D 边界框标注，并统一到虚拟相机坐标系。

#### (6) 代码与 STEM
*   **多模态代码**: 收集 UI 到 HTML/CSS 转换、SVG 生成、图表到代码等任务数据。
*   **STEM**:
    *   **视觉感知**: 代码渲染几何图形，生成点定位和感知型 VQA 数据。
    *   **推理**: 收集 6000 万 K-12 及本科习题，清洗并标准化格式。合成 1200 万长思维链（Long CoT）推理样本，并进行严格验证。

#### (7) 视频 (Video)
*   **时序理解**:
    *   **密集描述**: 采用“短到长”策略合成连贯的故事级描述。
    *   **时空定位**: 标注对象、动作和人物，增强细粒度理解。
*   **数据平衡**: 涵盖教学、电影、第一视角等多种源，动态调整采样率（FPS）以适应不同长度限制。

#### (8) Agent (GUI & 工具调用)
*   **GUI**: 收集桌面、移动和 Web 环境数据，合成元素描述和密集定位任务。
*   **Function Calling**: 构建多模态函数调用轨迹，包含搜索任务，鼓励模型利用搜索引擎获取知识。

### 1.2 后训练数据构建 (Post-Training Data)

后训练阶段专注于指令遵循、复杂推理和人类偏好对齐。

#### (1) SFT 数据 (Supervised Fine-Tuning)
*   **规模**: 约 120 万样本（1/3 纯文本，2/3 多模态）。
*   **长上下文**: 包含 256K token 长度的数据（长文档、教科书、2小时视频）。
*   **质量过滤**:
    *   **Query 过滤**: 剔除不可验证或模糊的指令。
    *   **Response 过滤**: 规则过滤（格式、重复）+ 模型过滤（使用 Qwen2.5-VL 评分）。

#### (2) Long-CoT 冷启动数据
*   **构建**: 专为 Thinking 模型设计，通过筛选基线模型无法解决或需要视觉信息才能解决的难题（Multimodal Necessity Filtering）。
*   **领域**: 重点关注 STEM、Agent 工作流等需要多步推理的任务。

#### (3) 强化学习数据 (RL Data)
*   **推理 RL**: 30K 高质量查询，通过拒绝采样（Best-of-N）和人工标注构建。
*   **通用 RL**: 针对指令遵循和偏好对齐，构建包含“陷阱”任务（如反直觉计数）的数据集以纠正错误先验。

---

## 2. 训练流程 (Training Pipeline)

Qwen3-VL 的训练分为预训练（4个阶段）和后训练（3个阶段）。

### 2.1 预训练阶段 (Pre-Training)

| 阶段 | 名称 | 训练目标 | 训练模块 | Token量 | 序列长度 | 关键内容 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 0** | **视觉-语言对齐** (Alignment) | 弥合模态差异 | 仅 Merger (MLP) | 67B | 8,192 | 高质量图文对、OCR数据。冻结 Vision Encoder 和 LLM。 |
| **Stage 1** | **多模态预训练** (Multimodal Pre-Training) | 全参数联合训练 | 所有模块 (ViT, Merger, LLM) | ~1T | 8,192 | 混合 VL 数据和纯文本数据。引入 STEM、Grounding、VQA 等多样化数据。 |
| **Stage 2** | **长上下文预训练** (Long-Context) | 扩展上下文能力 | 所有模块 | ~1T | 32,768 | 增加纯文本比例增强长文理解；引入更多视频和 Agent 指令数据。 |
| **Stage 3** | **超长上下文适应** (Ultra-Long Context) | 极限上下文窗口 | 所有模块 | 100B | **262,144** | 专注于长视频和长文档理解任务。 |

**核心架构升级**:
1.  **Interleaved MRoPE**: 均衡频率分布，提升长视频理解。
2.  **DeepStack**: 跨层融合，将 ViT 中间层特征注入 LLM 前几层。
3.  **视频时间戳**: 使用文本 token (e.g., `<3.0s>`) 替代绝对位置编码，更精准。

### 2.2 后训练阶段 (Post-Training)

#### Phase 1: 监督微调 (SFT)
*   **双阶段**: 先在 32K 长度下训练，再扩展至 256K。
*   **双模式**:
    *   **Non-thinking**: 标准指令遵循。
    *   **Thinking**: 使用 CoT 格式数据，显式建模推理过程。

#### Phase 2: 强对弱蒸馏 (Strong-to-Weak Distillation)
*   利用强大的教师模型（如 Qwen3-VL-235B）指导学生模型（如 2B/8B/32B）。
*   **Off-policy**: 学习教师的响应。
*   **On-policy**: 学生生成响应，通过 KL 散度与教师对齐。

#### Phase 3: 强化学习 (Reinforcement Learning)
*   **推理 RL (Reasoning RL)**: 针对 Math、Code 等可验证任务，使用 **SAPO** 算法。
*   **通用 RL (General RL)**: 针对指令遵循和偏好，结合规则奖励和模型奖励（Model-based Reward）。
*   **Thinking with Images**: 针对 Agent 能力的两阶段训练（冷启动 SFT -> 工具集成 RL），引入 Tool-Calling Reward 防止作弊。

---

## 3. 训练流程图 (Training Flowchart)

```mermaid
graph TD
    %% 节点样式定义
    classDef data fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef train fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef model fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;

    subgraph Initialization [初始化]
        ViT[Vision Encoder<br/>SigLIP-2 Dynamic]:::model
        LLM[LLM Backbone<br/>Qwen3]:::model
        Merger[Merger<br/>MLP]:::model
    end

    subgraph PreTraining [Pre-Training (预训练)]
        direction TB
        S0_Data(S0 Data: Image-Caption, OCR<br/>67B Tokens):::data
        S0_Train[Stage 0: Alignment<br/>Train Merger Only<br/>Seq: 8K]:::train
        
        S1_Data(S1 Data: VL + Text Mix<br/>~1T Tokens):::data
        S1_Train[Stage 1: Multimodal Pre-Training<br/>Train All Modules<br/>Seq: 8K]:::train
        
        S2_Data(S2 Data: More Video/Agent<br/>~1T Tokens):::data
        S2_Train[Stage 2: Long-Context<br/>Train All Modules<br/>Seq: 32K]:::train
        
        S3_Data(S3 Data: Long Video/Doc<br/>100B Tokens):::data
        S3_Train[Stage 3: Ultra-Long Context<br/>Train All Modules<br/>Seq: 256K]:::train
    end

    subgraph PostTraining [Post-Training (后训练)]
        direction TB
        SFT_Data(SFT Data: 1.2M Samples<br/>Thinking / Non-thinking):::data
        SFT_Train[SFT: Supervised Fine-Tuning<br/>Phase 1: 32K -> Phase 2: 256K]:::train
        
        Distill[Strong-to-Weak Distillation<br/>Teacher -> Student]:::train
        
        RL_Data(RL Queries & Verifiable Tasks):::data
        RL_Train[Reinforcement Learning<br/>Reasoning RL + General RL<br/>Algorithm: SAPO]:::train
    end

    %% 连接关系
    Initialization --> S0_Train
    S0_Data --> S0_Train
    S0_Train --> S1_Train
    S1_Data --> S1_Train
    S1_Train --> S2_Train
    S2_Data --> S2_Train
    S2_Train --> S3_Train
    S3_Data --> S3_Train
    
    S3_Train --> SFT_Train
    SFT_Data --> SFT_Train
    SFT_Train --> Distill
    Distill --> RL_Train
    RL_Data --> RL_Train

    RL_Train --> FinalModel[Qwen3-VL Final Models<br/>(Instruct / Thinking)]:::model
```

