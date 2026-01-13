# Qwen3-VL-Embedding and Qwen3-VL-Reranker: A Unified Framework for State-of-the-Art Multimodal Retrieval and Ranking

Mingxin Li* Yanzhao Zhang* Dingkun Long* Keqin Chen

Sibo Song Shuai Bai Zhibo Yang Pengjun Xie

An Yang Dayiheng Liu Jingren Zhou Junyang Lin

Tongyi Lab, Alibaba Group

![](images/245eca72933491090d5a2b2152ca3dbf59a6122d52210371f9bd6e010248fe91.jpg)

![](images/dfd7f3c61c025dfe3853104e451abe303f3bf6af8fad6fdb0fcb776693ebbff1.jpg)

https://huggingface.cocollections/Qwen

https://modelscope.cn/organization/qwen

https://github.com/QwenLM/Qwen3-VL-Embedding

# Abstract

In this report, we introduce the Qwen3-VL-Embedding and Qwen3-VL-Reranker model series, the latest extensions of the Qwen family built on the Qwen3-VL foundation model. Together, they provide an end-to-end pipeline for high-precision multimodal search by mapping diverse modalities, including text, images, document images, and video, into a unified representation space. The Qwen3-VL-Embedding model employs a multi-stage training paradigm, progressing from large-scale contrastive pre-training to reranking model distillation, to generate semantically rich high-dimensional vectors. It supports Matryoshka Representation Learning, enabling flexible embedding dimensions, and handles inputs up to 32k tokens. Complementing this, Qwen3-VL-Reranker performs fine-grained relevance estimation for query-document pairs using a cross-encoder architecture with cross-attention mechanisms. Both model series inherit the multilingual capabilities of Qwen3-VL, supporting more than 30 languages, and are released in 2B and 8B parameter sizes to accommodate diverse deployment requirements. Empirical evaluations demonstrate that the Qwen3-VL-Embedding series achieves state-of-the-art results across diverse multimodal embedding evaluation benchmarks. Specifically, Qwen3-VL-Embedding-8B attains an overall score of 77.8 on MMEB-V2, ranking first among all models (as of January 8, 2025). This report presents the architecture, training methodology, and practical capabilities of the series, demonstrating their effectiveness on various multimodal retrieval tasks, including image-text retrieval, visual question answering, and video-text matching.

![](images/90608b216084bdd6f9dd670a898c1a8183dc25b655e7a7e32f7b86a5697d7237.jpg)

![](images/08dde6011acc561bf6eba752023460015bc74ec0dd220e5e27f4625d1a1aca57.jpg)  
Figure 1: Illustration of the Unified Multimodal Representation Space. Qwen3-VL-Embedding model series represent multi-source data (Text, Image, Visual Document, and Video) into a common manifold. By aligning semantic concepts across modalities (e.g., the text "urban architecture" and its corresponding image), the model achieves a holistic understanding of complex visual and textual information.

# 1 Introduction

The exponential growth of multimodal content on the internet has fundamentally transformed how information is created, shared, and consumed. Modern digital ecosystems are increasingly populated with diverse data modalities, including natural images, text documents, infographics, screenshots, and videos. This proliferation necessitates advanced retrieval systems capable of understanding and matching semantic concepts across different modalities, moving beyond traditional text-only search paradigms. Multimodal search, which aims to retrieve relevant content regardless of the query or document modality, has emerged as a critical capability for applications ranging from e-commerce product discovery to scientific literature exploration and social media navigation (Faysse et al., 2025; Fu et al., 2025).

Within contemporary multimodal retrieval architectures, embedding and reranking models constitute the two most critical modules. The field of multimodal representation learning has witnessed significant progress over the past decade (Manzoor et al., 2023; Mei et al., 2025). Among these pioneering works, CLIP (Contrastive Language-Image Pre-training) (Radford et al., 2021) has been particularly influential by demonstrating that large-scale contrastive learning on image-text pairs can produce powerful aligned representations. Its success has cemented the importance of learning shared embedding spaces where semantically similar content is positioned proximate in the representation space regardless of its modality.

As the development of foundation models accelerates, multimodal pre-trained vision-language models (VLMs) such as Qwen-VL (Wang et al., 2024b; Bai et al., 2025) and GPT-4o (Hurst et al., 2024) have achieved unprecedented success in multimodal comprehension. Building on these breakthroughs, the multimodal retrieval community has increasingly explored training unified multimodal embedding models based on VLMs. Notable efforts in this space include E5-V (Jiang et al., 2024), GME (Zhang et al., 2025b), BGE-VL (Zhou et al., 2025), and VLM2Vec (Meng et al., 2025; Jiang et al., 2025). Training unified multimodal representations based on VLMs offers several compelling advantages. First, VLMs possess inherent cross-modal alignment through their pre-training on large-scale image-text datasets. Second, they leverage sophisticated attention mechanisms to capture fine-grained interactions between visual and textual elements. Third, they provide a natural pathway to handling complex multimodal documents such as infographics and presentation slides where visual and textual information are deeply intertwined. Furthermore, VLM-based approaches can inherit the extensive multilingual and multi-domain knowledge encoded in foundation models, enabling more robust generalization across diverse retrieval scenarios.

![](images/21333a1a7a9571fdacf73adcc33f457c99d2c85d9ed8dcf1cfa2752c396218d9.jpg)  
Figure 2: Overview of the Qwen3-VL-Embedding and Qwen3-VL-Reranker architecture.

In this work, we introduce the Qwen3-VL-Embedding and Qwen3-VL-Reranker model series, which are specifically designed for multimodal retrieval applications. Built upon the powerful Qwen3-VL (Bai et al., 2025) foundation model, these models bring together advanced vision-language understanding capabilities with specialized training methodologies tailored for retrieval tasks. The Qwen3-VL-Embedding series employs a sophisticated multi-stage training paradigm that progresses from contrastive pre-training on large-scale multimodal data to knowledge distillation from ranking models, ultimately producing semantically rich embeddings that capture nuanced relationships across modalities. These models support Matryoshka Representation Learning (Kusupati et al., 2022), allowing users to flexibly select embedding dimensions according to their storage and computational constraints without retraining. Additionally, we incorporate quantization-aware training strategies during the training process to ensure that the generated embeddings maintain robust performance after quantization. This capability significantly improves the storage efficiency and computational friendliness of downstream tasks. The models can process inputs containing up to 32,768 tokens, enabling comprehensive understanding of long documents and videos. Complementing the embedding models, the Qwen3-VL-Reranker series adopts a cross-encoder architecture that performs deep cross-attention between query and document representations, providing precise relevance scores for candidate retrieval results. Both model series inherit the impressive multilingual capabilities of the Qwen3-VL foundation model, supporting more than 30 languages with high proficiency, and are released in two sizes (2B, and 8B parameters) to accommodate diverse application scenarios.

We evaluate the Qwen3-VL-Embedding and Qwen3-VL-ReRanker model series across a comprehensive set of benchmarks spanning multiple tasks and domains. Experimental results demonstrate that our embedding and reranking models achieve state-of-the-art performance across multiple types of downstream tasks. For example, the flagship model Qwen3-VL-Embedding-8B attains a score of 77.8 on the MMEB-V2 benchmark (Meng et al., 2025), as evaluated in January 2026, surpassing all models currently on the leaderboard<sup>1</sup>, including both open-source models and closed-source API services. Beyond multimodal evaluation, in pure text evaluation, the Qwen3-VL-Embedding-8B model achieves a mean task score of 67.9 on the MTEB Multilingual benchmark (Enevoldsen et al., 2025a), demonstrating highly competitive performance. Moreover, our reranking model delivers competitive results across a range of retrieval tasks. The Qwen3-VL-Reranker-2B model exceeds previously top-performing models in numerous retrieval tasks, while the larger Qwen3-VL-Reranker-8B model demonstrates even superior performance, improving ranking results by 4.1 points over the 2B model across multiple tasks. Furthermore, we include a constructive ablation study to elucidate the key factors contributing to the superior performance of the Qwen3-VL-Embedding series, providing insights into its effectiveness.

In the following sections, we present the architectural design of our model, elaborate on the training procedures, report comprehensive experimental results for both the embedding and reranking components, and conclude this technical report by synthesizing key findings and discussing promising avenues for future investigation.

Table 1: Model specifications for the Qwen3-VL-Embedding and Qwen3-VL-Reranker. "Quantization Support" indicates the supported quantization formats for the embeddings. "MRL support" denotes whether the embedding model allows user-specified embedding dimensionalities. "Instruction-aware" indicates whether the models support task-specific customization of the input instruction.  

<table><tr><td>Model Type</td><td>Size</td><td>Layers</td><td>Sequence Length</td><td>Embedding Dimension</td><td>Quantization Support</td><td>MRL Support</td><td>Instruction Aware</td></tr><tr><td rowspan="2">Qwen3-VL-Embedding</td><td>2B</td><td>28</td><td>32K</td><td>2048</td><td>Yes</td><td>Yes</td><td>Yes</td></tr><tr><td>8B</td><td>36</td><td>32K</td><td>4096</td><td>Yes</td><td>Yes</td><td>Yes</td></tr><tr><td rowspan="2">Qwen3-VL-Reranker</td><td>2B</td><td>28</td><td>32K</td><td>-</td><td>-</td><td>-</td><td>Yes</td></tr><tr><td>8B</td><td>36</td><td>32K</td><td>-</td><td>-</td><td>-</td><td>Yes</td></tr></table>

# 2 Model

Qwen3-VL-Embedding and Qwen3-VL-Reranker models are designed to make task-aware relevance judgments for multimodal instances. As shown in Figure 2, the embedding model follows a bi-encoder architecture to produce dense vector representations of instances and uses cosine similarity as the relevance measure. In contrast, the reranking model adopts a cross-encoder architecture to provide more fine-grained relevance estimates for each query-document pair.

Model Architecture Both the embedding and reranking models are built on the Qwen3-VL backbone, using causal attention. After being trained on a large-scale collection of multimodal, multi-task relevance data, they retain the backbone's world knowledge, multimodal perception, and instruction-following capabilities, while additionally gaining the ability to estimate relevance. We train two model sizes—2B and 8B—and summarize their specifications in Table 1.

**Embedding Method** The embedding model extracts task-aware dense vectors for multimodal inputs. The input format follows the Qwen3-VL context structure, where the instruction is passed as a system message, with the default instruction being "Represent the user's input." The multimodal instance to be represented is passed as a user message, and it can be in the form of text, images, videos, or any combination of these modalities. Finally, a "PAD" (<|endoftext|>) token is appended to the input, and the last hidden state corresponding to this token is used as the dense vector representation of the instance.

# Input Template for Embedding

```txt
<|im_start|>system  
{Instruction}  
<|im_end|>  
<|im_start|>user  
{Instance}  
<|im_end|><|endoftext|>
```

