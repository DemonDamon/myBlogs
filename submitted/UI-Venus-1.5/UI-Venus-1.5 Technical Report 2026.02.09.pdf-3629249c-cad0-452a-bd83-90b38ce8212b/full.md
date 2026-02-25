![](images/56e72a19ffd93118c528a3a2703dce846894043fb9c27a44ee87e1ff73ea6f5f.jpg)

# UI-Venus-1.5 Technical Report

# Venus Team, Ant Group

GUI agents have emerged as a powerful paradigm for automating interactions in digital environments, yet achieving both broad generality and consistently strong task performance remains challenging. In this report, we present UI-Venus-1.5, a unified, end-to-end GUI Agent designed for robust real-world applications. The proposed model family comprises two dense variants (2B and 8B) and one mixture-of-experts variant (30B-A3B) to meet various downstream application scenarios. Compared to our previous version, UI-Venus-1.5 introduces three key technical advances: (1) a comprehensive Mid-Training stage leveraging 10 billion tokens across $^ { 3 0 + }$ datasets to establish foundational GUI semantics; (2) Online Reinforcement Learning with full-trajectory rollouts, aligning training objectives with longhorizon, dynamic navigation in large-scale environments; and (3) a single unified GUI Agent constructed via Model Merging, which synthesizes domain-specific models (grounding, web, and mobile) into one cohesive checkpoint. Extensive evaluations demonstrate that UI-Venus-1.5 establishes new state-of-the-art performance on benchmarks such as ScreenSpot-Pro $( 6 9 . 6 \% )$ , VenusBench-GD $( 7 5 . 0 \% )$ , and AndroidWorld $( 7 7 . 6 \% )$ , significantly outperforming previous strong baselines. In addition, UI-Venus-1.5 demonstrates robust navigation capabilities across a variety of Chinese mobile apps, effectively executing user instructions in real-world scenarios.

Code: https://github.com/inclusionAI/UI-Venus

Model: https://huggingface.co/collections/inclusionAI/ui-venus

![](images/c3d93cc7b356cfe0b145583d7b97c37e9bfd39f15c67c1cf69b14ce44199db3a.jpg)

ANT

GROUP

![](images/bc285623e1a694455b5e62b5b310cad5b25fb19fa433af288338cc96b4413571.jpg)  
Figure 1 UI-Venus-1.5 achieves SOTA performance across multiple GUI grounding and navigation benchmarks. Note that in the three radar charts of grounding, we have normalized the results of the top-performing model to $100 \%$ to more clearly differentiate comparisons among various baselines.

# 1 Introduction

The pursuit of creating intelligent systems capable of autonomously operating digital devices has long been a central goal in artificial intelligence. With the rapid evolution of Multimodal Large Language Models (MLLMs) Anthropic (2024); Bai et al. (2025b); Zhu et al. (2025); Zhipu-AI (2025); Seed (2025a); Bai et al. (2025a); Ling-Team et al. (2025a); Inclusion-AI et al. (2025); Ling-Team et al. (2025b), GUI Agents Gu et al. (2025); Tang et al. (2025a); Ye et al. (2025); Yan et al. (2025); Zhou et al. (2025b); Wang et al. (2025b); Liu et al. (2024); H-Company (2025); Zhang et al. (2026) have emerged as a promising solution to bridge the gap between human instructions and digital execution. Unlike traditional automation tools that rely on rigid APIs, these agents leverage visual perception to interact directly with graphical interfaces, effectively mimicking human behavior to navigate web and mobile environments.

Currently, this field is experiencing a period of intense development. The research community is actively exploring various dimensions of agent construction, ranging from the curation of large-scale GUI datasets Zhou et al. (2025b,a); Li et al. (2025a); Rawles et al. (2025); Li et al. (2024); Gu et al. (2023); He et al. (2024); Lu et al. (2025a) to the optimization of training paradigms Chen et al. (2025). While early works focused on basic feasibility like purely Supervised Finetuning(SFT), recent studies have shifted toward more sophisticated approaches, such as designing rule-based rewards for offline/online reinforcement learning and optimizing token usage for better efficiency. Despite this progress, building an agent that is both universally capable and easy to deploy remains a significant challenge. Building on this momentum, we firstly released UI-Venus-1.0 Gu et al. (2025) not long ago. By relying solely on reinforcement learning, UI-Venus-GD and UI-Venus-Navi achieved previous state-of-the-art (SOTA) results in grounding and mobile navigation tasks, respectively.

While the GUI agent landscape has expanded rapidly, the rapid influx of new GUI agents has escalated performance standards, challenging the dominance of UI-Venus-1.0. Beyond pure performance metrics, we observe a critical discrepancy between step-level and trace-level accuracy during both SFT and offline reinforcement learning phases. This mismatch is largely due to the sparsity of rewards in individual steps and the inherent domain shift between training data and real-world benchmarks. Moreover, we posit that an ideal agent suitable for daily usage should be an end-to-end system that adheres to a simple yet effective design philosophy. To address these challenges, we present UI-Venus-1.5 in this report, a substantially enhanced version of our previous system. Compared to UI-Venus-1.0, UI-Venus-1.5 introduces three key technical advances that jointly improve the final performances:

• Mid-Training Stage: Unlike the previous approach, we have added a comprehensive midtraining stage before the reinforcement learning phase. This stage utilizes an extensive corpus of GUI data, comprising $^ { 3 0 + }$ datasets and a total of 10B tokens. By incorporating this step, we equip the base model with robust inherent GUI knowledge, enabling it to effectively solve GUIrelated VQA, grounding, and simple navigation tasks even before entering the reinforcement learning stage.   
• Scaled Online Reinforcement Learning: Recognizing that Online Reinforcement Learning is a highly effective method for training GUI Agents, we have integrated it into UI-Venus-1.5 specifically for mobile and web scenarios. Inspired by T-GRPO Chen et al. (2025), we perform full trajectory rollouts and reward calculations across different environments, which also contributes to address the challenging step-trace accuracy mismatch problem during GUI

Agent finetuning. By scaling up the interaction devices, we have further improved the model’s performance in complex navigation tasks.

• Unified Single-Agent via Model Merging: A major distinction from UI-Venus-1.0 is that UI-Venus-1.5 is a purely end-to-end model, which greatly simplifies deployment for users. To achieve this, we first conduct finetuning for grounding, web, and mobile domains by using domain-specific reward functions, data, and prompts. Once we obtain these three specialized models, we apply a model merge strategy. This allows us to combine them into a single, unified model with minimal performance loss across individual domains.

We extensively evaluate UI-Venus-1.5 on diverse benchmarks to verify its versatility and robustness. In terms of GUI Grounding, our model establishes a new state-of-the-art on challenging datasets like ScreenSpot-Pro Li et al. (2025a) and VenusBench-GD Zhou et al. (2025a), achieving accuracies of $6 9 . 6 \%$ and $7 5 . 0 \%$ respectively, which substantially surpasses existing strong baselines like Seed1.8 Seed (2025a), Holo2 H-Company (2025) and MAI-UI Zhou et al. (2025b). Furthermore, in dynamic Navigation tasks, UI-Venus-1.5 proves the efficacy of our proposed training pipeline. On the highly competitive AndroidWorld Rawles et al. (2025) benchmark, it attains a success rate of $7 7 . 6 \%$ , outperforming Mobile-Agent-v3 Ye et al. (2025), MAI-UI Zhou et al. (2025b) and StepGUI Yan et al. (2025). When extended to web-based interaction on WebVoyager He et al. (2024), UI-Venus-1.5 achieves $7 6 . 0 \%$ accuracy, closely matching the performance of leading prior baselines. Even when compared to significantly larger models, UI-Venus-1.5 delivers superior efficiency and decision-making accuracy across both grounding and navigation domains.

Beyond achieving state-of-the-art results on standard GUI benchmarks, we place a strong emphasis on the practical utility of UI-Venus-1.5. To this end, we have specifically optimized the model for $^ { 4 0 + }$ Chinese mobile ecosystem, ensuring it can handle a wide array of complex, real-world tasks within third-party applications. These capabilities include, but are not limited to, ticket booking, purchase of goods, and automated conversation management. By mastering these diverse and high-demand scenarios, UI-Venus-1.5 moves closer to becoming a truly helpful digital assistant for everyday life.

# 2 Methodology

System overview: UI-Venus-1.5 is an end-to-end multimodal agent designed to bridge high-level user intentions with concrete GUI interactions across mobile and web platforms. As shown in Figure 2, the system operates via a closed-loop perception-action mechanism: given a natural language command, the model interprets visual screenshots, grounds semantic intentions into executable actions, and iteratively interacts with the environment until task completion. This unified architecture eliminates the need for handcrafted intermediate representations or API integrations, enabling seamless deployment on heterogeneous interfaces. Beyond state-of-the-art benchmark performance, UI-Venus-1.5 demonstrates robust practical applicability, having been validated across a diverse array of real-world applications ranging from media streaming to complex e-commerce platforms. Whether manipulating native mobile apps or navigating dynamic web content, the model exhibits consistent robustness in handling complex, context-dependent workflows, positioning it as a versatile solution for automating daily digital tasks.

Action Spaces: Building upon the foundational action space of UI-Venus-1.0, we expand the model’s capabilities to encompass web-specific interactions. Specifically, we introduce three additional primitives: Hover, DoubleClick, and Hotkey. This augmented action space (Table 8) unifies mobile

![](images/bef2933d8a5079b6f6055ecfe0de2df1a66124f3fa0597f507fd7d291ecaad51.jpg)

![](images/05d4cfb140b3de2316f292f471c21d2067b34f96d028b0e59f3d71506735baf3.jpg)

![](images/1f675e188fd5cb190047fb9f35ffe20e5349fe7ec81b9430701b4fc51e82b6cd.jpg)  
Figure 2 System Overview of UI-Venus-1.5. It operates as an end-to-end GUI Agent that interprets user instructions, perceives interface states through screenshots, and executes interactive actions (e.g., clicking, typing, scrolling) to accomplish tasks across diverse executable environments.

and web interaction modalities, allowing the end-to-end model to execute precise operations across diverse environments.

Overall Training Pipeline: Subsequently, we elaborate on the model’s training process, which is divided into four distinct stages as shown in Figure 3: (1) a Mid-Training phase for knowledge injection using large-scale GUI data in Section 2.1; (2) task-specific Offline-RL training for each of the three objectives in Section 2.2; (3) Online-RL to further enhance the agent’s navigation capabilities in complex, real-world scenarios in Section 2.3; and (4) a model merge strategy to unify the specialized models in Section 2.4.

# 2.1 Mid-Training

# 2.1.1 Motivation and Data Collection

The Mid-Training phase is designed to bridge the semantic gap between general visual perception and the fine-grained structural understanding required by GUI Agents. Specifically, general-purpose vision-language models often lack the granularity needed to capture the structural nuances of user interfaces. In the subsequent reinforcement learning phase, this deficiency severely hinders effective exploration, leading to sparse reward signals and preventing policy improvement from bootstrapping in complex interaction scenarios. This limitation is mainly due to the scarcity of GUI-specific structural modeling in standard pre-training corpora. Consequently, rather than relying solely on capability elicitation, we shift our objective toward foundational representation building. This phase (Mid-Training) enables the model to encode diverse GUI layouts and interaction logic, providing a robust initialization for subsequent policy optimization, which can also be experimentally verified in Section 3.3.

To support the Mid-Training phase, we constructed a unified corpus by aggregating over 30 diverse

![](images/791611a1076d8500703dbae3aac8d5fc798fc5d3dac771ea98f46e560ffe2cb1.jpg)  
Figure 3 The Four-Stage Pipeline of UI-Venus-1.5. Starting from Qwen3-VL Series, the model progresses through a multi-stage curriculum: (1) Mid-Training on large-scale GUI data for domain knowledge injection; (2) Offline-RL for task-specific optimization across grounding, mobile, and web objectives; (3) Online-RL to enhance navigation in complex, real-world settings; and (4) Model Merge, which unifies the specialized models into the final UI-Venus-1.5.

![](images/385ec1e6d6cdd6bdb54872abaee87dc5ba25f670545351725d680f2e8e4624e0.jpg)  
(a) Mid-Training Corpus

![](images/961ce5eac94686c56d81e7f898e95a5b293b75c09edce16f17c8bf7355b9a3e4.jpg)  
(b) Iterative Data Refinement Pipeline   
Figure 4 (a) The inner part represents the functional task categories (e.g., GUI-VQA, Grounding, Perception), while the outer one details the distribution of specific data sources and target platforms (Web, Desktop, Mobile); (b) Iterative data refinement pipeline with teacher scoring, trace rewriting/reconstruction, and manual verification.

sources, including Mind2Web Deng et al. (2023), ShowUI Lin et al. (2024), AITW Rawles et al. (2023) and so on. The hierarchical distribution of this corpus is detailed in Figure 4a. This 10B-token dataset is strategically stratified to ensure functional diversity: semantic perception $( 2 0 . 8 \% )$ and GUI-VQA $( 2 2 . 1 \% )$ provide the representational foundation, while grounding $( 2 4 . 8 \% )$ and hybrid navigation-reasoning tasks ensure execution robustness.

Based on this unified corpus, the Mid-Training data supports four complementary supervision objectives covering perception, reasoning, and action alignment. Specifically, the dataset provides supervisions for:

• Navigation & Grounding: Learning the precise alignment between natural language instructions and executable agent actions.   
• Sequential Reasoning: Generating Chain-of-Thought (CoT) traces that decompose high-level goals into intermediate steps.

![](images/54e34d05efabf8389d51c1f4f139dc93e956a9c2d5436158276eca9543a2b923.jpg)  
Figure 5 Data generation loop via DaaS environment. By iteratively performing this pipeline, the success rate of total trace generation raises from $1 7 . 9 \%$ to over $70 \%$ .

• GUI-VQA: Providing semantic interpretations of GUI components, functional descriptions, and layout logic.   
• Fine-Grained Perception: Capturing detailed attributes of visual elements, including icon recognition, widget state detection, and OCR-free dense captioning.

# 2.1.2 Iterative Data Refinement

With the large scale data we collected for Mid-Training, the next step is to clean and refine the low-quality navigation traces since some open-source datasets often contain noise that can limit performance gains. To address this, we propose a teacher-based quality refinement module to rank, select, and rewrite the Mid-Training data. Specifically, we first utilize Qwen3-VL-235B-A22B Bai et al. (2025a) to evaluate and rank the input data with numerical quality assessments as illustrated in Figure 4b following the LLM-as-a-judge fashion. We chose this model because of its superior generalization and reasoning capabilities among open-source models. Mid-Training samples are scored from 0 to 10 based on action-visual alignment and task reachability according to our carefully designed prompts. Among the results, high-quality traces(score $\geq 7$ ) are retained in gold pool since the goal is accomplished; mid-quality traces(4-6) are routed to a rewriting model to refine the instruction according to the last state; and low-quality samples(0-3) are totally reconstructed or just discarded.

By performing recursive refinements, the proportion of high-fidelity samples in our dataset increased from $6 9 . 7 \%$ to $8 9 . 7 \%$ . Finally, we conduct subsequent manual verification of sampled trajectories from the gold pool and ensure that the training signal remains both dense and accurate.

# 2.1.3 Data Generation Loop

To further improve robustness in real-world environments, we augment the Mid-Training corpus with interaction trajectories collected from real-device execution. Compared with static opensource datasets, real-device interaction data better captures execution failures, GUI dynamics, and environment-dependent behaviors that GUI agents must handle in practice. We therefore build a data generation loop on top of our DaaS system (Section 2.3.2). As illustrated in Figure 5, an open-source MLLM first generates candidate task prompts from seed instructions. After semantic verification

based on embedding similarity, valid and non-duplicate prompts are stored in a task bank and executed by GUI agents on cloud-hosted devices. The system then performs GUI trajectory scraping followed by multi-annotator verification to collect high-quality interaction trajectories. A key feature of this pipeline is its iterative generation loop. Verified trajectories are fed back to the MLLM as in-context examples for subsequent task generation, enabling progressively more executable and realistic task prompts. As a result, the success rate of the trajectory generation pipeline improves from $1 7 . 9 \%$ to over $70 \%$ after several iterations. In total, this real-device generation loop produces more than 30,000 verified interaction trajectories.

# 2.2 Offline Reinforcement Learning

# 2.2.1 Grounding

Reward: Following our previous work, the reward function is composed of two components formally: We first check whether the predicted answer string conforms to a predefined syntax as the format reward $R _ { \mathrm { f o r m a t } }$ . Next, given a screenshot and the instruction, the model must predict a center point that localizes the element. We use the commonly used point-in-box reward noted as $R _ { \mathrm { p o i n t - i n - b o x } }$ to train the model.

Combining all components, the final action-wise reward is computed as:

$$
R = R _ {\text {f o r m a t}} \cdot w _ {1} + R _ {\text {p o i n - i n - b o x}} \cdot w _ {2}, \tag {1}
$$

where $w _ { 1 }$ and $w _ { 2 }$ control the relative importance of format correctness and location precision.

Refusal Samples: A major departure from UI-Venus-1.0 is the modification of our grounding prompts to incorporate what we define as refusal capability. Specifically, when faced with an instruction that refers to an element or icon, not present in the image, the model is trained to return a fixed output of $[ - 1 , - 1 ]$ , refer to our prompt as shown in A.2. Compared to models that strictly output coordinates regardless of the instruction’s validity, this refusal-aware approach is significantly more intelligent and effectively mitigates hallucinations during user interactions.

Although the introduction of refusal prompts may lead to a marginal performance trade-off on benchmarks lacking refusal examples (such as ScreenSpot-Pro Li et al. (2025a)), UI-Venus-1.5 nevertheless maintains its state-of-the-art (SOTA) standing. Furthermore, on benchmarks that explicitly include refusal tasks—such as VenusBench-GD Zhou et al. (2025a), and OSWorld-G-Refine Xie et al. (2025b), our model achieves new SOTA results, particularly demonstrating superior accuracy on refusal-specific samples.

# 2.2.2 Navigation

In this section, we detail the Offline-RL formulation and empirical observations across Mobile and Web navigation tasks. In reinforcement learning, a well-designed and robust reward system is essential for stable policy optimization. Despite the differences between Mobile and Web platforms, GUI agents typically share a substantially overlapping action space allowing for a unified reward design across both domains.

Reward: To ensure the agent model generates structured, executable outputs, we build upon our prior UI-Venus-1.0 Gu et al. (2025) framework and adopt a decoupled reward system comprising two primary components: (i) a format reward and (ii) an action reward.

