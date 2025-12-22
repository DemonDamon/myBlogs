# DataFlow: An LLM-Driven Framework for Unified Data Preparation and Workflow Automation in the Era of Data-Centric AI

Hao Liang*,†, Xiaochen Ma*,†, Zhou Liu*,†, Zhen Hao Wong*, Zhengyang Zhao*, Zimo Meng*, Runming He*, Chengyu Shen*, Qifeng Cai*, Zhaoyang Han*, Meiyi Qiang*, Yalin Feng*, Tianyi Bai*, Zewei Pan, Ziyi Guo, Yizhen Jiang, Jingwen Deng, Qijie You, Peichao Lai, Tianyu Guo, Chi Hsu Tsai, Hengyi Feng, Rui Hu, Wenkai Yu, Junbo Niu, Bohan Zeng, Ruichuan An, Lu Ma, Jihao Huang, Yaowei Zheng, Conghui He, Linpeng Tang, Bin Cui, Weinan E, Wentao Zhang‡

$^{1}$ Peking University,  $^{2}$ Institute for Advanced Algorithms Research, Shanghai,  $^{3}$ OriginHub Technology,  $^{4}$ OpenDataLab, Shanghai Artificial Intelligence Laboratory,  $^{5}$ LLaMA-Factory Team

The rapidly growing demand for high-quality data in Large Language Models (LLMs) has intensified the need for scalable, reliable, and semantically rich data preparation pipelines. However, current practices remain dominated by ad-hoc scripts and loosely specified workflows, which lack principled abstractions, hinder reproducibility, and offer limited support for model-in-the-loop data generation. To address these challenges, we present DataFlow, a unified and extensible LLM-driven data preparation framework. DataFlow is designed with system-level abstractions that enable modular, reusable, and composable data transformations, and provides a PyTorch-style pipeline construction API for building debuggable andizable dataflows. The framework consists of nearly 200 reusable operators and six domain-general pipelines spanning text, mathematical reasoning, code, Text-to-SQL, agentic RAG, and large-scale knowledge extraction. To further improve usability, we introduce DataFlow-Agent, which automatically translates natural-language specifications into executable pipelines via operator synthesis, pipeline planning, and iterative verification. Across six representative use cases, DataFlow consistently improves downstream LLM performance. Our math, code, and text pipelines outperform curated human datasets and specialized synthetic baselines, achieving up to  $+3\%$  execution accuracy in Text-to-SQL over SynSQL,  $+7\%$  average improvements on code benchmarks, and 1-3 point gains on MATH, GSM8K, and AIME. Moreover, a unified 10K-sample dataset produced by DataFlow enables base models to surpass counterparts trained on 1M Infinity-Instruct data. These results demonstrate that DataFlow provides a practical and high-performance substrate for reliable, reproducible, and scalable LLM data preparation, and establishes a system-level foundation for future data-centric AI development.

*Equal Contribution, †Project Leader, ‡Corresponding author

Correspondence: wentao.zhang@pku.edu.cn  
Source Code: https://github.com/OpenDCAI/DataFlow  
Dataset: https://huggingface.co/datasets/OpenDCAI/dataflow-instruct-10k  
Codebase Documentation: https://opendcai.github.io/DataFlow-Doc/

# Contents

1 Introduction 4  
2 Background and Related Works 6

2.1 Data in LLM Development 6  
2.2 Data Preparation for LLMs 6  
2.3 Existing LLM Data Preparation Systems 6

3 DataFlow System Overview 7

3.1 Goals and Design Philosophy 7  
3.2 System Scope and Positioning 7  
3.3 System Workflow 8

4 Framework Design and Architecture 8

4.1 Global Storage Abstraction and Operator Interaction 9  
4.2 Hierarchical Programming Interfaces 9

4.2.1 LLM Serving API 9  
4.2.2 Operator Programming Interface 10  
4.2.3 Prompt Template Interface 11  
4.2.4 Pipeline Composition Interface 11

4.3Operator Categorization 12  
4.4 DataFlow-Ecosystem 13

5 DataFlow-Agent 14

5.1 AgentRoles 14  
5.2 Intelligent Pipeline Recommendation 15  
5.3 Summary 15

6 Use Cases & Pipelines 16

6.1 Case Study: Text-to-SQL Data Pipeline in DATAFLOW 16

6.1.1 Operators 16  
6.1.2 Pipelines 17  
6.1.3 DATAFlow-support Mechanism 18

7 Experiments 18

7.1 Text Data Preparation 19

7.1.1 Experimental Setting 19  
7.1.2 Experimental Results 19

7.2 Math Reasoning Data Preparation 20

7.2.1 Experimental Setting 20  
7.2.2 Experimental Results 21

7.3 Code Data Preparation 21

7.3.1 Experimental Setting 21  
7.3.2 Experimental Results 22

7.4 Text-to-SQL Data Preparation 22

7.4.1 Experimental Setting 22  
7.4.2 Experimental Results 23

7.5 AgenticRAG Data Preparation 24

7.5.1 Experimental Setting 24  
7.5.2 Experimental Results 24

7.6 Knowledge Extraction 25

7.6.1 Experimental Setting 25  
7.6.2 Experimental Results 26

7.7 Unified Multi-Domain Data Preparation with DataFlow 26

7.7.1 Experimental Setting 26  
7.7.2 Experimental Results 27

7.8 Agentic Orchestration 28

7.8.1 Experimental Setting 28  
7.8.2 Experimental Results 29

8 Conclusion 29

A Author Contributions 35

# 1 Introduction

Large language models (LLMs) have rapidly evolved from research prototypes to foundational infrastructure across natural language processing and beyond. Since OpenAI introduced the GPT [1] family through large-scale human annotation and ignited the era of large language models (LLMs), scaling-law studies [26, 55] have consistently demonstrated that data quality and quantity are central to model performance. As model scales continue to grow and downstream tasks become increasingly complex, the size and semantic diversity of training corpora have expanded dramatically [29, 67]. Modern LLM development now relies on multi-stage, semantics-heavy data preparation pipelines that integrate synthetic, refinement, filtering, and domain-specific transformation across trillions of tokens [6, 47, 61].

However, despite the critical role of high-quality data, data preparation for LLMs remains fragmented and largely unstandardized. Most practitioners still rely on ad-hoc scripts and loosely standardized workflows, which lack explicit dataflow abstractions, well-defined atomic operators, or any form of pipeline-level optimization. The absence of a unified and programmable paradigm makes pipelines difficult to reproduce, extend, or compare across projects [6, 47, 48]. This problem is amplified by the trend toward increasingly fine-grained post-training tasks, such as instruction tuning, chain-of-thought generation, or function calling, where both the semantic richness and the semantic accuracy in data preparation are essential for achieving precise task-level model behavior [62, 72].

In response to this fragmentation, several systems have recently emerged with the goal of standardizing LLM data curation. Frameworks such as NeMo Curator [47] and Data-Juicer [6] offer substantial functionality—including captioning, rewriting, classification, and multimodal processing—and have significantly improved the efficiency of large-scale corpus construction. Yet these systems remain fundamentally extraction- and filtering-oriented, and their abstractions provide limited support for expressing iterative, model-in-the-loop generative workflows with fine-grained semantic control. As a result, they are ill-suited for pipelines in which data synthesis and multi-step semantic refinement are central rather than auxiliary.

This limitation is becoming increasingly consequential. LLMs are no longer only consumers of data, but also producers. Because large-scale human annotation is prohibitively expensive, recent work heavily leverages LLM-based data synthesis workflows to construct high-quality corpora at scale [3]. Multiple recent reports show that, in many regimes, carefully synthesized data can outperform even high-quality selected data [60, 69], further underscoring the importance of LLM-driven generation workflows.

Given these trends, we argue that a unified framework for LLM data preparation must elevate LLM-driven data synthesis to a first-class, programmable dataflow abstraction. Such a framework should: (1) provide fine-grained, composable operators for model-in-the-loop generation and semantic refinement; (2) support explicit, verifiable pipeline definitions that serve as an inspectable, domain-agnostic open-source protocol for LLM data preparation—much like how torch(nn).Module standardizes model composition in deep learning; (3) remain backend-agnostic to integrate different LLM engines and storage backends; and (4) enable principled workflow composition, reuse, and optimization across models, tasks, and domains, while further supporting agent-driven automatic workflow construction. Taken together, these requirements signal a shift in data preparation—from post-hoc corpus cleaning toward LLM-centric workflows that build high-fidelity, semantically rich, and task-aligned synthetic corpora through iterative synthesis and refinement.

Motivated by this shift, we introduce DATAFLOW, a unified and automated LLM-driven framework for end-to-end LLM data preparation, with a DATAFLOW-AGENT that allows users to compose pipelines directly from natural-language specifications. DATAFLOW places LLMs at the center of the operator ecosystem: most operators are LLM-driven, with a small number implemented using heuristics or small models. The framework provides over 180 operators organized into four categories—generation, evaluation, filtering, and refinement—and includes more than 90 reusable prompt templates that enable operator-level composition and consistent behavior across tasks. Using these primitives, DATAFLOW includes a set of state-of-the-art (SOTA) synthesis pipelines that span mathematical reasoning, raw text, code, Text-to-SQL, agentic RAG-style data, and large-scale QA extraction from web or PDF corpora. All pipelines are expressed within DATAFLOW's common abstractions and require no task-specific glue code, adhering to a generate-evaluate-filter workflow augmented with targeted refinement stages.

To ensure usability, extensibility, and long-term maintainability, DATAFLOW adopts a PyTorch-like programming interface that exposes its core abstractions, global storage, LLM serving, operators, prompt templates, and pipelines, through modular Python classes and functions. This code-first design avoids complex YAML or shell-based configuration schemes and provides an IDE-friendly development workflow, including code completion and reliable navigation. Beyond the core library, operators, prompt templates, and pipelines can be developed outside the main repository and packaged as standalone Python modules, enabling practitioners to publish and reuse domain-specific components as first-class DATAFLOW-EXTENSIONS. To support this ecosystem, DATAFLOW includes a Command-Line Interface (CLI) toolchain that scaffolds new extension packages, from operator stubs to full pipeline repositories, standardizing development practices and lowering the barrier to community contribution. Finally, DATAFLOW-Agent serves as an agentic orchestration layer that translates natural-language specifications into executable pipelines and can automatically synthesize and debug new operators when needed, further accelerating the construction of scalable and semantically rich LLM-driven data preparation workflows.

Extensive experiments on six DATAFLOW-implemented pipelines show that our design philosophy is effective across diverse data preparation scenarios, consistently producing high-quality training data. Across all settings, the resulting DATAFLOW datasets match or even surpass SOTA baselines, including curated human datasets, specialized synthetic workflows, and the strong Qwen2.5-Instruct series. For example, DATAFLOW-synthesized mathematical reasoning data yields 1-3 point gains over high-quality synthetic baselines [28, 43] on MATH, GSM8K, and AIME; our Text-to-SQL pipelines achieve over  $+3\%$  execution-accuracy improvements compared with the 2.5M-sample SynSQL corpus [37] while using less than 0.1M training examples; and DATAFLOW-based code pipelines deliver over  $7\%$  average improvements relative to widely used public code instruction datasets [5, 63].

Moreover, by combining DATAFLOW-generated text, math, and code data into a unified corpus, DATAFLOW-INSTRUCT-10K, we find that training on only 10K samples enables Qwen2-base and Qwen2.5-base to surpass models trained on 1M Infinity-Instruct [39] instances, while approaching the performance of their corresponding Qwen-Instruct model. This demonstrates that DATAFLOW can produce domain-diverse supervision of sufficiently high quality to yield substantial gains in data efficiency.

Together, these results demonstrate that DATAFlow is not only an end-to-end system for LLM-based data preparation, but also a comprehensive operator and algorithm library and an open, user-friendly protocol framework. Built around six SOTA template pipelines and a large collection of reusable operators, DATAFlow offers a unified foundation for LLM-centric data construction, enabling principled, semantically rich, and scalable workflows that improve programmability, reproducibility, and data quality across domains.

Overall, our key contributions are summarized as follows:

- A unified LLM-driven data preparation framework. We propose DATAFLOW, a unified system for LLM data preparation built on composable abstractions and an LLM-first operator execution model.  
- A rich and extensible operator-pipeline ecosystem. DATAFLOW provides nearly 200 reusable operators and six SOTA template pipelines covering text, mathematical reasoning, code, Text-to-SQL, agentic RAG data, and large-scale QA extraction.  
- A developer- and open-source-friendly programming model. Through a PyTorch-like API, IDE native tooling, and plugin-style extensibility via Python packages, DATAFLOW enables reproducible experimentation, easy customization, and community-driven extensions to form DATAFLOW-ECOSYSTEM  
- An agentic orchestration layer for automated pipeline construction. DATAFLOW-Agent composes executable pipelines from natural-language intent, lowering the barrier to building scalable and semantically rich LLM-driven workflows  
- Extensive empirical validation and open-source data release. Experiments across six pipelines show that DATAFlow-generated data consistently improves downstream LLM performance and data efficiency. We additionally release a high-quality, multi-domain dataset produced entirely with DATAFLOW to support further research and benchmarking.

# 2 Background and Related Works

# 2.1 Data in LLM Development

The development of LLMs involves several key stages, among which training is particularly crucial, as the model learns fundamental linguistic patterns from large-scale corpora. During this stage, the model is exposed to vast amounts of text data from various domains, enabling it to acquire a broad understanding of language.