Reranking Method The reranking model adopts a pointwise ranking approach, which evaluates the relevance between a pair of multimodal instances according to the relevance definition provided in the instruction. The input format follows the Qwen3-VL context structure, where both the relevance-defining instruction and the pair of multimodal instances to be evaluated are passed as user messages. These multimodal inputs can be text, images, videos, or any combination of these modalities. Finally, the relevance estimation for the pair is obtained by calculating the model's probability of predicting "yes" or "no" as the next output token.

# Input Template for Reranking

<|im_start|>system  
Judge whether the Document meets the requirements based on the Query and the Instruct  $\rightarrow$  provided. Note that the answer can only be "yes" or "no".

<|im_end|>  
<|im_start|>user  
<Instruct>: {Instruction}

```javascript
<Query>: {Query}  
<Document>: {Document}  
<|im_end|>  
<|im_start|>assistant
```

# 3 Data

To endow the model with universal representation capabilities across diverse modalities, tasks, and domains, we curated a massive-scale dataset. The distribution of different categories within the dataset is illustrated in Figure 3. However, both publicly available and proprietary in-house data exhibit significant imbalances and, in specific scenarios, notable scarcity across these dimensions. To address these challenges, we leverage data synthesis to construct a balanced training corpus that ensures robust coverage across all modalities, tasks, and domains.

# 3.1 Dataset Format

The complete dataset comprises multiple sub-datasets, denoted as  $\mathcal{D} = \{D_i\}_{i=1}^M$ . Each sub-dataset  $D_i$  is defined by a quadruple  $D_i = (I_i, Q_i, C_i, R_i)$ , structured as follows:

- Instruction  $(I_i)$ : A textual description defining the specific relevance criteria and task objectives for the sub-dataset.  
- Queries  $(Q_{i})$ : A collection of  $N_{q}$  query objects,  $Q_{i} = \{q_{j}\}_{j=1}^{N_{q}}$ . Each  $q_{j}$  can consist of text, images, videos, or any multimodal combination thereof.  
- Corpus  $(C_i)$ : A repository of  $N_d$  document objects,  $C_i = \{d_j\}_{j=1}^{N_d}$ . Similar to queries, each  $d_j$  may be a single modality or a multimodal composite of text, images, and videos.  
- Relevance Labels  $(R_{i})$ : This component identifies the relationships between queries and documents, denoted as  $R_{i} = \{(q_{j},\{d_{j,k}^{+}\}_{k = 1}^{n^{+}},\{d_{j,k}^{-}\}_{k = 1}^{n^{-}})\}_{j = 1}^{N_{q}}$ . For each query  $q_{j}$ ,  $\{d_{j,k}^{+}\}_{k = 1}^{n^{+}} \subset C_{i}$  represents the set of relevant documents (positive documents), while  $\{d_{j,k}^{-}\}_{k = 1}^{n^{-}} \subset C_{i}$  represents the set of irrelevant documents (negative documents).

Representative dataset examples are presented in Appendix A.

# 3.2 Data Synthesis

![](images/64dae933cfad639b3678d4df143a29faa38e6751c363d37edfe5bff60c615e73.jpg)  
Figure 3: Distribution of different categories in the training data.

![](images/aa59683a625281352fcedbd512910ee8699666e529c2edf6d18ce7502a460323.jpg)  
(a) image

![](images/52553faf3bd3bac743e96f469d833e2e97d12b6ddf545631731a7109a9ddb37b.jpg)  
(b) video  
Figure 4: Data distribution of the seed pool for data synthesis.

We employ data synthesis to construct various sub-datasets  $D_{i}$ . Specifically, we extend the methodology introduced in Qwen3 Embedding (Zhang et al., 2025c) to multimodal scenarios.

Seed Pool Construction Since the diversity of synthesized data depends on the underlying seed pool, we first aggregate an extensive collection of high-quality and diverse raw image and video datasets. To establish a high-quality foundation, we first apply coarse-grained quality filtering to prune assets with low resolutions or irregular aspect ratios. This is followed by structural refinement, specifically employing scene cut detection and removing static or corrupted segments, to preserve the integrity of temporal dynamics in video data. Subsequently, we leverage Qwen3-VL-32B (Bai et al., 2025) to generate fine-grained categorical labels for the remaining assets. To ensure cross-modal alignment, we implement a rigorous filtering mechanism that excludes samples with low-confidence annotations or poor visual-text correspondence, as measured by similarity scores from the GME (Zhang et al., 2025b) embedding model. Finally, we perform category-wise rebalancing on the refined dataset to construct the final seed pool. The resulting category distribution is illustrated in Figure 4.

Based on the seed pool, we leverage Qwen3-VL-32B (Bai et al., 2025) to perform multimodal and multi-task annotation.

Image Tasks Annotation We synthesize image datasets across three primary task paradigms:

1. Image Classification: The query  $q$  comprises an image and a classification instruction, while the document  $d$  is the specific category label. We synthesize datasets for a wide range of classification tasks, including object recognition, scene parsing, landmark identification, and action recognition. For each sample, the model designates a specific task type and annotates the image with its ground-truth category along with a semantically confusing negative label.  
2. Image Question Answering: The query  $q$  consists of an image and a grounded question, and the document  $d$  is the corresponding answer. We generate diverse QA pairs covering factoid identification, visual reasoning, OCR-based data extraction, and domain-specific knowledge inquiry. Following a prescribed task orientation, the model formulates a question based on the visual content, providing a ground-truth response and a plausible but deceptive distractor.  
3. Image Retrieval: The query  $q$  is a search text, and the document  $d$  is the candidate image. We synthesize retrieval queries across a hierarchy of semantic depths, spanning direct visual descriptions, abstract narrative scenarios, compositional logical constraints, and knowledge-centric textual localization. The model assigns a specific retrieval intent and generates a corresponding search query that captures either the salient visual features or the embedded textual logic within the image.

Video Tasks Annotation We synthesize video datasets across four primary task paradigms:

1. Video Classification: The query  $q$  combines a video with a classification task, and the document  $d$  is the resulting category. We synthesize datasets for diverse classification tasks, including activity recognition, scene parsing, event categorization, and sentiment/intent analysis. For each sample, the model identifies its category and generates a semantically related negative label.  
2. Video Question Answering: The query  $q$  includes a video and a question, while the document  $d$  is the answer. We generate diverse QA pairs spanning factual identification, temporal grounding, thematic reasoning, and cinematic analysis. Guided by a specified task type, the model formulates a question and provides a correct response and a deceptive distractor.  
3. Video Retrieval: The query  $q$  is a textual description, and the document  $d$  is the video. We synthesize retrieval queries across a spectrum of semantic granularities, ranging from entity and action-centric searches to temporal-event descriptions, thematic/emotional discovery, and instructional tutorial localization. The model produces a search query that captures the primary events and thematic content of the video.  
4. Moment Retrieval: The query  $q$  is a textual query (optionally including a keyframe), and the document  $d$  is a specific video segment. The moment retrieval task aims at fine-grained temporal grounding. The model identifies a specific target—such as an action, object, or character—and localizes a relevant temporal segment. Simultaneously, it identifies an irrelevant segment with a clear temporal gap to serve as a negative contrast.

Prior to synthesizing task-specific annotations, we require the model to generate a descriptive caption for each image or video to provide necessary context. This two-step approach ensures higher quality and consistency in the subsequent annotation generation. Selected prompt examples for the synthesis of specific tasks are provided in Appendix B.

![](images/e8648634de47d1c5820e357bfaaf580a3886ddd83811d2f5b5734c56d134defe.jpg)  
Figure 5: The multi-stage training pipeline of Qwen3-VL-Embedding and Qwen3-VL-Reranker.

# 3.3 Positive Refinement and Hard Negative Mining

Hard negative samples play a crucial role in contrastive representation learning (Robinson et al., 2021). To enhance the quality of positive pairs and identify effective hard negatives, we implement an automated two-stage mining pipeline: Recall and Relevance Filtering.

Recall For each sub-dataset  $D_{i}$ , we use an embedding model to extract representations for all queries  $q_{j} \in Q_{i}$  and documents  $d_{k} \in C_{i}$ . For each query  $q_{j}$ , we retrieve the top- $K$  most relevant candidates  $\{d_k\}_{k=1}^K$  based on cosine similarity, denoted as relevance scores  $S = \{s_{j,k}\}_{k=1}^K$ .

Relevance Filtering Finally, we refine the relevance labels  $R_{i}$  based on the relevance scores  $S$  to eliminate noise:

- Positive Refinement: We retain  $q_{j}$  only if at least one positive document  $d^{+} \in \{d_k\}_{k=1}^K$  achieves a score  $s > t^{+}$ , where  $t^{+}$  is a hyperparameter acting as the score threshold. If no such candidate exists, the query  $q_{j}$  is discarded.  
- Hard Negative Selection: For a valid query  $q_j$ , we compute the average score of its refined positive samples,  $\bar{s}^+$ . Any non-positive document  $d \in \{d_k\}_{k=1}^K$  is selected as a hard negative only if its score satisfies  $s < \bar{s}^+ + \delta^-$ , where  $\delta^-$  is a small safety margin to prevent the inclusion of "false negatives".

# 4 Training Strategy

To train our Qwen3-VL-Embedding and Qwen3-VL-Reranker, we employ a multi-stage training pipeline, as shown in Figure 5. This approach is designed to mitigate the data imbalance between abundant weakly-supervised data and scarce high-quality samples (Wang et al., 2022; Li et al., 2023; Chen et al., 2024; Zhang et al., 2025c). The model is first pre-trained on vast amounts of weakly supervised, noisy data to establish a baseline for relevance understanding and to boost generalization. We then perform fine-tuning on high-quality, task-specific datasets to steer the model toward more precise relevance scoring and fine-grained interaction. In addition to the aforementioned reasons, another objective of the multi-stage training strategy is to bootstrap both data quality and model performance. As the training progresses through successive stages, the model's capabilities are continuously enhanced. This improvement, in turn, facilitates more effective data mining, thereby refining the quality of the training data. This iterative cycle ultimately leads to a substantial boost in the model's overall performance.

# 4.1 Multi-stage Training

We implement a three-stage training strategy as follows:

Stage 1: Contrastive Pre-training In the pre-training stage, we first perform contrastive learning on the embedding model using large-scale, multimodal, and multi-task synthetic data. The synthetic data utilized in this stage is mined using the methodology described in Section 3.3, utilizing an existing open-source model (Zhang et al., 2025b) as the embedding model.

The optimization objective employed during training is defined in Equation 1. Upon completion of this stage, we obtain the initial model version, Qwen3-VL-Embedding: s0.

Stage 2: Multi-Task Contrastive Learning and Supervised Fine-Tuning In this stage, we primarily utilize a combination of curated public datasets and proprietary in-house data, augmented with sampled synthetic data to address the task imbalance inherent in existing datasets. Benefiting from the improved multi-task performance of Qwen3-VL-Embedding: s0, we employ this model to perform data mining, thereby ensuring high data quality across various tasks. We then train our embedding model using multi-task contrastive learning, implementing tailored contrastive objectives for different task types (see Section 5.1 for details). This results in Qwen3-VL-Embedding: s1.

