# Qwen3-VL Technical Report

# Qwen Team

https://chat.qwen.ai https://huggingface.co/Qwen https://modelscope.cn/organization/qwen https://github.com/QwenLM/Qwen3-VL

# Abstract

We introduce Qwen3-VL, the most capable vision–language model in the Qwen series to date, achieving superior performance across a broad range of multimodal benchmarks. It natively supports interleaved contexts of up to 256K tokens, seamlessly integrating text, images, and video. The model family includes both dense (2B/4B/8B/32B) and mixture-of-experts (30B-A3B/235B-A22B) variants to accommodate diverse latency–quality trade-offs. Qwen3-VL delivers three core pillars: (i) markedly stronger pure-text understanding, surpassing comparable text-only backbones in several cases; (ii) robust long-context comprehension with a native 256K-token window for both text and interleaved multimodal inputs, enabling faithful retention, retrieval, and crossreferencing across long documents and videos; and (iii) advanced multimodal reasoning across single-image, multi-image, and video tasks, demonstrating leading performance on comprehensive evaluations such as MMMU and visual-math benchmarks (e.g., MathVista and MathVision). Architecturally, we introduce three key upgrades: (i) an enhanced interleaved-MRoPE for stronger spatial–temporal modeling across images and video; (ii) DeepStack integration, which effectively leverages multi-level ViT features to tighten vision–language alignment; and (iii) text-based time alignment for video, evolving from T-RoPE to explicit textual timestamp alignment for more precise temporal grounding. To balance text-only and multimodal learning objectives, we apply square-root reweighting, which boosts multimodal performance without compromising text capabilities. We extend pretraining to a context length of 256K tokens and bifurcate post-training into non-thinking and thinking variants to address distinct application requirements. Furthermore, we allocate additional compute resources to the post-training phase to further enhance model performance. Under comparable token budgets and latency constraints, Qwen3-VL achieves superior performance in both dense and Mixture-ofExperts (MoE) architectures. We envision Qwen3-VL serving as a foundational engine for image-grounded reasoning, agentic decision-making, and multimodal code intelligence in real-world workflows.

![](images/d8436b9b25a27ac44a8e9b0f6683cc9ba9567e45cac05a20554697b37f5485a4.jpg)

![](images/30793b07f1ee11de589e7739626882f4ec01e0703f6adeeb4143ee0928a0161e.jpg)

# 1 Introduction

Vision–language models (VLMs) have achieved substantive progress in recent years, evolving from foundational visual perception to advanced multimodal reasoning across images and video. The rapid advancement of VLMs has given rise to a rapidly expanding landscape of downstream applications—such as long-context understanding, STEM reasoning, GUI comprehension and interaction, and agentic workflows. Crucially, these advances must not erode the underlying large language model’s (LLM’s) linguistic proficiency; multimodal models are expected to match or surpass their text-only counterparts on language benchmarks.

In this report, we present Qwen3-VL and its advances in both general-purpose and advanced applications. Built on the Qwen3 series (Yang et al., 2025a), we instantiate four dense models (2B/4B/8B/32B) and two mixture-of-experts (MoE) models (30B-A3B / 235B-A22B), each trained with a context window of up to 256K tokens to enable long-context understanding. By optimizing the training corpus and training strategy, we preserve the underlying LLM’s language proficiency during vision–language (VL) training, thereby substantially improving overall capability. We release both non-thinking and thinking variants; the latter demonstrates significantly stronger multimodal reasoning capabilities, achieving superior performance on complex reasoning tasks.

We first introduce the architectural improvements, which span three components: 1) Enhanced positional encoding. In Qwen2.5-VL, we used MRoPE as a unified positional encoding scheme for text and vision. We observed that chunking the embedding dimensions into temporal (t), horizontal (h), and vertical (w) groups induces an imbalanced frequency spectrum and hampers long-video understanding. We therefore adopt an interleaved MRoPE that distributes $\mathrm { t , h , }$ and w uniformly across low- and high-frequency bands, yielding more faithful positional representations. 2) DeepStack for cross-layer fusion. To strengthen vision–language alignment, we incorporate the pioneering DeepStack (Meng et al., 2024) mechanism. Visual tokens from different layers of the vision encoder are routed to corresponding LLM layers via lightweight residual connections, enhancing multi-level fusion without introducing extra context length. 3) Explicit video timestamps. We replace the absolute-time alignment via positional encoding used in Qwen2.5-VL with explicit timestamp tokens to mark frame groups, providing a simpler and more direct temporal representation. In addition, on the optimization side, we move from a per-sample loss to a square-root-normalized per-token loss, which better balances the contributions of text and multimodal data during training.

To build a more capable and robust vision–language foundation model, we overhauled our training data in terms of quality, diversity, and structure. Key upgrades include enhanced caption supervision, expanded omni-recognition and OCR coverage, normalized grounding with 3D/spatial reasoning, and new corpora for code, long documents, and temporally grounded video. We further infused chain-ofthought reasoning and high-quality, diverse GUI-agent interaction data to bridge perception, reasoning, and action. Together, these innovations enable stronger multimodal understanding, precise grounding, and tool-augmented intelligence.

Our training pipeline consists of two stages: pretraining and post-training. Pretraining proceeds in four phases: a warm-up alignment phase that updates only the merger (vision–language projection) layers while keeping the rest of the model frozen, followed by full-parameter training with progressively larger context windows at 8K, 32K, and 256K sequence lengths. Post-training comprises three phases: (i) supervised fine-tuning on long chain-of-thought data, (ii) knowledge distillation from stronger teacher models, and (iii) reinforcement learning.

The above innovations equip Qwen3-VL with strong capabilities not only as a robust vision–language foundation model but also as a flexible platform for real-world multimodal intelligence—seamlessly integrating perception, reasoning, and action across diverse application domains. In the following sections, we present the model architecture, training framework, and extensive evaluations that demonstrate its consistent and competitive performance on text, vision, and multimodal reasoning benchmarks.

# 2 Model Architecture

Following Qwen2.5-VL (Bai et al., 2025), Qwen3-VL adopts a three-module architecture comprising a vision encoder, an MLP-based vision–language merger, and a large language model (LLM). Figure 1 depicts the detailed model structure.

Large Language Model: Qwen3-VL is instantiated in three dense variants (Qwen3-VL-2B/4B/8B/32B) and two MoE variants (Qwen3-VL-30B-A3B, Qwen3-VL-235B-A22B), all built upon Qwen3 backbones. The flagship model, Qwen3-VL-235B-A22B, has 235B total parameters with 22B activated per token. It outperforms most VLMs across a broad set of multimodal tasks and surpasses its text-only counterpart on the majority of language benchmarks.

![](images/93c0e008e267b596ac7e939ce370c0ad80d55cb85d3c26a352a790837b97a84a.jpg)  
Figure 1: The Qwen3-VL framework integrates a vision encoder and a language model decoder to process multimodal inputs, including text, images, and video. The vision encoder is specifically designed to handle dynamic, native-resolution visual inputs, mapping them to visual tokens of variable length. To enhance perceptual capability and preserve rich visual information, we incorporate the pioneering DeepStack mechanism, which injects visual tokens from multiple layers of the vision encoder into corresponding layers of the LLM. Furthermore, we adopt Interleaved MRoPE to encode positional information for multimodal inputs with a balanced frequency spectrum, and introduce text-based timestamp tokens to more effectively capture the temporal structure of video sequences.

Vision Encoder: We utilize the SigLIP-2 architecture (Tschannen et al., 2025) as our vision encoder and continue training it with dynamic input resolutions, initialized from official pretrained checkpoints. To accommodate dynamic resolutions effectively, we employ 2D-RoPE and interpolate absolute position embeddings based on input size, following the methodology of CoMP (Chen et al., 2025). Specifically, we default to the SigLIP2-SO-400M variant and use SigLIP2-Large (300M) for small-scale LLMs (2B and 4B).

MLP-based Vision-Language Merger: As in Qwen2.5-VL, we use a two-layer MLP to compress $2 \times 2$ visual features from the vision encoder into a single visual token, aligned with the LLM’s hidden dimension. Additionally, we deploy specialized mergers to support the DeepStack mechanism (Meng et al., 2024), the details of which are fully described in Section 2.2.

# 2.1 Interleaved MRoPE

Qwen2-VL (Wang et al., 2024c) introduced MRoPE to model positional information for multimodal inputs. In its original formulation, the embedding dimensions are partitioned into temporal (t), horizontal (h), and vertical (w) subspaces, each assigned distinct rotary frequencies. This results in an imbalanced frequency spectrum, which subsequent studies have shown to degrade performance on long-video understanding benchmarks. To address this, we redesign the frequency allocation by interleaving the $^ { \mathrm { t , h , } }$ and w components across the embedding dimensions (Huang et al., 2025). This ensures that each spatial–temporal axis is uniformly represented across both low- and high-frequency bands. The resulting balanced spectrum mitigates the original spectral bias and significantly improves long-range positional modeling for video.

# 2.2 DeepStack

We draw inspiration from DeepStack (Meng et al., 2024) and inject visual tokens into multiple layers of the LLM. Unlike the original DeepStack approach, which stacks tokens from multi-scale visual inputs, we extend DeepStack to extract visual tokens from intermediate layers of the Vision Transformer (ViT). This design preserves rich visual information, ranging from low- to high-level representations.

Specifically, as illustrated in Figure 1, we select features from three distinct levels of the vision encoder. Subsequently, dedicated vision–language merger modules project these multi-level features into visual tokens, which are then added directly to the corresponding hidden states of the first three LLM layers.

# 2.3 Video Timestamp

In ${ \mathrm { Q } } { \mathrm { w e n } } 2 . 5 { \mathrm { - V L } } ,$ a time-synchronized variant of MRoPE is employed to endow the model with temporal awareness. However, we identify two key limitations of this approach: (1) By tying temporal position IDs directly to absolute time, the method produces excessively large and sparse temporal position ids for long videos, degrading the model’s ability to understand long temporal contexts. (2) Effective learning under this scheme requires extensive and uniformly distributed sampling across various frame rates (fps), significantly increasing the cost of training data construction.

To address these issues, we adopt a textual token–based time encoding strategy (Chen et al., 2024b), wherein each video temporal patch is prefixed with a timestamp expressed as a formatted text string—e.g., $< 3 . 0$ seconds>. Furthermore, during training, we generate timestamps in both seconds and HMS (hours:minutes:seconds) formats to ensure the model learns to interpret diverse timecode representations. Although this approach incurs a modest increase in context length, it enables the model to perceive temporal information more effectively and precisely, thereby facilitating time-aware video tasks such as video grounding and dense captioning.

# 3 Pre-Training

# 3.1 Training Recipe

We first enhance the vision encoder by conducting continuous training with dynamic resolutions based on the pre-trained SigLIP-2 model. The overall Qwen3-VL model adopts a three-module architecture, comprising this vision encoder, an MLP-based vision–language merger, and a Qwen3 large language model (LLM) backbone. Building on this architecture, our pre-training methodology is systematically structured into four distinct stages, designed to progressively build capabilities from basic alignment to long-context understanding. An overview of these stages is presented in Table 1.

Table 1: Training setup and hyperparameters across different stages for Qwen3-VL.   

<table><tr><td>Stage</td><td>Objective</td><td>Training</td><td>Token Budget</td><td>Sequence Length</td></tr><tr><td>SO</td><td>Vision-Language Alignment</td><td>Merger</td><td>67B</td><td>8,192</td></tr><tr><td>S1</td><td>Multimodal Pre-Training</td><td>All</td><td>~1T</td><td>8,192</td></tr><tr><td>S2</td><td>Long-Context Pre-Training</td><td>All</td><td>~1T</td><td>32,768</td></tr><tr><td>S3</td><td>Ultra-Long-Context Adaptation</td><td>All</td><td>100B</td><td>262,144</td></tr></table>

Stage 0: Vision-Language Alignment. The initial stage (S0) focuses on efficiently bridging the modality gap between the vision encoder and the LLM. Crucially, only the parameters of the MLP merger are trained during this phase, while both the vision encoder and the LLM backbone remain frozen. We utilize a curated dataset of approximately 67B tokens, consisting of high-quality image-caption pairs, visual knowledge collections, and optical character recognition (OCR) data. All training is conducted with a sequence length of 8,192. This alignment-first approach establishes a solid foundation for cross-modal understanding before proceeding to full-parameter training.

Stage 1: Multimodal Pre-Training. Following the initial alignment, Stage 1 (S1) transitions to fullparameter Multimodal Pre-Training. In this phase, we unfreeze all model components—the vision encoder, the merger, and the LLM—for joint end-to-end training. The model is trained on a massive and diverse dataset of approximately 1 trillion (1T) tokens. To maintain the LLM’s strong language abilities, the data mixture is composed of vision-language (VL) data and text-only data. The VL portion is rich and varied, adding interleaved image-text documents, visual grounding tasks, visual question answering (VQA), data from STEM domains, and a small amount of video data to introduce temporal understanding. The sequence length remains at 8,192.

Stage 2: Long-Context Pre-Training. Stage 2 (S2) aims to significantly extend the model’s contextual processing abilities. A key change in this stage is the quadrupling of the sequence length to 32,768, while all model parameters continue to be trainable. Training is conducted on a dataset of approximately 1T tokens, with an adjusted data mixture to support long-context tasks. The proportion of text-only data is increased to bolster long-form text comprehension, while the remaining VL data incorporates a significantly larger volume of video and agent-oriented instruction-following data. This stage is critical for enabling the model to process and reason over longer videos and complex, multi-step tasks.

Stage 3: Ultra-Long-Context Adaptation. The final stage (S3) is a specialized phase designed to push the model’s context window to its operational limits. Here, we dramatically increase the sequence length to 262,144. The model is trained on a more focused 100B token dataset specifically curated for this purpose. The data is also composed of text-only data and VL data, with a strong emphasis on long-video and longdocument understanding tasks. This final adaptation solidifies Qwen3-VL’s proficiency in processing and analyzing extremely long sequential inputs, a key capability for applications like comprehensive document analysis and lengthy video summarization.

# 3.2 Pre-Training Data

# 3.2.1 Image Caption and Interleaved Text-Image Data

To build a robust foundation model for general-purpose vision–language understanding, we significantly expand and refine two core data modalities: image–caption pairs and interleaved text–image sequences. Our strategy emphasizes high-quality, diverse, and semantically rich multimodal grounding, supported by purpose-built models and rigorous filtering pipelines.

Image Caption Data: We curate a large-scale corpus of contemporary, predominantly Chinese–English multilingual image–text pairs from web sources and apply a multi-stage refinement pipeline centered on a specialized Qwen2.5-VL-32B model fine-tuned for recaptioning. This model leverages the original raw text associated with each image to generate more comprehensive, fluent, and fine-grained captions—enriching descriptions of visual elements (e.g., object attributes, spatial layouts, and contextual semantics) while simultaneously improving the linguistic quality and informativeness of the textual component.

Deduplication is performed exclusively on the recaptioned text using semantic similarity metrics, ensuring removal of redundant samples without sacrificing visual diversity. To further enhance coverage of underrepresented concepts, we apply clustering (Johnson et al., 2019; Douze et al., 2024; Diao et al., 2025) over visual embeddings to identify sparse regions in the data distribution and perform targeted augmentation. The result is a high-fidelity caption dataset that balances scale, diversity, and descriptive granularity.

Interleaved Text-Image Data: We collect diverse real-world multimodal documents sourced from recent Chinese and English websites (Laurençon et al., 2023; Zhu et al., 2023; Li et al., $2 0 2 4 \mathrm { c } )$ . All documents undergo domain classification (Wettig et al., 2025) using a lightweight Qwen-based scorer fine-tuned for fine-grained domain identification. Based on validation experiments across domains, we systematically exclude harmful or low-value categories—such as advertisements, promotional content, and clickbait—using the same efficient scorer to filter out undesirable samples.

For book-scale interleaved data, we employ a fine-tuned Qwen2.5-VL-7B model to perform high-accuracy multimodal parsing, precisely extracting and aligning text with embedded figures, diagrams, and photographs. To enable ultra-long context modeling, we construct a specialized subset by merging consecutive pages into sequences of up to 256K tokens, preserving natural page order and multimodal coherence. During preprocessing, we enforce strict quality controls: (i) pure-text or low-alignment segments are removed; (ii) for ultra-long book sequences, we require a minimum page count and a minimum image-to-text ratio to ensure meaningful visual–textual interaction throughout the context. This yields a clean, diverse, and layout-aware interleaved corpus optimized for both grounded understanding and long-range multimodal reasoning.

# 3.2.2 Knowledge

World knowledge is essential for multimodal large language models (MLLMs) to achieve robust visual understanding, grounded reasoning, and entity-aware generation across diverse downstream tasks. To equip Qwen3-VL with a comprehensive grasp of both real-world and fictional concepts, we construct a large-scale pretraining dataset centered on well-defined entities spanning more than a dozen semantic categories—including animals, plants, landmarks, food, and everyday objects such as vehicles, electronics, and clothing.

Real-world entities follow a long-tailed distribution: prominent concepts appear frequently with highquality annotations, while the majority are rare. To address this imbalance, we adopt an importance-based sampling strategy. High-prominence entities are sampled more heavily to ensure a sufficient learning signal, while low-prominence entities are included in smaller proportions to maintain broad coverage without overwhelming the training process. This approach effectively balances data quality, utility, and diversity.

All retained samples undergo a multi-stage refinement pipeline. In addition to standard filtering for noise and misalignment, we replace original or sparse captions—such as generic alt-text—with richer, LLM-generated descriptions. These enhanced captions not only identify the main entity but also describe its visual attributes, surrounding context, spatial layout, and interactions with other objects or people, thereby providing a more complete and grounded textual representation.

Together, these efforts yield a knowledge-rich, context-aware, and discrimination-focused training signal that significantly enhances Qwen3-VL’s ability to recognize, reason about, and accurately describe visual concepts in real-world scenarios.

# 3.2.3 OCR, Document Parsing and Long Document Understanding

OCR: To enhance OCR performance on real-world images, we curate a dataset of 30 million in-house collected samples using a coarse-to-fine pipeline. This pipeline refines OCR annotations by integrating pseudo-labels from OCR-specialized models with refinements from Qwen2.5-VL—without any human annotation. Expanding beyond the 10 languages supported by Qwen2.5-VL (excluding Chinese and English), we incorporate an additional 29 languages, synthesizing approximately 30 million high-quality multilingual OCR samples and curating over 1 million internal real-world multilingual images.

Document Parsing: For document parsing, we collect 3 million PDFs from Common Crawl, evenly distributed across 10 document types (300K samples each), along with 4 million internal documents. An in-house layout model first predicts the reading order and bounding boxes for textual and non-textual regions; Qwen2.5-VL-72B then performs region-specific recognition. The outputs are reassembled into position-aware, layout-aligned parsing data.

To ensure robust parsing across heterogeneous formats, we design a unified annotation framework supporting two representations:

• QwenVL-HTML, which includes fine-grained, element-level bounding boxes; • QwenVL-Markdown, where only images and tables are localized, with tables encoded in LaTeX

We construct a large-scale synthetic HTML corpus with precise annotations and systematically convert it to Markdown format. To further improve model generalization, we generate pseudo-labels on extensive collections of real documents and filter them for quality. The final training set combines synthetic and high-quality pseudo-labeled data to enhance both scalability and robustness.

Long Document Understanding: To enhance the model’s ability to understand multi-page PDFs—often spanning dozens of pages—we leverage a large-scale corpus of long-document data. First, we synthesize long-document parsing sequences by merging single-page document samples. In each sequence, multiple page images are placed at the beginning, followed by their corresponding text derived from OCR or HTML parsing. Second, we construct long-document visual question answering (VQA) data. Specifically, we sample high-quality multi-page PDFs and generate a diverse set of VQA examples that require the model to reason across multiple pages and heterogeneous document elements—such as charts, tables, figures, and body text. We carefully balance the distribution of question types and ensure that supporting evidence draws from a wide range of modalities and layout components, thereby promoting robust, grounded, and multi-hop reasoning over extended contexts.

# 3.2.4 Grounding and Counting

Visual grounding is a fundamental capability for multimodal models, enabling them to accurately identify, interpret, and localize a wide spectrum of visual targets from specific objects to arbitrary image regions. In Qwen3-VL, we systematically enhance grounding proficiency and support two grounding modalities: bounding boxes and points. These representations allow for precise and flexible interpretation of image content across diverse scenarios and downstream tasks. In addition, we extend the grounding capacity of the model to support counting, enabling quantitative reasoning about visual entities. In the following, we briefly describe the data construction pipelines for grounding and counting.

Box-based Grounding: We begin by aggregating widely used open-source datasets, including COCO (Lin et al., 2014), Objects365 (Shao et al., 2019), OpenImages (Kuznetsova et al., 2020), and $\mathrm { R e f C O C O / + / g }$ (Kazemzadeh et al., 2014; Mao et al., 2016). To further enrich data diversity, we developed an automated synthesis pipeline that generates high-quality object annotations across a broad range of scenarios. This pipeline operates in three stages: (i) object candidates are extracted from unlabeled images using Qwen2.5-VL; (ii) these candidates are localized and annotated using both open-vocabulary detectors (specifically, Grounding DINO (Liu et al., 2023a)) and Qwen2.5-VL; and (iii) the resulting annotations undergo quality assessment, with low-confidence or inaccurate ones systematically filtered out. Through this approach, we constructed a large-scale, highly diverse box-based grounding dataset spanning a wide variety of visual contexts and object categories.

Point-based Grounding: To ensure robust point-based grounding, we curated a comprehensive dataset combining publicly available and synthetically generated pointing annotations. It integrates three sources: (i) public pointing and counting annotations from PixMo (Deitke et al., 2024); (ii) object grounding data derived from public object detection and instance segmentation benchmarks; and (iii) high-precision pointing annotations generated by a dedicated synthesis pipeline designed to target fine-grained image details.

Counting: Building upon the grounding data, we curated a high-quality subset to form the basis of our counting dataset, which includes three distinct task formulations: direct counting, box-based counting, and point-based counting. Collectively, these three task types constitute a comprehensive counting dataset.