Consequently, the quality and diversity of training data directly impact the model's ability to generalize effectively across different contexts [19, 38]. Recently, the rapid development of large language models has brought about a substantial increase in the volume of training data [1, 57]. In this scenario, the quality and quantity of data become even more paramount.

High-quality data can significantly enhance model performance [44]. As the volume of data increases, ensuring high data quality becomes more challenging, as it requires additional resources for data cleaning, selection, and annotation [3]. Poor-quality data can cause models to learn incorrect patterns and produce inaccurate predictions. Furthermore, insufficient data diversity may result in models performing well in specific domains but exhibiting poor generalization in cross-domain tasks. Additionally, distributional shifts in the data can exacerbate model over-reliance on training distributions, diminishing their applicability in real-world scenarios.

# 2.2 Data Preparation for LLMs

As disclosed by the above discussion, data preparation is a crucial step in training LLMs, significantly impacting the model's performance and generalization capabilities. With the continuous expansion of LLM scales, the complexity and efficiency of data preparation have become key research focuses. However, although systems like Apache Spark [71], Dask [52], and Hadoop [13, 20, 65] are powerful for large-scale Extract-Transform-Load (ETL), they are not a good fit for modern LLM data preparation. These frameworks can, in principle, run semantic cleaning by calling LLMs or embedding models as user-defined functions, but they provide no native support for model-in-the-loop processing, GPU-efficient batching, or token-level text operations. More importantly, their built-in operators focus on structured data and offer very limited functionality for unstructured text, meaning that essential steps—such as tokenization, language detection, document segmentation, semantic dedduplication, or safety filtering—must be implemented manually with ad-hoc User-Defined Functions (UDFs). This leads to significant overhead and engineering complexity, making general big-data engines inadequate for the large-scale, semantics-heavy pipelines required for LLM corpus construction.

LLM-based methods have been widely used in data quality evaluation and data selection. For instance, MoDS [15] leverages DeBERTa for scoring and retaining high-quality data, while Alphagasus [7] uses ChatGPT to score data accuracy. Other studies have employed GPT-4 for data rewriting and quality improvement. For a comprehensive overview, refer to the data for LLM survey [3].

# 2.3 Existing LLM Data Preparation Systems

Recent work increasingly approaches LLM training data preparation as a first-class systems problem. Table 1 summarizes the distinguishing characteristics of the major frameworks.

NeMo Curator [47] is an open-source, GPU-accelerated library from NVIDIA that offers modular pipelines for large-scale LLM data curation, including data download and extraction (e.g., Commoncrawl, arXiv, Wikipedia), language identification, text cleaning, heuristic and learned quality filtering, domain and toxicity classification, document- and semantic-level dedduplication, privacy filtering, and even synthetic data generation, all built on Dask/RAPIDS and designed to scale to multi-node, multi-GPU environments.

Data-Juicer [6] is a "one-stop" data processing system that abstracts LLM data recipes into composable operators: the original system already provides  $50+$  operators for constructing and evaluating text data mixtures, while the 2.0 version extends this to  $100+$  operators across text, image, video, and audio, supporting analysis, cleaning, synthesis, annotation, and post-training data pipelines with tight integration to Ray and HuggingFace Datasets.

Table 1 High-level comparison of existing data preparation systems for LLM.  

<table><tr><td>Dimension</td><td>Data-Juicer [6]</td><td>NeMo Curator [47]</td><td>DataFlow (ours)</td></tr><tr><td>Primary focus</td><td>Filtering / Cleaning</td><td>Large-scale Curation</td><td>LLM-driven Synthesis + Refinement</td></tr><tr><td>Programming model</td><td>Config-based Recipes</td><td>Component-based Pipelines</td><td>PyTorch-like Operators &amp; Pipelines</td></tr><tr><td>LLM integration</td><td>Partial (some gen ops)</td><td>Minimal (mainly filtering)</td><td>First-class Serving + Templates</td></tr><tr><td>Automation</td><td>Recommendation Agent</td><td>None</td><td>Pipeline Construct/Debug Agent</td></tr><tr><td>Extensibility</td><td>OperatorZoo / Cookbook</td><td>Custom Scripts</td><td>Extension Packages + CLI Scaffolding</td></tr></table>

These systems substantially improve the efficiency and quality of LLM data preparation, but they remain largely configuration-centric toolkits. In contrast, our framework is built around a rich library of nearly 200 reusable text-specific operators, enabling fine-grained control over cleaning, transformation, synthesis, and evaluation; multiple pipelines instantiated from these operators consistently yield strong downstream gains, and even simple mixtures of data produced by different pipelines remain highly effective. Moreover, the system adopts a modular, PyTorch-style "building-block" design with lightweight, well-defined interfaces, making it natural for data agents to compose, orchestrate, and invoke data-processing pipelines programmatically.

# 3 DataFlow System Overview

In this section, we present a overview of DATAFLOW a unified and automated system that standardizes and streamlines multi-domain data preparation for LLMs.

# 3.1 Goals and Design Philosophy

DataFlow is designed around six core goals:

Ease of Use. A PyTorch-inspired [49], IDE-friendly programming interface enables users to build and debug complex data preparation pipelines with minimal boilerplate.

