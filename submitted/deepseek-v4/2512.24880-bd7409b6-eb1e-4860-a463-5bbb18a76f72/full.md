# mHC: Manifold-Constrained Hyper-Connections

Zhenda Xie*†, Yixuan Wei*, Huanqi Cao*,

Chenggang Zhao, Chengqi Deng, Jiashi Li, Damai Dai, Huazuo Gao, Jiang Chang, Kuai Yu, Liang Zhao, Shangyan Zhou, Zhean Xu, Zhengyan Zhang, Wangding Zeng, Shengding Hu, Yuqing Wang, Jingyang Yuan, Lean Wang, Wenfeng Liang

# DeepSeek-AI

# Abstract

Recently, studies exemplified by Hyper-Connections (HC) have extended the ubiquitous residual connection paradigm established over the past decade by expanding the residual stream width and diversifying connectivity patterns. While yielding substantial performance gains, this diversification fundamentally compromises the identity mapping property intrinsic to the residual connection, which causes severe training instability and restricted scalability, and additionally incurs notable memory access overhead. To address these challenges, we propose Manifold-Constrained Hyper-Connections (mHC), a general framework that projects the residual connection space of HC onto a specific manifold to restore the identity mapping property, while incorporating rigorous infrastructure optimization to ensure efficiency. Empirical experiments demonstrate that mHC is effective for training at scale, offering tangible performance improvements and superior scalability. We anticipate that mHC, as a flexible and practical extension of HC, will contribute to a deeper understanding of topological architecture design and suggest promising directions for the evolution of foundational models.

![](images/925d5faaeb5c6499924e9fb8fc967a4af5b28fcf7e654fe60e380858bb010285.jpg)

![](images/808f5eefe31c474b7c31abc5c2d032964b2c4e4e3693bc09e5a30a765c6216d5.jpg)

![](images/991ab077b28f1a58cf390ab86fb4c19a51ef28af379f2c6340bc66946ccfa08e.jpg)  
Figure 1 | Illustrations of Residual Connection Paradigms. This figure compares the structural design of (a) standard Residual Connection, (b) Hyper-Connections (HC), and (c) our proposed Manifold-Constrained Hyper-Connections (mHC). Unlike the unconstrained HC, mHC focuses on optimizing the residual connection space by projecting the matrices onto a constrained manifold to ensure stability.

# Contents

# 1 Introduction 3

# 2 Related Works 4

2.1 Micro Design 4   
2.2 Macro Design 5

# 3 Preliminary 5

3.1 Numerical Instability . . 6   
3.2 System Overhead 7

# 4 Method 8

4.1 Manifold-Constrained Hyper-Connections 8   
4.2 Parameterization and Manifold Projection . . 9   
4.3 Efficient Infrastructure Design . . 9

4.3.1 Kernel Fusion 9   
4.3.2 Recomputing 10   
4.3.3 Overlapping Communication in DualPipe 11

# 5 Experiments 12

5.1 Experimental Setup . . 12   
5.2 Main Results . 12   
5.3 Scaling Experiments 13   
5.4 Stability Analysis . 14

# 6 Conclusion and Outlook 15

# A Appendix 19

A.1 Detailed Model Specifications and Hyper-parameters. . . 19

# 1. Introduction

Deep neural network architectures have undergone rapid evolution since the introduction of ResNets (He et al., 2016a). As illustrated in Fig. 1(a), the structure of a single-layer can be formulated as follows:

$$
\mathbf {x} _ {l + 1} = \mathbf {x} _ {l} + \mathcal {F} (\mathbf {x} _ {l}, \mathcal {W} _ {l}), \tag {1}
$$

where $\mathbf { x } _ { l }$ and $\mathbf { x } _ { l + 1 }$ denote the ??-dimensional input and output of the ??-th layer, respectively, and $\mathcal { F }$ represents the residual function. Although the residual function $\mathcal { F }$ has evolved over the past decade to include various operations such as convolution, attention mechanisms, and feed forward networks, the paradigm of the residual connection has maintained its original form. Accompanying the progression of Transformer (Vaswani et al., 2017) architecture, this paradigm has currently established itself as a fundamental design element in large language models (LLMs) (Brown et al., 2020; Liu et al., 2024b; Touvron et al., 2023).

This success is primarily attributed to the concise form of the residual connection. More importantly, early research (He et al., 2016b) revealed that the identity mapping property of the residual connection maintains stability and efficiency during large-scale training. By recursively extending the residual connection across multiple layers, Eq. (1) yields:

$$
\mathbf {x} _ {L} = \mathbf {x} _ {l} + \sum_ {i = l} ^ {L - 1} \mathcal {F} \left(\mathbf {x} _ {i}, \mathcal {W} _ {i}\right), \tag {2}
$$

where ?? and ?? correspond to deeper and shallower layers, respectively. The term identity mapping refers to the component $\mathbf { x } _ { l }$ itself, which emphasizes the property that the signal from the shallower layer maps directly to the deeper layer without any modification.

Recently, studies exemplified by Hyper-Connections (HC) (Zhu et al., 2024) have introduced a new dimension to the residual connection and empirically demonstrated its performance potential. The single-layer architecture of HC is illustrated in Fig. 1(b). By expanding the width of the residual stream and enhancing connection complexity, HC significantly increases topological complexity without altering the computational overhead of individual units regarding FLOPs. Formally, single-layer propagation in HC is defined as:

$$
\mathbf {x} _ {l + 1} = \mathcal {H} _ {l} ^ {\mathrm {r e s}} \mathbf {x} _ {l} + \mathcal {H} _ {l} ^ {\mathrm {p o s t} \top} \mathcal {F} (\mathcal {H} _ {l} ^ {\mathrm {p r e}} \mathbf {x} _ {l}, \mathcal {W} _ {l}), \tag {3}
$$

where $\mathbf { x } _ { l }$ and $\mathbf { x } _ { l + 1 }$ denote the input and output of the ??-th layer, respectively. Unlike the formulation in Eq. (1), the feature dimension of $\mathbf { x } _ { l }$ and $\mathbf { x } _ { l + 1 }$ is expanded from ?? to $n \times C ,$ , where ?? is the expansion rate. The term $\mathcal { H } _ { l } ^ { \mathrm { r e s } } \in \mathbb { R } ^ { n \times n }$ represents a learnable mapping that mixes features within the residual stream. Also as a learnable mapping, $\mathcal { H } _ { l } ^ { \mathrm { p r e } } \in \mathbb { R } ^ { 1 \times n }$ aggregates features from the ????-dim stream into a ??-dim layer input, and conversely, $\mathcal { H } _ { l } ^ { \mathrm { p o s t } } \in \mathbb { R } ^ { 1 \times n }$ maps the layer output back onto the stream.

However, as the training scale increases, HC introduces potential risks of instability. The primary concern is that the unconstrained nature of HC compromises the identity mapping property when the architecture extends across multiple layers. In architectures comprising multiple parallel streams, an ideal identity mapping serves as a conservation mechanism. It ensures that the average signal intensity across streams remains invariant during both forward and backward propagation. Recursively extending HC to multiple layers via Eq. (3) yields:

$$
\mathbf {x} _ {L} = \left(\prod_ {i = 1} ^ {L - l} \mathcal {H} _ {L - i} ^ {\text {r e s}}\right) \mathbf {x} _ {l} + \sum_ {i = l} ^ {L - 1} \left(\prod_ {j = 1} ^ {L - 1 - i} \mathcal {H} _ {L - j} ^ {\text {r e s}}\right) \mathcal {H} _ {i} ^ {\text {p o s t} \top} \mathcal {F} \left(\mathcal {H} _ {i} ^ {\text {p r e}} \mathbf {x} _ {i}, \mathcal {W} _ {i}\right), \tag {4}
$$

where $L$ and ?? represent a deeper layer and a shallower layer, respectively. In contrast to Eq. (2), the composite mapping $\Pi _ { i = 1 } ^ { L - l } \dot { \mathcal { H } } _ { L - i } ^ { \mathrm { r e s } }$ in HC fails to preserve the global mean of the features. This discrepancy leads to unbounded signal amplification or attenuation, resulting in instability during large-scale training. A further consideration is that, while HC preserves computational efficiency in terms of FLOPs, the hardware efficiency concerning memory access costs for the widened residual stream remains unaddressed in the original design. These factors collectively restrict the practical scalability of HC and hinder its application in large-scale training.