Different from Qwen2.5-VL, we adopt a normalized coordinate system scaled to the range [0, 1000] in this version. This design improves robustness to variations in image resolution and aspect ratio across diverse inputs, while also simplifying post-processing and enhancing the usability of predicted coordinates in downstream applications.

# 3.2.5 Spatial Understanding and 3D Recognition

To facilitate sophisticated interaction with the physical world, Qwen3-VL is designed with a deep understanding of spatial context. This enables the model to interpret spatial relationships, infer object affordances, and perform action planning and embodied reasoning. It can also estimate the 3D spatial positions of objects from a single monocular image. To support these capabilities, we created two comprehensive datasets focused on Spatial Understanding and 3D Grounding.

Spatial Understanding. Beyond localizing objects, Qwen3-VL is trained to reason about spatial relationships, object affordances, and feasible actions in 2D scenes—capabilities essential for embodied AI and interactive applications. To this end, we construct a specialized dataset that goes beyond standard grounding by incorporating: (i) relational annotations (e.g., “the cup to the left of the laptop”), (ii) affordance labels (e.g., “graspable”, “pressable”, “sittable”), and (iii) action-conditioned queries that require planning (e.g., “What should I move first to reach the book behind the monitor?”). These samples are derived from both curated real-world scenes and synthetically generated layouts, with natural language queries automatically generated via templated and LLM-based methods to ensure diversity and complexity. Critically, all spatial references are expressed relative to other objects or scene frames, rather than absolute coordinates, encouraging robust relational reasoning. This training enables Qwen3-VL to not only answer “where” questions but also “how” and “what can be done” — forming a foundation for agentic interaction with visual environments.

3D Grounding. To further enhance the model’s ability to understand the physical world from images, we constructed a specialized pretraining dataset for 3D visual grounding. We sourced data from public collections of diverse indoor and outdoor scenes and reformulated it into a visual question-answering format. Each sample consists of: 1) a single-view camera image, 2) a natural language referring expression, and 3) the corresponding 9-DoF 3D bounding box annotations in a structured JSON format, specifying the object’s spatial position and semantic label. As the 3D bounding boxes are derived from multiple sensors and data sources, they exhibit varying camera intrinsic parameters and inherent noise. To this end, we filter out heavily occluded and inaccurate labels and follow Omni3D (Brazil et al., 2023) to unify all data into a virtual camera coordinate system. We also synthesized a large corpus of descriptive captions to create rich textual queries for 3D grounding. These descriptions go beyond naming the object’s category to include detailed attributes, layout arrangements, spatial location, visual affordances, and interactions with surrounding objects—yielding more fine-grained and grounded referring expressions.

# 3.2.6 Code

We enhance the Qwen3-VL series with dedicated coding capabilities by incorporating two categories of code-related data into the training corpus, enabling the model to read, write, and reason about programs in both text-only and visually grounded contexts.

Text-Only Coding. We reuse the extensive code corpus from the Qwen3 and Qwen3-Coder series. This large-scale dataset spans a wide range of programming languages and domains—including software development, algorithmic problem solving, mathematical reasoning, and agent-oriented tasks—and establishes the model’s foundational understanding of code syntax, algorithmic logic, and generalpurpose program generation.

Multimodal Coding. To address tasks requiring both visual understanding and code generation, we curate data for a diverse suite of multimodal coding tasks. This dataset, sourced from both open-source datasets and internal synthesis pipelines, teaches the model to jointly understand visual inputs and generate functional code. The data covers several key tasks, including: converting UI screenshots into responsive HTML/CSS; generating editable SVG codes from images (Li et al., 2025c); solving visual programming challenges (Li et al., 2024a); answering multimodal coding questions (e.g., StackOverflow posts with images); and transcribing visual representations (such as flowcharts, diagrams, and LATEX equations) into their respective code or markup. This novel data mixture enables Qwen3-VL to act as a bridge between visual perception and executable logic.

# 3.2.7 Video

The video comprehension capabilities of Qwen3-VL have been substantially advanced, enabling robust modeling of temporal dynamics across frames, fine-grained perception of spatial relationships, and coherent summarization of ultra-long video sequences. This enhancement is underpinned by a data processing pipeline featuring two principal innovations:

Temporal-Aware Video Understanding. (i) Dense Caption Synthesis: For long video sequences, we employ a short-to-long caption synthesis strategy to generate holistic, timestamp-interleaved, and temporally coherent story-level descriptions. Leveraging in-house captioning models, we further produce fine-grained annotations that jointly capture event-level temporal summaries and segment-specific visual details. (ii) Spatio-Temporal Video Grounding: We curate and synthesize large-scale video data annotated at the levels of objects, actions, and persons to strengthen the model’s spatio-temporal grounding capabilities, thereby improving its capacity for fine-grained video understanding.

Video Data Balancing and Sampling. (i) Source Balancing: To ensure data balance and diversity, we assemble a large-scale dataset encompassing various video sources, including instructional content, cinematic films, egocentric recordings, etc. Dataset balance is achieved through systematic curation guided by metadata such as video titles, duration, and categorical labels. (ii) Length-Adaptive Sampling: During pre-training stages, we dynamically adjust sampling parameters, such as frames per second (fps) and the maximum number of frames, according to different sequence length constraints. This adaptive strategy mitigates information loss associated with suboptimal sampling practices (e.g., overly sparse frame selection or excessively low spatial resolution), thus preserving visual details and optimizing training efficacy.

# 3.2.8 Science, Technology, Engineering, and Mathematics (STEM)

Multimodal reasoning lies at the heart of Qwen3-VL, with STEM reasoning constituting its most essential part. Our philosophy follows a divide-and-conquer strategy: we first develop fine-grained visual perception and robust linguistic reasoning capabilities independently, and then integrate them in a synergistic manner to achieve effective multimodal reasoning.

Visual Perception Data. We develop a dedicated synthetic data generation pipeline that constructs geometric diagrams through programmatic (code-based) rendering. Using this pipeline, we generate: (i) 1 million point-grounding samples, such as intersection points, corners, and centers of gravity; and (ii) 2 million perception-oriented visual question answering pairs targeting fine-grained visual understanding of diagrams. To obtain high-fidelity textual descriptions, we further implement a two-stage captioning framework: an initial generation phase followed by rigorous model-based verification. Both stages employ ensembles of specialized models to ensure accuracy and descriptive granularity. This process yields a comprehensive dataset of 6 million richly annotated diagram captions spanning diverse STEM disciplines.

Multi-modal Reasoning Data. The majority of our multi-modal reasoning data consists of over 60 million K–12 and undergraduate-level exercises, meticulously curated through a rigorous cleaning and reformulation pipeline. During quality filtering, we discard low-quality items, including those with corrupted images, irrelevant content, or incomplete or incorrect answers. During the reformulation stage, we translate exercises between Chinese and English and standardize the format of answers—such as step-by-step solution lists, mathematical expressions, and symbolic notations—to ensure consistency and uniform presentation. Regarding long CoT problem-solving data, we synthesize over 12 million multimodal reasoning samples paired with images. To ensure the continuity and richness of the reasoning process, we utilize the original rollouts generated by a strong reasoning model. To guarantee data reliability and applicability, each sample’s reasoning trajectory undergoes rigorous validation—combining rule-based checks and model-based verification—and any instances containing ambiguous answers or code-switching are explicitly filtered out. Furthermore, to enhance reasoning quality, we retain only challenging problems via rejection sampling.

Linguistic Reasoning Data. In addition to multimodal reasoning data, we also incorporate reasoning data from Qwen3, as multimodal reasoning capabilities are largely derived from linguistic reasoning competence.

# 3.2.9 Agent

GUI: To endow Qwen3-VL with agentic capability for autonomous interaction with graphical user interfaces (GUIs), we curate and synthesize large-scale, cross-platform data spanning desktop, mobile, and web environments (Ye et al., 2025; Wang et al., 2025a; Lu et al., 2025). For GUI interface perception, we leverage metadata, parsing tools, and human annotations to construct tasks such as element description, dense captioning, and dense grounding, enabling robust understanding of diverse user interfaces. For agentic capability, we assemble multi-step task trajectories via a self-evolving trajectory-production framework, complemented by targeted human audits; we also carefully design and augment Chainof-Thought rationales to strengthen planning, decision-making, and reflective self-correction during real-world execution.

Function Calling: For general function calling capabilities with multimodal contexts, we build a multimodal function calling trajectory synthesis pipeline. We first instruct capable models with images to generate user queries and their corresponding function definitions. We then sample model function calls with rationales and synthesize the function responses. This process is repeated until the user’s query is judged to be solved. Between each step, trajectories can be filtered out due to formatting errors. Such a pipeline enables us to construct large-scale multimodal function-calling trajectories from vast images, without the need to implement executable functions.

Search: Among the general function calling capabilities, we regard the ability to perform searches as key to facilitating knowledge integration for long-tail entities in real-world scenarios. In this case, we collect multimodal factual lookup trajectories with online image search and text search tools, encouraging the model to perform searches for unfamiliar entities. By doing so, the model learns to gather information from the web to generate more accurate responses.

# 4 Post-Training

# 4.1 Training Recipe

Our post-training pipeline is a three-stage process designed to refine the model’s instruction-following capabilities, bolster its reasoning abilities, and align it with human preferences. The specific data and methods for each stage are detailed in the subsequent sections.

Supervised Fine-Tuning (SFT). The first stage imparts instruction-following abilities and activates latent reasoning skills. This is conducted in two phases: an initial phase at a 32k context length, followed by an extension to a 256k context window that focuses on long-document and long-video data. To cater to different needs, we bifurcate the training data into standard formats for non-thinking models and Chain-of-Thought (CoT) formats for thinking models, the latter of which explicitly models the reasoning process.

Strong-to-Weak Distillation. The second stage employs knowledge distillation, where a powerful teacher model transfers its capabilities to our student models. Crucially, we perform this distillation using text-only data to fine-tune the LLM backbone. This method proves highly effective, yielding significant improvements in reasoning abilities across both text-centric and multimodal tasks.

Reinforcement Learning (RL). The final stage utilizes RL to further enhance model performance and alignment. This phase is divided into Reasoning RL and General RL. We apply large-scale reinforcement learning across a comprehensive set of text and multimodal domains, including but not limited to math, OCR, grounding, and instruction-following, to improve finer-grained capabilities.

# 4.2 Cold Start Data

# 4.2.1 SFT Data

Our principal objective is to endow the model with the capacity to address a wide spectrum of realworld scenarios. Building upon the foundational capabilities of ${ \mathrm { Q } } { \mathrm { w e n } } 2 . 5 { \mathrm { - V L } } ,$ which is proficient in approximately eight core domains and 30 fine-grained subcategories, we have strategically expanded its functional scope. This expansion was achieved by integrating insights from community feedback, academic literature, and practical applications, facilitating the introduction of novel capabilities. These include, but are not limited to, spatial reasoning for embodied intelligence, image-grounded reasoning for fine-grained visual understanding, spatio-temporal grounding in videos for robust object tracking, and the comprehension of long-context technical documents spanning hundreds of pages. Guided by these target tasks and grounded in authentic use cases, we systematically curated the SFT dataset through the meticulous selection and synthesis of samples from open-source datasets and web resources. This targeted data engineering effort has been instrumental in establishing Qwen3-VL as a more comprehensive and robust multimodal foundation model.

This dataset comprises approximately 1,200,000 samples, strategically composed to foster robust multimodal capabilities. This collection is partitioned into unimodal and multimodal data, with one-third consisting of text-only entries and the remaining two-thirds comprising image-text and video-text pairs. The integration of multimodal content is specifically designed to enable the model to interpret complex, real-world scenarios. To ensure global relevance, the dataset extends beyond its primary Chinese and English corpora to include a diverse set of multilingual samples, thereby broadening its linguistic coverage. Furthermore, it simulates realistic conversational dynamics by incorporating both single-turn and multiturn dialogues contextualized within various visual settings, from single-image to multi-image sequences. Crucially, the dataset also features interleaved image-text examples engineered to support advanced agentic behaviors, such as tool-augmented image search and visually-grounded reasoning. This heterogeneous data composition ensures comprehensive coverage and enhances the dataset’s representativeness for training generalizable and sophisticated multimodal agents.

Given Qwen3-VL’s native support for a 256K token context length, we employ a staged training strategy to optimize for computational efficiency. This strategy comprises two phases: an initial one-epoch training phase with a sequence length of 32K tokens, followed by a second epoch at the full 256K token length. During this latter stage, the model is trained on a curriculum that interleaves long-context inputs with data sampled at the 32K token length. The long-context inputs include materials such as hundreds of pages of technical documents, entire textbooks, and videos up to two hours in duration.

The quality of training data is a critical determinant of the performance of vision-language models. Datasets derived from open-source and synthetic origins are often plagued by substantial variability and noise, including redundant, irrelevant, or low-quality samples. To mitigate these deficiencies, the implementation of a rigorous data filtering protocol is indispensable. Accordingly, our data curation process incorporates a two-phase filtering pipeline: Query Filtering and Response Filtering.

Query Filtering. In this initial phase, we leverage Qwen2.5-VL to identify and discard queries that are not readily verifiable. Queries with ambiguous instructions are minimally revised to enhance clarity while preserving the original semantic intent. Furthermore, web-sourced queries lacking substantive content are systematically eliminated. Crucially, all remaining queries undergo a final assessment of their complexity and contextual relevance, ensuring only appropriately challenging and pertinent samples are retained for the next stage.

Response Filtering. This phase integrates two complementary strategies:

Rule-Based Filtering: A set of predefined heuristics is applied to eliminate responses exhibiting qualitative deficiencies, such as repetition, incompleteness, or improper formatting. To maintain semantic relevance and uphold ethical principles, we also discard any query-response pairs that are off-topic or possess the potential to generate harmful content.

• Model-Based Filtering: The dataset is further refined by employing reward models derived from the Qwen2.5-VL series. These models conduct a multi-dimensional evaluation of multimodal questionanswering pairs. Specifically: (a) answers are scored against a range of criteria, including correctness, completeness, clarity, and helpfulness; (b) for vision-grounded tasks, the evaluation places special emphasis on verifying the accurate interpretation and utilization of visual information; and (c) this model-based approach enables the detection of subtle issues that typically elude rule-based methods, such as inappropriate language mixing or abrupt stylistic shifts.

This multi-dimensional filtering framework ensures that only data meeting stringent criteria for quality, reliability, and ethical integrity is advanced to the SFT phase.

# 4.2.2 Long-CoT Cold Start Data

The foundation of our thinking models is a meticulously curated Long Chain-of-Thought (CoT) cold start dataset, engineered to elicit and refine complex reasoning capabilities. This dataset is built upon a diverse collection of queries spanning both pure-text and multimodal data, maintaining an approximate 1:1 ratio between vision-language and text-only samples to ensure balanced skill development.

The multimodal component, while covering established domains such as visual question answering (VQA), optical character recognition (OCR), 2D/3D grounding, and video analysis, places a special emphasis on enriching tasks related to STEM and agentic workflows. This strategic focus is designed to push the model’s performance on problems requiring sophisticated, multi-step inference. The pure-text portion closely mirrors the data used for Qwen3, featuring challenging problems in mathematics, code generation, logical reasoning, and general STEM.

To guarantee high quality and an appropriate level of difficulty, we implement a rigorous multi-stage filtering protocol.

• Difficulty Curation: We selectively retain instances where baseline models exhibited low pass rates or generated longer, more detailed responses. This enriches the dataset with problems that are genuinely challenging for current models.   
• Multimodal Necessity Filtering: For vision-language mathematics problems, we introduce a critical filtering step: we discard any samples that our Qwen3-30B-nothink model could solve correctly without access to the visual input. This ensures that the remaining instances genuinely necessitate multimodal understanding and are not solvable via textual cues alone.   
• Response Quality Control: Aligning with the methodology of Qwen3, we sanitize the generated responses. For queries with multiple candidate answers, we first remove those containing incorrect final results. Subsequently, we filter out responses exhibiting undesirable patterns, such as excessive repetition, improper language mixing, or answers that showed clear signs of guessing without sufficient reasoning steps.

This stringent curation process yields a high-quality, challenging dataset tailored for bootstrapping advanced multimodal reasoning.

# 4.3 Strong-to-Weak Distillation

We adopt the Strong-to-Weak Distillation pipeline as described in Qwen3 to further improve the performance of lightweight models. This distillation process consists of two main phases:

• Off-policy Distillation: In the first phase, outputs generated by teacher models are combined to provide response distillation. This helps lightweight student models acquire fundamental reasoning abilities, establishing a strong foundation for subsequent on-policy training. • On-policy Distillation: In the second phase, the student model generates the responses based on the provided prompts. These on-policy sequences are then used for fine-tuning the student model. We align the logits predicted by the student and teacher by minimizing the KL divergence.

# 4.4 Reinforcement Learning

# 4.4.1 Reasoning Reinforcement Learning

We train models across a diverse set of text and multimodal tasks, including mathematics, coding, logical reasoning, visual grounding, and visual puzzles. Each task is designed so that solutions can be verified deterministically via rules or code executors.

Data Preparation We curate training data from both open-source and proprietary sources and apply rigorous preprocessing and manual annotation to ensure high-quality RL queries. For multimodal queries, we use a preliminary checkpoint of our most advanced vision–language model (Qwen3-VL-235BA22B) to sample 16 responses per query; any query for which all responses are incorrect is discarded.

We then run preliminary RL experiments per task to identify and remove data sources with limited potential for improvement. This process yields approximately 30K RL queries covering a variety of text and multimodal tasks. For training each model, we sample 16 responses for all queries and filter out easy queries whose pass rate exceeds $9 0 \%$ . We shuffle and combine task-specific datasets to construct mixed-task batches, ensuring a consistent, predefined ratio of samples per task. The ratio is determined through extensive preliminary experiments.

Reward System We implement a unified reward framework that delivers precise feedback across all tasks. The system provides shared infrastructure—data preprocessing, utility functions, and a reward manager to integrate multiple reward types—while the core reward logic is implemented per task. We use task-specific format prompts to guide model outputs to the required formats and therefore do not rely on explicit format rewards. To mitigate code-switching, we apply a penalty when the response language differs from the prompt language.

RL Algorithm We employ SAPO (Gao et al., 2025), a smooth and adaptive policy-gradient method, for RL training. SAPO delivers consistent improvements across diverse text and multimodal tasks and across different model sizes and architectures.

# 4.4.2 General Reinforcement Learning

The General Reinforcement Learning (RL) stage is designed to enhance the model’s generalization capabilities and operational robustness. To this end, we employ a multi-task RL paradigm where the reward function is formulated based on a comprehensive set of tasks from the SFT phase, including VQA, image captioning, OCR, document parsing, grounding, and clock recognition. The reward mechanism is structured to optimize two principal dimensions of model performance:

• Instruction Following: This dimension evaluates the model’s adherence to explicit user directives. It assesses the ability to handle complex constraints on content, format, length, and structured outputs (e.g., JSON), ensuring the generated response precisely matches user requirements. • Preference Alignment: For open-ended or subjective queries, this dimension aligns the model’s outputs with human preferences by optimizing for helpfulness, factual accuracy, and stylistic appropriateness. This fosters a more natural and engaging user interaction.

Furthermore, this stage acts as a corrective mechanism to unlearn strong but flawed knowledge priors ingrained during SFT. We address this by introducing specialized, verifiable tasks designed to trigger these specific errors, such as counter-intuitive object counting and complex clock time recognition. This targeted intervention is designed to supplant erroneous priors with factual knowledge.

Another critical objective is to mitigate inferior behaviors like inappropriate language mixing, excessive repetition, and formatting errors. However, the low prevalence of these issues makes general RL a sample-inefficient correction strategy. To overcome this, we curate a dedicated dataset at this stage. This dataset isolates prompts known to elicit such undesirable behaviors. This focused training enables the application of targeted, high-frequency penalties, effectively suppressing these residual errors.

Feedback for the RL process is delivered via a hybrid reward system that combines two complementary approaches:

• Rule-Based Rewards: This approach provides unambiguous, high-precision feedback for tasks with verifiable ground truths, such as format adherence and instruction following. By using well-defined heuristics, this method offers a robust mechanism for assessing correctness and effectively mitigates reward hacking, where a model might exploit ambiguities in a learned reward function. • Model-Based Rewards: This method employs Qwen2.5-VL-72B-Instruct or Qwen3 as sophisticated judgers. The judge models evaluate each generated response against a ground-truth reference, scoring its quality across multiple axes. This approach offers superior flexibility for assessing nuanced or openended tasks where strict, rule-based matching is inadequate. It is particularly effective at minimizing false negatives that would otherwise penalize valid responses with unconventional formatting or phrasing.

# 4.5 Thinking with Images

Inspired by the great prior works on "thinking with images" (Wu et al., 2025a; Jin et al., 2025; Zheng et al., 2025; Lai et al., 2025), we endow Qwen3-VL with similar agentic capabilities through a two-stage training paradigm.

In the first stage, we synthesize a cold-start agentic dataset comprising approximately $1 0 \mathrm { k }$ grounding examples—primarily simple two-turn visual question answering tasks such as attribute detection. We then perform supervised fine-tuning (SFT) on Qwen2.5-VL-32B to emulate the behavior of a visual agent: $t h i n k  a c t $ analyze feedback answer. To further enhance its reasoning abilities, we apply multi-turn, tool-integrated reinforcement learning (RL).

In the second stage, we distill the trained Qwen2.5-VL-32B visual agents from the first stage to generate a larger, more diverse dataset of approximately 120k multi-turn agentic interactions spanning a broader range of visual tasks. We then apply a similar cold-start SFT and tool-integrated RL pipeline (now using both distilled and synthesized data) for the post-training of Qwen3-VL.

The multi-turn, tool-integrated RL procedure is nearly identical across both stages, differing only in the underlying data. During $\scriptstyle \mathrm { { R L , } }$ we employ three complementary reward signals to encourage robust, tool-mediated reasoning:

• Answer Accuracy Reward leverages Qwen3-32B to measure whether the final answer is correct.   
• Multi-Turn Reasoning Reward leverages Qwen2.5-VL-72B to evaluate whether the assistant correctly interprets tool or environment feedback and arrives at the answer through coherent, step-by-step reasoning.   
• Tool-Calling Reward encourages appropriate tool usage by comparing the actual number of tool calls to an expert-estimated target. This target is determined offline by Qwen2.5-VL-72B based on task complexity.

Early experiments reveal a tendency for models to degenerate into making only a single tool call to hack the first two rewards, regardless of task demands. To mitigate this, we explicitly incorporate the tool-calling reward to promote adaptive tool exploration aligned with task complexity.

# 4.6 Infrastructure

We train the Qwen3-VL series models on Alibaba Cloud’s PAI-Lingjun AI Computing Service, which provides the high-performance computing power required for compute-intensive scenarios such as AI and high-performance computing.

During the pretraining phase, the system employs a hybrid parallelism strategy built upon the MegatronLM framework, integrating Tensor Parallelism (TP), Pipeline Parallelism (PP), Context Parallelism (CP), Expert Parallelism (EP), and ZeRO-1 Data Parallelism (DP). This configuration achieves a fine-grained balance among model scale, computational load, and communication overhead, enabling high hardware utilization and sustaining both high throughput and low communication latency—even at scales of up to 10,000 GPUs.

For local deployment and performance evaluation, we adopt deployment strategies based on either vLLM or SGLang. vLLM utilizes PagedAttention to enable memory-efficient management and high-throughput inference, while SGLang excels at structured generation and handling complex prompts. Together, these backends provide efficient inference and evaluation with stable, efficient, and flexible model inference capabilities.

# 5 Evaluation

# 5.1 General Visual Question Answering

To comprehensively assess the general visual question answering (VQA) capabilities of the Qwen3-VL series, we conduct extensive evaluations on a diverse set of benchmarks, including MMBench-V1.1 (Liu et al., 2023b), RealWorldQA (xAI, 2024), MMStar (Chen et al., 2024a), and SimpleVQA (Cheng et al., 2025). As detailed in Table 2, Table 3 and Table 4, the Qwen3-VL family demonstrates robust and highly competitive performance across a wide spectrum of model sizes, from 2B to 235B parameters.

In the comparison of thinking mode, Qwen3-VL-235B-A22B-Thinking achieves the highest score of 78.7 on MMStar. Gemini-2.5-Pro’s (Comanici et al., 2025) Thinking mode delivers the best overall performance, but Qwen3-VL-235B-A22B-Thinking is not far behind. In the non-reasoning mode comparison, Qwen3- VL-235B-A22B-Instruct obtains the highest scores on MMBench and RealWorldQA, with 89.3/88.9 and 79.2, respectively.

In the experiments with medium-sized models, Qwen3-VL-32B-Thinking achieves the highest scores on MMBench and RealWorldQA, with 89.5/89.5 and 79.4, respectively. Notably, Qwen3-VL-32B-Instruct even outperforms the Thinking variant on RealWorldQA, scoring 79.0.

The scalability of the Qwen3-VL series is evident in the strong performance of our smaller models. Specifically, the largest model, Qwen3-VL-8B, achieves the highest performance across all five benchmarks. For example, on MMBench-EN, the score in "thinking" mode increases from 79.9 for the 2B model to 85.3 for the 8B model. A similar upward trend is observed on other benchmarks, such as MMStar, where the score rises from 68.1 (2B, thinking) to 75.3 (8B, thinking).

# 5.2 Multimodal Reasoning

We evaluate the Qwen3-VL series on a wide range of multimodal reasoning benchmarks, primarily focusing on STEM-related tasks and visual puzzles, including MMMU (Yue et al., 2024a), MMMUPro (Yue et al., 2024b), MathVision (Wang et al., 2024b), MathVision-Wildphoto (hereafter MathVisionWP) , MathVista (Lu et al., 2023), We-Math (Qiao et al., 2024), MathVerse (Zhang et al., 2024), DynaMath (Zou et al., 2024), Math-VR (Duan et al., 2025), LogicVista (Xiao et al., 2024), VisualPuzzles (Song et al., 2025b), VLM are Blind (Rahmanzadehgervi et al., 2025), ZeroBench (Main/Subtasks) (Roberts et al., 2025), and VisuLogic (Xu et al., 2025). As shown in Table 2, the flagship Qwen3-VL model demonstrates outstanding performance across both “non-thinking” and “thinking” models. Notably, Qwen3-VL-235B-A22B-Instruct achieves the best reported results among non-thinking or low-thinking-budget models on multiple benchmarks, including MathVistamini, MathVision, MathVersemini, DynaMath, ZeroBench, VLMsAreBlind, VisuLogic, and VisualPuzzlesDirect. While, Qwen3-VL-235B-A22B-Thinking achieves state-of-the-art results on MathVista $\mathrm { \ m i n i }$ , MathVision, MathVersemini, ZeroBench, LogicVista, and VisuLogic.

Among medium-sized models, as shown in Table 3, Qwen3-VL-32B demonstrates significant advantages, consistently outperforming Gemini-2.5-Flash and GPT-5-mini. Compared to the previous-generation Qwen2.5-VL-72B model, the medium-sized Qwen3-VL model has already surpassed it on reasoning tasks. This highlights significant progress in VLMs. Additionally, our newly introduced Qwen3-VL-30B-A3B MoE model also delivers competitive results.

Among small-sized models, we compare Qwen3-VL-2B/4B/8B against GPT-5-Nano, with results presented in Table 4. The 8B variant maintains a clear advantage overall, while the 4B model achieves the highest scores on DynaMath and VisuLogic. Notably, even the smallest 2B model exhibits strong reasoning capabilities.

# 5.3 Alignment and Subjective Tasks

The ability to follow complex user instructions and reduce potential image-level hallucinations is indispensable for current large vision language models (VLMs). We assess our models on three representative benchmarks: MM-MT-Bench (Agrawal et al., 2024), HallusionBench (Guan et al., 2023) and MIA-Bench (Qian et al., 2024). MM-MT-Bench is a multi-turn LLM-as-a-judge evaluation benchmark for testing multimodal instruction-tuned models. HallusionBench aims at diagnosing image-context reasoning and poses great challenges for current VLMs. MIA-Bench is a more comprehensive benchmark to evaluate models’ reactions to users’ complex instructions (e.g., creative writing with character limit and compositional instructions).

As shown in Table 2, our flagship Qwen3-VL-235B-A22B model consistently outperforms other closedsource models. On HallusionBench, our thinking version surpasses Gemini-2.5-pro (Comanici et al., 2025), GPT-5 (OpenAI., 2025) and Claude opus 4.1 (Anthropic., 2025) by 3.0, 1.0, and 6.3 points, respectively. On MIA-Bench, Qwen3-VL-235B-A22B-Thinking achieves the overall best score across all the other models, showing our superior multimodal instruction following ability. We also investigate detailed subtask results of MIA-Bench: our model overtakes GPT-5-high-thinking version by 10.0 and 5.0 points in math and textual subtasks of MIA-Bench, respectively. The same trend can be observed on our smaller-sized models like Qwen3-VL-30B-A3B, and Qwen3-VL-32B, where they overtake other models with comparable sizes. Our 2B/4B/8B series also performs well and shows a negligible drop, especially on MIA-Bench.

# 5.4 Text Recognition and Document Understanding

We compare the Qwen3-VL series with other models of comparable size on document-related benchmarks, including OCR, document parsing, document question answering (QA), and document reasoning.

We evaluate our flagship model, Qwen3-VL-235B-A22B, against state-of-the-art VLMs on the benchmarks listed in Table 2. On OCR-focused parsing benchmarks — including CC-OCR (Yang et al., 2024b) and OmniDocBench (Ouyang et al., 2024) — as well as comprehensive OCR benchmarks such as OCRBench (Liu et al., 2024) and OCRBench_v2 (Fu et al., 2024b), the Qwen3-VL-235B-A22B-Instruct model establishes a new state of the art, marginally outperforming its “thinking” counterpart, Qwen3-VL235B-A22B-Thinking. On OCR-related visual question answering (VQA) benchmarks that require both OCR capability and keyword search — such as DocVQA (Mathew et al., 2021b), InfoVQA (Mathew et al., 2021a), AI2D (Kembhavi et al., 2016), ChartQA (Masry et al., 2022), and the CharXiv (Wang et al., $2 0 2 4 \mathrm { g } )$ ) description subset — both the Instruct and Thinking variants achieve comparable performance, demonstrating consistently strong results across these tasks. Notably, on the reasoning subset of CharXiv — which demands deep chart comprehension and multi-step reasoning — the Thinking variant surpasses the Instruct version and ranks second only to GPT5-thinking and Gemini-2.5-Pro-Thinking.

Table 2: Performance of Qwen3-VL-235B-A22B and top-tier models on visual benchmarks. The highest scores of the reasoning and non-reasoning models are shown in bold and underlined, respectively. Results marked with an $^ *$ are sourced from the technical report. $^ +$ denotes results with tool use.   

<table><tr><td></td><td>Benchmark MMMU</td><td>Qwen3-VL 235B-A22B thinking</td><td>instruct 78.7 81.7*</td><td>Gemini 2.5 Pro thinking budget-128</td><td>80.9</td><td>OpenAI GPT-5 high minimal 84.2*</td><td>74.4* 78.4 62.7*</td><td>Claude Opus 4.1 thinkingnon-thinking 77.2 60.7</td></tr><tr><td>STEM Puzzle</td><td>MMMU-Pro MathVistamini MathVision MathVisionwP We-Math MathVersemini DynaMath Math-VR ZeroBench VlmsAreBlind LogicVista VisuLogic VisualPuzzles</td><td>80.6 69.3 85.8 74.6 63.8 74.8 85.0 82.8 66.8 4 79.5 72.2 34.4 57.2</td><td>68.1 84.9 66.5 570 67.5 72.5 794 65.0 2 80.4 65.8 9</td><td>68.8* 82.7* 73.3* 63.2 80.6 82.9 80.0 64.7* 3 86.1 72.0 31.6 60.9</td><td>712 777 66.0 56.9 74.5 65.9 78.5 54.3 1 78.5 68.7 26.9 56.9</td><td>78.4* 81.3 70.9 62.8 73.8 84.1 85.4 58.1 2 80.5 71.8 28.5 57.3</td><td>64.8 50.9 75.5 45.8 64.3 40.1 54.0 51.8 65.2 43.0 70.6 74.0 75.1 21.7 54.3 2 3 53.4 77.8 46.3 67.3 27.2 27.9 47.9 48.8 81.3</td><td>74.5 57.7 46.4 60.2 68.1 72.0 38.0 1 72.2 63.5 272 47.6</td></tr><tr><td>General VQA</td><td>MMBench-EN MMBench-CN RealWorldQA MMStar SimpleVQA HallusionBench</td><td>88.8 88.6 81.3 78.7 61.3</td><td>89.3 889 792 78.4 63.0</td><td>90.1* 89.7* 78.0* 77.5* 65.4 63.7*</td><td>88.4 86.4 76.0 78.5 66.9 60.9</td><td>83.8 83.5 79.9 82.8 77.3 76.4 65.2 61.8 56.7 65.7 53.7</td><td>79.4 84.9 69.9 72.1 56.7 60.4</td><td>83.0 74.3 68.5 71.0 55.7 55.1</td></tr><tr><td>Alignment</td><td>MM-MT-Bench MIA-Bench DocVQAtest InfoVQAtest AI2Dw.M. ChartQAtest</td><td>66.7 8.5 92.7 96.5 89.5 89.2 90.3</td><td>63.2 85 91.3 97.1 892 89.7 90.3</td><td>8.4* 92.3 92.6 84.2 90.9 83.3 866</td><td>7.6 91.3 94.0 82.9 90.0 62.6 872</td><td>7.6 92.4 91.5 79.0 89.7 59.7 810</td><td>7.5 7.8 92.6 91.2 89.6 92.5 69.9 69.4 84.1 86.4 59.1 86.2 787 764</td><td>7.9 90.0 89.2 60.9 84.4 83.9 750</td></tr><tr><td>Document Understanding</td><td>OCRBench OCRBench_v2en OCRBench_V2zh CC-OCR OmniDocBenchen OmniDocBenchzh CharXiv(DQ) CharXiv(RQ) MMLongBenchDoc RefCOCO-avg</td><td>875 66.8 63.5 81.5 0.155 0.207 90.5 66.1 56.2 92.1</td><td>920 671 61.8 82.2 0.143 0.207 89.4 62.1 57.0 91.9</td><td>54.3 55.2 48.5 53.1 77.2 76.8 0.347 0.206 0.238 0.249 94.4 87.8 67.9 62.9 55.6 51.2 74.6*</td><td>53.0 43.2 68.3 0.356 0.472 89.2 81.1* 51.5 66.8</td><td>48.2 37.7 66.1 0.174 0.389 79.5 57.8 42.4 87.8</td><td>48.4 43.7 69.1 0.194 0.293 88.5 63.6 54.5 - 93.1</td><td>47.2 38.0 66.0 1 - 87.8 60.2 48.1 - 91.9</td></tr><tr><td>2D/3D Grounding</td><td>CountBench ODinW-13 ARKitScenes Hypersim SUNRGBD</td><td>93.7 43.2 53.7 11.0 34.9</td><td>930 48.6 56.9 13.0 39.4</td><td>91.0* 33.7* - - 29.7</td><td>91.0 34.5 - - -</td><td>91.7 1 1 - - - 1 1 -</td><td>- - 1 1</td><td>1 1 - 1</td></tr><tr><td>Embodied/Spatial Understanding</td><td>ERQA VSI-Bench EmbSpatialBench RefSpatialBench RoboSpatialHome</td><td>52.5 60.0 84.3 69.9 73.9</td><td>513 627 83.1 65.5 69.4</td><td>55.3 - 79.1 36.5 47.5</td><td>50.3 - 73.3 35.6 49.2</td><td>65.7* 42.0* - 82.9 75.1 23.8 23.1 53.5 43.6</td><td>34.8 - 69.2 - -</td><td>28.0 - 66.0 - -</td></tr><tr><td>Multi-Image</td><td>BLINK MUIRBENCH MVBench</td><td>67.1 80.1 75.2 79.0</td><td>70.7 730 76.5</td><td>70.6* 77.2 69.9</td><td>70.0 74.0 65.8</td><td>71.0 62.8 77.5 66.5 75.3 64.6</td><td>64.1 1 61.4</td><td>62.9 1 59.0</td></tr><tr><td>Video Understanding</td><td>Video-MMEw/o sub. MLVUM-Avg5 LVBench Charades-STAmIoU VideoMMMU MMVU</td><td>83.8 63.6 63.5 80.0 71.1</td><td>79.2 84.3 67.7 64.8 74.7 68.1</td><td>85.1 85.6 73.0 - 83.6*</td><td>80.6 81.2 69.0 - 79.4</td><td>84.7 77.3 86.2 78.3 - 1 - - 84.6* 61.6* 68.1</td><td>75.6 73.5 - - 76.2 66.4</td><td>73.3 71.2 1 - 70.1 61.4</td></tr><tr><td>Perception with Tool</td><td>V* HRBench4K HRBench8K</td><td>85.9 84.3 76.6</td><td>93.7+ 85.4 824</td><td>74.9 83.8 87.3 85.4</td><td>22 72.7 84.8 80.1</td><td>73.0 72.8 1 1</td><td>56.7 1 1 - - -</td><td>- - -</td></tr><tr><td>Multi-Modal Coding</td><td>Design2Code ChartMimic UniSVG ScreenSpot Pro</td><td>93.4 78.4 65.8 61.8</td><td>92.0 80.5 69.8 62.0</td><td>89.2 83.9 70.0</td><td>90.3 79.9 67.9 1</td><td>92.5 88.9 62.1 41.4 71.7 74.5 1</td><td>88.5 85.2 73.0 -</td><td>85.3 82.9 72.5</td></tr><tr><td>Multi-Modal Agent</td><td>OSWorldG AndroidWorld OSWorld WindowsAA</td><td>68.3 62.0 38.1 32.1</td><td>66.7 637 31.6 28.9</td><td>1 45.2 - 1 -</td><td>- 1 1 -</td><td>1 - - -</td><td>1 - 1 1 -</td><td>- - - 1</td><td>1 1 - 44.4 -</td></tr></table>

Table 3: Performance of medium-sized Qwen3-VL models and previous models on visual benchmarks. The highest scores are shown in bold. Results marked with an $^ *$ are sourced from the technical report. $^ +$ denotes results with tool use.   

<table><tr><td></td><td>Benchmark</td><td>Qwen3-VL 30B-A3B thinking</td><td>instruct 74.2</td><td>Qwen3-VL 32B thinking instruct 78.1</td><td>76.0 77.7 67.2</td><td>Gemini 2.5Flash thinkingnon-thinking 76.3</td><td>GPT-5 mini high 79.0</td><td>minimal 67.9 53.7</td></tr><tr><td>STEM Puzzle</td><td>MMMU MMMU-Pro MathVistamini MathVision MathVisionwP We-Math MathVersemini DynaMath Math-VR ZeroBench VlmsAreBlind LogicVista VisuLogic VisualPuzzles</td><td>76.0 63.0 81.9 65.7 58.9 70.0 79.6 80.1 61.7 0 72.5 65.8 26.6 52.0</td><td>60.4 80.1 60.2 52.3 56.9 70.2 73.4 61.3 0 67.5 53.5 23.0 46.2</td><td>68.1 85.9 70.2 58.6 71.6 82.6 82.0 62.3 2 85.1 70.9 32.4</td><td>65.3 83.8 63.4 54.6 63.3 76.8 76.7 59.8 1 87.0 62.2 29.7</td><td>65.9 79.4 75.3 64.3 60.7 53.6 49.0 53.9 60.3 77.7 75.9 75.9 69.7 58.8 54.7 1 3 77.5 75.9 67.3 60.0 31.0 23.3</td><td>67.3 79.1 71.9 56.6 70.2 78.8 81.4 58.2 3 75.8 71.4 27.2 59.3</td><td>59.6 46.6 42.8 51.4 36.5 71.3 26.4 2 62.0 50.8 27.6 48.2</td></tr><tr><td>General VQA</td><td>MMBench-EN MMBench-CN RealWorldQA MMStar SimpleVQA</td><td>87.0 85.9 77.4 75.5 54.3</td><td>86.1 85.3 73.7 72.1 52.7</td><td>54.7 89.5 89.4 78.4 79.4 55.4</td><td>53.2 87.6 87.7 79.0 77.7 56.9</td><td>41.4 87.1 87.3 76.0 76.5 63.2</td><td>45.0 86.6 86.0 75.7 75.8 59.2</td><td>86.6 78.5 84.0 76.3 79.0 73.3 74.1 61.3 56.8</td></tr><tr><td> Alignment</td><td>HallusionBench MM-MT-Bench MIA-Bench DocVQAtest InfoVQAtest</td><td>66.0 7.9 91.6 95.5 85.6</td><td>61.5 8.0 91.2 95.0 81.8</td><td>67.4 8.3 92.3 96.1 89.2</td><td>63.8 8.4 91.8 96.9 87.0</td><td>63.5 59.1 8.1 8.0 91.1 90.6 92.8 93.0 82.5</td><td>63.2 7.7 92.0 90.5 81.7 77.6</td><td>50.3 55.9 7.4 92.3 90.6 72.8</td></tr><tr><td>Document Understanding</td><td>AI2Dw.M. ChartQAtest OCRBench OCRBench_v2en OCRBench_v2zh CC-OCR OmniDocBenchen OmniDocBenchzh CharXiv(DQ) CharXiv(RQ) MMLongBenchDoc RefCOCO-avg</td><td>86.9 89.4 839 62.6 60.4 77.8 0.165 0.233 86.9 56.6 47.4</td><td>85.0 86.8 903 63.2 57.8 80.7 0.183 0.253 85.5 48.9 47.1</td><td>88.9 89.0 855 68.4 62.1 79.6 0.148 0.236 90.2 65.2 54.6</td><td>89.5 88.5 895 67.4 59.2 80.3 0.151 0.239 90.5 62.8 55.4</td><td>88.7 87.7 60.6 69.0 853 864 52.2 50.6 43.8 43.9 75.4 74.8 0.265 0.228 0.245 0.305 90.1 85.5 61.7 60.1 49.0 44.6</td><td>88.2 57.5 821 52.6 45.1 70.8 0.181 0.316 89.4 68.6 50.3</td><td>82.9 57.8 807 45.7 41.0 61.6 0.260 0.425 78.6 48.9 39.6</td></tr><tr><td>2D/3D Grounding</td><td>CountBench ODinW-13 ARKitScenes Hypersim SUNRGBD ERQA</td><td>90.0 42.3 55.6 11.4 34.6</td><td>89.8 47.5 56.1 12.5 38.1</td><td>91.1 94.1 41.8 46.1 12.5 33.9</td><td>91.9 94.9 46.6 55.6 14.0 37.0</td><td>1 1 86.0 83.7 1 1 1 - 1 - -</td><td>1 91.0 1 1 1 1</td><td>84.1 - - 1 1 45.8</td></tr><tr><td>Embodied/Spatial Understanding</td><td>VSI-Bench EmbSpatialBench RefSpatialBench RoboSpatialHome</td><td>45.3 56.1 80.6 54.2 65.5</td><td>43.0 63.2 76.4 53.1 62.9</td><td>52.3 61.2 82.7 67.2 74.2</td><td>48.8 61.5 81.5 61.4 64.6</td><td>1 1 1 1 1 - 1 1 1</td><td>54.0 31.5 80.7 9.0 54.3</td><td>30.5 72.1 4.0 44.6</td></tr><tr><td> Multi-Image</td><td>BLINK MUIRBENCH MVBench Video-MMEw/o sub.</td><td>65.4 77.6 72.0 73.3</td><td>67.7 62.9 72.3 74.5</td><td>68.5 80.3 73.2 77.3</td><td>67.3 72.8 72.8 76.6</td><td>68.1 66.8 72.7 1 79.6</td><td>1 67.5 - 1 1 75.6 78.9</td><td>56.7 57.5 1 71.0</td></tr><tr><td>Video Understanding</td><td>MLVUM-Avg LVBench Charades-STAmIoU VideoMMMU MMVU</td><td>78.9 59.2 62.7 75.0 66.1</td><td>81.3 62.5 63.5 68.7 59.8</td><td>82.3 62.6 62.8 79.0 67.9</td><td>82.1 63.8 61.2 71.9 66.8</td><td>82.1 77.8 64.5 62.2 1 1 73.9 65.2 69.8 68.2</td><td>83.3 1 82.5* 69.8</td><td>71.7 1 1 56.7 64.8</td></tr><tr><td>Perception with Tool</td><td>V* HRBench4K HRBench8K ScreenSpot Pro</td><td>81.2 77.8 71.3 57.3</td><td>89.5+ 82.5+ 79.3+ 60.5</td><td>84.8 82.1 74.8 57.1</td><td>91.1+ 84.6+ 81.6+ 57.9</td><td>1 1 1</td><td>1 - - 1</td><td>78.6 63.9 78.6 66.3 74.4 60.9</td></tr><tr><td>Multi-Modal Agent</td><td>OSWorldG AndroidWorld OSWorld WindowsAA</td><td>59.6 55.0 30.6 24.2</td><td>61.0 54.3 30.3 24.9</td><td>64.0 63.7 41.0 42.9</td><td>65.1 57.3 32.6 30.9</td><td>- 1 1 1 1 - 1 1</td><td>1 1 1 1 1</td><td>1 1 - -</td></tr></table>