Extensibility. Following a modular abstraction similar to torch(nnModule, new operators, and algorithms can be added as plug-and-play components and naturally compose with existing workflows.

Unified Paradigm. DATAFLOW unifies heterogeneous data preparation workflows under a standardized abstraction layer. The design balances standardization, for consistency and reproducibility, with customization needed across domains, enabling efficient pipeline reuse and adaptation.

Performance Efficiency. The official pipelines in DATAFlow achieve performance comparable to or exceeding SOTA data preparation methods, demonstrating that unification does not impose substantial overhead.

Intelligent Automation. A lightweight agentic subsystem leverages core abstractions to interpret natural-language intent and automatically construct or adjust operators and pipelines, supporting rapid prototyping and reducing manual engineering.

Open Source Paradigm. DATAFlow aims to serve as a community standard for LLM data preparation. Its unified abstractions enable reproducible pipeline sharing, transparent swapping of LLM backends, and controlled experimentation.

# 3.2 System Scope and Positioning

DATAFlow spans the full workflow of LLM-centric data preparation. As Figure 1 shown, at its core, the system provides unified abstractions for storage, LLM serving, operators, prompt templates, and pipelines—defining the execution substrate on which all transformations are performed. Above the core, two user-facing control layers, the CLI and the DATAFLOW-Agent, support both scriptable and automated workflow construction.

![](images/1e2b546603f330c5deb2b67ab4c0090f5cf0e235c52c7493e4ef0effe85658cb.jpg)  
Figure 1 High-level architecture of DATAFlow. The system consists of a core execution engine (storage, operators, templates, and LLM serving), reusable pipelines, user-facing control layers (CLI and agent), and an extensible ecosystem for domain-specialized workflows. DATAFlow produces high-quality, task-aligned datasets consumed by downstream LLM applications.

Beyond the engine, DATAFLOW-EXTENSIONS offer a modular interface for adding Python-package-based operators, templates, and pipelines. Domain-specialized packages built on this interface collectively form the broader DATAFLOW-ECOSYSTEM. Together, these components define the system boundary: DATAFLOW provides the abstractions and control layers for data preparation, while downstream LLM training, evaluation, and retrieval applications consume its outputs.

# 3.3 System Workflow

Figure 1 also illustrates the end-to-end workflow of DATAFlow. The system ingests datasets from common file formats (e.g., JSON, JSONL, CSV, Parquet, Markdown, PDF) as well as domain-specific sources such as SQL logs and code repositories, converting all inputs into a unified tabular representation maintained by the core storage layer. Operators interact with this shared storage to read and write intermediate results, enabling consistent data flow across transformation stages.

Operators implement transformations such as generation, refinement, filtering, and evaluation. LLM-driven operators invoke local inference engines (e.g., vLLM [35], SGLang [73]) or online API-based services (e.g., Gemini [56], ChatGPT [1]) via the unified serving abstraction, while rule-based and small-model operators execute independently of LLM backends.

Pipelines in the Pipeline Zoo compose these operators into reusable workflows for tasks such as text synthesis, mathematical reasoning, code processing, Text-to-SQL generation, agentic RAG, and large-scale knowledge extraction. Pipelines may be executed directly, compiled for optimized execution, resumed from intermediate states, or adapted to new domains.

Users interact with DATAFlow during workflow execution through either the CLI or the DATAFLOW-AGENT: the CLI issues explicit execution commands, while the agent translates natural-language specifications into executable workflows and performs iterative debugging. Workflow outputs, high-quality, task-aligned datasets, integrate seamlessly into downstream LLM applications.

# 4 Framework Design and Architecture

This section presents the internal design of DATAFLOW and formalizes the execution model underlying its abstractions in Section 3. DATAFLOW is organized around four architectural pillars: (1) a global storage abstraction that maintains the canonical tabular representation of datasets and mediates all data access; (2) a set of hierarchical programming interfaces for LLM serving, operators, prompt templates, and pipelines; (3) a principled operator categorization scheme that reconciles open-ended domain requirements with a compact set of reusable transformation primitives; and (4) an extension mechanism that supports a growing ecosystem

of user-contributed components. Together, these elements provide a scalable and extensible substrate for constructing, executing, and sharing LLM-centric data preparation workflows.

# 4.1 Global Storage Abstraction and Operator Interaction

At the core of DATAFLOW's execution substrate is a unified storage abstraction that maintains the canonical tabular representation of the dataset and mediates all data access during workflow execution. LLM-oriented data—such as instructions, responses, chain-of-thought traces, scores, and metadata—is naturally expressed as key-value fields associated with each sample, making a tabular structure a suitable and expressive organizational format. The storage layer decouples data management from operator logic, exposing a minimal, backend-agnostic API through the DataFlowStorage base class. This design allows custom storage backends—such as file-system, object-store, or database implementations—to be integrated without altering operator behavior.

The abstraction provides two primary operations:

- read(): retrieve the current dataset (or relevant fields) in a format required by the operator.  
- write(data): update or append fields to the shared dataset representation.

Centralizing all access through these operations ensures that operators remain agnostic to physical storage layout, while intermediate artifacts produced by one operator become immediately available to others. A typical operator interaction follows the pattern in Figure 2.

```python
def run(self, storage: DataFlowStorage, **kwargs):  
    inputs = storage.read()  # 1. Read input  
    results = operator_transform(inputs, ** kwargs)  # 2. Transform the data  
    storage.write(results)  # 3. Write output
```

Figure 2 The standard execution pattern of an operator's run() method in DATAFLOW. Within run(), the operator interacts with the global DataFlowStorage by retrieving inputs through storage.read(), applying its transformation logic, and writing updated fields back via storage.write(). This read-transform-write paradigm captures how data flows from one operator to the next throughout the workflow.

Because operators operate only against this logical abstraction, they can be reordered, recomposed, or batched without modifying their internals, and improvements to the storage backend (e.g., adding distributed or database-backed implementations) require no operator-level changes. The default storage implementation uses a Pandas as the execution substrate and supports common input/output formats such as JSON, JSONL, CSV, and Parquet.

# 4.2 Hierarchical Programming Interfaces

DATAFlow exposes a hierarchical programming interface built around four core abstractions. (1) The serving interface provides a unified mechanism for issuing LLM inference requests across heterogeneous backends. (2) Operators define reusable data-transformation units and may optionally invoke the serving layer when LLM-driven computation is required. (3) Prompt templates specify how operator inputs are rendered into concrete prompts and how model outputs should be structured or constrained, providing a declarative interface for consistent prompt construction. (4) Pipelines compose operators into multi-stage workflows with explicit data dependencies and support optional compilation for validation and optimization. The following subsections describe these abstractions in detail.

# 4.2.1 LLM Serving API

LLM-driven operators rely on a unified serving API that abstracts over heterogeneous model backends. The API exposes a single high-level entry point, generate_from_input(user_entries, system_prompt, json_schema), which accepts a list of prompts, typically assembled by the calling operator, and returns a list of model-generated outputs. Optional arguments such as a system_prompt or an output json_schema enable

![](images/479af365725b1dc92e179f201504cb3236a8da71ed6584e37394779321e29f8b.jpg)  
Figure 3 Example of how an operator's run() method interacts with data via key-based bindings. This flexible key-binding mechanism adapts to arbitrary datasets without preprocessing and enables seamless operator composition.

structured prompting and decoding when needed. This interface shields operators from backend-specific considerations such as batching, retry strategies, request routing, and rate limiting.

The serving layer supports both:

- Local inference engines (e.g., vLLM [35], SGLang [73]), which exploit backend-level parallelism for high-throughput execution; and  
- Online API-based services (e.g., ChatGPT [1], Gemini [56]), for which DATAFlow performs multi-threaded request dispatch to maximize throughput.

This unified serving abstraction reduces the implementation burden of LLM-driven operators and enables flexible backend substitution, making it easy to assess how different LLM choices influence data preparation quality.

# 4.2.2 Operator Programming Interface

Operators serve as the fundamental transformation units in DATAFlow. They follow a two-phase interface that cleanly separates initialization from execution: initialization configures the operator, while execution performs the transformation. This separation allows heterogeneous behaviors, from LLM-driven generation to rule-based filtering, to be expressed under a unified abstraction.

During initialization (__init__()) an operator receives configuration parameters such as hyperparameters or task-specific settings. LLM-driven operators may additionally bind to a LLM serving object and a prompt-template object in this stage, whereas rule-based and lightweight-model operators omit these bindings entirely. Initialization therefore captures all static configuration and external dependencies, leaving execution to focus exclusively on data transformation.

An operator's run() method implements its transformation logic and constitutes the unit of execution within a pipeline. To keep operators general and easily composable, run() accepts only a DataFlowStorage object together with a set of input_* and output_* keys. Interpreting these as key-value pairs, an input_* key indicates the storage column to be read as an input field, while an output_* key indicates the name of the new column to be written for each processed data item. Figure 3 illustrates this mapping. This design provides flexible I/O bindings that naturally adapt to diverse upstream datasets, while the declared keys form a directed dependency graph among operators, enabling topological scheduling and downstream optimization checks.

By isolating configuration from execution and constraining state changes to explicit key-based read/write operations on shared storage, the operator abstraction remains lightweight, deterministic, and easy to compose. These properties allow DATAFLOW to support a wide range of transformation behaviors under a single, portable interface while preserving consistent execution semantics throughout the system.

```python
class TranslatePipeline(PipelineABC): def __init__(self): super().__init_(   ) # Init Resources self(storage = FileStorage( entry_file="input_data.json1", ) self.llm_serving = APILLMServing( api_url="<api_url>", model_name="gpt-4o", ) # Initialize Operators self.op1 = PromptedGenerator( llm_serving= self.llm_serving, system_prompt="Translate the content to Chinese", ) self.op2 = PromptedGenerator( llm_serving= self.llm_serving, system_prompt="Translate the content to English", ) if __name_ == "_main_: TransPipeline = TranslatePipeline(   ) Transpipeline.compile(   ) # Optional # execute pipeline, resume from `op2` Transpipeline.forward(resume_step=1)
```

Figure 4 Illustration of the DATAFLOW pipeline API. The example shows how a pipeline declares its storage and serving backends, instantiates operators with task-specific configurations, and executes them via forward() using input/output key bindings. The interface supports compilation and stepwise resumption, enabling flexible and modular workflow construction.

# 4.2.3 Prompt Template Interface

Prompts serve as the primary mechanism guiding LLMs to perform task-specific transformations. Every LLM-driven operator relies on a prompt, and operators that share the same high-level logic often differ only in subtle prompt variations. For instance, in Text-to-SQL generation, synthesizing queries for SQLite and MySQL involves identical operator logic; the only difference lies in minor syntax adjustments communicated through the prompt. To support such reuse while accommodating domain-specific variations, DATAFlow decouples prompt construction from operator implementation through a dedicated prompt template interface.

A prompt template encapsulates a reusable prompt pattern and provides parameterized slots that operators populate at execution time. Each LLM-driven operator initializes its associated template during __init__(), following the same configuration—execution paradigm as other system components. During execution, the operator invokes the template's build_prompt() method, which assembles task-relevant information—such as input fields, schema hints, or contextual metadata—into a concrete prompt that is subsequently passed to the LLM serving layer. This encapsulation allows the operator's transformation logic to remain agnostic to how prompts are rendered.

To facilitate one-to-many mappings between operators and templates, LLM-driven operators expose a unified op. ALLOWED_prompt interface that enumerates all compatible prompt templates. This design enables operators to be flexibly reused across domains or tasks by simply switching or tuning templates, without modifying operator logic.

Overall, the prompt template interface provides a declarative mechanism for prompt construction, promotes operator reuse across closely related tasks, and ensures consistent prompting behavior throughout DATAFLOW's LLM-driven workflows.

# 4.2.4 Pipeline Composition Interface

Building on the abstractions introduced above, DATAFlow provides a pipeline interface that enables users to compose operators into multi-stage data-preparation workflows. A pipeline is represented as an ordered sequence of operators (or a lightweight DAG), forming an end-to-end execution graph that captures the intended dataflow. Figure 4 illustrates the pipeline API and its core components.

The pipeline API adopts a PyTorch [49]-like design in which the __init__() method handles resource allocation and operator configuration, while the () method encodes a single pass of execution. Within

forward(), operator-specific key bindings implicitly define the dataflow topology, allowing pipelines to be constructed in a modular, readable, and IDE-friendly manner.

Functionally, the pipeline interface provides a built-in compile() procedure that performs static analysis of the operator sequence prior to execution. During compilation, DATAFLOW extracts operator dependencies and parameters, constructs the corresponding DAG, and conducts key-level validation to detect missing fields, type inconsistencies, and malformed dependency chains. Instead of executing operators immediately, compile() records all operator configurations and dependency information to produce a deferred execution plan. This deferred-construction design follows the Factory Method pattern [16], in which object creation is separated from object execution: the actual invocation of each operator's run() method is deferred until the subsequent forward() call.

The compiled execution graph first provides complete structural information to the DATAFlow-Agent, enabling it to surface all key- and dependency-related errors in a single report. This significantly reduces the number of debugging rounds required by the agent and lowers the associated inference cost. Additionally, the compiled graph defines a minimal and efficient execution plan that supports advanced runtime features such as checkpointing and stepwise resumption, improving iterative development and large-scale pipeline construction.

# 4.3 Operator Categorization

Operators in DATAFLOW encapsulate diverse data-processing algorithms that, when composed, support end-to-end LLM data preparation workflows. As a unified yet extensible framework intended to serve arbitrarily many domains, DATAFLOW must simultaneously accommodate an open-ended set of domain-specific algorithms while exposing a stable and comprehensible operator space. These competing forces—unbounded domain requirements and the need for conceptual compactness—introduce inherent tension. To reconcile this, DATAFLOW organizes operators along multiple orthogonal categorization dimensions. Categories are mutually exclusive within each dimension, while dimensions themselves are parallel. This categorization scheme has been validated across the diverse domains covered in this paper, including more than six state-of-the-art data preparation pipelines, demonstrating both its representational sufficiency and scalable generality.

Modality Dimension. The fundamental categorization separates operators by the modality they process, such as text, visual content, or document-like inputs. Modalities must be distinguished because operators within the same modality share compatible input-output semantics and can interoperate, whereas operators across different modalities often cannot be composed directly. DATAFlow primarily operates on textual representations, with non-text modalities first processed by modality-specific operators that parse or convert raw inputs—such as images or PDFs—into text before any downstream transformations are applied. Therefore, Clear modality classification makes this conversion flow explicit and enables the pipeline compiler to validate operator chains, ensuring that modality transitions are correctly specified and that only compatible operators are composed.

Core vs. Domain-Specific Dimension. A second categorization distinguishes between core operators and domain operators. Core operators reflect the fundamental design philosophy of DATAFlow and serve as the conceptual basis from which most other operators can be derived. Although domain operators may wrap or specialize core operators, their semantics can generally be expressed by instantiating the parameters of a corresponding core operator. Core operators are intentionally limited in number and relatively stable, forming the recommended entry point for new users. Domain operators, by contrast, expand without bound as new domains, modalities, or tasks emerge. Although theoretically unbounded, the domain operators included in DATAFlow are limited to those required to support the best-performing pipelines across existing domains, ensuring practical conciseness and avoiding unnecessary proliferation.

Functional Dimension. At a finer granularity, operators fall into four functional categories—generate, evaluate, filter, and refine—each capturing a distinct transformation pattern in data preparation. These categories align with a core design philosophy of DATAFLOW as a data-synthesis framework: pipelines first expand the candidate space through generation, then score and filter the results, optionally applying refinement stages in

![](images/4410528d6cd7f3f028f5a4bc2e9ee6d14b2af0bb03c9ad07ab0d44095541d8f2.jpg)  
Figure 5 Evolution of sample counts across operator stages in DATAFlow pipelines. All pipelines start with 1000 input samples. The Text pipeline mainly performs pre-training data filtering, and the Code pipeline focuses on expanding code capabilities based on existing instruction data; therefore, neither of these pipelines involves any generative components.

between. This generate-evaluate-filter-refine paradigm underlies most pipeline designs in DATAFLOW. As illustrated in Figure 5, when a pipeline begins with 1,000 input samples, the number of data items typically increases during generation stages and then contracts as evaluation, filtering, and refinement operators are applied.

To make this paradigm concrete, DATAFlow defines four operator categories, each with clear semantics and naming conventions. Throughout this discussion, we use the tabular representation adopted by DATAFlow: each row denotes a data sample, and each field corresponds to a named column within that sample.

- Generate. These operators augment data by adding new textual fields or producing additional rows. Operators ending with Generator add new fields to existing rows, whereas those ending with RowGenerator increase the number of rows. Example usages include generating answers to questions.  
- Evaluate. These operators compute scores or labels for either individual samples or entire datasets. SampleEvaluator operators attach evaluation metadata to each row, whereas DatasetEvaluator operators output dataset-level metrics. Examples include assigning difficulty levels to math problems or classifying QA pairs by subject.  
- Filter. These operators reduce the number of rows based on criteria derived from existing fields or evaluation results. Their semantics maintain row contents apart from newly added evaluation fields. Examples include removing samples with incorrect answers.  
- Refine. These operators modify specific fields within existing rows without changing the number of samples. They often apply lightweight transformations such as removing URLs or emojis from text. Operators typically end with the suffix Refiner.

Across these dimensions, DATAFLOW supports both systematic extensibility and bounded conceptual complexity: the modality and core-versus-domain dimensions organize an open-ended operator ecosystem, while the functional dimension provides a compact and reusable set of transformation primitives for constructing scalable LLM data preparation workflows.

# 4.4 DataFlow-Ecosystem

A unified data preparation framework must accommodate an open-ended set of algorithms and workflows, which naturally leads to an unbounded space of operators and pipelines. To structure this extensibility in a maintainable manner, DATAFlow introduces the concept of a DATAFlow-Extension: a modular

![](images/df4df686a366d178143f95ca2de428c83752bc643bffae5854dcae7534f915d7.jpg)  
Figure 6 DATAFLOW-AGENT architecture: a LangGraph-orchestrated multi-agent workflow that translates natural-language intent into a verified executable DAG pipeline.

package that encapsulates additional operators, prompt templates, and pipelines. User-contributed extensions collectively form the broader DATAFLOW-Ecosystem, a plug-and-play environment analogous to Python's package ecosystem, where practitioners can readily publish, share, and reuse domain-specific components.

To streamline extension development, DATAFLOW provides automated project scaffolding through the DATAFLOW-CLI. Given a few high-level specifications, the CLI generates ready-to-use templates for operators, prompt templates, pipelines, and even full repository layouts suitable for distribution via PyPI or GitHub. Developers need only implement task-specific logic within these generated stubs. Both the core system and extension packages can be installed and imported through Python's package manager, while lazy-loading mechanisms ensure that multiple extensions coexist with minimal environmental interference.

Complementing the CLI, the DATAFLOW-AGENT supports natural-language-driven construction of operators and pipelines. Leveraging the domain knowledge embedded in large language models, the agent synthesizes effective data-transformation logic and automates common design steps, substantially reducing the cost of authoring high-quality DATAFLOW-Extensions.

Together, the DATAFLOW-CLI and DATAFLOW-Agent reduce the overhead of extension development and promote community-driven growth. Our goal is to cultivate a sustainable open-source ecosystem in which data preparation recipes—constructed from standardized operators, prompt templates, and pipelines—can be shared, reproduced, and improved, ultimately accelerating progress across the data-centric ML community.

# 5 DataFlow-Agent

The DATAFLOW-AGENT serves as the intelligent orchestration layer atop the DATAFLOW framework. It bridges high-level human intent with low-level data-processing execution by leveraging the modular abstractions of DataFlow together with a graph-based multi-agent workflow engine. Built on LangGraph [2], the agent layer coordinates a set of specialized agents through a stateful execution graph, translating natural-language directives into executable, self-correcting, and optimized data preparation pipelines.

# 5.1 AgentRoles

To achieve autonomous pipeline construction and code synthesis, the system decomposes responsibilities across a roster of specialized agents. Each agent encapsulates specific logic and interacts with the DATAFLOW core components:

- Intent Analysis Agent: Accepts the user's high-level natural language query and decomposes it into a structured sequence of actionable sub-intents, providing the foundational blueprint for the pipeline.  
- Data Routing Agent: Analyzes the provided input data to determine the task category for routing, or generates synthetic data placeholders if no data is supplied to enable dry-run execution.

- Operator Retrieval Agent: Takes specific sub-intents as input and employs RAG to retrieve the most relevant existing operators from the DATAFlow library as potential candidates.  
- Operator Sequencing Agent: Evaluates candidate operators for I/O compatibility to select the best fit, or outputs detailed specifications for new operators when functional gaps are detected.  
- Operator Synthesis Agent: Receives specifications for missing functions and generates context-aware code using RAG, performing automated unit-level debugging until the code is executable.  
- Operator Reuse Agent: Assesses the generated operator code for quality and creates a reusable prompt__template, ensuring the code can be efficiently reused without rewriting.  
- Pipeline Construction Agent: Orchestrates the assembly of all validated operators (both pre-existing and newly synthesized) into a coherent Directed Acyclic Graph (DAG) structure ready for processing.  
- Pipeline Verification Agent: Executes the assembled pipeline within a sandboxed environment to identify runtime errors, autonomously adjusting connections or parameters to output a validated, error-free pipeline.  
- Result Reporting Agent: Synthesizes the final workflow details and execution results, generating a comprehensive report and an executable pipeline artifact as the final solution.

# 5.2 Intelligent Pipeline Recommendation

As shown in Figure 6, the core capabilities of the system are realized through a sophisticated agentic layer built atop the DataFlow framework. This layer employs LangGraph [2] to orchestrate a series of specialized agents within graph-based stateful workflows.

Intent Decomposition The workflow begins when the system receives a user's natural language query. The Intent Analysis Agent decomposes this high-level objective into a sequence of discrete, actionable sub-intents. Concurrently, the Data Routing Agent evaluates the input dataset to categorize the task for downstream routing. If no dataset is provided, this agent generates synthetic data placeholders to enable a complete dry-run execution.

Operator Synthesis To fulfill these sub-intents, the Operator Retrieval Agent searches the DATAFLOW library for relevant operators, which the Operator Sequencing Agent evaluates for compatibility. If a functional gap is identified, the Operator Reuse Agent first assesses whether the requirement can be met by reusing existing code via a prompt_template. Only when reuse is not feasible does the Operator Synthesis Agent generate new code using RAG-based few-shot learning. The code is then debugged automatically to ensure stable execution.

Pipeline Assembly After all retrieved or synthesized operators are validated, the Pipeline Construction Agent assembles them into a single pipeline. It represents the pipeline as a DAG and defines the initial connections so data can flow from the source to the sink.

Verification The system then runs an integration test. The Pipeline Verification Agent executes the pipeline in a sandbox with a data sample to check connectivity and runtime behavior. If errors occur, it fixes them by adjusting parameters or connections. After the pipeline passes validation, the Result Reporting Agent generates a report and outputs the final executable pipeline definition.

# 5.3 Summary

In summary, unlike Data-Juicer's agentic approach [6], which is largely constrained to parameterizing and sequencing a static library of pre-existing operators, DATAFLOW-AGENT achieves a significantly higher degree of autonomy through its ability to dynamically synthesize and debug executable code for missing functionalities. By integrating a "retrieve-reuse-synthesize" strategy with a self-correcting verification loop,

![](images/6e0f3c060a6cb19427f8b278fbe1d16141e0a0edcfeba0696cb0b4b10401e917.jpg)  
Figure 7 Overall framework of Text-to-SQL pipelines in DATAFlow.

our system transcends simple configuration generation, enabling the construction of truly adaptive pipelines that can handle unforeseen requirements without manual coding intervention.

# 6 Use Cases & Pipelines

DATAFLow integrates a rich collection of data pipelines covering diverse text centric task domains, including text processing, mathematical reasoning data, Text-to-SQL generation, and agentic data preparation. In addition, DATAFLow supports structured knowledge extraction and normalization from PDFs and textbooks, enabling tasks such as schema construction, domain grounding, and instruction synthesis.

All pipelines are implemented through reusable operators and declarative workflow specifications, allowing users to flexibly compose, extend, and adapt them to new scenarios with minimal engineering effort. More detailed tutorials, pipeline examples, and operator-level documentation are available at the website: https://opendcai.github.io/DataFlow-Doc/.

# 6.1 Case Study: Text-to-SQL Data Pipeline in DataFlow

We first design a set of specifically designed, reusable Text-to-SQL operators to ensure modularity and extensibility (see Section 6.1.1). As shown in Figure 7, we introduce two pipelines to construct high-quality Text-to-SQL datasets (see Section 6.1.2). Furthermore, Section 6.1.3 describes the support for database operations and the prompt template mechanisms provided by DATAFlow.

# 6.1.1 Operators

SQL Generator. The SQL Generator operator produces SQL queries from scratch using the database, ensuring both diversity and validity. Four levels of complexity, simple, moderate, complex, and highly complex, are defined and randomly selected to guide the LLM in generating queries of varying difficulty through clear definitions and few-shot examples. The database schema, including CREATE TABLE statements for all relational tables and randomly sampled column values, provides the necessary context for the LLM to understand the database. Advanced SQL functions are also randomly supplied to increase the realism of the generated queries. Since natural language questions often require querying specific entries, the number of returned columns is constrained accordingly. Under task instructions, the LLM produces meaningful SQL queries. Within the DATAFLOW framework, the SQL Generator operator can be naturally adapted and reused across different databases (e.g., MySQL, SQLite, PostgreSQL) simply by replacing the corresponding prompt template.

SQL Augmentor. The SQL Augmentor operator generates diverse, closely related augmented SQL queries based on seed SQL rather than synthesizing them from scratch. We propose six augmentation strategies to expand SQL queries in different directions: (1) Data Value Transformation, (2) Query Structure Modification, (3) Business Logic Alteration, (4) Complexity Enhancement, (5) Introduction of Advanced SQL Features, and (6) Performance and Optimization. Categories are randomly selected and applied through few-shot prompting. The database schema and values are provided as contextual information. Given an original SQL query and task instructions, the augmentor produces its augmented SQL counterpart.

Text2SQL Consistency Filter. For existing pairs of natural language questions and SQL queries, inconsistencies may arise where the two do not correspond. Such problematic data needs to be filtered out. This is achieved using an LLM, which analyzes whether the question and SQL align in content.

SQL Execution Filter. Not all generated SQL queries are valid or efficient. Therefore, the SQL Execution Filter operator filters queries from two perspectives: (1) whether the SQL query can be successfully executed on the target database, and (2) whether its runtime exceeds a preset threshold, in which case it is discarded to ensure system responsiveness.

Question Generator. The Question Generator operator generates a semantically equivalent natural language question based on the SQL. Natural language questions are categorized into the following stylistic types: (1) Tone and Formality: formal vs. colloquial, (2) Syntactic Structure and Intent: imperative, interrogative, and declarative, (3) Information Density and Clarity: concise, descriptive, ambiguous, and metaphorical, and (4) Interaction Mode: role-playing and procedural. The first two categories cover queries with clear user intent, whereas ambiguous and metaphorical styles involve unclear or figurative language. A target language style is randomly selected, and the database schema is provided for context. Based on task instructions and the generated SQL query, the LLM produces a natural language question.

Chain-of-Thought Generator. Chain-of-Thought(CoT) reasoning enhances a model's ability to solve complex tasks by breaking them down into a series of smaller, manageable sub-problems. To generate CoT reasoning traces, the task instructions, database schema, the generated natural language question, and the generated SQL query are needed. The LLM produces a complete reasoning chain covering intermediate reasoning steps and the final SQL query. During CoT validation, the generated SQL is extracted from the reasoning chain. A CoT process is considered a valid solution only if the execution result of its generated SQL matches that of the reference SQL on the given database.

Prompt Generator. As the primary input to the model, a prompt contains the necessary information for reasoning. To facilitate reliable Text-to-SQL generation, a well-structured prompt should include not only the natural language question but also the database schema and specific task instructions to guide the model. The Prompt Generation operator synthesizes these components into a final prompt.

SQL Component Classifier. Classifying SQL queries enables deeper analysis of their structural complexity. Following the evaluation standards of Spider [70], SQL queries are categorized into four difficulty levels, simple, moderate, hard, and extra hard, based on the number and complexity of their syntactic components. These components include column selections, the use of aggregate functions in the SELECT clause, and advanced constructs such as GROUP BY, ORDER BY, INTERSECT, or nested subqueries. The SQL Component Classifier operator assigns each SQL query to one of these categories according to the defined criteria.

SQL Execution Classifier. Whether the model can generate correct SQL for a given natural language question is also a meaningful measure of difficulty. In the SQL Execution Classifier operator, LLM is instructed to generate SQL query  $k$  times on the same input prompt and count the number of successful executions, denoted as  $n$ . We then classify the difficulty level based on  $\frac{n}{k}$ . Unlike the SQL component classifier operator, execution difficulty is model-dependent: more capable LLMs achieve higher success rates on the same task and thus are considered to have lower execution difficulty.

# 6.1.2 Pipelines

In the design philosophy of DATAFLOW, pipelines are decomposed into independent operator units according to their functionalities, enabling maximal reusability of operators. As shown in Figure 7, the designed operators are composed into two pipelines to support SQL data synthesis in different scenarios.

Table 2 Pre-training Data Filtering: Performance comparison across models trained with 30B-scale tokens on general evaluation benchmarks.  

<table><tr><td>Methods</td><td>ARC-C</td><td>ARC-E</td><td>MMLU</td><td>HellaSwag</td><td>WinoGrande</td><td>Gaokao-MathQA</td><td>Avg</td></tr><tr><td>Random-30B</td><td>25.26</td><td>43.94</td><td>27.03</td><td>37.02</td><td>50.99</td><td>27.35</td><td>35.26</td></tr><tr><td>Qurating-30B</td><td>25.00</td><td>43.14</td><td>27.50</td><td>37.03</td><td>50.67</td><td>26.78</td><td>35.02</td></tr><tr><td>FineWeb-Edu-30B</td><td>26.45</td><td>45.41</td><td>27.41</td><td>38.06</td><td>50.43</td><td>25.64</td><td>35.57</td></tr><tr><td>DataFlow-30B</td><td>25.51</td><td>45.58</td><td>27.42</td><td>37.58</td><td>50.67</td><td>27.35</td><td>35.69</td></tr></table>

SQL Generation Pipeline. This pipeline generates SQL from scratch based on the database schema. It first uses the SQL Generator operator to produce initial SQL statements, followed by the SQL Execution Filter to remove low-quality or non-executable SQL. Next, the Question Generator produces the natural language question corresponding to each SQL query, the Chain-of-Thought Generator operates the reasoning steps (CoT), and the Prompt Generator constructs the prompt content. Finally, the SQL Component Classifier and SQL Execution Classifier assign difficulty labels to the data.

SQL Refinement Pipeline. This pipeline generates data starting from the existing seed SQLs. The pipeline first verifies the quality of the seed SQL using the SQL Execution Filter, and the Text2SQL Consistency Filter removes samples where the SQL does not align with the natural language question. Then, the SQL Augmentor produces augmented SQL based on the seed SQL. The subsequent steps mirror those in the SQL Generation Pipeline: filtering low-quality SQL with the SQL Execution Filter, generating natural language questions via the Question Generator, producing CoT reasoning via the Chain-of-Thought Generator, composing prompts with the Prompt Generator, and finally assigning difficulty labels using the SQL Component Classifier and SQL Execution Classifier.

# 6.1.3 DataFlow-support Mechanism

Database Manager Module. Within the Pipeline, an efficient and reliable data interaction mechanism serves as the core infrastructure that ensures the stable execution of the workflow. To this end, we implement the Database Manager module, which encapsulates the low-level details of database interaction and provides a unified, efficient, and extensible programming interface. The Database Manager improves processing throughput under high-concurrency workloads and abstracts schema metadata retrieval, thereby reducing the upper layers' dependency on the underlying database structure. To achieve cross-database compatibility, we introduce the abstract base class DatabaseConnector. This class defines a standardized set of interfaces, including connect_db (establishing a database connection), execute sql (executing SQL statements and returning results), and get_schema (retrieving complete schema metadata). For each database system, developers need only subclass this base class and implement the system-specific driver invocation and error-handling logic, enabling seamless integration into the overall system.

Prompt Template Module. When generating SQL, different scenarios, such as CRUD queries, vector search SQL, or SQL categorized by different difficulty specifications, require distinct prompt templates. To maximize operator reusability under these varying requirements, DATAFlow introduces the Prompt Template module. This design allows the SQL Generator operator to be reused across scenarios by simply substituting the Prompt class. In practice, one only needs to reimplement the build_prompt method within a new Prompt class, without modifying the SQL Generator operator itself.

# 7 Experiments

In this section, we present a comprehensive set of experiments spanning text, math, and code data preparation, as well as Text-to-SQL and AgenticRAG workflows constructed using DATAFLOW. Except for the AgenticRAG setting, which is trained using the Recall [9, 54] framework, all other experiments are conducted using the LLaMA-Factory [74] training framework. We further integrate these modalities to assess the model's general instruction-tuning performance across diverse tasks.

Table 3 SFT Data Filtering: Comparison of different 5k dataset filtering methods across Math, Code, and Knowledge benchmarks.  

<table><tr><td rowspan="2">Methods</td><td colspan="6">Math</td><td colspan="3">Code</td><td colspan="3">Knowledge</td></tr><tr><td>math</td><td>gsm8k</td><td>aime24</td><td>minerva</td><td>olympiad</td><td>Avg</td><td>HumanEval</td><td>MBPP</td><td>Avg</td><td>MMLU</td><td>C-EVAL</td><td>Avg</td></tr><tr><td>Alpaca(random)</td><td>54.9</td><td>77.2</td><td>13.3</td><td>14.0</td><td>27.0</td><td>37.3</td><td>71.3</td><td>75.9</td><td>73.6</td><td>71.8</td><td>80.0</td><td>75.9</td></tr><tr><td>Alpaca/filtered)</td><td>60.3</td><td>80.0</td><td>13.3</td><td>14.7</td><td>30.7</td><td>39.8</td><td>73.8</td><td>75.7</td><td>74.8</td><td>71.8</td><td>80.0</td><td>75.9</td></tr><tr><td>WizardLM(random)</td><td>61.1</td><td>84.2</td><td>6.7</td><td>18.0</td><td>29.3</td><td>39.9</td><td>75.6</td><td>82.0</td><td>78.8</td><td>71.8</td><td>79.2</td><td>75.5</td></tr><tr><td>WizardLM/filtered)</td><td>69.7</td><td>88.8</td><td>10.0</td><td>19.9</td><td>35.4</td><td>44.8</td><td>77.4</td><td>80.4</td><td>78.9</td><td>71.9</td><td>79.6</td><td>75.8</td></tr><tr><td>DataFlow-SFT-15K(random)</td><td>72.6</td><td>89.6</td><td>13.3</td><td>37.9</td><td>32.9</td><td>49.3</td><td>79.9</td><td>75.9</td><td>77.9</td><td>72.1</td><td>80.0</td><td>76.1</td></tr><tr><td>DataFlow-SFT-15K/filtered)</td><td>73.3</td><td>90.2</td><td>13.3</td><td>36.0</td><td>35.9</td><td>49.7</td><td>82.9</td><td>74.9</td><td>78.9</td><td>72.2</td><td>80.4</td><td>76.3</td></tr></table>