To address these challenges, we propose Manifold-Constrained Hyper-Connections (mHC), as shown in Fig. 1(c), a general framework that projects the residual connection space of HC onto a specific manifold to restore the identity mapping property, while incorporating rigorous infrastructure optimization to ensure efficiency. Specifically, mHC utilizes the Sinkhorn-Knopp algorithm (Sinkhorn and Knopp, 1967) to entropically project $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ onto the Birkhoff polytope. This operation effectively constrains the residual connection matrices within the manifold that is constituted by doubly stochastic matrices. Since the row and column sums of these matrices equal to 1, the operation $\mathcal { H } _ { l } ^ { \mathrm { r e s } } \mathbf { x } _ { l }$ functions as a convex combination of the input features. This characteristic facilitates a well-conditioned signal propagation where the feature mean is conserved, and the signal norm is strictly regularized, effectively mitigating the risk of vanishing or exploding signals. Furthermore, due to the closure of matrix multiplication for doubly stochastic matrices, the composite mapping $\Pi _ { i = 1 } ^ { L - l } \mathcal { H } _ { L - i } ^ { \mathrm { r e s } }$ retains this conservation property. Consequently, mHC effectively maintains the stability of identity mappings between arbitrary depths. To ensure efficiency, we employ kernel fusion and develop mixed precision kernels utilizing TileLang (Wang et al., 2025). Furthermore, we mitigate the memory footprint through selective recomputing and carefully overlap communication within the DualPipe schedule (Liu et al., 2024b).

Extensive experiments on language model pretraining demonstrate that mHC exhibits exceptional stability and scalability while maintaining the performance advantages of HC. Inhouse large-scale training indicates that mHC supports training at scale and introduces only a $6 . 7 \%$ additional time overhead when expansion rate $n = 4$ .

# 2. Related Works

Architectural advancements in deep learning can be primarily classified into micro-design and macro-design. Micro-design concerns the internal architecture of computational blocks, specifying how features are processed across spatial, temporal, and channel dimensions. In contrast, macro-design establishes the inter-block topological structure, thereby dictating how feature representations are propagated, routed, and merged across distinct layers.

# 2.1. Micro Design

Driven by parameter sharing and translation invariance, convolution initially dominated the processing of structured signals. While subsequent variations such as depthwise separable (Chollet, 2017) and grouped convolutions (Xie et al., 2017) optimized efficiency, the advent of Transformers (Vaswani et al., 2017) established Attention and Feed-Forward Networks (FFNs) as the fundamental building blocks of modern architecture. Attention mechanisms facilitate global information propagation, while FFNs enhance the representational capacity of individual features. To balance performance with the computational demands of LLMs, attention mechanisms have evolved towards efficient variants such as Multi-Query Attention (MQA) (Shazeer, 2019), Grouped-Query Attention (GQA) (Ainslie et al., 2023), and Multi-Head Latent Attention

(MLA) (Liu et al., 2024a). Simultaneously, FFNs have been generalized into sparse computing paradigms via Mixture-of-Experts (MoE) (Fedus et al., 2022; Lepikhin et al., 2020; Shazeer et al., 2017), allowing for massive parameter scaling without proportional computational costs.

# 2.2. Macro Design

Macro-design governs the global topology of the network (Srivastava et al., 2015). Following ResNet (He et al., 2016a), architectures such as DenseNet (Huang et al., 2017) and Fractal-Net (Larsson et al., 2016) aimed to enhance performance by increasing topological complexity through dense connectivity and multi-path structures, respectively. Deep Layer Aggregation (DLA) (Yu et al., 2018) further extended this paradigm by recursively aggregating features across various depths and resolutions.

More recently, the focus of macro-design has shifted toward expanding the width of the residual stream (Chai et al., 2020; Fang et al., 2023; Heddes et al., 2025; Mak and Flanigan, 2025; Menghani et al., 2025; Pagliardini et al., 2024; Xiao et al., 2025; Xie et al., 2023; Zhu et al., 2024). Hyper-Connections (HC) (Zhu et al., 2024) introduced learnable matrices to modulate connection strengths among features at varying depths, while the Residual Matrix Transformer (RMT) (Mak and Flanigan, 2025) replaced the standard residual stream with an outer-product memory matrix to facilitate feature storage. Similarly, MUDDFormer (Xiao et al., 2025) employs multiway dynamic dense connections to optimize cross-layer information flow. Despite their potential, these approaches compromise the inherent identity mapping property of the residual connection, thereby introducing instability and hindering scalability. Furthermore, they incur significant memory access overhead due to expanded feature widths. Building upon HC, the proposed mHC restricts the residual connection space onto a specific manifold to restore the identity mapping property, while also incorporating rigorous infrastructure optimizations to ensure efficiency. This approach enhances stability and scalability while maintaining the topological benefits of expanded connections.

# 3. Preliminary

We first establish the notation used in this work. In the HC formulation, the input to the ??-th layer, $\mathbf { x } _ { l } \in \mathbb { R } ^ { 1 \times C }$ , is expanded by a factor of $n$ to construct a hidden matrix $\begin{array} { r } { \mathbf { x } _ { l } = ( \mathbf { x } _ { l , 0 } ^ { \top } , \ldots , \mathbf { x } _ { l , n - 1 } ^ { \top } ) ^ { \top } \in \mathbb { R } ^ { n \times C } . } \end{array}$ which can be viewed as $n$ -stream residual. This operation effectively broadens the width of the residual stream. To govern the read-out, write-in, and updating processes of this stream, HC introduces three learnable linear mappings— $\mathcal { H } _ { l } ^ { \mathrm { p r e } } , \mathcal { H } _ { l } ^ { \mathrm { p o s } \bar { \mathrm { t } } } \in \mathbb { R } ^ { 1 \times \bar { n } } .$ , and $\mathcal { H } _ { l } ^ { \mathrm { r e s } } \in \mathbb { R } ^ { n \times n }$ . These mappings modify the standard residual connection shown in Eq. (1), resulting in the formulation given in Eq. (3).

In the HC formulation, learnable mappings are composed of two parts of coefficients: the input-dependent one and the global one, referred to as dynamic mappings and static mappings, respectively. Formally, HC computes the coefficients as follows:

$$
\left\{ \begin{array}{l} \tilde {\mathbf {x}} _ {l} = \operatorname {R M S N o r m} \left(\mathbf {x} _ {l}\right) \\ \mathcal {H} _ {l} ^ {\text {p r e}} = \alpha_ {l} ^ {\text {p r e}} \cdot \tanh  \left(\theta_ {l} ^ {\text {p r e}} \tilde {\mathbf {x}} _ {l} ^ {\top}\right) + \mathbf {b} _ {l} ^ {\text {p r e}} \\ \mathcal {H} _ {l} ^ {\text {p o s t}} = \alpha_ {l} ^ {\text {p o s t}} \cdot \tanh  \left(\theta_ {l} ^ {\text {p o s t}} \tilde {\mathbf {x}} _ {l} ^ {\top}\right) + \mathbf {b} _ {l} ^ {\text {p o s t}} \\ \mathcal {H} _ {l} ^ {\text {r e s}} = \alpha_ {l} ^ {\text {r e s}} \cdot \tanh  \left(\theta_ {l} ^ {\text {r e s}} \tilde {\mathbf {x}} _ {l} ^ {\top}\right) + \mathbf {b} _ {l} ^ {\text {r e s}}, \end{array} \right. \tag {5}
$$

where RMSNorm(·) (Zhang and Sennrich, 2019) is applied to the last dimension, and the scalars $\alpha _ { l } ^ { \mathrm { p r e } } , \alpha _ { l } ^ { \mathrm { p o s t } }$ and $\alpha _ { l } ^ { \mathrm { r e s } } \in \mathbb { R }$ are learnable gating factors initialized to small values. The dynamic

mappings are derived via linear projections parameterized by $\theta _ { l } ^ { \mathrm { { p r e } } } , \theta _ { l } ^ { \mathrm { { p o s t } } } \in \mathbb { R } ^ { 1 \times C }$ and $\theta _ { l } ^ { \mathrm { r e s } } \in \mathbb { R } ^ { n \times C } ,$ while the static mappings are represented by learnable biases $\mathbf { b } _ { l } ^ { \mathrm { p r e } } , \mathbf { b } _ { l } ^ { \mathrm { p o s t } } \in \mathbb { R } ^ { 1 \times n }$ and $\mathbf { b } _ { l } ^ { \mathrm { r e s } } \in \mathbb { R } ^ { n \times n }$

It is worth noting that the introduction of these mappings—H pre?? , $\mathcal { H } _ { l } ^ { \mathrm { p o s t } } .$ , and $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ —incurs negligible computational overhead, as the typical expansion rate $n$ , e.g. 4, is much smaller than the input dimension ??. With this design, HC effectively decouples the information capacity of the residual stream from the layer’s input dimension, which is strongly correlated with the model’s computational complexity (FLOPs). Consequently, HC offers a new avenue for scaling by adjusting the residual stream width, complementing the traditional scaling dimensions of model FLOPs and training data size discussed in pre-training scaling laws (Hoffmann et al., 2022).

Although HC necessitates three mappings to manage the dimensional mismatch between the residual stream and the layer input, preliminary experiments presented in Tab. 1 indicate that the residual mapping $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ yields the most significant performance gain. This finding underscores the critical importance of effective information exchange within the residual stream.

Table 1 | Ablation Study of HC Components. When a specific mapping $( \mathcal { H } _ { l } ^ { \mathrm { p r e } } , \mathcal { H } _ { l } ^ { \mathrm { p o s t } } ,$ , or $\mathcal { H } _ { l } ^ { \mathrm { r e s } } )$ ) is disabled, we employ a fixed mapping to maintain dimensional consistency: uniform weights of $1 / n$ for $\mathcal { H } _ { l } ^ { \mathrm { p r e } }$ , uniform weights of ones for $\mathcal { H } _ { l } ^ { \mathrm { p o s t } } .$ , and the identity matrix for $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ .   