![](images/a7ce9c6789b8bbe7a79ec219b8e6e793261eed26993e74bec477c3a6e29162eb.jpg)  
Figure 2: Multilingual OCR performance of our model on a self-built test set. The model achieves over $7 0 \%$ accuracy on 32 out of 39 supported languages, demonstrating strong and usable multilingual capabilities.

Furthermore, among the smaller-sized variants in the Qwen3-VL series, both Qwen3-VL-30BA3B models and Qwen3-VL-32B models consistently outperform Gemini-2.5-Flash and GPT-5-mini across most evaluation metrics, as shown in Table 3. Even the compact dense models — Qwen3-VL-8B, Qwen3-VL-4B, and Qwen3-VL-2B — demonstrate remarkably competitive performance on OCR parsing, visual question answering (VQA), and comprehensive benchmark suites, as detailed in Table 4. This highlights the exceptional efficiency and strong scalability of the Qwen3-VL architecture across model sizes.

In this version of the Qwen3-VL, we have placed particular emphasis on enhancing its ability to understand long documents. As reported in Table 2, in the comparison within the flagship models on the MMLongBench-Doc benchmark (Ma et al., 2024), our Qwen3-VL-235B-A22B achieves overall accuracy of $5 7 . 0 \% / 5 6 . 2 \%$ under the instruct/thinking settings, showcasing the SOTA performance on the long document understanding task.

Beyond its strong performance on established benchmarks, we have also made substantial strides in multilingual support. This represents a major expansion from the 10 non-English/Chinese languages supported by Qwen2.5-VL to 39 languages in Qwen3-VL. We assess this expanded capability on a newly constructed, in-house dataset. As illustrated in Figure 2, the model’s accuracy surpasses $7 0 \%$ —a threshold we consider practical for real-world usability—on 32 out of the 39 languages tested. This demonstrates that the strong OCR capabilities of Qwen3-VL are not confined to a handful of languages but extend across a broad and diverse linguistic spectrum.

# 5.5 2D and 3D Grounding

In this section, we conduct a comprehensive evaluation of the Qwen3-VL series on both 2D and 3D grounding-related benchmarks and compare the models with state-of-the-art models that possess similar capabilities.

We evaluate Qwen3-VL’s 2D grounding capabilities on the referring expression comprehension benchmarks $\mathrm { R e f C O C O / + / g }$ (Kazemzadeh et al., 2014; Mao et al., 2016), the open-vocabulary object detection benchmark ODinW-13 (Li et al., 2022), and the counting benchmark CountBench (Paiss et al., 2023). For

Table 4: Performance of small-sized Qwen3-VL models and GPT-5-nano on visual benchmarks.   

<table><tr><td rowspan="2"></td><td rowspan="2">Benchmark MMMU</td><td colspan="2">Qwen3-VL 2B thinking instruct</td><td colspan="2">Qwen3-VL 4B thinking</td><td colspan="2">Qwen3-VL 8B thinking</td><td colspan="2">OpenAI GPT-5 nano instruct</td></tr><tr><td>61.4 MMMU-Pr0 42.5 MathVistamini 73.6 MathVision 45.9</td><td>53.4 36.5 61.3 31.6 30.9</td><td>70.8 57.0 79.5 60.0 48.7 75.2 74.4</td><td>instruct 67.4 53.2 73.7 51.6 44.4 46.8</td><td>74.1 60.4 81.4 62.7 53.3 77.7</td><td>69.6 55.9 77.2 53.9 45.4</td><td>high 75.8 57.2 71.5 62.2 49.3 74.2 78.0</td><td>minimal 57.6 36.5 40.9 33.2 28.3 27.0 62.0 25.0</td></tr><tr><td>STEM Puzzle</td><td>MathVisionwP MathVersemini DynaMath Math-VR ZeroBench VlmsAreBlind LogicVista VisuLogic VisualPuzzles MMBench-EN MMBench-CN</td><td>35.5 66.9 66.7 37.7 0 50.0 50.0 25.4 37.4 79.9 78.8</td><td>52.1 54.2 20.7 0 56.0 35.8 11.5 34.3 78.4 75.9</td><td>58.1 0 68.6 61.1 30.2 48.9 84.6 83.8</td><td>65.3 52.3 0 71.9 53.2 19.0 43.7 83.9 83.5</td><td>73.2 59.0 2 69.1 65.1 27.5 51.7 85.3 85.5</td><td>62.1 67.7 53.4 1 74.0 55.3 22.5 47.9 84.5 84.7</td><td>49.7 1 66.7 59.7 24.5 43.5 78.4 77.6</td><td>1 40.2 40.5 24.0 31.3 50.8 48.5</td></tr><tr><td>General VQA</td><td>RealWorldQA MMStar SimpleVQA HallusionBench</td><td>69.5 68.1 43.6 54.9 6.9</td><td>63.9 58.3 40.7 51.4 5.9</td><td>73.2 73.2 48.8 64.1 7.7</td><td>70.9 69.8 48.0 57.6 7.5</td><td>73.5 75.3 49.6 65.4 8.0</td><td>71.5 70.9 50.2 61.1 77</td><td>71.8 68.6 46.0 58.4 6.6</td><td>60.7 41.3 39.0 39.3 6.2</td></tr><tr><td>Alignment Document Understanding</td><td>MM-MT-Bench MIA-Bench DocVQAtest InfoVQAtest AI2Dw.M. ChartQAtest OCRBench OCRBench_v2en OCRBench_v2zh CC-OCR OmniDocBenchen</td><td>85.6 92.9 77.1 80.4 86.6 792 56.4 51.9 68.3</td><td>83.6 93.3 72.4 76.9 79.1 858 56.3 53.0 72.8 0.292</td><td>91.0 94.2 83.0 84.9 88.8 808 61.8 55.8 73.8 0.234 0.244</td><td>89.7 95.3 80.3 84.1 84.6 881 63.7 57.6 76.2</td><td>91.5 95.3 86.0 84.9 88.6 819 63.9 59.2 76.3 0.209</td><td>91.1 96.1 83.1 85.7 89.6 896 65.4 61.2 79.9</td><td>89.9 88.2 68.6 81.9 52.1 753 48.1 33.6 58.9</td><td>89.6 78.3 49.2 65.7 48.6 701 37.9 27.3 52.9</td></tr><tr><td>2D/3D Grounding</td><td>CharXiv(DQ) CharXiv(RQ) MMLongBenchDoc RefCOCO-avg CountBench ODinW-13 ARKitScenes</td><td>70.1 37.1 33.8 84.8 84.1 36.0 47.7</td><td>62.3 26.8 31.6 85.6 88.4 43.4 56.2 12.0</td><td>83.9 50.3 44.4 88.2 89.4 39.4 46.3</td><td>76.2 39.7 43.5 89.0 84.9 48.2 56.6</td><td>85.9 53.0 48.0 88.2 91.5 39.8 46.6 12.0</td><td>83.0 46.4 47.9 89.1 80.5 44.7 56.8</td><td>82.0 50.1 31.8 1 80.0 1 1</td><td>64.4 31.7 22.1 1 62.9 1</td></tr><tr><td>Embodied/Spatial Understanding</td><td>Hypersim SUNRGBD ERQA VSI-Bench EmbSpatialBench</td><td>11.2 28.6 41.8 48.0 75.9</td><td>33.8 28.3 53.9 69.2 30.3</td><td>11.9 28.0 47.3 55.2 80.7</td><td>12.2 34.7 41.3 59.3 79.6</td><td>30.4 46.8 56.6 81.1 44.6</td><td>12.7 36.2 45.8 59.4 78.5</td><td>1 45.8 15.4 74.2</td><td>- 1 37.8 27.0 50.7</td></tr><tr><td> Multi-Image</td><td>RefSpatialBench RoboSpatialHome BLINK MUIRBENCH</td><td>28.9 45.3 57.2 68.1</td><td>49.1 53.8 47.4 61.7</td><td>45.3 63.2 63.4 75.0 69.3</td><td>46.6 61.7 65.8 63.8</td><td>62.0 64.7 76.8</td><td>54.2 66.9 69.1 64.4</td><td>12.6 46.1 58.3 65.7</td><td>2.5 44.8 42.2 45.7</td></tr><tr><td>Video Understanding</td><td>MVBench Vide0-MMEw/o sub. MLVUM-Avg LVBench Charades-STAmIoU</td><td>64.5 62.1 69.2 47.6 56.9</td><td>61.9 68.3 47.4 54.5</td><td>68.9 75.7 53.5 59.0</td><td>68.9 69.3 75.3 56.2 55.5</td><td>69.0 71.8 75.1 55.8 59.9</td><td>68.7 71.4 78.1 58.0 56.0</td><td>1 66.2 69.2 1 1</td><td>1 49.4 52.6 1 1</td></tr><tr><td>Perception</td><td>VideoMMMU MMVU V* HRBench4K</td><td>54.1 48.9 69.1 69.4</td><td>41.9 41.7 75.9+ 72.6+</td><td>69.4 58.6 74.9 73.5</td><td>56.2 50.5 88.0+ 81.3+</td><td>72.8 62.0 77.5 72.4</td><td>65.3 58.7 90.1+ 82.3+</td><td>63.0 63.1 1 1</td><td>40.2 51.0 1 1</td></tr><tr><td>with Tool</td><td>HRBench8K ScreenSpot Pro</td><td>62.6 32.2 41.8</td><td>68.9+ 48.5 46.1</td><td>67.1 49.2 53.9</td><td>74.4+ 59.5 58.2</td><td>68.1 46.6 56.7</td><td>78.0+ 54.6 58.2 47.6</td><td>1 1</td><td>1</td></tr><tr><td>Multi-Modal Agent</td><td>OSWorldG AndroidWorld OSWorld WindowsAA</td><td>46.1 19.0 1</td><td>36.4 17.0 1</td><td>52.0 31.4 35.5</td><td>45.3 26.2 23.4</td><td>50.0 33.9 24.1</td><td>33.9 28.8</td><td></td><td></td></tr></table>

ODinW-13, we adopt mean Average Precision (mAP) as the evaluation metric by setting confidence scores to 1.0. To ensure comparability with conventional open-set object detection specialist models, we provide all dataset categories simultaneously within the prompt during evaluation. As shown in Table 2, our flagship model, Qwen3-VL-235B-A22B, demonstrates outstanding performance and achieves state-of-the-art (SOTA) results across 2D grounding and counting benchmarks. Notably, it achieves $4 8 . 6 \ \mathrm { m A P }$ on ODinW-13, demonstrating strong performance in multi-target open-vocabulary object grounding. Detailed results for our smaller-scale variants, which also exhibit competitive performance in 2D visual grounding, are presented in Tables 3 and 4, respectively.

Moreover, in this version of Qwen3- ${ \mathrm { . V L } } ,$ we enhance its spatial perception capabilities for 3D object localization. We evaluate the Qwen3-VL series against other models of comparable scale on Omni3D (Brazil et al., 2023), a comprehensive benchmark comprising datasets such as ARKitScenes (Baruch et al., 2021), Hypersim (Roberts et al., 2021), and SUN RGB-D (Song et al., 2015). We employ mean Average Precision (mAP) as our evaluation metric. Each input is an image-text pair consisting of the image and a textual prompt specifying the object category. To ensure a fair comparison with existing VLMs, we set the IoU threshold to 0.15 and report $\mathrm { m A } \breve { \mathrm { P @ 0 . 1 5 } }$ on the Omni3D test set, with detection confidence fixed at 1.0. As shown in Table 2, our flagship Qwen3-VL-235B-A22B model consistently outperforms other closedsource models across multiple datasets. Specifically, on the SUN RGB-D dataset (Song et al., 2015), the Qwen3-VL-235B-A22B-Thinking variants surpass the performance of Gemini-2.5-Pro by 5.2 points. Our smaller-scale variants (e.g., Qwen3-VL-30BA3B, -32B, -8B, -4B, -2B) also exhibit remarkably competitive performance in 3D object grounding, with detailed results provided in Tables 3 and 4, respectively.

# 5.6 Fine-grained Perception

We measure the models’ fine-grained perception capabilities on three popular benchmarks. The Qwen3- VL series demonstrates a substantial leap in fine-grained visual understanding compared to its predecessor, Qwen2.5-VL-72B. Notably, Qwen3-VL-235B-A22B achieves the state-of-the-art performance across all three benchmarks when augmented with tools—reaching 93.7 on $\mathrm { V } ^ { \ast }$ (Wu &Xie, 2024), 85.3 on HRBench-4k (Wang et al., 2024e), and 82.3 on HRBench-8k (Wang et al., 2024e). This consistent outperformance highlights the effectiveness of architectural refinements and training strategies introduced in Qwen3-VL, particularly in handling high-resolution inputs and subtle visual distinctions critical for fine-grained perception tasks. Second, and perhaps more surprisingly, the performance gains from integrating external tools consistently outweigh those from simply increasing model size. For example, within the Qwen3-VL family, the absolute improvement by adding tools is consistently $\sim 5$ points across $\mathrm { V } ^ { \ast }$ . These findings reinforce our conviction that scaling tool-integrated agentic learning in multimodality is a highly promising path forward.

# 5.7 Multi-Image Understanding

Beyond single-image grounded dialogue evaluation, advancing VLMs to handle multi-image understanding is of significant value. This task requires higher-level contextual analysis across diverse visual patterns, enabling more advanced recognition and reasoning capabilities. To this end, we nourish Qwen3-VL with comprehensive cross-image pattern learning techniques, including multi-image referring grounding, visual correspondence, and multi-hop reasoning. We evaluated Qwen3-VL on two prominent multiimage benchmarks: BLINK (Fu et al., 2024c) and MuirBench (Wang et al., 2024a). As shown in Table 2, Qwen3-VL demonstrates overall superiority in multi-image understanding compared to other leading LVLMs. Specifically, Qwen3-VL-235B-A22B-Instruct achieves performance comparable to state-of-the-art models such as Gemini-2.5-pro, while Qwen3-VL-235B-A22B-Thinking attains a remarkable leading score of 80.1 on MuirBench, surpassing all other models.

# 5.8 Embodied and Spatial Understanding

