# MegaRAG: Multimodal Knowledge Graph-Based Retrieval Augmented Generation

Chi-Hsiang Hsiao $^{1*}$  Yi-Cheng Wang $^{1*}$  Tzung-Sheng Lin $^{2}$  Yi-Ren Yeh $^{3}$  Chu-Song Chen $^{1}$

$^{1}$ National Taiwan University  $^{2}$ E.SUN Financial Holding Co., Ltd.  $^{3}$ National Kaohsiung Normal University

$^{1}\{r12922048, d13922033, chusong\} @csie.ntu.edu.tw$

2francis-17710@esunbank.com 3yryeh@nknu.edu.tw

# Abstract

Retrieval-augmented generation (RAG) enables large language models (LLMs) to dynamically access external information, which is powerful for answering questions over previously unseen documents. Nonetheless, they struggle with high-level conceptual understanding and holistic comprehension due to limited context windows, which constrain their ability to perform deep reasoning over long-form, domain-specific content such as full-length books. To solve this problem, knowledge graphs (KGs) have been leveraged to provide entity-centric structure and hierarchical summaries, offering more structured support for reasoning. However, existing KG-based RAG solutions remain restricted to text-only inputs and fail to leverage the complementary insights provided by other modalities such as vision. On the other hand, reasoning from visual documents requires textual, visual, and spatial cues into structured, hierarchical concepts. To address this issue, we introduce a multimodal knowledge graph-based RAG that enables cross-modal reasoning for better content understanding. Our method incorporates visual cues into the construction of knowledge graphs, the retrieval phase, and the answer generation process. Experimental results across both global and fine-grained question answering tasks show that our approach consistently outperforms existing RAG-based approaches on both textual and multimodal corpora. Our code is available on GitHub.

# 1 Introduction

Humans naturally integrate multiple modalities such as textual, visual, and layout to fluidly transition between abstract and detailed reasoning. However, multimodal large language models (MLLMs) (Bai et al., 2025; Grattafori et al., 2024; Hurst et al., 2024; Team et al., 2023), despite recent progress, remain limited by constrained context windows,

restricting their ability to deeply process long-form, domain-specific content. E.g., interpreting a history textbook involves both conceptual insights and localized observations, which remains challenging for MLLMs.

On the other hand, RAG can enhance LLMs by providing on-demand access to external knowledge. Early text-based RAG relied on sparse or dense retrieval but struggled with deep, multi-hop reasoning in multimodal documents. Recently, Graph-based RAG introduces structured abstraction via entity-relation graphs. With models like GraphRAG (Edge et al., 2024) and LightRAG (Guo et al., 2025), long-range knowledge retrieval of improved scalability are enhanced through KG-assisted retrieval pipelines. However, these methods excel in text-based multi-hop reasoning but remain constrained in handling complex, multimodal content. Current graph-based RAG methods face some key limitations. First, existing approaches remain unimodal, overlooking visual cues like diagrams, charts or maps, yielding disjointed representations that hinder multimodal reasoning. Additionally, due to context window constraints, most approaches segment documents into independent chunks, extracting entities separately rather than sequentially. This leads to fragmented KGs that miss cross-chunk relationships and key entities.

To our knowledge, while recent studies have explored manually constructed multimodal knowledge graphs (KGs) for RAG-based question answering (Lee et al., 2024), automatically building such KGs for RAG-assisted reasoning remains underexplored. To address this gap, we introduce MegaRAG, a multimodal, graph-based RAG method that enhances cross-modal reasoning.

To better handle the association of different modalities in visual documents, more relations beyond text-to-texts need to be extracted, such as text-to-figures and figure-to-figure relations. Although the parallel-reading-then-combining strategy can

refine entities and relations as in GraphRAG (Edge et al., 2024) and LightRAG (Guo et al., 2025), such refinement still relies on a single chunk while overlooking global document information. To address this limitation, we design a page-based, two-round approach for KG construction. Our solution initiates a KG by simply extracting entity-relation pairs in parallel for every page of a document using existing MLLMs, and the page-based relations are joined to form an initial graph. As the initial KG may not capture the inter-relationship between texts and visual elements sufficiently well, we conduct refinement processes in subsequent stage(s), where the initial KG(s) serve as global guidance to capture subtle relationships often lost in naïve, isolated extraction. In particular, to maintain scalability while incorporating long-range dependencies, we avoid injecting the entire initial KG into the MLLM inputs. Instead, we retrieve only a subgraph of the entire KG for each page, yielding a lightweight yet context-aware input. This strategy enables progressive improvement of the graph's structural coherence, semantic coverage, and cross-modal grounding.

We validate MegaRAG across global (book-level) and local (page/slide-level) QA benchmarks, spanning both text-only and multimodal datasets. Experimental results demonstrate that MegaRAG consistently outperforms strong baselines, particularly in scenarios requiring deep cross-modal integration and structured abstraction. Our contributions are summarized as follows.

- We introduce MegaRAG, an easy-to-use system that automatically constructs Multimodal KGs for visual document question answering with MLLMs.  
- We develop a novel refinement process that enhances cross-modal grounding while addressing limitations in independent KG construction.  
- We demonstrate that MegaRAG outperforms strong baselines on both global and local QA tasks, including GraphRAG and LightRAG.

# 2 Related Work

We briefly review several major directions of RAG: including retrieving information directly from raw data sources such as documents and images, and integrating structured knowledge through KGs.

RAG with Raw Data Source. Early RAG methods (Guu et al., 2020; Lewis et al., 2020) retrieve text chunks from corpora to support answer generation, primarily relying on retrieval strategies either

sparse or dense. Sparse methods exemplified by TF-IDF (Salton et al., 1975) and BM25 (Robertson and Zaragoza, 2009) depend on lexical heuristics to match queries with relevant text segments. They offer computational efficiency but lack deeper semantic comprehension. Dense techniques (Karpukhin et al., 2020; Khattab and Zaharia, 2020; Santhanam et al., 2022) project queries and documents into a shared embedding space, significantly improving retrieval performance of lexical variations. Subsequent works have enhanced this pipeline using LLM recently: HyDE (Gao et al., 2023) generates a hypothetical answer to enrich the retrieval query, Self-RAG (Asai et al., 2024) introduces reflection tokens to enable adaptive retrieval and self-critique within a single LLM, while RQ-RAG (Chan et al., 2024) decomposes the query into sub-queries to improve context coverage. Despite their strong performance on text-based RAG tasks, these methods often struggle with multimodal documents involving complex texts, layouts and visual elements.

Multimodal RAG (MMRAG). To tackle the limitations, more recent studies have focused on multimodal retrieval methods that better retain the structural information of documents. DSE (Ma et al., 2024) treats document screenshots as unified inputs and directly encodes their visual layout, text, and images into a single vector embedding. ColPaLi (Faysse et al., 2025) continues this direction by encoding document images into multi-vector embeddings, effectively capturing fine-grained visual cues. Its variant, ColQwen, replaces the PaLI-Gemma (Beyer et al., 2024) with Qwen2-VL (Wang et al., 2024b) and achieves improved retrieval performance. Moving beyond retrieval, VisRAG (Yu et al., 2025) integrates MLLMs into the full RAG pipeline. Instead of extracting text, it embeds document images directly for retrieval and incorporates them into the generation stage, allowing the model to jointly reason over visual and textual content.

The above methods excel in text-to-image retrieval but fail to solve tasks involving a mixture of single-modality (e.g., text-to-text), cross-modality (e.g., text-to-image), and fused-modality (text+image-to-text+image) retrieval. GME (Zhang et al., 2025) tackles this by introducing a unified embedding model that encodes diverse modality combinations and enables flexible retrieval within a shared representation space.

While these approaches significantly enhance document understanding, they neglect the long-

![](images/243dd469ac5ae0b6a9cfd40170a05f650335fc32ea9daea3ed158b1fc771bb64.jpg)  
(a) Initial MMKG Construction

![](images/d613d003f2fbb60820e6cb8b141ba50f24d54685672df7880bb2d3e489f5bf34.jpg)  
(c) Indexing

![](images/4e839b69459c2a2e56f51433bd0b558606797fb8336cbed5f3f4d7d4ed7c57be.jpg)  
(b) MMKG Refinement

![](images/3be93b36bef6444a30377dc253a1f76879584136909e71501672819615e71021.jpg)  
(d) Retrieval and Answer Generation  
Figure 1: Overview of our MegaRAG for MMKG construction and MMKG-augmented generation. (a) Initial Construction: Multimodal inputs from each page are processed by an MLLM to extract entities and relations  $(E,R)_i^0$  in parallel. The page-level results are then joined by aligning identical entity names and relations, forming the initial document-level MMKG  $\mathcal{G}^0$ . (b) Refinement: Each page retrieves a subgraph  $\mathcal{G}_i^0$  from  $\mathcal{G}^0$  to assist the MLLM in refining the initial graph, yielding  $\mathcal{G}^1$ . (c) Indexing: The refined MMKG is encoded by an MMRAG's retrieval approach into dense entity, relation, and page embeddings for efficient retrieval. (d) Retrieval & Answer Generation: A user query is parsed into low- and high-level keywords for retrieving relevant subgraphs and pages. These are fed into the MLLM for 2-stage answer generation.

range corpus-level structure, which is essential for handling complex, multi-hop QA (Tanaka et al., 2023; Yang et al., 2018).

RAG with Knowledge Graph. Knowledge-augmented generation (Procko and Ochoa, 2024) leverages KGs to provide structured, factual context for LLMs. Within this line of research, SubgraphRAG (Li et al., 2025) enhances efficiency through lightweight scoring mechanisms for subgraph retrieval, while G-Retriever (He et al., 2024) frames subgraph selection as a Steiner Tree optimization problem to support large-scale textual graphs. Gao et al. (Gao et al., 2022) employ a learning-to-rank approach to improve retrieval from KGs. While these methods advance graph-based retrieval, they depend on manually constructed KGs, which are costly to build and require substantial domain expertise. Moreover, static KGs are inherently limited in addressing queries that require corpus-level reasoning beyond fixed graph structures.

To address this limitation, GraphRAG (Edge et al., 2024) proposes building KGs directly from raw text using LLMs, followed by a hierarchical community detection algorithm (Traag et al., 2019) to cluster semantically related nodes. During inference, it prompts the LLM to generate intermediate answers for each community summary, scores them by confidence, and aggregates the top responses into a final answer. Although this enables corpus-level reasoning, it incurs high computational cost due to repeated LLM queries over many community summaries. To improve efficiency, LightRAG (Guo et al., 2025) introduces a two-stage retrieval process: it first extracts local and global keywords from the query, then retrieves relevant nodes and their surrounding subgraphs using dense retrieval. This design reduces the need for repeated LLM inference and significantly improves scalability. which introduces a hybrid RAG framework that alternates between naive and graph-based retrieval. TOG-2 (Ma et al., 2025) introduces a hybrid RAG