• Format reward $R _ { \mathrm { f o r m a t } }$ : This component ensures the agent model follows a predefined XMLbased template. Specifically, the agent is rewarded for enclosing its response within <think>, <action>, and <conclusion> tags, which represent the reasoning process, the GUI action, and a concise action summary, respectively.   
• Action reward $R _ { \mathrm { a c t i o n } }$ : The primary objective of the action reward is to encourage the model to predict valid and contextually appropriate actions for the current step. It is decomposed into two parts: an action-type reward $R _ { \mathrm { t y p e } }$ and either a content-related reward $R _ { \mathrm { c o n t e n t } }$ or a coordinate-related reward $R _ { \mathrm { c o o r d } }$ . Specifically, $R _ { \mathrm { t y p e } }$ is a binary reward determined by whether the predicted action type matches the ground-truth type. $R _ { \mathrm { c o n t e n t } }$ is applied to text-based actions and is computed as the token-level F1-score between the predicted and ground-truth content. For $R _ { \mathrm { c o o r d } }$ , we adopt a hierarchical reward strategy that gradually relaxes the tolerance on coordinate errors, smoothing the reward scale and reducing the difficulty of policy optimization.

Compared to the UI-Venus-1.0 baseline, we enhance navigation performance in web environments by introducing several specialized GUI actions, such as Hover and Hotkey. Furthermore, we implement domain-specific constraints for the Scroll action to align with the different operational logics of each platform: in mobile tasks, the model must predict precise start and end coordinates, whereas in web tasks, it is only required to specify the scrolling direction.

Overall, the total reward $R$ is formulated as:

$$
R = w _ {1} \cdot R _ {\text {f o r m a t}} + w _ {2} \cdot R _ {\text {a c t i o n}}, \tag {2}
$$

where $w _ { 1 }$ and $w _ { 2 }$ control the trade-off between the format reward and the action reward.

![](images/6c8744821036e6fbebd9ddaad46403e4d1225078e58010f76d5117a929566349.jpg)  
(a) Mobile Scenario

![](images/670808fdd20339b3e0f0399b48d525161f4007ffc58ffa9c3f5521636d1b78d0.jpg)  
(b) Web Scenario   
Figure 6 Step vs. trace success rates during Offline-RL training in (a) Mobile and (b) Web scenarios. We show the performance of training iterations on mobile and web benchmarks with two curves. The dashed line marks the peak trace-level success rate.

Discrepancy Between Step and Trace Success Rates: We use the above reward system for stable Offline-RL. However, we observe a notable trend during Offline-RL training. As shown in Figure 6, while step-level success rates increase steadily, trace-level success rates eventually peak and then decline. We attribute this behavior to an inherent limitation of Offline-RL: step-level rewards only optimize individual actions and fail to guide the successful composition of a full multi-step trace. To improve the deployable performance of the model, we therefore append an online reinforcement learning stage after the Offline-RL, explicitly optimizing for trace-level rewards and substantially enhancing the model’s end-to-end task completion.

# 2.3 Online Reinforcement Learning

# 2.3.1 Motivation

While SFT and Offline-RL provide a solid initialization for GUI agents, their effectiveness is inherently constrained by existing static datasets and predefined interaction distributions. In realworld GUI environments, agents are required to navigate dynamic GUI states, stochastic system behaviors, and extended decision-making horizons, where real-time feedback during execution is critical to performance. Pure offline training is insufficient to address these challenges. Online Reinforcement Learning(Online-RL) responds to these limitations by enabling the agent to learn and adapt in real time through direct interaction with the environment. This allows for rich and immediate feedback and better handling of uncertainties in dynamic settings especially in long interaction sequences. Consequently, policies trained solely offline often exhibit brittleness when deployed in novel GUI layouts or unexpected intermediate states. These limitations are further corroborated by the inconsistencies in step-trace accuracy observed in Section 2.2.

To address these limitations, we introduce online reinforcement learning as a complementary training paradigm. By enabling direct environmental interaction, Online-RL enables the agent to collect trajectories that reflect the actual deployment distribution and to iteratively refine and update its policy based on observed feedback. This leads to the design of a dedicated online learning framework, which comprises a robust execution infrastructure called DaaS (Section 2.3.2), comprehensive task generation and reward formulations (Section 2.3.3), and a stable RL training algorithm (Section 2.3.4).

# 2.3.2 Device as a Service (DaaS)

Training and deploying a GUI Agent capable of generalizing across heterogeneous devices imposes stringent demands on the underlying execution environment in terms of uniformity, extensibility, and performance. Unlike simulators designed for a single device category, such an environment must accommodate a wide variety of device types, offer a unified abstraction over diverse interaction protocols, and—under strict network-isolation policies, securely and efficiently expose large-scale device resources to upstream training and deployment frameworks. Therefore, we build a unified Device-as-a-Service (DaaS) layer (Figure 7) to meet these requirements. It consists of two core components: the Group Control Gateway (GCGW) and the Unified Client SDK, whose design and implementation are detailed next.

Group Control Gateway (GCGW). The GCGW serves as a high-performance centralized reverse proxy and the orchestration core of the DaaS layer. It abstracts heterogeneous control protocols across diverse platforms—including Android (ADB), Chrome (CDP), and Linux containers (SSH)—enabling extensible support through a protocol-centric abstraction.

To ensure system stability and performance under high-throughput workloads, the GCGW integrates several key architectural optimizations. First, to handle stateful protocols like ADB and CDP which rely on long-lived connections, the GCGW employs an internal secondary hash routing algorithm. This mechanism ensures that all requests for a specific device are consistently routed to the same gateway node, effectively preventing the $^ { 6 6 } M \times N$ connection explosion” problem $M$ gateway nodes and $N$ devices) and significantly reducing the connection overhead per node. To support this routing strategy without sacrificing performance, the gateway utilizes streaming transmission and zero-copy I/O for internal forwarding between nodes, ensuring near-zero additional latency. Furthermore, the entire GCGW architecture is built on a high-concurrency coroutine model. This design is specifically

![](images/efd1ac49928a05ee50fb29d79fc494b3e6c54ee28f7bf1b6a795ba71865d47b7.jpg)  
Figure 7 Architecture of the Unified Device-as-a-Service (DaaS) layer. This framework bridges upstream tasks (Training and Inference) with downstream heterogeneous device clusters (Chrome, Mobile, and Desktop). The Multi-language DaaS SDK provides a unified abstraction for diverse interaction protocols, while the Group Control Gateway (GCGW) ensures high-performance and secure resource exposure through secondary hash routing, zero-copy I/O, and a multi-protocol reverse proxy.

tailored for the “high-concurrency, low-frequency” access patterns of device operations, allowing the system to maintain hundreds of thousands of concurrent connections with minimal memory overhead.

Unified Client SDK. To further shield downstream users from the complexities of infrastructure management, a multi-language Unified Client SDK was developed that acts as a high-level API layer atop the GCGW. This SDK encapsulates several critical functions into a streamlined workflow. Specifically, it automates device lifecycle management, including device preemption, heartbeat maintenance, and resource release. Furthermore, it provides a unified semantic interaction interface that standardizes communication across various internal protocols. By abstracting these lowlevel operations, the SDK significantly lowers integration barriers, allowing downstream teams to concentrate on building and operating the end-to-end training pipeline for large-scale online reinforcement learning of GUI-specialized models, as well as the production deployment of those GUI-focused models—rather than dealing with protocol-specific technicalities.

By implementing these architectural optimizations, the DaaS layer achieves the following performance benchmarks:

• Scale and Throughput: The system successfully integrates thousands of heterogeneous devices, establishing a resilient architecture that processes millions of operation requests daily.   
• Resource Allocation Efficiency: Device resource allocation and scheduling achieve millisecondlevel responsiveness, enabling rapid elastic provisioning.   
• High-Concurrency Support: The system has successfully supported large-scale reinforcement learning training tasks involving hundreds to thousands of concurrent devices, which demonstrated superior stability and extensibility under high-load conditions.

# 2.3.3 Task Formulation and Reward Design

Ahead of the training principles and pipeline of online-RL, we introduce task formulation and reward design which are fundamental to the success of online-RL. The quality, diversity, and calibrated difficulty of the input tasks define the potential ceiling of policy optimization, while the specialized reward function serves as the primary driver for training efficiency and stability.

Task Generation and Stratified Sampling: The performance ceiling of online-RL is fundamentally governed by the diversity and quality of its task pool $\tau$ . To this end, we employ a hybrid generation strategy combining static heuristics with dynamic evolution:

• Static Task Library via LLM: For a predefined set of applications $\mathcal { A }$ and target websites $\mathcal { W }$ , we leverage Large Language Models to extract functional maps and generate common tasks covering core user flows.   
• Dynamic Trajectory-based Generation via MLLM: To capture long-tail interaction patterns, we randomly sample screenshots $s _ { t }$ from offline trajectories $\tau$ and use MLLMs to infer plausible task query $q ^ { \prime }$ from the observed state. To maintain task uniqueness, each newly generated goal is filtered by a deduplication function $\psi ( \cdot )$ :

$$
\mathcal {T} _ {\text {n e w}} = \left\{q ^ {\prime} \mid \psi \left(q ^ {\prime}, \mathcal {T} _ {\text {p o o l}}\right) <   \epsilon \right\}, \tag {3}
$$

where $\epsilon$ is a semantic similarity threshold that promotes uniform coverage of the task space.

• Stratified Sampling: We stratify tasks by difficulty, which correlates positively with the minimum steps to completion. Tasks are bucketed based on expected step count $N _ { s t e p s }$ into: Easy $( N _ { s t e p s } \leq 1 0 )$ ), Medium $( 1 0 < N _ { s t e p s } \leq 2 0 )$ , and Hard $( N _ { s t e p s } > 2 0 )$ . During each training iteration, batches are sampled proportionally from these three buckets to support structured curriculum learning.

Reward: To guide the agent effectively in complex GUI environments, we design a composite reward function $R$ . For a given execution trajectory $\tau = ( a _ { 0 } , a _ { 1 } , \dots , a _ { T } )$ with $T$ steps, the total reward consists of a task completion reward $R _ { c o m p }$ , an action constraint penalty $R _ { p }$ , and a trace length decay coefficient $\eta \in ( 0 , 1 ]$ :

$$
R (\tau) = \mathbb {1} _ {\text {s u c c e s s}} \cdot R _ {\text {c o m p}} \cdot \eta^ {\frac {T - T _ {\min }}{T _ {\min }}} + \sum_ {t = 0} ^ {T} R _ {p} \left(a _ {t}\right), \tag {4}
$$

where $T _ { \mathrm { m i n } }$ is the minimum number of steps to success among a group of trajectories collected during the online RL process. Specifically, to encourage the agent to learn the shortest operational path, we introduce a decay coefficient $\eta$ . A larger step count $T$ results in a lower final reward, thereby suppressing redundant or circular actions during policy gradient optimization. Another important factor of GUI Agent is to generate the correct actions in the predefined action pool, i.e., the agent’s output must adhere to specific syntactic specifications. If the agent’s generated response cannot be recognized by the parser as a valid action, a negative penalty $\lambda$ is assigned at the current step. The penalty term is defined as:

$$
R _ {p} \left(a _ {t}\right) = \left\{ \begin{array}{l l} - \lambda , & \text {i f} a _ {t} \text {i s u n p a r s a b l e} \\ 0, & \text {o t h e r w i s e} \end{array} \right. \tag {5}
$$

By incorporating $R _ { p }$ , we significantly reduce the number of invalid attempts during the online exploration phase, thereby improving sample efficiency.

After that, we implement a dual-track verification mechanism to determine task success (1success):

• Rule-based Verification: For tasks with clear system-side outcomes (e.g., URL redirection, specific file generation, or system setting changes), success is verified deterministically by querying low-level system APIs.   
• MLLM-as-a-Judge: For semantically ambiguous tasks where visual feedback is prominent, the initial task $q$ and the final keyframe screenshot $s _ { i }$ are fed into an MLLM to judge whether the logical intent has been satisfied.

# 2.3.4 Training Algorithm

We employ the Group Relative Policy Optimization (GRPO) algorithm. Unlike the conventional Actor-Critic framework, GRPO estimates relative advantages directly from a group of sampled trajectories, thereby bypassing the need for a separate value function network. This approach substantially reduces computational complexity and effectively addresses the convergence challenges posed by sparse reward signals in GUI-based tasks.

In each training step, for a task $q$ sampled from the task pool, the agent generates a group of $G$ complete interaction trajectories $\{ \tau _ { i } \} _ { i = 1 } ^ { G }$ using the current policy $\pi _ { \theta _ { o l d } }$ . The GRPO loss function $L _ { G R P O } ( \theta )$ is defined as follows:

$$
L _ {G R P O} (\theta) = - \frac {1}{G} \sum_ {i = 1} ^ {G} \frac {1}{| \tau_ {i} |} \sum_ {t = 1} ^ {| \tau_ {i} |} \min  \left(r _ {i, t} (\theta) \hat {A} _ {i}, \operatorname {c l i p} (r _ {i, t} (\theta), 1 - \epsilon , 1 + \epsilon) \hat {A} _ {i}\right), \tag {6}
$$

where $\begin{array} { r } { r _ { i , t } ( \theta ) = \frac { \pi _ { \theta } ( a _ { i , t } | s _ { i , t } , q ) } { \pi _ { \theta _ { o l d } } ( a _ { i , t } | s _ { i , t } , q ) } } \end{array}$ πθ(ai,t|si,t,q) denotes the importance sampling ratio between the new and old policies at the action (or token) level.

Trajectory-level Advantage Calculation and Assignment: Given the long execution horizons of GUI tasks and the difficulty in identifying critical actions, we forgo step-wise reward signals in favor of evaluating the overall quality of each complete trajectory $\tau _ { i }$ . The trajectory-level advantage ${ \hat { A } } _ { i }$ is derived by normalizing relative scores within the sampled group:

$$
\hat {A} _ {i} = \frac {R \left(\tau_ {i} , q\right) - \operatorname {m e a n} \left(\left\{R \left(\tau_ {j} , q\right) \right\} _ {j = 1} ^ {G}\right)}{\operatorname {s t d} \left(\left\{R \left(\tau_ {j} , q\right) \right\} _ {j = 1} ^ {G}\right) + \epsilon}, \tag {7}
$$

where $R ( \tau _ { i } , q )$ is the composite reward defined in Section 2.3.3 (incorporating task success rewards and invalid action penalties). The calculated ${ \hat { A } } _ { i }$ is uniformly assigned to all action steps within the trajectory. By relying on competition within the sampled group, this approach filters out environmental stochasticity and supplies a stable credit assignment signal, thereby supporting stable policy updates in long-horizon decision-making.

Training Stability and Exploration Enhancement: Rewards in GUI navigation are both sparse and costly to verify, which can lead to policy collapse during extended online training. To mitigate these issues, we implement two complementary regularization mechanisms:

• Adaptive KL Constraint: To prevent the model from losing the fundamental GUI manipulation capabilities (e.g., basic clicking and swiping logic) acquired during SFT or Offline-RL, we incorporate a KL divergence penalty between the current policy $\pi _ { \theta }$ and reference policy $\pi _ { r e f }$ :

$$
L _ {K L} (\theta) = \beta \mathbb {D} _ {K L} \left(\pi_ {\theta} \| \pi_ {r e f}\right). \tag {8}
$$

To prevent the reference policy from becoming a stationary constraint that limits progress, we update it adaptively. When the current policy outperforms $\pi _ { r e f }$ on a held-out validation set by a margin $\delta$ , we smoothly blend the two policies:

$$
\pi_ {r e f} \leftarrow (1 - \alpha) \pi_ {r e f} + \alpha \pi_ {\theta}. \tag {9}
$$

This allows the KL penalty to dynamically track the policy’s improvement, preserving stability while allowing continued optimization.

• Annealed Entropy Regularization: After SFT or Offline-RL, policies often become overly deterministic, hampering exploration early in online training. We encourage action diversity via an entropy term:

$$
L _ {\text {e n t r o p y}} (\theta) = - \lambda_ {t} \mathbb {H} \left(\pi_ {\theta} (\cdot | s, q)\right). \tag {10}
$$

To avoid divergence from sustained high entropy, we anneal the coefficient $\lambda _ { t }$ exponentially with training steps $k$ :

$$
\lambda_ {t} = \lambda_ {0} \cdot \sigma^ {k}, \quad \sigma \in (0, 1).
$$

By maintaining a high $\lambda _ { t }$ to trigger exploration in the early stages and gradually reducing the weight to converge toward an optimal deterministic policy, this method effectively balances exploration and exploitation.

The final total optimization objective for the Online-RL stage is:

$$
J (\theta) = L _ {G R P O} (\theta) - L _ {K L} (\theta) + L _ {\text {e n t r o p y}} (\theta). \tag {11}
$$

# 2.4 Model Merge

After offline-RL and online-RL phases, we implement a model merge Li et al. (2023); DeepResearch et al. (2025); Ling-Team et al. (2025a) strategy to consolidate the specialized expertise of our taskspecific models into a single, unified GUI Agent. This approach leverages the principle that models fine-tuned from a common foundational ancestor occupy a shared parameter space, allowing for their weights to be integrated through strategic interpolation. Specifically, we explored two distinct merging paradigms as follows: Linear Merge Li et al. (2023) and TIES-Merge Yadav et al. (2023).

Linear Merge: We take the checkpoints optimized for grounding, web, and mobile navigation, and synthesize them into a global parameter set $\theta _ { l i n e a r }$ using a weighted combination:

$$
\theta_ {\text {l i n e a r}} = \sum_ {i = 1} ^ {3} w _ {i} \cdot \theta_ {i}, \quad \text {s u b j e c t t o} \quad \sum_ {i = 1} ^ {3} w _ {i} = 1, \tag {12}
$$

where $\theta _ { i }$ denotes the parameters of the $i$ -th specialized model and $w _ { i }$ represents its relative importance in the fusion process.

TIES-Merge: Compared to standard linear merging, TIES-Merge reduces parameter interference through two key steps. First, it calculates task vectors (differences between fine-tuned models and the base model) and prunes low-magnitude updates to retain only the most significant changes. Second, before merging, it elects a dominant sign direction for each parameter and aggregates only updates aligned with that direction. By pruning noisy updates and resolving sign conflicts, TIES-Merge achieves markedly lower performance regression than simple interpolation.

Performance comparison: According to our experiments in Section 3.4, TIES-Merge always performs better than Linear Merge. Take our UI-Venus-1.5-30B-A3B for example, it achieves $7 1 . 0 \%$

and $7 5 . 5 \%$ accuracy on ScreenSpot-Pro and AndroidWorld before Model Merging, respectively. By adopting Linear Merge, the performances drop $2 . 9 \% \downarrow$ and $2 . 3 \% \downarrow$ . Refer to the experiment results of TIES-Merging in Table 7, i.e. $6 9 . 6 \% ( 1 . 4 \% \downarrow )$ and $7 7 . 6 \% ( 2 . 1 \% \uparrow )$ , it significantly outperforms Linear Merge in the context of cross-task fusion. Note that although model merging may lead to performance drop of some tasks compared to domain-specific models, the resulting UI-Venus-1.5 achieves a harmonious balance across all three domains, delivering robust performance without the computational overhead of training a multi-task model from scratch.

# 3 Experiments

Table 1 Performance comparison on various Grounding Benchmarks. For each benchmark, the best and second-best performing models are indicated in bold and underlined, respectively. “*” indicates results that may require verification with original sources.   

<table><tr><td rowspan="2">Models</td><td colspan="7">Grounding Benchmarks</td></tr><tr><td>VenusBench-GD</td><td>ScreenSpot-Pro</td><td>ScreenSpot-V2</td><td>MMbench</td><td>OSworld-G-R</td><td>OSworld-G</td><td>UI-Vision</td></tr><tr><td colspan="8">General VLMs</td></tr><tr><td>Seed1.8 (Seed, 2025a)</td><td>-</td><td>64.3</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>Qwen3-VL-2B* (Bai et al., 2025a)</td><td>45.2</td><td>40.6</td><td>85.6</td><td>69.5</td><td>60.6</td><td>47.7</td><td>13.1</td></tr><tr><td>Qwen3-VL-8B* (Bai et al., 2025a)</td><td>55.1</td><td>52.7</td><td>92.1</td><td>81.4</td><td>67.0</td><td>57.5</td><td>21.9</td></tr><tr><td>Qwen3-VL-30B-A3B* (Bai et al., 2025a)</td><td>52.4</td><td>53.7</td><td>91.7</td><td>83.7</td><td>69.3</td><td>61.2</td><td>25.6</td></tr><tr><td colspan="8">GUI-specific Models</td></tr><tr><td>OpenCUA-7B (Wang et al., 2025b)</td><td>48.2</td><td>50.0</td><td>92.3</td><td>-</td><td>-</td><td>55.3</td><td>29.7</td></tr><tr><td>OpenCUA-32B (Wang et al., 2025b)</td><td>50.1</td><td>55.3</td><td>93.4</td><td>-</td><td>70.2</td><td>59.6</td><td>33.3</td></tr><tr><td>OpenCUA-72B (Wang et al., 2025b)</td><td>-</td><td>60.8</td><td>92.9</td><td>-</td><td>-</td><td>-</td><td>37.3</td></tr><tr><td>GTA1-7B (Yang et al., 2025)</td><td>46.4</td><td>50.1</td><td>92.4</td><td>-</td><td>67.7</td><td>60.1</td><td>-</td></tr><tr><td>GTA1-32B (Yang et al., 2025)</td><td>58.8</td><td>63.6</td><td>95.2</td><td>-</td><td>72.2</td><td>65.2</td><td>-</td></tr><tr><td>GUI-Owl-7B (Ye et al., 2025)</td><td>-</td><td>54.9</td><td>92.8</td><td>80.5</td><td>-</td><td>55.9</td><td>-</td></tr><tr><td>GUI-Owl-32B (Ye et al., 2025)</td><td>-</td><td>58.0</td><td>93.1</td><td>83.0</td><td>-</td><td>58.0</td><td>-</td></tr><tr><td>UI-TARS-1.5-7B (Seed, 2025b)</td><td>40.7</td><td>35.7</td><td>91.6</td><td>64.3</td><td>64.2</td><td>52.8</td><td>22.3</td></tr><tr><td>UI-Venus-1.0-7B (Gu et al., 2025)</td><td>49.0</td><td>50.8</td><td>94.1</td><td>79.9</td><td>61.7</td><td>54.6</td><td>26.5</td></tr><tr><td>UI-Venus-1.0-72B (Gu et al., 2025)</td><td>70.2</td><td>61.9</td><td>95.3</td><td>86.3</td><td>69.5</td><td>62.2</td><td>36.8</td></tr><tr><td>Holo2-8B (H-Company, 2025)</td><td>56.4*</td><td>58.9</td><td>93.2</td><td>84.5*</td><td>70.1</td><td>63.5*</td><td>35.1*</td></tr><tr><td>Holo2-30B-A3B (H-Company, 2025)</td><td>59.5*</td><td>66.1</td><td>94.9</td><td>86.8*</td><td>76.1</td><td>65.2*</td><td>40.9*</td></tr><tr><td>Step-GUI-4B (Yan et al., 2025)</td><td>54.6*</td><td>60.0</td><td>93.6</td><td>84.0</td><td>66.9</td><td>60.5*</td><td>30.0*</td></tr><tr><td>Step-GUI-8B (Yan et al., 2025)</td><td>-</td><td>62.6</td><td>95.1</td><td>85.6</td><td>70.0</td><td>-</td><td>-</td></tr><tr><td>MAI-UI-2B (Zhou et al., 2025b)</td><td>55.4*</td><td>57.4</td><td>92.5</td><td>82.6</td><td>63.5</td><td>52.0</td><td>30.3</td></tr><tr><td>MAI-UI-8B (Zhou et al., 2025b)</td><td>65.2*</td><td>65.8</td><td>95.2</td><td>88.8</td><td>68.6</td><td>60.1</td><td>40.7</td></tr><tr><td>MAI-UI-32B (Zhou et al., 2025b)</td><td>-</td><td>67.9</td><td>96.5</td><td>91.3</td><td>73.9</td><td>67.6</td><td>47.1</td></tr><tr><td colspan="8">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>67.3</td><td>57.7</td><td>92.8</td><td>80.3</td><td>65.6</td><td>59.4</td><td>44.8</td></tr><tr><td>UI-Venus-1.5-8B</td><td>72.3</td><td>68.4</td><td>95.9</td><td>88.1</td><td>74.1</td><td>69.7</td><td>46.5</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>75.0</td><td>69.6</td><td>96.2</td><td>88.6</td><td>76.4</td><td>70.6</td><td>54.7</td></tr></table>

# 3.1 Experimental Setup

# 3.1.1 Implementation details

UI-Venus-1.5 incorporates the Qwen3-VL Bai et al. (2025a) architecture as its core backbone, leveraging its advanced multimodal processing capabilities to interpret complex visual interfaces. Note that we map all spatial targets into a normalized [0, 1000] coordinate space following Qwen3- VL and unifies diverse events into a shared set of action space as shown in Table 8.

Note that methods marked with * indicate our own reproductions with official prompts, some of which achieve superior performance compared to their original reported results. Moreover, all methods evaluated in this section follow the end-to-end design without any zoom-in or agentframework strategies except specially mentioned.

# 3.1.2 Benchmarks

Grounding: We evaluate the model’s grounding capabilities with seven complementary benchmarks: VenusBench-GD Zhou et al. (2025a) for its assessment of high-level reasoning and refusal capabilities, ScreenSpot-Pro Wu et al. (2024) focuses on high-resolution, fine-grained professional layouts, UI-Vision Nayak et al. (2025) assesses reasoning abilities (e.g., spatial and functional) in diverse applications, MMBench-GUI L2 Wang et al. (2025c) evaluates hierarchical-instruction following and compositional reasoning, OSWorldG and OSWorld-G Refine Xie et al. (2025b) jointly assess comprehensive skills such as layout understanding, widget matching, and fine-grained manipulation, and ScreenSpot-V2 Wu et al. (2024) serves to broaden coverage across different operating systems.

Navigation: We first evaluated UI-Venus-1.5 on two widely-adopted online mobile benchmarks: AndroidWorld Rawles et al. (2025) and Androidlab Xu et al. (2025), based on a live Android emulator with various applications and tasks. In addition, we also performed experiments on VenusBench-Mobile, a more challenging benchmark whose tasks are more related to real-world human applications. To further validate the cross-domain versatility of UI-Venus-1.5, we extended our evaluation to real-world web environments. We evaluate our model on a representative subset of WebVoyager He et al. (2024), as the full benchmark is time-consuming to evaluate and some time-sensitive tasks are no longer valid.

# 3.2 Main Results

# 3.2.1 Grounding Benchmarks

In the experiments, we compare UI-Venus-1.5 models against various state-of-the-art baselines across two different model categories: (1) General VLMs: Seed1.8 Seed (2025a) and widely used Qwen3-VL Bai et al. (2025a). (2) GUI-specific Models: OpenCUA Wang et al. (2025b), UI-TARS-1.5 Seed (2025b), GTA1 Yang et al. (2025), Gui-Owl Ye et al. (2025), Holo2 H-Company (2025), Step-GUI Yan et al. (2025) and MAI-UI Zhou et al. (2025b).

VenusBench-GD. VenusBench-GD is a comprehensive grounding benchmark spanning web, desktop, and mobile UIs, covering both basic localization and advanced, reasoning-heavy cases, and further includes refusal grounding to test whether agents can correctly reject infeasible instructions. As shown in Table 1, UI-Venus-1.5 achieves strong and scalable performance, with our 30B-A3B model reaching $7 5 . 0 \%$ and outperforming competitive GUI-specialized baselines.

ScreenSpot-Pro. ScreenSpot-Pro focuses on high-resolution professional software interfaces (e.g., CAD, development tools, creative suites, and office applications), where dense layouts and small icons make fine-grained grounding particularly challenging. In Table 1, UI-Venus-1.5-30B-A3B achieves the best overall accuracy at $6 9 . 6 \%$ , exceeding the strongest reported baseline MAI-UI-32B $( 6 7 . 9 \% )$ and showing clear gains over smaller UI-Venus-1.5 variants $5 7 . 7 \%$ for 2B, $6 8 . 4 \%$ for 8B).

ScreenSpot-V2. ScreenSpot-V2 is a broad cross-platform grounding benchmark covering mobile, web, and desktop UIs with both text and icon/widget targets, reflecting everyday GUI interaction scenarios. As shown in Table 1, UI-Venus-1.5 achieves strong performance, with 30B-A3B reaching $9 6 . 2 \%$ (second-best, $0 . 3 \%$ behind MAI-UI-32B) and 8B reaching $9 5 . 9 \%$ , demonstrating robust generalization even in a near-saturated benchmark.

MMBench-GUI L2. MMBench-GUI L2 evaluates instruction-following grounding with both Basic (low-level attributes) and Advanced (goal-oriented, compositional) instructions, testing a model’s ability to align implicit user intent with the correct UI element. In Table 1, UI-Venus-1.5 remains

competitive, reaching $8 8 . 6 \%$ with 30B-A3B.

OSWorld-G. OSWorld-G(and its refined split OSWorld-G-R) contains fine-grained desktop grounding tasks that require diverse skills such as text matching, widget recognition, layout understanding, and precise manipulation. Table 1 shows UI-Venus-1.5-30B-A3B achieves state-of-the-art performance on both settings, reaching $7 6 . 4 \%$ on OSWorld-G-R and $7 0 . 6 \%$ on OSWorld-G, surpassing strong baselines such as MAI-UI-32B $( 7 3 . 9 \% / 6 7 . 6 \% )$ and GTA1-32B $( 7 2 . 2 \% / 6 5 . 2 \% )$ .

UI-Vision. UI-Vision is a license-permissive benchmark for desktop GUI grounding that emphasizes real-world applications and fine-grained reasoning (e.g., spatial and functional understanding). As shown in Table 1, UI-Venus-1.5-30B-A3B achieves the strongest result at $5 4 . 7 \%$ , substantially outperforming prior GUI-specific baselines (e.g., MAI-UI-32B at $4 7 . 1 \%$ ).

In summary, our evaluation reveals several key insights:

• Strong Overall Grounding: UI-Venus-1.5-30B-A3B achieves state-of-the-art results on most benchmarks, leading VenusBench-GD $( 7 5 . 0 \% )$ , ScreenSpot-Pro $( 6 9 . 6 \% )$ , OSWorld-G-R $( 7 6 . 4 \% )$ , OSWorld-G $( 7 0 . 6 \% )$ , and UI-Vision $( 5 4 . 7 \% )$ , while remaining highly competitive on ScreenSpot-V2 ( $9 6 . 2 \%$ , second-best, $0 . 3 \%$ behind MAI-UI-32B).   
• Consistent Scaling Gains: Increasing model scale yields steady improvements across all benchmarks (e.g., ScreenSpot-Pro: $5 7 . 7 \%  6 8 . 4 \%  6 9 . 6 \%$ for 2B/8B/30B-A3B).   
• Broad Generalization Across Tasks: UI-Venus shows robust performance on diverse grounding settings, from refusal-aware evaluation in VenusBench-GD to fine-grained professional UI layouts in ScreenSpot-Pro, and remains competitive on instruction-intensive MMBench $( 8 8 . 6 \% )$ .

Table 2 Performance comparison on AndroidWorld for end-toend models.   

<table><tr><td>Models</td><td>Params.</td><td>Success Rate</td></tr><tr><td colspan="3">General VLMs</td></tr><tr><td>Qwen3-VL-2B (Bai et al., 2025a)</td><td>2B</td><td>36.4</td></tr><tr><td>Qwen3-VL-8B (Bai et al., 2025a)</td><td>8B</td><td>47.6</td></tr><tr><td>Qwen3-VL-30B-A3B (Bai et al., 2025a)</td><td>30B</td><td>54.3</td></tr><tr><td>GLM-4.6V (V-Team et al., 2025)</td><td>106B</td><td>57.0</td></tr><tr><td>Gemini-2.5-Pro (Comanici et al., 2025)</td><td>-</td><td>69.7</td></tr><tr><td>Seed1.8 (Seed, 2025a)</td><td>-</td><td>70.7</td></tr><tr><td colspan="3">GUI-specific Models</td></tr><tr><td>UI-TARS-1.5-7B (Seed, 2025b)</td><td>7B</td><td>30.0</td></tr><tr><td>GUI-Owl-7B (Ye et al., 2025)</td><td>7B</td><td>66.4</td></tr><tr><td>UI-TARS-72B (Qin et al., 2025)</td><td>72B</td><td>46.6</td></tr><tr><td>UI-Venus-1.0-7B (Gu et al., 2025)</td><td>7B</td><td>49.1</td></tr><tr><td>UI-Venus-1.0-72B (Gu et al., 2025)</td><td>72B</td><td>65.9</td></tr><tr><td>Step-GUI-4B (Yan et al., 2025)</td><td>4B</td><td>63.9</td></tr><tr><td>Step-GUI-8B (Yan et al., 2025)</td><td>8B</td><td>67.7</td></tr><tr><td>Holo2-8B (H-Company, 2025)</td><td>8B</td><td>60.4</td></tr><tr><td>Holo2-30B-A3B (H-Company, 2025)</td><td>30B</td><td>71.6</td></tr><tr><td>MAI-UI-2B (Zhou et al., 2025b)</td><td>2B</td><td>49.1</td></tr><tr><td>MAI-UI-8B (Zhou et al., 2025b)</td><td>8B</td><td>70.7</td></tr><tr><td>MAI-UI-32B (Zhou et al., 2025b)</td><td>32B</td><td>73.3</td></tr><tr><td colspan="3">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>2B</td><td>55.6</td></tr><tr><td>UI-Venus-1.5-8B</td><td>8B</td><td>73.7</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>30B</td><td>77.6</td></tr></table>

Table 3 Performance comparison on AndroidLab. Note that * indicates that the results are evaluated by us; † denotes results that have been manually verified by humans.   

<table><tr><td>Models</td><td>Params.</td><td>Success Rate</td></tr><tr><td colspan="3">General VLMs</td></tr><tr><td>Gemini-1.5-Pro (Gemini-Team et al., 2024)</td><td>-</td><td>16.7</td></tr><tr><td>GLM4-9B-ft (GLM et al., 2024)</td><td>9B</td><td>21.0</td></tr><tr><td>LLaMA3.1-ft (Grattaftiori et al., 2024)</td><td>8B</td><td>23.9</td></tr><tr><td>GPT-4o (Hurst et al., 2024)</td><td>-</td><td>31.2</td></tr><tr><td>Qwen3-VL-2B* (Bai et al., 2025a)</td><td>2B</td><td>33.3</td></tr><tr><td>Qwen3-VL-8B* (Bai et al., 2025a)</td><td>8B</td><td>43.5</td></tr><tr><td>Qwen3-VL-30B-A3B* (Bai et al., 2025a)</td><td>30B</td><td>42.0</td></tr><tr><td colspan="3">GUI-specific Models&amp;Frameworks</td></tr><tr><td>V-Droid (Dai et al., 2025)</td><td>8B</td><td>38.3</td></tr><tr><td>UI-Genie (Xiao et al., 2025)</td><td>72B</td><td>41.2</td></tr><tr><td>MobileUse (Li et al., 2025b)</td><td>72B</td><td>44.2</td></tr><tr><td>UI-Venus-1.0-7B (Gu et al., 2025)</td><td>7B</td><td>41.3</td></tr><tr><td>UI-Venus-1.0-72B (Gu et al., 2025)</td><td>72B</td><td>49.3</td></tr><tr><td>AutoGLM-Mobile (Liu et al., 2024)</td><td>9B</td><td>46.8</td></tr><tr><td>AutoGLM-Multilingual (Liu et al., 2024)</td><td>9B</td><td>47.7</td></tr><tr><td>Step-GUI-4B* (Yan et al., 2025)</td><td>4B</td><td>47.8</td></tr><tr><td colspan="3">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>2B</td><td>36.2/44.2†</td></tr><tr><td>UI-Venus-1.5-8B</td><td>8B</td><td>55.1/68.1†</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>30B</td><td>52.9/68.1†</td></tr></table>

# 3.2.2 Navigation Benchmarks

In addition to evaluating GUI grounding capabilities, we further assess the UI-Venus-1.5 series on four navigation benchmarks spanning both mobile and web environments, including Android World Rawles et al. (2025), Android Lab Xu et al. (2025), VenusBench-Mobile and WebVoyager He et al. (2024). These benchmarks are challenging, fully dynamic online suites that require GUI agents to perform multi-turn adaptive perception, reasoning, and action in evolving environments, thus providing a more reliable assessment of the model’s navigation capabilities.