<table><tr><td>Hlres</td><td>Hlpre</td><td>Hlpost</td><td>Absolute Loss Gap</td></tr><tr><td></td><td></td><td></td><td>0.0</td></tr><tr><td>✓</td><td></td><td></td><td>-0.022</td></tr><tr><td>✓</td><td>✓</td><td></td><td>-0.025</td></tr><tr><td>✓</td><td>✓</td><td>✓</td><td>-0.027</td></tr></table>

# 3.1. Numerical Instability

While the residual mapping $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ is instrumental for performance, its sequential application poses a significant risk to numerical stability. As detailed in Eq. (4), when HC is extended across multiple layers, the effective signal propagation from layer ?? to $L$ is governed by the composite mapping $\dot { \Pi } _ { i = 1 } ^ { L - l } \mathcal { H } _ { L - i } ^ { \mathrm { r e s } }$ . Since the learnable mapping $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ is unconstrained, this composite mapping inevitably deviates from the identity mapping. Consequently, the signal magnitude is prone to explosion or vanishing during both the forward pass and backpropagation. This phenomenon undermines the fundamental premise of residual learning, which relies on unimpeded signal flow, thereby destabilizing the training process in deeper or larger-scale models.

Empirical evidence supports this analysis. We observe unstable loss behavior in large-scale experiments, as illustrated in Fig. 2. Taking mHC as the baseline, HC exhibits an unexpected loss surge around the 12k step, which is highly correlated with the instability in the gradient norm. Furthermore, the analysis on $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ validates the mechanism of this instability. To quantify how the composite mapping $\Pi _ { i = 1 } ^ { L - l } \mathcal { H } _ { L - i } ^ { \mathrm { r e s } }$ amplifies signals along the residual stream, we utilize mapping, captures the worst-case expansion in the forward pass. The second, based on the maximum absolute column sum, corresponds to the backward pass. We refer to these metrics as the Amax Gain Magnitude of the composite mapping. As shown in Fig. 3 (b), the Amax Gain Magnitude yields extreme values with peaks of 3000, a stark divergence from 1 that confirms the presence of exploding residual streams.

![](images/61ff91dc512c2e6a8871d3593401d0c2fc3b1c5b06e8b1e65389d782da01746c.jpg)  
(a) Absolute Training Loss Gap vs: Training Steps

![](images/5d2ae68d0cb38beb4d66e991f5bf77e4a4fbe6765d65797ce26af365ae54e397.jpg)  
(b) Gradient Norm vs: Training Steps

![](images/98a3fee2a09b5ecd134af6c1c453116f8963cd2e6d3dc0ce11feb2007f129df6.jpg)  
Figure 2 | Training Instability of Hyper-Connections (HC). This figure illustrates (a) the absolute loss gap of HC relative to mHC, and (b) the comparisons of gradient norms. All results are based on 27B models.   
(a) Single-Layer Mapping

![](images/4be87886118ca80d45743ec7953ed34350b8dd9ad666172c688a56586a3cc177.jpg)  
(b) Composite Mapping   
Figure 3 | Propagation Instability of Hyper-Connections (HC). This figure illustrates the propagation dynamics of (a) the single-layer mapping $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ and (b) the composite mapping $\Pi _ { i = 1 } ^ { L - l } \mathcal { H } _ { L - i } ^ { \mathrm { r e s } }$ Î ??=1 within the 27B model. The layer index ?? (x-axis) unrolls each standard Transformer two independent layers (Attention and FFN). The Amax Gain Magnitude (y-axis) is calculated as the maximum absolute row sum (for the forward signal) and column sum (for the backward gradient), averaged over all tokens in a selected sequence.

# 3.2. System Overhead

While the computational complexity of HC remains manageable due to the linearity of the additional mappings, the system-level overhead prevents a non-negligible challenge. Specifically, memory access (I/O) costs often constitute one of the primary bottlenecks in modern model architectures, which is widely referred to as the “memory wall” (Dao et al., 2022). This bottleneck is frequently overlooked in architectural design, yet it decisively impacts runtime efficiency.

Focusing on the widely adopted pre-norm Transformer (Vaswani et al., 2017) architecture, we analyze the I/O patterns inherent to HC. Tab. 2 summarizes the per token memory access overhead in a single residual layer introduced by the $n$ -stream residual design. The analysis reveals that HC increases the memory access cost by a factor approximately proportional to ??. This excessive I/O demand significantly degrades training throughput without the mitigation of fused kernels. Besides, since $\mathcal { H } _ { l } ^ { \mathrm { p r e } } , \mathcal { H } _ { l } ^ { \mathrm { p o s t } } .$ , and $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ involve learnable parameters, their intermediate activations are required for backpropagation. This results in a substantial increase in the GPU memory footprint, often necessitating gradient checkpointing to maintain feasible memory usage. Furthermore, HC requires $n$ -fold more communication cost in pipeline parallelism (Qi et al., 2024), leading to larger bubbles and decreasing the training throughput.

Table 2 | Comparison of Memory Access Costs Per Token. This analysis accounts for the overhead introduced by the residual stream maintenance in the forward pass, excluding the internal I/O of the layer function $\mathcal { F }$ .   

<table><tr><td>Method</td><td>Operation</td><td>Read (Elements)</td><td>Write (Elements)</td></tr><tr><td rowspan="2">Residual Connection</td><td>Residual Merge</td><td>2C</td><td>C</td></tr><tr><td>Total I/O</td><td>2C</td><td>C</td></tr><tr><td rowspan="5">Hyper-Connections</td><td>Calculate Hlpre, Hlpost, Hlres</td><td>nC</td><td>n2+2n</td></tr><tr><td>Hlpre</td><td>nC+n</td><td>C</td></tr><tr><td>Hlpost</td><td>C+n</td><td>nC</td></tr><tr><td>Hlres</td><td>nC+n2</td><td>nC</td></tr><tr><td>Residual Merge</td><td>2nC</td><td>nC</td></tr><tr><td></td><td>Total I/O</td><td>(5n+1)C+n2+2n</td><td>(3n+1)C+n2+2n</td></tr></table>

# 4. Method

# 4.1. Manifold-Constrained Hyper-Connections

Drawing inspiration from the identity mapping principle (He et al., 2016b), the core premise of mHC is to constrain the residual mapping $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ onto a specific manifold. While the original identity mapping ensures stability by enforcing $\mathcal { H } _ { l } ^ { \mathrm { r e s } } = \mathbf { I } ,$ it fundamentally precludes information exchange within the residual stream, which is critical for maximizing the potential of multistream architectures. Therefore, we propose projecting the residual mapping onto a manifold that simultaneously maintains the stability of signal propagation across layers and facilitates mutual interaction among residual streams to preserve the model’s expressivity. To this end, we restrict $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ to be a doubly stochastic matrix, which has non-negative entries where both the rows and columns sum to 1. Formally, let $M ^ { \mathrm { r e s } }$ denote the manifold of doubly stochastic matrices (also known as the Birkhoff polytope). We constrain $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ to $\mathcal { P } _ { M ^ { \mathrm { r e s } } } ( \mathcal { H } _ { l } ^ { \mathrm { r e s } } )$ , defined as:

$$
\mathcal {P} _ {\mathcal {M} ^ {\mathrm {r e s}}} (\mathcal {H} _ {l} ^ {\mathrm {r e s}}) := \left\{\mathcal {H} _ {l} ^ {\mathrm {r e s}} \in \mathbb {R} ^ {n \times n} \mid \mathcal {H} _ {l} ^ {\mathrm {r e s}} \mathbf {1} _ {n} = \mathbf {1} _ {n}, \mathbf {1} _ {n} ^ {\top} \mathcal {H} _ {l} ^ {\mathrm {r e s}} = \mathbf {1} _ {n} ^ {\top}, \mathcal {H} _ {l} ^ {\mathrm {r e s}} \geqslant 0 \right\}, \tag {6}
$$