method that alternates between dense retrieval and graph reasoning. However, these approaches rely on manually curated KGs, which are costly to construct and limited in coverage.

However, these KG-augmented RAGs rely solely on textual KGs, limiting their ability to handle multimodal content such as images. To overcome this limitation, multimodal knowledge graphs (MMKGs)(Liu et al., 2019; Zhang et al., 2023) enrich KGs by associating entities with aligned visual (e.g., images), numeric (e.g., dates, measurements), and textual descriptions. A representative benchmark(Liu et al., 2019) introduces MMKGs that were constructed by linking overlapping entities via sameAS relations and annotating them with web-crawled images and numeric literals. MMKGs have demonstrated utility across tasks, including KG completion (Mousselly-Sergieh et al., 2018; Xie et al., 2017), recommendation systems (Sun et al., 2020), and image captioning (Zhao and Wu, 2023).

More recently, MMKGs have been integrated into RAG pipelines to support multimodal QA with LLMs. For instance, Lee et al. (Lee et al., 2024) utilized manually constructed MMKGs that encode visual and factual knowledge, enabling LLMs to reason over structured multimodal inputs. Although this study improves performance, it depends on manually built, domain-specific MMKGs that are costly to scale. No existing method using LLMs to construct MMKG for RAG, and current systems still struggle with open-ended reasoning beyond predefined graph structures. Building scalable, automatically constructed MMKGs that support open-domain, MMRAG remains a key challenge.

# 3 Methodology

In this section, we present MegaRAG, covering the iterative construction process of MMKG, graph indexing and retrieval mechanisms, and the answer generation pipeline.

# 3.1 MMKG Construction

We define our MMKG as  $\mathcal{G} = (\mathcal{V},\mathcal{E})$  , where  $\mathcal{V}$  is the set of nodes representing entities, and  $\mathcal{E}$  is the set of edges denoting relations between entities. Given a document consisting of  $N$  pages, we extract four types of content from each page  $i$  : text content  $\mathrm{T}_i$  , figure images  $\mathrm{F}_i$  , table images  $\mathrm{B}_i$  , and the full-page rendered image  $\mathrm{I}_i$  (which captures the layout of the page). These elements are obtained

using an off-the-shelf document analysis tool. We define the input for page  $i$  as  $\mathrm{P}_i = \{\mathrm{T}_i,\mathrm{F}_i,\mathrm{B}_i,\mathrm{I}_i\}$  which serves as input to our graph construction pipeline.

Initial Graph Construction. As illustrated in Figure 1(a), the initial stage involves extracting entities and relations from each page in parallel using a graph generation function  $G(\cdot)$ , which leverages an MLLM guided by a task-specific prompt. The prompt specifies the extraction goals, provides reasoning instructions, and enforces a constrained output format to ensure consistency across pages. In our implementation, GPT-4o-mini serves as the MLLM for the MMKG construction.

Given a multimodal input  $\mathrm{P}_i$ , the graph generation function produces a set of page-level entities and relations  $(\mathrm{E},\mathrm{R})_i^0 = G(\mathrm{P}_i)$ , extracted from both textual and visual content. The MLLM is guided to identify multiple entities within the text and to treat each figure or table as a single, standalone entity. For instance, a bar chart titled "Monthly Website Visitors" may be recognized as an entity and connected to surrounding text discussing user engagement trends. Decorative or non-informative visuals, such as background patterns or logos, are ignored. The full-page image  $\mathrm{I}_i$  is used solely to support spatial reasoning and does not generate entity nodes. Each extracted entity includes a name, a predefined type (e.g., person, organization), and a description. Relations are defined by a source and target entity, a description, and a set of representative keywords.

After generating the set of page-level entities and relations (denoted as  $\{(E,R)_i^0\}_{i = 1}^N$ ), we merge them into a unified MMKG  $\mathcal{G}^0$ . This involves consolidating entity nodes with the same name and merging relation edges with matching source, target, and relation types. During this process, different descriptions associated with the same entity or relation are aggregated to form a richer, more comprehensive representation. Similarly, keywords from multiple occurrences are accumulated.

Graph Refinement and Enrichment. The initial MMKG  $\mathcal{G}^0$  is often incomplete, as many cross-modal entities and relationships may be overlooked during the first-pass extraction. To bridge the gaps, we introduce a refinement stage that enhances graph  $\mathcal{G}^1$ , leveraging both the original multimodal inputs and the preliminary knowledge encoded in  $\mathcal{G}^0$ . The process is illustrated in Figure 1(b).

To efficiently refine MMKG under the MLLM's limited context window, we focus on constructing

lightweight, page-specific subgraphs rather than processing the entire graph. For each page  $i$ , we extract a context-specific subgraph  $\mathcal{G}_i^0$  from  $\mathcal{G}^0$ . In practice, we reuse entity names and relation keywords from the previously extracted page-level output  $(\mathrm{E},\mathrm{R})_i^0$  to retrieve relevant content in  $\mathcal{G}^0$ , reducing redundancy and simplifying subgraph construction. These entity names and relation keywords are encoded into semantic embeddings and efficiently matched against dense vector representations of entities and relations built from initial MMKG. To enrich the local context, the selected nodes and edges are further expanded by including their one-hop neighbors, resulting in a compact yet informative subgraph. A detailed explanation of this graph indexing and retrieval process is provided in Section 3.2.

The refinement process is formalized as  $(\mathrm{E},\mathrm{R})_i^1 = R(\mathrm{P}_i,\mathcal{G}_i^0)$ , where  $R(\cdot)$  is a refinement function that reuses the same MLLM from the initial stage, now guided by a KG-specific refinement prompt. Since the pages remain independent when extracting the entity relationship leveraging the subgraph, the benefit of parallelism is maintained for efficient graph construction. This function identifies missing knowledge in page  $\mathrm{P}_i$  by examining the retrieved subgraph  $\mathcal{G}_i^0$ . Specifically, it detects entities mentioned in the input that are not yet present in the subgraph, as well as implicit relations between entities that are suggested by the content but missing from  $\mathcal{G}_i^0$ .

For example, consider a page where the text states "Electric vehicle sales increased significantly in 2023," and a nearby figure titled "Annual Sales by Vehicle Type" presents a bar chart with a prominent "EV" bar (denoting Electric Vehicles). In the initial extraction, the text and the figure may be treated as independent entities. During refinement, the MLLM infers that the figure visually supports the textual claim and adds a relation such as illustrates or supports between the textual entity "Electric vehicle sales in 2023" and the visual entity "Annual Sales by Vehicle Type."

These newly identified entities and relations are added to the refined set  $(\mathrm{E},\mathrm{R})_i^1$ . The updated page-level outputs  $\{(E,R)_i^1\}_{i = 1}^N$  are then merged to form the enriched MMKG  $\mathcal{G}^1$ . Although we perform only a single refinement step, the process can be applied iteratively to further improve graph completeness. To balance effectiveness and efficiency, we adopt one round of refinement and provide the full prompt formats used for both the initial con

struction and refinement. More details can be found in Appendix B.

# 3.2 Indexing and Retrieval

We adopt a unified retrieval framework that integrates graph structure, represented by entities and relations, along with page images within a shared embedding space to enable seamless cross-modal retrieval. Specifically, we use GME (Zhang et al., 2025), a multimodal encoder that jointly embeds textual and visual inputs. GME aligns all content types, including both textual and visual information, into a common vector space, supporting text-to-text and text-to-image retrieval through a unified representation.

Indexing. Our indexing process encompasses three content types, as illustrated in Figure 1(c): document page images, entities, and relations. Page images are directly encoded using GME without additional preprocessing. For each entity, we concatenate its name with its textual description to form a descriptive sentence, which is then embedded using GME. Relation embeddings are constructed similarly, by combining relation keywords, the names of the source and target entities, and a textual description. All embeddings are stored in separate dense vector stores by type.

Graph Retrieval. To retrieve relevant knowledge, we adopt a dual-level retrieval strategy (Guo et al., 2025) that targets both entities and relations. Given a user query, we first prompt the MLLM to extract two types of keywords: low-level keywords corresponding to specific entities, and high-level keywords that capture broader concepts. These keywords are then embedded by using the same GME model adopted during indexing. Both low-level and high-level keywords are combined into a single keyword list and used to query the entity vector store, retrieving the top- $k$  most relevant entities. In parallel, the top- $k$  most relevant relations, along with their associated source and target entities, are retrieved from the relation store. To further enrich the context, each retrieved entity is expanded by incorporating its one-hop neighbors from  $\mathcal{G}^1$ . The final set of entities and relations serves as input to the downstream reasoning module.

Page Retrieval. Complementary to graph retrieval, we also perform text-to-page(image) retrieval to capture fine-grained visual and layout cues that may be missed by symbolic representations alone. Given the same input query, we retrieve the top- $m$  relevant document pages by comparing text and