# 7.1 Text Data Preparation

# 7.1.1 Experimental Setting

We evaluate the impact of high-quality text data preparation on both pre-training (PT) and supervised fine-tuning (SFT) using our DATAFLOW system. Our experiments cover three complementary scenarios:

(1) Pre-training Data Filtering (30B Scale). From the SlimPajama-627B corpus, we extract a 100B-token subset and apply multiple DATAFlow text-pretraining filters (implemented in dataflow/operators/text-pt/filter). For each filter, the top  $30\%$  (approximately 30B tokens) is selected. We train a Qwen2.5-0.5B model from scratch for 30B tokens using the Megatron-DeepSpeed framework. We compare four settings:

- Random-30B: a random 30B-token subset.  
- FineWeb-Edu-30B: educational filtering based on FineWeb-Edu [50].  
- Qurating-30B: Qurating filters [64] using thresholds: educational_value  $\geq 7.5$ , facts_and_trivia  $\geq 4.0$ , required_expertise  $\geq 5.0$ , writing_style  $\geq 1.0$ .  
- DataFlow-30B: intersection of all DATAFLOW PT filters selecting the top  $30\%$ .

(2) SFT Data Filtering (5K Scale). To study small-scale SFT data quality, we fine-tune the Qwen2.5-7B base model using LLaMA-Factory on WizardLM and Alpaca datasets. For each dataset, we compared a randomly sampled set of 5K instances against a set of 5K instances filtered by DATAFLOW's SFT pipeline. Additionally, we synthesize a 15k-size dataset, DATAFLOW-SFT-15K, using DATAFLOW's Condor Generator and Condor Refiner pipeline, followed by DATAFLOW's SFT filtering pipeline (excluding the Instagram filter). Benchmarks include comprehensive Math, Code, and Knowledge evaluation suites.  
(3) Conversation-Domain Synthesis (15K Scale). We synthesize DATAFLOW-CHAT-15K using DATAFLOW's conversation-generation pipeline and fine-tune Qwen2.5-7B-Base on it. Baselines include ShareGPT-15K, UltraChat-15K, and their full (non-truncated) versions. We evaluate on domain-specific tasks (TopDial, Light) and general benchmarks (MMLU [23], AlpacaEval [42], Arena-Hard [41]).