For embodied and spatial understanding, Qwen3-VL’s performance is rigorously benchmarked against leading SOTA models using a challenging suite of benchmarks: ERQA (Team et al., 2025), VSIBench (Yang et al., 2025b), EmbSpatial (Du et al., 2024), RefSpatial (Zhou et al., 2025), and RoboSpatialHome (Song et al., 2025a). Across these benchmarks, the model showcases exceptional capabilities, rivaling the performance of top-tier models like Gemini-2.5-Pro, GPT-5, and Claude-Opus-4.1. This success is largely driven by the model’s profound spatial understanding, which stems from its training on high-resolution visual data with fine-grained pointing, relative-position annotations, and QA pairs. This capability is clearly validated by its strong results on EmbSpatial, RefSpatial, and RoboSpatialHome, where Qwen3-VL-235BA22 achieves scores of 84.3, 69.9, and 73.9, respectively. Moreover, its embodied intelligence is significantly enhanced through the integration of pointing, grounding, and spatio-temporal perception data during training, leading to top-tier scores of 52.5 on ERQA (Team et al., 2025) and 60.0 on VSIBench (Yang et al.,

# 5.9 Video Understanding

Benefiting from the scaling of training data and key architectural enhancements, Qwen3-VL demonstrates substantially improved video understanding capabilities. In particular, the integration of interleaved MRoPE, the insertion of textual timestamps, and scaling temporally dense video captions collectively enable the Qwen3-VL 8B variant to achieve performance competitive with the significantly larger Qwen2.5-VL 72B model.

We conduct a comprehensive evaluation across a diverse set of video understanding tasks, encompassing general video understanding (VideoMME (Fu et al., 2024a), MVBench (Li et al., 2024b)), temporal video grounding (Charades-STA (Gao et al., 2017)), video reasoning (VideoMMMU (Hu et al., 2025), MMVU (Zhao et al., 2025)), and long-form video understanding (LVBench (Wang et al., 2024d), MLVU (Zhou et al., 2024)). In comparison with state-of-the-art proprietary models — including Gemini 2.5 Pro, GPT-5, and Claude Opus 4.1, Qwen3-VL demonstrates competitive and, in several cases, superior performance. In particular, our flagship model, Qwen3-VL-235B-A22B-Instruct, achieves performance on par with leading models such as Gemini 2.5 Pro (with a thinking budget of 128) and GPT-5 minimal on standard video understanding benchmarks. By extending the context window to 256K tokens, it further attains or even surpasses Gemini-2.5-Pro on long-video evaluation tasks, most notably on MLVU.

Regarding evaluation details, we imposed a cap of 2,048 frames per video for all benchmarks, ensuring that the total number of video tokens did not exceed 224K. The maximum number of tokens per frame was set to 768 for VideoMMMU and MMVU, and to 640 for all other benchmarks. Additionally, videos from Charades-STA were sampled at 4 frames per second (fps), while a rate of 2 fps was used for all other benchmarks. For VideoMMMU, we employed a model-based judge for evaluation, as rule-based scoring proved insufficiently accurate. It is worth noting that our comparison cannot guarantee full fairness due to resource and API limitations, which constrained the number of input frames used during evaluation: 512 for Gemini 2.5 Pro, 256 for GPT-5, and 100 for Claude Opus 4.1.

# 5.10 Agent

We evaluate UI perception with GUI-grounding tasks (ScreenSpot (Cheng et al., 2024), ScreenSpot Pro (Li et al., 2025b), OSWorldG(Xie et al., 2025a)) and assess decision-making abilities through online environment evaluations (AndroidWorld (Rawles et al., 2024), OSWorld (Xie et al., 2025c;b)). For GUI grounding, Qwen3-VL-235B-A22B achieves state-of-the-art performance across multiple tasks, covering interactive interfaces on desktop, mobile, and PC, and demonstrating exceptionally strong UI perception capabilities. For online evaluations, Qwen3-VL 32B scores 41 on OSWorld and 63.7 on AndroidWorld, which surpasses the current foundation VLMs. Qwen3-VL demonstrates exceptionally strong planning, decision-making, and reflection abilities as a GUI agent. Furthermore, smaller Qwen3-VL models have demonstrated highly competitive performance on these benchmarks.

# 5.11 Text-Centric Tasks

To comprehensively evaluate the text-centric performance of Qwen3-VL, we adopt automatic benchmarks to assess model performance on both instruct and thinking models. These benchmarks can be categorized into the following key types: (1) Knowledge: MMLU-Pro (Wang et al., 2024f), MMLU-Redux (Gema et al., 2024), GPQA (Rein et al., 2023), SuperGPQA (Team, 2025), (2) Reasoning: AIME-25 (AIME, 2025), HMMT-25 (HMMT, 2025), LiveBench (2024-11-25) (White et al., 2024), (3) Code: LiveCodeBench v6 (Jain et al., 2024), CFEval, OJBench (Wang et al., 2025c), (4) Alignment Tasks: IFEval (Zhou et al., 2023), Arena-Hard v2 (Li et al., 2024d) 1, Creative Writing v3 (Paech, 2023) 2, WritingBench (Wu et al., 2025b), (5) Agent: BFCL-v3 (Patil et al., 2024), TAU2-Retail, TAU2-Airline, TAU2-Telecom, (6) Multilingual: MultiIF (He et al., 2024), MMLU-ProX, INCLUDE (Romanou et al., 2025), PolyMATH (Wang et al., 2025b).

Evaluation Settings For Qwen3-VL instruct models including 235B-A22B, 32B and 30B-A3B, we configure the sampling hyperparameters with temperature $= 0 . 7 ,$ top- $\cdot \mathrm { p } = 0 . 8 ,$ , top- $\mathbf { \partial } \cdot \mathbf { k } = 2 0$ , and presence penalty $= 1 . 5$ . As for the small instruct models including 8B, 4B and 2B, we set the temperature $\overset { - } { = } 1 . 0$ , top- $\mathrm { \bar { p } } = 1 . \mathrm { \bar { 0 } }$ , top- $\mathbf { \partial \cdot k } = 4 0$ , and presence penalty $= 2 . 0$ . We set the max output length to 32,768 tokens.

For Qwen3-VL thinking models with Mixture-of-Experts (MoE) architecture, we set the sampling temperature to 0.6, top-p to 0.95, and top- $\mathbf { \nabla } \cdot \mathbf { k }$ to 20. For the dense thinking models, we set temperature $= 1 . 0$ , top-p $= 0 . 9 5 ,$ top- $\mathbf { \partial } \cdot \mathbf { k } = 2 0$ , and additionally apply a presence penalty of 1.5 to encourage greater output diversity. We set the max output length to 32,768 tokens, except AIME-25, HMMT-25 and LiveCodeBench v6 where we extend the length to 81,920 tokens to provide sufficient thinking space.

Table 5: Comparison among Qwen3-VL-235B-A22B (Instruct) and other baselines. The highest and second-best scores are shown in bold and underlined respectively.   

<table><tr><td></td><td>Benchmark</td><td>Qwen3-VL 235B-A22B Instruct</td><td>Qwen3 235B-A22B Instruct-2507</td><td>0324</td><td>Deepseek V3 Claude-Opus-4 (Without thinking)</td></tr><tr><td rowspan="3">Knowledge</td><td>MMLU-Pro</td><td>81.8</td><td>83.0</td><td>81.2</td><td>86.6</td></tr><tr><td>MMLU-Redux</td><td>92.2</td><td>93.1</td><td>90.4</td><td>94.2</td></tr><tr><td>GPQA</td><td>74.3</td><td>77.5</td><td>68.4</td><td>74.9</td></tr><tr><td rowspan="3">Reasoning</td><td>SuperGPQA</td><td>60.4</td><td>62.6</td><td>57.3</td><td>56.5</td></tr><tr><td>AIME-25</td><td>74.7</td><td>70.3</td><td>46.6</td><td>33.9</td></tr><tr><td>HMMT-25 LiveBench 2024-11-25</td><td>57.4 74.8</td><td>55.4 75.4</td><td>27.5 66.9</td><td>15.9 74.6</td></tr><tr><td rowspan="3">Alignment Tasks</td><td>IFEval</td><td>87.8</td><td>88.7</td><td>82.3</td><td>87.4</td></tr><tr><td>Arena-Hard V2 (winrate)</td><td>77.4</td><td>79.2</td><td>45.6</td><td>51.5</td></tr><tr><td>Creative Writing v3</td><td>86.5</td><td>87.5</td><td>81.6</td><td>83.8</td></tr><tr><td rowspan="2">Coding &amp; Agent</td><td>WritingBench</td><td>85.5</td><td>85.2</td><td>74.5</td><td>79.2</td></tr><tr><td>LiveCodeBench v6</td><td>54.3</td><td>51.8</td><td>45.2</td><td>44.6</td></tr><tr><td rowspan="3"></td><td>BFCL-v3</td><td>67.7</td><td>70.9</td><td>64.7</td><td>60.1</td></tr><tr><td>MultiIF</td><td>76.3</td><td>77.5</td><td>66.5</td><td>1</td></tr><tr><td>MMLU-ProX</td><td>77.8</td><td>79.4</td><td>75.8</td><td>-</td></tr><tr><td rowspan="3">Multilingualism</td><td>INCLUDE</td><td>80.0</td><td>79.5</td><td>80.1</td><td>1</td></tr><tr><td>PolyMATH</td><td>45.1</td><td>50.2</td><td>32.2</td><td>30.0</td></tr><tr><td></td><td></td><td></td><td></td><td></td></tr></table>

The detailed results are as follows.

Qwen3-VL-235B-A22B We compare our flagship model Qwen3-VL-235B-A22B with the leading instruct and thinking models. For the Qwen3-VL-235B-A22B-Instruct, we take Qwen3-235B-A22B-Instruct-2507, DeepSeek V3 0324, and Claude-Opus-4 (without thinking) as the baselines. For the Qwen3-VL-235BA22B-Thinking, we take Qwen3-235B-A22B-Thinking-2507, OpenAI o3 (medium), Claude-Opus-4 (with thinking) as baselines. We present the evaluation results in Table 5 and Table 6.

• From Table 5, Qwen3-VL-235B-A22B-Instruct achieves competitive results, comparable to or even surpassing the other leading models, including DeepSeek V3 0324, Claude-Opus-4 (without thinking), and our previous flagship model Qwen3-235B-A22B-Instruct-2507. Particularly, Qwen3-VL-235B-A22BInstruct exceeds other models on reasoning-demand tasks (e.g., mathematics and coding). It is worth noting that DeepSeek V3 0324 and Qwen3-235B-A22B-Instruct-2507 are Large Language Models, while Qwen3-VL-235B-A22B-Instruct is a Vision Language model which can process visual and textual tasks. This means that Qwen3-VL-235B-Instruct has achieved the integration of visual and textual capabilities. From Table 6, Qwen3-VL-235B-A22B-Thinking also achieves competitive results compared with other leading thinking models. Qwen3-VL-235B-A22B-Thinking exceeds OpenAI o3 (medium) and ClaudeOpus-4 (with thinking) on AIME-25 and LiveCodeBench v6, which means Qwen3-VL-235B-A22BThinking has better reasoning ability.

Qwen3-VL-32B / 30B-A3B We compare our Qwen3-VL-32B and Qwen3-VL-30B-A3B models with their corresponding text-only counterparts, namely Qwen3-32B, Qwen3-30B-A3B, and Qwen3-30B-A3B-2507. We present the evaluation results in Table 7 and Table 8.

• From Table 7, for instruct models, Qwen3-VL-32B and Qwen3-VL-30B-A3B show significant performance improvement compared with Qwen3-32B and Qwen3-30B-A3B on all the benchmarks. Qwen3-VL-30B-A3B achieves comparable or even better results compared with Qwen3-30B-A3B-2507, particularly AIME-25 and HMMT-25.   
• From Table 8, for thinking models, Qwen3-VL-32B and Qwen3-VL-30B-A3B surpass the baselines in most of the benchmarks. Qwen3-VL-30B-A3B also shows comparable performance compared with Qwen3-30B-A3B-2507.

Table 6: Comparison among Qwen3-VL-235B-A22B (Thinking) and other reasoning baselines. The highest and second-best scores are shown in bold and underlined respectively.   

<table><tr><td></td><td>Benchmark</td><td>Qwen3-VL 235B-A22B Thinking</td><td>Qwen3 235B-A22B Thinking-2507</td><td>OpenAI o3 (medium)</td><td>Claude-Opus-4 (With thinking)</td></tr><tr><td rowspan="2">Knowledge</td><td>MMLU-Pro MMLU-Redux</td><td>83.8 93.7</td><td>84.4</td><td>85.9</td><td></td></tr><tr><td>GPQA</td><td>77.1</td><td>93.8 81.1</td><td>94.9 83.3(high)</td><td>94.6 79.6</td></tr><tr><td rowspan="2"></td><td>SuperGPQA</td><td>64.3</td><td>64.9</td><td>1</td><td>1</td></tr><tr><td>AIME-25</td><td>89.7</td><td>92.3</td><td>88.9(high)</td><td>75.5</td></tr><tr><td rowspan="2">Reasoning</td><td>HMMT-25 LiveBench 2024-11-25</td><td>77.4</td><td>83.9</td><td>77.5</td><td>58.3</td></tr><tr><td></td><td>79.6</td><td>78.4</td><td>78.3</td><td>78.2</td></tr><tr><td rowspan="2">Coding</td><td>LiveCodeBench v6 CFEval</td><td>70.1 1964</td><td>74.1 2134</td><td>58.6 2043</td><td>48.9</td></tr><tr><td>OJBench</td><td>27.5</td><td>32.5</td><td>25.4</td><td>- -</td></tr><tr><td rowspan="4">Alignment Tasks</td><td>IFEval</td><td>88.2</td><td>87.8</td><td>92.1</td><td>89.7</td></tr><tr><td>Arena-Hard V2 (winrate)</td><td>74.8</td><td>79.7</td><td>80.8</td><td>59.1</td></tr><tr><td>Creative Writing v3</td><td>85.7</td><td>86.1</td><td>87.7</td><td>83.8</td></tr><tr><td>WritingBench</td><td>86.7</td><td>88.3</td><td>85.3</td><td>79.1</td></tr><tr><td rowspan="4">Agent</td><td>BFCL-v3</td><td>71.8</td><td>71.9</td><td>72.4</td><td>61.8</td></tr><tr><td>TAU2-Retail</td><td>67.0</td><td>71.9</td><td>76.3</td><td>-</td></tr><tr><td>TAU2-Airline</td><td>62.0</td><td>58.0</td><td>70.0</td><td></td></tr><tr><td>TAU2-Telecom</td><td>44.7</td><td>45.6</td><td>60.5</td><td></td></tr><tr><td rowspan="4">Multilingualism</td><td>MultiIF</td><td>79.1</td><td>80.6</td><td>80.3</td><td></td></tr><tr><td>MMLU-ProX</td><td>80.6</td><td>81.0</td><td>83.3</td><td></td></tr><tr><td>INCLUDE</td><td>80.0</td><td>81.0</td><td>86.6</td><td></td></tr><tr><td>PolyMATH</td><td>57.8</td><td>60.1</td><td>49.7</td><td></td></tr></table>

Table 7: Comparison among Qwen3-VL-32B-Instruct, Qwen3-VL-30B-A3B-Instruct, and corresponding baselines.   

<table><tr><td></td><td>Benchmark</td><td>Qwen3-VL 32B Instruct</td><td>Qwen3 32B Instruct</td><td>Qwen3-VL 30B-A3B Instruct</td><td>Qwen3 30B-A3B Instruct</td><td>Qwen3 30B-A3B Instruct-2507</td></tr><tr><td rowspan="4">Knowledge</td><td>MMLU-Pro</td><td>78.6</td><td>71.9</td><td>77.8</td><td>69.1</td><td>78.4</td></tr><tr><td>MMLU-Redux</td><td>89.8</td><td>85.7</td><td>88.4</td><td>84.1</td><td>89.3</td></tr><tr><td>GPQA</td><td>68.9</td><td>54.6</td><td>70.4</td><td>54.8</td><td>70.4</td></tr><tr><td>SuperGPQA</td><td>54.6</td><td>43.2</td><td>53.1</td><td>42.2</td><td>53.4</td></tr><tr><td rowspan="3">Reasoning</td><td>AIME-25</td><td>66.2</td><td>20.2</td><td>69.3</td><td>21.6</td><td>61.3</td></tr><tr><td>HMMT-25</td><td>46.1</td><td>10.9</td><td>50.6</td><td>12.0</td><td>43.0</td></tr><tr><td>LiveBench 2024-11-25</td><td>72.2</td><td>31.3</td><td>65.4</td><td>59.4</td><td>69.0</td></tr><tr><td rowspan="4">Alignment Tasks</td><td>IFEval</td><td>84.7</td><td>83.2</td><td>85.8</td><td>83.7</td><td>84.7</td></tr><tr><td>Arena-Hard V2 (winrate)</td><td>64.7</td><td>37.4</td><td>58.5</td><td>24.8</td><td>69.0</td></tr><tr><td>Creative Writing v3</td><td>85.6</td><td>80.6</td><td>84.6</td><td>68.1</td><td>86.0</td></tr><tr><td>WritingBench</td><td>82.9</td><td>81.3</td><td>82.6</td><td>72.2</td><td>85.5</td></tr><tr><td rowspan="2">Coding &amp; Agent</td><td>LiveCodeBench v6</td><td>43.8</td><td>29.1</td><td>42.6</td><td>29.0</td><td>43.2</td></tr><tr><td>BFCL-v3</td><td>70.2</td><td>63.0</td><td>66.3</td><td>58.6</td><td>65.1</td></tr><tr><td rowspan="4">Multilingualism</td><td>MultiIF</td><td>72.0</td><td>70.7</td><td>66.1</td><td>70.8</td><td>67.9</td></tr><tr><td>MMLU-ProX</td><td>73.4</td><td>69.3</td><td>70.9</td><td>65.1</td><td>72.0</td></tr><tr><td>INCLUDE</td><td>74.0</td><td>69.6</td><td>71.6</td><td>67.8</td><td>71.9</td></tr><tr><td>PolyMATH</td><td>40.5</td><td>22.5</td><td>44.3</td><td>23.3</td><td>43.1</td></tr></table>

Qwen3-VL-8B / 4B / 2B We present the evaluation results of Qwen3-VL-2B, Qwen3-VL-4B, and Qwen3- VL-8B in Table 9 and Table 10. For Qwen3-VL-2B and Qwen3-VL-8B, we compare them with Qwen3-1.7B and Qwen3-8B. For Qwen3-VL-4B, we compare it with Qwen3-4B and Qwen3-4B-2507. Overall, these edge-side models exhibit impressive performance and outperform baselines. These results demonstrate

Table 8: Comparison among Qwen3-VL-32B (Thinking), Qwen3-VL-30B-A3B (Thinking), and corresponding baselines.   

<table><tr><td></td><td>Benchmark</td><td>Qwen3-VL 32B Thinking</td><td>Qwen3 32B Thinking</td><td>Qwen3-VL 30B-A3B Thinking</td><td>Qwen3 30B-A3B Thinking</td><td>Qwen3 30B-A3B Thinking-2507</td></tr><tr><td rowspan="3">Knowledge</td><td>MMLU-Pro</td><td>82.1</td><td>79.1</td><td>80.5</td><td>78.5</td><td>80.9</td></tr><tr><td>MMLU-Redux</td><td>91.9</td><td>90.9</td><td>90.9</td><td>89.5</td><td>91.4</td></tr><tr><td>GPQA</td><td>73.1</td><td>68.4</td><td>74.4</td><td>65.8</td><td>73.4</td></tr><tr><td rowspan="3">Reasoning</td><td>SuperGPQA</td><td>59.0</td><td>54.1</td><td>56.4</td><td>51.8</td><td>56.8</td></tr><tr><td>AIME-25</td><td>83.7</td><td>72.9</td><td>83.1</td><td>70.9</td><td>85.0</td></tr><tr><td>HMMT-25 LiveBench 2024-11-25</td><td>64.6 74.7</td><td>51.8 65.7</td><td>67.6 72.1</td><td>49.8 74.3</td><td>71.4</td></tr><tr><td rowspan="3">Coding</td><td>LiveCodeBench v6</td><td>65.6</td><td>60.6</td><td></td><td></td><td>76.8</td></tr><tr><td>CFEval</td><td>1842</td><td>1986</td><td>64.2 1894</td><td>57.4 1940</td><td>66.0 2044</td></tr><tr><td>OJBench</td><td>20.0</td><td>24.1</td><td>23.4</td><td>20.7</td><td>25.1</td></tr><tr><td rowspan="4">Alignment Tasks</td><td>IFEval</td><td>87.8</td><td>85.0</td><td>81.7</td><td>86.5</td><td>88.9</td></tr><tr><td>Arena-Hard V2 (winrate)</td><td>60.5</td><td>50.3</td><td>56.7</td><td>36.3</td><td>56.0</td></tr><tr><td>Creative Writing v3</td><td>83.3</td><td>84.4</td><td>82.5</td><td>79.1</td><td>84.4</td></tr><tr><td>WritingBench</td><td>86.2</td><td>78.4</td><td>85.2</td><td>77.0</td><td>85.0</td></tr><tr><td rowspan="4">Agent</td><td>BFCL-v3</td><td>71.7</td><td>70.3</td><td>68.6</td><td>69.1</td><td>72.4</td></tr><tr><td>TAU2-Retail</td><td>59.4</td><td>59.6</td><td>64.0</td><td>34.2</td><td>58.8</td></tr><tr><td>TAU2-Airline</td><td>52.5</td><td>38.0</td><td>48.0</td><td>36.0</td><td>58.0</td></tr><tr><td>TAU2-Telecom</td><td>46.9</td><td>26.3</td><td>27.2</td><td>22.8</td><td>26.3</td></tr><tr><td rowspan="4">Multilingualism</td><td>MultiIF</td><td>78.0</td><td>73.0</td><td>73.0</td><td>72.2</td><td>76.4</td></tr><tr><td>MMLU-ProX</td><td>77.2</td><td>74.6</td><td>76.1</td><td>73.1</td><td>76.4</td></tr><tr><td>INCLUDE</td><td>76.3</td><td>73.7</td><td>74.5</td><td>71.9</td><td>74.4</td></tr><tr><td>PolyMATH</td><td>52.0</td><td>47.4</td><td>51.7</td><td>46.1</td><td>52.6</td></tr></table>

Table 9: Comparison among Qwen3-VL-2B (Instruct), Qwen3-VL-4B (Instruct), Qwen3-VL-8B (Instruct) and corresponding baselines.   

<table><tr><td rowspan="2"></td><td rowspan="2">Benchmark</td><td colspan="7">Qwen3-VL Qwen3-VL Qwen3-VL Qwen3 Qwen3 Qwen3</td></tr><tr><td>2B Instruct</td><td>4B Instruct</td><td>8B</td><td>1.7B</td><td>Qwen3 4B Instruct</td><td>8B Instruct</td><td>4B Instruct-2507</td></tr><tr><td rowspan="4">Knowledge</td><td></td><td></td><td></td><td>Instruct</td><td>Instruct</td><td></td><td></td><td></td></tr><tr><td>MMLU-Pro</td><td>49.0</td><td>67.1</td><td>71.6</td><td>42.3</td><td>58.0</td><td>63.4</td><td>69.6</td></tr><tr><td>MMLU-Redux</td><td>66.5</td><td>81.5</td><td>84.9</td><td>63.6</td><td>77.3</td><td>79.5</td><td>84.2</td></tr><tr><td>GPQA SuperGPQA</td><td>42.0 24.3</td><td>55.9 40.3</td><td>61.9 44.5</td><td>34.7 22.8</td><td>41.7 32.0</td><td>39.3 35.8</td><td>62.0 42.8</td></tr><tr><td rowspan="3">Reasoning</td><td>AIME-25</td><td>22.2</td><td>46.6</td><td>45.9</td><td>10.6</td><td>19.1</td><td>20.9</td><td>47.4</td></tr><tr><td>HMMT-25</td><td>10.9</td><td>30.7</td><td>32.5</td><td>6.2</td><td>12.1</td><td>11.8</td><td>31.0</td></tr><tr><td>LiveBench 2024-11-25</td><td>39.5</td><td>60.9</td><td>62.0</td><td>35.6</td><td>48.4</td><td>53.5</td><td>63.0</td></tr><tr><td rowspan="4">Alignment Tasks</td><td>IFEval</td><td>68.2</td><td>82.3</td><td>83.7</td><td>67.1</td><td>81.2</td><td>83.0</td><td>83.4</td></tr><tr><td>Arena-Hard V2 (winrate) 6.4</td><td></td><td>30.4</td><td>46.3</td><td>4.1</td><td>9.5</td><td>15.5</td><td>43.4</td></tr><tr><td>Creative Writing v3</td><td>48.6</td><td>72.3</td><td>77.0</td><td>49.1</td><td>53.6</td><td>69.0</td><td>83.5</td></tr><tr><td>WritingBench</td><td>73.0</td><td>82.5</td><td>83.1</td><td>65.1</td><td>68.5</td><td>71.4</td><td>83.4</td></tr><tr><td rowspan="2">Coding &amp; Agent</td><td>LiveCodeBench v6</td><td>20.3</td><td>37.9</td><td>39.3</td><td>16.1</td><td>26.4</td><td>25.5</td><td>35.1</td></tr><tr><td>BFCL-v3</td><td>55.4</td><td>63.3</td><td>66.3</td><td>52.2</td><td>57.6</td><td>60.2</td><td>61.9</td></tr><tr><td rowspan="4">Multilingualism</td><td>MultiIF</td><td>43.2</td><td>61.5</td><td>66.8</td><td>43.2</td><td>61.3</td><td>69.2</td><td>69.0</td></tr><tr><td>MMLU-ProX</td><td>38.8</td><td>59.4</td><td>65.4</td><td>33.5</td><td>49.6</td><td>58.0</td><td>61.6</td></tr><tr><td>INCLUDE</td><td>45.8</td><td>61.4</td><td>67.0</td><td>42.6</td><td>53.8</td><td>62.5</td><td>60.1</td></tr><tr><td>PolyMATH</td><td>14.9</td><td>28.8</td><td>30.4</td><td>10.3</td><td>16.6</td><td>18.8</td><td>31.1</td></tr></table>

the efficacy of our Strong-to-Weak Distillation approach, making it possible for us to build the lightweight models with remarkably reduced costs and efforts.

Table 10: Comparison among Qwen3-VL-2B (Thinking), Qwen3-VL-4B (Thinking), Qwen3-VL-8B (Thinking) and corresponding baselines.   

<table><tr><td></td><td>Benchmark</td><td>Qwen3-VL Qwen3-VL 2B 4B Thinking</td><td>Thinking</td><td>Qwen3-VL 8B Thinking</td><td>Qwen3 Qwen3 1.7B Thinking</td><td>4B Thinking Thinking</td><td>Qwen3 8B</td><td>Qwen3 4B</td></tr><tr><td rowspan="4">Knowledge</td><td>MMLU-Pro</td><td>62.3</td><td>73.6</td><td>77.3</td><td>58.1</td><td>70.4</td><td>74.6</td><td>74.0</td></tr><tr><td>MMLU-Redux</td><td>76.9</td><td>86.0</td><td>88.8</td><td>73.9</td><td>83.7</td><td>87.5</td><td>86.1</td></tr><tr><td>GPQA</td><td>49.5</td><td>64.1</td><td>69.9</td><td>27.9</td><td>55.9</td><td>62.0</td><td>65.8</td></tr><tr><td>SuperGPQA</td><td>34.6</td><td>46.8</td><td>51.2</td><td>31.2</td><td>42.7</td><td>47.6</td><td>47.8</td></tr><tr><td rowspan="3">Reasoning</td><td>AIME-25</td><td>39.0</td><td>74.5</td><td>80.3</td><td>36.8</td><td>65.6</td><td>67.3</td><td>81.3</td></tr><tr><td>HMMT-25</td><td>22.8</td><td>53.1</td><td>60.6</td><td>24.3</td><td>42.1</td><td>43.2</td><td>55.5</td></tr><tr><td>LiveBench 2024-11-25</td><td>50.1</td><td>68.4</td><td>69.8</td><td>51.1</td><td>63.6</td><td>67.1</td><td>71.8</td></tr><tr><td rowspan="4">Alignment Tasks</td><td>IFEval</td><td>75.1</td><td>82.6</td><td>83.2</td><td>72.5</td><td>81.9</td><td>85.0</td><td>87.4</td></tr><tr><td>Arena-Hard V2 (winrate)</td><td>12.0</td><td>36.8</td><td>51.1</td><td>4.7</td><td>13.7</td><td>29.1</td><td>34.9</td></tr><tr><td>Creative Writing v3</td><td>55.6</td><td>76.1</td><td>82.4</td><td>50.6</td><td>61.1</td><td>78.5</td><td>75.6</td></tr><tr><td>WritingBench</td><td>77.9</td><td>84.0</td><td>85.5</td><td>68.9</td><td>73.5</td><td>75.0</td><td>83.3</td></tr><tr><td rowspan="2">Coding &amp; Agent</td><td>LiveCodeBench v6 BFCL-v3</td><td>29.3</td><td>51.3</td><td>58.6</td><td>31.3</td><td>48.4</td><td>51.0</td><td>55.2</td></tr><tr><td></td><td>57.2</td><td>67.3</td><td>63.0</td><td>56.6</td><td>65.9</td><td>68.1</td><td>71.2</td></tr><tr><td rowspan="4">Multilingualism</td><td>MultiIF</td><td>58.9</td><td>73.6</td><td>75.1</td><td>51.2</td><td>66.3</td><td>71.2</td><td>77.3</td></tr><tr><td>MMLU-ProX</td><td>55.1</td><td>65.0</td><td>70.7</td><td>50.4</td><td>61.0</td><td>68.1</td><td>64.2</td></tr><tr><td>INCLUDE</td><td>53.3</td><td>64.6</td><td>69.5</td><td>51.8</td><td>61.8</td><td>67.8</td><td>64.4</td></tr><tr><td>PolyMATH</td><td>28.0</td><td>44.6</td><td>47.5</td><td>25.2</td><td>40.0</td><td>42.7</td><td>46.2</td></tr></table>

# 5.12 Ablation Study

# 5.12.1 Vision Encoder

We conduct comparative experiments against the original SigLIP-2. As shown in Table 11, in zero-shot evaluation at the CLIP pretraining stage, Qwen3-ViT maintains competitive performance on standard benchmarks while achieving substantial gains on OmniBench, our in-house holistic evaluation suite designed to assess world knowledge integration under diverse and challenging conditions. Furthermore, when integrated with the same 1.7B Qwen3 language model and trained for 1.5T tokens, Qwen3-ViT consistently outperforms the SigLIP-2-based baseline across multiple key tasks and remains significantly ahead on OmniBench, demonstrating its superiority and effectiveness as a stronger visual backbone.

Table 11: Ablation on Qwen3-ViT. We compare the performance metrics of Qwen3-ViT and SigLIP-2 during the CLIP pre-training stage, and further evaluate their downstream performance in the visionlanguage modeling (VLM) stage when paired with the same 1.7B Qwen3 language model.   

<table><tr><td rowspan="2">ViT</td><td colspan="7">Clip Bench</td><td colspan="5">VLMBench OCRB AI2D RLWDQA InfoVQA Omni</td></tr><tr><td>ImageNet-1K ImageNet-V2 ImageNet-A ImageNet-R ImageNet-S ObjectNet Omni</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>SigLIP-2</td><td>84.2</td><td>78.6</td><td>87.0</td><td>96.1</td><td>76.2</td><td>79.9</td><td>36.9</td><td>77.2</td><td>74.1</td><td>58.7</td><td>65.3</td><td>50.1</td></tr><tr><td>Qwen3-ViT</td><td>84.6</td><td>78.8</td><td>87.1</td><td>95.7</td><td>74.5</td><td>81.0</td><td>45.5</td><td>78.7</td><td>76.2</td><td>66.1</td><td>67.0</td><td>53.0</td></tr></table>

# 5.12.2 DeepStack

We conduct an ablation study to verify the effectiveness of the DeepStack mechanism. As demonstrated in Table 12, the model equipped with DeepStack achieved an overall performance gain across various benchmarks, strongly affirming its effectiveness. This gain is attributed to DeepStack’s ability to integrate rich visual information, which effectively boosts the capability in fine-grained visual understanding, such as on the InfoVQA and DocVQA benchmarks.

Table 12: Ablation on DeepStack. We conduct the ablation study on the DeepStack using an internal 15BA2B LLM, with all experiments pretrained on 200 billion tokens. We directly evaluate these pretrained models on the validation sets, without any post-training.   

<table><tr><td>Method</td><td>AVG</td><td>AI2D</td><td>OCRB</td><td>TVQA</td><td>InfoVQA ChartQA DocVQA MMMU MMStarRLWDQA MMBEN</td><td></td><td></td><td></td><td></td><td></td><td></td><td>MMBcN</td></tr><tr><td>Baseline</td><td>74.7</td><td>81.8</td><td>81.0</td><td>80.6</td><td>71.9</td><td>81.5</td><td>89.5</td><td>52.9</td><td>55.5</td><td>67.7</td><td>81.0</td><td>78.1</td></tr><tr><td>DeepStack</td><td>76.0</td><td>83.2</td><td>83.6</td><td>80.5</td><td>74.2</td><td>83.3</td><td>91.1</td><td>54.1</td><td>57.7</td><td>68.1</td><td>81.2</td><td>78.5</td></tr></table>

![](images/9af3f2895469b2bfbe3cae0b106be7b38b8256abc0e47e1932e5f1d1da9e0d5c.jpg)  
Figure 3: Needle-in-a-Haystack performance heatmap for Qwen3-VL-235B-A22B-Instruct across varying video durations and needle positions. Each cell shows accuracy $( \% )$ for locating and answering questions about the inserted “needle” frame.

# 5.12.3 Needle-in-a-Haystack

To evaluate the model’s capability in processing long-context inputs, we construct a video “Needle-ina-Haystack” evaluation on Qwen3-VL-235B-A22B-Instruct. In this task, a semantically salient “needle” frame—containing critical visual evidence—is inserted at varying temporal positions within a long video. The model is then tasked with accurately locating the target frame from the long video and answering the corresponding question. During evaluation, videos are uniformly sampled at 1 FPS, and frame resolution is dynamically adjusted to maintain a constant visual token budget.

As shown in Figure 3, the model achieves a perfect $1 0 0 \%$ accuracy on videos up to 30 minutes in duration—corresponding to a context length of 256K tokens. Remarkably, even when extrapolating to sequences of up to 1M tokens (approximately 2 hours of video) via YaRN-based positional extension, the model retains a high accuracy of $9 9 . 5 \%$ . These results strongly demonstrate the model’s powerful long-sequence modeling capabilities.

# 6 Conclusion

In this work, we present Qwen3-VL, a state-of-the-art series of vision–language foundation models that advances the frontier of multimodal understanding and generation. By integrating high-quality multimodal data iteration and architectural innovations—such as enhanced interleaved-MRoPE, DeepStack vision-language alignment, and text-based temporal grounding—Qwen3-VL achieves unprecedented performance across a broad spectrum of multimodal benchmarks while maintaining strong pure-text capabilities. Its native support for 256K-token interleaved sequences enables robust reasoning over long, complex documents, image sequences, and videos, making it uniquely suited for real-world applications demanding high-fidelity cross-modal comprehension. The availability of both dense and Mixture-ofExperts variants ensures flexible deployment across diverse latency and quality requirements, and our post-training strategy—including non-thinking and thinking modes.

Looking forward, we envision Qwen3-VL as a foundational engine for embodied AI agents capable of seamlessly bridging the digital and physical worlds. Such agents will not only perceive and reason over rich multimodal inputs but also execute decisive, context-aware actions in dynamic environments—interacting with users, manipulating digital interfaces, and guiding robotic systems through grounded, multimodal decision-making. Future work will focus on extending Qwen3-VL’s capabilities toward interactive perception, tool-augmented reasoning, and real-time multimodal control, with the ultimate goal of enabling AI systems that learn, adapt, and collaborate alongside humans in both virtual and physical domains. Additionally, we are actively exploring unified understanding-generation architectures, leveraging visual generation capabilities to elevate overall intelligence further. By openly releasing the entire model family under the Apache 2.0 license, we aim to catalyze community-driven innovation toward the vision of truly integrated, multimodal AI agents.

# 7 Contributions and Acknowledgments

All contributors of Qwen3-VL are listed in alphabetical order by their last names.

Core Contributors: Shuai Bai, Yuxuan Cai, Ruizhe Chen, Keqin Chen, Xionghui Chen, Zesen Cheng, Lianghao Deng, Wei Ding, Chang Gao, Chunjiang Ge, Wenbin Ge, Zhifang Guo, Qidong Huang, Jie Huang, Fei Huang, Binyuan Hui, Shutong Jiang, Zhaohai Li, Mingsheng Li, Mei Li, Kaixin Li, Zicheng Lin, Junyang Lin, Xuejing Liu, Jiawei Liu, Chenglong Liu, Yang Liu, Dayiheng Liu, Shixuan Liu, Dunjie Lu, Ruilin Luo, Chenxu Lv, Rui Men, Lingchen Meng, Xuancheng Ren, Xingzhang Ren, Sibo Song, Yuchong Sun, Jun Tang, Jianhong Tu, Jianqiang Wan, Peng Wang, Pengfei Wang, Qiuyue Wang, Yuxuan Wang, Tianbao Xie, Yiheng Xu, Haiyang Xu, Jin Xu, Zhibo Yang, Mingkun Yang, Jianxin Yang, An Yang, Bowen Yu, Fei Zhang, Hang Zhang, Xi Zhang, Bo Zheng, Humen Zhong, Jingren Zhou, Fan Zhou, Jing Zhou, Yuanzhi Zhu, Ke Zhu

Contributors: Yizhong Cao, Bei Chen, Chen Cheng, Yunfei Chu, Zeyu Cui, Kai Dang, Xiaodong Deng, Yang Fan, Rongyao Fang, Tongkun Guan, Jinzheng He, Miao Hong, Songtao Jiang, Zheng Li, Xiaochuan Li, Junrong Lin, Yuqiong Liu, Yantao Liu, Na Ni, Xinyao Niu, Yatian Pang, Zihan Qiu, Tianhao Shen, Tianyi Tang, Yu Wan, Jinxi Wei, Chenfei Wu, Buxiao Wu, Xiao Xu, Mingfeng Xue, Ming Yan, Yuhuan Yang, Jiaxi Yang, Kexin Yang, Le Yu, Hao Yu, Jianke Zhang, Jianwei Zhang, Yichang Zhang, Zhenru Zhang, Siqi Zhang, Peiyang Zhang, Beichen Zhang, Hongbo Zhao, Xianwei Zhuang

Acknowledgments: We gratefully acknowledge the unwavering support provided by the teams led by Zulong Chen, Bing Deng, Feiyu Gao, Guanjun Jiang, Yue Liu, Hangdi Xing and Daijun Yu.

# References

Pravesh Agrawal, Szymon Antoniak, Emma Bou Hanna, Baptiste Bout, Devendra Chaplot, Jessica Chudnovsky, Diogo Costa, Baudouin De Monicault, Saurabh Garg, Theophile Gervet, et al. Pixtral 12b. arXiv preprint arXiv:2410.07073, 2024.

AIME. Aime problems and solutions, 2025. URL https://artofproblemsolving.com/wiki/index.php/ AIMEProblemsandSolutions.

Anthropic. Claude opus 4.1, 2025. URL https://www.anthropic.com/news/claude-opus-4-1.

Shuai Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin Ge, Sibo Song, Kai Dang, Peng Wang, Shijie Wang, Jun Tang, Humen Zhong, Yuanzhi Zhu, Mingkun Yang, Zhaohai Li, Jianqiang Wan, Pengfei Wang, Wei Ding, Zheren Fu, Yiheng Xu, Jiabo Ye, Xi Zhang, Tianbao Xie, Zesen Cheng, Hang Zhang, Zhibo Yang, Haiyang Xu, and Junyang Lin. Qwen2.5-vl technical report, 2025.

Gilad Baruch, Zhuoyuan Chen, Afshin Dehghan, Tal Dimry, Yuri Feigin, Peter Fu, Thomas Gebauer, Brandon Joffe, Daniel Kurz, Arik Schwartz, et al. Arkitscenes: A diverse real-world dataset for 3d indoor scene understanding using mobile rgb-d data. arXiv preprint arXiv:2111.08897, 2021.

Garrick Brazil, Abhinav Kumar, Julian Straub, Nikhila Ravi, Justin Johnson, and Georgia Gkioxari. Omni3d: A large benchmark and model for 3d object detection in the wild. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 13154–13164, 2023.

Lin Chen, Jinsong Li, Xiaoyi Dong, Pan Zhang, Yuhang Zang, Zehui Chen, Haodong Duan, Jiaqi Wang, Yu Qiao, Dahua Lin, et al. Are we on the right way for evaluating large vision-language models? arXiv:2403.20330, 2024a.

Shimin Chen, Xiaohan Lan, Yitian Yuan, Zequn Jie, and Lin Ma. Timemarker: A versatile video-llm for long and short video understanding with superior temporal localization ability. arXiv preprint arXiv:2411.18211, 2024b.

Yitong Chen, Lingchen Meng, Wujian Peng, Zuxuan Wu, and Yu-Gang Jiang. Comp: Continual multimodal pre-training for vision foundation models. arXiv preprint arXiv:2503.18931, 2025.

Kanzhi Cheng, Qiushi Sun, Yougang Chu, Fangzhi Xu, Yantao Li, Jianbing Zhang, and Zhiyong Wu. Seeclick: Harnessing gui grounding for advanced visual gui agents. arXiv preprint arXiv:2401.10935, 2024.

Xianfu Cheng, Wei Zhang, Shiwei Zhang, Jian Yang, Xiangyuan Guan, Xianjie Wu, Xiang Li, Ge Zhang, Jiaheng Liu, Yuying Mai, et al. Simplevqa: Multimodal factuality evaluation for multimodal large language models. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pp. 4637– 4646, 2025.

Gheorghe Comanici, Eric Bieber, Mike Schaekermann, Ice Pasupat, Noveen Sachdeva, Inderjit Dhillon, Marcel Blistein, Ori Ram, Dan Zhang, Evan Rosen, et al. Gemini 2.5: Pushing the frontier with advanced reasoning, multimodality, long context, and next generation agentic capabilities. arXiv preprint arXiv:2507.06261, 2025.

Matt Deitke, Christopher Clark, Sangho Lee, Rohun Tripathi, Yue Yang, Jae Sung Park, Mohammadreza Salehi, Niklas Muennighoff, Kyle Lo, Luca Soldaini, et al. Molmo and pixmo: Open weights and open data for state-of-the-art multimodal models. arXiv preprint arXiv:2409.17146, 2024.

Shizhe Diao, Yu Yang, Yonggan Fu, Xin Dong, Dan Su, Markus Kliegl, Zijia Chen, Peter Belcak, Yoshi Suhara, Hongxu Yin, et al. Climb: Clustering-based iterative data mixture bootstrapping for language model pre-training. arXiv preprint arXiv:2504.13161, 2025.

Matthijs Douze, Alexandr Guzhva, Chengqi Deng, Jeff Johnson, Gergely Szilvasy, Pierre-Emmanuel Mazaré, Maria Lomeli, Lucas Hosseini, and Hervé Jégou. The faiss library. 2024.

Mengfei Du, Binhao Wu, Zejun Li, Xuanjing Huang, and Zhongyu Wei. Embspatial-bench: Benchmarking spatial understanding for embodied tasks with large vision-language models. arXiv preprint arXiv:2406.05756, 2024.

Chengqi Duan, Kaiyue Sun, Rongyao Fang, Manyuan Zhang, Yan Feng, Ying Luo, Yufang Liu, Ke Wang, Peng Pei, Xunliang Cai, et al. Codeplot-cot: Mathematical visual reasoning by thinking with codedriven images. arXiv preprint arXiv:2510.11718, 2025.

Chaoyou Fu, Yuhan Dai, Yondong Luo, Lei Li, Shuhuai Ren, Renrui Zhang, Zihan Wang, Chenyu Zhou, Yunhang Shen, Mengdan Zhang, et al. Video-mme: The first-ever comprehensive evaluation benchmark of multi-modal llms in video analysis. arXiv:2405.21075, 2024a.

Ling Fu, Biao Yang, Zhebin Kuang, Jiajun Song, Yuzhe Li, Linghao Zhu, Qidi Luo, Xinyu Wang, Hao Lu, Mingxin Huang, Zhang Li, Guozhi Tang, Bin Shan, Chunhui Lin, Qi Liu, Binghong Wu, Hao Feng, Hao Liu, Can Huang, Jingqun Tang, Wei Chen, Lianwen Jin, Yuliang Liu, and Xiang Bai. Ocrbench v2: An improved benchmark for evaluating large multimodal models on visual text localization and reasoning, 2024b. URL https://arxiv.org/abs/2501.00321.

Xingyu Fu, Yushi Hu, Bangzheng Li, Yu Feng, Haoyu Wang, Xudong Lin, Dan Roth, Noah A Smith, Wei-Chiu Ma, and Ranjay Krishna. Blink: Multimodal large language models can see but not perceive. In European Conference on Computer Vision, pp. 148–166. Springer, 2024c.

Chang Gao, Chujie Zheng, Xiong-Hui Chen, Kai Dang, Shixuan Liu, Bowen Yu, An Yang, Shuai Bai, Jingren Zhou, and Junyang Lin. Soft adaptive policy optimization. arXiv preprint arXiv:2511.20347, 2025.

Jiyang Gao, Chen Sun, Zhenheng Yang, and Ram Nevatia. Tall: Temporal activity localization via language query. In Proceedings of the IEEE international conference on computer vision, pp. 5267–5275, 2017.

Aryo Pradipta Gema, Joshua Ong Jun Leang, Giwon Hong, Alessio Devoto, Alberto Carlo Maria Mancino, Rohit Saxena, Xuanli He, Yu Zhao, Xiaotang Du, Mohammad Reza Ghasemi Madani, Claire Barale, Robert McHardy, Joshua Harris, Jean Kaddour, Emile van Krieken, and Pasquale Minervini. Are we done with mmlu? CoRR, abs/2406.04127, 2024. doi: 10.48550/ARXIV.2406.04127. URL https: //doi.org/10.48550/arXiv.2406.04127.

Tianrui Guan, Fuxiao Liu, Xiyang Wu, Ruiqi Xian, Zongxia Li, Xiaoyu Liu, Xijun Wang, Lichang Chen, Furong Huang, Yaser Yacoob, Dinesh Manocha, and Tianyi Zhou. Hallusionbench: An advanced diagnostic suite for entangled language hallucination & visual illusion in large vision-language models, 2023.

Yun He, Di Jin, Chaoqi Wang, Chloe Bi, Karishma Mandyam, Hejia Zhang, Chen Zhu, Ning Li, Tengyu Xu, Hongjiang Lv, Shruti Bhosale, Chenguang Zhu, Karthik Abinav Sankararaman, Eryk Helenowski, Melanie Kambadur, Aditya Tayade, Hao Ma, Han Fang, and Sinong Wang. Multi-if: Benchmarking llms on multi-turn and multilingual instructions following. CoRR, abs/2410.15553, 2024. doi: 10.48550/ ARXIV.2410.15553. URL https://doi.org/10.48550/arXiv.2410.15553.

HMMT. Hmmt 2025. https://www.hmmt.org, 2025.

Kairui Hu, Penghao Wu, Fanyi Pu, Wang Xiao, Yuanhan Zhang, Xiang Yue, Bo Li, and Ziwei Liu. Videommmu: Evaluating knowledge acquisition from multi-discipline professional videos. arXiv preprint arXiv:2501.13826, 2025.

Jie Huang, Xuejing Liu, Sibo Song, Ruibing Hou, Hong Chang, Junyang Lin, and Shuai Bai. Revisiting multimodal positional encoding in vision-language models, 2025.

Naman Jain, King Han, Alex Gu, Wen-Ding Li, Fanjia Yan, Tianjun Zhang, Sida Wang, Armando SolarLezama, Koushik Sen, and Ion Stoica. Livecodebench: Holistic and contamination free evaluation of large language models for code. CoRR, abs/2403.07974, 2024. doi: 10.48550/ARXIV.2403.07974. URL https://doi.org/10.48550/arXiv.2403.07974.

Bowen Jin, Hansi Zeng, Zhenrui Yue, Jinsung Yoon, Sercan Arik, Dong Wang, Hamed Zamani, and Jiawei Han. Search-r1: Training llms to reason and leverage search engines with reinforcement learning. arXiv preprint arXiv:2503.09516, 2025.

Jeff Johnson, Matthijs Douze, and Hervé Jégou. Billion-scale similarity search with GPUs. IEEE Transactions on Big Data, 7(3):535–547, 2019.

Sahar Kazemzadeh, Vicente Ordonez, Mark Matten, and Tamara Berg. Referitgame: Referring to objects in photographs of natural scenes. In EMNLP, 2014.

Aniruddha Kembhavi, Michael Salvato, Eric Kolve, Minjoon Seo, Hannaneh Hajishirzi, and Ali Farhadi. A diagram is worth a dozen images. ArXiv, abs/1603.07396, 2016.

Alina Kuznetsova, Hassan Rom, Neil Alldrin, Jasper Uijlings, Ivan Krasin, Jordi Pont-Tuset, Shahab Kamali, Stefan Popov, Matteo Malloci, Alexander Kolesnikov, et al. The open images dataset v4: Unified image classification, object detection, and visual relationship detection at scale. International journal of computer vision, pp. 1956–1981, 2020.

Xin Lai, Junyi Li, Wei Li, Tao Liu, Tianjian Li, and Hengshuang Zhao. Mini-o3: Scaling up reasoning patterns and interaction turns for visual search. arXiv preprint arXiv:2509.07969, 2025.

Hugo Laurençon, Lucile Saulnier, Léo Tronchon, Stas Bekman, Amanpreet Singh, Anton Lozhkov, Thomas Wang, Siddharth Karamcheti, Alexander Rush, Douwe Kiela, et al. Obelics: An open web-scale filtered dataset of interleaved image-text documents. Advances in Neural Information Processing Systems, 36: 71683–71702, 2023.

Jinke Li, Jiarui Yu, Chenxing Wei, Hande Dong, Qiang Lin, Liangjing Yang, Zhicai Wang, and Yanbin Hao. Unisvg: A unified dataset for vector graphic understanding and generation with multimodal large language models. In Proceedings of the 33rd ACM International Conference on Multimedia, pp. 13156–13163, 2025a.

Kaixin Li, Yuchen Tian, Qisheng Hu, Ziyang Luo, Zhiyong Huang, and Jing Ma. Mmcode: Benchmarking multimodal large language models for code generation with visually rich programming problems. In Findings of the Association for Computational Linguistics: EMNLP 2024, pp. 736–783, 2024a.

Kaixin Li, Ziyang Meng, Hongzhan Lin, Ziyang Luo, Yuchen Tian, Jing Ma, Zhiyong Huang, and Tat-Seng Chua. Screenspot-pro: Gui grounding for professional high-resolution computer use, 2025b. URL https://likaixin2000.github.io/papers/ScreenSpot_Pro.pdf. Preprint.

Kaixin Li et al. Iconstack, 2025c. URL https://huggingface.co/datasets/likaixin/ IconStack-48M-Rendered-Train.

Kunchang Li, Yali Wang, Yinan He, Yizhuo Li, Yi Wang, Yi Liu, Zun Wang, Jilan Xu, Guo Chen, Ping Luo, et al. Mvbench: A comprehensive multi-modal video understanding benchmark. In CVPR, 2024b.

Liunian Harold Li, Pengchuan Zhang, Haotian Zhang, Jianwei Yang, Chunyuan Li, Yiwu Zhong, Lijuan Wang, Lu Yuan, Lei Zhang, Jenq-Neng Hwang, et al. Grounded language-image pre-training. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 10965–10975, 2022.

Qingyun Li, Zhe Chen, Weiyun Wang, Wenhai Wang, Shenglong Ye, Zhenjiang Jin, Guanzhou Chen, Yinan He, Zhangwei Gao, Erfei Cui, et al. Omnicorpus: An unified multimodal corpus of 10 billion-level images interleaved with text. arXiv preprint arXiv:2406.08418, 2024c.

Tianle Li, Wei-Lin Chiang, Evan Frick, Lisa Dunlap, Tianhao Wu, Banghua Zhu, Joseph E. Gonzalez, and Ion Stoica. From crowdsourced data to high-quality benchmarks: Arena-hard and benchbuilder pipeline. CoRR, abs/2406.11939, 2024d. doi: 10.48550/ARXIV.2406.11939. URL https://doi.org/10. 48550/arXiv.2406.11939.

Tsung-Yi Lin, Michael Maire, Serge Belongie, James Hays, Pietro Perona, Deva Ramanan, Piotr Dollár, and C Lawrence Zitnick. Microsoft coco: Common objects in context. In ECCV, 2014.

Shilong Liu, Zhaoyang Zeng, Tianhe Ren, Feng Li, Hao Zhang, Jie Yang, Chun yue Li, Jianwei Yang, Hang Su, Jun-Juan Zhu, and Lei Zhang. Grounding dino: Marrying dino with grounded pre-training for open-set object detection. arXiv:2303.05499, 2023a.

Yuan Liu, Haodong Duan, Bo Li Yuanhan Zhang, Songyang Zhang, Wangbo Zhao, Yike Yuan, Jiaqi Wang, Conghui He, Ziwei Liu, Kai Chen, and Dahua Lin. Mmbench: Is your multi-modal model an all-around player? arXiv:2307.06281, 2023b.

Yuliang Liu, Zhang Li, Mingxin Huang, Biao Yang, Wenwen Yu, Chunyuan Li, Xu-Cheng Yin, ChengLin Liu, Lianwen Jin, and Xiang Bai. Ocrbench: on the hidden mystery of ocr in large multimodal models. Science China Information Sciences, 67(12), December 2024. ISSN 1869-1919. doi: 10.1007/ s11432-024-4235-6. URL http://dx.doi.org/10.1007/s11432-024-4235-6.

Dunjie Lu, Yiheng Xu, Junli Wang, Haoyuan Wu, Xinyuan Wang, Zekun Wang, Junlin Yang, Hongjin Su, Jixuan Chen, Junda Chen, Yuchen Mao, Jingren Zhou, Junyang Lin, Binyuan Hui, and Tao Yu. Videoagenttrek: Computer use pretraining from unlabeled videos, 2025. URL https://arxiv.org/ abs/2510.19488.

Pan Lu, Hritik Bansal, Tony Xia, Jiacheng Liu, Chunyuan Li, Hannaneh Hajishirzi, Hao Cheng, Kai-Wei Chang, Michel Galley, and Jianfeng Gao. Mathvista: Evaluating mathematical reasoning of foundation models in visual contexts. arXiv preprint arXiv:2310.02255, 2023.

Yubo Ma, Yuhang Zang, Liangyu Chen, Meiqi Chen, Yizhu Jiao, Xinze Li, Xinyuan Lu, Ziyu Liu, Yan Ma, Xiaoyi Dong, et al. Mmlongbench-doc: Benchmarking long-context document understanding with visualizations. Advances in Neural Information Processing Systems, 37:95963–96010, 2024.

Junhua Mao, Jonathan Huang, Alexander Toshev, Oana Camburu, Alan L Yuille, and Kevin Murphy. Generation and comprehension of unambiguous object descriptions. In CVPR, 2016.

Ahmed Masry, Do Xuan Long, Jia Qing Tan, Shafiq Joty, and Enamul Hoque. Chartqa: A benchmark for question answering about charts with visual and logical reasoning. arXiv:2203.10244, 2022.

Minesh Mathew, Viraj Bagal, Rubèn Pérez Tito, Dimosthenis Karatzas, Ernest Valveny, and C.V. Jawahar. Infographicvqa. 2022 IEEE/CVF Winter Conference on Applications of Computer Vision (WACV), pp. 2582–2591, 2021a.

Minesh Mathew, Dimosthenis Karatzas, and CV Jawahar. Docvqa: A dataset for vqa on document images. In WACV, 2021b.

Lingchen Meng, Jianwei Yang, Rui Tian, Xiyang Dai, Zuxuan Wu, Jianfeng Gao, and Yu-Gang Jiang. Deepstack: Deeply stacking visual tokens is surprisingly simple and effective for lmms. In Advances in Neural Information Processing Systems, volume 37, pp. 23464–23487, 2024.

OpenAI. Gpt-5 system card, 2025. URL https://cdn.openai.com/gpt-5-system-card.pdf.

Linke Ouyang, Yuan Qu, Hongbin Zhou, Jiawei Zhu, Rui Zhang, Qunshu Lin, Bin Wang, Zhiyuan Zhao, Man Jiang, Xiaomeng Zhao, Jin Shi, Fan Wu, Pei Chu, Minghao Liu, Zhenxiang Li, Chao Xu, Bo Zhang, Botian Shi, Zhongying Tu, and Conghui He. Omnidocbench: Benchmarking diverse pdf document parsing with comprehensive annotations, 2024. URL https://arxiv.org/abs/2412.07626.

Samuel J. Paech. Eq-bench: An emotional intelligence benchmark for large language models. CoRR, abs/2312.06281, 2023. doi: 10.48550/ARXIV.2312.06281. URL https://doi.org/10.48550/arXiv.2312. 06281.

Roni Paiss, Ariel Ephrat, Omer Tov, Shiran Zada, Inbar Mosseri, Michal Irani, and Tali Dekel. Teaching clip to count to ten. In Proceedings of the IEEE/CVF International Conference on Computer Vision, pp. 3170–3180, 2023.

Shishir G. Patil, Huanzhi Mao, Charlie Cheng-Jie Ji, Fanjia Yan, Vishnu Suresh, Ion Stoica, and Joseph E. Gonzalez. The berkeley function calling leaderboard (bfcl): From tool use to agentic evaluation of large language models. In Advances in Neural Information Processing Systems, 2024.

Yusu Qian, Hanrong Ye, Jean-Philippe Fauconnier, Peter Grasch, Yinfei Yang, and Zhe Gan. Mia-bench: Towards better instruction following evaluation of multimodal llms. arXiv preprint arXiv:2407.01509, 2024.

Runqi Qiao, Qiuna Tan, Guanting Dong, Minhui Wu, Chong Sun, Xiaoshuai Song, Zhuoma GongQue, Shanglin Lei, Zhe Wei, Miaoxuan Zhang, et al. We-math: Does your large multimodal model achieve human-like mathematical reasoning? arXiv preprint arXiv:2407.01284, 2024.

Pooyan Rahmanzadehgervi, Logan Bolton, Mohammad Reza Taesiri, and Anh Totti Nguyen. Vision language models are blind: Failing to translate detailed visual features into words, 2025. URL https: //arxiv.org/abs/2407.06581.

Christopher Rawles, Sarah Clinckemaillie, Yifan Chang, Jonathan Waltz, Gabrielle Lau, Marybeth Fair, Alice Li, William Bishop, Wei Li, Folawiyo Campbell-Ajala, et al. Androidworld: A dynamic benchmarking environment for autonomous agents. arXiv:2405.14573, 2024.

David Rein, Betty Li Hou, Asa Cooper Stickland, Jackson Petty, Richard Yuanzhe Pang, Julien Dirani, Julian Michael, and Samuel R. Bowman. GPQA: A graduate-level google-proof q&a benchmark. CoRR, abs/2311.12022, 2023. doi: 10.48550/ARXIV.2311.12022. URL https://doi.org/10.48550/arXiv.2311. 12022.

Jonathan Roberts, Mohammad Reza Taesiri, Ansh Sharma, Akash Gupta, Samuel Roberts, Ioana Croitoru, Simion-Vlad Bogolin, Jialu Tang, Florian Langer, et al. Zerobench: An impossible visual benchmark for contemporary large multimodal models, 2025. URL https://arxiv.org/abs/2502.09696.

Mike Roberts, Jason Ramapuram, Anurag Ranjan, Atulit Kumar, Miguel Angel Bautista, Nathan Paczan, Russ Webb, and Joshua M Susskind. Hypersim: A photorealistic synthetic dataset for holistic indoor scene understanding. In Proceedings of the IEEE/CVF international conference on computer vision, pp. 10912–10922, 2021.

Angelika Romanou, Negar Foroutan, Anna Sotnikova, Zeming Chen, Sree Harsha Nelaturu, Shivalika Singh, Rishabh Maheshwary, Micol Altomare, Mohamed A. Haggag, Imanol Schlag, et al. INCLUDE: evaluating multilingual language understanding with regional knowledge. In The Thirteenth International Conference on Learning Representations, ICLR 2025, Singapore, April 24-28, 2025. OpenReview.net, 2025.

Shuai Shao, Zeming Li, Tianyuan Zhang, Chao Peng, Gang Yu, Xiangyu Zhang, Jing Li, and Jian Sun. Objects365: A large-scale, high-quality dataset for object detection. In Proceedings of the IEEE/CVF international conference on computer vision, pp. 8430–8439, 2019.

Chenglei Si, Yanzhe Zhang, Ryan Li, Zhengyuan Yang, Ruibo Liu, and Diyi Yang. Design2code: Benchmarking multimodal code generation for automated front-end engineering. In Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), pp. 3956–3974, 2025.