<table><tr><td rowspan="2"></td><td colspan="3">Agriculture</td><td colspan="3">CS</td><td colspan="3">Legal</td><td colspan="3">Mix</td></tr><tr><td>NaiveRAG</td><td>Ours</td><td>Tie</td><td>NaiveRAG</td><td>Ours</td><td>Tie</td><td>NaiveRAG</td><td>Ours</td><td>Tie</td><td>NaiveRAG</td><td>Ours</td><td>Tie</td></tr><tr><td>Comprehensiveness</td><td>5.6</td><td>42.7</td><td>51.6</td><td>7.2</td><td>44.8</td><td>48.0</td><td>8.0</td><td>51.2</td><td>40.8</td><td>5.6</td><td>50.4</td><td>44.0</td></tr><tr><td>Diversity</td><td>16.1</td><td>70.2</td><td>13.7</td><td>14.4</td><td>68.0</td><td>17.6</td><td>17.6</td><td>69.6</td><td>12.8</td><td>12.0</td><td>77.6</td><td>10.4</td></tr><tr><td>Empowerment</td><td>12.9</td><td>66.9</td><td>20.2</td><td>22.4</td><td>47.2</td><td>30.4</td><td>20.8</td><td>61.6</td><td>17.6</td><td>20.0</td><td>62.4</td><td>17.6</td></tr><tr><td>Overall</td><td>8.1</td><td>62.1</td><td>29.8</td><td>9.6</td><td>53.6</td><td>36.8</td><td>13.6</td><td>64.0</td><td>22.4</td><td>8.0</td><td>66.4</td><td>25.6</td></tr><tr><td></td><td>GraphRAG</td><td>Ours</td><td>Tie</td><td>GraphRAG</td><td>Ours</td><td>Tie</td><td>GraphRAG</td><td>Ours</td><td>Tie</td><td>GraphRAG</td><td>Ours</td><td>Tie</td></tr><tr><td>Comprehensiveness</td><td>5.6</td><td>64.8</td><td>29.6</td><td>4.0</td><td>68.0</td><td>28.0</td><td>11.2</td><td>60.8</td><td>28.0</td><td>4.0</td><td>59.2</td><td>36.8</td></tr><tr><td>Diversity</td><td>14.4</td><td>76.8</td><td>8.8</td><td>14.4</td><td>72.0</td><td>13.6</td><td>12.8</td><td>75.2</td><td>12.0</td><td>22.4</td><td>59.2</td><td>18.4</td></tr><tr><td>Empowerment</td><td>0.8</td><td>94.4</td><td>4.8</td><td>2.4</td><td>93.6</td><td>4.0</td><td>10.4</td><td>86.4</td><td>3.2</td><td>12.0</td><td>80.0</td><td>8.0</td></tr><tr><td>Overall</td><td>5.6</td><td>82.4</td><td>12.0</td><td>4.0</td><td>79.2</td><td>16.8</td><td>11.2</td><td>80.0</td><td>8.8</td><td>7.2</td><td>70.4</td><td>22.4</td></tr><tr><td></td><td>LightRAG</td><td>Ours</td><td>Tie</td><td>LightRAG</td><td>Ours</td><td>Tie</td><td>LightRAG</td><td>Ours</td><td>Tie</td><td>LightRAG</td><td>Ours</td><td>Tie</td></tr><tr><td>Comprehensiveness</td><td>4.0</td><td>65.6</td><td>30.4</td><td>3.2</td><td>68.8</td><td>28.0</td><td>9.6</td><td>54.4</td><td>36.0</td><td>3.2</td><td>76.8</td><td>20.0</td></tr><tr><td>Diversity</td><td>10.4</td><td>70.4</td><td>19.2</td><td>12.8</td><td>72.0</td><td>15.2</td><td>14.4</td><td>69.6</td><td>16.0</td><td>11.2</td><td>76.8</td><td>12.0</td></tr><tr><td>Empowerment</td><td>4.8</td><td>76.0</td><td>19.2</td><td>10.4</td><td>75.2</td><td>14.4</td><td>12.0</td><td>73.6</td><td>14.4</td><td>4.0</td><td>80.8</td><td>15.2</td></tr><tr><td>Overall</td><td>4.8</td><td>75.2</td><td>20.0</td><td>4.8</td><td>76.8</td><td>18.4</td><td>11.2</td><td>72.0</td><td>16.8</td><td>7.2</td><td>80.0</td><td>12.8</td></tr></table>

Table 1: Performance on the UltraDomain benchmark in terms of win rates  $(\%)$

image embeddings within the shared vector space.

# 3.3 MMKG-augmented Generation

When combined with visual content and MMKG in a single MLLM prompt, this integration can lead to modality bias. The model often disproportionately focuses on one modality, typically text, while underutilizing the other. To address this issue, we propose a two-stage answer generation approach that decouples the processing of textual and visual inputs. Given the retrieved subgraph and the relevant page images, the model first generates two intermediate responses in parallel: one based on the symbolic knowledge graph, and the other on the visual content. In the second stage, the MLLM synthesizes a final answer by integrating both intermediate outputs. Full prompt formats for each generation stage are provided in Appendix B.

# 4 Experiments

In this section, we outline the experimental setups and present the results for our MegaRAG method.

# 4.1 Datasets

Global QA. To evaluate the global (book-level) QA capabilities of MegaRAG, we use two document collections: a textual corpus and a multimodal dataset. For the textual benchmark, we adopt the Ultradomain (Qian et al., 2024) dataset, which contains 428 college-level textbooks across 18 disciplines; we focus on four representative subsets: Agriculture (2,017,886 tokens), Legal (5,081,069 tokens), Computer Science (2,306,535 tokens) and Mixed-Domain (619,009 tokens). Since no standard benchmark exists for multimodal global QA,

we curate a new multimodal benchmark comprising four documents: World History (a world history textbook, 788 pages), Environmental Report (a corporate environmental report slide deck, 422 pages), DLCV (an English lecture slide deck, 1,984 pages), and GenAI (a Chinese lecture slide deck, 594 pages).

As these datasets lack manually labeled global questions, we adopt the question generation strategy from GraphRAG (Edge et al., 2024) and LightRAG (Guo et al., 2025). For each dataset, we use the document outline as input and prompt an LLM to create five synthetic RAG users, each with a profile describing their background and information needs. Each user is assigned five tasks representing distinct information-seeking goals, and each task is used to generate five questions that require a comprehensive understanding of the full document. This process yields 125 global questions per dataset.

Local QA. To evaluate local (slide- or page-level) QA, we use two benchmarks: SlideVQA (Yang et al., 2018) and RealMMBench (Wasserman et al., 2025). SlideVQA includes over 52,000 slides and 14,500 questions covering complex reasoning and numerical understanding, but its scale makes full evaluation computationally expensive. Instead, we construct a subset of 2,000 slides, referred to as SlideVQA (2k). RealMMBench assesses retrieval in multimodal RAG settings using visual-rich, table-heavy, and rephrased queries. RealMMBench consists of four sub-datasets: FinReport (2,687 pages), FinSlides (2,280 pages), TechReport (1,674 pages), and TechSlides (1,963 pages). Additional details are provided in Appendix A.

<table><tr><td rowspan="2"></td><td colspan="3">DLCV</td><td colspan="3">World History</td><td colspan="3">Environmental Report</td><td colspan="3">GenAI</td></tr><tr><td>NaiveRAG</td><td>Ours</td><td>Tie</td><td>NaiveRAG</td><td>Ours</td><td>Tie</td><td>NaiveRAG</td><td>Ours</td><td>Tie</td><td>NaiveRAG</td><td>Ours</td><td>Tie</td></tr><tr><td>Comprehensiveness</td><td>2.4</td><td>67.2</td><td>30.4</td><td>0.0</td><td>81.5</td><td>18.5</td><td>0.0</td><td>72.8</td><td>27.2</td><td>0.0</td><td>95.2</td><td>4.8</td></tr><tr><td>Diversity</td><td>6.4</td><td>84.8</td><td>8.8</td><td>0.0</td><td>96.8</td><td>3.2</td><td>2.4</td><td>92.0</td><td>5.6</td><td>0.0</td><td>98.4</td><td>1.6</td></tr><tr><td>Empowerment</td><td>11.2</td><td>66.4</td><td>22.4</td><td>3.2</td><td>82.3</td><td>14.5</td><td>12.8</td><td>64.0</td><td>23.2</td><td>0.8</td><td>88.0</td><td>11.2</td></tr><tr><td>Overall</td><td>4.8</td><td>75.2</td><td>20.0</td><td>0.0</td><td>89.5</td><td>10.5</td><td>1.6</td><td>80.0</td><td>18.4</td><td>0.0</td><td>98.4</td><td>1.6</td></tr><tr><td></td><td>GraphRAG</td><td>Ours</td><td>Tie</td><td>GraphRAG</td><td>Ours</td><td>Tie</td><td>GraphRAG</td><td>Ours</td><td>Tie</td><td>GraphRAG</td><td>Ours</td><td>Tie</td></tr><tr><td>Comprehensiveness</td><td>0.0</td><td>88.8</td><td>11.2</td><td>0.0</td><td>92.0</td><td>8.0</td><td>0.8</td><td>68.8</td><td>30.4</td><td>0.0</td><td>92.8</td><td>7.2</td></tr><tr><td>Diversity</td><td>3.2</td><td>92.8</td><td>4.0</td><td>1.6</td><td>97.6</td><td>0.8</td><td>7.2</td><td>81.6</td><td>11.2</td><td>0.0</td><td>97.6</td><td>2.4</td></tr><tr><td>Empowerment</td><td>1.6</td><td>95.2</td><td>3.2</td><td>0.0</td><td>96.0</td><td>4.0</td><td>1.6</td><td>93.6</td><td>4.8</td><td>0.0</td><td>100.0</td><td>0.0</td></tr><tr><td>Overall</td><td>0.0</td><td>92.8</td><td>7.2</td><td>0.0</td><td>93.6</td><td>6.4</td><td>0.8</td><td>84.8</td><td>14.4</td><td>0.0</td><td>99.2</td><td>0.8</td></tr><tr><td></td><td>LightRAG</td><td>Ours</td><td>Tie</td><td>LightRAG</td><td>Ours</td><td>Tie</td><td>LightRAG</td><td>Ours</td><td>Tie</td><td>LightRAG</td><td>Ours</td><td>Tie</td></tr><tr><td>Comprehensiveness</td><td>0.0</td><td>78.4</td><td>21.6</td><td>0.0</td><td>89.6</td><td>10.4</td><td>0.0</td><td>80.8</td><td>19.2</td><td>0.0</td><td>92.0</td><td>8.0</td></tr><tr><td>Diversity</td><td>3.2</td><td>90.4</td><td>6.4</td><td>0.0</td><td>95.2</td><td>4.8</td><td>1.6</td><td>92.0</td><td>6.4</td><td>1.6</td><td>92.8</td><td>5.6</td></tr><tr><td>Empowerment</td><td>11.2</td><td>74.4</td><td>14.4</td><td>3.2</td><td>86.4</td><td>10.4</td><td>4.8</td><td>79.2</td><td>16.0</td><td>1.6</td><td>91.2</td><td>7.2</td></tr><tr><td>Overall</td><td>0.8</td><td>84.8</td><td>14.4</td><td>0.0</td><td>90.4</td><td>9.6</td><td>0.0</td><td>90.4</td><td>9.6</td><td>0.0</td><td>94.4</td><td>5.6</td></tr></table>

Table 2: Performance across four multimodal datasets in terms of win rates  $(\%)$  

<table><tr><td rowspan="2">Method</td><td rowspan="2">SlideVQA (2k)</td><td colspan="4">RealMMBench</td></tr><tr><td>FinReport</td><td>FinSlides</td><td>TechReport</td><td>TechSlides</td></tr><tr><td>NaiveRAG</td><td>11.34</td><td>29.66</td><td>14.64</td><td>36.63</td><td>32.94</td></tr><tr><td>GraphRAG (L)</td><td>6.80</td><td>24.50</td><td>11.98</td><td>29.60</td><td>26.81</td></tr><tr><td>GraphRAG (G)</td><td>5.22</td><td>10.08</td><td>3.04</td><td>15.07</td><td>16.03</td></tr><tr><td>LightRAG</td><td>27.66</td><td>31.30</td><td>13.02</td><td>42.74</td><td>31.39</td></tr><tr><td>MegaRAG</td><td>64.85</td><td>39.51</td><td>58.37</td><td>51.51</td><td>60.86</td></tr></table>

Table 3: Performance on SlideVQA (2k) and RealMMBench datasets in terms of Accuracy (%). GraphRAG (L) and GraphRAG (G) denote its local and global search modes.

# 4.2 Baselines and Evaluation Metrics