# 7.1.2 Experimental Results

Pre-training First, from Table 2, we can see across six general benchmarks (ARC-C/E, MMLU, HellaSwag, WinoGrande, Gaokao-MathQA), the DATAFLOW method achieves the highest average score (35.69), outperforming Random (35.26), FineWeb-Edu (35.57), and Qurating (35.02). Despite using the same 30B token budget, DATAFLOW's multi-filter intersection produces a cleaner and more semantically consistent dataset, leading to better generalization for a 0.5B-scale Qwen2.5 model trained from scratch.

SFT In Table 3, we then evaluate 5K-scale SFT data filtering using Alpaca, WizardLM, and DATAFLOW synthetic data. For all three sources, DATAFlow's filtering pipeline consistently improves performance over random sampling across Math, Code, and Knowledge benchmarks. At the same time, the results also show that the DATAFlow-constructed SFT corpus is inherently stronger than Alpaca and WizardLM: even without

Table 4 Conversation Synthesis: Performance comparison on conversation-domain datasets and general benchmarks for Qwen2.5-7B under different 15K SFT data sources.  

<table><tr><td rowspan="2">Model</td><td colspan="3">Conversation Benchmarks</td><td colspan="4">General Benchmarks</td></tr><tr><td>TopDial</td><td>Light</td><td>Avg</td><td>MMLU</td><td>AlpacaEval</td><td>Arena-Hard</td><td>Avg</td></tr><tr><td>Qwen2.5-7B</td><td>7.71</td><td>7.79</td><td>7.75</td><td>71.45</td><td>7.05</td><td>0.60</td><td>26.36</td></tr><tr><td>+ ShareGPT-15K</td><td>7.75</td><td>6.72</td><td>7.24</td><td>73.09</td><td>3.70</td><td>1.30</td><td>26.03</td></tr><tr><td>+ UltraChat-15K</td><td>7.72</td><td>6.83</td><td>7.28</td><td>72.97</td><td>3.97</td><td>0.80</td><td>25.91</td></tr><tr><td>+ DataFlow-Chat-15K</td><td>7.98</td><td>8.10</td><td>8.04</td><td>73.41</td><td>10.11</td><td>1.10</td><td>28.21</td></tr></table>

filtering, DATAFLOW-SFT-15K achieves higher Math averages (49.3) than the filtered variants of Alpaca (39.8) and WizardLM (44.8), and remains competitive on Code and Knowledge. Moreover, the smaller performance gap between the random and filtered versions of DATAFLOW-SFT-15K  $(49.3\rightarrow 49.7)$  further suggests that DATAFLOW-synthesized data is already cleaner and more informative, requiring less aggressive filtering to reach peak performance.

Conversation Finally, from Table 4 we can see DATAFLOW-CHAT-15K boosts the overall general benchmark mean from 26.36 to 28.21 and improves AlpacaEval from 7.05 to 10.11, outperforming ShareGPT and UltraChat.

These findings demonstrate that high-quality synthetic data, when paired with DATAFLOW's refinement and filtering stack, can surpass commonly used human-collected instruction datasets.

# 7.2 Math Reasoning Data Preparation

# 7.2.1 Experimental Setting

We construct a high-quality synthetic mathematical reasoning dataset based on the DATAFLOW Reasoning Pipeline, with adaptations tailored for large-scale reasoning generation. Our goal is to compare three training sources: (1) a random 10K subset from Open-R1 [28], (2) a random 10K subset from Synthetic-1 [43], and (3) our 10K synthesized DATAFLOW-REASONING-10K dataset constructed using DATAFLOW.

Data Synthesis Method. The data generation process follows the core structure of the DATAFLOW Reasoning Pipeline and includes three stages:

- Problem Synthesis. We adopt the NuminaMath dataset as a high-quality seed set and utilize the o4-mini model together with DATAFLOW's math problem synthesis operators to expand it into a diverse candidate problem pool.  
- Quality Verification. All candidate problems are validated using DATAFlow's MathQ-Verify [53] module, which detects incorrect, ambiguous, or logically inconsistent problems. Low-quality samples are removed to ensure correctness and robustness.  
- Chain-of-Thought (CoT) Generation. For all verified problems, we employ DATAFLOW's CoT-generation operators to prompt DeepSeek-R1 to produce complete, step-by-step reasoning traces.

Compared with the original Reasoning Pipeline, we omit the seed-level pre-verification stage, because NuminaMath is already a curated and validated dataset. This reduces computational overhead while maintaining overall data reliability.

We evaluate Qwen2.5-32B-Instruct fine-tuned on different 10k synthetic datasets across eight mathematical benchmarks, including GSM8K [11], MATH [24], AMC23, Olympiad, Gaokao24-Mix, Minerva, and AIME 2024/2025. Table 5 reports the full results.

Generation Hyperparameters. For non-AIME problems, we use temperature  $= 0$  and top-p  $= 0.95$ . For AIME-style problems, we adopt a more exploratory sampling strategy with temperature  $= 0.6$ , top-p  $= 0.95$ .

Table 5 Math Reasoning Pipeline: Performance comparison of Qwen2.5-32B-Instruct under different synthetic data training settings.  

<table><tr><td>Model</td><td>gsm8k</td><td>math</td><td>amc23</td><td>olympiad</td><td>gaokao24混</td><td>minerva</td><td>AIME24@32</td><td>AIME25@32</td><td>Avg</td></tr><tr><td>Qwen2.5-32B-Instruct</td><td>95.8</td><td>73.5</td><td>70.0</td><td>38.5</td><td>42.9</td><td>26.5</td><td>16.8</td><td>11.6</td><td>46.95</td></tr><tr><td colspan="10">Trained with 1 epoch</td></tr><tr><td>+ SYNTHETIC-1-10k</td><td>92.9</td><td>71.8</td><td>52.5</td><td>38.4</td><td>23.1</td><td>24.3</td><td>35.6</td><td>34.0</td><td>46.6</td></tr><tr><td>+ Open-R1-10k</td><td>91.5</td><td>72.3</td><td>65.0</td><td>38.4</td><td>20.9</td><td>24.6</td><td>43.0</td><td>33.5</td><td>48.7</td></tr><tr><td>+ DataFlow-Reasoning-10K</td><td>93.9</td><td>72.3</td><td>72.5</td><td>38.7</td><td>38.5</td><td>26.5</td><td>35.9</td><td>34.5</td><td>51.6</td></tr><tr><td colspan="10">Trained with 2 epochs</td></tr><tr><td>+ SYNTHETIC-1-10k</td><td>94.5</td><td>78.4</td><td>75.0</td><td>45.0</td><td>24.2</td><td>28.3</td><td>48.4</td><td>37.9</td><td>54.0</td></tr><tr><td>+ Open-R1-10k</td><td>93.9</td><td>77.2</td><td>80.0</td><td>44.1</td><td>20.9</td><td>25.4</td><td>51.0</td><td>40.7</td><td>54.2</td></tr><tr><td>+ DataFlow-Reasoning-10K</td><td>94.4</td><td>76.6</td><td>75.0</td><td>45.2</td><td>42.9</td><td>25.7</td><td>45.4</td><td>40.0</td><td>55.7</td></tr></table>

0.95, and top-k = 20. All models are fine-tuned with either 1 epoch or 2 epochs on 10k examples using Qwen2.5-32B-Instruct.

# 7.2.2 Experimental Results

Our first observation is that training on Synthetic-1 random subsets yields limited improvement over the base model. While minor gains appear on AMC23 and AIME benchmarks after 2 epochs, the overall average remains similar to the instruction-only baseline (47.0 vs. 46.6).

In contrast, the Open-R1 synthetic subset provides a stronger training signal: two epochs of fine-tuning increase the average score from 48.7 to 54.2, demonstrating that Open-R1-style CoT data is effective for enhancing mathematical reasoning in a 32B model. Building on this, our DATAFLOW-synthesized dataset achieves the strongest overall gains using only 10k samples, two epochs of fine-tuning reach the highest average performance of 55.7, surpassing both Open-R1 (54.2) and Synthetic-1 (54.0). These results indicate that combining verified NuminaMath seeds, MathQ-Verify filtering, and DeepSeek-R1-driven CoT generation yields more precise, diverse, and robust reasoning supervision.

Overall, the experiments demonstrate that data quality, rather than data scale, is the dominant factor in mathematical reasoning performance. Even with the same 10k size, our DATAFLOW-based synthesis pipeline consistently outperforms existing synthetic sources.

# 7.3 Code Data Preparation

# 7.3.1 Experimental Setting

To investigate the effect of high-quality code instruction data on code generation performance, we construct supervised fine-tuning (SFT) datasets using seed samples from Ling-Coder-SFT [12]. We first randomly sample 20k instances from the Ling-Coder-SFT corpus and process them through the DATAFLOW CodeGenDataset_APIPipeline. This yields three curated code instruction datasets of different scales, DATAFLOW-CODE-1K, DATAFLOW-CODE-5K, and DATAFLOW-CODE-10K, each designed to provide high-quality, pipeline-refined supervision signals for code generation tasks.

We compare our synthesized datasets against two widely used baselines, each subsampled to 1k examples for fairness:

- Code Alpaca (1k)[5]: a randomly sampled subset from the Code Alpaca dataset.  
- Self-OSS-Instruct-SC2-Exec-Filter-50k(1k) [63]: a 1k random subset from the SC2-Exec-Filter dataset, which incorporates execution-based filtering.

Models are fine-tuned on DATAFLOW-CODE-1K, DATAFLOW-CODE-5K, and DATAFLOW-CODE-10K using full-parameter SFT.

We then experiment with two base models: Qwen2.5-7B-Instruct and Qwen2.5-14B-Instruct. Evaluation

Table 6 Code Pipeline: Performance comparison of Qwen2.5-7B-Instruct and Qwen2.5-14B-Instruct under different SFT dataset settings (all numbers in %).  