Simultaneously, we train a new reranking model, Qwen3-VL-Reranker, by training on the retrieval-specific subset of the newly mined data, using Equation 4 as the optimization objective. This subset encompasses diverse tasks, including image retrieval, video retrieval, moment retrieval, and visual document retrieval. The resulting model demonstrates superior performance across these retrieval-centric tasks.

Stage 3: Distillation and Model Merging In this final stage, we further enhance the embedding model by distilling the relevance discrimination expertise from the previously trained Qwen3-VL-Reranker. To achieve this, we curate a compact sub-dataset from both public and proprietary sources, ensuring a balanced distribution across multiple retrieval categories. We then employ Qwen3-VL-Reranker to generate fine-grained relevance scores for this subset, which serves as the supervision signal for training the embedding model under the objective defined in Equation 3. This distillation process yields Qwen3-VL-Embedding: s2.

While Qwen3-VL-Embedding: s2 exhibits significant gains in retrieval-centric tasks, it suffers a slight performance degradation in classification and QA tasks. To address this, we merge Qwen3-VL-Embedding: s2 with Qwen3-VL-Embedding: s1 using the methodology proposed by Li et al. (2024). This process results in our final model, Qwen3-VL-Embedding: s3, which achieves optimal and balanced performance across all evaluated tasks.

# 4.2 Implementation

We employ Low-Rank Adaptation (LoRA) (Hu et al., 2022) for model training, with the model parameters initialized from Qwen3-VL-Instruct. This approach offers several key advantages: 1) reduced memory footprint, allowing for larger effective batch sizes; 2) enhanced generalization performance; and 3) significantly more efficient hyperparameter search for model merging (Li et al., 2024). Additionally, we adopt dynamic resolution and frame rates. For the image modality, we preserve the original aspect ratio while capping the maximum token consumption at 1,280 (approximately  $1.3 \times 10^{6}$  pixels). For video, we first sample at 1 FPS with a maximum of 64 frames. For each frame, the aspect ratio is maintained, and the total token budget for all frames is constrained to 4,500 (approximately  $9.2 \times 10^{6}$  pixels).

# 5 Training Objective

This section outlines the training objectives for the Qwen3-VL-Embedding and Qwen3-VL-Reranker. For Qwen3-VL Embedding model, We extend the loss function from the Qwen3 Embedding model (Zhang et al., 2025c) to handle a wider variety of data types. We also integrate two key techniques: Matryoshka Representation Learning (MRL) (Kusupati et al., 2022) to produce variable-dimension embeddings, and Quantization-Aware Training (QAT) (Esser et al., 2020) to support multiple numerical precisions. Together, these methods reduce storage and compute costs, improving inference efficiency. The Qwen3-VL-Reranker adopts the same objective function as Qwen3 Reranker (Zhang et al., 2025c). The specific loss functions for each model are detailed below.

# 5.1 Loss Functions for the Embedding Model

The training of Qwen3-VL-Embedding involves diverse data types across multiple stages. To accommodate this, we employ distinct loss function tailored to the specific characteristics of each data category.

Loss for Retrieval Data This category includes data from various multimodal and cross-modal retrieval tasks, such as Text-to-Text (T2T), Text-to-Image (T2I), and Image+Text-to-Image+Text (IT2IT) retrieval. In Stage 1, we use the same InfoNCE loss (Oord et al., 2018) formulation as in the Qwen3-Embedding:

$$
\mathcal {L} _ {\text {r e t r i e v a l}} = - \frac {1}{N} \sum_ {i} ^ {N} \log \frac {e ^ {(s \left(q _ {i} , d _ {i} ^ {+}\right) / \tau)}}{Z _ {i}}, \tag {1}
$$

where  $s(\cdot, \cdot)$  is a similarity function (we use cosine similarity),  $\tau$  is a temperature parameter, and  $Z_{i}$  aggregates scores from the positive pair and various types of negative pairs:

$$
Z _ {i} = e ^ {(s (q _ {i}, d _ {i} ^ {+}) / \tau)} + \sum_ {k} ^ {K} m _ {i k} e ^ {(s (q _ {i}, d _ {i, k} ^ {-}) / \tau)} + \sum_ {j \neq i} m _ {i j} e ^ {(s (q _ {i}, q _ {j}) / \tau)} + \sum_ {j \neq i} m _ {i j} e ^ {(s (d _ {i} ^ {+}, d _ {j}) / \tau)} + \sum_ {j \neq i} m _ {i j} e ^ {(s (q _ {i}, d _ {j}) / \tau)}
$$

corresponding to similarities with (1) the positive document  $d_{i}^{+}$ , (2)  $K$  hard negatives  $\{d_{i,k}^{-}\}_{k=1}^{K}$ , (3) other in-batch queries  $\{q_{j}\}_{j \neq i}$ , (4) other in-batch documents  $\{d_{j}\}_{j \neq i}$  contrasted with  $d_{i}^{+}$ , and (5) other in-batch documents  $\{d_{j}\}_{j \neq i}$  contrasted with  $q_{i}$ .  $m_{ij}$  is a masking factor to mitigate the impact of false negatives:

$$
m _ {i j} = \left\{ \begin{array}{l l} 0, & \text {i f} s _ {i j} > s (q _ {i}, d _ {i} ^ {+}) + 0. 1 \text {o r} d _ {j} = d _ {i} ^ {+}, \\ 1, & \text {o t h e r w i s e}, \end{array} \right.
$$

where  $s_{ij}$  denotes the corresponding similarity score (e.g.,  $s(q_i, d_j)$  or  $s(q_i, q_j)$ ).

In Stage 2, we further modify the objective by removing the query-query and document-document terms from  $Z_{i}$ . Empirically, this adjustment yields better performance on high-quality multimodal retrieval data.

Loss for Classification Data For text or image classification tasks, we likewise formulate training as contrastive learning. Specifically, the instance to be classified is treated as a query  $q$ , and its class label is treated as the corresponding document  $d^{+}$ . In contrast to retrieval, negative samples are restricted to explicitly incorrect labels for the same query, while other labels in the batch are ignored to avoid introducing false negatives.

Semantic Textual Similarity (STS) Data STS datasets are symmetric and thus do not admit a natural query-document asymmetry. Moreover, supervision is typically provided as real-valued similarity scores. To exploit this fine-grained signal, we optimize the model with the CoSent loss (Huang et al., 2024), which encourages cosine similarities between paired embeddings to preserve the ordering induced by ground-truth similarity scores:

$$
\mathcal {L} _ {\mathrm {s t s}} = \log \left(1 + \sum_ {\hat {s} (q _ {i}, d _ {j}) > \hat {s} (q _ {m}, d _ {n})} \exp \left(\frac {\cos \left(q _ {m} , d _ {n}\right) - \cos \left(q _ {i} , d _ {j}\right)}{\tau}\right)\right), \tag {2}
$$

where  $\hat{s}(q_i, d_j)$  denotes the ground-truth score for the pair  $(q_i, d_j)$ .

Distillation Data In the final training stage, we further improve the embedding model via knowledge distillation. We sample a high-quality subset from the union of all training data and use a strong reranker to provide supervision. Concretely, for each query  $q$ , we pre-compute (offline) reranker relevance logits for its positive document and  $k$  negatives. During training, we compute embedding-based scores online using cosine similarity and minimize a distribution-matching objective (cross-entropy) to align the embedding model's score distribution with that of the reranker:

$$
\mathcal {L} _ {\text {d i s t i l l}} = - \sum_ {i = 1} ^ {k + 1} P _ {\text {r e r a n k e r}} \left(d _ {i} \mid q\right) \log P _ {\text {e m b e d d i n g}} \left(d _ {i} \mid q\right), \tag {3}
$$

where  $P(d_{i} \mid q)$  is the softmax distribution over the  $(k + 1)$  candidate documents (one positive and  $k$  negatives) for query  $q$ .

# 5.1.1 Additional Techniques for Efficient Inference

In practical retrieval systems, index construction requires storing a large number of embeddings offline. To reduce storage overhead and improve retrieval efficiency, we incorporate the following auxiliary training objectives.

Matryoshka Representation Learning (MRL) When optimizing the objectives described above, we compute each loss not only on the full-dimensional embedding, but also on truncated lower-dimensional prefixes of the same representation (Kusupati et al., 2022). Empirically, training over a sufficiently dense set of MRL dimensions yields strong generalization, enabling competitive performance at intermediate dimensions that are not explicitly included during training.

Quantization-Aware Training (QAT) Storing embeddings with lower numerical precision (int8 or binary) can further reduce both storage and compute overhead. To preserve embedding quality under low-precision representations, we adopt a quantization-aware training (QAT) strategy. Concretely, during training we compute the optimization objective using both full-precision embeddings and their low-precision (quantized) counterparts, so that the model learns to produce embeddings that are robust to quantization. This allows the learned representations to better adapt to low-bit embedding formats, mitigating the performance degradation that may otherwise occur at deployment time. We instantiate QAT with Learned Step Size Quantization (LSQ) (Esser et al., 2020). LSQ treats the quantization scale (step size) as a learnable parameter and optimizes it jointly with the model weights via backpropagation. In addition, it uses a Straight-Through Estimator (STE) (Bengio et al., 2013) to propagate gradients through the non-differentiable rounding operation, enabling end-to-end training under simulated quantization.

# 5.2 Loss Function for the Reranking Model

We frame reranking as a binary classification problem: given a query-document pair, the model predicts either a special yes token (relevant) or no token (irrelevant).

$$
\mathcal {L} _ {\text {r e r a n k i n g}} = - \log p (l | I, q, d), \tag {4}
$$

where  $p(\cdot |*)$  denotes the probability assigned by the VLM. The label  $l$  is "yes" for positive pairs and "no" for negatives. This loss function encourages the model to assign higher probabilities to correct labels, thereby improving the ranking performance (Dai et al., 2025).

During inference, the final relevance score is computed by applying the sigmoid function to the difference between the logits of the 'yes' and 'no' tokens:

$$
s = \operatorname {s i g m o i d} (\operatorname {l o g i t} (\text {y e s}) - \operatorname {l o g i t} (\text {n o})). \tag {5}
$$

# 6 Evaluation

# 6.1 Multimodal Benchmarks

To evaluate the overall performance of Qwen3-VL-Embedding in multimodal and multi-task representation learning, we report its results on the MMEB-v2 benchmark (Meng et al., 2025). MMEB-v2 provides a comprehensive assessment spanning three primary domains—Image, Video, and Visual Document—comprising nine task categories and 78 datasets in total. We compared our model against several prominent open-source and proprietary baselines. During evaluation, the context length is constrained to 16,384 tokens. For image-based tasks, the maximum token consumption is set at 1,800, while for video-based tasks, we cap the total tokens at 15,000 and the frame count at 64. As summarized in Table 2, the results demonstrate that our model achieves state-of-the-art (SOTA) average performance and exhibits exceptional proficiency across all three domains. Specifically, Qwen3-VL-Embedding-8B achieves an average score of 77.8 on MMEB-v2, representing a  $6.7\%$  improvement over the previous best open-source model.

# 6.2 Visual Document Benchmarks

In addition to the evaluation datasets in MMEB-V2, we conducted further tests on the latest JinaVDR (Günther et al., 2025) and Vidore-v3  $^{3}$  benchmarks for visual document retrieval tasks. We compared our models with current state-of-the-art ColPali-style models, with the results illustrated in Table 3. As shown, our embedding model achieves performance comparable to ColPali-style models that require significantly higher computational costs. Furthermore, our reranker model substantially outperforms ColPali models of a similar parameter size.

Table 2: Results on the MMEB-V2 benchmark (Meng et al., 2025). CLS: classification, QA: question answering, RET: retrieval, GD: grounding, MRET: moment retrieval, VDR: ViDoRe, VR: VisRAG, OOD: out-of-distribution.  $\dagger$ : link to the model's homepage. All models except IFM-TTE have been re-evaluated on the updated VisDoc OOD $^2$ split.  

<table><tr><td rowspan="2">Model</td><td rowspan="2">Size</td><td colspan="5">Image</td><td colspan="5">Video</td><td colspan="5">VisDoc</td><td rowspan="2">All</td></tr><tr><td>CLS</td><td>QA</td><td>RET</td><td>GD</td><td>Overall</td><td>CLS</td><td>QA</td><td>RET</td><td>MRET</td><td>Overall</td><td>VDRv1</td><td>VDRv2</td><td>VR</td><td>OOD</td><td>Overall</td></tr><tr><td># of Datasets →</td><td></td><td>10</td><td>10</td><td>12</td><td>4</td><td>36</td><td>5</td><td>5</td><td>5</td><td>3</td><td>18</td><td>10</td><td>4</td><td>6</td><td>4</td><td>24</td><td>78</td></tr><tr><td colspan="18">Open-Source Models</td></tr><tr><td>VLM2Vec (Jiang et al., 2025)</td><td>2B</td><td>58.7</td><td>49.3</td><td>65</td><td>72.9</td><td>59.7</td><td>33.4</td><td>30.5</td><td>20.6</td><td>30.7</td><td>28.6</td><td>49.8</td><td>13.5</td><td>51.8</td><td>48.2</td><td>44</td><td>47.7</td></tr><tr><td>VLM2Vec-V2 (Meng et al., 2025)</td><td>2B</td><td>62.9</td><td>56.3</td><td>69.5</td><td>77.3</td><td>64.9</td><td>39.3</td><td>34.3</td><td>28.8</td><td>36.8</td><td>34.6</td><td>75.5</td><td>44.9</td><td>79.4</td><td>62.2</td><td>69.2</td><td>59.2</td></tr><tr><td>GME (Zhang et al., 2025b)</td><td>2B</td><td>54.4</td><td>29.9</td><td>66.9</td><td>55.5</td><td>51.9</td><td>34.9</td><td>42.0</td><td>25.6</td><td>31.1</td><td>33.6</td><td>86.1</td><td>54.0</td><td>82.5</td><td>67.5</td><td>76.8</td><td>55.3</td></tr><tr><td>Ops-MM-embedding-v1†</td><td>2B</td><td>68.1</td><td>65.1</td><td>69.2</td><td>80.9</td><td>69.0</td><td>53.6</td><td>55.6</td><td>41.8</td><td>33.7</td><td>47.6</td><td>76.4</td><td>53.2</td><td>77.6</td><td>64.2</td><td>70.8</td><td>64.6</td></tr><tr><td>RzenEmbed (Jian et al., 2025)</td><td>2B</td><td>68.5</td><td>66.3</td><td>74.5</td><td>90.3</td><td>72.3</td><td>50.4</td><td>49.7</td><td>46.6</td><td>38.9</td><td>47.3</td><td>87.1</td><td>55.1</td><td>87.2</td><td>43.4</td><td>74.5</td><td>67.2</td></tr><tr><td>VLM2Vec (Jiang et al., 2025)</td><td>8B</td><td>62.7</td><td>56.9</td><td>69.4</td><td>82.2</td><td>65.5</td><td>39.1</td><td>30.0</td><td>29.0</td><td>38.9</td><td>33.7</td><td>56.9</td><td>9.4</td><td>59.1</td><td>54.0</td><td>49.1</td><td>53.1</td></tr><tr><td>GME (Zhang et al., 2025b)</td><td>8B</td><td>57.7</td><td>34.7</td><td>71.2</td><td>59.3</td><td>56.0</td><td>37.4</td><td>50.4</td><td>28.4</td><td>37.0</td><td>38.4</td><td>89.4</td><td>55.6</td><td>85.0</td><td>68.3</td><td>79.3</td><td>59.1</td></tr><tr><td>Ops-MM-embedding-v1†</td><td>8B</td><td>69.7</td><td>69.6</td><td>73.1</td><td>87.2</td><td>72.7</td><td>59.7</td><td>62.2</td><td>45.7</td><td>43.2</td><td>53.8</td><td>80.1</td><td>59.6</td><td>79.3</td><td>67.8</td><td>74.4</td><td>68.9</td></tr><tr><td>RzenEmbed (Jian et al., 2025)</td><td>8B</td><td>70.6</td><td>71.7</td><td>78.5</td><td>92.1</td><td>75.9</td><td>58.8</td><td>63.5</td><td>51.0</td><td>45.5</td><td>55.7</td><td>89.7</td><td>60.7</td><td>88.7</td><td>69.9</td><td>81.3</td><td>72.9</td></tr><tr><td colspan="18">Closed-Source Models</td></tr><tr><td>IFM-TTE†</td><td>8B</td><td>76.7</td><td>78.5</td><td>74.6</td><td>89.3</td><td>77.9</td><td>60.5</td><td>67.9</td><td>51.7</td><td>54.9</td><td>59.2</td><td>85.2</td><td>71.5</td><td>92.7</td><td>53.3</td><td>79.5</td><td>74.1</td></tr><tr><td>Seed-1.6-embedding-0615†</td><td>-</td><td>76.1</td><td>74.0</td><td>77.9</td><td>91.3</td><td>77.8</td><td>55.0</td><td>60.8</td><td>51.3</td><td>53.5</td><td>55.3</td><td>85.3</td><td>56.6</td><td>84.7</td><td>68.6</td><td>77.7</td><td>72.6</td></tr><tr><td>Seed-1.6-embedding-1215†</td><td>-</td><td>75.0</td><td>74.9</td><td>79.3</td><td>89.0</td><td>78.0</td><td>85.2</td><td>66.7</td><td>59.1</td><td>54.8</td><td>67.7</td><td>90.0</td><td>60.3</td><td>90.0</td><td>70.7</td><td>82.2</td><td>76.9</td></tr><tr><td colspan="18">Qwen3 VL Embedding Models</td></tr><tr><td>Qwen3-VL-Embedding-2B</td><td>2B</td><td>70.3</td><td>74.3</td><td>74.8</td><td>88.5</td><td>75.0</td><td>71.9</td><td>64.9</td><td>53.9</td><td>53.3</td><td>61.9</td><td>84.4</td><td>65.3</td><td>86.4</td><td>69.4</td><td>79.2</td><td>73.2</td></tr><tr><td>Qwen3-VL-Embedding-8B</td><td>8B</td><td>74.2</td><td>81.1</td><td>80.2</td><td>92.3</td><td>80.1</td><td>78.4</td><td>71.0</td><td>58.7</td><td>56.1</td><td>67.1</td><td>87.2</td><td>69.9</td><td>88.7</td><td>73.3</td><td>82.4</td><td>77.8</td></tr></table>

Table 3: Results on visual document retrieval benchmarks. All results are obtained from our experimental runs.  

<table><tr><td>Model</td><td>Size</td><td>VisRAG</td><td>VisDocOOD</td><td>Vidore-v1</td><td>Vidore-v2</td><td>Vidore-v3</td><td>JinaVDR</td><td>Avg</td></tr><tr><td>llama-nemoretriever-colembed-1b-v1 (Xu et al., 2025)</td><td>1B</td><td>82.4</td><td>65.6</td><td>90.5</td><td>62.1</td><td>55.5</td><td>66.4</td><td>70.4</td></tr><tr><td>llama-nemoretriever-colembed-3b-v1 (Xu et al., 2025)</td><td>3B</td><td>85.5</td><td>69.7</td><td>91.0</td><td>55.5</td><td>57.1</td><td>67.8</td><td>71.1</td></tr><tr><td>colnomic-embed-multimodal-3b (Team, 2025)</td><td>3B</td><td>86.8</td><td>71.0</td><td>89.7</td><td>63.5</td><td>56.4</td><td>77.6</td><td>74.2</td></tr><tr><td>colqwen2.5-v0.2 (Faysse et al., 2025)</td><td>3B</td><td>86.6</td><td>70.9</td><td>89.5</td><td>59.3</td><td>52.4</td><td>75.6</td><td>72.4</td></tr><tr><td>tomoro-colqwen3-embed-4b (Huang &amp;Tan, 2025)</td><td>4B</td><td>89.0</td><td>75.9</td><td>90.6</td><td>66.0</td><td>60.2</td><td>76.2</td><td>76.5</td></tr><tr><td>colnomic-embed-multimodal-7b (Team, 2025)</td><td>7B</td><td>88.7</td><td>75.6</td><td>90.0</td><td>62.0</td><td>57.6</td><td>78.9</td><td>75.5</td></tr><tr><td>tomoro-colqwen3-embed-8b (Huang &amp;Tan, 2025)</td><td>8B</td><td>90.2</td><td>76.8</td><td>90.8</td><td>67.7</td><td>61.6</td><td>79.2</td><td>77.7</td></tr><tr><td colspan="9">Qwen3 VL Embedding Models</td></tr><tr><td>Qwen3-VL-Embedding-2B</td><td>2B</td><td>86.3</td><td>74.3</td><td>84.4</td><td>65.3</td><td>52.9</td><td>71.0</td><td>72.2</td></tr><tr><td>Qwen3-VL-Embedding-8B</td><td>8B</td><td>88.8</td><td>78.3</td><td>87.2</td><td>69.9</td><td>59.0</td><td>76.9</td><td>76.7</td></tr><tr><td colspan="9">Qwen3 VL Reranking Models</td></tr><tr><td>Qwen3-VL-Ranker-2B</td><td>2B</td><td>89.7</td><td>77.5</td><td>90.3</td><td>62.5</td><td>60.8</td><td>80.9</td><td>77.0</td></tr><tr><td>Qwen3-VL-Ranker-8B</td><td>8B</td><td>91.1</td><td>80.4</td><td>91.7</td><td>71.3</td><td>66.7</td><td>83.6</td><td>80.8</td></tr></table>

# 6.3 Text Benchmarks

Table 4 compares our Qwen3-VL-Embedding models with standard text-only embedding models on the MMTEB (Enevoldsen et al., 2025b) benchmark. Compared to text-only Qwen3 embedding models of similar sizes, the Qwen3-VL-Embedding model series show slightly lower performance. Nevertheless, Qwen3-VL-Embedding maintains competitive performance on pure text tasks. Specifically, Qwen3-VL-Embedding-8B achieves a mean task score of 67.9 on MMTEB, performing on par with other similarly sized text-only embedding models.

# 6.4 Evaluation for Reranking Model

Table 5 presents the evaluation results across various reranking tasks. For multimodal retrieval, we utilize the MMEB-v2 suite, covering image, video (including moment retrieval), and visual document tasks. Text retrieval is evaluated using MMTEB, while visual document retrieval is further assessed on MMEB-v2, JinaVDR, and ViDoRe v3. To ensure a fair comparison, we use Qwen3-VL-Embedding-2B to retrieve the top 100 candidates before applying the reranking models for refinement. Our results demonstrate that all three Qwen3-VL-Reranker models consistently outperform the base embedding model and baseline rerankers, with the 8B variant achieving the best performance across most tasks.

Table 4: Performance on MTEB Multilingual (Enevoldsen et al., 2025a). For compared models, the scores are retrieved from MTEB online leaderboard on December 25th, 2025.  

<table><tr><td>Model</td><td>Size</td><td>Mean (Task)</td><td>Mean (Type)</td><td>Bitext Mining</td><td>Class- ification</td><td>Clus- tering</td><td>Inst. Retrieval</td><td>Multilabel Class.</td><td>Pair Class.</td><td>Rerank</td><td>Retrieval</td><td>STS</td></tr><tr><td colspan="13">Open-Source Models</td></tr><tr><td>KaLM-Embedding-Gemma3-12B-2511 (Zhao et al., 2025)</td><td>12B</td><td>72.3</td><td>62.5</td><td>83.8</td><td>77.9</td><td>55.8</td><td>5.5</td><td>33.0</td><td>84.7</td><td>67.3</td><td>75.7</td><td>79.0</td></tr><tr><td>llama-embed-nemotron-8b (Babakhin et al., 2025)</td><td>8B</td><td>69.5</td><td>61.1</td><td>81.7</td><td>73.2</td><td>54.4</td><td>10.8</td><td>29.9</td><td>84.0</td><td>67.8</td><td>68.7</td><td>79.4</td></tr><tr><td>NV-Embed-v2 Lee et al. (2024)</td><td>7B</td><td>56.3</td><td>49.6</td><td>57.8</td><td>57.3</td><td>40.8</td><td>1.0</td><td>18.6</td><td>78.9</td><td>63.8</td><td>56.7</td><td>71.1</td></tr><tr><td>GritLM-7B (Muennighoff et al., 2024)</td><td>7B</td><td>60.9</td><td>53.7</td><td>70.5</td><td>61.8</td><td>49.8</td><td>3.5</td><td>22.8</td><td>80.9</td><td>63.8</td><td>58.3</td><td>73.3</td></tr><tr><td>BGE-M3 (Chen et al., 2024)</td><td>0.6B</td><td>59.6</td><td>52.2</td><td>79.1</td><td>60.4</td><td>40.9</td><td>-3.1</td><td>20.1</td><td>80.8</td><td>62.8</td><td>54.6</td><td>74.1</td></tr><tr><td>multilingual-e5-large-instruct (Wang et al., 2024a)</td><td>0.6B</td><td>63.2</td><td>55.1</td><td>80.1</td><td>64.9</td><td>50.8</td><td>-0.4</td><td>22.9</td><td>80.9</td><td>62.6</td><td>57.1</td><td>76.8</td></tr><tr><td>gte-Qwen2-1.5B-instruct (Li et al., 2023)</td><td>1.5B</td><td>59.5</td><td>52.7</td><td>62.5</td><td>58.3</td><td>52.1</td><td>0.74</td><td>24.0</td><td>81.6</td><td>62.6</td><td>60.8</td><td>71.6</td></tr><tr><td>gte-Qwen2-7b-instruct (Li et al., 2023)</td><td>7B</td><td>62.5</td><td>55.9</td><td>73.9</td><td>61.6</td><td>52.8</td><td>4.9</td><td>25.5</td><td>85.1</td><td>65.6</td><td>60.1</td><td>74.0</td></tr><tr><td>Qwen3-Embedding-0.6B (Zhang et al., 2025c)</td><td>0.6B</td><td>64.3</td><td>56.0</td><td>72.2</td><td>66.8</td><td>52.3</td><td>5.1</td><td>24.6</td><td>80.8</td><td>61.4</td><td>64.6</td><td>76.2</td></tr><tr><td>Qwen3-Embedding-4B (Zhang et al., 2025c)</td><td>4B</td><td>69.5</td><td>60.9</td><td>79.4</td><td>72.3</td><td>57.2</td><td>11.6</td><td>26.8</td><td>85.1</td><td>65.1</td><td>69.6</td><td>80.9</td></tr><tr><td>Qwen3-Embedding-8B (Zhang et al., 2025c)</td><td>8B</td><td>70.6</td><td>61.7</td><td>80.9</td><td>74.0</td><td>57.7</td><td>10.1</td><td>28.7</td><td>86.4</td><td>65.6</td><td>70.9</td><td>81.1</td></tr><tr><td colspan="13">Closed-Source Models</td></tr><tr><td>text-embedding-3-large†</td><td>-</td><td>58.9</td><td>51.4</td><td>62.2</td><td>60.3</td><td>46.9</td><td>-2.7</td><td>22.0</td><td>79.2</td><td>63.9</td><td>59.3</td><td>71.7</td></tr><tr><td>Cohere-embed-multilingual-v3.0†</td><td>-</td><td>61.1</td><td>53.2</td><td>70.5</td><td>63.0</td><td>46.9</td><td>-1.9</td><td>22.7</td><td>79.9</td><td>64.1</td><td>59.2</td><td>74.8</td></tr><tr><td>Gemini Embedding (Lee et al., 2025)</td><td>-</td><td>68.4</td><td>59.6</td><td>79.3</td><td>71.8</td><td>54.6</td><td>5.2</td><td>29.2</td><td>83.6</td><td>65.6</td><td>67.7</td><td>79.4</td></tr><tr><td>Seed-1.6-embedding-1215†</td><td>-</td><td>70.3</td><td>61.3</td><td>78.7</td><td>76.8</td><td>56.8</td><td>-0.0</td><td>46.2</td><td>85.5</td><td>66.2</td><td>66.1</td><td>75.9</td></tr><tr><td colspan="13">Qwen3 VL Embedding Models</td></tr><tr><td>Qwen3-VL-Embeddnig-2B</td><td>2B</td><td>63.9</td><td>55.8</td><td>69.5</td><td>65.9</td><td>52.5</td><td>3.9</td><td>26.1</td><td>78.5</td><td>64.8</td><td>67.1</td><td>74.3</td></tr><tr><td>Qwen3-VL-Embeddnig-8B</td><td>8B</td><td>67.9</td><td>58.9</td><td>77.5</td><td>72.0</td><td>55.8</td><td>4.5</td><td>28.6</td><td>81.1</td><td>65.7</td><td>69.4</td><td>75.4</td></tr></table>

Table 5: Evaluation results for reranking models and baselines. All scores are obtained from our experimental runs.  

<table><tr><td rowspan="2">Model</td><td rowspan="2">Size</td><td colspan="4">MMEB-v2(Retrieval)</td><td rowspan="2">MMTEB(Retrieval)</td><td rowspan="2">JinaVDR</td><td rowspan="2">ViDoRe(v3)</td></tr><tr><td>Avg</td><td>Image</td><td>Video</td><td>VisDoc</td></tr><tr><td>Qwen3-VL-Embedding-2B</td><td>2B</td><td>73.4</td><td>74.8</td><td>53.6</td><td>79.2</td><td>68.1</td><td>71.0</td><td>52.9</td></tr><tr><td>jina-reranker-m0†</td><td>2B</td><td>-</td><td>68.2</td><td>-</td><td>85.2</td><td>-</td><td>82.2</td><td>57.8</td></tr><tr><td>Qwen3-VL-Reranker-2B</td><td>2B</td><td>75.1</td><td>73.8</td><td>52.1</td><td>83.4</td><td>70.0</td><td>80.9</td><td>60.8</td></tr><tr><td>Qwen3-VL-Reranker-8B</td><td>8B</td><td>79.2</td><td>80.7</td><td>55.8</td><td>86.3</td><td>74.9</td><td>83.6</td><td>66.7</td></tr></table>

# 7 Analysis

# 7.1 Efficacy of Matryoshka Representation Learning and Embedding Quantization

![](images/a506ce8e3fb22a1a5e2faeeb20e92d8c5c22ada9002ad38f2578dad2eecbdcce.jpg)  
Figure 6: Performance analysis of different embedding dimensions and embedding quantization on MSMARCO Passage Dataset (text to text retrieval) and VL3-Syn Dataset (text to image retrieval).

Embedding models are foundational to modern retrieval systems, spanning both unimodal tasks (e.g., text retrieval) and cross-modal scenarios (e.g., text to image retrieval). In large-scale production environments, the corpus size often reaches millions or even billions of entries. Consequently, optimizing storage requirements for the corpus while enhancing computational efficiency by reducing retrieval latency is a critical challenge. The Qwen3-VL-Embedding series addresses these needs by integrating Matryoshka Representation Learning (MRL) and Quantization-Aware Training (QAT) into its training pipeline.

To evaluate the practical impact of these strategies on retrieval performance, we conduct benchmarks

Table 6: Performance of Qwen3-VL-Embedding-2B across different training stages on the MMEB-V2.  

<table><tr><td rowspan="2">Model Stage</td><td colspan="5">Image</td><td colspan="5">Video</td><td colspan="5">VisDoc</td><td rowspan="2">All</td></tr><tr><td>CLS</td><td>QA</td><td>RET</td><td>GD</td><td>Overall</td><td>CLS</td><td>QA</td><td>RET</td><td>MRET</td><td>Overall</td><td>VDRv1</td><td>VDRv2</td><td>VR</td><td>OOD</td><td>Overall</td></tr><tr><td>s0</td><td>62.2</td><td>63.7</td><td>65.9</td><td>80.0</td><td>65.8</td><td>60.8</td><td>65.9</td><td>51.1</td><td>48.4</td><td>57.5</td><td>76.7</td><td>59.8</td><td>79.5</td><td>64.3</td><td>74.8</td><td>66.6</td></tr><tr><td>s1</td><td>71.2</td><td>75.8</td><td>72.4</td><td>88.3</td><td>74.8</td><td>73.0</td><td>67.7</td><td>51.3</td><td>41.6</td><td>60.3</td><td>83.5</td><td>58.8</td><td>84.9</td><td>66.4</td><td>77.1</td><td>72.1</td></tr><tr><td>s2</td><td>61.8</td><td>69.8</td><td>78.8</td><td>76.3</td><td>71.3</td><td>63.9</td><td>60.0</td><td>55.6</td><td>57.8</td><td>59.5</td><td>84.2</td><td>72.4</td><td>87.9</td><td>70.6</td><td>80.9</td><td>71.5</td></tr><tr><td>s3</td><td>70.3</td><td>74.3</td><td>74.8</td><td>88.5</td><td>75.0</td><td>71.9</td><td>64.9</td><td>53.9</td><td>53.3</td><td>61.9</td><td>84.4</td><td>65.3</td><td>86.4</td><td>69.4</td><td>79.2</td><td>73.2</td></tr></table>

across two representative tasks. The first is a text retrieval task utilizing the MSMARCO Passage Ranking dataset (Bajaj et al., 2016), where we sample 10,000 queries and use all passages from the training dataset as our test corpus. The second is a cross-modal text to image retrieval task based on the VL3-Syn (Zhang et al., 2025a) dataset, featuring 10,000 captions as queries and a corpus of 2,000,000 images. We adopt the Qwen3-VL-Embedding-2B model for experimentation and utilize MRR@10 as our primary evaluation metric. Furthermore, we provide a comprehensive analysis of index storage overhead and retrieval latency across varying embedding dimensions and quantization schemes to demonstrate the tradeoffs between accuracy and efficiency.

As illustrated in Figure 6, we observe consistent patterns in both text retrieval and text to image cross-modal retrieval. Regarding embedding dimensionality, retrieval performance degrades as dimensions decrease; however, within a reasonable range, this degradation is acceptable given the substantial savings in storage and retrieval latency. For instance, in text retrieval tasks, reducing the embedding dimension from 1024 to 512 results in only a  $1.4\%$  decrease in retrieval performance while achieving  $50\%$  storage reduction and doubling retrieval speed. Regarding embedding quantization, we find that int8 quantization preserves retrieval performance with negligible degradation, whereas binary quantization significantly impairs retrieval effectiveness. Moreover, this performance loss becomes increasingly pronounced as embedding dimensionality decreases.

# 7.2 Impact of Spatial and Temporal Granularity

![](images/261cff043dfdcd181e960a2e496aeb3bba9d9bedeb537c0a93ef770d9e33c88a.jpg)  
Figure 7: Impact of visual granularity on model performance across different domains.

![](images/0a6a07cdebf8adc5b7591b901fc5f402e1c8e84a8df93e88472c515680d2ed65.jpg)

![](images/040df98abc604307b9bbc4ab0d20111d5014f22bcd3ee28a61f60523fdc78360.jpg)

![](images/304e38ba2c578e19e2fcae7733ab1426db6989ab2ad61e57e0e68f4a72d08ab6.jpg)

In this section, we investigate how model performance scales with visual granularity across different dimensions. Specifically, for the image modality, we examine the impact of spatial resolution as measured by the number of visual tokens. For video, we decouple our analysis into two axes: (i) temporal granularity, measured by the number of frames, and (ii) spatial resolution, quantified by the aggregate token budget across all frames.

We first analyzed the distribution of image/video resolutions and frame counts across the MMEB-v2 benchmarks, selecting several high-resolution tasks from the Image, Video, and Visual Document domains for our experiments. The results are illustrated in Figure 7. Our findings indicate a consistent trend where performance improves with increased resource consumption across all task categories. However, we observe a pronounced diminishing return as resource allocation grows, with a slight performance regression occurring at the highest levels of consumption. A potential explanation for this decline is the inherent performance degradation that the model encounters when processing excessively long contexts.

# 7.3 Performance Across Training Stages

In our multi-stage training pipeline, a total of four embedding models were produced. Table 6 details the performance of these four models at the 2B size. The results indicate that by distilling from a reranking model, the embedding model achieves a substantial performance boost in retrieval-oriented tasks.

Although a slight decline is observed in other task categories during this process, the final model merging stage successfully reconciles these trade-offs, leading to a robust and superior overall performance across all benchmarks.

# 8 Conclusion

In this work, we present Qwen3-VL-Embedding and Qwen3-VL-Reranker, a state-of-the-art model series for multimodal retrieval. By integrating a multi-stage training pipeline with high-quality multimodal data while maximally leveraging the multimodal knowledge and general understanding capabilities of Qwen3-VL Foundation models, Qwen3-VL-Embedding and Qwen3-VL-Reranker model series achieve unprecedented performance across a broad spectrum of multimodal retrieval benchmarks while maintaining strong pure-text capabilities. Furthermore, through matryoshka representation learning and quantization-aware training, the Qwen3-VL-Embedding series offers excellent practical deployment characteristics, significantly reducing computational costs for downstream tasks while preserving superior performance. Looking forward, promising directions include extending support to additional modalities, developing more efficient training paradigms, enhancing compositional reasoning capabilities, and establishing more comprehensive evaluation protocols. We believe these models represent a significant advancement in multimodal retrieval technology and hope they will facilitate further innovation in this rapidly evolving field.

# References

Yauhen Babakhin, Radek Osmulski, Ronay Ak, Gabriel Moreira, Mengyao Xu, Benedikt Schifferer, Bo Liu, and Even Oldridge. Llama-embed-nemotron-8b: A universal text embedding model for multilingual and cross-lingual tasks, 2025. URL https://arxiv.org/abs/2511.07025.  
Shuai Bai, Yuxuan Cai, Ruizhe Chen, Keqin Chen, Xionghui Chen, Zesen Cheng, Lianghao Deng, Wei Ding, Chang Gao, Chunjiang Ge, Wenbin Ge, Zhifang Guo, Qidong Huang, Jie Huang, Fei Huang, Binyuan Hui, Shutong Jiang, Zhaohai Li, Mingsheng Li, Mei Li, Kaixin Li, Zicheng Lin, Junyang Lin, Xuejing Liu, Jiawei Liu, Chenglong Liu, Yang Liu, Dayiheng Liu, Shixuan Liu, Dunjie Lu, Ruilin Luo, Chenxu Lv, Rui Men, Lingchen Meng, Xuancheng Ren, Xingzhang Ren, Sibo Song, Yuchong Sun, Jun Tang, Jianhong Tu, Jianqiang Wan, Peng Wang, Pengfei Wang, Qiuyue Wang, Yuxuan Wang, Tianbao Xie, Yiheng Xu, Haiyang Xu, Jin Xu, Zhibo Yang, Mingkun Yang, Jianxin Yang, An Yang, Bowen Yu, Fei Zhang, Hang Zhang, Xi Zhang, Bo Zheng, Humen Zhong, Jingren Zhou, Fan Zhou, Jing Zhou, Yuanzhi Zhu, and Ke Zhu. Qwen3-vl technical report. arXiv preprint arXiv:2511.21631, 2025.  
Payal Bajaj, Daniel Campos, Nick Craswell, Li Deng, Jianfeng Gao, Xiaodong Liu, Rangan Majumder, Andrew McNamara, Bhaskar Mitra, Tri Nguyen, et al. Ms marco: A human generated machine reading comprehension dataset. arXiv preprint arXiv:1611.09268, 2016.  
Yoshua Bengio, Nicholas Léonard, and Aaron Courville. Estimating or propagating gradients through stochastic neurons for conditional computation. arXiv preprint arXiv:1308.3432, 2013.  
Jianlyu Chen, Shitao Xiao, Peitian Zhang, Kun Luo, Defu Lian, and Zheng Liu. M3-embedding: Multi-linguality, multi-functionality, multi-granularity text embeddings through self-knowledge distillation. In Lun-Wei Ku, Andre Martins, and Vivek Srikumar (eds.), Findings of the Association for Computational Linguistics: ACL 2024, pp. 2318-2335, Bangkok, Thailand, August 2024. Association for Computational Linguistics. doi: 10.18653/v1/2024-findings-acl.137. URL https://aclanthology.org/2024-findings-acl.137/.  
Ziqi Dai, Xin Zhang, Mingxin Li, Yanzhao Zhang, Dingkun Long, Pengjun Xie, Meishan Zhang, Wenjie Li, and Min Zhang. Supervised fine-tuning or contrastive learning? towards better multimodal llm reranking. arXiv preprint arXiv:2510.14824, 2025.  
Kenneth Enevoldsen, Isaac Chung, Imene Kerboua, Marton Kardos, Ashwin Mathur, David Stap, Jay Gala, Wissam Siblini, Dominik Krzeminski, Genta Indra Winata, et al. Mmteb: Massive multilingual text embedding benchmark. In International Conference on Learning Representations. International Conference on Learning Representations, 2025a.  
Kenneth Enevoldsen, Isaac Chung, Imene Kerboua, Marton Kardos, Ashwin Mathur, David Stap, Jay Gala, Wissam Siblini, Dominik Krzeminski, Genta Indra Winata, Saba Sturua, Saiteja Utpala, Mathieu Ciancone, Marion Schaeffer, Gabriel Sequeira, Diganta Misra, Shreeya Dhakal, Jonathan Rystrom, Roman Solomatin, Omer Cagatan, Akash Kundu, Martin Bernstorff, Shitao Xiao, Akshitta Sukhlecha,

Bhavish Pahwa, Rafał Poswiata, Kranthi Kiran GV, Shawon Ashraf, Daniel Auras, Björn Plüster, Jan Philipp Harries, Loic Magne, Isabelle Mohr, Mariya Hendriksen, Dawei Zhu, Hippolyte Gisserot-Boukhlef, Tom Aarsen, Jan Kostkan, Konrad Wojtasik, Taemin Lee, Marek Šuppa, Crystina Zhang, Roberta Rocca, Mohammed Hamdy, Andrianos Michail, John Yang, Manuel Faysse, Aleksei Vatolin, Nandan Thakur, Manan Dey, Dipam Vasani, Pranjal Chitale, Simone Tedeschi, Nguyen Tai, Artem Snegirev, Michael Günther, Mengzhou Xia, Weijia Shi, Xing Han Lu, Jordan Clive, Gayatri Krishnakumar, Anna Maksimova, Silvan Wehrli, Maria Tikhonova, Henil Panchal, Aleksandr Abramov, Malte Ostendorff, Zheng Liu, Simon Clematide, Lester James Miranda, Alena Fenogenova, Guangyu Song, Ruqiya Bin Safi, Wen-Ding Li, Alessia Borghini, Federico Cassano, Hongjin Su, Jimmy Lin, Howard Yen, Lasse Hansen, Sara Hooker, Chenghao Xiao, Vaibhav Adlakha, Orion Weller, Siva Reddy, and Niklas Muennighoff. Mmteb: Massive multilingual text embedding benchmark, 2025b. URL https://arxiv.org/abs/2502.13595.  
Steven K Esser, Jeffrey L McKinstry, Deepika Bablani, Rathinakumar Appuswamy, and Dharmendra S Modha. Learned step size quantization. In International Conference on Learning Representations, 2020.  
Manuel Faysse, Hugues Sibille, Tony Wu, Bilel Omrani, Gautier Viaud, Céline Hudelot, and Pierre Colombo. Colpali: Efficient document retrieval with vision language models. In ICLR, 2025.  
Chenghan Fu, Daoze Zhang, Yukang Lin, Zhanheng Nie, Xiang Zhang, Jianyu Liu, Yueran Liu, Wanxian Guan, Pengjie Wang, Jian Xu, et al. Moon embedding: Multimodal representation learning for e-commerce search advertising. arXiv preprint arXiv:2511.11305, 2025.  
Yash Goyal, Tejas Khot, Douglas Summers-Stay, Dhruv Batra, and Devi Parikh. Making the v in vqa matter: Elevating the role of image understanding in visual question answering. In Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 6904-6913, 2017.  
Michael Günther, Saba Sturua, Mohammad Kalim Akram, Isabelle Mohr, Andrei Ungureanu, Sedigheh Eslami, Scott Martens, Bo Wang, Nan Wang, and Han Xiao. jina-embeddings-v4: Universal embeddings for multimodal multilingual retrieval, 2025. URL https://arxiv.org/abs/2506.18902.  
Edward J. Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yanzhi Li, Shean Wang, Lu Wang, and Weizhu Chen. Lora: Low-rank adaptation of large language models. In The Tenth International Conference on Learning Representations, ICLR 2022, Virtual Event, April 25-29, 2022. OpenReview.net, 2022. URL https://openreview.net/forum?id=nZeVKeeFYf9.  
Xiang Huang, Hao Peng, Dongcheng Zou, Zhiwei Liu, Jianxin Li, Kay Liu, Jia Wu, Jianlin Su, and Philip S. Yu. Cosent: Consistent sentence embedding via similarity ranking. IEEE/ACM Trans. Audio, Speech and Lang. Proc., 32:2800-2813, May 2024. ISSN 2329-9290. doi: 10.1109/TASLP.2024.3402087. URL https://doi.org/10.1109/TASLP.2024.3402087.  
Xin Huang and Kye Min Tan. Beyond text: Unlocking true multimodal, end-to-end rag with tomoro colqwen3, 2025. URL https://tomoro.ai/insights/beyond-text-unlocking-true-multimodal-end-to-end-rag-with-tomoro-colqwen3.  
Aaron Hurst, Adam Lerer, Adam P Goucher, Adam Perelman, Aditya Ramesh, Aidan Clark, AJ Ostrow, Akila Welihinda, Alan Hayes, Alec Radford, et al. Gpt-4o system card. arXiv preprint arXiv:2410.21276, 2024.  
Weijian Jian, Yajun Zhang, Dawei Liang, Chunyu Xie, Yixiao He, Dawei Leng, and Yuhui Yin. Rzenembed: Towards comprehensive multimodal retrieval. arXiv preprint arXiv:2510.27350, 2025.  
Ting Jiang, Minghui Song, Zihan Zhang, Haizhen Huang, Weiwei Deng, Feng Sun, Qi Zhang, Deqing Wang, and Fuzhen Zhuang. E5-v: Universal embeddings with multimodal large language models. arXiv preprint arXiv:2407.12580, 2024.  
Ziyan Jiang, Rui Meng, Xinyi Yang, Semih Yavuz, Yingbo Zhou, and Wenhu Chen. Vlm2vec: Training vision-language models for massive multimodal embedding tasks. In ICLR, 2025.  
Alex Krizhevsky, Geoffrey Hinton, et al. Learning multiple layers of features from tiny images. 2009.  
Aditya Kusupati, Gantavya Bhatt, Aniket Rege, Matthew Wallingford, Aditya Sinha, Vivek Ramanujan, William Howard-Snyder, Kaifeng Chen, Sham Kakade, Prateek Jain, et al. Matryoshka representation learning. Advances in Neural Information Processing Systems, 35:30233-30249, 2022.  
Chankyu Lee, Rajarshi Roy, Mengyao Xu, Jonathan Raiman, Mohammad Shoeybi, Bryan Catanzaro, and Wei Ping. Nv-embed: Improved techniques for training llms as generalist embedding models. arXiv preprint arXiv:2405.17428, 2024.

Jinhyuk Lee, Feiyang Chen, Sahil Dua, Daniel Cer, Madhuri Shanbhogue, Iftekhar Naim, Gustavo Hernández Abrego, Zhe Li, Kaifeng Chen, Henrique Schechter Vera, et al. Gemini embedding: Generalizable embeddings from gemini. arXiv preprint arXiv:2503.07891, 2025.  
Mingxin Li, Zhijie Nie, Yanzhao Zhang, Dingkun Long, Richong Zhang, and Pengjun Xie. Improving general text embedding model: Tackling task conflict and data imbalance through model merging. arXiv preprint arXiv:2410.15035, 2024.  
Zehan Li, Xin Zhang, Yanzhao Zhang, Dingkun Long, Pengjun Xie, and Meishan Zhang. Towards general text embeddings with multi-stage contrastive learning. arXiv preprint arXiv:2308.03281, 2023.  
Tsung-Yi Lin, Michael Maire, Serge Belongie, James Hays, Pietro Perona, Deva Ramanan, Piotr Dólár, and C Lawrence Zitnick. Microsoft coco: Common objects in context. In European conference on computer vision, pp. 740-755. Springer, 2014.  
Muhammad Arslan Manzoor, Sarah Albarri, Ziting Xian, Zaiqiao Meng, Preslav Nakov, and Shangsong Liang. Multimodality representation learning: A survey on evolution, pretraining and its applications. ACM Transactions on Multimedia Computing, Communications and Applications, 20(3):1-34, 2023.  
Lang Mei, Siyu Mo, Zhihan Yang, and Chong Chen. A survey of multimodal retrieval-augmented generation. arXiv preprint arXiv:2504.08748, 2025.  
Rui Meng, Ziyan Jiang, Ye Liu, Mingyi Su, Xinyi Yang, Yuepeng Fu, Can Qin, Zeyuan Chen, Ran Xu, Caiming Xiong, et al. Vlm2vec-v2: Advancing multimodal embedding for videos, images, and visual documents. arXiv preprint arXiv:2507.04590, 2025.  
Niklas Muennighoff, Hongjin Su, Liang Wang, Nan Yang, Furu Wei, Tao Yu, Amanpreet Singh, and Douwe Kiela. Generative representational instruction tuning, 2024.  
Aaron van den Oord, Yazhe Li, and Oriol Vinyals. Representation learning with contrastive predictive coding. arXiv preprint arXiv:1807.03748, 2018.  
Alec Radford, Jong Wook Kim, Chris Hallacy, Aditya Ramesh, Gabriel Goh, Sandhini Agarwal, Girish Sastry, Amanda Askell, Pamela Mishkin, Jack Clark, et al. Learning transferable visual models from natural language supervision. In International conference on machine learning, pp. 8748-8763. PmLR, 2021.  
Pranav Rajpurkar, Jian Zhang, Konstantin Lopyrev, and Percy Liang. Squad: 100,000+ questions for machine comprehension of text. arXiv preprint arXiv:1606.05250, 2016.  
Joshua Robinson, Ching-Yao Chuang, Suvrit Sra, and Stefanie Jegelka. Contrastive learning with hard negative samples. In International Conference on Learning Representations (ICLR), 2021.  
Khurram Soomro, Amir Roshan Zamir, and Mubarak Shah. Ucf101: A dataset of 101 human actions classes from videos in the wild. arXiv preprint arXiv:1212.0402, 2012.  
Nomic Team. Nomic embed multimodal: Interleaved text, image, and screenshots for visual document retrieval, 2025. URL https://nomic.ai/blog/posts/nomic-embed-multimodal.  
Liang Wang, Nan Yang, Xiaolong Huang, Binxing Jiao, Linjun Yang, Daxin Jiang, Rangan Majumder, and Furu Wei. Text embeddings by weakly-supervised contrastive pre-training. arXiv preprint arXiv:2212.03533, 2022.  
Liang Wang, Nan Yang, Xiaolong Huang, Linjun Yang, Rangan Majumder, and Furu Wei. Multilingual e5 text embeddings: A technical report. arXiv preprint arXiv:2402.05672, 2024a.  
Peng Wang, Shuai Bai, Sinan Tan, Shijie Wang, Zhihao Fan, Jinze Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin Ge, et al. Qwen2-vl: Enhancing vision-language model's perception of the world at any resolution. arXiv preprint arXiv:2409.12191, 2024b.  
Junbin Xiao, Xindi Shang, Angela Yao, and Tat-Seng Chua. Next-qa: Next phase of question-answering to explaining temporal actions. In Proceedings of the IEEE/CVF conference on computer vision and pattern recognition, pp. 9777-9786, 2021.  
Jun Xu, Tao Mei, Ting Yao, and Yong Rui. Msr-vtt: A large video description dataset for bridging video and language. In Proceedings of the IEEE conference on computer vision and pattern recognition, pp. 5288-5296, 2016.

Mengyao Xu, Gabriel Moreira, Ronay Ak, Radek Osmulski, Yauhen Babakhin, Zhiding Yu, Benedikt Schifferer, and Even Oldridge. Llama nemoretriever colembed: Top-performing text-image retrieval model, 2025. URL https://arxiv.org/abs/2507.05513.  
Boqiang Zhang, Kehan Li, Zesen Cheng, Zhiqiang Hu, Yuqian Yuan, Guanzheng Chen, Sicong Leng, Yuming Jiang, Hang Zhang, Xin Li, et al. Videollama 3: Frontier multimodal foundation models for image and video understanding. arXiv preprint arXiv:2501.13106, 2025a.  
Xiang Zhang, Junbo Zhao, and Yann LeCun. Character-level convolutional networks for text classification. Advances in neural information processing systems, 28, 2015.  
Xin Zhang, Yanzhao Zhang, Wen Xie, Mingxin Li, Ziqi Dai, Dingkun Long, Pengjun Xie, Meishan Zhang, Wenjie Li, and Min Zhang. Bridging modalities: Improving universal multimodal retrieval by multimodal large language models. In Proceedings of the Computer Vision and Pattern Recognition Conference, pp. 9274-9285, 2025b.  
Yanzhao Zhang, Mingxin Li, Dingkun Long, Xin Zhang, Huan Lin, Baosong Yang, Pengjun Xie, An Yang, Dayiheng Liu, Junyang Lin, Fei Huang, and Jingren Zhou. Qwen3 embedding: Advancing text embedding and reranking through foundation models. arXiv preprint arXiv:2506.05176, 2025c.  
Xinping Zhao, Xinshuo Hu, Zifei Shan, Shouzheng Huang, Yao Zhou, Xin Zhang, Zetian Sun, Zhenyu Liu, Dongfang Li, Xinyuan Wei, Youcheng Pan, Yang Xiang, Meishan Zhang, Haofen Wang, Jun Yu, Baotian Hu, and Min Zhang. Kalm-embedding-v2: Superior training techniques and data inspire a versatile embedding model, 2025. URL https://arxiv.org/abs/2506.20923.  
Junjie Zhou, Yongping Xiong, Zheng Liu, Ze Liu, Shitao Xiao, Yueze Wang, Bo Zhao, Chen Jason Zhang, and Defu Lian. Megapairs: Massive data synthesis for universal multimodal retrieval. In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pp. 19076-19095, 2025.

# A Dataset Examples

Table 7: Dataset format examples: Docmatix  ${}^{ \dagger  }$  and MS-COCO (Lin et al.,2014).  

<table><tr><td>Dataset</td><td>Docmatix</td></tr><tr><td>Instruction</td><td>Find a screenshot that relevant to the user&#x27;s question.</td></tr><tr><td colspan="2">Queries (Qi)</td></tr><tr><td>q_01</td><td>What type of research project was announced by the Danish Cancer Society on 01/02/21?</td></tr><tr><td colspan="2">Corpus (Ci)</td></tr><tr><td>d_01</td><td></td></tr><tr><td>d_02</td><td></td></tr><tr><td>d_03</td><td></td></tr><tr><td>Relevance (Ri)</td><td>{q_01: pos: [d_01], neg: [d_02, d_03]};</td></tr><tr><td>Dataset</td><td>MS-COCO</td></tr><tr><td>Instruction</td><td>Find an image caption describing the following everyday image.</td></tr><tr><td colspan="2">Queries (Qi)</td></tr><tr><td>q_01</td><td></td></tr><tr><td colspan="2">Corpus (Ci)</td></tr><tr><td>d_01</td><td>A man swinging a baseball bat on a baseball field.</td></tr><tr><td>d_02</td><td>The man is walking on the field to play a game of baseball.</td></tr><tr><td>d_03</td><td>A boy playing baseball waiting for a pitch.</td></tr><tr><td>Relevance (Ri)</td><td>{q_01: pos: [d_01], neg: [d_02, d_03]};</td></tr></table>

# B Examples of Data Synthesis Prompts

# Image Question Answering Prompt

You are given an image. Your job is to create ONE high-quality multimodal training  $\rightarrow$  example for an Image Question Answering (IQA) dataset. The final answer MUST be a single JSON object and nothing else.

STEP 1 - Visual Description (less or equal than 500 {language} words)

- General scene summary and object-level details (attributes, positions, relations).  
- Contextual features (environment, lighting, actions).  
- Brainstorm the types of reasoning enabled (e.g., spatial, comparative, predictive).

STEP 2 - Task Selection

Choose ONE task type from the list below that best fits the image content:  
- Factoid Identification: Questions about specific entities, brands, or basic facts  $\leftrightarrow$  (e.g., "What brand is the watch?").  
- Visual Reasoning: Questions requiring logical inference or analysis (e.g., "How many rats were fed the control diet?").  
- OCR-based Data Extraction: Questions targeting text, tables, or document info (e.g.,  $\leftrightarrow$  "Who is the author of the book?").  
- Domain-specific Knowledge Inquiry: Questions requiring specialized background  $\rightarrow$  knowledge (e.g., "What style of architecture is this?").

STEP 3 - Populate the Example

```txt
Fill every key below using double quotes. Do not add extra keys.   
{ "description": "<STEP 1 output>", "task_type": "<Task selected in STEP 2>", "question": "<A visually grounded question in {language}>", "positive_answer": "<Concise, correct answer in {language}>", "hard_negative_answer": "<A plausible but deceptive incorrect answer in {language}>"   
}
```

Hard Constraints:

- "task_type" must be exactly chosen from the list in STEP 2.  
- Ensure the question is directly answerable from the visual or embedded textual  
$\leftrightarrow$  content.  
- Output ONLY the JSON object.

# Video Classification Prompt

You are given a video. Your job is to create ONE high-quality multimodal training  $\leftrightarrow$  example for a video classification dataset.

The final answer MUST be a single JSON object and nothing else.

STEP 1 - Visual Analysis (less or equal than 300 {language} words)

- General overview of the video content.  
- Identify primary actions, environmental settings, and the overall event type.  
- Brainstorm potential ways this video could support the classification tasks listed in  $\rightarrow$  STEP 2.

STEP 2 - Task Selection

Choose ONE task type from the list below that best fits the video:

- Activity Recognition: Identifying the main activity or action being performed.  
- Scene Parsing: Determining the primary environment or setting of the video.  
- Event Categorization: Classifying the video into a specific event type or intended  $\leftrightarrow$  purpose.  
- Sentiment/Intent Analysis: Recognizing the dominant emotional tone or the sentiment  $\leftrightarrow$  expressed.

STEP 3 - Populate the Example

Fill every key below using double quotes. Do not add extra keys.

```txt
{ "description": "<STEP 1 output>", "task_type": "<Task Selected in STEP 2>", "label": "<Correct label in {language}>",
```

"misleading_label": "<Plausible but incorrect label in {language} for hard negative  $\rightarrow$  mining>"

}

