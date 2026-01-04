# MegaRAG：打破 GraphRAG 的文本次元壁，基于多模态知识图谱的 RAG 新范式

> **一句话总结**：微软 GraphRAG 虽然强大，但它是“盲人”——MegaRAG 首次将**视觉信息（图片/图表/布局）**引入知识图谱构建，通过“**Page-level 并行提取 + 子图 Refinement**”策略，实现了对 PPT、研报、教科书等**富视觉长文档**的深度理解与推理。

![MegaRAG Overview](images/paper_figure_1.png)
*图：MegaRAG 整体架构：从多模态 KG 构建到双路检索生成*

---

## 1. 为什么我们需要 MegaRAG？

在 RAG 领域，2024 年是 GraphRAG 爆发的一年。通过将非结构化文本转化为知识图谱，GraphRAG 解决了传统 RAG 难以处理“全局性问题（Global QA）”和“跨段落推理”的痛点。

然而，现有的 GraphRAG（包括 LightRAG）存在一个致命缺陷：**它们是单模态的（Text-Only）**。
当面对 PDF、PPT、技术手册等**富视觉文档**时：
1.  **视觉丢失**：图表（Chart）、流程图（Diagram）、布局（Layout）信息被 OCR 暴力转为文本或直接丢弃。
2.  **割裂感**：“图”和“文”是分离的，KG 中没有“图片节点”，导致无法回答“根据图 3 的趋势分析...”这类问题。
3.  **长窗口瓶颈**：虽然 Gemini/GPT-4o 支持长窗口，但直接把整本书丢进去不仅贵，而且在处理细粒度视觉细节时容易“幻觉”或“丢失注意力”。

**MegaRAG**（国立台湾大学，2025.11）提出了**MMKG（Multimodal Knowledge Graph）** 方案，核心思路是：**把图片、图表也当做 KG 中的“实体（Entity）”**，并在构建和检索阶段深度融合视觉特征。

---

## 2. 核心架构：如何构建多模态大脑？

MegaRAG 的 Pipeline 分为三个阶段：**MMKG 构建**、**统一索引**、**检索与生成**。最精彩的部分在于它如何低成本地构建高质量多模态图谱。

### 2.1 MMKG 构建：并行提取 + 迭代精修

为了解决长文档的成本和上下文限制，MegaRAG 采用了“分治 + 修正”的策略。

```mermaid
graph TD
    subgraph "Phase 1: Initial Construction"
    Doc[Document] -->|Split| P1[Page 1]
    Doc -->|Split| P2[Page 2]
    P1 -->|MinerU| MM1[Multimodal Input<br>（Text+Image+Layout）]
    P2 -->|MinerU| MM2[Multimodal Input<br>（Text+Image+Layout）]
    
    MM1 -->|MLLM Extract| G1[Page Graph 1]
    MM2 -->|MLLM Extract| G2[Page Graph 2]
    end

    subgraph "Phase 2: Refinement"
    G1 & G2 -->|Merge| G_Init[Initial MMKG G⁰]
    
    G_Init -->|Retrieve Top-K| SubG[Subgraph G_i⁰]
    MM1 & SubG -->|MLLM Refine| G1_Ref[Refined Page Graph]
    
    G1_Ref -->|Merge| G_Final[Final MMKG G¹]
    end
    
    style Doc fill:#f9f,stroke:#333
    style G_Final fill:#bbf,stroke:#333
```

#### 第一步：Page-level 并行提取
将文档按**页**切分，并行喂给 MLLM（如 GPT-4o-mini）。
- **输入**：当前页的 Text + 提取出的 Figure/Table + 完整 Page Image（保留布局）。
- **输出**：局部实体与关系 $(E, R)_i^0$。
- **关键创新**：**图表即实体**。例如，一张“2025 营收趋势图”会被识别为一个 Entity，并与文本中的“营收增长”Entity 建立关系。

#### 第二步：基于子图检索的Refinement —— **核心 Trick**
初步提取的 KG 往往是碎片化的，跨页关系容易丢失。MegaRAG 设计了一个巧妙的 **Refinement** 环节：
1.  **Global Merge**：将所有页的局部图合并为初始图 $\mathcal{G}^0$。
2.  **Subgraph Retrieval**：对于第 $i$ 页，不直接喂全量图（太大了），而是根据当前页的实体，去 $\mathcal{G}^0$ 中检索一个 **Top-K 子图**。
3.  **Context-Aware Refinement**：将“当前页内容” + “检索到的全局子图”再次喂给 MLLM。
    - MLLM 会发现：“哎，这一页提到的‘Project X’在第 10 页也出现过，而且子图里显示它属于‘AI 部门’，那我在这里把关系补上。”
    - **效果**：补全了隐式的 Cross-page 和 Cross-modal 关系（如下图所示）。

![Refinement Effect](MegaRAG：基于多模态知识图谱的检索增强生成_2025.11_台湾国立大学.pdf-ea976211-3e70-4df8-8545-9aebde79fac7/images/77302290a69ddbf3a1486feb5a70c1eb972266ede931be56e490e84c3f671c0c.jpg)
*(待替换图) 图：Refinement 前后对比。Refinement 后，视觉实体（图表）与文本实体之间的潜在关系被补全。*

### 2.2 统一向量空间 (Unified Embedding)

图建好了，怎么检索？文本和图片属于不同模态，传统的 Text Embedding 模型（如 OpenAI ada-003）搞不定图片节点。
MegaRAG 使用了 **GME (General Multimodal Embedder)**（基于 Qwen2-VL-2B 微调）：
- **统一编码**：Text Entity、Visual Entity (Image)、Relation Description 均通过 GME 映射到**同一个 Dense Vector Space**。
- **优势**：支持任意组合的检索（Text-to-Image, Image-to-Text, Text-to-Graph）。