Chan Hee Song, Valts Blukis, Jonathan Tremblay, Stephen Tyree, Yu Su, and Stan Birchfield. Robospatial: Teaching spatial understanding to 2d and 3d vision-language models for robotics. In Proceedings of the Computer Vision and Pattern Recognition Conference, pp. 15768–15780, 2025a.

Shuran Song, Samuel P Lichtenberg, and Jianxiong Xiao. Sun rgb-d: A rgb-d scene understanding benchmark suite. In Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 567–576, 2015.

Yueqi Song, Tianyue Ou, Yibo Kong, Zecheng Li, Graham Neubig, and Xiang Yue. Visualpuzzles: Decoupling multimodal reasoning evaluation from domain knowledge. arXiv preprint arXiv:2504.10342, 2025b. URL https://arxiv.org/abs/2504.10342.

Gemini Robotics Team, Saminda Abeyruwan, Joshua Ainslie, Jean-Baptiste Alayrac, Montserrat Gonzalez Arenas, Travis Armstrong, Ashwin Balakrishna, Robert Baruch, Maria Bauza, Michiel Blokzijl, et al. Gemini robotics: Bringing ai into the physical world. arXiv preprint arXiv:2503.20020, 2025.

M-A-P Team. Supergpqa: Scaling LLM evaluation across 285 graduate disciplines. CoRR, abs/2502.14739, 2025. doi: 10.48550/ARXIV.2502.14739. URL https://doi.org/10.48550/arXiv.2502.14739.