Hard Constraints:

- "task_type" must be exactly chosen from the list in STEP 2.  
- "description", "label", and "misleading_label" must be in {language}.  
- Output ONLY the JSON object-no extra text or explanations.

# C Model Applications and Examples

In this section, we present several real-world application scenarios to demonstrate the practical utility of Qwen3-VL-Embedding. The showcases in Table Tables 8 to 11 illustrate how the model handles diverse queries and complex visual data, providing a clearer understanding of its integration into downstream tasks.

Table 8: Similarity scores evaluated by Qwen3-VL-Embedding (text tasks).  

<table><tr><td>Task</td><td>AG News (Zhang et al., 2015)</td><td></td><td></td></tr><tr><td>Instruction</td><td>Classify the news article.</td><td></td><td></td></tr><tr><td>Ex.</td><td>Query</td><td>Document</td><td>Sim.</td></tr><tr><td>1</td><td>Text: Fears for T N pension after talks Unions representing workers at Turner Newall say they are &#x27;disappointed&#x27; after talks with stricken par-ent firm Federal Mogul.</td><td>Text: Business</td><td>0.55</td></tr><tr><td>2</td><td>Text: US fighter squadron to be deployed in South Korea next month (AFP) AFP - A squadron of US Air Force F-15E fighters based in Alaska will fly to South Korea next month for temporary deployment aimed at enhancing US firepower on the Korean peninsula...</td><td>Text: World</td><td>0.57</td></tr><tr><td>Task</td><td>SQuAD (Rajpurkar et al., 2016)</td><td></td><td></td></tr><tr><td>Instruction</td><td>Retrieve passages that answer this question.</td><td></td><td></td></tr><tr><td>Ex.</td><td>Query</td><td>Document</td><td>Sim.</td></tr><tr><td>1</td><td>Text: Which NFL team represented the AFC at Super Bowl 50?</td><td>Text: Super Bowl 50 was an American football game to determine the champion of the National Football League (NFL) for the 2015 season. The American Football Conference (AFC) champion Denver Broncos defeated...</td><td>0.81</td></tr><tr><td>2</td><td>Text: Who headlined the halftime show for Super Bowl 50?</td><td>Text: CBS broadcast Super Bowl 50 in the U.S., and charged an average of $5 million for a 30-second commercial during the game. The Super Bowl 50 halftime show was headlined by the British rock group Coldpl...</td><td>0.75</td></tr><tr><td>Task</td><td>MS MARCO (Lin et al., 2014)</td><td></td><td></td></tr><tr><td>Instruction</td><td>Retrieve relevant passages.</td><td></td><td></td></tr><tr><td>Ex.</td><td>Query</td><td>Document</td><td>Sim.</td></tr><tr><td>1</td><td>Text: walgreens store sales average</td><td>Text: The average Walgreens salary ranges from approximately $15,000 per year for Customer Service Associate / Cashier to $179,900 per year for District Manager. Average Walgreens hourly pay ranges from app...</td><td>0.77</td></tr><tr><td>2</td><td>Text: how much do bartenders make</td><td>Text: According to the Bureau of Labor Statistics, the average hourly wage for a bartender is 10.36, and the average yearly take – homeis21,550. Bartending can be a lot of things. For some it is exciting,...</td><td>0.81</td></tr></table>