As our approach is the first one automatically building Multimodal KGs for MMRAG-based question answering, we compare it with several widely adopted RAG baselines, including raw-source-based NaiveRAG, as well as KG-aided methods GraphRAG (Edge et al., 2024), and LightRAG (Guo et al., 2025) that are recent advancements in graph-based RAG. Details of them are provided in Appendix C. For fairness, besides the multimodal benchmark, we compare our method with them using only the textual benchmark too.

Global QA. In the absence of ground truth answers for global (book-level) questions, we follow the LLM-based evaluation strategy from GraphRAG (Edge et al., 2024) and LightRAG (Guo et al., 2025). Model responses are assessed along four qualitative dimensions: Comprehensiveness, Diversity, Empowerment, and Overall, as defined in prior work (Guo et al., 2025). Each response is compared against a baseline in a pairwise setup, with win rates (including ties) reported. Comprehensiveness measures how well the answer covers all aspects of the question; Diversity captures the richness and variety of perspectives; Empowerment reflects how effectively the answer informs and supports user

understanding; Overall provides an aggregate score across the three preceding criteria.

Local QA. For local (slide- or page-level) QA, we evaluate performance by comparing the generated answers against ground truth answers. Specifically, LLM is used to judge whether the generated answer aligns semantically with the reference answer. Accuracy is then computed based on the proportion of correct matches. Further details regarding the evaluation dimensions and procedures are provided in Appendix C.

# 4.3 Implementation Details

To ensure consistency across all RAG methods, we standardize the LLM/MLLM implementation. Response generation and global question generation use GPT-4o-mini, while evaluation uses GPT-4.1-mini for greater robustness. All methods, including NaiveRAG, GraphRAG, and LightRAG, use OpenAI's text-embedding-3-small model for textual embeddings. Textual documents are segmented into 1,200 token chunks with a 100-token overlap. We follow GraphRAG and LightRAG by setting their gleaning parameter to 1. The generation temperature is fixed at 0 across all tasks to reduce output variance.

<table><tr><td rowspan="2"></td><td colspan="3">DLCV</td><td colspan="3">World History</td><td colspan="3">Environmental Report</td><td colspan="3">GenAI</td></tr><tr><td>A1</td><td>MegaRAG</td><td>Tie</td><td>A1</td><td>MegaRAG</td><td>Tie</td><td>A1</td><td>MegaRAG</td><td>Tie</td><td>A1</td><td>MegaRAG</td><td>Tie</td></tr><tr><td>Comprehensiveness</td><td>6.4</td><td>49.6</td><td>44.0</td><td>0.0</td><td>72.0</td><td>28.0</td><td>2.4</td><td>48.8</td><td>48.8</td><td>0.8</td><td>75.2</td><td>24.0</td></tr><tr><td>Diversity</td><td>19.2</td><td>59.2</td><td>21.6</td><td>5.6</td><td>80.8</td><td>13.6</td><td>12.0</td><td>75.2</td><td>12.8</td><td>4.8</td><td>86.4</td><td>8.8</td></tr><tr><td>Empowerment</td><td>23.2</td><td>49.6</td><td>27.2</td><td>5.6</td><td>75.2</td><td>19.2</td><td>24.0</td><td>50.4</td><td>25.6</td><td>6.4</td><td>72.0</td><td>21.6</td></tr><tr><td>Overall</td><td>14.4</td><td>57.6</td><td>28.0</td><td>1.6</td><td>78.4</td><td>20.0</td><td>5.6</td><td>64.0</td><td>30.4</td><td>0.8</td><td>86.4</td><td>12.8</td></tr><tr><td></td><td>A2</td><td>MegaRAG</td><td>Tie</td><td>A2</td><td>MegaRAG</td><td>Tie</td><td>A2</td><td>MegaRAG</td><td>Tie</td><td>A2</td><td>MegaRAG</td><td>Tie</td></tr><tr><td>Comprehensiveness</td><td>0.0</td><td>100.0</td><td>0.0</td><td>0.8</td><td>88.0</td><td>11.2</td><td>0.0</td><td>98.4</td><td>1.6</td><td>0.0</td><td>100.0</td><td>0.0</td></tr><tr><td>Diversity</td><td>0.0</td><td>100.0</td><td>0.0</td><td>0.8</td><td>96.0</td><td>3.2</td><td>0.0</td><td>100.0</td><td>0.0</td><td>0.0</td><td>99.2</td><td>0.8</td></tr><tr><td>Empowerment</td><td>0.0</td><td>100.0</td><td>0.0</td><td>1.6</td><td>86.4</td><td>12.0</td><td>0.0</td><td>98.4</td><td>1.6</td><td>0.0</td><td>94.4</td><td>5.6</td></tr><tr><td>Overall</td><td>0.0</td><td>100.0</td><td>0.0</td><td>0.8</td><td>91.2</td><td>8.0</td><td>0.0</td><td>99.2</td><td>0.8</td><td>0.0</td><td>100.0</td><td>0.0</td></tr><tr><td></td><td>A3</td><td>MegaRAG</td><td>Tie</td><td>A3</td><td>MegaRAG</td><td>Tie</td><td>A3</td><td>MegaRAG</td><td>Tie</td><td>A3</td><td>MegaRAG</td><td>Tie</td></tr><tr><td>Comprehensiveness</td><td>0.8</td><td>52.8</td><td>46.4</td><td>0.0</td><td>67.2</td><td>32.8</td><td>1.6</td><td>58.1</td><td>40.3</td><td>0.0</td><td>96.8</td><td>3.2</td></tr><tr><td>Diversity</td><td>12.0</td><td>72.8</td><td>15.2</td><td>8.0</td><td>79.2</td><td>12.8</td><td>7.3</td><td>80.6</td><td>12.1</td><td>0.8</td><td>97.6</td><td>1.6</td></tr><tr><td>Empowerment</td><td>5.6</td><td>70.4</td><td>24.0</td><td>4.0</td><td>77.6</td><td>18.4</td><td>16.9</td><td>57.3</td><td>25.8</td><td>0.8</td><td>99.2</td><td>0.0</td></tr><tr><td>Overall</td><td>1.6</td><td>61.6</td><td>36.8</td><td>0.8</td><td>75.2</td><td>24.0</td><td>3.2</td><td>70.2</td><td>26.6</td><td>0.0</td><td>98.4</td><td>1.6</td></tr></table>

Table 4: Ablation studies on four multimodal datasets in terms of win rates (\%). A1: text-only graph construction (no visual inputs); A2: disable MMKG retrieval (page retrieval only); A3: replace two-stage generation with single-pass generation.

For multimodal documents, we use the MinerU toolkit (Wang et al., 2024a) to extract text, figures, and tables. MinerU converts PDFs into machine-readable formats while preserving layout and symbols, making it especially effective for processing scientific and technical documents. In MegaRAG, multimodal embeddings are encoded using GMEQwen2-VL-2B (Zhang et al., 2025), which is designed to support a unified embedding space across single-, cross-, and fused-modality retrieval tasks. This allows MegaRAG to flexibly retrieve diverse input types within a consistent representation space. During retrieval, we set the top- $k$  value to  $k = 60$  for graph retrieval steps, following the dual-level retrieval strategy and set the top- $m$  value to  $m = 6$  for the page retrieval described in Section 3.2. For baselines without multimodal support, we retain only the extracted text and process it using the same pipeline as for textual documents. To mitigate inconsistencies, we standardize response prompts across all baselines, so output quality differences stem from model capabilities rather than prompt variations.

# 4.4 Main Results

Textual Global QA. Table 1 shows the results on the UltraDomain benchmark consisting of purely textual documents. As can be seen, across all domains and evaluation dimensions, MegaRAG consistently outperforms the baselines, achieving average win rates of  $59.0\%$  for Comprehensiveness,  $71.4\%$  for Diversity,  $74.8\%$  for Empowerment, and

# 71.8% Overall.

A key contributor to this performance is MegaRAG's graph refinement process. Unlike GraphRAG and LightRAG, which employ gleaning per page, a form of local subgraph refinement, MegaRAG doesn't employ gleaning but constructs and refines a global knowledge graph that captures broader contextual relationships between documents. This approach enhances the expressiveness and coverage of the graph, leading to superior performance.

Multimodal Global QA. An main characteristic of our method is that it can build MMKGs for RAG. In this experiment, we evaluate our MegaRAG on global QA tasks over multimodal documents. As shown in Table 2, MegaRAG outperforms all baselines on four visually rich datasets: World History, Environmental Report, DLCV, and GenAI. It achieves average win rates of  $83.3\%$  for Comprehensiveness,  $92.7\%$  for Diversity,  $84.7\%$  for Empowerment, and  $89.5\%$  Overall. The advantage is particularly evident on slide-based datasets such as DLCV and GenAI, where much of the core content is visual rather than textual. Compared with NaiveRAG and LightRAG, relying primarily on text, MegaRAG delivers stronger results across all evaluation dimensions. These gains stem from MegaRAG's ability to build KGs that jointly encode textual information and visual cues.

Although all baselines in this comparison are text-only models, our ablation study, Section 4.5, further demonstrates that removing MMKG from

MegaRAG leads to a substantial performance drop. Since our MegaRAG reduces to an MMRAG approach when its KG components are removed, this suggests that even vision-capable retrieval methods of MMRAG would struggle to match MegaRAG without multimodal global knowledge integration. Multimodal Local QA. Table 3 shows the accuracy results on SlideVQA (2k) and the four RealMMBench subsets. Across all five test sets, MegaRAG performs more favorably. On SlideVQA (2k), which focuses on fine-grained slide-level reasoning, MegaRAG achieves  $64.85\%$  accuracy, higher than double the score of the strongest baseline. Similar trends are observed in RealMM-Bench. On FinSlides and TechSlides, which feature highly visual and table slide content, MegaRAG achieves  $58.37\%$  and  $60.86\%$ , outperforming the best baseline by 45 and 29 percent, respectively. Even in the more text-heavy FinReport and TechReport subsets, MegaRAG maintains a clear lead with  $39.51\%$  and  $51.51\%$ , surpassing LightRAG by 8 to 9 percent.

# 4.5 Ablation Study

To evaluate the contribution of each major component in MegaRAG, we conduct an ablation study by disabling key modules across the three main stages: MMKG construction, retrieval, and answer generation. In the first setting (A1), we remove all visual inputs, such as figures, tables, and page images, from the graph construction stage, relying solely on textual content. In the second setting (A2), we disable the MMKG-based retrieval mechanism and rely solely on the page retrieval. In the third setting (A3), we replace the two-stage generation pipeline with a single-pass generation setup that simultaneously considers both the subgraph and visual input.