<table><tr><td>Training Data</td><td>BigIntCodeBench</td><td>LiveCodeBench(v6)</td><td>CruxEval (Input)</td><td>CruxEval (Output)</td><td>HumanEval+</td><td>Avg</td></tr><tr><td colspan="7">Trained on Qwen2.5-7B-Instruct</td></tr><tr><td>Qwen2.5-7B-Instruct</td><td>35.3</td><td>23.4</td><td>44.8</td><td>43.9</td><td>72.6</td><td>44.0</td></tr><tr><td>+ Code Alpaca-1K</td><td>33.3</td><td>18.7</td><td>45.6</td><td>46.4</td><td>66.5</td><td>42.1</td></tr><tr><td>+ Self-OSS</td><td>31.9</td><td>21.4</td><td>46.9</td><td>45.9</td><td>70.1</td><td>43.2</td></tr><tr><td>+ DataFlow-Code-1K</td><td>35.5</td><td>25.7</td><td>48.0</td><td>45.1</td><td>72.6</td><td>45.4</td></tr><tr><td>+ DataFlow-Code-5K</td><td>36.2</td><td>26.4</td><td>48.6</td><td>45.0</td><td>73.2</td><td>45.9</td></tr><tr><td>+ DataFlow-Code-10K</td><td>36.8</td><td>26.0</td><td>48.8</td><td>45.4</td><td>73.8</td><td>46.2</td></tr><tr><td colspan="7">Trained on Qwen2.5-14B-Instruct</td></tr><tr><td>Qwen2.5-14B-Instruct</td><td>37.5</td><td>33.4</td><td>48.0</td><td>48.5</td><td>74.4</td><td>48.4</td></tr><tr><td>+ Code Alpaca-1K</td><td>37.0</td><td>28.2</td><td>50.2</td><td>49.6</td><td>71.3</td><td>47.3</td></tr><tr><td>+ Self-OSS</td><td>36.9</td><td>22.3</td><td>52.6</td><td>50.1</td><td>68.3</td><td>46.0</td></tr><tr><td>+ DataFlow-Code-1K</td><td>41.4</td><td>33.7</td><td>51.0</td><td>50.9</td><td>77.3</td><td>50.9</td></tr><tr><td>+ DataFlow-Code-5K</td><td>41.1</td><td>33.2</td><td>52.5</td><td>50.6</td><td>76.2</td><td>50.7</td></tr><tr><td>+ DataFlow-Code-10K</td><td>41.9</td><td>33.2</td><td>52.9</td><td>51.0</td><td>76.2</td><td>51.0</td></tr></table>

is conducted on four code benchmarks: (1) BigCodeBench [75],(2) LiveCodeBench [30],(3) CruxEval [22], and(4) HumanEval [8]. The final performance is reported as the average across these four benchmarks. All values in Table 6 are percentages.

# 7.3.2 Experimental Results

Table 6 shows that our synthesized datasets consistently improve the code generation performance of both Qwen2.5-7B-Instruct and Qwen2.5-14B-Instruct across all benchmarks. For the 7B model, even 1k of our synthetic data already outperforms both the Code Alpaca and SC2 execution-filtered baselines. Specifically, DATAFLOW-CODE-1K improves BigCodeBench, LiveCodeBench, and CruxEval scores over the original model, while remaining competitive on HumanEval+. Scaling the supervision to 5k and 10k further boosts overall performance. In particular, the DATAFLOW-CODE-10K setting achieves the best results on all metrics, including 36.8 on BigCodeBench, 48.8 on CruxEval(Input), and 45.4 on CruxEval(Output), and yields the highest overall average score of 46.2, surpassing both Code Alpaca-1K and SC2-Exec-Filter under the same data scale.

For the larger Qwen2.5-14B-Instruct model, the benefits are even more pronounced. While Code Alpaca-1k and SC2 filtering provide moderate improvements over the original 14B model, our datasets consistently deliver stronger gains across all metrics. In particular, DATAFLOW-CODE-10K reaches an average score of 51.0, achieving 41.9 on BigCodeBench, 52.9 on CruxEval(Input), and 51.0 on CruxEval(Output). Notably, LiveCodeBench, which stresses executable correctness—rises from 21.9 (Code Alpaca-1k) to 33.2 under our synthetic supervision. These results indicate that the DATAFLOW-generated data provide more explicit execution-grounded signals and structured reasoning cues than existing open-source sources.

Overall, the experiments demonstrate that DATAFLOW-driven synthesis consistently outperforms existing open-source code instruction datasets even under the same sample scale. The consistent gains from 1k to 10k indicate a simple trend: with more high-quality DATAFLOW training samples, the model keeps getting better on code reasoning tasks.

# 7.4 Text-to-SQL Data Preparation

# 7.4.1 Experimental Setting

To evaluate the effectiveness of Text-to-SQL data generation, we construct a training corpus comprising 89,544 high-quality Text-to-SQL instances, which is called DATAFLOW-TEXT2SQL-90K. Each instance in DATAFLOW-TEXT2SQL-90K includes natural language questions, corresponding SQL queries, and chain-of-thought reasoning traces. Specifically, these data are derived through systematic augmentation of seed SQL queries: 37,517 instances originate from the Spider-train [70] dataset, 37,536 from the BIRD-train [40]

Table 7 Text-to-SQL Pipeline: Performance of LLMs on mainstream benchmarks. The first two blocks list closed-source and open-source base models. The last two blocks show fine-tuned models, where the first column indicates the training data setting.  

<table><tr><td rowspan="2">LLM / Training Data</td><td colspan="2">Spider dev</td><td colspan="2">Spider test</td><td colspan="2">BIRD dev</td><td colspan="2">EHRSQL</td><td colspan="2">Spider-DK</td><td colspan="2">Spider-Syn</td><td colspan="2">Spider-Realistic</td><td colspan="2">Average</td></tr><tr><td>Gre</td><td>Maj</td><td>Gre</td><td>Maj</td><td>Gre</td><td>Maj</td><td>Gre</td><td>Maj</td><td>Gre</td><td>Maj</td><td>Gre</td><td>Maj</td><td>Gre</td><td>Maj</td><td>Gre</td><td>Maj</td></tr><tr><td colspan="17">Closed-source LLMs</td></tr><tr><td>GPT-4o-mini</td><td>70.4</td><td>71.0</td><td>82.4</td><td>83.7</td><td>58.8</td><td>61.5</td><td>37.9</td><td>43.1</td><td>73.3</td><td>74.4</td><td>60.5</td><td>61.6</td><td>64.4</td><td>66.7</td><td>64.0</td><td>66.0</td></tr><tr><td>GPT-4-Turbo</td><td>72.4</td><td>72.2</td><td>83.4</td><td>84.2</td><td>62.0</td><td>63.6</td><td>43.1</td><td>44.8</td><td>72.3</td><td>72.1</td><td>62.9</td><td>63.5</td><td>67.5</td><td>68.3</td><td>66.2</td><td>67.0</td></tr><tr><td>GPT-4o</td><td>70.9</td><td>70.7</td><td>83.2</td><td>84.9</td><td>61.9</td><td>64.0</td><td>44.9</td><td>45.5</td><td>72.9</td><td>73.5</td><td>59.6</td><td>62.3</td><td>66.5</td><td>66.7</td><td>65.7</td><td>66.8</td></tr><tr><td colspan="17">Open-source LLMs</td></tr><tr><td>DeepSeek-Coder-7B-Instruct</td><td>63.2</td><td>63.2</td><td>70.5</td><td>73.2</td><td>43.1</td><td>48.0</td><td>28.6</td><td>33.9</td><td>60.9</td><td>64.1</td><td>49.9</td><td>51.7</td><td>58.7</td><td>58.9</td><td>53.6</td><td>56.1</td></tr><tr><td>Qwen2.5-Coder-7B-Instruct</td><td>73.4</td><td>77.1</td><td>82.2</td><td>85.6</td><td>50.9</td><td>61.3</td><td>24.3</td><td>36.9</td><td>67.5</td><td>73.6</td><td>63.1</td><td>66.9</td><td>66.7</td><td>70.5</td><td>61.2</td><td>67.4</td></tr><tr><td>Qwen2.5-7B-Instruct</td><td>65.4</td><td>68.9</td><td>76.8</td><td>82.6</td><td>46.9</td><td>56.4</td><td>20.9</td><td>32.1</td><td>63.7</td><td>71.8</td><td>54.2</td><td>60.0</td><td>56.7</td><td>63.6</td><td>54.9</td><td>62.2</td></tr><tr><td>OpenCoder-8B-Instruct</td><td>59.5</td><td>59.5</td><td>68.3</td><td>70.1</td><td>37.5</td><td>45.3</td><td>21.9</td><td>29.9</td><td>62.6</td><td>64.7</td><td>46.0</td><td>46.1</td><td>49.0</td><td>49.4</td><td>49.3</td><td>52.1</td></tr><tr><td>Meta-Llama-3.1-8B-Instruct</td><td>61.8</td><td>67.7</td><td>72.2</td><td>78.5</td><td>42.0</td><td>53.1</td><td>24.6</td><td>33.7</td><td>62.6</td><td>69.9</td><td>53.1</td><td>59.3</td><td>57.5</td><td>61.0</td><td>53.4</td><td>60.5</td></tr><tr><td>Granite-8B-Code-Instruct</td><td>58.5</td><td>59.2</td><td>64.9</td><td>68.6</td><td>27.6</td><td>32.5</td><td>16.0</td><td>22.6</td><td>50.7</td><td>54.4</td><td>45.0</td><td>46.8</td><td>48.8</td><td>49.4</td><td>44.5</td><td>47.6</td></tr><tr><td>Granite-3.1-8B-Instruct</td><td>58.3</td><td>65.0</td><td>69.8</td><td>75.3</td><td>36.0</td><td>47.2</td><td>19.6</td><td>32.3</td><td>60.0</td><td>66.5</td><td>47.7</td><td>53.8</td><td>46.5</td><td>57.1</td><td>48.3</td><td>56.7</td></tr><tr><td colspan="17">Trained on Meta-Llama-3.1-8B-Instruct</td></tr><tr><td>SynSQL(50K)</td><td>67.1</td><td>73.9</td><td>72.7</td><td>78.6</td><td>49.1</td><td>55.2</td><td>33.6</td><td>40.8</td><td>63.8</td><td>66.1</td><td>59.6</td><td>63.5</td><td>69.3</td><td>71.6</td><td>59.3</td><td>64.2</td></tr><tr><td>SynSQL(90K)</td><td>68.2</td><td>74.6</td><td>73.4</td><td>78.5</td><td>51.1</td><td>54.9</td><td>31.8</td><td>38.0</td><td>61.8</td><td>67.4</td><td>58.9</td><td>63.6</td><td>69.0</td><td>70.9</td><td>59.2</td><td>64.0</td></tr><tr><td>SynSQL(2.5M)</td><td>70.6</td><td>73.7</td><td>78.3</td><td>82.5</td><td>58.9</td><td>62.0</td><td>35.1</td><td>37.0</td><td>72.3</td><td>74.7</td><td>61.0</td><td>63.1</td><td>67.9</td><td>69.4</td><td>63.4</td><td>66.1</td></tr><tr><td>Spider+BIRD+DataFlow-Text2SQL-90K</td><td>74.9</td><td>79.2</td><td>78.4</td><td>82.3</td><td>53.4</td><td>58.9</td><td>28.4</td><td>36.5</td><td>67.7</td><td>69.7</td><td>66.6</td><td>69.1</td><td>74.4</td><td>75.0</td><td>63.4</td><td>67.2</td></tr><tr><td>DataFlow-Text2SQL-50K</td><td>69.9</td><td>76.8</td><td>75.1</td><td>80.1</td><td>51.4</td><td>57.6</td><td>28.0</td><td>36.4</td><td>65.9</td><td>68.1</td><td>61.3</td><td>67.5</td><td>69.6</td><td>73.5</td><td>60.2</td><td>65.7</td></tr><tr><td>DataFlow-Text2SQL-90K</td><td>71.4</td><td>76.4</td><td>75.8</td><td>80.0</td><td>54.6</td><td>56.8</td><td>55.5</td><td>56.3</td><td>66.5</td><td>67.7</td><td>61.6</td><td>67.3</td><td>71.4</td><td>72.7</td><td>65.3</td><td>68.2</td></tr><tr><td colspan="17">Trained on Qwen2.5-Coder-7B-Instruct</td></tr><tr><td>SynSQL(50K)</td><td>77.1</td><td>82.1</td><td>81.8</td><td>84.8</td><td>54.0</td><td>59.3</td><td>33.1</td><td>44.1</td><td>67.1</td><td>69.5</td><td>68.0</td><td>70.6</td><td>77.2</td><td>80.3</td><td>65.5</td><td>70.1</td></tr><tr><td>SynSQL(90K)</td><td>79.2</td><td>83.1</td><td>82.3</td><td>84.4</td><td>56.2</td><td>59.4</td><td>31.4</td><td>41.4</td><td>65.0</td><td>70.7</td><td>67.2</td><td>70.7</td><td>77.0</td><td>79.9</td><td>65.5</td><td>69.9</td></tr><tr><td>SynSQL(2.5M)</td><td>81.2</td><td>81.6</td><td>87.9</td><td>88.3</td><td>63.9</td><td>66.1</td><td>34.9</td><td>40.0</td><td>76.1</td><td>77.8</td><td>69.7</td><td>69.6</td><td>76.2</td><td>78.0</td><td>70.0</td><td>71.6</td></tr><tr><td>Spider+BIRD+DataFlow-Text2SQL-90K</td><td>85.5</td><td>87.5</td><td>87.5</td><td>88.5</td><td>58.3</td><td>64.0</td><td>27.9</td><td>39.8</td><td>71.0</td><td>73.1</td><td>75.0</td><td>76.2</td><td>82.3</td><td>83.7</td><td>69.6</td><td>73.3</td></tr><tr><td>DataFlow-Text2SQL-50K</td><td>80.9</td><td>84.9</td><td>84.6</td><td>85.8</td><td>57.9</td><td>62.5</td><td>27.8</td><td>39.4</td><td>69.7</td><td>71.2</td><td>70.0</td><td>74.0</td><td>77.8</td><td>82.1</td><td>67.0</td><td>71.4</td></tr><tr><td>DataFlow-Text2SQL-90K</td><td>82.0</td><td>85.0</td><td>84.8</td><td>86.0</td><td>59.2</td><td>61.5</td><td>56.1</td><td>58.7</td><td>69.7</td><td>71.0</td><td>69.9</td><td>74.4</td><td>79.5</td><td>81.7</td><td>71.6</td><td>74.0</td></tr></table>