where ${ \bf 1 } _ { n }$ represents the $n$ -dimensional vector of all ones.

It is worth noting that when $n = 1$ , the doubly stochastic condition degenerates to the scalar 1, thereby recovering the original identity mapping. The choice of double stochasticity confers several rigorous theoretical properties beneficial for large-scale model training:

1. Norm Preservation: The spectral norm of a doubly stochastic matrix is bounded by 1 (i.e., $\| \mathcal { H } _ { l } ^ { \mathrm { r e s } } \| _ { 2 } \leq 1 )$ . This implies that the learnable mapping is non-expansive, effectively mitigating the gradient explosion problem.   
2. Compositional Closure: The set of doubly stochastic matrices is closed under matrix multiplication. This ensures that the composite residual mapping across multiple layers, $\begin{array} { r } { \prod _ { i = 1 } ^ { L - l } \dot { \mathcal { H } } _ { L - i } ^ { \mathrm { r e s } } , } \end{array}$ remains doubly stochastic, thereby preserving stability throughout the entire   
3. Geometric Interpretation via the Birkhoff Polytope: The set $M ^ { \mathrm { r e s } }$ forms the Birkhoff polytope, which is the convex hull of the set of permutation matrices. This provides a clear geometric interpretation: the residual mapping acts as a convex combination of permutations. Mathematically, the repeated application of such matrices tends to increase

the mixing of information across streams monotonically, effectively functioning as a robust feature fusion mechanism.

Additionally, we impose non-negativity constraints on the input mappings $\mathcal { H } _ { l } ^ { \mathrm { p r e } }$ and output mappings $\mathcal { H } _ { l } ^ { \mathrm { p o s t } }$ . This constrain prevents signal cancellation arising from the composition of positive and negative coefficients, which can also be considered as a special manifold projection.

# 4.2. Parameterization and Manifold Projection

In this section, we detail the calculation process of $\mathcal { H } _ { l } ^ { \mathrm { p r e } } , \mathcal { H } _ { l } ^ { \mathrm { p o s t } }$ , and $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ in mHC. Given the input hidden matrix $\mathbf { x } _ { l } \in \mathbb { R } ^ { n \times C }$ at the ??-th layer, we first flatten it into a vector $\vec { \bf x } _ { l } = \mathrm { v e c } ( { \bf x } _ { l } ) \in \mathbb { R } ^ { 1 \times n C }$ to preserve full context information. Then, we follow the original HC formulation to get the dynamic mappings and the static mappings as follows:

$$
\left\{ \begin{array}{l} \vec {\mathbf {x}} _ {l} ^ {\prime} = \operatorname {R M S N o r m} (\vec {\mathbf {x}} _ {l}) \\ \tilde {\mathcal {H}} _ {l} ^ {\text {p r e}} = \alpha_ {l} ^ {\text {p r e}} \cdot \left(\vec {\mathbf {x}} _ {l} ^ {\prime} \varphi_ {l} ^ {\text {p r e}}\right) + \mathbf {b} _ {l} ^ {\text {p r e}} \\ \tilde {\mathcal {H}} _ {l} ^ {\text {p o s t}} = \alpha_ {l} ^ {\text {p o s t}} \cdot \left(\vec {\mathbf {x}} _ {l} ^ {\prime} \varphi_ {l} ^ {\text {p o s t}}\right) + \mathbf {b} _ {l} ^ {\text {p o s t}} \\ \tilde {\mathcal {H}} _ {l} ^ {\text {r e s}} = \alpha_ {l} ^ {\text {r e s}} \cdot \operatorname {m a t} \left(\vec {\mathbf {x}} _ {l} ^ {\prime} \varphi_ {l} ^ {\text {r e s}}\right) + \mathbf {b} _ {l} ^ {\text {r e s}}, \end{array} \right. \tag {7}
$$

where $\varphi _ { l } ^ { \mathrm { p r e } } , \varphi _ { l } ^ { \mathrm { p o s t } } \in \mathbb { R } ^ { n C \times n }$ and $\varphi _ { l } ^ { \mathrm { r e s } } \in \mathbb { R } ^ { n C \times n ^ { 2 } }$ are linear projections for dynamic mappings and mat(·) is a reshape function from $\mathbb { R } ^ { 1 \times n ^ { 2 } }$ to $\mathbb { R } ^ { n \times n }$ .

Then, the final constrained mappings are obtained via:

$$
\left\{ \begin{array}{l} \mathcal {H} _ {l} ^ {\text {p r e}} = \sigma \left(\tilde {\mathcal {H}} _ {l} ^ {\text {p r e}}\right) \\ \mathcal {H} _ {l} ^ {\text {p o s t}} = 2 \sigma \left(\tilde {\mathcal {H}} _ {l} ^ {\text {p o s t}}\right) \\ \mathcal {H} _ {l} ^ {\text {r e s}} = \operatorname {S i n k h o r n - K n o p p} \left(\tilde {\mathcal {H}} _ {l} ^ {\text {r e s}}\right), \end{array} \right. \tag {8}
$$

where $\sigma ( \cdot )$ denotes the Sigmoid function. The Sinkhorn-Knopp(·) operator firstly makes all elements to be positive via an exponent operator and then conducts iterative normalization process that alternately rescales rows and columns to sum to 1. Specifically, given a positive matrix $\mathbf { M } ^ { ( 0 ) } = \exp ( \mathcal { \tilde { H } } _ { l } ^ { \mathrm { r e s } } )$ as the start point, the normalization iteration proceeds as:

$$
\mathbf {M} ^ {(t)} = \mathcal {T} _ {r} \left(\mathcal {T} _ {c} \left(\mathbf {M} ^ {(t - 1)}\right)\right), \tag {9}
$$

where $\mathcal { T } _ { r }$ and $\mathcal { T } _ { c }$ denote row and column normalization, respectively. This process converges to a doubly stochastic matrix $\mathcal { H } _ { l } ^ { \mathrm { r e s } } = \mathbf { M } ^ { ( t _ { \mathrm { m a x } } ) }$ as $t _ { \mathrm { m a x } } \to \infty$ . We choose $t _ { \mathrm { m a x } } = 2 0$ as a practical value in our experiments.

# 4.3. Efficient Infrastructure Design

In this section, we detail the infrastructure design tailored for mHC. Through rigorous optimization, we implement mHC (with $n = 4$ ) in large-scale models with a marginal training overhead of only $6 . 7 \%$ .

# 4.3.1. Kernel Fusion

Observing that RMSNorm in mHC imposes significant latency when operating on the highdimensional hidden state $\vec { \bf x } _ { l } \in \mathbb { R } ^ { 1 \times n C }$ , we reorder the dividing-by-norm operation to follow the

matrix multiplication. This optimization maintains mathematical equivalence while improving efficiency. Furthermore, we employ mixed-precision strategies to maximize numerical accuracy without compromising speed, and fuse multiple operations with shared memory access into unified compute kernels to reduce memory bandwidth bottlenecks. Based on the inputs and parameters detailed in Eq. (10) to (13), we implement three specialized mHC kernels to compute H pre?? , $\bar { \mathcal { H } } _ { l } ^ { \mathrm { p r e } } , \mathcal { H } _ { l } ^ { \mathrm { p o s t } } ,$ H post , and $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ . In these kernels, the biases and linear projections are consolidated into ${ \bf b } _ { l }$ and $\varphi _ { l } ,$ and the RMSNorm weight is also absorbed in $\varphi _ { l }$ .

• Eq. (14) to (15): We develop a unified kernel that fuses two scans on $\vec { \bf x } _ { l } ,$ leveraging matrix multiplication units to maximize memory bandwidth utilization. The backward pass—comprising two matrix multiplications—is similarly consolidated into a single kernel, eliminating redundant reloading of $\vec { \bf x } _ { l }$ . Both kernels feature a finely tuned pipeline (load, cast, compute, store) to efficiently handle mixed-precision processing.   
• Eq. (16) to (18): These lightweight operations on small coefficients are opportunistically fused into a single kernel, significantly reducing kernel launch overhead.   
• Eq. (19): We implement the Sinkhorn-Knopp iteration within a single kernel. For the backward pass, we derive a custom backward kernel that recomputes the intermediate results on-chip and traverses the entire iteration.

$$
\varphi_ {l}: \text {t f l o a t} 3 2 \quad [ n C, n ^ {2} + 2 n ] \tag {10}
$$

$$
\vec {\mathbf {x}} _ {l}: \text {b f l o a t} 1 6 \quad [ 1, n C ] \tag {11}
$$

$$
\alpha_ {l} ^ {\text {p r e}}, \alpha_ {l} ^ {\text {p o s t}}, \alpha_ {l} ^ {\text {r e s}}: \text {f l o a t 3 2} \quad \text {S c a l a r s} \tag {12}
$$

$$
\mathbf {b} _ {l}: \text {f l o a t 3 2} \quad [ 1, n ^ {2} + 2 n ] \tag {13}
$$

$$
\begin{array}{l} \left[ \tilde {\mathcal {H}} _ {l} ^ {\text {p r e}}, \tilde {\mathcal {H}} _ {l} ^ {\text {p o s t}}, \tilde {\mathcal {H}} _ {l} ^ {\text {r e s}} \right]: \text {f l o a t 3 2} = \vec {\mathrm {x}} _ {l} \varphi_ {l} (14) \\ r: \text {f l o a t 3 2} = \left\| \vec {\mathbf {x}} _ {l} \right\| _ {2} / \sqrt {n C} (15) \\ \end{array}
$$

$$
\begin{array}{l} \left[ \tilde {\mathcal {H}} _ {l} ^ {\text {p r e}}, \tilde {\mathcal {H}} _ {l} ^ {\text {p o s t}}, \tilde {\mathcal {H}} _ {l} ^ {\text {r e s}} \right]: \text {f l o a t 3 2} = 1 / r \left[ \alpha_ {l} ^ {\text {p r e}} \tilde {\mathcal {H}} _ {l} ^ {\text {p r e}}, \alpha_ {l} ^ {\text {p o s t}} \tilde {\mathcal {H}} _ {l} ^ {\text {p o s t}}, \alpha_ {l} ^ {\text {r e s}} \tilde {\mathcal {H}} _ {l} ^ {\text {r e s}} \right] + \mathbf {b} _ {l} (16) \\ \mathcal {H} _ {l} ^ {\text {p r e}}: \text {f l o a t 3 2} = \sigma \left(\tilde {\mathcal {H}} _ {l} ^ {\text {p r e}}\right) (17) \\ \mathcal {H} _ {l} ^ {\text {p o s t}}: \text {f l o a t 3 2} = 2 \sigma \left(\tilde {\mathcal {H}} _ {l} ^ {\text {p o s t}}\right) (18) \\ \mathcal {H} _ {l} ^ {\text {r e s}}: \text {f l o a t 3 2} \quad = \text {S i n k h o r n - K n o p p} \left(\tilde {\mathcal {H}} _ {l} ^ {\text {r e s}}\right) (19) \\ \end{array}
$$

Using the coefficients derived from the aforementioned kernels, we introduce two additional kernels to apply these mappings: one for $\mathcal { F } _ { \mathrm { p r e } } : = \mathcal { H } _ { l } ^ { \mathrm { p r e } } \mathbf { x } _ { l }$ and another for $\mathcal { F } _ { \mathrm { p o s t , r e s } } : =$ $\mathcal { H } _ { l } ^ { \mathrm { r e s } } \mathbf { x } _ { l } + \mathcal { H } _ { l } ^ { \mathrm { p o s t } \top } \mathcal { F } ( \cdot , \cdot )$ . Through fusing the application of $\mathcal { H } _ { l } ^ { \mathrm { p o s t } }$ and $\mathcal { H } _ { l } ^ { \mathrm { r e s } }$ with residual merging, we reduce the number of elements read from $( 3 n + 1 ) C$ to $( n + 1 ) C$ and the number of elements written from $3 n C$ to $n C$ for this kernel. We efficiently implement the majority of kernels (excluding Eq. (14) to (15)) using TileLang (Wang et al., 2025). This framework streamlines the implementation of kernels with complex calculation process and allows us to fully utilize the memory bandwidth with minimal engineering effort.

# 4.3.2. Recomputing

The $n$ -stream residual design introduces substantial memory overhead during training. To mitigate this, we discard the intermediate activations of the mHC kernels after the forward pass and recompute them on-the-fly in the backward pass, through re-executing the mHC kernels

without the heavy layer function $\mathcal { F }$ . Consequently, for a block of $L _ { r }$ consecutive layers, we need only store the input $\mathbf { x } _ { l _ { 0 } }$ to the first layer. Excluding lightweight coefficients while accounting for the pre-norm with in $\mathcal { F } _ { \cdot }$ , Tab. 3 summarizes the intermediate activations preserved for the backward pass.

Table 3 | Stored and Recomputed Intermediate Activations We list per token activation preserved for the backward pass and the transient activation recomputed in $L _ { r }$ consecutive layers. Layer $l _ { 0 }$ represents the first layer in $L _ { r }$ layers and layer ?? is in $[ l _ { 0 } , l _ { 0 } + L _ { r } - 1 ]$ .   

<table><tr><td>Activations</td><td>x l0</td><td>F(Hl pre x l, Wl)</td><td>x l</td><td>Hl pre x l</td><td>RMSNorm(Hl pre x l)</td></tr><tr><td>Size (Elements)</td><td>nC</td><td>C</td><td>nC</td><td>C</td><td>C</td></tr><tr><td>Stored Method</td><td>Every Lr layers</td><td>Every layer</td><td colspan="3">Transient inside Lr layers</td></tr></table>

Since mHC kernels recomputation is performed for blocks of $L _ { r }$ consecutive layers, given a total of $L$ layers, we must persistently store the first layer input $\mathbf { x } _ { l _ { 0 } }$ for all $\textstyle \left\lceil { \frac { L } { L _ { r } } } \right\rceil$ blocks for the backward pass. In addition to this resident memory, the recomputation process introduces a transient memory overhead of $( n + 2 ) C \times L _ { r }$ elements for the active block, which determines the peak memory usage during backpropagation. Consequently, we determine the optimal block size $L _ { r } ^ { * }$ by minimizing the total memory footprint corresponded to $L _ { r }$ :

$$
L _ {r} ^ {*} = \arg \min  _ {L _ {r}} \left[ n C \times \left\lceil \frac {L}{L _ {r}} \right\rceil + (n + 2) C \times L _ {r} \right] \approx \sqrt {\frac {n L}{n + 2}}. \tag {20}
$$

Furthermore, pipeline parallelism in large-scale training imposes a constraint: recomputation blocks must not cross pipeline stage boundaries. Observing that the theoretical optimum $L _ { r } ^ { * }$ typically aligns with the number of layers per pipeline stage, we choose to synchronize the recomputation boundaries with the pipeline stages.

# 4.3.3. Overlapping Communication in DualPipe

In large-scale training, pipeline parallelism is the standard practice for mitigating parameter and gradient memory footprints. Specifically, we adopt the DualPipe schedule (Liu et al., 2024b), which effectively overlaps scale-out interconnected communication traffic, such as those in expert and pipeline parallelism. However, compared to the single-stream design, the proposed ??-stream residual in mHC incurs substantial communication latency across pipeline stages. Furthermore, at stage boundaries, the recomputation of mHC kernels for all $L _ { r }$ layers introduces non-negligible computational overhead. To address these bottlenecks, we extend the DualPipe schedule (see Fig. 4) to facilitate improved overlapping of communication and computation at pipeline stage boundaries.

Notably, to prevent blocking the communication stream, we execute the $\mathcal { F } _ { \mathrm { p o s t , r e s } }$ kernels of MLP (i.e. FFN) layers on a dedicated high-priority compute stream. We further refrain from employing persistent kernels for long-running operations in attention layers, thereby preventing extended stalls. This design enables the preemption of overlapped attention computations, allowing for flexible scheduling while maintaining high utilization of the compute device’s processing units. Furthermore, the recomputation process is decoupled from pipeline communication dependencies, as the initial activation of each stage $\mathbf { x } _ { l _ { 0 } }$ is already cached locally.

![](images/65851a277d90d5dae38cf3e56cc7804675a6b8744db2a63299d18a7e61a35213.jpg)  
Figure 4 | Communication-Computation Overlapping for mHC. We extend the DualPipe schedule to handle the overhead introduced by mHC. Lengths of each block are illustrative only and do not represent actual duration. (F), (B), (W) refers to forward pass, backward pass, weight gradient computation, respectively. $\mathcal { F } ^ { \mathrm { A } }$ and ${ \mathcal { F } } ^ { \mathrm { M } }$ represents kernels corresponded to Attention and MLP, respectively.

# 5. Experiments

# 5.1. Experimental Setup

We validate the proposed method via language model pre-training, conducting a comparative analysis between the baseline, HC, and our proposed mHC. Utilizing MoE architectures inspired by DeepSeek-V3 (Liu et al., 2024b), we train four distinct model variants to cover different evaluation regimes. Specifically, the expansion rate ?? for both HC and mHC is set to 4. Our primary focus is a 27B model trained with a dataset size proportional to its parameters, which serves as the subject for our system-level main results. Expanding on this, we analyze the compute scaling behavior by incorporating smaller 3B and 9B models trained with proportional data, which allows us to observe performance trends across varying compute. Additionally, to specifically investigate the token scaling behavior, we train a separate 3B model on a fixed corpus of 1 trillion tokens. Detailed model configurations and training hyper-parameters are provided in Appendix A.1.

# 5.2. Main Results

![](images/7567f452b1400c03c3e8ef4e3262fb09d866ec0335cebdd52565203fad3645df.jpg)  
(a) Absolute Training Loss Gap vs: Training Steps

![](images/f10743e73c052f531718c3f3032b0485de6d71bd7a8c8cb57fcc4ef34c19f4b6.jpg)  
(b) Gradient Norm vs: Training Steps   
Figure 5 | Training Stability of Manifold-Constrained Hyper-Connections (mHC). This figure illustrates (a) the absolute training loss gap of mHC and HC relative to the baseline, and (b) the gradient norm of the three methods. All experiments utilize the 27B model. The results demonstrate that mHC exhibits improved stability in terms of both loss and gradient norm.

We begin by examining the training stability and convergence of the 27B models. As illustrated in Fig. 5 (a), mHC effectively mitigates the training instability observed in HC, achieving a final loss reduction of 0.021 compared to the baseline. This improved stability is further corroborated by the gradient norm analysis in Fig. 5 (b), where mHC exhibits significantly better behavior than HC, maintaining a stable profile comparable to the baseline.

Table 4 | System-level Benchmark Results for 27B Models. This table compares the zeroshot and few-shot performance of the Baseline, HC, and mHC across 8 diverse downstream benchmarks. mHC consistently outperforms the Baseline and surpasses HC on the majority of benchmarks, demonstrating its effectiveness in large-scale pre-training.   

<table><tr><td>Benchmark (Metric)</td><td>BBH (EM)</td><td>DROP (F1)</td><td>GSM8K (EM)</td><td>HellaSwag (Acc.)</td><td>MATH (EM)</td><td>MMLU (Acc.)</td><td>PIQA (Acc.)</td><td>TriviaQA (EM)</td></tr><tr><td># Shots</td><td>3-shot</td><td>3-shot</td><td>8-shot</td><td>10-shot</td><td>4-shot</td><td>5-shot</td><td>0-shot</td><td>5-shot</td></tr><tr><td>27B Baseline</td><td>43.8</td><td>47.0</td><td>46.7</td><td>73.7</td><td>22.0</td><td>59.0</td><td>78.5</td><td>54.3</td></tr><tr><td>27B w/ HC</td><td>48.9</td><td>51.6</td><td>53.2</td><td>74.3</td><td>26.4</td><td>63.0</td><td>79.9</td><td>56.3</td></tr><tr><td>27B w/ mHC</td><td>51.0</td><td>53.9</td><td>53.8</td><td>74.7</td><td>26.0</td><td>63.4</td><td>80.5</td><td>57.6</td></tr></table>

Tab. 4 presents the downstream performance across a diverse set of benchmarks (Bisk et al., 2020; Cobbe et al., 2021; Hendrycks et al., 2020, 2021; Joshi et al., 2017; Zellers et al., 2019). mHC yields comprehensive improvements, consistently outperforming the baseline and surpassing HC on the majority of tasks. Notably, compared to HC, mHC further enhances the model’s reasoning capabilities, delivering performance gains of $2 . 1 \%$ on BBH (Suzgun et al., 2022) and $2 . 3 \%$ on DROP (Dua et al., 2019).

# 5.3. Scaling Experiments

![](images/e7bf631ab2876db45244bcfa18144c1d66e71a4e960421217a685ae82b212dd5.jpg)

![](images/bff03a73e8874be0de65a0a40f09f9bdf45a8360a579b39445f5b96c203f09ea.jpg)  
(a) Compute Scaling Curve

![](images/64c73cfa3e1c1190229a0bcea56621251777f5c6b0a407ac2a48f5f767b51984.jpg)

![](images/92c99f9a5a62538c93e898cd97bd14991e33d97930d0bb4047f7c0b8fe4cc359.jpg)  
(b) Token Scaling Curve   
Figure 6 | Scaling properties of mHC compared to the Baseline. (a) Compute Scaling Curve. Solid lines depict the performance gap across different compute budgets. Each point represents a specific compute-optimal configuration of model size and dataset size, scaling from 3B and 9B to 27B parameters. (b) Token Scaling Curve. Trajectory of the 3B model during training. Each point represents the model’s performance at different training tokens. Detailed architectures and training configurations are provided in Appendix A.1.

To assess the scalability of our approach, we report the relative loss improvement of mHC against the baseline across different scales. In Fig. 6 (a), we plot the compute scaling curve spanning 3B, 9B, and 27B parameters. The trajectory indicates that the performance advantage is robustly maintained even at higher computational budgets, showing only marginal attenuation. Furthermore, we examine the within-run dynamics in Fig. 6 (b), which presents the token scaling curve for the 3B model. Collectively, these findings validate the effectiveness of mHC in large-scale scenarios. This conclusion is further corroborated by our in-house large-scale training experiments.

![](images/159c503f36d35d8ad937b23104a7a90d5062bdbd9bfacb0c0ae8d9b35a9dd26d.jpg)  
(a) Single-Layer Mapping

![](images/226084785797e72a51ac3a4f47680739fbb2d004bc89e651bbe31e3a5cd14548.jpg)  
(b) Composite Mapping

![](images/2f266e96478241ff13961953cf9a181e3a70ed02da02ee4658bfd3a33908ac13.jpg)  
Figure 7 | Propagation Stability of Manifold-Constrained Hyper-Connections (mHC). This figure illustrates the propagation dynamics of (a) the single-layer mapping $\mathcal { P } _ { M ^ { \mathrm { r e s } } } ( \mathcal { H } _ { l } ^ { \mathrm { r e s } } )$ and (b) the composite mapping $\Pi _ { i = 1 } ^ { L - l } { \mathcal { P } } _ { M ^ { \mathrm { r e s } } } ( { \mathcal { H } } _ { L - i } ^ { \mathrm { r e s } } )$ within the 27B model. The results demonstrate that mHC significantly enhances propagation stability compared to HC.

![](images/04d2b43ad9fcbf98cc66616ade47bf92bf744fe638cfe61b677ccbad585b20e0.jpg)

![](images/b80726d7f9123614e32e3ea61b8c3476840cbd320aaf14ad5c589c380e692bda.jpg)

![](images/d50b0e15cf8386189096845356dd28db44730f94511fb5d6ea2b8eb0eee81ac4.jpg)

![](images/0f71dcdac99d601c67379f1e8fdb01cd192c2324d9fa641fa0f1f7278501a85f.jpg)

![](images/1427a22f5b5b09cfe763ee5d06e3aa390f59fa12c4add7b0eac19ea56e1815ae.jpg)  
Figure 8 | Visualizations of Learnable Mappings. This figure displays representative singlelayer and composite mappings for HC (first row) and mHC (second row). Each matrix is computed by averaging over all tokens within a selected sequence. The labels annotated along the y-axis and x-axis indicate the forward signal gain (row sum) and the backward gradient gain (column sum), respectively.

# 5.4. Stability Analysis

Similar to Fig. 3, Fig. 7 illustrates the propagation stability of mHC. Ideally, the single-layer mapping satisfies the doubly stochastic constraint, implying that both the forward signal gain and the backward gradient gain should equal to 1. However, practice implementations utilizing the Sinkhorn-Knopp algorithm must limit the number of iterations to achieve computational efficiency. In our settings, we use 20 iterations to obtain an approximate solution. Consequently, as shown in Fig. 7(a), the backward gradient gain deviates slightly from 1. In the composite case shown in Fig. 7(b), the deviation increases but remains bounded, reaching a maximum value of approximately 1.6. Notably, compared to the maximum gain magnitude of nearly 3000 in HC, mHC significantly reduces it by three orders of magnitude. These results demonstrate that mHC significantly enhances propagation stability compared to HC, ensuring stable forward signal and backward gradient flows. Additionally, Fig. 8 displays representative mappings. We observe that for HC, when the maximum gain is large, other values also tend to be significant, which indicates general instability across all propagation paths. In contrast, mHC consistently yields stable results.

# 6. Conclusion and Outlook

In this paper, we identify that while expanding the width of residual stream and diversifying connections yields performance gains as proposed in Hyper-Connections (HC), the unconstrained nature of these connections leads to signal divergence. This disruption compromises the conservation of signal energy across layers, inducing training instability and hindering the scalability of deep networks. To address these challenges, we introduce Manifold-Constrained Hyper-Connections (mHC), a generalized framework that projects the residual connection space onto a specific manifold. By employing the Sinkhorn-Knopp algorithm to enforce a doubly stochastic constraint on residual mappings, mHC transforms signal propagation into a convex combination of features. Empirical results confirm that mHC effectively restores the identity mapping property, enabling stable large-scale training with superior scalability compared to conventional HC. Crucially, through efficient infrastructure-level optimizations, mHC delivers these improvements with negligible computational overhead.

As a generalized extension of the HC paradigm, mHC opens several promising avenues for future research. Although this work utilizes doubly stochastic matrices to ensure stability, the framework accommodates the exploration of diverse manifold constraints tailored to specific learning objectives. We anticipate that further investigation into distinct geometric constraints could yield novel methods that better optimize the trade-off between plasticity and stability. Furthermore, we hope mHC rejuvenates community interest in macro-architecture design. By deepening the understanding of how topological structures influence optimization and representation learning, mHC will help address current limitations and potentially illuminate new pathways for the evolution of next-generation foundational architectures.

# References

J. Ainslie, J. Lee-Thorp, M. De Jong, Y. Zemlyanskiy, F. Lebrón, and S. Sanghai. Gqa: Training generalized multi-query transformer models from multi-head checkpoints. arXiv preprint arXiv:2305.13245, 2023.   
Y. Bisk, R. Zellers, R. L. Bras, J. Gao, and Y. Choi. PIQA: reasoning about physical commonsense in natural language. In The Thirty-Fourth AAAI Conference on Artificial Intelligence, AAAI 2020, The Thirty-Second Innovative Applications of Artificial Intelligence Conference, IAAI 2020, The Tenth AAAI Symposium on Educational Advances in Artificial Intelligence, EAAI 2020, New York, NY, USA, February 7-12, 2020, pages 7432–7439. AAAI Press, 2020. doi: 10.1609/aaai.v34i05.6239. URL https://doi.org/10.1609/aaai.v34i05.6239.   
T. Brown, B. Mann, N. Ryder, M. Subbiah, J. D. Kaplan, P. Dhariwal, A. Neelakantan, P. Shyam, G. Sastry, A. Askell, et al. Language models are few-shot learners. Advances in neural information processing systems, 33:1877–1901, 2020.   
Y. Chai, S. Jin, and X. Hou. Highway transformer: Self-gating enhanced self-attentive networks. In D. Jurafsky, J. Chai, N. Schluter, and J. Tetreault, editors, Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics, pages 6887–6900, Online, July 2020. Association for Computational Linguistics. doi: 10.18653/v1/2020.acl-main.616. URL https://aclanthology.org/2020.acl-main.616/.   
F. Chollet. Xception: Deep learning with depthwise separable convolutions. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 1251–1258, 2017.

K. Cobbe, V. Kosaraju, M. Bavarian, M. Chen, H. Jun, L. Kaiser, M. Plappert, J. Tworek, J. Hilton, R. Nakano, et al. Training verifiers to solve math word problems. arXiv preprint arXiv:2110.14168, 2021.   
T. Dao, D. Y. Fu, S. Ermon, A. Rudra, and C. Ré. FlashAttention: Fast and memory-efficient exact attention with IO-awareness. In Advances in Neural Information Processing Systems (NeurIPS), 2022.   
D. Dua, Y. Wang, P. Dasigi, G. Stanovsky, S. Singh, and M. Gardner. DROP: A reading comprehension benchmark requiring discrete reasoning over paragraphs. In J. Burstein, C. Doran, and T. Solorio, editors, Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, NAACL-HLT 2019, Minneapolis, MN, USA, June 2-7, 2019, Volume 1 (Long and Short Papers), pages 2368– 2378. Association for Computational Linguistics, 2019. doi: 10.18653/V1/N19-1246. URL https://doi.org/10.18653/v1/n19-1246.   
Y. Fang, Y. CAI, J. Chen, J. Zhao, G. Tian, and G. Li. Cross-layer retrospective retrieving via layer attention. In The Eleventh International Conference on Learning Representations, 2023. URL https://openreview.net/forum?id=pvgEL1yS3Ql.   
W. Fedus, B. Zoph, and N. Shazeer. Switch transformers: Scaling to trillion parameter models with simple and efficient sparsity. Journal of Machine Learning Research, 23(120):1–39, 2022.   
K. He, X. Zhang, S. Ren, and J. Sun. Deep residual learning for image recognition. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 770–778, 2016a.   
K. He, X. Zhang, S. Ren, and J. Sun. Identity mappings in deep residual networks. In European conference on computer vision, pages 630–645. Springer, 2016b.   
M. Heddes, A. Javanmard, K. Axiotis, G. Fu, M. Bateni, and V. Mirrokni. Deepcrossattention: Supercharging transformer residual connections. In Forty-second International Conference on Machine Learning, 2025. URL https://openreview.net/forum?id=j3JBfFnGYh.   
D. Hendrycks, C. Burns, S. Basart, A. Zou, M. Mazeika, D. Song, and J. Steinhardt. Measuring massive multitask language understanding. arXiv preprint arXiv:2009.03300, 2020.   
D. Hendrycks, C. Burns, S. Kadavath, A. Arora, S. Basart, E. Tang, D. Song, and J. Steinhardt. Measuring mathematical problem solving with the math dataset. arXiv preprint arXiv:2103.03874, 2021.   
J. Hoffmann, S. Borgeaud, A. Mensch, E. Buchatskaya, T. Cai, E. Rutherford, D. de Las Casas, L. A. Hendricks, J. Welbl, A. Clark, T. Hennigan, E. Noland, K. Millican, G. van den Driessche, B. Damoc, A. Guy, S. Osindero, K. Simonyan, E. Elsen, O. Vinyals, J. Rae, and L. Sifre. An empirical analysis of compute-optimal large language model training. In S. Koyejo, S. Mohamed, A. Agarwal, D. Belgrave, K. Cho, and A. Oh, editors, Advances in Neural Information Processing Systems, volume 35, pages 30016–30030. Curran Associates, Inc., 2022. URL https://proceedings.neurips.cc/paper_files/paper/2022/file/c1e2faf f6f588870935f114ebe04a3e5-Paper-Conference.pdf.   
G. Huang, Z. Liu, L. Van Der Maaten, and K. Q. Weinberger. Densely connected convolutional networks. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 4700–4708, 2017.

M. Joshi, E. Choi, D. Weld, and L. Zettlemoyer. TriviaQA: A large scale distantly supervised challenge dataset for reading comprehension. In R. Barzilay and M.-Y. Kan, editors, Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 1601–1611, Vancouver, Canada, July 2017. Association for Computational Linguistics. doi: 10.18653/v1/P17-1147. URL https://aclanthology.org/P17-1147.   
G. Larsson, M. Maire, and G. Shakhnarovich. Fractalnet: Ultra-deep neural networks without residuals. arXiv preprint arXiv:1605.07648, 2016.   
D. Lepikhin, H. Lee, Y. Xu, D. Chen, O. Firat, Y. Huang, M. Krikun, N. Shazeer, and Z. Chen. Gshard: Scaling giant models with conditional computation and automatic sharding. arXiv preprint arXiv:2006.16668, 2020.   
A. Liu, B. Feng, B. Wang, B. Wang, B. Liu, C. Zhao, C. Dengr, C. Ruan, D. Dai, D. Guo, et al. Deepseek-v2: A strong, economical, and efficient mixture-of-experts language model. arXiv preprint arXiv:2405.04434, 2024a.   
A. Liu, B. Feng, B. Xue, B. Wang, B. Wu, C. Lu, C. Zhao, C. Deng, C. Zhang, C. Ruan, et al. Deepseek-v3 technical report. arXiv preprint arXiv:2412.19437, 2024b.   
I. Loshchilov and F. Hutter. Decoupled weight decay regularization. arXiv preprint arXiv:1711.05101, 2017.   
B. Mak and J. Flanigan. Residual matrix transformers: Scaling the size of the residual stream. arXiv preprint arXiv:2506.22696, 2025.   
G. Menghani, R. Kumar, and S. Kumar. LAurel: Learned augmented residual layer. In Forty-second International Conference on Machine Learning, 2025. URL https://open review.net/forum?id $\equiv$ rUDRWP9WvZ.   
M. Pagliardini, A. Mohtashami, F. Fleuret, and M. Jaggi. Denseformer: Enhancing information flow in transformers via depth weighted averaging. In The Thirty-eighth Annual Conference on Neural Information Processing Systems, 2024. URL https://openreview.net/forum ?id=kMnoh7CXrq.   
P. Qi, X. Wan, G. Huang, and M. Lin. Zero bubble (almost) pipeline parallelism. In The Twelfth International Conference on Learning Representations, 2024. URL https://openreview .net/forum?id=tuzTN0eIO5.   
N. Shazeer. Fast transformer decoding: One write-head is all you need. arXiv preprint arXiv:1911.02150, 2019.   
N. Shazeer, A. Mirhoseini, K. Maziarz, A. Davis, Q. Le, G. Hinton, and J. Dean. Outrageously large neural networks: The sparsely-gated mixture-of-experts layer. arXiv preprint arXiv:1701.06538, 2017.   
R. Sinkhorn and P. Knopp. Concerning nonnegative matrices and doubly stochastic matrices. Pacific Journal of Mathematics, 21(2):343–348, 1967.   
R. K. Srivastava, K. Greff, and J. Schmidhuber. Training very deep networks. In C. Cortes, N. Lawrence, D. Lee, M. Sugiyama, and R. Garnett, editors, Advances in Neural Information Processing Systems, volume 28. Curran Associates, Inc., 2015. URL https://proceedings. neurips.cc/paper_files/paper/2015/file/215a71a12769b056c3c32e7299f1c5e d-Paper.pdf.

J. Su, M. Ahmed, Y. Lu, S. Pan, W. Bo, and Y. Liu. Roformer: Enhanced transformer with rotary position embedding. Neurocomputing, 568:127063, 2024.   
M. Suzgun, N. Scales, N. Schärli, S. Gehrmann, Y. Tay, H. W. Chung, A. Chowdhery, Q. V. Le, E. H. Chi, D. Zhou, et al. Challenging big-bench tasks and whether chain-of-thought can solve them. arXiv preprint arXiv:2210.09261, 2022.   
H. Touvron, T. Lavril, G. Izacard, X. Martinet, M.-A. Lachaux, T. Lacroix, B. Rozière, N. Goyal, E. Hambro, F. Azhar, et al. Llama: Open and efficient foundation language models. arXiv preprint arXiv:2302.13971, 2023.   
A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polosukhin. Attention is all you need. Advances in neural information processing systems, 30, 2017.   
L. Wang, H. Gao, C. Zhao, X. Sun, and D. Dai. Auxiliary-loss-free load balancing strategy for mixture-of-experts. arXiv preprint arXiv:2408.15664, 2024.   
L. Wang, Y. Cheng, Y. Shi, Z. Tang, Z. Mo, W. Xie, L. Ma, Y. Xia, J. Xue, F. Yang, et al. Tilelang: A composable tiled programming model for ai systems. arXiv preprint arXiv:2504.17577, 2025.   
D. Xiao, Q. Meng, S. Li, and X. Yuan. Muddformer: Breaking residual bottlenecks in transformers via multiway dynamic dense connections. arXiv preprint arXiv:2502.12170, 2025.   
S. Xie, R. Girshick, P. Dollár, Z. Tu, and K. He. Aggregated residual transformations for deep neural networks. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 1492–1500, 2017.   
S. Xie, H. Zhang, J. Guo, X. Tan, J. Bian, H. H. Awadalla, A. Menezes, T. Qin, and R. Yan. Residual: Transformer with dual residual connections, 2023. URL https://arxiv.org/abs/2304.1 4802.   
F. Yu, D. Wang, E. Shelhamer, and T. Darrell. Deep layer aggregation. In Proceedings of the IEEE conference on computer vision and pattern recognition, pages 2403–2412, 2018.   
R. Zellers, A. Holtzman, Y. Bisk, A. Farhadi, and Y. Choi. HellaSwag: Can a machine really finish your sentence? In A. Korhonen, D. R. Traum, and L. Màrquez, editors, Proceedings of the 57th Conference of the Association for Computational Linguistics, ACL 2019, Florence, Italy, July 28- August 2, 2019, Volume 1: Long Papers, pages 4791–4800. Association for Computational Linguistics, 2019. doi: 10.18653/v1/p19-1472. URL https://doi.org/10.18653/v1/p1 9-1472.   
B. Zhang and R. Sennrich. Root mean square layer normalization. Advances in neural information processing systems, 32, 2019.   
D. Zhu, H. Huang, Z. Huang, Y. Zeng, Y. Mao, B. Wu, Q. Min, and X. Zhou. Hyper-connections. arXiv preprint arXiv:2409.19606, 2024.

# A. Appendix

# A.1. Detailed Model Specifications and Hyper-parameters.

Table 5 | Detailed Model Specifications and Hyper-parameters. This table presents the architectural configurations for the 3B, 9B, and 27B models based on the DeepSeek-V3 (Liu et al., 2024b) architecture. It outlines the specific hyper-parameters for mHC and HC, including the residual stream expansion and Sinkhorn-Knopp settings, alongside the optimization and training protocols used in the experiments.   

<table><tr><td>Attribute</td><td>3B</td><td>9B</td><td>27B</td><td>3B
1T Tokens</td></tr><tr><td>Vocab Params</td><td>331M</td><td>496M</td><td>662M</td><td>331M</td></tr><tr><td>Active Params</td><td>612M</td><td>1.66B</td><td>4.14B</td><td>612M</td></tr><tr><td>Total Params</td><td>2.97B</td><td>9.18B</td><td>27.0B</td><td>2.97B</td></tr><tr><td>Layers</td><td>12</td><td>18</td><td>30</td><td>12</td></tr><tr><td>Leading Dense Layers</td><td></td><td>1</td><td></td><td>1</td></tr><tr><td>Routed Experts</td><td>64</td><td>64</td><td>72</td><td>64</td></tr><tr><td>Active Experts</td><td></td><td>6</td><td></td><td>6</td></tr><tr><td>Shared Experts</td><td></td><td>2</td><td></td><td>2</td></tr><tr><td>Dimension</td><td>1280</td><td>1920</td><td>2560</td><td>1280</td></tr><tr><td>FFN Dimension</td><td>896</td><td>1280</td><td>1536</td><td>896</td></tr><tr><td>Load Balancing Method</td><td colspan="3">Loss-Free (Wang et al., 2024)</td><td>Loss-Free</td></tr><tr><td>Attention Heads</td><td>16</td><td>24</td><td>32</td><td>16</td></tr><tr><td>Attention Dimension</td><td></td><td>128</td><td></td><td>128</td></tr><tr><td>Attention Variant</td><td colspan="3">MLA (Liu et al., 2024a)</td><td>MLA</td></tr><tr><td>KV Rank</td><td></td><td>512</td><td></td><td>512</td></tr><tr><td>Position Embedding</td><td colspan="3">RoPE (Su et al., 2024)</td><td>RoPE</td></tr><tr><td>RoPE Dimension</td><td></td><td>64</td><td></td><td>64</td></tr><tr><td>RoPE θ</td><td></td><td>10000</td><td></td><td>10000</td></tr><tr><td>Layer Norm Type</td><td colspan="3">RMSNorm (Zhang and Sennrich, 2019)</td><td>RMSNorm</td></tr><tr><td>Layer Norm ε</td><td></td><td>1e-20</td><td></td><td>1e-20</td></tr><tr><td>mHC/HC Expansion Rate n</td><td></td><td>4</td><td></td><td>4</td></tr><tr><td>mHC/HC Gating Factor Init α</td><td></td><td>0.01</td><td></td><td>0.01</td></tr><tr><td>mHC Sinkhorn-Knopp tmax</td><td></td><td>20</td><td></td><td>20</td></tr><tr><td>Sequence Length</td><td></td><td>4096</td><td></td><td>4096</td></tr><tr><td>Vocab Size</td><td></td><td>129280</td><td></td><td>129280</td></tr><tr><td>Batch Size</td><td>320</td><td>512</td><td>1280</td><td>2560</td></tr><tr><td>Training Steps</td><td>30000</td><td>50000</td><td>50000</td><td>100000</td></tr><tr><td>Training Tokens</td><td>39.3B</td><td>105B</td><td>262B</td><td>1.05T</td></tr><tr><td>Warmup Steps</td><td></td><td>2000</td><td></td><td>2000</td></tr><tr><td>Optimizer</td><td colspan="3">AdamW (Loshchilov and Hutter, 2017)</td><td>AdamW</td></tr><tr><td>AdamW Betas</td><td></td><td>(0.9, 0.95)</td><td></td><td>(0.9, 0.95)</td></tr><tr><td>AdamW ε</td><td></td><td>1e-20</td><td></td><td>1e-20</td></tr><tr><td>Base Learning Rate</td><td>8.6e-4</td><td>5.9e-4</td><td>4.0e-4</td><td>9.0e-4</td></tr><tr><td>Lr Scheduler</td><td></td><td>Step</td><td></td><td>Step</td></tr><tr><td>Lr Decay Step Ratio</td><td></td><td>[0.8 ×, 0.9 ×]</td><td></td><td>[0.8 ×, 0.9 ×]</td></tr><tr><td>Lr Decay Rate</td><td></td><td>[0.316, 0.1]</td><td></td><td>[0.316, 0.1]</td></tr><tr><td>Weight Decay</td><td></td><td>0.1</td><td></td><td>0.1</td></tr></table>