Michael Tschannen, Alexey Gritsenko, Xiao Wang, Muhammad Ferjad Naeem, Ibrahim Alabdulmohsin, Nikhil Parthasarathy, Talfan Evans, Lucas Beyer, Ye Xia, Basil Mustafa, et al. Siglip 2: Multilingual vision-language encoders with improved semantic understanding, localization, and dense features. arXiv preprint arXiv:2502.14786, 2025.

Fei Wang, Xingyu Fu, James Y Huang, Zekun Li, Qin Liu, Xiaogeng Liu, Mingyu Derek Ma, Nan Xu, Wenxuan Zhou, Kai Zhang, et al. Muirbench: A comprehensive benchmark for robust multi-image understanding. arXiv preprint arXiv:2406.09411, 2024a.

Ke Wang, Junting Pan, Weikang Shi, Zimu Lu, Houxing Ren, Aojun Zhou, Mingjie Zhan, and Hongsheng Li. Measuring multimodal mathematical reasoning with math-vision dataset. Advances in Neural Information Processing Systems, 37:95095–95169, 2024b.

Peng Wang, Shuai Bai, Sinan Tan, Shijie Wang, Zhihao Fan, Jinze Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin Ge, Yang Fan, Kai Dang, Mengfei Du, Xuancheng Ren, Rui Men, Dayiheng Liu, Chang Zhou, Jingren Zhou, and Junyang Lin. Qwen2-vl: Enhancing vision-language model’s perception of the world at any resolution. arXiv:2409.12191, 2024c.

Weihan Wang, Zehai He, Wenyi Hong, Yean Cheng, Xiaohan Zhang, Ji Qi, Xiaotao Gu, Shiyu Huang, Bin Xu, Yuxiao Dong, et al. Lvbench: An extreme long video understanding benchmark. arXiv preprint arXiv:2406.08035, 2024d.

Wenbin Wang, Liang Ding, Minyan Zeng, Xiabin Zhou, Li Shen, Yong Luo, and Dacheng Tao. Divide, conquer and combine: A training-free framework for high-resolution image perception in multimodal large language models. arXiv preprint, 2024e. URL https://arxiv.org/abs/2408.15556.

Xinyuan Wang, Bowen Wang, Dunjie Lu, Junlin Yang, Tianbao Xie, Junli Wang, Jiaqi Deng, Xiaole Guo, Yiheng Xu, Chen Henry Wu, et al. Opencua: Open foundations for computer-use agents. arXiv preprint arXiv:2508.09123, 2025a.

Yiming Wang, Pei Zhang, Jialong Tang, Haoran Wei, Baosong Yang, Rui Wang, Chenshu Sun, Feitong Sun, Jiran Zhang, Junxuan Wu, Qiqian Cang, Yichang Zhang, Fei Huang, Junyang Lin, et al. Polymath: Evaluating mathematical reasoning in multilingual contexts. CoRR, abs/2504.18428, 2025b. doi: 10.48550/ARXIV.2504.18428. URL https://doi.org/10.48550/arXiv.2504.18428.

Yubo Wang, Xueguang Ma, Ge Zhang, Yuansheng Ni, Abhranil Chandra, Shiguang Guo, Weiming Ren, Aaran Arulraj, Xuan He, Ziyan Jiang, Tianle Li, et al. MMLU-Pro: A more robust and challenging multi-task language understanding benchmark. CoRR, abs/2406.01574, 2024f.

Zhexu Wang, Yiping Liu, Yejie Wang, Wenyang He, Bofei Gao, Muxi Diao, Yanxu Chen, Kelin Fu, Flood Sung, Zhilin Yang, Tianyu Liu, and Weiran Xu. Ojbench: A competition level code benchmark for large language models. CoRR, abs/2506.16395, 2025c. doi: 10.48550/ARXIV.2506.16395. URL https://doi.org/10.48550/arXiv.2506.16395.

Zirui Wang, Mengzhou Xia, Luxi He, Howard Chen, Yitao Liu, Richard Zhu, Kaiqu Liang, Xindi Wu, Haotian Liu, Sadhika Malladi, Alexis Chevalier, Sanjeev Arora, and Danqi Chen. Charxiv: Charting gaps in realistic chart understanding in multimodal llms. arXiv preprint arXiv:2406.18521, $2 0 2 4 \mathrm { g }$ .

Alexander Wettig, Kyle Lo, Sewon Min, Hannaneh Hajishirzi, Danqi Chen, and Luca Soldaini. Organize the web: Constructing domains enhances pre-training data curation. arXiv preprint arXiv:2502.10341, 2025.

Colin White, Samuel Dooley, Manley Roberts, Arka Pal, Benjamin Feuer, Siddhartha Jain, Ravid Shwartz-Ziv, Neel Jain, et al. Livebench: A challenging, contamination-free LLM benchmark. CoRR, abs/2406.19314, 2024. doi: 10.48550/ARXIV.2406.19314. URL https://doi.org/10.48550/arXiv.2406. 19314.

Jinming Wu, Zihao Deng, Wei Li, Yiding Liu, Bo You, Bo Li, Zejun Ma, and Ziwei Liu. Mmsearch-r1: Incentivizing lmms to search. arXiv preprint arXiv:2506.20670, 2025a.

Penghao Wu and Saining Xie. V\*: Guided visual search as a core mechanism in multimodal llms. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pp. 13084– 13094, June 2024.

Yuning Wu, Jiahao Mei, Ming Yan, Chenliang Li, Shaopeng Lai, Yuran Ren, Zijia Wang, Ji Zhang, Mengyue Wu, Qin Jin, and Fei Huang. Writingbench: A comprehensive benchmark for generative writing. CoRR, abs/2503.05244, 2025b. doi: 10.48550/ARXIV.2503.05244. URL https://doi.org/10. 48550/arXiv.2503.05244.

xAI. Realworldqa: A benchmark for real-world spatial understanding. https://huggingface.co/ datasets/xai-org/RealworldQA, 2024. Accessed: 2025-04-26.

Yijia Xiao, Edward Sun, Tianyu Liu, and Wei Wang. Logicvista: Multimodal llm logical reasoning benchmark in visual contexts. arXiv preprint arXiv:2407.04973, 2024.

Tianbao Xie, Jiaqi Deng, Xiaochuan Li, Junlin Yang, Haoyuan Wu, Jixuan Chen, Wenjing Hu, Xinyuan Wang, Yuhui Xu, Zekun Wang, Yiheng Xu, Junli Wang, Doyen Sahoo, Tao Yu, and Caiming Xiong. Scaling computer-use grounding via user interface decomposition and synthesis, 2025a. URL https: //arxiv.org/abs/2505.13227.

Tianbao Xie, Mengqi Yuan, Danyang Zhang, Xinzhuang Xiong, Zhennan Shen, Zilong Zhou, Xinyuan Wang, Yanxu Chen, Jiaqi Deng, Junda Chen, Bowen Wang, Haoyuan Wu, Jixuan Chen, Junli Wang, Dunjie Lu, Hao Hu, and Tao Yu. Introducing osworld-verified. xlang.ai, July 2025b. URL https: //xlang.ai/blog/osworld-verified.

Tianbao Xie, Danyang Zhang, Jixuan Chen, Xiaochuan Li, Siheng Zhao, Ruisheng Cao, et al. Osworld Benchmarking multimodal agents for open-ended tasks in real computer environments. Advances in Neural Information Processing Systems, 37:52040–52094, 2025c.

Weiye Xu, Jiahao Wang, Weiyun Wang, Zhe Chen, Wengang Zhou, Aijun Yang, Lewei Lu, Houqiang Li, Xiaohua Wang, Xizhou Zhu, et al. Visulogic: A benchmark for evaluating visual reasoning in multi-modal large language models, 2025. URL https://arxiv.org/abs/2504.15279.

An Yang, Anfeng Li, Baosong Yang, Beichen Zhang, Binyuan Hui, Bo Zheng, Bowen Yu, et al. Qwen3 technical report, 2025a.

Cheng Yang, Chufan Shi, Yaxin Liu, Bo Shui, Junjie Wang, Mohan Jing, Linran Xu, Xinyu Zhu, Siheng Li, Yuxiang Zhang, et al. Chartmimic: Evaluating lmm’s cross-modal reasoning capability via chart-to-code generation. arXiv preprint arXiv:2406.09961, 2024a.

Jihan Yang, Shusheng Yang, Anjali W Gupta, Rilyn Han, Li Fei-Fei, and Saining Xie. Thinking in space: How multimodal large language models see, remember, and recall spaces. In Proceedings of the Computer Vision and Pattern Recognition Conference, pp. 10632–10643, 2025b.

Zhibo Yang, Jun Tang, Zhaohai Li, Pengfei Wang, Jianqiang Wan, Humen Zhong, Xuejing Liu, Mingkun Yang, Peng Wang, Shuai Bai, LianWen Jin, and Junyang Lin. Cc-ocr: A comprehensive and challenging ocr benchmark for evaluating large multimodal models in literacy, 2024b. URL https://arxiv.org/ abs/2412.02210.

Jiabo Ye, Xi Zhang, Haiyang Xu, Haowei Liu, Junyang Wang, Zhaoqing Zhu, Ziwei Zheng, et al. Mobile agent-v3: Fundamental agents for gui automation. arXiv preprint arXiv:2508.15144, 2025.

Xiang Yue, Yuansheng Ni, Kai Zhang, Tianyu Zheng, Ruoqi Liu, Ge Zhang, et al. Mmmu: A massive multi-discipline multimodal understanding and reasoning benchmark for expert agi. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pp. 9556–9567, 2024a.

Xiang Yue, Tianyu Zheng, Yuansheng Ni, Yubo Wang, Kai Zhang, Shengbang Tong, Yuxuan Sun, Botao Yu, Ge Zhang, Huan Sun, et al. Mmmu-pro: A more robust multi-discipline multimodal understanding benchmark. arXiv preprint arXiv:2409.02813, 2024b.