Android World. AndroidWorld is a comprehensive online evaluation environment for GUI agents. It includes 116 programmatic tasks across 20 real-world Android applications and is widely used as a benchmark for assessing GUI agent performance. As shown in Table 2, the Venus-1.5 model family achieves state-of-the-art (SOTA) performance among models of comparable scale. Specifically, our 2B / 8B / 30B-A3B variants reach accuracies of $5 5 . 6 \% / 7 3 . 7 \% / 7 7 . 6 \%$ , outperforming existing domain-specific and general-purpose baselines. Relative to the strongest existing contender, MAI-UI-32B, UI-Venus-1.5-30B-A3B secures an absolute margin of $4 . 3 \%$ .

Android Lab. Android Lab is another dynamic, online evaluation benchmark comprising 138 tasks across 9 Android applications. Our model uses only raw screen screenshots as input, yet it outperforms both a range of GUI-specialized models and general-purpose models, some of which take both screenshots and XML information as inputs. As shown in Table 3, our UI-Venus-1.5 series models (2B, 8B, and 30A3B) achieve $3 6 . 2 \%$ , $5 5 . 1 \%$ , and $5 2 . 9 \%$ on AndroidLab, respectively. It is worth noting that, due to bugs in the official AndroidLab evaluation code, we additionally report human-verified results (marked with a †) in the Table 3. The corrected results show that our UI-Venus-1.5-30A3B model does not exhibit any performance degradation on AndroidLab compared with the UI-Venus-1.5-8B model $6 8 . 1 \%$ vs. $6 8 . 1 \%$ ). Compared with our UI-Venus-1.0-72B model, the best model in the 1.5 series yields up to $5 . 8 \%$ improvement. Notably, even UI-Venus-1.5-8B significantly outperforms other state-of-the-art models.

<table><tr><td>Models</td><td>Params.</td><td>Success Rate</td></tr><tr><td colspan="3">General VLMs</td></tr><tr><td>Qwen3-VL-8B (Bai et al., 2025a)</td><td>8B</td><td>6.7</td></tr><tr><td>Qwen3-VL-30B-A3B (Bai et al., 2025a)</td><td>30B</td><td>8.7</td></tr><tr><td colspan="3">GUI-specific Models</td></tr><tr><td>GUI-Owl-7B (Ye et al., 2025)</td><td>7B</td><td>6.7</td></tr><tr><td>UI-Venus-1.0-7B (Gu et al., 2025)</td><td>7B</td><td>8.1</td></tr><tr><td>UI-Venus-1.0-72B (Gu et al., 2025)</td><td>72B</td><td>15.4</td></tr><tr><td>Step-GUI-4B (Yan et al., 2025)</td><td>4B</td><td>8.0</td></tr><tr><td>MAI-UI-2B (Zhou et al., 2025b)</td><td>2B</td><td>6.7</td></tr><tr><td>MAI-UI-8B (Zhou et al., 2025b)</td><td>8B</td><td>12.7</td></tr><tr><td colspan="3">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>2B</td><td>8.7</td></tr><tr><td>UI-Venus-1.5-8B</td><td>8B</td><td>16.1</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>30B</td><td>21.5</td></tr></table>

Table 4 Performance comparison on VenusBench-Mobile for end-to-end models. Our UI-Venus-1.5 achieves state-of-the-art performance on this challenging benchmark.   
Table 5 Performance comparison on Webvoyager existing GUI Agents. Note that * indicates that the results are evaluated by us.   

<table><tr><td>Models</td><td>Params.</td><td>Success Rate</td></tr><tr><td colspan="3">General VLMs</td></tr><tr><td>GPT-4o (Hurst et al., 2024)</td><td>-</td><td>55.5</td></tr><tr><td>Claude-3.7 (Anthropic, 2025a)</td><td>-</td><td>84.1</td></tr><tr><td>Qwen3-VL-2B* (Bai et al., 2025a)</td><td>2B</td><td>35.2</td></tr><tr><td>Qwen3-VL-8B* (Bai et al., 2025a)</td><td>8B</td><td>45.2</td></tr><tr><td>Qwen3-VL-30B-A3B* (Bai et al., 2025a)</td><td>30B</td><td>47.5</td></tr><tr><td colspan="3">GUI-specific Models</td></tr><tr><td>WebVoyager (He et al., 2024)</td><td>-</td><td>59.1</td></tr><tr><td>OpenAI-CUA (OpenAI, 2025a)</td><td>-</td><td>87.0</td></tr><tr><td>UI-TARS-1.5 (Qin et al., 2025)</td><td>-</td><td>84.8</td></tr><tr><td>Holo2-4B (H-Company, 2025)</td><td>4B</td><td>80.2</td></tr><tr><td>Holo2-8B (H-Company, 2025)</td><td>8B</td><td>80.2</td></tr><tr><td>Holo2-30B-A3B (H-Company, 2025)</td><td>30B</td><td>83.0</td></tr><tr><td colspan="3">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>2B</td><td>56.4</td></tr><tr><td>UI-Venus-1.5-8B</td><td>8B</td><td>70.8</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>30B</td><td>76.0</td></tr></table>

VenusBench-Mobile. VenusBench-Mobile is a challenging benchmark designed to evaluate the end-to-end performance of GUI agents in complex mobile environments. As illustrated in Table 4, the UI-Venus-1.5 model family achieves state-of-the-art (SOTA) performance across all scales.

Specifically, our 2B, 8B, and 30B-A3B variants reach success rates of $8 . 7 \%$ , $1 6 . 1 \%$ , and $2 1 . 5 \%$ , respectively, consistently outperforming both general-purpose VLMs and specialized GUI models. Notably, our 8B model $( 1 6 . 1 \% )$ already surpasses the much larger UI-Venus-1.0-72B $( 1 5 . 4 \% )$ , while our 30B-A3B variant sets a new record with a substantial $6 . 1 \%$ absolute margin over the previous best-performing model.

WebVoyager. WebVoyager is a comprehensive end-to-end benchmark for evaluating web agents on 15 real-world websites including e-commerce, travel, and social platforms. It employs an automatic evaluation protocol leveraging MLLM to assess task completion rates, measuring agents’ abilities to autonomously navigate and interact with dynamic web environments through visual screenshots and textual elements. As shown in Table 5, the UI-Venus-1.5 model family achieves comparable performance among models of comparable scale. Specifically, our 2B/8B/30B-A3B variants reach success rates of $5 6 . 4 \% / 7 0 . 8 \% / 7 6 . 0 \%$ , outperforming WebVoyager He et al. (2024) and general VLMs (e.g., GPT-4o, Qwen3-VL).

In summary, our evaluation reveals several key insights:

• Superior End-to-End Performance: UI-Venus-1.5-30B-A3B achieves state-of-the-art or comparable results across a diverse range of GUI agent benchmarks, including Android World $( 7 7 . 6 \% )$ , Android Lab $( 5 5 . 1 \% / 6 8 . 1 \% + )$ ), VenusBench-Mobile $( 2 1 . 5 \% )$ , and WebVoyager $( 7 6 . 0 \% )$ . It consistently outperforms both specialized GUI models (e.g., MAI-UI-32B) and leading general-purpose VLMs (e.g., GPT-4o, Qwen3-VL), establishing a new performance ceiling for autonomous agents.   
• Significant Architectural Efficiency and Scaling: Increasing the model scale leads to consistent performance gains across all benchmarks. Notably, the UI-Venus-1.5 family exhibits remarkable efficiency; our 8B model already surpasses the previous generation’s 72B variant on both Android Lab (up to $5 . 8 \%$ improvement) and VenusBench-Mobile ( $1 6 . 1 \%$ vs. $1 5 . 4 \%$ ), demonstrating the effectiveness of our updated training methodology.   
• Robust Cross-Platform Generalization: UI-Venus demonstrates exceptional adaptability across different operating systems and input modalities. It excels not only in programmatic Android environments but also in dynamic web navigation (WebVoyager). Furthermore, the models show strong visual-only reasoning capabilities, outperforming XML-augmented baselines in Android Lab even when relying solely on raw screenshots.

# 3.3 The Influence of Mid-Training

To verify the effectiveness of our Mid-Training strategy, we conduct the qualitative latent space analysis as shown in Figure 8. Specifically, we analyzed the latent representations using t-SNE visualization to quantify the impact of Mid-Training. By comparing the base model with our model after Mid-Training, we observe several key observations:

• Cluster Separability: After Mid-Training, GUI-specific features exhibit a transition to highdensity clusters. The Silhouette Score reached 0.315, a relative increase of $3 4 . 0 \%$ over the base model $\mathrm { 0 . 2 3 5  0 . 3 1 5 }$ ).   
• Feature Sensitivity: The $1 1 . 6 \%$ decrease in Intra-class Consistency $( 0 . 4 4 8  0 . 3 9 6 )$ indicates enhanced discriminative power. It demonstrates that the model is now capable of capturing fine-grained functional and structural variances, allowing for a more granular characterization of GUI elements that were previously treated as uniform.

(a) Latent Space of Origin Base Model   
(b) Latent Space of GUl-Native Model   
![](images/cf4fba05485490bab8800d4922fb31583f97e3640bfdde7c2c4370440d736bc8.jpg)  
General Perception Data

Figure 8 Latent space visualization of (a) base model and (b) model with GUI knowledge. The emergence of distinct clusters indicates that our Mid-Training has successfully enriched the model with GUI domain knowledge. This increased discriminative power between GUI and general data provides a robust structural basis for the reinforcement learning stage.   
![](images/2d378ea233647a6bf86a81a7d5fc8be1c24abb1146dbcabcd0ef1991be0efd4d.jpg)  
GUI-Domain Clusters

• Global Space Stability: The Inter-class Similarity remains stable (only $1 . 4 \%$ increase), confirming that GUI-specific knowledge does not cause representation collapse.

Table 6 Latent space metrics of the model before and after Mid-Training.   

<table><tr><td>Metric</td><td>Qwen3VL</td><td>Model After Mid-Training</td><td>Change</td></tr><tr><td>Silhouette Score</td><td>0.235</td><td>0.315</td><td>+34.0% (↑)</td></tr><tr><td>Intra-class Consistency</td><td>0.448</td><td>0.396</td><td>-11.6% (↓)</td></tr><tr><td>Inter-class Similarity</td><td>0.220</td><td>0.223</td><td>+1.4% (≈ stable)</td></tr></table>

# 3.4 Ablation Studies

Table 7 Ablation studies of UI-Venus-1.5 on ScreenSpot-Pro (denote as “SS-Pro”) and AndroidWorld (denote as “AW”).   

<table><tr><td rowspan="2">Models</td><td colspan="2">Mid-Training</td><td colspan="2">Offline-RL</td><td colspan="2">Online-RL</td><td colspan="2">Model Merge</td></tr><tr><td>SS-Pro</td><td>AW</td><td>SS-Pro</td><td>AW</td><td>SS-Pro</td><td>AW</td><td>SS-Pro</td><td>AW</td></tr><tr><td colspan="9">UI-Venus-1.5</td></tr><tr><td>2B</td><td>52.3</td><td>39.0</td><td>59.0(+6.7↑)</td><td>45.3(+6.3↑)</td><td>-</td><td>59.8(+14.5↑)</td><td>57.7(-1.3↓)</td><td>55.6 (-4.2↓)</td></tr><tr><td>8B</td><td>63.1</td><td>57.0</td><td>70.0(+6.9↑)</td><td>63.5(+6.5↑)</td><td>-</td><td>72.7(+9.2↑)</td><td>68.4(-1.6↓)</td><td>73.7(+1.0↑)</td></tr><tr><td>30B-A3B</td><td>65.2</td><td>67.1</td><td>71.0(+5.8↑)</td><td>68.0(+0.9↑)</td><td>-</td><td>75.5(+7.5↑)</td><td>69.6(-1.4↓)</td><td>77.6(+2.1↑)</td></tr></table>

In this section, we will show the performance gains of every step in the UI-Venus-1.5 pipeline, including Mid-Training, Offline-RL, Online-RL and Model Merge. As shown in Table 7, we can conclude following insights:

• Offline-RL: Building Foundation for Grounding and Navigation. The transition from Mid-Training to Offline-RL yields consistent improvements across all scales and tasks. Specifically, ScreenSpot-Pro scores increase by approximately $6- 7 \%$ , while AndroidWorld (AW) performance also sees a significant boost (up to $+ 6 . 5 \%$ for the 8B model). This confirms that

GRPO on diverse, task-specific offline data effectively aligns the model’s visual perception with GUI-specific action spaces.

• Online-RL: The Catalyst for Complex Navigation. Online-RL serves as the most critical stage for enhancing autonomous navigation capabilities. We observe a substantial leap in AndroidWorld success rates, with the 2B model showing a remarkable $+ 1 4 . 5 \%$ absolute gain. By interacting with dynamic environments and learning from exploration, the models overcome the limitations of static datasets, significantly improving their ability to handle long-horizon tasks and error recovery in real-world scenarios.   
• Model Merge: Balancing Specialization and Generalization. The final model merge stage aims to unify specialized capabilities. While it leads to a minor, acceptable trade-off in finegrained grounding (a drop of ${ \sim } 1 . 4 \%$ on ScreenSpot-Pro), it further stabilizes and enhances navigation performance for larger models. Notably, UI-Venus-1.5-30B-A3B gains an additional $2 . 1 \%$ on AndroidWorld after the merge, suggesting that the unification process helps the model leverage cross-task knowledge to solve complex GUI sequences more effectively.

# 4 Related Works

GUI agents can automatically execute a series of operations on GUI screens based on given instructions. In early works, the system typically relied on predefined rules, which exhibited limited scalability. With the emergence and advancement of LLMs, it is possible to adopt a single model to handle diverse tasks as an intelligent GUI agent.

GUI Grounding. Some researches focus on GUI grounding that aims to map natural language descriptions or instructions to precise positions of GUI elements on screens, enabling autonomous agents to identify widgets with diverse functionalities and select the appropriate one to interact by an equipped planner. Early methods Cheng et al. (2024); Lin et al. (2024); Xu et al. (2024); Wu et al. (2024); Gu et al. (2023); Gou et al. (2024); Wang et al. (2024c); Wu et al. (2025); Xie et al. (2025b); Tang et al. (2025b) usually adopt supervised fine-tuning (SFT) to train grounding models, which leverages labeled data rapidly and produces various grounding models that are able to recognize and locate diverse elements on common GUI scenarios. As models evolve rapidly, the accuracies on some grounding benchmarks Cheng et al. (2024); Wu et al. (2024) has hit a ceiling. To further evaluate the grounding capabilities of models in complex scenarios, more benchmarks like Screenspot-Pro Li et al. (2025a) and VenusBench-GD Zhou et al. (2025a) have been introduced to explore the limit of performance, which additionally requires the understanding of professional software and comprehensive visual reasoning. In parallel, the training paradigms are shifting. Inspired by DeepSeek-R1 DeepSeek-AI (2025), recent works have incorporated reinforcement learning (RL) into training process, aiming to enhance model generalization across unseen scenarios with limited labeled data Lu et al. (2025b); Luo et al. (2025); Liu et al. (2025); Zhou et al. (2025c); Yuan et al. (2025); Tang et al. (2025c,a); Zhang et al. (2026); Zhou et al. (2025b); Qin et al. (2025); Seed (2025b); Yan et al. (2025). In addition, some works Zhang et al. (2025); Jiang et al. (2025) focus on post-processing to improve the test-time performance of the model. The mutual evolution between benchmarks and models drives the continuous advancement of the grounding research.

End-to-End GUI Agent. Also, some researchers attempt to tackle navigation tasks end-to-end with a unified model. At early stage, the agents were trained on foundation models directly, which served as preliminary attempts at autonomous GUI agents and produced promising results Hong et al. (2024); Lin et al. (2024); Cheng et al. (2024); Deng et al. (2023); Wu et al. (2024), but there

remained a gap between the actual performance and the requirement of practical deployment. Driven by further practicality, with the incorporation of RL techniques like Direct Preference Optimization (DPO) Rafailov et al. (2023) and Group Relative Policy Optimization (GRPO) Shao et al. (2024), improved pipeline of data generation and increased computational resources, many research groups have developed more powerful agents Qin et al. (2025); Zeng et al. (2025); Sun et al. (2025b); Yang et al. (2024); Sun et al. (2025a); Qiu et al. (2026). More recently, as the alignment between real-world and training environments receives widespread focus, more end-to-end GUI agents exhibit robust practical deployment capabilities Wang et al. (2025a); Liu et al. (2024); Yan et al. (2025), which advances the feasibility of GUI agents in real-life scenarios.

GUI Agent Framework. As a collaboration paradigm that distributes the extensive context across sub-agents with various functionalities, the GUI agent framework fully leverages the base model’s understanding and reasoning capabilities to analyze the task progress and GUI screens, and subsequently takes a correct action. Agent S Agashe et al. (2024) introduces experience-augmented hierarchical planning strategy to improve task execution with several role-specific agents, and Agent S2 Agashe et al. (2025) upgrades the strategy as proactive hierarchical planning to dynamically refine actions based on real-time observations. Besides, began with Mobile-Agent Wang et al. (2024b), Mobile-Agent-v2 Wang et al. (2024a) incorporates a multi-agent collaboration architecture for long-step navigation, which includes planning, decision, reflection agents and a memory unit to retain focus content. Moreover, Mobile-Agent-E Wang et al. (2025d) implements a self-evolving hierarchical framework to store long-term memory and learn from the past, and Mobile-Agent-v3 Ye et al. (2025) further advances the framework by improved base model and training strategies based on its predecessors. More studies have also explored GUI agent frameworks dro (2025); Xie et al. (2025a). These agent frameworks probably possess a higher capacity ceiling, enabling them to perform navigation tasks that require intricate reasoning and analysis. Nevertheless, the data flow in the framework usually necessitates multiple rounds of LLM input and output, which leads to substantial computational costs and obvious operation latency.

# 5 Conclusion

In this work, we presented UI-Venus-1.5, a comprehensive advancement in the development of practical and reliable GUI agents. To address the limitations of previous iterations and current baselines, we introduced a three-tiered training paradigm: a large-scale Mid-Training stage for robust GUI knowledge injection, a task-specific Offline-RL phase unified by an efficient model merge strategy, and a scaled Online-RL framework to master complex navigation. Furthermore, the unified capability of UI-Venus-1.5 is achieved through strategic model merging, which effectively consolidates specialized domain expertise—including grounding, web, and mobile navigation—into a single end-to-end agent while preserving robust performance across tasks.