### 2.3 双路检索与生成 (Dual-Pathway Generation)

为了防止模型偏科（只看字不看图，或反之），MegaRAG 采用了**解耦生成**策略：

```mermaid
graph LR
    User[User Query] -->|Extract| KW[Keywords]
    
    subgraph "Dual-Pathway Retrieval"
    KW -->|GME Embed| Vec[Query Vector]
    
    Vec -->|Search KG| Ret_G[Subgraph & Neighbors]
    Vec -->|Search Pages| Ret_P[Top-M Page Images]
    end
    
    subgraph "Two-Stage Generation"
    Ret_G -->|Stage 1| Ans_G[Intermediate<br>KG Answer]
    Ret_P -->|Stage 1| Ans_P[Intermediate<br>Visual Answer]
    
    Ans_G & Ans_P -->|Stage 2: Synthesis| Final[Final Answer]
    end
    
    style User fill:#f9f,stroke:#333
    style Final fill:#bbf,stroke:#333
```

1.  **检索**：
    - **Graph Pathway**：检索 Top-K 相关的实体、关系及其邻居（提供结构化、全局知识）。
    - **Page Pathway**：检索 Top-M 相关的原始页面图片（提供原始视觉细节、布局信息）。

2.  **生成**：
    - **Stage 1 (Intermediate)**：
        - 这里的 Prompt 让模型只看 **KG** 生成一个“逻辑推导版答案”。
        - 同时让模型只看 **Page Images** 生成一个“视觉感知版答案”。
    - **Stage 2 (Final)**：
        - 将上述两个中间答案合并，生成最终回复。

---

## 3. 关键算法与数学表述

### 3.1 页面级图生成
定义文档第 $i$ 页的输入为 $\mathrm{P}_i = \{\mathrm{T}_i, \mathrm{F}_i, \mathrm{B}_i, \mathrm{I}_i\}$，其中 T, F, B, I 分别代表文本、Figure、Table 和完整 Page Image。
图生成函数 $G(\cdot)$ 为：
$$ (\mathrm{E}, \mathrm{R})_i^0 = G(\mathrm{P}_i) $$
这里 MLLM 被 Prompt 引导去识别 Text-to-Text, Text-to-Image 甚至 Image-to-Image 的关系。

### 3.2 Refinement 过程
这是 MegaRAG 的精髓。为了解决 $\mathcal{G}^0$ 的不完整性，定义 Refinement 函数 $R(\cdot)$：
$$ (\mathrm{E}, \mathrm{R})_i^1 = R(\mathrm{P}_i, \mathcal{G}_i^0) $$
其中 $\mathcal{G}_i^0$ 是从全局图 $\mathcal{G}^0$ 中检索出的、与当前页 $\mathrm{P}_i$ 最相关的子图。
> **Insight**：这实际上是一种 **Retrieval-Augmented Construction (RAC)**。在构建 KG 的过程中，就利用 RAG 的思想去检索已有的知识，从而辅助当前的构建。

---

## 4. 工程落地指南

对于算法工程师，复现或落地 MegaRAG 需要关注以下细节：

### 4.1 模型选型
- **LLM/MLLM**：原论文构建和 Refinement 均使用 `GPT-4o-mini`。这是一个 **Cost-Effective** 的选择。对于本地部署，可以用 `Qwen2.5-VL` 或 `InternVL2` 替代。
- **Embedding**：必须使用支持多模态的 Embedding 模型。论文推荐 **GME-Qwen2-VL-2B**。如果没有多模态 Embedder，你的 Visual Entity 将无法被文本 Query 检索到。

### 4.2 坑与注意事项
1.  **PDF 解析是基础**：论文使用了 `MinerU` 工具包来精准提取 Layout、Figure 和 Table。如果解析很烂（比如把图表截断了），后面的 MMKG 质量会直线下降。
2.  **Visual Entity 的描述**：在建图时，不要只存图片的 Embedding。最好让 MLLM 生成一段该图片的 **Caption** 或 **Summary** 作为 Entity 的属性，这样能显著提升 Text-based Retrieval 的召回率。
3.  **Refinement 的开销**：虽然比直接读全文便宜，但 Refinement 意味着要对每一页多做一次 LLM 调用。工程上可以做 Trade-off：只对“信息密度高”或“包含复杂图表”的页面做 Refinement。

### 4.3 性能指标
在 **Global QA**（如“总结整本书的碳排放策略”）场景下，MegaRAG 完胜。
- **Comprehensiveness (全面性)**：比 GraphRAG 高出 **20%+** 的胜率。
- **Multimodal Bench (图表问答)**：在 SlideVQA 等数据集上，Accuracy 达到 **64.85%**，远超 GraphRAG 的 5.22%。这直接证明了引入 Visual Entity 的必要性。

---

## 5. 总结

MegaRAG 的核心贡献在于它打破了 RAG 中“文本”与“视觉”的界限。它告诉我们：
> **不要简单地把 PDF 转成 Markdown 存进向量库。保留视觉结构，将其显式建模为 KG 中的节点，并利用 LLM 的反思能力去修补关系，才是处理复杂文档的终局。**

对于正在构建企业级 RAG（尤其是处理研报、说明书、合同）的团队，MegaRAG 提供了一个非常具有实操性的升级路线：**MinerU 解析 -> 多模态建图 -> 混合检索**。

---
**参考文献**
- *MegaRAG: Multimodal Knowledge Graph-Based Retrieval Augmented Generation, 2025.11*
- *GraphRAG: From Local to Global, Microsoft Research*
- *MinerU: An Open-Source Solution for Precise Document Content Extraction*