Renrui Zhang, Dongzhi Jiang, Yichi Zhang, Haokun Lin, Ziyu Guo, Pengshuo Qiu, Aojun Zhou, Pan Lu, Kai-Wei Chang, Yu Qiao, et al. Mathverse: Does your multi-modal llm truly see the diagrams in visual math problems? In European Conference on Computer Vision, pp. 169–186. Springer, 2024.

Yilun Zhao, Lujing Xie, Haowei Zhang, Guo Gan, Yitao Long, Zhiyuan Hu, Tongyan Hu, Weiyuan Chen, Chuhan Li, Junyang Song, Zhijian Xu, Chengye Wang, et al. Mmvu: Measuring expert-level multi-discipline video understanding, 2025. URL https://arxiv.org/abs/2501.12380.

Ziwei Zheng, Michael Yang, Jack Hong, Chenxiao Zhao, Guohai Xu, Le Yang, Chao Shen, and Xing Yu. Deepeyes: Incentivizing" thinking with images" via reinforcement learning. arXiv preprint arXiv:2505.14362, 2025.

Enshen Zhou, Jingkun An, Cheng Chi, Yi Han, Shanyu Rong, Chi Zhang, Pengwei Wang, Zhongyuan Wang, Tiejun Huang, Lu Sheng, et al. Roborefer: Towards spatial referring with reasoning in visionlanguage models for robotics. arXiv preprint arXiv:2506.04308, 2025.

Jeffrey Zhou, Tianjian Lu, Swaroop Mishra, Siddhartha Brahma, Sujoy Basu, Yi Luan, Denny Zhou, and Le Hou. Instruction-following evaluation for large language models. CoRR, abs/2311.07911, 2023. doi: 10.48550/ARXIV.2311.07911. URL https://doi.org/10.48550/arXiv.2311.07911.

Junjie Zhou, Yan Shu, Bo Zhao, Boya Wu, Shitao Xiao, Xi Yang, Yongping Xiong, Bo Zhang, Tiejun Huang, and Zheng Liu. Mlvu: A comprehensive benchmark for multi-task long video understanding. arXiv preprint arXiv:2406.04264, 2024.

Wanrong Zhu, Jack Hessel, Anas Awadalla, Samir Yitzhak Gadre, Jesse Dodge, Alex Fang, Youngjae ${ \mathrm { Y u } } ,$ Ludwig Schmidt, William Yang Wang, and Yejin Choi. Multimodal c4: An open, billion-scale corpus of images interleaved with text. Advances in Neural Information Processing Systems, 36:8958–8974, 2023.

Chengke Zou, Xingang Guo, Rui Yang, Junyu Zhang, Bin Hu, and Huan Zhang. Dynamath: A dynamic visual benchmark for evaluating mathematical reasoning robustness of vision language models. arXiv preprint arXiv:2411.00836, 2024.

# A Benchmarks

We evaluate Qwen3-VL on a wide range of public benchmarks across distinct capabilities: multimodal reasoning, general visual question answering, subjective experience & instruction following, document understanding (including OCR), 2D/3D visual grounding and counting, spatial reasoning, video understanding, GUI agent, and Text-Centric tasks. Below, we provide a detailed list of all the benchmarks used.

• Multimodal Reasoning: We evaluate the models on 12 benchmarks spanning a diverse range of domains—from mathematics and STEM to visual reasoning and puzzle-solving tasks: MMMU (Yue   
et al., 2024a), MMMU-Pro (Yue et al., 2024b), MathVision (Wang et al., 2024b), MathVision-Wildphoto, MathVista (Lu et al., 2023), We-Math (Qiao et al., 2024), MathVerse (Zhang et al., 2024), DynaMath (Zou et al., 2024), Math-VR (Duan et al., 2025), LogicVista (Xiao et al., 2024), VisualPuzzles (Song et al., 2025b), VLM are Blind (Rahmanzadehgervi et al., 2025), ZeroBench (Main/Subtasks) (Roberts et al., 2025), and VisuLogic (Xu et al., 2025).   
General Visual Question Answering: We evaluate the models on 4 General VQA benchmarks:   
MMBench-V1.1 (Liu et al., 2023b), RealWorldQA (xAI, 2024), MMStar (Chen et al., 2024a), and SimpleVQA Cheng et al. (2025).   
• Subjective Experience and Instruction Following: We evaluate the model on 3 benchmarks, across subject experience and complex instruction following: HallusionBench (Guan et al., 2023), MM-MTBench (Agrawal et al., 2024), and MIA-Bench (Qian et al., 2024).   
• Document Understanding: We perform comprehensive evaluation on OCR and document understanding ability of Qwen3-VL series across a diverse range OCR related benchmarks: DocVQA (Mathew et al., 2021b), InfoVQA (Mathew et al., 2021a), AI2D (Kembhavi et al., 2016), ChartQA (Masry et al., 2022), OCRBench (Liu et al., 2024), OCRBench_v2 (Fu et al., 2024b), CC-OCR (Yang et al., 2024b), OmniDocBench (Ouyang et al., 2024), CharXiv (Wang et al., $2 0 2 4 \mathrm { g }$ ), and MMLongBench-Doc (Ma et al., 2024).   
2D/3D Grounding and Spatial Understanding: We evaluate the models on 11 benchmarks include 2D grounding, 3D grounding and spatial understanding: $\mathrm { R e f C O C O / + / g }$ (Kazemzadeh et al., 2014; Mao et al., 2016), ODinW-13 (Li et al., 2022), CountBench (Paiss et al., 2023), ARKitScenes (Baruch et al., 2021), Hypersim (Roberts et al., 2021), SUN RGB-D (Song et al., 2015), ERQA (Team et al., 2025), VSIBench (Yang et al., 2025b), EmbSpatial (Du et al., 2024),RefSpatial (Zhou et al., 2025), and RoboSpatialHome (Song et al., 2025a).   
• Video Understanding: We use seven benchmarks to evaluate the model’s video understanding capabilities: VideoMME (Fu et al., 2024a), MVBench (Li et al., 2024b), VideoMMMU (Hu et al., 2025), MMVU (Zhao et al., 2025), LVBench (Wang et al., 2024d), MLVU (Zhou et al., 2024), Charades-STA (Gao et al., 2017).   
• Coding: We evaluate the model’s multi-modal coding capabilities, particularly in front-end reconstruction and SVG generation, using the Design2Code (Si et al., 2025), ChartMimic (Yang et al., 2024a), and UniSVG (Li et al., 2025a) benchmarks.   
• GUI Agent: We evaluate GUI agent capabilities using benchmarks that test both perception and decision-making. For perception, we use ScreenSpot (Cheng et al., 2024), ScreenSpot Pro (Li et al., 2025b), and OSWorldG (Xie et al., 2025a) to measure GUI grounding and understanding of interface layouts across devices. For decision-making, we use AndroidWorld (Rawles et al., 2024) and OSWorld (Xie et al., 2025c;b) to evaluate interactive control, planning, and execution within real or simulated operating environments.   
• Text-Centric Tasks: We evaluate the models on a wide range of text-centric datasets. (1) Knowledge: MMLU-Pro (Wang et al., 2024f), MMLU-Redux (Gema et al., 2024), GPQA (Rein et al., 2023), Su  
perGPQA (Team, 2025), (2) Reasoning: AIME-25 (AIME, 2025), HMMT-25 (HMMT, 2025), LiveBench (2024-11-25) (White et al., 2024), (3) Code: LiveCodeBench v6 (Jain et al., 2024), CFEval, OJBench (Wang et al., 2025c), (4) Alignment Tasks: IFEval (Zhou et al., 2023), Arena-Hard v2 (Li et al., 2024d) , Creative Writing v3 (Paech, 2023), WritingBench (Wu et al., 2025b), (5) Agent: BFCL-v3 (Patil et al., 2024), TAU2-Retail, TAU2-Airline, TAU2-Telecom, (6) Multilingual: MultiIF (He et al., 2024), MMLU-ProX, INCLUDE (Romanou et al., 2025), PolyMATH (Wang et al., 2025b).

# B Evaluation Prompts

To ensure reproducibility and facilitate future research, we provide here the complete set of prompts used to evaluate our model across all benchmarks. These prompts were consistently applied during inference to maintain fairness and comparability.

# B.1 STEM & Puzzle

# MMMU

<image>   
Question: {question}   
Options:   
{options}   
Please select the correct answer from the options above.

# MMMUPro_Standard

<image>   
{question}   
{options}   
Please select the correct answer from the options.

# MMMUPro_Vision

<image> Identify the problem and solve it. Think step by step before answering.

# MathVista | MathVision | MathVerse | LogicVista

<table><tr><td>&lt;image&gt;</td></tr><tr><td>{question}</td></tr></table>

# We-Math

<image>   
Now, we require you to solve a multiple-choice math question. Please briefly describe your thought process and provide the final answer(option).   
Question: {question}   
Option: {options}   
Regarding the format, please answer following the template below, and be sure to include two $\mathrm { \Phi } < >$ symbols:   
<Thought process>: «your thought process» <Answer>: «your option»

# ZeroBench

<image>   
{question}   
Let’s think step by step and give the final answer in curly braces, like this: {final   
answer}

# DynaMath

<image>   
## Question   
{question}   
## Answer Instruction: Please provide an answer to the question outlined above. Your response should adhere to the following JSON format, which includes two keys: ’solution’ and ’short answer’. The ’solution’ key can contain detailed steps needed to solve the question, and the ’short answer’ key should provide a concise response.   
Example of expected JSON response format:   
{   
"solution": "[Detailed step-by-step explanation]",   
"short answer": "[Concise Answer]"   
}

# VLMBlind

<image> Question: {question}

# VisuLogic

<image>   
{question}   
Solve the complex visual logical reasoning problem through step-by-step reasoning. Think about the reasoning process first and answer the question following this format: Answer://boxed{\$LETTER}

# VisualPuzzles-Direct

<image>   
Question: {question}   
Options:   
{options}   
Answer the question with the option’s letter from the given choices directly.

# VisualPuzzles-CoT

<image>   
Question: {question}   
Options:   
{options}   
Solve the multiple-choice question and then answer with the option letter from the given choices. The last line of your response should be of the following format: ’Answer: \$LETTER’ (without quotes), where LETTER is one of the options. Think step by step before answering.

# B.2 GeneralVQA

# MMBench | RealWorldQA | MMStar

<image>   
Question: {question}   
Options:   
{options}   
Please select the correct answer from the options above.

# SimpleVQA

<image> {question}

# B.3 Alignment

<table><tr><td>HallusionBench 丨MM_MT_Bench 丨 MIA-Bench</td></tr><tr><td>&lt;image&gt;</td></tr><tr><td>{question}</td></tr></table>

# B.4 Document-Understanding

# MMLongBench-Doc

<image_1> <image_2> ... <image_n> {question}

# DocVQA | InfoVQA | ChartQA_TEST

<table><tr><td>&lt;image&gt;</td></tr><tr><td>{question}</td></tr><tr><td>Answer the question using a single word or phrase.</td></tr><tr><td></td></tr></table>

# AI2D

<image>   
Question: {question}   
Options:   
{options}   
Please select the correct answer from the options above.

# OCRBench | OCRBench_v2 | CC-OCR | CharXiv

<table><tr><td>&lt;image&gt;</td></tr><tr><td>{question}</td></tr></table>

# OmniDocBench

<image>

You are an AI assistant specialized in converting PDF images to Markdown format. Please follow these instructions for the conversion:

1. Text Processing: - Accurately recognize all text content in the PDF image without guessing or inferring. - Convert the recognized text into Markdown format. - Maintain the original document structure, including headings, paragraphs, lists, etc.

2. Mathematical Formula Processing:

- Convert all mathematical formulas to LaTeX format. - Enclose inline formulas with \( \). For example: This is an inline formula $\backslash ( \textsf { E } = \mathsf { m c } ^ { \wedge } 2 \textsf { \backslash } )$ - Enclose block formulas with \[ \]. For example: \[ \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} \]

3. Table Processing: - Convert tables to HTML format. - Wrap the entire table with <table> and </table>.

4. Figure Handling: - Ignore figures in the PDF image. Do not attempt to describe or convert images.

5. Output Format: - Ensure the output Markdown document has a clear structure with appropriate line breaks between elements. - For complex layouts, try to maintain the original document’s structure and format as closely as possible.

Please strictly follow these guidelines to ensure accuracy and consistency in the conversion. Your task is to accurately convert the content of the PDF image into Markdown format without adding any extra explanations or comments.

# B.5 2D/3D Grounding

# RefCOCO

<image>   
Locate every object that matches the description "{ref_sentence}" in the image. Report bbox coordinates in JSON format.

# CountBench

<image>   
Question: {question}   
Options:   
{options}   
Please select the correct answer from the options above.

# ODinW-13

<image>   
Locate every instance that belongs to the following categories: ´{obj_names}´. Report bbox coordinates in JSON format.

# ARKitScenes | Hypersim | SUNRGBD

<image> Locate the {class_name } in the provided image and output their positions and dimensions using 3D bounding boxes. The results must be in the JSON format: ["bbox_3d":[x_center, y_center, z_center, x_size, y_size, z_size, roll, pitch, yaw],"label":"category"].

# B.6 Embodied/Spatial Understanding

<table><tr><td>ERQA</td></tr><tr><td>&lt;image_1&gt;</td></tr><tr><td>&lt;image_2&gt;</td></tr><tr><td></td></tr><tr><td>&lt;image_n&gt; {question}</td></tr><tr><td></td></tr></table>

# VSI-Bench

# multiple-choice:

<video>   
These are frames of a video.   
{question}   
Options:   
{options}   
Answer with the option's letter from the given choices directly.

# open-ended:

<video>   
These are frames of a video.   
{question}   
Please answer the question using a single word or phrase.

# EmbSpatialBench

<image> {question}

# RoboSpatialHome

<image>   
Locate {object_name} in this image. Output the point coordinates in JSON format. For example:   
[   
{"point_2d": [x, y], "label": "point_1"}   
]

# RefSpatialBench

<image>   
{question} Output the point coordinates in JSON format. For example:   
[   
{"point_2d": [x, y], "label": "point_1"}   
]

# B.7 Multi-Image

# BLINK

<image>   
Question: {question}   
Options:   
{options}   
Please select the correct answer from the options above.

# MUIRBENCH

<image_1>   
<text_1>   
<image_2>   
<text_2>   
...   
<image_n>   
<text_n>   
Answer with the option’s letter from the given choices directly.

# B.8 Video Understanding

# MVBench | VideoMME | MLVU | LVBench - For instruct models

<video>   
Select the best answer to the following multiple-choice question based on the video. Respond with only the letter (A, B, C, or D) of the correct option.   
Question: {question} Possible answer choices:   
{options}   
The best answer is:

# MVBench | VideoMME | MLVU | LVBench - For thinking models

<video>   
Select the best answer to the following multiple-choice question based on the video. Respond with only the letter (A, B, C, or D) of the correct option.   
Question: {question}   
{options}   
Please reason step-by-step, identify relevant visual content, analyze key timestamps and clues, and then provide the final answer.

# Charades-STA

<video> Give you a textual query: {query_text} When does the described content occur in the video? Please return the timestamp in seconds.

# VideoMMMU

# Perception & Comprehension:

<video>   
{question}   
{options}   
Please ignore the Quiz question in last frame of the video.

# Adaptation-multiple-choice:

<video>   
<image>   
You should watch and learn the video content. Then apply what you learned to answer the following multi-choice question. The image for this question is at the end of the video. {question}   
{options}

# Adaptation-open-ended:

<video>   
<image>   
You should watch and learn the video content. Then apply what you learned to answer the following open-ended question. The image for this question is at the end of the video. {question}

# MMVU

# multiple-choice:

<video>   
{question}   
{options}   
Visual Information: processed video   
Answer the given multiple-choice question step by step. Begin by explaining your reasoning process clearly. Conclude by stating the final answer using the following format: "Therefore, the final answer is: \$LETTER" (without quotes), where \$LETTER is one of the options. Think step by step before answering.

# open-ended:

<video>   
{question}   
Visual Information: processed video   
Answer the given question step by step. Begin by explaining your reasoning process clearly.   
Conclude by stating the final answer using the following format: "Therefore, the final answer is: "Answer: \$ANSWER" (without quotes), where \$ANSWER is the final answer of the question. Think step by step before answering.

# B.9 Perception with Tool

<table><tr><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>Your role is that of a research assistant specializing in visual information. Answer</td></tr><tr><td></td><td></td><td>questions about images by looking at them closely and then using research tools. Please</td><td>follow this structured thinking process and show your work.</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>Start an iterative loop for each question:</td><td></td><td>- **First， look closely:** Begin with a detailed description of the image，paying atention</td><td></td><td></td><td></td><td>to the user&#x27;s question. List what you can tell just by looking，and what you&#x27;ll need to</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>look up.</td><td></td><td></td><td></td><td>- **Next， find information:** Use a tool to research the things you need to find out.</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>- **Then，review the findings:** Carefully analyze what the tool tells you and decide on</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>To finish，bring everything together in a clear，synthesized answer that fully responds</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>You may call one or more functions to assist with the user query.</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>You are provided with function signatures within &lt;tools&gt;&lt;/tools&gt; XML tags:</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>{ &quot;type&quot;:&quot;function&quot;， &quot;function&quot;: {&quot;name&quot;: &quot;image_zoom_in_tool&quot;， &quot;description&quot;: &quot;Zoom in</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>on a specific region of an image by cropping it based on a bounding box (bbox） and an</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>optional object_label&quot;, &quot;arguments&quot;: {&quot;type&quot;: &quot;object&quot;,&quot;properties&quot;: {&quot;bbox_2d&quot;: {&quot;type&quot;:</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>&quot;array&quot;，&quot;items&quot;: {&quot;type&quot;: &quot;number&quot;}，&quot;minItems&quot;: 4，&quot;maxItems&quot;:4，&quot;description&quot;:&quot;The</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>bounding box of the region to zoom in，as [x1，y1，x2，y2]，where (x1，y1） is the</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>&quot;description&quot;: &quot;The name or label of the object in the specified bounding box&quot;}，&quot;img_idx&quot;: {&quot;type&quot;: &quot;number&quot;，&quot;description&quot;: &quot;The index of the zoomed-in image (starting from 0)&quot;}},</td><td></td><td>top-left corner and (x2，y2) is the bottom-right corner&quot;}，&quot;label&quot;: {&quot;type&quot;: &quot;string&quot;,</td><td></td></table>

# HRBench4K | HRBench8K

Your role is that of a research assistant specializing in visual information. Answer questions about images by looking at them closely and then using research tools. Please follow this structured thinking process and show your work.

Start an iterative loop for each question:

- \*\*First, look closely: $\star \star$ Begin with a detailed description of the image, paying attention to the user’s question. List what you can tell just by looking, and what you’ll need to look up.   
- \*\*Next, find information: $\star \star$ Use a tool to research the things you need to find out. - \*\*Then, review the findings: $\star \star$ Carefully analyze what the tool tells you and decide on your next action.

Continue this loop until your research is complete.

To finish, bring everything together in a clear, synthesized answer that fully responds to the user’s question.

#Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags: <tools>

{ "type":"function", "function": {"name": "image_zoom_in_tool", "description": "Zoom in on a specific region of an image by cropping it based on a bounding box (bbox) and an optional object label", "arguments": {"type": "object", "properties": {"bbox_2d": {"type": "array", "items": {"type": "number"}, "minItems": 4, "maxItems": 4, "description": "The bounding box of the region to zoom in, as [x1, y1, $\times 2$ , y2], where (x1, y1) is the top-left corner and ( $\times 2$ , y2) is the bottom-right corner"}, "label": {"type": "string", "description": "The name or label of the object in the specified bounding ${ \mathsf { b o x } } ^ { n } \}$ , "img_idx": {"type": "number", "description": "The index of the zoomed-in image (starting from 0)"}}, "required": ["bbox_2d", "label", "img_idx"]}}}   
</tools>   
For each function call, return a JSON object with function name and arguments within <tool_call></tool_call> XML tags:   
<tool_call>   
{{"name": <function-name>, "arguments": <args-json-object>}}   
</tool_call>   
<image>   
{question}   
{options}

# B.10 Coding

# Design2Code (Generation)

<image>

You are an expert web developer who specializes in HTML and CSS. A user will provide you with a screenshot of a webpage. You need to return a single HTML file that uses HTML and CSS to reproduce the given website. Include all CSS code in the HTML file itself. If it involves any images, use "rick.jpg" as the placeholder. Some images on the webpage are replaced with a blue rectangle as the placeholder, and use "rick.jpg" for those as well. Do not hallucinate any dependencies on external files. You do not need to include JavaScript scripts for dynamic interactions. Pay attention to things like size, text, position, and color of all the elements, as well as the overall layout. Respond with the content of the HTML $+ \mathsf { C S S }$ file:

# Design2Code (GPT-o4-mini Evaluation)

I will give you two images. The first is the reference, and the second is generated from the first via code rendering. Please rate their similarity from 0-100, where 0 means completely different and 100 means identical. Provide the score inside a LaTeX and briefly explain your reasoning.   
<reference_image>   
<generated_image>

# B.11 Agent

# Screenspot | Screenspot-Pro | OSWorld-G

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools> . . . </tools> XML tags:

<tools> { "name":"computer_use", "description": "Use a mouse to interact with a computer. The screen’s resolution is <display_width_px>x <display_height_px>." "notes": "Click with the cursor tip centered on targets; avoid edges unless asked. Do not use other tools (type, key, scroll, left_click_drag). Only left_click and mouse_move are allowed. If you can’t find the element, terminate and report failure.", "parameters":{ "type":"object", "required":["action"], "properties":{ "action":{ "type":"string", "enum":["mouse_move","left_click"], "description":"The action to perform." }, "coordinate":{ "type":"array", "description":"(x, y): pixels from left/top. Required for action=mouse_move and action $=$ left_click." } } } }   
</tools>   
For each function call, return a JSON object with function name and arguments within <tool_call> . . . </tool_call> XML tags:   
<tool_call>   
{{"name": <function-name>, "arguments": <args-json-object>}}   
</tool_call>   
Additionally, if you think the task is infeasible (e.g., the task is not related to the image), return: <tool_call>   
{"name": "computer_use", "arguments": {"action": "terminate", "status": "failure"}} </tool_call>