Table 9: Similarity scores evaluated by Qwen3-VL-Embedding (image tasks).  

<table><tr><td>Task
Instruction</td><td colspan="3">CIFAR-10 (Krizhevsky et al., 2009)
Classify the object in this image.</td></tr><tr><td>Ex.</td><td>Query</td><td>Document</td><td>Sim.</td></tr><tr><td>1</td><td>Image:</td><td>Text: cat</td><td>0.67</td></tr><tr><td>2</td><td>Image:</td><td>Text: truck</td><td>0.69</td></tr><tr><td>Task</td><td rowspan="2" colspan="3">VQAv2 (Goyal et al., 2017)Find the answer to this question about the image.</td></tr><tr><td>Instruction</td></tr><tr><td>Ex.</td><td>Query</td><td>Document</td><td>Sim.</td></tr><tr><td>1</td><td>Text: Where is he looking?
Image:</td><td>Text: down</td><td>0.54</td></tr><tr><td>2</td><td>Text: What are the people in the background
doing?
Image:</td><td>Text: watching</td><td>0.67</td></tr><tr><td>Task</td><td rowspan="2" colspan="3">MS COCO (Lin et al., 2014)Find images matching this description.</td></tr><tr><td>Instruction</td></tr><tr><td>Ex.</td><td>Query</td><td>Document</td><td>Sim.</td></tr><tr><td>1</td><td>Text: A man with a red helmet on a small moped
on a dirt road.</td><td>Image:</td><td>0.52</td></tr><tr><td>2</td><td>Text: The bathroom is clean and ready to be
used.</td><td>Image:</td><td>0.46</td></tr></table>