(A1) Text-only graph construction. Removing visual inputs from the graph construction stage leads to a substantial performance decline across all datasets. Without visual entities and relations, the MMKG lacks critical cross-modal context, which is especially detrimental in visually rich domains such as GenAI. For example, the overall win rate on GenAI drops dramatically from  $86.4\%$  to just  $0.8\%$ . These results underscore the importance of incorporating visual elements in MMKG.

(A2) Disable MMKG retrieval. Disabling MMKG-based retrieval and relying solely on page retrieval results in the most severe performance degradation. Across all datasets and evaluation di

mensions, MegaRAG achieves near  $100\%$  win rates when compared to this variant. This clearly demonstrates that structured retrieval over the MMKG is essential for accessing semantically rich and well-connected information, far outperforming page-level retrieval alone.

(A3) Remove two-stage answer generation. Replacing the two-stage generation pipeline with a single-pass setup causes moderate but consistent performance drops. Although this variant still benefits from MMKG construction and retrieval, average win rates decline by 14 to 25 percent. The largest drops appear in Diversity and Empowerment, suggesting that separating textual and visual reasoning before integration helps generate more nuanced and informative answers.

Among the three components, MMKG-based retrieval (A2) proves to be the most critical; its removal leads to a near-complete collapse in performance. Visual inputs in graph construction (A1) also play an important role, particularly for slidecentric documents, though their absence results in less dramatic losses. The two-stage generation strategy (A3) contributes more subtle but consistent gains, especially in generating diverse and empowering responses. Together, these results highlight the complementary value of all three components, with graph-based retrieval emerging as the core driver of MegaRAG's effectiveness.

# 5 Conclusion

In this paper, we introduced MegaRAG, a novel KG-based RAG method that leverages MLLMs to automatically construct MMKGs. MegaRAG improves MLLMs' capabilities over complex, long-form documents by combining textual and visual information into a unified graph representation and refining it through iterative updates. MegaRAG needs no fine-tuning and is easy to use. To reduce modality bias, we adopt a two-stage answer generation process that separately reasons over textual and visual evidence before integrating the results, enabling more comprehensive and balanced responses. Through evaluations on both global and local QA tasks across textual and multimodal datasets, MegaRAG consistently outperforms other competitive RAG approaches. Our work highlights a promising new direction for scalable and interpretable multimodal reasoning in RAG systems.

# References

Akari Asai, Zeqiu Wu, Yizhong Wang, Avirup Sil, and Hannaneh Hajishirzi. 2024. Self-RAG: Learning to retrieve, generate, and critique through self-reflection. In ICLR.  
Shuai Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin Ge, Sibo Song, Kai Dang, Peng Wang, Shijie Wang, Jun Tang, and 1 others. 2025. Qwen2. 5-vl technical report. arXiv preprint arXiv:2502.13923.  
Lucas Beyer, Andreas Steiner, André Susano Pinto, Alexander Kolesnikov, Xiao Wang, Daniel Salz, Maxim Neumann, Ibrahim Alabdulmohsin, Michael Tschannen, Emanuele Bugliarello, and 1 others. 2024. Paligemma: A versatile 3b vlm for transfer. arXiv preprint arXiv:2407.07726.  
Chi-Min Chan, Chunpu Xu, Ruibin Yuan, Hongyin Luo, Wei Xue, Yike Guo, and Jie Fu. 2024. RQ-RAG: Learning to refine queries for retrieval augmented generation. In COLM.  
Darren Edge, Ha Trinh, Newman Cheng, Joshua Bradley, Alex Chao, Apurva Mody, Steven Truitt, and Jonathan Larson. 2024. From local to global: A graph rag approach to query-focused summarization. arXiv preprint arXiv:2404.16130.  
Manuel Faysse, Hugues Sibille, Tony Wu, Bilel Omrani, Gautier Viaud, Céline Hudelot, and Pierre Colombo. 2025. Colpali: Efficient document retrieval with vision language models. In ICLR.  
Hanning Gao, Lingfei Wu, Po Hu, Zhihua Wei, Fangli Xu, and Bo Long. 2022. Graph-augmented learning to rank for querying large-scale knowledge graph. In AACL.  
Luyu Gao, Xueguang Ma, Jimmy Lin, and Jamie Callan. 2023. Precise zero-shot dense retrieval without relevance labels. In ACL.  
Aaron Grattafori, Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Alex Vaughan, and 1 others. 2024. The llama 3 herd of models. arXiv preprint arXiv:2407.21783.  
Zirui Guo, Lianghao Xia, Yanhua Yu, Tu Ao, and Chao Huang. 2025. Lighthrag: Simple and fast retrieval-augmented generation. In Findings of EMNLP.  
Kelvin Guu, Kenton Lee, Zora Tung, Panupong Pasupat, and Mingwei Chang. 2020. Retrieval augmented language model pre-training. In ICLR.  
Xiaoxin He, Yijun Tian, Yifei Sun, Nitesh Chawla, Thomas Laurent, Yann LeCun, Xavier Bresson, and Bryan Hooi. 2024. G-retriever: Retrieval-augmented generation for textual graph understanding and question answering. In NeurIPS.  
Aaron Hurst, Adam Lerer, Adam P Goucher, Adam Perelman, Aditya Ramesh, Aidan Clark, AJ Ostrow, Akila Welihinda, Alan Hayes, Alec Radford, and 1

others. 2024. Gpt-4o system card. arXiv preprint arXiv:2410.21276.  
Vladimir Karpukhin, Barlas Oguz, Sewon Min, Patrick SH Lewis, Ledell Wu, Sergey Edunov, Danqi Chen, and Wen-tau Yih. 2020. Dense passage retrieval for open-domain question answering. In EMNLP.  
Omar Khattab and Matei Zaharia. 2020. Colbert: Efficient and effective passage search via contextualized late interaction over bert. In SIGIR.  
Junlin Lee, Yequan Wang, Jing Li, and Min Zhang. 2024. Multimodal reasoning with multimodal knowledge graph. In ACL.  
Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Kuttler, Mike Lewis, Wen-tau Yih, Tim Rocktäschel, and 1 others. 2020. Retrieval-augmented generation for knowledge-intensive nlp tasks. In NeurIPS.  
Mufei Li, Siqi Miao, and Pan Li. 2025. Simple is effective: The roles of graphs and large language models in knowledge-graph-based retrieval-augmented generation. In ICLR.  
Ye Liu, Hui Li, Alberto Garcia-Duran, Mathias Niepert, Daniel Onoro-Rubio, and David S. Rosenblum. 2019. Mmkg: Multi-modal knowledge graphs. In ESWC.  
Shengjie Ma, Chengjin Xu, Xuhui Jiang, Muzhi Li, Huaren Qu, Cehao Yang, Jiaxin Mao, and Jian Guo. 2025. Think-on-graph 2.0: Deep and faithful large language model reasoning with knowledge-guided retrieval augmented generation. In ICLR.  
Xueguang Ma, Sheng-Chieh Lin, Minghan Li, Wenhu Chen, and Jimmy Lin. 2024. Unifying multimodal retrieval via document screenshot embedding. In EMNLP.  
Hatem Mousselly-Sergieh, Teresa Botschen, Iryna Gurevych, and Stefan Roth. 2018. A multimodal translation-based approach for knowledge graph representation learning. In SEM.  
Tyler Thomas Procko and Omar Ochoa. 2024. Graph retrieval-augmented generation for large language models: A survey. In AIxSET.  
Hongjin Qian, Peitian Zhang, Zheng Liu, Kelong Mao, and Zhicheng Dou. 2024. Memorag: Moving towards next-gen rag via memory-inspired knowledge discovery. arXiv preprint arXiv:2409.05591.  
Stephen Robertson and Hugo Zaragoza. 2009. The probabilistic relevance framework: Bm25 and beyond. Found. Trends Inf. Retr.  
G. Salton, A. Wong, and C. S. Yang. 1975. A vector space model for automatic indexing. ACM.

Keshav Santhanam, Omar Khattab, Jon Saad-Falcon, Christopher Potts, and Matei Zaharia. 2022. Colbertv2: Effective and efficient retrieval via lightweight late interaction. In ACL.  
Rui Sun, Xuezhi Cao, Yan Zhao, Junchen Wan, Kun Zhou, Fuzheng Zhang, Zhongyuan Wang, and Kai Zheng. 2020. Multi-modal knowledge graphs for recommender systems. In CIKM.  
Ryota Tanaka, Kyosuke Nishida, Kosuke Nishida, Taku Hasegawa, Itsumi Saito, and Kuniko Saito. 2023. Slidevqa: A dataset for document visual question answering on multiple images. In AAAI.  
Gemini Team, Rohan Anil, Sebastian Borgeaud, Jean Baptiste Alayrac, Jiahui Yu, Radu Soricut, Johan Schalkwyk, Andrew M Dai, Anja Hauth, Katie Millican, and 1 others. 2023. Gemini: a family of highly capable multimodal models. arXiv preprint arXiv:2312.11805.  
Vincent A Traag, Ludo Waltman, and Nees Jan Van Eck. 2019. From louvain to leiden: guaranteeing well-connected communities. Scientific reports.  
Bin Wang, Chao Xu, Xiaomeng Zhao, Linke Ouyang, Fan Wu, Zhiyuan Zhao, Rui Xu, Kaiwen Liu, Yuan Qu, Fukai Shang, and 1 others. 2024a. Mineru: An open-source solution for precise document content extraction. arXiv preprint arXiv:2409.18839.  
Peng Wang, Shuai Bai, Sinan Tan, Shijie Wang, Zhihao Fan, Jinze Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin Ge, and 1 others. 2024b. Qwen2vl: Enhancing vision-language model's perception of the world at any resolution. arXiv preprint arXiv:2409.12191.  
Navee Wasserman, Roi Pony, Oshri Naparstek, Adi Raz Goldfarb, Eli Schwartz, Udi Barzelay, and Leonid Karlinsky. 2025. Real-mm-rag: A real-world multimodal retrieval benchmark. In ACL.  
Ruobing Xie, Zhiyuan Liu, Huanbo Luan, and Maosong Sun. 2017. Image-embodied knowledge representation learning. In *IJCAI*.  
Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William Cohen, Ruslan Salakhutdinov, and Christopher D Manning. 2018. Hotpotqa: A dataset for diverse, explainable multi-hop question answering. In EMNLP.  
Shi Yu, Chaoyue Tang, Bokai Xu, Junbo Cui, Junhao Ran, Yukun Yan, Zhenghao Liu, Shuo Wang, Xu Han, Zhiyuan Liu, and 1 others. 2025. Visrag: Vision-based retrieval-augmented generation on multi-modality documents. In ICLR.  
Ningyu Zhang, Lei Li, Xiang Chen, Xiaozhuan Liang, Shumin Deng, and Huajun Chen. 2023. Multimodal analogical reasoning over knowledge graphs. In ICLR.