Experimental results demonstrate that UI-Venus-1.5 establishes a new state of the art across a wide spectrum of benchmarks, including GUI grounding and navigation. Beyond academic metrics, we have optimized the model for real-world utility within the $^ { 4 0 + }$ Chinese third-party app ecosystem, enabling seamless automation for tasks such as ticket booking, and shopping. Collectively, these contributions on GUI Agents mark a significant step towards a truly autonomous and user-centric digital assistant.

# 6 Contributions

All contributors of UI-Venus-1.5 are listed in alphabetical order by their last names.

# 6.1 Core Contributors

Changlong Gao, Zhangxuan Gu, Yulin Liu, Xinyu Qiu, Shuheng Shen†, Yue Wen, Tianyu Xia, Zhenyu Xu, Zhengwen Zeng, Beitong Zhou, Xingran Zhou

# 6.2 Contributors

Weizhi Chen, Sunhao Dai, Jingya Dou, Yichen Gong, Yuan Guo, Zhenlin Guo, Feng Li, Qian Li, Jinzhen Lin, Yuqi Zhou, Linchao Zhu

# 6.3 Supervisors

Liang Chen, Zhenyu Guo, Changhua Meng†, Weiqiang Wang

# References

Droidrun. https://github.com/droidrun/droidrun, 2025.   
Saaket Agashe, Jiuzhou Han, Shuyu Gan, Jiachen Yang, Ang Li, and Xin Eric Wang. Agent s: An open agentic framework that uses computers like a human. arXiv preprint arXiv:2410.08164, 2024.   
Saaket Agashe, Kyle Wong, Vincent Tu, Jiachen Yang, Ang Li, and Xin Eric Wang. Agent s2: A compositional generalist-specialist framework for computer use agents. arXiv preprint arXiv:2504.00906, 2025.   
Anthropic. Claude computer use. Available at: https://www.anthropic.com/news/developing-computer-use, 2024.   
Anthropic. Claude-3-7-sonnet. https://www.anthropic.com/news/claude-3-7-sonnet, 2025a.   
Shuai Bai, Yuxuan Cai, Ruizhe Chen, Keqin Chen, Xionghui Chen, Zesen Cheng, Lianghao Deng, Wei Ding, Chang Gao, Chunjiang Ge, Wenbin Ge, Zhifang Guo, Qidong Huang, Jie Huang, Fei Huang, Binyuan Hui, Shutong Jiang, Zhaohai Li, Mingsheng Li, Mei Li, Kaixin Li, Zicheng Lin, Junyang Lin, Xuejing Liu, Jiawei Liu, Chenglong Liu, Yang Liu, Dayiheng Liu, Shixuan Liu, Dunjie Lu, Ruilin Luo, Chenxu Lv, Rui Men, Lingchen Meng, Xuancheng Ren, Xingzhang Ren, Sibo Song, Yuchong Sun, Jun Tang, Jianhong Tu, Jianqiang Wan, Peng Wang, Pengfei Wang, Qiuyue Wang, Yuxuan Wang, Tianbao Xie, Yiheng Xu, Haiyang Xu, Jin Xu, Zhibo Yang, Mingkun Yang, Jianxin Yang, An Yang, Bowen Yu, Fei Zhang, Hang Zhang, Xi Zhang, Bo Zheng, Humen Zhong, Jingren Zhou, Fan Zhou, Jing Zhou, Yuanzhi Zhu, and Ke Zhu. Qwen3-vl technical report. arXiv preprint arXiv:2511.21631, 2025a.   
Shuai Bai, Keqin Chen, Xuejing Liu, Jialin Wang, Wenbin Ge, Sibo Song, Kai Dang, Peng Wang, Shijie Wang, Jun Tang, Humen Zhong, Yuanzhi Zhu, Mingkun Yang, Zhaohai Li, Jianqiang Wan, Pengfei Wang, Wei Ding, Zheren Fu, Yiheng Xu, Jiabo Ye, Xi Zhang, Tianbao Xie, Zesen Cheng, Hang Zhang, Zhibo Yang, Haiyang Xu, and Junyang Lin. Qwen2.5-vl technical report, 2025b. https://arxiv.org/abs/2502.13923.   
Zengjue Chen, Runliang Niu, He Kong, Qi Wang, Qianli Xing, and Zipei Fan. Tgrpo: Fine-tuning vision-language-action model via trajectory-wise group relative policy optimization. arXiv preprint arXiv:2506.08440, 2025.   
Kanzhi Cheng, Qiushi Sun, Yougang Chu, Fangzhi Xu, Yantao Li, Jianbing Zhang, and Zhiyong Wu. Seeclick: Harnessing gui grounding for advanced visual gui agents, 2024. https://arxiv.org/abs/2401.10935.   
Gheorghe Comanici, Eric Bieber, Mike Schaekermann, Ice Pasupat, Noveen Sachdeva, Inderjit Dhillon, Marcel Blistein, Ori Ram, Dan Zhang, Evan Rosen, et al. Gemini 2.5: Pushing the frontier with advanced reasoning, multimodality, long context, and next generation agentic capabilities. arXiv preprint arXiv:2507.06261, 2025.   
Gaole Dai, Shiqi Jiang, Ting Cao, Yuanchun Li, Yuqing Yang, Rui Tan, Mo Li, and Lili Qiu. Advancing mobile gui agents: A verifier-driven approach to practical deployment. arXiv preprint arXiv:2503.15937, 2025.   
Tongyi-Team DeepResearch, Baixuan Li, Bo Zhang, Dingchu Zhang, Fei Huang, Guangyu Li, Guoxin Chen, Huifeng Yin, Jialong Wu, Jingren Zhou, et al. Tongyi deepresearch technical report. arXiv preprint arXiv:2510.24701, 2025.   
DeepSeek-AI. Deepseek-r1: Incentivizing reasoning capability in llms via reinforcement learning, 2025. https://arxiv.org/abs/ 2501.12948.   
Xiang Deng, Yu Gu, Boyuan Zheng, Shijie Chen, Sam Stevens, Boshi Wang, Huan Sun, and Yu Su. Mind2web: Towards a generalist agent for the web. Advances in Neural Information Processing Systems, 36:28091–28114, 2023.   
Gemini-Team, Petko Georgiev, Ving Ian Lei, Ryan Burnell, Libin Bai, Anmol Gulati, Garrett Tanzer, Damien Vincent, Zhufeng Pan, Shibo Wang, et al. Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context. arXiv preprint arXiv:2403.05530, 2024.   
Team GLM, Aohan Zeng, Bin Xu, Bowen Wang, Chenhui Zhang, Da Yin, Dan Zhang, Diego Rojas, Guanyu Feng, Hanlin Zhao, et al. Chatglm: A family of large language models from glm-130b to glm-4 all tools. arXiv preprint arXiv:2406.12793, 2024.   
Boyu Gou, Ruohan Wang, Boyuan Zheng, Yanan Xie, Cheng Chang, Yiheng Shu, Huan Sun, and Yu Su. Navigating the digital world as humans do: Universal visual grounding for gui agents, 2024. https://arxiv.org/abs/2410.05243.   
Aaron Grattafiori, Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Alex Vaughan, et al. The llama 3 herd of models. arXiv preprint arXiv:2407.21783, 2024.   
Zhangxuan Gu, Zhuoer Xu, Haoxing Chen, Jun Lan, Changhua Meng, and Weiqiang Wang. Mobile user interface element detection via adaptively prompt tuning. In Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, pages 11155–11164, 2023.

Zhangxuan Gu, Zhengwen Zeng, Zhenyu Xu, Xingran Zhou, Shuheng Shen, Yunfei Liu, Beitong Zhou, Changhua Meng, Tianyu Xia, Weizhi Chen, et al. Ui-venus technical report: Building high-performance ui agents with rft. arXiv preprint arXiv:2508.10833, 2025.   
H-Company. Holo2 - open foundation models for navigation and computer use agents, 2025.   
Hongliang He, Wenlin Yao, Kaixin Ma, Wenhao Yu, Yong Dai, Hongming Zhang, Zhenzhong Lan, and Dong Yu. Webvoyager: Building an end-to-end web agent with large multimodal models. arXiv preprint arXiv:2401.13919, 2024.   
Wenyi Hong, Weihan Wang, Qingsong Lv, Jiazheng Xu, Wenmeng Yu, Junhui Ji, Yan Wang, Zihan Wang, Yuxuan Zhang, Juanzi Li, Bin Xu, Yuxiao Dong, Ming Ding, and Jie Tang. Cogagent: A visual language model for gui agents, 2024. https: //arxiv.org/abs/2312.08914.   
Aaron Hurst, Adam Lerer, Adam P Goucher, Adam Perelman, Aditya Ramesh, Aidan Clark, AJ Ostrow, Akila Welihinda, Alan Hayes, Alec Radford, et al. Gpt-4o system card. arXiv preprint arXiv:2410.21276, 2024.   
Inclusion-AI, Bowen Ma, Cheng Zou, Canxiang Yan, Chunxiang Jin, Chunjie Shen, Chenyu Lian, Dandan Zheng, Fudong Wang, Furong Xu, et al. Ming-flash-omni: A sparse, unified architecture for multimodal perception and generation. arXiv preprint arXiv:2510.24821, 2025.   
Zhiyuan Jiang, Shenghao Xie, Wenyi Li, Wenqiang Zu, Peihang Li, Jiahao Qiu, Siqi Pei, Lei Ma, Tiejun Huang, Mengdi Wang, et al. Zoom in, click out: Unlocking and evaluating the potential of zooming for gui grounding. arXiv preprint arXiv:2512.05941, 2025.   
Kaixin Li, Ziyang Meng, Hongzhan Lin, Ziyang Luo, Yuchen Tian, Jing Ma, Zhiyong Huang, and Tat-Seng Chua. Screenspot-pro: Gui grounding for professional high-resolution computer use, 2025a.   
Ning Li, Xiangmou Qu, Jiamu Zhou, Jun Wang, Muning Wen, Kounianhua Du, Xingyu Lou, Qiuying Peng, and Weinan Zhang. Mobileuse: A gui agent with hierarchical reflection for autonomous mobile operation. arXiv preprint arXiv:2507.16853, 2025b.   
Wei Li, William Bishop, Alice Li, Chris Rawles, Folawiyo Campbell-Ajala, Divya Tyamagundlu, and Oriana Riva. On the effects of data scale on ui control agents, 2024. https://arxiv.org/abs/2406.03679.   
Weishi Li, Yong Peng, Miao Zhang, Liang Ding, Han Hu, and Li Shen. Deep model fusion: A survey. arXiv preprint arXiv:2309.15698, 2023.   
Kevin Qinghong Lin, Linjie Li, Difei Gao, Zhengyuan Yang, Shiwei Wu, Zechen Bai, Weixian Lei, Lijuan Wang, and Mike Zheng Shou. Showui: One vision-language-action model for gui visual agent, 2024. https://arxiv.org/abs/2411.17465.   
Ling-Team, Ang Li, Ben Liu, Binbin Hu, Bing Li, Bingwei Zeng, Borui Ye, Caizhi Tang, Changxin Tian, Chao Huang, et al. Every activation boosted: Scaling general reasoner to 1 trillion open language foundation. arXiv preprint arXiv:2510.22115, 2025a.   
Ling-Team, Anqi Shen, Baihui Li, Bin Hu, Bin Jing, Cai Chen, Chao Huang, Chao Zhang, Chaokun Yang, Cheng Lin, et al. Every step evolves: Scaling reinforcement learning for trillion-scale thinking model. arXiv preprint arXiv:2510.18855, 2025b.   
Xiao Liu, Bo Qin, Dongzhu Liang, Guang Dong, Hanyu Lai, Hanchen Zhang, Hanlin Zhao, Iat Long Iong, Jiadai Sun, Jiaqi Wang, et al. Autoglm: Autonomous foundation agents for guis. arXiv preprint arXiv:2411.00820, 2024.   
Yuhang Liu, Pengxiang Li, Congkai Xie, Xavier Hu, Xiaotian Han, Shengyu Zhang, Hongxia Yang, and Fei Wu. Infigui-r1: Advancing multimodal gui agents from reactive actors to deliberative reasoners. 2025. https://arxiv.org/abs/2504.14239.   
Quanfeng Lu, Wenqi Shao, Zitao Liu, Lingxiao Du, Fanqing Meng, Boxuan Li, Botong Chen, Siyuan Huang, Kaipeng Zhang, and Ping Luo. Guiodyssey: A comprehensive dataset for cross-app gui navigation on mobile devices, 2025a. https://arxiv.org/ abs/2406.08451.   
Zhengxi Lu, Yuxiang Chai, Yaxuan Guo, Xi Yin, Liang Liu, Hao Wang, Han Xiao, Shuai Ren, Guanjing Xiong, and Hongsheng Li. Uir1: Enhancing efficient action prediction of gui agents by reinforcement learning. 2025b. https://arxiv.org/abs/2503.21620.   
Run Luo, Lu Wang, Wanwei He, and Xiaobo Xia. Gui-r1 : A generalist r1-style vision-language action model for gui agents. 2025. https://arxiv.org/abs/2504.10458.   
Shravan Nayak, Xiangru Jian, Kevin Qinghong Lin, Juan A Rodriguez, Montek Kalsi, Rabiul Awal, Nicolas Chapados, M Tamer Özsu, Aishwarya Agrawal, David Vazquez, et al. Ui-vision: A desktop-centric gui benchmark for visual perception and interaction. arXiv preprint arXiv:2503.15661, 2025.   
OpenAI. Computer using agent. https://platform.openai.com/docs/guides/tools-computer-use, 2025a.   
Yujia Qin, Yining Ye, Junjie Fang, Haoming Wang, Shihao Liang, Shizuo Tian, Junda Zhang, Jiahao Li, Yunxin Li, Shijue Huang, Wanjun Zhong, Kuanye Li, Jiale Yang, Yu Miao, Woyu Lin, Longxiang Liu, Xu Jiang, Qianli Ma, Jingyu Li, Xiaojun Xiao, Kai Cai, Chuang Li, Yaowei Zheng, Chaolin Jin, Chen Li, Xiao Zhou, Minchao Wang, Haoli Chen, Zhaojian Li, Haihua Yang,

Haifeng Liu, Feng Lin, Tao Peng, Xin Liu, and Guang Shi. Ui-tars: Pioneering automated gui interaction with native agents, 2025. https://arxiv.org/abs/2501.12326.   
Xinyu Qiu, Heng Jia, Zhengwen Zeng, Shuheng Shen, Changhua Meng, Yi Yang, and Linchao Zhu. Unified generation and self-verification for vision-language models via advantage decoupled preference optimization. arXiv preprint arXiv:2601.01483, 2026.   
Rafael Rafailov, Archit Sharma, Eric Mitchell, Christopher D Manning, Stefano Ermon, and Chelsea Finn. Direct preference optimization: Your language model is secretly a reward model. Advances in neural information processing systems, 36:53728– 53741, 2023.   
Christopher Rawles, Alice Li, Daniel Rodriguez, Oriana Riva, and Timothy Lillicrap. Androidinthewild: A large-scale dataset for android device control. Advances in Neural Information Processing Systems, 36:59708–59728, 2023.   
Christopher Rawles, Sarah Clinckemaillie, Yifan Chang, Jonathan Waltz, Gabrielle Lau, Marybeth Fair, Alice Li, William Bishop, Wei Li, Folawiyo Campbell-Ajala, Daniel Toyama, Robert Berry, Divya Tyamagundlu, Timothy Lillicrap, and Oriana Riva. Androidworld: A dynamic benchmarking environment for autonomous agents, 2025. https://arxiv.org/abs/2405.14573.   
Bytedance Seed. Seed1. 8 model card: Towards generalized real-world agency, 2025a. https://lf3-static.bytednsdoc.com/obj/ eden-cn/lapzild-tss/ljhwZthlaukjlkulzlp/research/Seed-1.8-Modelcard.pdf.   
ByteDance Seed. Ui-tars-1.5. https://seed-tars.com/1.5, 2025b.   
Zhihong Shao, Peiyi Wang, Qihao Zhu, Runxin Xu, Junxiao Song, Xiao Bi, Haowei Zhang, Mingchuan Zhang, Y. K. Li, Y. Wu, and Daya Guo. Deepseekmath: Pushing the limits of mathematical reasoning in open language models, 2024. https://arxiv.org/ abs/2402.03300.   
Qiushi Sun, Kanzhi Cheng, Zichen Ding, Chuanyang Jin, Yian Wang, Fangzhi Xu, Zhenyu Wu, Chengyou Jia, Liheng Chen, Zhoumianze Liu, Ben Kao, Guohao Li, Junxian He, Yu Qiao, and Zhiyong Wu. Os-genesis: Automating gui agent trajectory construction via reverse task synthesis, 2025a. https://arxiv.org/abs/2412.19723.   
Yuchen Sun, Shanhui Zhao, Tao Yu, Hao Wen, Samith Va, Mengwei Xu, Yuanchun Li, and Chongyang Zhang. Gui-xplore: Empowering generalizable gui agents with one exploration, 2025b. https://arxiv.org/abs/2503.17709.   
Fei Tang, Zhangxuan Gu, Zhengxi Lu, Xuyang Liu, Shuheng Shen, Changhua Meng, Wen Wang, Wenqi Zhang, Yongliang Shen, Weiming Lu, Jun Xiao, and Yueting Zhuang. Gui- $\mathbf { g } ^ { 2 }$ : Gaussian reward modeling for gui grounding, 2025a. https: //arxiv.org/abs/2507.15846.   
Fei Tang, Yongliang Shen, Hang Zhang, Siqi Chen, Guiyang Hou, Wenqi Zhang, Wenqiao Zhang, Kaitao Song, Weiming Lu, and Yueting Zhuang. Think twice, click once: Enhancing gui grounding via fast and slow systems. 2025b. https://arxiv.org/abs/ 2503.06470.   
Jiaqi Tang, Yu Xia, Yi-Feng Wu, Yuwei Hu, Yuhui Chen, Qing-Guo Chen, Xiaogang Xu, Xiangyu Wu, Hao Lu, Yanqing Ma, Shiyin Lu, and Qifeng Chen. Lpo: Towards accurate gui agent interaction via location preference optimization, 2025c. https: //arxiv.org/abs/2506.09373.   
V-Team, Wenyi Hong, Wenmeng Yu, Xiaotao Gu, Guo Wang, Guobing Gan, Haomiao Tang, Jiale Cheng, Ji Qi, Junhui Ji, Lihang Pan, Shuaiqi Duan, Weihan Wang, Yan Wang, Yean Cheng, Zehai He, Zhe Su, Zhen Yang, Ziyang Pan, Aohan Zeng, Baoxu Wang, Bin Chen, Boyan Shi, Changyu Pang, Chenhui Zhang, Da Yin, Fan Yang, Guoqing Chen, Jiazheng Xu, Jiale Zhu, Jiali Chen, Jing Chen, Jinhao Chen, Jinghao Lin, Jinjiang Wang, Junjie Chen, Leqi Lei, Letian Gong, Leyi Pan, Mingdao Liu, Mingde Xu, Mingzhi Zhang, Qinkai Zheng, Sheng Yang, Shi Zhong, Shiyu Huang, Shuyuan Zhao, Siyan Xue, Shangqin Tu, Shengbiao Meng, Tianshu Zhang, Tianwei Luo, Tianxiang Hao, Tianyu Tong, Wenkai Li, Wei Jia, Xiao Liu, Xiaohan Zhang, Xin Lyu, Xinyue Fan, Xuancheng Huang, Yanling Wang, Yadong Xue, Yanfeng Wang, Yanzi Wang, Yifan An, Yifan Du, Yiming Shi, Yiheng Huang, Yilin Niu, Yuan Wang, Yuanchang Yue, Yuchen Li, Yutao Zhang, Yuting Wang, Yu Wang, Yuxuan Zhang, Zhao Xue, Zhenyu Hou, Zhengxiao Du, Zihan Wang, Peng Zhang, Debing Liu, Bin Xu, Juanzi Li, Minlie Huang, Yuxiao Dong, and Jie Tang. Glm-4.5v and glm-4.1v-thinking: Towards versatile multimodal reasoning with scalable reinforcement learning, 2025. https://arxiv.org/abs/2507.01006.   
Haoming Wang, Haoyang Zou, Huatong Song, Jiazhan Feng, Junjie Fang, Junting Lu, Longxiang Liu, Qinyu Luo, Shihao Liang, Shijue Huang, et al. Ui-tars-2 technical report: Advancing gui agent with multi-turn reinforcement learning. arXiv preprint arXiv:2509.02544, 2025a.   
Junyang Wang, Haiyang Xu, Haitao Jia, Xi Zhang, Ming Yan, Weizhou Shen, Ji Zhang, Fei Huang, and Jitao Sang. Mobile-agent-v2: Mobile device operation assistant with effective navigation via multi-agent collaboration, 2024a. https://arxiv.org/abs/2406. 01014.