dataset, and 14,491 from the EHRSQL-train [36] dataset. DATAFlow pipeline ensures rich syntactic and semantic diversity in SQL structures, question phrasing, and multi-step reasoning processes.

For our method (DATAFLOW-Text2SQL rows in Table 7), models are fine-tuned exclusively on our synthesized corpus, unless otherwise specified. For evaluation, we adopt six widely recognized Text-to-SQL benchmarks: Spider [70], BIRD [40], EHRSQL [36], Spider-DK [18], Spider-Syn [17], and Spider-Realistic [14]. During inference with LLMs, we investigate two decoding strategies: greedy decoding (denoted as Gre), which uses temperature 0 for deterministic output generation, and majority voting (denoted as Maj). The majority voting strategy samples 8 candidate responses per input at temperature 0.8, executes all valid SQL queries, and selects the query whose execution result appears most frequently among the candidates as the final prediction. We additionally randomly sampled 50K instances to construct DATAFLOW-Text2SQL-50K. For comparison, we also randomly sampled the same number of instances from SynSQL [37].

# 7.4.2 Experimental Results

As shown in Table 7, the generated data leads to consistent performance improvements across multiple mainstream benchmarks, demonstrating the effectiveness of DATAFLOW [4]. For both models, Meta-Llama-3.1-8B-Instruct [21] and Qwen2.5-Coder-7B-Instruct [29], training on our generated data significantly improves performance over their respective baselines as well as other competing models. When fine-tuned on the generated data, Qwen2.5-Coder-7B-Instruct achieves notable gains: execution accuracy (Gre) on Spider-dev increases from 73.4 to 82.0 (+8.6), on BIRD-dev from 50.9 to 59.2 (+8.3), and on the challenging EHRSQL benchmark from 24.3 to 56.1 (+31.8). These results confirm that DATAFLOW-TEXT2SQL-90K exhibits high quality and strong training utility.

Compared with other training datasets, our data also demonstrates clear advantages. At comparable

data scales, models trained on DATAFLOW-TEXT2SQL-90K and DATAFLOW-TEXT2SQL-50K consistently outperform those trained on SynSQL [37] (SynSQL(90K) and SynSQL(50K), respectively). Specifically, on the Spider-test and BIRD-dev datasets, the model trained on DATAFLOW-TEXT2SQL-50K achieves 84.6 and 57.9 execution accuracy (Gre), surpassing SynSQL(50K) [37], which obtains 81.8 and 54.0. Likewise, the model trained on DATAFLOW-TEXT2SQL-90K not only surpasses the baseline models but also outperforms SynSQL(90K) [37]. Remarkably, even when trained on a much smaller dataset, the model fine-tuned with DATAFLOW-TEXT2SQL-90K achieves performance comparable to SynSQL-2.5M [37] on several challenging benchmarks. These improvements highlight the higher quality of the training data generated by DATAFLOW.

# 7.5 AgenticRAG Data Preparation

# 7.5.1 Experimental Setting

In the field of AgenticRAG, the automatic generation of multihop questions has long been a challenging issue in research. This study constructs a multihop question dataset with a scale of 10k based on the DataFlow AgenticRAG Pipeline and conducts a comparative analysis with existing mainstream multihop question answering datasets (2WikiMultiHopQA [25], Musique [58], HotpotQA [68], and Bamboogle [51]).

The specific workflow of the dataset generation pipeline is as follows:

- Documents are randomly selected from the Wikipedia dump to form the initial document set. To avoid the interference of data distribution overlap on the experimental results, documents that have already appeared in the test benchmark are excluded.  
- The o4-mini model combined with the generation module of DATAFLOW AgenticRAG is used to generate the initial draft of multihop questions based on the filtered initial documents.  
- The verification module is employed to screen the quality of the initial question drafts, eliminating samples with problems such as intermediate question leakage, logical errors, and excessively high or low difficulty, ultimately forming a high-quality multihop question dataset, which we call DATAFLOW_ACENTICRAG-10K.

This study adopts the ReCall [9] framework to complete the model training and evaluation. In the training phase, Qwen2.5-7B-Instruct is selected as the base model, and the GRPO reinforcement learning algorithm is used for model optimization. In the evaluation phase, the model's temperature parameter is set to 0.0.

For the retrieval component, E5-base-v2 [59] is chosen as the retriever, and the 2018 Wikipedia dump is used as the corpus. All corpus indexing and embedding calculations are preprocessed using FlashRAG [32]. Throughout the entire training and evaluation process, the model is allowed to independently specify the topk value for retrieval, and the default topk value is set to 5 to balance retrieval efficiency and performance.

# 7.5.2 Experimental Results

Table 8 reports the exact-match performance across four multi-hop benchmarks. We group the results by the training dataset and compute an out-of-distribution (OOD) average by removing the in-domain test set of each dataset (e.g., HotpotQA-trained models exclude HotpotQA). To fairly compare against our synthetic data, we additionally report DF-OOD (matched), which applies the same in-domain exclusion to DF-AgenticRAG-10k.

Comparison with HotpotQA-trained models. Across 1-3 epochs, HotpotQA-10k achieves OOD averages of 33.7, 35.1, and 36.4. Under the same exclusion (w/o HotpotQA), DF-AgenticRAG achieves 33.8, 35.9, and 37.4—consistently matching or surpassing HotpotQA by  $+0.1$  to  $+1.0$  points despite using entirely synthetic supervision. This indicates that DF-AgenticRAG provides generalization comparable to a widely used human-constructed dataset.

Comparison with Musique-trained models. Musique-20k yields an OOD average of 42.4 when evaluated w/o Musique. Under the same exclusion, DF-AgenticRAG (2 epochs effective scale  $= 20\mathrm{k}$ ) reaches 43.6, outperforming Musique by +1.2 points. This shows that our synthetic dataset not only matches but outperforms a strong human-annotated multi-hop benchmark at the same effective training scale.

Table 8 AgenticRAG Pipeline: Performance comparison between synthetic datasets and existing human-constructed datasets. All values are Exact Match (%). "OD-Avg" excludes the in-domain test set of each training dataset. "DF-OOD (matched)" provides the OOD score of DF-AgenticRAG under the *same* in-domain exclusion, ensuring fair comparison.  

<table><tr><td>Training Data</td><td>HotpotQA</td><td>2Wiki</td><td>Musique</td><td>Bamboogle</td><td>Avg</td><td>OOD-Avg</td><td>DF-OOD (matched)</td></tr><tr><td>Qwen-2.5-7B-Instruct</td><td>25.0</td><td>25.8</td><td>9.9</td><td>27.2</td><td>22.0</td><td>-</td><td>-</td></tr><tr><td colspan="8">Trained on HotpotQA (in-domain = HotpotQA)</td></tr><tr><td>HotpotQA-10k (1 epoch)</td><td>40.2</td><td>41.9</td><td>16.7</td><td>42.4</td><td>35.3</td><td>33.7</td><td>33.8</td></tr><tr><td>HotpotQA-10k (2 epochs)</td><td>43.4</td><td>44.9</td><td>18.9</td><td>41.6</td><td>37.2</td><td>35.1</td><td>35.9</td></tr><tr><td>HotpotQA-10k (3 epochs)</td><td>45.3</td><td>48.0</td><td>20.3</td><td>40.8</td><td>38.6</td><td>36.4</td><td>37.4</td></tr><tr><td colspan="8">Trained on Musique (in-domain = Musique)</td></tr><tr><td>Musique-20k (1 epoch)</td><td>41.1</td><td>44.7</td><td>19.2</td><td>41.6</td><td>36.6</td><td>42.4</td><td>43.6</td></tr><tr><td colspan="8">Trained on 2Wiki (in-domain = 2Wiki)</td></tr><tr><td>2Wiki-30k (2 epochs)</td><td>41.3</td><td>55.1</td><td>17.8</td><td>42.4</td><td>39.1</td><td>33.8</td><td>36.4</td></tr><tr><td colspan="8">DF-AgenticRAG (raw results, for reference)</td></tr><tr><td>DataFlow-AgenticRAG-10k (1 epoch)</td><td>39.3</td><td>42.6</td><td>17.3</td><td>41.6</td><td>34.3</td><td>-</td><td>-</td></tr><tr><td>DataFlow-AgenticRAG-10k (2 epochs)</td><td>43.1</td><td>44.6</td><td>19.9</td><td>43.2</td><td>37.7</td><td>-</td><td>-</td></tr><tr><td>DataFlow-AgenticRAG-10k (3 epochs)</td><td>42.6</td><td>45.5</td><td>20.2</td><td>46.4</td><td>38.7</td><td>-</td><td>-</td></tr></table>

Table 9 Knowledge Extraction: Accuracy comparison on PubMedQA, Covert, and PubHealth under different reasoning and training settings.  

<table><tr><td>Method (ACC)</td><td>PubMedQA</td><td>Covert</td><td>PubHealth</td></tr><tr><td>CoT</td><td>36.40%</td><td>48.33%</td><td>29.00%</td></tr><tr><td>RAG</td><td>43.33%</td><td>17.55%</td><td>19.60%</td></tr><tr><td>SFT (DataFlow-Knowledge)</td><td>53.40%</td><td>68.33%</td><td>40.86%</td></tr></table>

Comparison with 2Wiki-trained models. 2Wiki-30k achieves an OOD average of 33.8. Under the same exclusion (w/o 2Wiki), DF-AgenticRAG (3 epochs, effective scale=30k) reaches 36.4, a substantial improvement of +2.6 points. This represents the largest gap among all baselines and highlights the strong cross-dataset generalization capacity of our synthetic questions.

Summary. Across all training regimes and all in-domain exclusions, DF-AgenticRAG-10k is either the best or tied for the best OOD dataset, and in several cases (Musique, 2Wiki) significantly surpasses human-constructed datasets. These results demonstrate that our pipeline produces multi-hop reasoning data with superior cross-dataset generalization, suggesting that high-quality synthetic data can not only match but consistently exceed the robustness of existing human-annotated multi-hop datasets.

# 7.6 Knowledge Extraction

# 7.6.1 Experimental Setting

To expand beyond the limited annotated data and take advantage of massive raw corpora from the Internet, we proposed the Knowledge Extraction pipeline, a semi-automated system for corpus cleaning and QA synthesis. The pipeline performs text normalization using MinerU [46], segments long documents, filters noisy or low-quality sentences, generates factuality-aware QA pairs, and conducts automated quality checks, ultimately producing a high-quality synthetic dataset used for supervised fine-tuning (SFT).

In our experiment, the training data is derived from 140M tokens of raw medical data drawn from three major sources. The first source is MedQA Books, a collection of 18 widely used medical textbooks from the USMLE curriculum [31]. The second source consists of 9,330 publicly available StatPearls articles from the NCBI Bookshelf [66]. The third source contains 45,679 clinical guideline documents aggregated from 16 professional guideline providers [10]. These corpora serve as the input to the Knowledge Extraction pipeline,

which converts them into structured, high-quality QA dataset, denoted as DATAFLOW-KNOWLEDGE which is suitable for model training.

For model training, we fine-tune Qwen2.5-7B-Instruct on the DATAFLOW-generated dataset. The SFT process is performed for 37,500 steps over five epochs. For comparison, we also evaluate a zero-shot Chain-of-Thought (CoT) prompting baseline and a retrieval-augmented generation (RAG) baseline using top- $k = 10$  retrieval with medcpt-query-encoder as the retriever and medcpt-article-encoder as the document encoder. All baselines share same hyperparameter setting during inference time.

We evaluate our models on three medical QA benchmarks: PubMedQA [33], which focuses on biomedical research questions; Covert [45], which evaluates clinical knowledge and reasoning; and PubHealth [34], which targets public-health misinformation classification.

# 7.6.2 Experimental Results

Table 9 presents the accuracy results across all benchmarks. The CoT baseline performs poorly across the board, indicating that zero-shot reasoning alone is insufficient for medical question answering without more targeted supervision. The RAG baseline provides modest improvement on PubMedQA, but remains unstable and substantially underperforms on Covert and PubHealth, suggesting that retrieval alone cannot substitute for explicit training on structured domain data.

In contrast, the SFT model trained on DATAFLOW-KNOWLEDGE synthetic data achieves the highest accuracy on all benchmarks, surpassing both CoT prompting and RAG-based methods by large margins. Notably, it delivers more than 15-20 absolute accuracy gains on PubMedQA and Covert, and an 11-point improvement on PubHealth, demonstrating that the cleaned and structured QA pairs produced by our Knowledge Extraction pipeline offer significantly stronger supervision.

Overall, these results show that high-quality synthetic QA data—when curated and verified through a targeted DATAFLOW pipeline—can substantially enhance the domain reasoning capabilities of a general-purpose model, outperforming both inference-time prompting and retrieval-augmented baselines.

# 7.7 Unified Multi-Domain Data Preparation with DataFlow

# 7.7.1 Experimental Setting

Data Construction To evaluate the efficiency and effectiveness of unified data preparation across modality-specific reasoning tasks, we construct an integrated training corpus that combines Math, Code, and General Instruction data. All data are generated or filtered through the DATAFLOW framework as follows:

- Math. We synthesize high-quality mathematical problems and chain-of-thought (CoT) solutions using the DATAFLOW Reasoning Pipeline, with the MATH dataset serving as seed input. We randomly sample 3k instances for training.  
- Code. Code data are produced using the DATAFLOW CodeGenDataset_APIPipeline, built upon 20k randomly sampled LingoCoder SFT examples. We generate 1k-10k high-quality code instructions and benchmark against Code Alpaca and SC2-Exec-Filter. A subset of 2k samples is used for training.  
- Text / General Instruction. For natural language tasks, we employ the DATAFLOW Condor Generator + Refiner pipeline to generate high-consistency instruction-response and dialogue pairs. Outputs are further processed by the SFT-quality filtering pipeline. We randomly sample 5k instances.

All models are fine-tuned on the combined DATAFLOW-INSTRUCT-10K corpus using full-parameter SFT. Evaluation covers: (1) seven math benchmarks, (2) four code benchmarks, and (3) MMLU [23] and C-Eval [27] for general knowledge and reasoning.

Baselines. We additionally compare DATAFLOW-INSTRUCT-10K with baselines constructed from the Infinity-Instruct (Inf) [39] dataset, a large-scale general-purpose instruction corpus widely used in instruction tuning. Two baselines are included:

Table 10 Performance of DATAFLOW-INSTRUCT-10K on Math Benchmarks: Qwen2-7B-Base and Qwen2.5-7B-Base finetuned series of models (Exact Match %).  

<table><tr><td>Model</td><td>MATH</td><td>GSM8K</td><td>AMC23</td><td>AIME24</td><td>Minerva</td><td>Gaokao</td><td>Olympiad</td><td>Math-Avg</td></tr><tr><td colspan="9">Models based on Qwen2-7B</td></tr><tr><td>Qwen2-7B-Base</td><td>21.2</td><td>55.9</td><td>15.0</td><td>0.0</td><td>9.9</td><td>30.8</td><td>7.7</td><td>20.1</td></tr><tr><td>+ Inf-10K</td><td>45.6</td><td>81.7</td><td>25.0</td><td>3.3</td><td>11.8</td><td>24.2</td><td>11.1</td><td>29.0</td></tr><tr><td>+ Inf-1M</td><td>45.4</td><td>79.2</td><td>25.0</td><td>0.0</td><td>13.2</td><td>22.0</td><td>10.4</td><td>27.9</td></tr><tr><td>+ DataFlow-Instruct-10K</td><td>54.0</td><td>83.0</td><td>27.5</td><td>0.0</td><td>16.5</td><td>25.3</td><td>20.3</td><td>32.4</td></tr><tr><td>Qwen2-7B-Instruct</td><td>53.9</td><td>86.2</td><td>22.5</td><td>3.3</td><td>17.6</td><td>35.2</td><td>19.6</td><td>34.0</td></tr><tr><td colspan="9">Models based on Qwen2.5-7B</td></tr><tr><td>Qwen2.5-7B-Base</td><td>62.8</td><td>67.1</td><td>45.0</td><td>10.0</td><td>17.6</td><td>27.5</td><td>29.6</td><td>37.1</td></tr><tr><td>+ Inf-10K</td><td>40.2</td><td>30.9</td><td>25.0</td><td>3.3</td><td>9.2</td><td>27.5</td><td>21.8</td><td>22.6</td></tr><tr><td>+ Inf-1M</td><td>50.6</td><td>82.0</td><td>27.5</td><td>0.0</td><td>22.1</td><td>30.8</td><td>20.0</td><td>33.3</td></tr><tr><td>+ DataFlow-Instruct-10K</td><td>73.8</td><td>88.2</td><td>47.5</td><td>16.7</td><td>30.9</td><td>31.9</td><td>37.6</td><td>46.7</td></tr><tr><td>Qwen2.5-7B-Instruct</td><td>75.1</td><td>92.4</td><td>47.5</td><td>10.0</td><td>34.9</td><td>48.4</td><td>40.6</td><td>49.8</td></tr></table>

Table 11 Performance of DATAFLOW-INSTRUCT-10K on Code and Knowledge benchmarks: Qwen2-7B-Base and Qwen2.5-7B-Base finetuned models.  

<table><tr><td>Model</td><td>HumanEval</td><td>MBPP</td><td>Code-Avg</td><td>MMLU</td><td>C-EVAL</td><td>Knowledge-Avg</td></tr><tr><td colspan="7">Models based on Qwen2-7B</td></tr><tr><td>Qwen2-7B-Base</td><td>66.5</td><td>66.1</td><td>66.3</td><td>69.6</td><td>82.8</td><td>76.2</td></tr><tr><td>+ Inf-10K</td><td>64.0</td><td>71.7</td><td>67.8</td><td>69.3</td><td>83.0</td><td>76.2</td></tr><tr><td>+ Inf-1M</td><td>65.9</td><td>70.4</td><td>68.2</td><td>69.5</td><td>83.0</td><td>76.2</td></tr><tr><td>+ DataFlow-Instruct-10K</td><td>64.6</td><td>67.7</td><td>66.2</td><td>69.4</td><td>82.8</td><td>76.1</td></tr><tr><td>Qwen2-7B-Instruct</td><td>73.8</td><td>65.3</td><td>69.6</td><td>69.9</td><td>82.0</td><td>76.0</td></tr><tr><td colspan="7">Models based on Qwen2.5-7B</td></tr><tr><td>Qwen2.5-7B-Base</td><td>78.7</td><td>74.3</td><td>76.5</td><td>71.9</td><td>80.0</td><td>76.0</td></tr><tr><td>+ Inf-10K</td><td>77.4</td><td>77.8</td><td>77.6</td><td>71.8</td><td>79.9</td><td>75.8</td></tr><tr><td>+ Inf-1M</td><td>78.0</td><td>78.0</td><td>78.0</td><td>72.2</td><td>79.4</td><td>75.8</td></tr><tr><td>+ DataFlow-Instruct-10K</td><td>80.5</td><td>76.7</td><td>78.6</td><td>72.1</td><td>80.2</td><td>76.2</td></tr><tr><td>Qwen2.5-7B-Instruct</td><td>81.7</td><td>79.4</td><td>80.6</td><td>71.8</td><td>79.6</td><td>75.7</td></tr></table>

- Inf-10K: a random 10k subset of Infinity-Instruct used for SFT.  
- Inf-1M: a random 1M subset of Infinity-Instruct.

Comparing against Inf-10K/1M allows us to assess whether high-quality, domain-specific synthetic data (math, code, text) generated through DATAFlow provides more stable and reliable improvements than large generic instruction data.

# 7.7.2 Experimental Results

Across Math, Code, and Knowledge evaluation suites, our unified multi-domain data preparation strategy provides consistent and robust gains for both Qwen2.5-7B and Qwen2-7B models. A notable pattern observed across all tables is that DATAFLOW-INSTRUCT-10K almost always achieves the best performance among all non-Instruct finetuned models, and in many cases narrows the gap to the Instruct models to within only 2-4 points, despite using orders-of-magnitude less data.

Math Reasoning. As shown in Table 10, DATAFlow-processed math data yields the largest and most stable gains. For Qwen2.5-7B-Base, training on our synthesized math subset improves the overall score from 37.1 to 46.7, which is:

- the best performance among all non-Instruct models, surpassing Inf-10K (22.6) and Inf-1M (33.3) by a clear margin;  
- only 3.1 points below the Instruct model (49.8), demonstrating that targeted, high-quality synthetic data can nearly match the performance of costly human-aligned instruction tuning.

A similar trend holds for Qwen2-7B: DATAFLOW-INSTRUCT-10K reaches 32.4 overall, outperforming Inf-10K and Inf-1M, and approaching the Instruct model (34.04). These results highlight that DATAFLOW math synthesis produces significantly more stable and effective improvements than generic inference-generated data.

Code Generation. As shown in Table 11, DATAFLOW-INSTRUCT-10K consistently delivers the best Code-Overall performance among all non-Instruct models. For Qwen2.5-7B-Base, DATAFLOW-INSTRUCT-10K raises Code-Overall from 76.5 to 78.6, outperforming Inf-10K (77.6) and Inf-1M (78.0), and reaching within 2.0 points of the Instruct model (80.6). For Qwen2-7B-Base, DATAFLOW-INSTRUCT-10K again matches or exceeds all Inf baselines.

These results show that adding multi-domain synthetic data does not harm code ability (a common issue in mixed-domain SFT), and often improves it. This further supports the robustness of DATAFLOW's domain-balanced synthetic corpus.

General Knowledge and NLP. As summarized in Table 11, our unified dataset also preserves strong general knowledge and reasoning. Across MMLU and C-Eval, DF-Gen-10K:

- matches or slightly improves upon the Base models,  
- avoids the regressions frequently observed in Inf-10K and Inf-1M,  
- frequently ranks second only to the Instruct model, confirming that DATAFLOW-generated text data provides high-quality supervision even without human instruction tuning.

Summary. Together, these results demonstrate that high-quality, domain-specialized synthetic data generated via DATAFLOW produces the strongest non-Instruct performance across Math, Code, and Knowledge. DATAFLOW-INSTRUCT-10K consistently outperforms generic inference-generated data (Inf-10K/Inf-1M) and often approaches the performance of the Instruct models themselves. This highlights the effectiveness of DATAFLOW's unified, pipeline-driven data preparation for building multi-capability LLMs without reliance on large-scale human-authored instruction corpora.

# 7.8 Agentic Orchestration

# 7.8.1 Experimental Setting

We evaluate the proposed agent orchestration framework on realistic data processing and pipeline construction tasks. Specifically, we selected 6 representative pipelines as benchmarks. For each pipeline, we manually constructed natural language task descriptions at 3 difficulty levels, resulting in 18 user queries to assess automatic orchestration capabilities across varying description granularities. The difficulty levels are defined as follows:

- Easy. Descriptions are explicit, directly specifying the functions of required operators (or key operators) and the main processing steps.  
- Medium. Descriptions are coarse, providing only general processing goals and key constraints without explicitly listing the complete operator sequence.  
- Hard. Only a high-level requirement or final goal is provided with minimal hints regarding intermediate steps, requiring the system to infer the complete processing flow and operator combination.

For each task, the user provides a natural language description of the goal, and the system must automatically orchestrate a pipeline composed of multiple operators to meet the requirement.

Evaluation Metrics. To quantitatively assess orchestration quality, we employ an external LLM as an automatic judge. The evaluator compares the generated pipeline against ground truth under two distinct settings:

- Text Specification Alignment. The predicted graph is evaluated against text specifications to verify if the pipeline structure satisfies the detailed task requirements.  
- Code Implementation Consistency. The pipeline is compared with reference Python implementations to assess logical equivalence regarding operator usage and processing steps.

Based on these comparisons, we report the LLM-Judge Score ( $s \in [0,1]$ ), which measures the consistency of operator coverage and execution order between the generated pipeline and the reference under the corresponding evaluation setting.

# 7.8.2 Experimental Results

Table 12 Agent orchestration performance by evaluation mode and description difficulty.  

<table><tr><td>Metric</td><td>Easy</td><td>Medium</td><td>Hard</td><td>Overall</td></tr><tr><td colspan="5">Text spec evaluation (pipeline mode)</td></tr><tr><td>Avg. LLM-Judge</td><td>0.92</td><td>0.86</td><td>0.60</td><td>0.80</td></tr><tr><td colspan="5">Code GT evaluation (code mode)</td></tr><tr><td>Avg. LLM-Judge</td><td>0.60</td><td>0.59</td><td>0.23</td><td>0.49</td></tr></table>

Table 12 reports the LLM-Judge scores under text-spec (pipeline) and code-GT (code) evaluations across difficulty levels. Overall, the framework performs well when judged against textual requirements (0.80 overall), but is markedly lower when matching reference implementations (0.49 overall), reflecting the stricter nature of code-level equivalence. Performance degrades as descriptions become less explicit: in pipeline mode scores drop from 0.92/0.86 (Easy/Medium) to 0.60 (Hard), while in code mode the drop is more severe, reaching 0.23 on Hard, indicating that under-specified queries often lead to alternative yet plausible operator compositions that diverge from a single ground-truth program.

# 8 Conclusion

In summary, DATAFLOW addresses a critical gap in the data-centric LLM ecosystem by providing the first unified, LLM-driven data preparation framework. It mitigates long-standing challenges in the field—such as the difficulty of sharing, reproducing, and comparing data preparation algorithms—through a modular and user-friendly programming interface. The framework integrates nearly 200 operators, over 80 prompt templates, and unified abstractions for serving and storage, all of which compose into six high-quality pipelines spanning the major LLM data domains. Extensive experiments demonstrate that these pipelines achieve strong, often state-of-the-art results, confirming that DATAFLOW effectively balances the tension between domain-specific customization and system-level standardization.

Built atop this foundation, the DATAFLOW-CLI and DATAFLOW-Agent further amplify extensibility by enabling rapid template generation, natural-language-driven workflow construction, and scalable extension development. Together, these components lay the groundwork for a sustainable and interoperable data preparation ecosystem that can evolve alongside increasingly complex data-centric AI workflows.

Looking forward, we aim to expand the DATAFLOW-Ecosystem along multiple modality axes, including DATAFLOW-TABLE, DATAFLOW-GRAPH, and DATAFLOW-MULTIMODAL, to support richer data types and workflows. We also plan to develop domain-oriented variants, such as DATAFLOW-AI4S and DATAFLOW-INDUSTRY, tailored for large-scale production environments. These extensions will broaden the applicability of DATAFLOW and strengthen its role as a foundational substrate—and a common protocol—for future research, engineering practice, and community-driven innovation in LLM data preparation.