Xin Zhang, Yanzhao Zhang, Wen Xie, Mingxin Li, Ziqi Dai, Dingkun Long, Pengjun Xie, Meishan Zhang, Wenjie Li, and Min Zhang. 2025. Gme: Improving universal multimodal retrieval by multimodal llms. In CVPR.  
Wentian Zhao and Xinxiao Wu. 2023. Boosting entity-aware image captioning with multi-modal knowledge graph. IEEE Transactions on Multimedia.

In the Appendix, we present the Datasets, Implementation Details, and Baselines & Evaluations in Appendices A, B, and C, respectively.

<table><tr><td>Dataset</td><td>Documents</td><td>Pages</td><td>Figures</td><td>Tables</td><td>Text Tokens</td></tr><tr><td colspan="6">Ultradomain</td></tr><tr><td>Agriculture</td><td>12</td><td>-</td><td>-</td><td>-</td><td>2,017,886</td></tr><tr><td>Computer Science (CS)</td><td>10</td><td>-</td><td>-</td><td>-</td><td>2,306,535</td></tr><tr><td>Legal</td><td>94</td><td>-</td><td>-</td><td>-</td><td>5,081,069</td></tr><tr><td>Mix</td><td>61</td><td>-</td><td>-</td><td>-</td><td>619,009</td></tr><tr><td colspan="6">Multimodal Documents</td></tr><tr><td>DLCV</td><td>18</td><td>1,984</td><td>2,018</td><td>75</td><td>136,032</td></tr><tr><td>Environmental Report</td><td>5</td><td>422</td><td>416</td><td>122</td><td>229,014</td></tr><tr><td>GenAI</td><td>20</td><td>594</td><td>686</td><td>33</td><td>55,913</td></tr><tr><td>World History</td><td>1</td><td>788</td><td>468</td><td>5</td><td>441,764</td></tr><tr><td colspan="6">SlideVQA</td></tr><tr><td>SlideVQA (2k)</td><td>100</td><td>2,000</td><td>1,581</td><td>139</td><td>119,776</td></tr><tr><td colspan="6">RealMMBench</td></tr><tr><td>FinReport</td><td>19</td><td>2,687</td><td>411</td><td>2,963</td><td>1,583,640</td></tr><tr><td>FinSlides</td><td>65</td><td>2,280</td><td>730</td><td>1,842</td><td>123,891</td></tr><tr><td>TechReport</td><td>17</td><td>1,674</td><td>928</td><td>337</td><td>535,415</td></tr><tr><td>TechSlides</td><td>62</td><td>1,963</td><td>2,254</td><td>119</td><td>138,766</td></tr></table>

Table 5: Datasets statistics used in our experiments. The Ultradomain benchmark is purely textual documents; hence, entries for pages, figures, and tables are marked with a dash  $(-)$  to indicate not applicable.

# A Datasets

We provide an overview of the datasets in our experiments and dataset statistics in Table 5.

# A.1 Dataset Statistics

The Ultradomain benchmark (Qian et al., 2024) comprises 428 college-level textbooks spanning 18 academic disciplines. For this study, we focus on the four representative subsets:

Agriculture dataset. Consisting of 12 textbooks and 2.02 million text tokens, this subset covers topics such as beekeeping, hive management, crop cultivation, and disease prevention in modern agriculture. Computer Science (CS) dataset. Containing 10 textbooks and 2.31 million tokens, the CS subset emphasizes key topics in algorithms, data structures, artificial intelligence, machine learning, and real-time data analytics. Legal dataset. Comprising 94 textbooks and totaling 5.08 million tokens. It spans a wide range of legal topics, including corporate restructuring, regulatory compliance, financial governance, and case law analysis. Mixed-Domain (Mix) dataset. A diverse collection of 61 textbooks totaling 620,000 tokens. This subset includes literary works, philosophical essays, biographies, and cultural-historical studies.

The global QA multimodal datasets are derived from publicly available documents:

Deep Learning for Computer Vision (DLCV) dataset. Comprising 18 slide decks, this dataset includes 1,984 pages, 2,018 figures, 75 tables, and 136,000 tokens. The content is drawn from a deep learning and computer vision course, covering image classification, object detection, and societal impacts of AI. Environmental Report dataset. Consisting of 5 corporate sustainability reports, this dataset includes 422 pages, 416 figures, 122 tables, and 229,000 tokens. It documents environmental strategies from Google $^{2}$ , Apple $^{3}$ , Microsoft $^{4}$ , Meta $^{5}$ , and NVIDIA $^{6}$  (FY24 Sustainability Report), including goals for carbon reduction and renewable energy. Generative AI (GenAI) dataset. This dataset comprises 20 lecture slide decks $^{7}$  (in Chinese), with 594 pages, 686 figures, 33 tables, and 55,900 tokens. Topics focus on generative AI, including transformer architectures, generation techniques, cross-modal applications, and ethical considerations in large-scale AI systems. World History dataset. A textbook $^{8}$  comprising 788 pages, 468 figures, 5 tables, and 442,000 tokens. It traces global developments from prehistory to 1500 CE, covering early civilizations, empires, religious movements, and intercultural exchanges. SlideVQA (2k). SlideVQA (Tanaka et al., 2023) includes over 52,000 slides and 14,500 questions covering complex reasoning and numerical understanding, but its scale makes full evaluation computationally expensive. Instead, we construct a subset of SlideVQA, which consists of 2,000 educational slides, featuring 1,581 figures, 139 tables, and 120,000 tokens.

The RealMMBench (Wasserman et al., 2025) is designed to evaluate retrieval performance in realistic multi-modal RAG scenarios, and contains four subsets:

FinReport. This subset includes 19 long-form table-heavy financial reports from IBM, totaling 2,687 pages, 411 figures, 2,963 tables, and 1.58 million tokens. FinSlides. Comprising 65 corporate financial slide decks, this subset spans 2,280 pages,

730 figures, 1,842 tables, and 124,000 tokens. It presents a more visual but still data-rich format for financial information, including quarterly earnings briefings, strategic outlooks, and KPI dashboards. TechReport. This collection includes 17 technical reports with 1,674 pages, 928 figures, 337 tables, and 535,000 tokens. Documents are sourced from specialized domains such as enterprise hardware and storage systems. TechSlides. Featuring 62 technical presentation slide decks, this subset comprises 1,963 pages, 2,254 figures, 119 tables, and 139,000 tokens. It has the highest figure density across RealMMBench, which conveys technical concepts through diagrams and flowcharts.

# A.2 Global Question Generation

To generate global questions, we utilize the prompt shown in Figure 5. This prompt guides the MLLM (GPT-4o-mini) to first identify representative user profiles and their associated tasks, then generate questions that require a comprehensive understanding of the dataset.

# B Implementation Details

# B.1 Prompts Used in MegaRAG

MMKG construction. For MMKG construction in Section 3.1, we use prompts to guide GPT-4o-mini in extracting structured knowledge from multimodal document inputs. The prompt used in the initial graph construction stage is shown in Figure 2. For graph refinement, we employ a separate prompt designed to identify missing or implicit connections. This prompt, illustrated in Figure 3.

MMKG-augmented Answer Generation. For MMKG-augmented answer generation (Section 3.3), we adopt a two-stage prompting strategy. In the first stage, GPT-4o-mini is guided to generate intermediate answers separately: one based on the visual page (Figure 4(a)) and another based on the retrieved subgraph (Figure 4(b)). In the second stage, a follow-up prompt combines these intermediate responses to produce the final answer (Figure 4(c)).

# B.2 Retrieval and Generation Details

MegaRAG leverages the General Multimodal Embedder (GME) (Zhang et al., 2025) to encode entities, relations, and page images within a unified embedding space. GME is built upon the Qwen2-VL architecture, a MLLM capable of processing text, images, or combined text-image inputs. It

supports a broad range of retrieval tasks, including single-modality retrieval (e.g., text-to-text, image-to-image), cross-modality retrieval (e.g., text-to-image, image-to-text), and fused-modality retrieval (e.g., text with image to text with image). To generate embeddings, GME uses the final hidden state of the last token as the representation of the input. GME's strength lies in its flexibility and generalization capability, making it well-suited for MegaRAG, which requires seamless integration of both text-to-text and text-to-page (image) retrieval tasks.

GME Encoding Time. In our pipeline, the GME-Qwen2-VL-2B encoder is executed locally to process both text and image inputs. All encoding is performed on a single NVIDIA RTX 3090 GPU with 24GB of VRAM. Due to memory constraints, we limit GME to encoding two page images concurrently, with an average processing time of approximately 0.97 seconds per image.

During graph retrieval in the MMKG refinement stage, as described in Section 3.1, we retrieve the top 120 entities and relations from the initial MMKG and concatenate them into a single string (as illustrated in Figure 3, subgraph). We then truncate this string to a maximum of 32,000 tokens. The truncated string is then used to prompt the MLLM to identify missing entity-relation pairs that were not captured in the initial stage. We experimented with both larger and smaller retrieval sizes and found that retrieving 120 entities and relations provides the best balance between global coverage of the MMKG and input length constraints.

![](images/bbdefb7281b2486571bfbc21459c34e3c20c00f14bd22d1580b37dd5a5ddc125.jpg)  
Figure 2: Prompt for extracting entities and relations during the initial construction of the MMKG.

![](images/bb9f4b3c8a0e207e3a880f022b2ad759846d6d88c73289f97e4810ebb8367df7.jpg)  
Figure 3: Prompt for MMKG refinement stage.

You are a helpful assistant responding to user query about Document Images provided below.

# ---Goal---

Generate a concise response based on Document Images and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Document Images, and incorporating general knowledge relevant to the Document Images. Do not include information not provided by Document Images.

When handling content with timestamps:

1. Each piece of content has a "created_at" timestamp indicating when we acquired this knowledge  
2. When encountering conflicting information, consider both the content and the timestamp. 3. Don't automatically prefer the most recent content use judgment based on the content  
3. Don't automatically prefer the most recent content use judgment based on the context. 4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

# --Response Rules--

- Target format and length: Multiple Paragraphs  
Target format and length: Multiple Printings - Use markdown formatting with appropriate section headings  
- Please respond in English.  
- Ensure the response maintains continuity with the conversation.  
If you don't know the answer, just say so.  
- Do not include information not provided by the Document Images.

# (a) Page Image Intermediate Answer Generation

You are a helpful assistant.

# --Goal--

Generate a concise response based on Knowledge Base and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Knowledge Base, and incorporating general knowledge relevant to the Knowledge Base. Do not include information not provided by Knowledge Base.

When handling relationships with timestamps:  
1. Each relationship has a "created at" timestamp indicating when we acquired this knowledge 2. If the relationship is not created, then  
2. When encountering conflicting relationships, consider both the semantic content and the timestamp 3.Don't automatically prefer the most recently created relationships use judgment based on the content  
3. Don't automatically prefer the most recently created relationships - use judgment based on the context  
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

# --Knowledge Base--

{context_data}