Junyang Wang, Haiyang Xu, Jiabo Ye, Ming Yan, Weizhou Shen, Ji Zhang, Fei Huang, and Jitao Sang. Mobile-agent: Autonomous multi-modal mobile device agent with visual perception, 2024b. https://arxiv.org/abs/2401.16158.   
Ke Wang, Tianyu Xia, Zhangxuan Gu, Yi Zhao, Shuheng Shen, Changhua Meng, Weiqiang Wang, and Ke Xu. E-ant: A large-scale dataset for efficient automatic gui navigation, 2024c. https://arxiv.org/abs/2406.14250.   
Xinyuan Wang, Bowen Wang, Dunjie Lu, Junlin Yang, Tianbao Xie, Junli Wang, Jiaqi Deng, Xiaole Guo, Yiheng Xu, Chen Henry Wu, Zhennan Shen, Zhuokai Li, Ryan Li, Xiaochuan Li, Junda Chen, Boyuan Zheng, Peihang Li, Fangyu Lei, Ruisheng Cao, Yeqiao Fu, Dongchan Shin, Martin Shin, Jiarui Hu, Yuyan Wang, Jixuan Chen, Yuxiao Ye, Danyang Zhang, Dikang Du, Hao Hu, Huarong Chen, Zaida Zhou, Yipu Wang, Heng Wang, Diyi Yang, Victor Zhong, Flood Sung, Y. Charles, Zhilin Yang, and Tao Yu. Opencua: Open foundations for computer-use agents, 2025b. https://arxiv.org/abs/2508.09123.   
Xuehui Wang, Zhenyu Wu, JingJing Xie, Zichen Ding, Bowen Yang, Zehao Li, Zhaoyang Liu, Qingyun Li, Xuan Dong, Zhe Chen, et al. Mmbench-gui: Hierarchical multi-platform evaluation framework for gui agents. arXiv preprint arXiv:2507.19478, 2025c.   
Zhenhailong Wang, Haiyang Xu, Junyang Wang, Xi Zhang, Ming Yan, Ji Zhang, Fei Huang, and Heng Ji. Mobile-agent-e: Self-evolving mobile assistant for complex tasks, 2025d. https://arxiv.org/abs/2501.11733.   
Qianhui Wu, Kanzhi Cheng, Rui Yang, Chaoyun Zhang, Jianwei Yang, Huiqiang Jiang, Jian Mu, Baolin Peng, Bo Qiao, Reuben Tan, et al. Gui-actor: Coordinate-free visual grounding for gui agents. arXiv preprint arXiv:2506.03143, 2025.   
Zhiyong Wu, Zhenyu Wu, Fangzhi Xu, Yian Wang, Qiushi Sun, Chengyou Jia, Kanzhi Cheng, Zichen Ding, Liheng Chen, Paul Pu Liang, and Yu Qiao. Os-atlas: A foundation action model for generalist gui agents, 2024. https://arxiv.org/abs/2410.23218.   
Han Xiao, Guozhi Wang, Yuxiang Chai, Zimu Lu, Weifeng Lin, Hao He, Lue Fan, Liuyang Bian, Rui Hu, Liang Liu, et al. Ui-genie: A self-improving approach for iteratively boosting mllm-based mobile gui agents. arXiv preprint arXiv:2505.21496, 2025.   
Bin Xie, Rui Shao, Gongwei Chen, Kaiwen Zhou, Yinchuan Li, Jie Liu, Min Zhang, and Liqiang Nie. Gui-explorer: Autonomous exploration and mining of transition-aware knowledge for gui agent. arXiv preprint arXiv:2505.16827, 2025a.   
Tianbao Xie, Jiaqi Deng, Xiaochuan Li, Junlin Yang, Haoyuan Wu, Jixuan Chen, Wenjing Hu, Xinyuan Wang, Yuhui Xu, Zekun Wang, Yiheng Xu, Junli Wang, Doyen Sahoo, Tao Yu, and Caiming Xiong. Scaling computer-use grounding via user interface decomposition and synthesis, 2025b. https://arxiv.org/abs/2505.13227.   
Yifan Xu, Xiao Liu, Xueqiao Sun, Siyi Cheng, Hao Yu, Hanyu Lai, Shudan Zhang, Dan Zhang, Jie Tang, and Yuxiao Dong. Androidlab: Training and systematic benchmarking of android autonomous agents. In Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 2144–2166, 2025.   
Yiheng Xu, Zekun Wang, Junli Wang, Dunjie Lu, Tianbao Xie, Amrita Saha, Doyen Sahoo, Tao Yu, and Caiming Xiong. Aguvis: Unified pure vision agents for autonomous gui interaction. 2024. https://arxiv.org/abs/2412.04454.   
Prateek Yadav, Derek Tam, Leshem Choshen, Colin A Raffel, and Mohit Bansal. Ties-merging: Resolving interference when merging models. Advances in Neural Information Processing Systems, 36:7093–7115, 2023.   
Haolong Yan, Jia Wang, Xin Huang, Yeqing Shen, Ziyang Meng, Zhimin Fan, Kaijun Tan, Jin Gao, Lieyu Shi, Mi Yang, et al. Step-gui technical report. arXiv preprint arXiv:2512.15431, 2025.   
Yan Yang, Dongxu Li, Yutong Dai, Yuhao Yang, Ziyang Luo, Zirui Zhao, Zhiyuan Hu, Junzhe Huang, Amrita Saha, Zeyuan Chen, Ran Xu, Liyuan Pan, Caiming Xiong, and Junnan Li. Gta1: Gui test-time scaling agent, 2025. https://arxiv.org/abs/2507.05791.   
Yuhao Yang, Yue Wang, Dongxu Li, Ziyang Luo, Bei Chen, Chao Huang, and Junnan Li. Aria-ui: Visual grounding for gui instructions, 2024. https://arxiv.org/abs/2412.16256.   
Jiabo Ye, Xi Zhang, Haiyang Xu, Haowei Liu, Junyang Wang, Zhaoqing Zhu, Ziwei Zheng, Feiyu Gao, Junjie Cao, Zhengxi Lu, et al. Mobile-agent-v3: Fundamental agents for gui automation. arXiv preprint arXiv:2508.15144, 2025.   
Xinbin Yuan, Jian Zhang, Kaixin Li, Zhuoxuan Cai, Lujian Yao, Jie Chen, Enguang Wang, Qibin Hou, Jinwei Chen, Peng-Tao Jiang, and Bo Li. Enhancing visual grounding for gui agents via self-evolutionary reinforcement learning. 2025. https: //arxiv.org/abs/2505.12370.   
Zhixiong Zeng, Jing Huang, Liming Zheng, Wenkang Han, Yufeng Zhong, Lei Chen, Longrong Yang, Yingjie Chu, Yuzhi He, and Lin Ma. Uitron: Foundational gui agent with advanced perception and planning. arXiv preprint arXiv:2508.21767, 2025.   
Le Zhang, Yixiong Xiao, Xinjiang Lu, Jingjia Cao, Yusai Zhao, Jingbo Zhou, Lang An, Zikan Feng, Wanxiang Sha, Yu Shi, Congxi Xiao, Jian Xiong, Yankai Zhang, Hua Wu, and Haifeng Wang. Omegause: Building a general-purpose gui agent for autonomous task execution, 2026. https://arxiv.org/abs/2601.20380.   
Yunzhu Zhang, Zeyu Pan, Zhengwen Zeng, Shuheng Shen, Changhua Meng, and Linchao Zhu. Mvp: Multiple view prediction improves gui grounding. arXiv preprint arXiv:2512.08529, 2025.

Zhipu-AI. Glm-4.5v. Available at: https://docs.z.ai/guides/vlm/glm-4.5v, 2025.   
Beitong Zhou, Zhexiao Huang, Yuan Guo, Zhangxuan Gu, Tianyu Xia, Zichen Luo, Fei Tang, Dehan Kong, Yanyi Shang, Suling Ou, et al. Venusbench-gd: A comprehensive multi-platform gui benchmark for diverse grounding tasks. arXiv preprint arXiv:2512.16501, 2025a.   
Hanzhang Zhou, Xu Zhang, Panrong Tong, Jianan Zhang, Liangyu Chen, Quyu Kong, Chenglin Cai, Chen Liu, Yue Wang, Jingren Zhou, et al. Mai-ui technical report: Real-world centric foundation gui agents. arXiv preprint arXiv:2512.22047, 2025b.   
Yuqi Zhou, Sunhao Dai, Shuai Wang, Kaiwen Zhou, Qinglin Jia, and Jun Xu. Gui-g1: Understanding r1-zero-like training for visual grounding in gui agents. 2025c. https://arxiv.org/abs/2505.15810.   
Jinguo Zhu, Weiyun Wang, Zhe Chen, Zhaoyang Liu, Shenglong Ye, Lixin Gu, Hao Tian, Yuchen Duan, Weijie Su, Jie Shao, Zhangwei Gao, Erfei Cui, Xuehui Wang, Yue Cao, Yangzhou Liu, Xingguang Wei, Hongjie Zhang, Haomin Wang, Weiye Xu, Hao Li, Jiahao Wang, Nianchen Deng, Songze Li, Yinan He, Tan Jiang, Jiapeng Luo, Yi Wang, Conghui He, Botian Shi, Xingcheng Zhang, Wenqi Shao, Junjun He, Yingtong Xiong, Wenwen Qu, Peng Sun, Penglong Jiao, Han Lv, Lijun Wu, Kaipeng Zhang, Huipeng Deng, Jiaye Ge, Kai Chen, Limin Wang, Min Dou, Lewei Lu, Xizhou Zhu, Tong Lu, Dahua Lin, Yu Qiao, Jifeng Dai, and Wenhai Wang. Internvl3: Exploring advanced training and test-time recipes for open-source multimodal models, 2025. https://arxiv.org/abs/2504.10479.

# A Action Space and Prompt Templates

# A.1 Action Space

Table 8 All actions and their definitions used in UI-Venus-1.5. We unify the action space and map all the actions in the existing open-source dataset to this space.   