Table 10: Similarity scores evaluated by Qwen3-VL-Embedding (video tasks).  

<table><tr><td>Task
Instruction</td><td colspan="3">UCF101 (Soomro et al., 2012)
Classify the action in this video.</td></tr><tr><td>Ex.</td><td>Query</td><td>Document</td><td>Sim.</td></tr><tr><td>1</td><td>Video:</td><td>Text: FloorGymnastics</td><td>0.66</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td>NExTQA (Xiao et al., 2021)
Instruction</td><td colspan="2">Find the answer to this question about the video.</td></tr><tr><td>Ex.</td><td>Query</td><td>Document</td><td>Sim.</td></tr><tr><td>1</td><td>Text: Why did the girl have painted nail polish on her nails... Video:</td><td>Text: (E) look nice</td><td>0.64</td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr></table>

Table 11: Similarity scores evaluated by Qwen3-VL-Embedding (visual document tasks).  

<table><tr><td>Task</td><td colspan="3">ViDoRe_ArxivQA (Faysse et al., 2025)</td></tr><tr><td>Instruction</td><td colspan="3">Find documents that answer this question.</td></tr><tr><td>Ex.</td><td>Query</td><td>Document</td><td>Sim.</td></tr><tr><td>1</td><td>Text: Based on the graph, what is the impact of correcting for fspec not equal to 1 on the surface density trend?</td><td>Image:</td><td>0.63</td></tr><tr><td></td><td></td><td>fspec=1
fspec≠1, w/o corr.
fspec≠1, with corr.</td><td></td></tr><tr><td></td><td></td><td>Surface Density log Σ/Σ Mpc
-1.50 -1.25 -1.00 -0.75 -0.50
Radius log Rp [h-1Mpc]</td><td></td></tr><tr><td>2</td><td>Text: Based on the progression from JUL10 to FEB11Q, what trend can be observed in the thread participation?</td><td>Image:</td><td>0.55</td></tr><tr><td></td><td></td><td>JUL10
PO
Tread ID
FEB11
Tread ID
FEB11Q</td><td></td></tr></table>