# --Response Rules--

- Target format and length: Multiple Paragraphs  
- Use markdown formatting with appropriate section headings  
- Please respond in English  
- Ensure the response maintains continuity with the conversation history.  
- If you don't know the answer, just say so.
- Do not make anything up. Do not include information not provided by the Knowledge Base.

# (b) Knowledge Graph Intermediate Answer Generation

You are a professional assistant responsible for answering questions based on both a knowledge graph and visual information extracted from document images containing relevant textual and visual content (e.g., scanned pages, slides, charts, or forms).

You are provided with a user query and two independent answers:  
1. An answer based on the knowledge graph  
2. An answer based on the document images.

Your task is to analyze the user's query and integrate the two provided answers into a single comprehensive response. Do not omit any relevant points from either source. When the answers conflict or provide complementary insights, use grounded reasoning to reconcile them. If the knowledge graph provides explicit facts, do not override them unless contradicted by strong visual evidence.

# Please respond in English.

# --Query--

{query}

# --Input Answers---

--**Answer from Knowledge Graph**  
{kg_answer}

-**Answer from Document Images**:

{image_answer}

# --Goal--

Generate a concise response to the query that incorporates all relevant information from both Answers from the Knowledge Graph and the Document Images. If you don't know the answer, just say so. Do not make anything up or include information where the supporting evidence is not provided.

When handling information with timestamps  
1. Each piece of information (both relationships and content) has a "created_at" timestamp indicating when we acquired this knowledge.  
2. When encountering conflicting information, consider both the content/relationship and the timestamp.  
3. Don't automatically prefer the most recent information - use judgment based on the context.  
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps.

# --Response Rules--

- Target format and length: Multiple Paragraphs  
- Generate a final answer that integrates both inputs.  
- Use markdown formatting with appropriate section headings.  
- Organize answer in sections focusing on one main point or aspect of the answer  
- List up to 5 most important reference sources at the end under a "References" section. Clearly indicate whether each source is from Knowledge Graph (KG) or Document Content (DC), using this format: [KG/DC]. Source content.  
Source is from Knowledge Graph (KG) of Document Content (DC), using: - Ensure the response maintains continuity with the conversation history.  
- If you don't know the answer, just say so. Do not make anything up.  
- Do not include information not provided by the inputs.

# (c) Final Answer Generation

Figure 4: Prompts for MMKG-augmented answer generation. (a) Generates an intermediate answer from the retrieved pages. (b) Generates an intermediate answer from the retrieved MMKG subgraph. (c) The final answer is produced by combining both intermediate responses.

# C Baselines and Evaluation

# C.1Baselines

We evaluate MegaRAG against two widely used graph-based RAG baselines: GraphRAG and LightRAG, as well as a commonly adopted non-graph baseline, NaiveRAG. To ensure a fair comparison, we set the generation temperature to 0 across all models. Below, we provide a detailed overview of each method along with its specific settings for reference.

NaiveRAG. Serving as a standard baseline among RAG systems, NaiveRAG divides the input document into multiple text chunks, which are then encoded into a vector space using text embeddings. At query time, relevant chunks are retrieved based on the similarity between their embeddings and the query representation.

GraphRAG. GraphRAG begins by segmenting the input text into chunks and extracting entities and relationships to construct a graph. This graph is subsequently partitioned into communities at multiple levels. During retrieval, GraphRAG identifies entities mentioned in the query and synthesizes answers by referencing summaries of the corresponding communities. Compared to traditional RAG approaches, GraphRAG offers a more structured and high-level understanding of the document.

LightRAG. LightRAG is a variant of GraphRAG. It is designed to reduce computational overhead while enhancing retrieval quality through a dual-level retrieval mechanism. This design improves both efficiency and effectiveness, offering a better balance between performance and resource usage compared to GraphRAG.

# C.2 Evaluation

Global QA. To evaluate model performance on global (book-level) questions, where no gold-standard answers are available, we conduct pairwise comparative evaluations between MegaRAG and baseline models. Responses are assessed along three qualitative dimensions: Comprehensiveness, Diversity, and Empowerment, as well as an overall rating that reflects performance across all criteria.

Each evaluation instance presents a question alongside two competing answers, one from a baseline model and one from MegaRAG. We employ GPT-4.1-mini as the evaluator to compare the two responses, select a winner for each dimension, and provide brief justifications. Comprehensiveness

measures how thoroughly the answer addresses all aspects of the question. Diversity evaluates the richness and variety of perspectives presented. Empowerment assesses how effectively the answer enhances user understanding and supports informed decision-making. The full evaluation prompt used in this process is shown in Figure 6 (a).

Local QA. For local (slide- or page-level) QA, where reference answers are available, we use GPT-4.1-mini to assess answer correctness. Each instance includes a question, the model's response, and the corresponding ground truth. The LLM judge evaluates whether the response is semantically consistent with the reference, regardless of surface phrasing. The output is a binary label (yes or no) accompanied by a brief explanation. Accuracy is calculated as the proportion of responses judged correct. The evaluation prompt is shown in Figure 6 (b).

# C.3 Ablation Study on Using GPT-4o-mini Only (without MMRAG)

To ensure that GPT-4o-mini has not been exposed to our evaluation datasets during pretraining, and to confirm that it cannot answer questions solely by relying on its internal knowledge, we conduct an additional ablation study. Specifically, we compare MegaRAG against a retrieval-free baseline where answers are generated using GPT-4o-mini without access to any external context or retrieved information. As shown in Table 6, MegaRAG consistently outperforms the retrieval-free baseline, highlighting the value of combining retrieval with multimodal knowledge to enhance answer quality.

<table><tr><td rowspan="2"></td><td colspan="3">DLCV</td><td colspan="3">World History</td><td colspan="3">Environmental Report</td><td colspan="3">GenAI</td></tr><tr><td>4o-mini</td><td>MegaRAG</td><td>Tie</td><td>4o-mini</td><td>MegaRAG</td><td>Tie</td><td>4o-mini</td><td>MegaRAG</td><td>Tie</td><td>4o-mini</td><td>MegaRAG</td><td>Tie</td></tr><tr><td>Comprehensiveness</td><td>0</td><td>94.4</td><td>5.6</td><td>0</td><td>98.4</td><td>1.6</td><td>0</td><td>96.8</td><td>3.2</td><td>0</td><td>99.2</td><td>0.8</td></tr><tr><td>Diversity</td><td>0</td><td>95.2</td><td>4.8</td><td>0</td><td>99.2</td><td>0.8</td><td>3.2</td><td>92.8</td><td>4</td><td>0.8</td><td>97.6</td><td>1.6</td></tr><tr><td>Empowerment</td><td>7.2</td><td>78.4</td><td>14.4</td><td>0</td><td>93.6</td><td>6.4</td><td>1.6</td><td>90.4</td><td>8</td><td>1.6</td><td>95.2</td><td>3.2</td></tr><tr><td>Overall</td><td>0</td><td>96</td><td>4</td><td>0</td><td>99.2</td><td>0.8</td><td>2.4</td><td>97.6</td><td>2.4</td><td>0</td><td>99.2</td><td>0.8</td></tr></table>

Table 6: Compare MegaRAG with using only GPT-4o-mini in terms of win rates  $(\%)$

![](images/8bbd745bd22ba89021185af4993cc1e19920f9c2d36aa461fe62ce8d5ed90ca0.jpg)  
Figure 5: (a) Prompt used for global question generation. (b) Example global questions.

```txt
You will evaluate two answers to the same question based on three criteria: Comprehensiveness, Diversity, and Empowerment.  
- Comprehensiveness: How much detail does the answer provide to cover all aspects and details of the question?  
- Diversity: How varied and rich is the answer in providing different perspectives and insights on the question?  
- Empowerment: How well does the answer help the reader understand and make informed judgments about the topic?
```

Here are the two answers:  
Answer 1 Start:  
{answer1}  
Answer 1 End  
Answer 2 Start:  
```txt
For each criterion, choose the better answer (either Answer 1 or Answer 2) and explain why. Then, select an overall winner based on these three categories. Here is the question: {query}
```

{answer2}  
Answer 2 End  
Evaluate both answers using the three criteria listed above and provide detailed explanations for each criterion.  
Output your evaluation in the following JSON format:  
```javascript
"Comprehensiveness": { "Winner": ["Answer 1 or Answer 2"], "Explanation": ["Provide explanation here"]}; "Diversity": { "Winner": ["Answer 1 or Answer 2"], "Explanation": ["Provide explanation here"]}; "Empowerment": { "Winner": ["Answer 1 or Answer 2"], "Explanation": ["Provide explanation here"]}; "Overall Winner": { "Winner": ["Answer 1 or Answer 2"], "Explanation": ["Summarize why this answer is the overall winner based on the three criteria"]};
```

# (a) Prompt for Pairwise Global QA Evaluation

You are given a question, the model's response, and the correct answer. Your task is to evaluate whether the model's response correctly answers the question based on the correct answer provided.

Please follow this format in your output:

```jsonl
{"is correct": "yes" or "no", "reason": "Your explanation of why the response is correct or incorrect."}
```

Make sure your judgment is based only on the given answer, and explain your reasoning clearly and concisely.

Here is the input: Question: {query}

Model's Response: {result}

Correct Answer: {answer}

# (b) Prompt for Locl QA Evaluation

Figure 6: Overview of the global and local QA evaluation prompts.

# C.4 Case Studies

We present two case studies demonstrating the benefits of our MMKG refinement stage in improving knowledge extraction from visually rich documents. These examples show how refinement enhances multimodal grounding and enables the recovery of global, cross-page relations.

# Example of enhanced multimodal relations.

In the initial MMKG stage shown in Figure 7, entities such as Estimated Global Emissions and Earth Network of Electric Grids are extracted from figure images, but their connections to textual entities are missing. After refinement, these visual entities are correctly linked to the 1 Gigaton Aspiration.

# Example of enhanced cross-page relations.

We deominate that cross-page relations can be recovered after the refinement stage in the example shown in Figure 8. By leveraging the provided MMKG subgraph, our method successfully links the visual entity Renewable Energy Purchasing vs. "Total Electricity" to the cross-page entity Total Electricity Consumption.

# Comparative Analysis.

Further examples are provided in Tables 7, 8, 9, 10 to compare our MegaRAG with GraphRAG and LightRAG. As shown in the respective LLM judgement, our approach consistently outperforms the baselines across four evaluation metrics: comprehensiveness, diversity, empowerment, and overall.

![](images/06b5d61bb1f67b11675b3678d37998cc24ad61bcae0b2d4c33fdd9a811e6803d.jpg)  
(a) Example Slide Page

![](images/17551e255e04c1d0d26f7ef42955bf4f7e92f7a833e328047e7f075ef2cd26c6.jpg)  
(b) Page-level MMKG from Initial Stage