<table><tr><td>Action</td><td>Definition</td></tr><tr><td>Click.box=(x,y))</td><td>Click at coordinates (x,y).</td></tr><tr><td>Drag(start=(x1,y1), end=(x2,y2))</td><td>Drag from (x1,y1) to (x2,y2).</td></tr><tr><td>Scroll(start=(x1,y1), end=(x2,y2), direction=&#x27;&#x27;)</td><td>Scroll from (x1,y1) to (x2,y2) with specified direction.</td></tr><tr><td>Type(content=&#x27;&#x27;)</td><td>Type the specified content.</td></tr><tr><td>Launch(app=&#x27;&#x27;)</td><td>Launch the specified app.</td></tr><tr><td>Wait()</td><td>Wait for loading.</td></tr><tr><td>Finished(content=&#x27;&#x27;)</td><td>Finish the task, with optional information.</td></tr><tr><td>CallUser(content=&#x27;&#x27;)</td><td>Conclude the answer for information-retrieval.</td></tr><tr><td>LongPress.box=(x,y))</td><td>Long press at coordinates (x,y).</td></tr><tr><td>PressBack()</td><td>Press the &#x27;back&#x27; button.</td></tr><tr><td>PressHome()</td><td>Press the &#x27;home&#x27; button.</td></tr><tr><td>PressEnter()</td><td>Press the &#x27;enter&#x27; button.</td></tr><tr><td>PressRecent()</td><td>Press the &#x27;recent&#x27; button.</td></tr><tr><td>Hover.box=(x,y))</td><td>Move the mouse cursor to coordinates (x,y) without clicking.</td></tr><tr><td>DoubleClick.box=(x,y))</td><td>Perform a double-click at coordinates (x,y).</td></tr><tr><td>Hotkey(key=[‘ctrl’, ‘c&#x27;])</td><td>Press the specified key combination (e.g., Ctrl+C for copy).</td></tr></table>

# A.2 Grounding

# Grounding Prompt

Output the center point of the position corresponding to the following instruction: {problem}. The output should just be the coordinates of a point, in the format [x,y]. Additionally, if the task is infeasible (e.g., the task is not related to the image), the output should be [-1,-1].

# A.3 Mobile

# Mobile Prompt

```markdown
**You are a GUI Agent**.  
Your task is to analyze a given user task, review current screenshot and previous actions, and determine the next action to complete the task.  
```markdown
**Available Actions
You may execute one of the following functions: 
- Click.box=(x1,y1)) 
- Drag(start=(x1,y1), end=(x2,y2)) 
- Scroll(start=(x1,y1), end=(x2,y2)) 
- Type(content='') 
- Launch(app='') 
- Wait()
- Finished(content='') 
```

- CallUser(content=‘’)  
- LongPress(box=(x1,y1))   
- PressBack()  
- PressHome()  
- PressEnter()  
- PressRecent()

### User Task

{problem}

### Previous Actions

{previous_actions}

### Output Format

<think> your thinking process </think>

<action> the next action </action>

<conclusion> the conclusion about the next action </conclusion>

# ### Instruction

- Make sure you understand the task goal to avoid wrong actions.   
- Make sure you carefully examine the the current screenshot. Sometimes the summarized history might not be reliable, over-claiming some effects.   
- For requests that are questions (or chat messages), remember to use the ‘CallUser’ action to reply to user explicitly before finishing! Then, after you have replied, use the Finished action if the goal is achieved.   
- Consider exploring the screen by using the ‘scroll’ action with different directions to reveal additional content.   
- To copy some text: first select the exact text you want to copy, which usually also brings up the text selection bar, then click the ‘copy’ button in bar.   
- To paste text into a text box, first long press the text box, then usually the text selection bar will appear with a ‘paste’ button in it.

# A.4 Web

# Web Prompt

**You are a GUI Agent**.

Your task is to analyze a given user task, review current screenshot and previous actions, and determine the next action to complete the task.

### Available Actions

You may execute one of the following functions:

- Click(box=(x1,y1))   
- Drag(start=(x1,y1), end=(x2,y2))   
- Scroll(direction $\ c = \ '$ ’down or up’)   
- Type(content=‘’)  
- Launch(url=‘’)   
- Wait()  
- Finished(content=‘’)

- CallUser(content=‘’)  
- LongPress(box=(x1,y1))   
- PressBack()  
- PressHome()  
- PressEnter()  
- PressRecent()   
- Hover(box=(x1,y1))   
- DoubleClick(box=(x1,y1))   
- Hotkey(keys=[‘ctrl’, ‘c’]) # Split keys with comma and wrap each key in single quotes. Do not use more than 3 keys in one Hotkey action.

### User Task

{problem}

### Previous Actions

{previous_actions}

### Output Format

<think> your thinking process </think>

<action> the next action </action>

<conclusion> the conclusion about the next action </conclusion>

### Instruction

- Make sure you understand the task goal to avoid wrong actions.   
- Make sure you carefully examine the the current screenshot. Sometimes the summarized history might not be reliable, over-claiming some effects.   
- For requests that are questions (or chat messages), remember to use the ‘CallUser’ action to reply to user explicitly before finishing! Then, after you have replied, use the Finished action if the goal is achieved.   
- Consider exploring the screen by using the ‘scroll’ action with different directions to reveal additional content.

# A.5 Chinese APPs Prompt

# Chinese APP Prompt

**你是一个 机图 面智能体代理**  
手 形界你的任务是根据历史 作和 前设 态去 行一系列 作来完 的任务。  
### 你可以 的 作以及对应功能 下: - Click(box=(x1,y1))  
用 操 如»点击 作，点击 幕上的指定位置。坐标区间从左上角(0,0)到右下角(999,999)。  
操 屏- Drag(start=(x1,y1), end=(x2,y2))   
» 动 作，从起 坐标长按数秒之后 动到结束坐标。 于 整app布 ，滑动滑拖 操块 证码 。  
验 等- Scroll(start=(x1,y1), end=(x2,y2))   
»滑动 作，从起 坐标 动到结束坐标。 于滚动查 内容，切换选 卡，下 通操 始 拖 用知栏 。坐标区间从左上角(0,0)到右下角(999,999)。  
等- Type(content=‘’)  
»输入 作，在 前激活的输入框输入指定内容。

- Launch(app=‘’)

»启动目标app。 目标app在 前 面不可见时，可以使 该动作 app。

- Wait()

» 面加载。

等待页- Finished(content=‘’)

»任务结束，退出设 接 。

备- CallUser(content=‘’)

»回 的问 者 前 面有 个 合要求的选 时需要 接 。

答用户 题或 当- LongPress(box=(x1,y1))

»长按 作，在指定位置长按一定的时间。该 作可以触发更 功能选 ，例操 操 多制、转发消息，删除 。坐标区间从左上角(0,0)到右下角(999,999)。

- PressBack()

»返回上一个 面，一般 于错误回退 继续 行剩余任务。

- PressHome()

»返回系统桌面，一般 于跨app任务中 速 下一个app 遇到严 错误时回退到系统桌面。

- PressEnter()

»回车 作， 于换行 者在 索框中输入内容之后 行 索 作。

操 用- PressRecent()

» 系统后台 面。

### 任务

用户{problem}

###先前的动作和推理过

{previous_actions}

### 输出格

式<think>你的思考过 </think>

程<action> 行的 作</action>

执 操<conclusion>总结 前 作</conclusion>

### Instruction

-输入内容之前，确保输入框已经被激活（出现键盘 者 ‘ADB Keyboard ON’字样代表输入框已经激活） 。

-在app内 不到任务要求的入口时， 试使 索功能， 者 果 前 面上方存在找 尝选 个 卡， 试使 Scroll 作查看。

多 项 尝 用 操- 果在 行任务的过 中进入到和任务无关的 面，使 PressBack进行回退。

如 执 程 界 用-任务结束之前，确保已经完整准确地完 的任务， 果存在漏做、错做的内容，需要返回 新 行。

# B Experiment Details of All Grounding Benchmarks

Note that in OSWorld-G, we re-calculate the performance of UI-Venus-1.0 with the refusal task, and thus, its results are different from our previous report.

# C Experiment Details of All Navigation Benchmarks

Table 9 Performance comparison on VenusBench-GD. For each benchmark, the best and second-best performing models are indicated in bold and underlined, respectively. Asterisk (*) indicates results that may require verification with original sources.   

<table><tr><td rowspan="2">Models</td><td colspan="4">Basic Tasks</td><td colspan="4">Advanced Tasks</td><td rowspan="2">Overall</td></tr><tr><td>Element</td><td>Visual</td><td>Spatial</td><td>Avg</td><td>Reasoning</td><td>Functional</td><td>Refusal</td><td>Avg</td></tr><tr><td colspan="10">General VLMs</td></tr><tr><td>Qwen3-VL-2B* (Bai et al., 2025a)</td><td>66.6</td><td>79.7</td><td>61.3</td><td>68.2</td><td>12.6</td><td>41.6</td><td>0.0</td><td>15.9</td><td>45.2</td></tr><tr><td>Qwen3-VL-8B* (Bai et al., 2025a)</td><td>73.9</td><td>83.8</td><td>75.5</td><td>76.8</td><td>22.6</td><td>61.3</td><td>6.8</td><td>27.3</td><td>55.1</td></tr><tr><td>Qwen3-VL-30B-A3B* (Bai et al., 2025a)</td><td>68.0</td><td>84.3</td><td>69.2</td><td>72.3</td><td>19.9</td><td>58.6</td><td>11.3</td><td>27.0</td><td>52.4</td></tr><tr><td colspan="10">GUI-specific Models</td></tr><tr><td>OpenCUA-7B (Wang et al., 2025b)</td><td>62.23</td><td>84.39</td><td>67.44</td><td>69.15</td><td>21.32</td><td>49.14</td><td>0.00</td><td>21.43</td><td>48.20</td></tr><tr><td>OpenCUA-32B (Wang et al., 2025b)</td><td>65.49</td><td>78.55</td><td>68.80</td><td>69.64</td><td>29.09</td><td>51.00</td><td>0.00</td><td>25.08</td><td>50.08</td></tr><tr><td>GTA1-7B (Yang et al., 2025)</td><td>63.73</td><td>76.64</td><td>57.05</td><td>64.87</td><td>23.31</td><td>51.14</td><td>0.00</td><td>22.75</td><td>46.38</td></tr><tr><td>GTA1-32B (Yang et al., 2025)</td><td>75.36</td><td>88.08</td><td>76.77</td><td>78.87</td><td>38.84</td><td>67.14</td><td>0.00</td><td>33.25</td><td>58.84</td></tr><tr><td>UI-Venus-1.0-7B (Gu et al., 2025)</td><td>64.30</td><td>78.78</td><td>67.15</td><td>68.66</td><td>24.39</td><td>53.85</td><td>0.00</td><td>23.90</td><td>49.01</td></tr><tr><td>UI-Venus-1.0-72B (Gu et al., 2025)</td><td>81.58</td><td>91.30</td><td>78.81</td><td>83.12</td><td>46.16</td><td>68.86</td><td>51.33</td><td>53.75</td><td>70.23</td></tr><tr><td>Holo2-8B* (H-Company, 2025)</td><td>71.4</td><td>85.8</td><td>77.9</td><td>76.8</td><td>34.0</td><td>63.1</td><td>0.0</td><td>30.2</td><td>56.4</td></tr><tr><td>Holo2-30B-A3B* (H-Company, 2025)</td><td>78.1</td><td>89.7</td><td>81.0</td><td>81.8</td><td>32.2</td><td>68.7</td><td>0.0</td><td>31.0</td><td>59.5</td></tr><tr><td>Step-GUI-4B* (Yan et al., 2025)</td><td>73.9</td><td>81.8</td><td>77.9</td><td>77.0</td><td>26.1</td><td>59.0</td><td>0.0</td><td>25.9</td><td>54.6</td></tr><tr><td>MAI-UI-2B* (Zhou et al., 2025b)</td><td>72.8</td><td>87.1</td><td>76.6</td><td>77.4</td><td>27.3</td><td>62.3</td><td>0.0</td><td>27.3</td><td>55.4</td></tr><tr><td>MAI-UI-8B* (Zhou et al., 2025b)</td><td>81.3</td><td>90.8</td><td>84.5</td><td>84.5</td><td>55.4</td><td>69.1</td><td>0.0</td><td>40.5</td><td>65.2</td></tr><tr><td colspan="10">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>79.4</td><td>85.8</td><td>80.9</td><td>81.4</td><td>22.0</td><td>57.3</td><td>76.3</td><td>49.2</td><td>67.3</td></tr><tr><td>UI-Venus-1.5-8B</td><td>84.2</td><td>93.1</td><td>84.9</td><td>86.6</td><td>38.1</td><td>70.1</td><td>61.6</td><td>54.2</td><td>72.3</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>85.1</td><td>93.2</td><td>86.4</td><td>87.5</td><td>41.8</td><td>68.1</td><td>73.1</td><td>59.0</td><td>75.0</td></tr></table>

Table 10 Performance comparison on ScreenSpot-Pro. For each benchmark, the best and second-best performing models are indicated in bold and underlined, respectively. Asterisk (*) indicates results that may require verification with original sources.   

<table><tr><td rowspan="2">Model</td><td colspan="2">CAD</td><td colspan="2">Dev</td><td colspan="2">Creative</td><td colspan="2">Scientific</td><td colspan="2">Office</td><td colspan="2">OS</td><td colspan="2">Avg.</td></tr><tr><td>Text</td><td>Icon</td><td>Text</td><td>Icon</td><td>Text</td><td>Icon</td><td>Text</td><td>Icon</td><td>Text</td><td>Icon</td><td>Text</td><td>Icon</td><td>Text</td><td>Icon</td></tr><tr><td colspan="15">General VLMs</td></tr><tr><td>Seed1.8 (Seed, 2025a)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>64.3</td></tr><tr><td>Qwen3-VL-2B* (Bai et al., 2025a)</td><td>27.9</td><td>10.9</td><td>57.1</td><td>9.7</td><td>58.1</td><td>16.8</td><td>62.5</td><td>22.7</td><td>73.4</td><td>34.0</td><td>55.1</td><td>19.1</td><td>55.0</td><td>17.4</td></tr><tr><td>Qwen3-VL-8B* (Bai et al., 2025a)</td><td>56.9</td><td>10.9</td><td>75.3</td><td>22.8</td><td>68.2</td><td>16.1</td><td>78.5</td><td>32.7</td><td>80.8</td><td>39.6</td><td>71.0</td><td>20.2</td><td>71.1</td><td>22.8</td></tr><tr><td>Qwen3-VL-30B-A3B* (Bai et al., 2025a)</td><td>51.8</td><td>15.6</td><td>76.0</td><td>24.8</td><td>69.2</td><td>20.3</td><td>76.4</td><td>27.3</td><td>80.8</td><td>37.7</td><td>75.7</td><td>38.2</td><td>70.6</td><td>26.3</td></tr><tr><td colspan="15">GUI-specific Models</td></tr><tr><td>OpenCUA-7B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>50.0</td></tr><tr><td>OpenCUA-32B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>55.3</td></tr><tr><td>OpenCUA-72B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>60.8</td></tr><tr><td>GTA1-7B (Yang et al., 2025)</td><td>66.9</td><td>20.7</td><td>62.6</td><td>18.2</td><td>53.3</td><td>17.2</td><td>76.4</td><td>31.8</td><td>82.5</td><td>50.9</td><td>48.6</td><td>25.9</td><td>65.5</td><td>25.2</td></tr><tr><td>GTA1-32B (Yang et al., 2025)</td><td>83.1</td><td>37.9</td><td>72.2</td><td>25.9</td><td>70.1</td><td>31.3</td><td>84.7</td><td>39.1</td><td>89.3</td><td>64.2</td><td>76.6</td><td>51.7</td><td>78.9</td><td>38.9</td></tr><tr><td>GUI-Owl-7B (Ye et al., 2025)</td><td>64.5</td><td>21.9</td><td>76.6</td><td>31.0</td><td>59.6</td><td>27.3</td><td>79.1</td><td>37.3</td><td>77.4</td><td>39.6</td><td>59.8</td><td>33.7</td><td>-</td><td>54.9</td></tr><tr><td>GUI-Owl-32B (Ye et al., 2025)</td><td>62.4</td><td>28.1</td><td>84.4</td><td>39.3</td><td>65.2</td><td>18.2</td><td>82.6</td><td>39.1</td><td>81.4</td><td>39.6</td><td>70.1</td><td>36.0</td><td>-</td><td>58.0</td></tr><tr><td>UI-Venus-1.0-7B (Gu et al., 2025)</td><td>60.4</td><td>21.9</td><td>74.7</td><td>24.1</td><td>63.1</td><td>14.7</td><td>76.4</td><td>31.8</td><td>75.7</td><td>41.5</td><td>49.5</td><td>22.5</td><td>67.1</td><td>24.3</td></tr><tr><td>UI-Venus-1.0-72B (Gu et al., 2025)</td><td>66.5</td><td>29.7</td><td>84.4</td><td>33.1</td><td>73.2</td><td>30.8</td><td>84.7</td><td>42.7</td><td>83.1</td><td>60.4</td><td>75.7</td><td>36.0</td><td>77.4</td><td>36.8</td></tr><tr><td>Holo2-8B (H-Company, 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>58.9</td></tr><tr><td>Holo2-30B-A3B (H-Company, 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>66.1</td></tr><tr><td>Step-GUI-4B (Yan et al., 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>60.0</td></tr><tr><td>Step-GUI-8B (Yan et al., 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>62.6</td></tr><tr><td>MAI-UI-2B (Zhou et al., 2025b)</td><td>61.4</td><td>23.4</td><td>76.6</td><td>32.4</td><td>69.2</td><td>21.7</td><td>81.2</td><td>34.5</td><td>85.9</td><td>39.6</td><td>68.2</td><td>41.6</td><td>-</td><td>57.4</td></tr><tr><td>MAI-UI-8B (Zhou et al., 2025b)</td><td>72.6</td><td>35.9</td><td>83.8</td><td>52.4</td><td>76.3</td><td>33.6</td><td>79.9</td><td>37.3</td><td>88.7</td><td>60.4</td><td>76.6</td><td>49.4</td><td>-</td><td>65.8</td></tr><tr><td>MAI-UI-32B (Zhou et al., 2025b)</td><td>70.1</td><td>45.3</td><td>86.4</td><td>40.7</td><td>82.8</td><td>37.8</td><td>91.7</td><td>46.4</td><td>90.4</td><td>71.7</td><td>78.5</td><td>34.8</td><td>-</td><td>67.9</td></tr><tr><td colspan="15">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>54.3</td><td>32.8</td><td>70.1</td><td>43.4</td><td>63.6</td><td>28.7</td><td>76.4</td><td>38.2</td><td>81.9</td><td>47.2</td><td>73.8</td><td>51.7</td><td>69.1</td><td>39.4</td></tr><tr><td>UI-Venus-1.5-8B</td><td>75.1</td><td>31.2</td><td>85.7</td><td>54.5</td><td>75.3</td><td>32.9</td><td>86.1</td><td>44.5</td><td>92.7</td><td>66.0</td><td>82.2</td><td>52.8</td><td>82.4</td><td>45.9</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>70.6</td><td>40.6</td><td>87.7</td><td>57.9</td><td>75.8</td><td>41.3</td><td>84.0</td><td>47.3</td><td>89.8</td><td>69.8</td><td>83.2</td><td>56.2</td><td>81.2</td><td>51.0</td></tr></table>

Table 11 Performance comparison on ScreenSpot-V2. For each benchmark, the best and second-best performing models are indicated in bold and underlined, respectively. Asterisk (*) indicates results that may require verification with original sources.   

<table><tr><td rowspan="2">Models</td><td colspan="2">Mobile</td><td colspan="2">Desktop</td><td colspan="2">Web</td><td rowspan="2">Avg</td></tr><tr><td>Text</td><td>Icon/Widget</td><td>Text</td><td>Icon/Widget</td><td>Text</td><td>Icon/Widget</td></tr><tr><td colspan="8">General VLMs</td></tr><tr><td>Qwen3-VL-2B* (Bai et al., 2025a)</td><td>94.1</td><td>80.6</td><td>94.8</td><td>74.3</td><td>89.7</td><td>72.9</td><td>85.6</td></tr><tr><td>Qwen3-VL-8B* (Bai et al., 2025a)</td><td>99.7</td><td>87.7</td><td>94.8</td><td>83.6</td><td>95.3</td><td>85.7</td><td>92.1</td></tr><tr><td>Qwen3-VL-30B-A3B* (Bai et al., 2025a)</td><td>99.0</td><td>87.7</td><td>95.4</td><td>82.9</td><td>95.3</td><td>83.7</td><td>91.7</td></tr><tr><td colspan="8">GUI-specific Models</td></tr><tr><td>OpenCUA-7B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>92.3</td></tr><tr><td>OpenCUA-32B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>93.4</td></tr><tr><td>OpenCUA-72B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>92.9</td></tr><tr><td>GTA1-7B (Yang et al., 2025)</td><td>99.0</td><td>88.6</td><td>94.9</td><td>89.3</td><td>92.3</td><td>86.7</td><td>92.4</td></tr><tr><td>GTA1-32B (Yang et al., 2025)</td><td>99.7</td><td>90.5</td><td>99.0</td><td>94.3</td><td>95.7</td><td>90.1</td><td>95.2</td></tr><tr><td>GUI-Owl-7B (Ye et al., 2025)</td><td>99.0</td><td>92.4</td><td>96.9</td><td>85.0</td><td>93.6</td><td>85.2</td><td>92.8</td></tr><tr><td>GUI-Owl-32B (Ye et al., 2025)</td><td>98.6</td><td>90.0</td><td>97.9</td><td>87.8</td><td>94.4</td><td>86.7</td><td>93.2</td></tr><tr><td>UI-Venus-1.0-7B (Gu et al., 2025)</td><td>99.0</td><td>90.0</td><td>97.0</td><td>90.7</td><td>96.2</td><td>88.7</td><td>94.1</td></tr><tr><td>UI-Venus-1.0-72B (Gu et al., 2025)</td><td>99.7</td><td>93.8</td><td>95.9</td><td>90.0</td><td>96.2</td><td>92.6</td><td>95.3</td></tr><tr><td>Holo2-8B (H-Company, 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>93.2</td></tr><tr><td>Holo2-30B-A3B (H-Company, 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>94.9</td></tr><tr><td>Step-GUI-4B (Yan et al., 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>93.6</td></tr><tr><td>Step-GUI-8B (Yan et al., 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>95.1</td></tr><tr><td>MAI-UI-2B (Zhou et al., 2025b)</td><td>99.3</td><td>87.2</td><td>97.4</td><td>88.6</td><td>94.0</td><td>84.7</td><td>92.5</td></tr><tr><td>MAI-UI-8B (Zhou et al., 2025b)</td><td>99.3</td><td>89.1</td><td>99.0</td><td>92.1</td><td>97.9</td><td>91.1</td><td>95.2</td></tr><tr><td>MAI-UI-32B (Zhou et al., 2025b)</td><td>99.0</td><td>92.9</td><td>99.5</td><td>93.6</td><td>97.4</td><td>94.6</td><td>96.5</td></tr><tr><td colspan="8">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>98.6</td><td>91.0</td><td>93.3</td><td>92.9</td><td>93.2</td><td>85.7</td><td>92.8</td></tr><tr><td>UI-Venus-1.5-8B</td><td>99.3</td><td>92.9</td><td>96.4</td><td>92.9</td><td>98.3</td><td>93.1</td><td>95.9</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>99.3</td><td>94.8</td><td>95.9</td><td>94.3</td><td>97.9</td><td>93.1</td><td>96.2</td></tr></table>

Table 12 Performance comparison on MMbench-GUI-L2. For each benchmark, the best and second-best performing models are indicated in bold and underlined, respectively. Asterisk (*) indicates results that may require verification with original sources.   

<table><tr><td rowspan="2">Model</td><td colspan="2">Windows</td><td colspan="2">MacOS</td><td colspan="2">Linux</td><td colspan="2">iOS</td><td colspan="2">Android</td><td colspan="2">Web</td><td rowspan="2">Avg.</td></tr><tr><td>Bas.</td><td>Adv.</td><td>Bas.</td><td>Adv.</td><td>Bas.</td><td>Adv.</td><td>Bas.</td><td>Adv.</td><td>Bas.</td><td>Adv.</td><td>Bas.</td><td>Adv.</td></tr><tr><td colspan="14">General VLMs</td></tr><tr><td>Qwen3-VL-2B* (Bai et al., 2025a)</td><td>82.3</td><td>41.2</td><td>79.1</td><td>45.4</td><td>67.5</td><td>44.4</td><td>92.0</td><td>68.2</td><td>91.6</td><td>69.6</td><td>85.8</td><td>52.9</td><td>69.5</td></tr><tr><td>Qwen3-VL-8B* (Bai et al., 2025a)</td><td>88.6</td><td>62.5</td><td>86.1</td><td>66.8</td><td>72.8</td><td>57.1</td><td>95.9</td><td>83.9</td><td>95.8</td><td>84.8</td><td>94.8</td><td>72.7</td><td>81.4</td></tr><tr><td>Qwen3-VL-30B-A3B* (Bai et al., 2025a)</td><td>87.8</td><td>69.9</td><td>85.2</td><td>68.8</td><td>78.0</td><td>60.7</td><td>96.5</td><td>84.5</td><td>96.3</td><td>88.5</td><td>96.5</td><td>78.6</td><td>83.7</td></tr><tr><td colspan="14">GUI-specific Models</td></tr><tr><td>GUI-Owl-7B (Ye et al., 2025)</td><td>86.4</td><td>61.8</td><td>81.7</td><td>64.5</td><td>74.4</td><td>61.7</td><td>94.9</td><td>83.0</td><td>95.8</td><td>83.7</td><td>93.2</td><td>72.7</td><td>80.5</td></tr><tr><td>GUI-Owl-32B (Ye et al., 2025)</td><td>85.6</td><td>65.1</td><td>84.9</td><td>67.1</td><td>77.0</td><td>63.3</td><td>95.2</td><td>85.5</td><td>96.1</td><td>87.0</td><td>95.5</td><td>80.8</td><td>83.0</td></tr><tr><td>Holo2-8B (H-Company, 2025)</td><td>90.8</td><td>70.2</td><td>87.5</td><td>71.4</td><td>78.5</td><td>60.2</td><td>96.2</td><td>88.2</td><td>96.3</td><td>87.9</td><td>95.5</td><td>77.9</td><td>84.5</td></tr><tr><td>Holo2-30B-A3B (H-Company, 2025)</td><td>91.9</td><td>72.8</td><td>88.1</td><td>74.9</td><td>84.3</td><td>67.3</td><td>96.5</td><td>89.7</td><td>96.3</td><td>90.1</td><td>96.5</td><td>82.5</td><td>86.8</td></tr><tr><td>Step-GUI-4B (Yan et al., 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>84.0</td></tr><tr><td>Step-GUI-8B (Yan et al., 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>85.6</td></tr><tr><td>MAI-UI-2B (Zhou et al., 2025b)</td><td>84.9</td><td>64.0</td><td>89.3</td><td>72.5</td><td>75.4</td><td>60.2</td><td>95.2</td><td>85.2</td><td>96.3</td><td>84.2</td><td>92.9</td><td>76.0</td><td>82.6</td></tr><tr><td>MAI-UI-8B (Zhou et al., 2025b)</td><td>92.3</td><td>74.3</td><td>90.7</td><td>86.4</td><td>81.2</td><td>67.3</td><td>97.1</td><td>90.0</td><td>97.5</td><td>92.7</td><td>95.8</td><td>86.0</td><td>88.8</td></tr><tr><td>MAI-UI-32B (Zhou et al., 2025b)</td><td>93.0</td><td>78.7</td><td>92.8</td><td>87.6</td><td>86.9</td><td>77.6</td><td>97.1</td><td>92.4</td><td>98.0</td><td>93.2</td><td>96.1</td><td>92.5</td><td>91.3</td></tr><tr><td colspan="14">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>88.2</td><td>61.8</td><td>82.3</td><td>65.6</td><td>77.0</td><td>60.7</td><td>92.7</td><td>80.3</td><td>93.3</td><td>83.9</td><td>94.8</td><td>72.1</td><td>80.3</td></tr><tr><td>UI-Venus-1.5-8B</td><td>92.6</td><td>74.6</td><td>86.1</td><td>82.1</td><td>84.3</td><td>67.3</td><td>97.1</td><td>89.4</td><td>96.9</td><td>92.4</td><td>96.8</td><td>86.0</td><td>88.1</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>91.5</td><td>76.5</td><td>88.1</td><td>76.6</td><td>85.9</td><td>69.9</td><td>96.5</td><td>93.0</td><td>97.2</td><td>93.8</td><td>96.5</td><td>87.7</td><td>88.6</td></tr></table>

Table 13 Performance comparison on OS-World-G. For each benchmark, the best and second-best performing models are indicated in bold and underlined, respectively. Asterisk (*) indicates results that may require verification with original sources.   

<table><tr><td>Models</td><td>Text Matching</td><td>Element Recognition</td><td>Layout Understanding</td><td>Fine-grained Manipulation</td><td>Refusal</td><td>Avg</td></tr><tr><td colspan="7">General VLMs</td></tr><tr><td>Qwen3-VL-2B* (Bai et al., 2025a)</td><td>60.9</td><td>49.7</td><td>57.3</td><td>38.9</td><td>0.0</td><td>47.7</td></tr><tr><td>Qwen3-VL-8B* (Bai et al., 2025a)</td><td>71.6</td><td>59.4</td><td>61.3</td><td>49.7</td><td>1.9</td><td>57.4</td></tr><tr><td>Qwen3-VL-30B-A3B* (Bai et al., 2025a)</td><td>73.9</td><td>65.2</td><td>67.2</td><td>51.0</td><td>5.6</td><td>61.2</td></tr><tr><td colspan="7">GUI-specific Models</td></tr><tr><td>OpenCUA-7B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>55.3</td></tr><tr><td>OpenCUA-32B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>59.6</td></tr><tr><td>GTA1-7B (Yang et al., 2025)</td><td>42.1</td><td>65.7</td><td>62.7</td><td>56.1</td><td>0.0</td><td>55.1</td></tr><tr><td>GTA1-32B (Yang et al., 2025)</td><td>63.2</td><td>78.4</td><td>73.3</td><td>65.2</td><td>0.0</td><td>65.2</td></tr><tr><td>GUI-Owl-7B (Ye et al., 2025)</td><td>64.8</td><td>63.6</td><td>61.3</td><td>41.0</td><td>-</td><td>55.9</td></tr><tr><td>GUI-Owl-32B (Ye et al., 2025)</td><td>67.0</td><td>64.5</td><td>67.2</td><td>45.6</td><td>-</td><td>58.0</td></tr><tr><td>UI-TARS-1.5-7B (Seed, 2025b)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>52.8</td></tr><tr><td>UI-Venus-1.0-7B (Gu et al., 2025)</td><td>74.6</td><td>60.5</td><td>61.5</td><td>45.5</td><td>-</td><td>54.6</td></tr><tr><td>UI-Venus-1.0-72B (Gu et al., 2025)</td><td>82.1</td><td>71.2</td><td>70.7</td><td>64.4</td><td>-</td><td>62.2</td></tr><tr><td>Holo2-8B* (H-Company, 2025)</td><td>74.3</td><td>68.2</td><td>67.6</td><td>59.1</td><td>0.0</td><td>63.5</td></tr><tr><td>Holo2-30B-A3B* (H-Company, 2025)</td><td>77.0</td><td>68.8</td><td>70.0</td><td>59.7</td><td>0.0</td><td>65.2</td></tr><tr><td>Step-GUI-4B* (Yan et al., 2025)</td><td>70.1</td><td>65.8</td><td>67.6</td><td>53.0</td><td>0.0</td><td>60.5</td></tr><tr><td>MAI-UI-2B (Zhou et al., 2025b)</td><td>62.8</td><td>56.7</td><td>59.3</td><td>40.3</td><td>-</td><td>52.0</td></tr><tr><td>MAI-UI-8B (Zhou et al., 2025b)</td><td>72.0</td><td>63.3</td><td>66.0</td><td>51.0</td><td>-</td><td>60.1</td></tr><tr><td>MAI-UI-32B (Zhou et al., 2025b)</td><td>73.6</td><td>72.4</td><td>73.9</td><td>57.7</td><td>-</td><td>67.6</td></tr><tr><td colspan="7">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>67.4</td><td>66.1</td><td>66.4</td><td>44.3</td><td>7.4</td><td>59.4</td></tr><tr><td>UI-Venus-1.5-8B</td><td>79.7</td><td>76.1</td><td>72.3</td><td>60.4</td><td>22.2</td><td>69.7</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>80.1</td><td>76.1</td><td>75.1</td><td>61.1</td><td>9.3</td><td>70.6</td></tr></table>

Table 14 Performance comparison on OS-World-G-Refine. For each benchmark, the best and second-best performing models are indicated in bold and underlined, respectively. Asterisk (*) indicates results that may require verification with original sources.   

<table><tr><td>Models</td><td>Text Matching</td><td>Element Recognition</td><td>Layout Understanding</td><td>Fine-grained Manipulation</td><td>Refusal</td><td>Avg</td></tr><tr><td colspan="7">General VLMs</td></tr><tr><td>Qwen3-VL-2B* (Bai et al., 2025a)</td><td>73.2</td><td>64.2</td><td>70.8</td><td>47.0</td><td>0.0</td><td>60.6</td></tr><tr><td>Qwen3-VL-8B* (Bai et al., 2025a)</td><td>78.2</td><td>71.5</td><td>72.3</td><td>55.7</td><td>1.9</td><td>67.0</td></tr><tr><td>Qwen3-VL-30B-A3B* (Bai et al., 2025a)</td><td>77.8</td><td>75.8</td><td>74.7</td><td>54.4</td><td>5.6</td><td>69.3</td></tr><tr><td colspan="7">GUI-specific Models</td></tr><tr><td>OpenCUA-32B (Wang et al., 2025b)</td><td>63.2</td><td>79.9</td><td>84.9</td><td>62.1</td><td>7.4</td><td>70.2</td></tr><tr><td>GTA1-7B (Yang et al., 2025)</td><td>63.2</td><td>82.1</td><td>74.2</td><td>70.5</td><td>0.0</td><td>67.7</td></tr><tr><td>GTA1-32B (Yang et al., 2025)</td><td>63.2</td><td>83.6</td><td>84.4</td><td>70.5</td><td>0.0</td><td>72.2</td></tr><tr><td>UI-Venus-1.0-7B (Gu et al., 2025)</td><td>74.6</td><td>60.5</td><td>61.5</td><td>45.5</td><td>-</td><td>58.8</td></tr><tr><td>UI-Venus-1.0-72B (Gu et al., 2025)</td><td>82.1</td><td>71.2</td><td>70.7</td><td>64.4</td><td>-</td><td>70.4</td></tr><tr><td>Holo2-8B* (H-Company, 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>70.1</td></tr><tr><td>Holo2-30B-A3B* (H-Company, 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>76.1</td></tr><tr><td>Step-GUI-4B* (Yan et al., 2025)</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>66.9</td></tr><tr><td>MAI-UI-2B (Zhou et al., 2025b)</td><td>70.9</td><td>69.1</td><td>72.7</td><td>47.7</td><td>-</td><td>63.5</td></tr><tr><td>MAI-UI-8B (Zhou et al., 2025b)</td><td>77.4</td><td>73.0</td><td>78.3</td><td>55.7</td><td>-</td><td>68.6</td></tr><tr><td>MAI-UI-32B (Zhou et al., 2025b)</td><td>79.7</td><td>79.4</td><td>81.0</td><td>61.7</td><td>-</td><td>73.9</td></tr><tr><td colspan="7">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>75.1</td><td>70.0</td><td>73.5</td><td>52.3</td><td>7.4</td><td>65.6</td></tr><tr><td>UI-Venus-1.5-8B</td><td>82.4</td><td>81.5</td><td>80.2</td><td>59.7</td><td>22.2</td><td>74.1</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>83.1</td><td>82.1</td><td>83.4</td><td>65.8</td><td>9.3</td><td>76.4</td></tr></table>

Table 15 Performance comparison on UI-Vision. For each benchmark, the best and second-best performing models are indicated in bold and underlined, respectively.Asterisk (*) indicates results that may require verification with original sources.   

<table><tr><td>Models</td><td>Basic</td><td>Functional</td><td>Spatial</td><td>Avg</td></tr><tr><td colspan="5">General VLMs</td></tr><tr><td>Qwen3-VL-2B* (Bai et al., 2025a)</td><td>16.4</td><td>19.1</td><td>4.6</td><td>13.1</td></tr><tr><td>Qwen3-VL-8B* (Bai et al., 2025a)</td><td>27.8</td><td>29.6</td><td>9.4</td><td>21.9</td></tr><tr><td>Qwen3-VL-30B-A3B* (Bai et al., 2025a)</td><td>31.2</td><td>31.9</td><td>14.6</td><td>25.6</td></tr><tr><td colspan="5">GUI-specific Models</td></tr><tr><td>OpenCUA-7B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>29.7</td></tr><tr><td>OpenCUA-32B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>33.3</td></tr><tr><td>OpenCUA-72B (Wang et al., 2025b)</td><td>-</td><td>-</td><td>-</td><td>37.3</td></tr><tr><td>UI-Venus-1.0-7B (Gu et al., 2025)</td><td>36.1</td><td>32.8</td><td>11.9</td><td>26.5</td></tr><tr><td>UI-Venus-1.0-72B (Gu et al., 2025)</td><td>45.6</td><td>42.3</td><td>23.7</td><td>36.8</td></tr><tr><td>Holo2-8B* (H-Company, 2025)</td><td>43.6</td><td>43.5</td><td>19.7</td><td>35.1</td></tr><tr><td>Holo2-30B-A3B* (H-Company, 2025)</td><td>51.0</td><td>50.1</td><td>23.2</td><td>40.9</td></tr><tr><td>Step-GUI-4B* (Yan et al., 2025)</td><td>39.2</td><td>36.5</td><td>15.7</td><td>30.0</td></tr><tr><td>MAI-UI-2B (Zhou et al., 2025b)</td><td>41.0</td><td>41.2</td><td>10.4</td><td>30.3</td></tr><tr><td>MAI-UI-8B (Zhou et al., 2025b)</td><td>51.7</td><td>49.6</td><td>22.5</td><td>40.7</td></tr><tr><td>MAI-UI-32B (Zhou et al., 2025b)</td><td>59.1</td><td>57.1</td><td>26.9</td><td>47.1</td></tr><tr><td colspan="5">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>63.5</td><td>51.5</td><td>21.6</td><td>44.8</td></tr><tr><td>UI-Venus-1.5-8B</td><td>56.3</td><td>52.4</td><td>32.0</td><td>46.5</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>69.0</td><td>59.3</td><td>37.4</td><td>54.7</td></tr></table>

Table 16 Performance comparison on VenusBench-Mobile. The best performing model is indicated in bold.   

<table><tr><td>Agent</td><td>FA</td><td>CF</td><td>VA</td><td>MR</td><td>GSA</td><td>GUIM</td><td>HGB</td><td>NR</td><td>BC</td><td>Total</td></tr><tr><td colspan="11">General VLMs</td></tr><tr><td>Qwen3-VL-8B Bai et al. (2025a)</td><td>18.2</td><td>4.6</td><td>18.8</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>6.3</td><td>10.0</td><td>6.7</td></tr><tr><td>Qwen3-VL-30B-A3B Bai et al. (2025a)</td><td>22.7</td><td>4.6</td><td>18.8</td><td>0.0</td><td>0.0</td><td>0.0</td><td>5.9</td><td>6.3</td><td>10.0</td><td>8.7</td></tr><tr><td colspan="11">GUI-specific Models</td></tr><tr><td>UI-Venus-7B Gu et al. (2025)</td><td>13.6</td><td>4.6</td><td>25.0</td><td>0.0</td><td>10.0</td><td>0.0</td><td>0.0</td><td>18.8</td><td>0.0</td><td>8.1</td></tr><tr><td>UI-Venus-72B Gu et al. (2025)</td><td>22.7</td><td>4.6</td><td>12.5</td><td>0.0</td><td>10.0</td><td>0.0</td><td>17.7</td><td>50.0</td><td>0.0</td><td>15.4</td></tr><tr><td>GUI-Owl-7B Ye et al. (2025)</td><td>13.6</td><td>0.0</td><td>18.8</td><td>0.0</td><td>0.0</td><td>11.1</td><td>2.9</td><td>12.5</td><td>0.0</td><td>6.7</td></tr><tr><td>MA3(GUI-Owl-7B) Ye et al. (2025)</td><td>18.2</td><td>9.1</td><td>6.3</td><td>0.0</td><td>0.0</td><td>0.0</td><td>11.8</td><td>31.3</td><td>20.0</td><td>12.1</td></tr><tr><td>MAI-UI-2B Zhou et al. (2025b)</td><td>9.1</td><td>0.0</td><td>18.8</td><td>0.0</td><td>0.0</td><td>0.0</td><td>0.0</td><td>25.0</td><td>10.0</td><td>6.7</td></tr><tr><td>MAI-UI-8B Zhou et al. (2025b)</td><td>9.1</td><td>13.6</td><td>25.0</td><td>0.0</td><td>10.0</td><td>11.1</td><td>5.9</td><td>31.3</td><td>10.0</td><td>12.8</td></tr><tr><td colspan="11">Ours</td></tr><tr><td>UI-Venus-1.5-2B</td><td>22.7</td><td>0.0</td><td>12.5</td><td>0.0</td><td>10.0</td><td>11.1</td><td>2.9</td><td>18.8</td><td>0.0</td><td>8.7</td></tr><tr><td>UI-Venus-1.5-8B</td><td>22.7</td><td>0.0</td><td>25.0</td><td>0.0</td><td>0.0</td><td>22.2</td><td>8.8</td><td>50.0</td><td>20.0</td><td>16.1</td></tr><tr><td>UI-Venus-1.5-30B-A3B</td><td>40.9</td><td>0.0</td><td>37.5</td><td>10.0</td><td>20.0</td><td>22.2</td><td>14.7</td><td>43.8</td><td>0.0</td><td>21.5</td></tr></table>