![](images/6028065ea9099e4cdb369fbf8888245b7695e7c8e57f3d77a41e5fb0d62f808c.jpg)  
(c) Page-level MMKG from Refinement Stage  
Figure 7: Example of enhanced multimodal relations. (a) A slide page from an environmental report. (b) Page-level MMKG generated in the initial stage. (c) Page-level MMKG from the refinement stage.

![](images/0b79d0620c6ebf19ef6987912c1bd2b879d3136592c98ebe9417498b730f17b5.jpg)  
(a) Example Slide Page

![](images/77302290a69ddbf3a1486feb5a70c1eb972266ede931be56e490e84c3f671c0c.jpg)

![](images/0efb47b3df32ff1da2145076ac87149be07b22a2a49ca80e640bed116ddc43f7.jpg)  
(b) Page-level MMKG from Initial Stage  
Figure 8: Example of enhanced cross-page relations. (a) A slide page from an environmental report. (b) Page-level MMKG generated in the initial stage. (c) Page-level MMKG from the refinement stage.

Question 1: What specific carbon reduction strategies are most effective across companies?

# MegaRAG

Effective Carbon Reduction Strategies Across Companies: The pursuit of effective carbon reduction strategies is critical for companies aiming to mitigate their environmental impact and achieve sustainability goals. Both knowledge from the knowledge graph and insights derived from document images reveal a comprehensive landscape of strategies being implemented by various organizations, highlighting key themes such as emissions reduction, renewable energy initiatives, supply chain management, and investment in carbon removal technologies.

Decarbonizing Energy Sources: Leading companies like Meta, Microsoft, and Google are shifting to renewable energy. For instance, Meta has contracted over 11,700 MW of renewable energy to match  $100\%$  of its electricity use. Google has matched its energy use with  $100\%$  renewables for seven years, collaborating with the First Movers Coalition.

Emissions Reduction Focus: Meta targets a  $42\%$  reduction in Scope 1 and 2 emissions by 2031. Apple has cut product energy use by over  $70\%$  since 2008. Google and LinkedIn are also working on operational emissions.

Supplier Engagement: Microsoft promotes sustainability in its supply chain, encouraging local sourcing and renewable energy use by vendors.

Investment in Carbon Removal: Companies like Google and Meta are investing in direct air capture and forest restoration. Apple and Google focus on high-quality carbon credits. Microsoft leads collaborative efforts like Carbon Call to improve reporting standards.

Conclusion: Effective strategies span emissions reduction, renewable energy, supplier engagement, and carbon removal investments.

# GraphRAG

Effective Carbon Reduction Strategies Across Companies: Companies are pursuing a range of strategies:

Renewable Energy: NVIDIA aims for  $100\%$  renewable electricity by FY2025. Apple is committed to carbon neutrality by 2030.

Scope 3 Emissions: Google, Apple, and Meta focus on tracking and reducing value-chain emissions.

Climate Innovation: Microsoft's Climate Innovation Fund invested \(761M in 2023 to support new technologies.

Circular Economy: Apple incorporates recycled materials into products; Meta operates on  $100\%$  renewable energy since 2020.

Supplier Programs: Apple's Supplier Energy Efficiency Program helps reduce emissions across the supply chain.

Summary: Key strategies include renewables, Scope 3 management, innovation funding, circularity, and supplier engagement.

# LLM Judgement

Comprehensiveness - Winner: MegaRAG

Answer 1 gives a broader, more detailed view, linking specific strategies, company actions, and goals. Answer 2, while informative, is more concise.

Diversity - Winner: MegaRAG

Answer 1 presents a wider variety of strategies, including both direct and indirect emissions, and a broader range of carbon removal methods.

Empowerment - Winner: MegaRAG

Answer 1 empowers readers with clear explanations, real examples, and reasoning behind each strategy. Answer 2 lacks the same level of depth.

Overall - Winner: MegaRAG

Answer 1 is the most comprehensive, diverse, and empowering of the two answers.

Table 7: Case (1) Study: Comparison between MegaRAG and GraphRAG.

Question 1: What specific carbon reduction strategies are most effective across companies?

# MegaRAG

Due to space constraints, the detailed responses are presented in Table 7 (MegaRAG).

# LightRAG

Effective Carbon Reduction Strategies Across Companies: Many companies, particularly in the technology sector, are implementing various carbon reduction strategies to achieve sustainability and mitigate climate change. Here are some of the most effective strategies identified across major organizations like Apple, Google, and Meta:

Commitment to Renewable Energy: Companies like Apple have achieved  $100\%$  renewable electricity for operations and are extending this to their supply chains. Meta and Google also match their energy use with renewables to reduce operational emissions.

Carbon Removals and Offsetting: Apple and Meta invest in high-quality carbon removal projects to handle residual emissions and support their net-zero goals.

Efficiency Improvements: Microsoft improves energy efficiency in data centers. Apple implements operational efficiency practices to lower emissions.

Supply Chain Engagement: Apple's programs help suppliers adopt low-carbon technologies. Meta's Net Zero Supplier Engagement Program supports suppliers in meeting emission reduction targets.

Innovative Technologies and Practices: Companies are adopting low-carbon technologies and nature-based solutions to reduce emissions in production and processes.

Transparency and Reporting: Apple and Meta publicly report their emissions and progress, increasing accountability and stakeholder trust.

Conclusion: These strategies show a unified effort among tech companies to reduce emissions through renewable energy, efficiency, supplier collaboration, and innovation.

# LLM Judgement

# Comprehensiveness - Winner: MegaRAG

Answer 1 delivers a more detailed view of carbon reduction strategies. It covers decarbonization, emissions targets, supplier engagement, carbon removal, and collaborative efforts, all backed by specific examples and data. Answer 2 provides a solid overview but lacks the same level of depth and specificity.

# Diversity - Winner: MegaRAG

Answer 1 explores a wider range of approaches, from operational reductions to nature- and tech-based carbon removal, and cross-company collaborations. Answer 2 touches on similar themes but offers fewer perspectives and less nuance.

# Empowerment - Winner: MegaRAG

By including concrete commitments, rationales, and cross-sector initiatives, Answer 1 helps readers better understand and assess real-world strategies. Answer 2 is clear but more general, offering less actionable insight.

# Overall - Winner: MegaRAG

Answer 1 stands out for its depth, breadth, and practical value. It consistently outperforms Answer 2 across all criteria, making it a more comprehensive and informative response for understanding corporate carbon reduction efforts.

Table 8: Case (1) Study: Comparison between MegaRAG and LightRAG.

Question 2: How can generative models be used to augment image classification datasets?

# MegaRAG

# Utilizing Generative Models for Augmenting Image Classification Datasets

Generative models, such as Generative Adversarial Networks (GANs) and Variational Autoencoders (VAEs), enhance image classification datasets by increasing both size and quality.

Data Generation: These models create synthetic images that resemble real data. GANs can alter image attributes without extra labeling, while VAEs sample new images from the original data distribution—crucial for small datasets.

Enhancing Feature Learning: Variations created by generative models help classifiers recognize subtle differences and learn more discriminative features, improving accuracy under different conditions like lighting or orientation.

Insight Extraction: Generative models reveal hidden data structures in high-dimensional spaces—beneficial in fields like medical imaging—helping researchers understand data with limited labeled samples.

Robust Augmentation: Advanced augmentation techniques, including super-resolution and colorization, not only create new data but also enhance robustness against overfitting by exposing models to more diverse representations.

Simulation and Adaptation: They can simulate diverse environments for applications like robotics and reinforcement learning, allowing broader scenario training for better generalization.

# GraphRAG

Generative models such as GANs and VAEs augment image classification datasets by generating synthetic images, improving dataset size and diversity. This process addresses class imbalance and boosts model robustness.

GANs use a generator and discriminator to produce realistic images, which are helpful when the dataset is small or imbalanced. VAEs encode input data into a latent space and sample from it to create new images, increasing dataset variation.

Generative models can also generate labeled data, reducing the need for expensive manual annotation. Basic augmentation like color shifts, noise addition, and rotations enhances generalization.

By integrating generative models early in the data pipeline, models learn from both real and synthetic images, leading to higher accuracy and reduced overfitting.

# LLM Judgement

# Comprehensiveness - Winner: MegaRAG

Answer 1 offers a more complete explanation, discussing synthetic generation, feature learning, data structure analysis, augmentation robustness, and simulation. Answer 2 focuses mainly on synthetic data and standard augmentation.

# Diversity - Winner: MegaRAG

Answer 1 explores multiple dimensions—from feature learning to simulation—while Answer 2 concentrates on class imbalance and dataset enlargement.

# Empowerment - Winner: MegaRAG

Answer 1 gives readers a clearer picture of how and why generative models are effective, with practical examples and diverse use cases. Answer 2 is helpful but more limited in depth.

# Overall - Winner: MegaRAG

Answer 1 outperforms Answer 2 in all aspects, providing broader insights and more actionable information for leveraging generative models in dataset augmentation.

Table 9: Case (2) Study: Comparison between MegaRAG and GraphRAG.

Question 2: How can generative models be used to augment image classification datasets?

# MegaRAG

Due to space constraints, the detailed responses are presented in Table 9 (MegaRAG).

# LightRAG

# Augmenting Image Classification Datasets with Generative Models

Generative models enhance image classification datasets by producing synthetic images that resemble original data, which is crucial for improving model robustness and generalization when data is limited.

Data Generation: GANs and VAEs can learn the data distribution and sample new images, expanding dataset size and diversity.

Creating Diverse Samples: Through transformations like rotation, scaling, color shifts, and noise, these models generate varied images, helping prevent overfitting.

Enhancing Underrepresented Classes: Generative models can target low-sample classes to balance the dataset.

Improving Model Stability: Adding synthetic data introduces broader scenarios, improving training stability and real-world performance.

Applications: Augmented datasets aid CNNs (e.g., AlexNet) and fine-tuning in transfer learning tasks for better classification results.

# LLM Judgement

# Comprehensiveness - Winner: MegaRAG

Answer 1 provides broader and more detailed coverage, including feature learning, high-dimensional insight extraction, advanced augmentation (e.g., super-resolution), and simulation. Answer 2 covers core concepts well but lacks these deeper applications.

# Diversity - Winner: MegaRAG

Answer 1 discusses a wider array of technical and application perspectives—ranging from data generation to domain-specific use. Answer 2 focuses more narrowly on basic augmentation and dataset balance.

# Empowerment - Winner: MegaRAG

Answer 1 better equips readers by showing *how and why* generative models enhance data. It includes multiple use cases and explains strategic benefits. Answer 2 is more concise, with fewer actionable insights.

# Overall - Winner: MegaRAG

Answer 1 wins across all criteria. Its comprehensive scope, nuanced techniques, and practical guidance make it more informative and valuable overall.

Table 10: Case (2) Study: Comparison between MegaRAG and LightRAG.