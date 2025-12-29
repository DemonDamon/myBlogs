# Sophia: A Persistent Agent Framework of Artificial Life

Mingyang Sun $^{1,2}$ , Feng Hong $^{3}$ , and Weinan Zhang $^{2,4*}$

<sup>1</sup>Westlake University, <sup>2</sup>Shanghai Innovation Institute  
<sup>3</sup>Project Cuddlepark Team, <sup>4</sup>Shanghai Jiao Tong University  
sunmingyang@westlake.edu.cn, wnzhang@sjtu.edu.cn

# Abstract

The rapid development of Large Language Models (LLMs) has elevated AI agents from task-specific tools to long-lived, decision-making entities capable of independent planning and strategic collaboration. However, most existing architectures remain reactive: they rely on manually crafted configurations that remain static after deployment, designed for narrow tasks or fixed scenarios. These systems excel at perception (System 1) and deliberation (System 2), yet lack a persistent meta-layer capable of maintaining identity, verifying internal reasoning, and aligning short-term tasks with long-term survival.

In this work, we first propose a third stratum, System 3, that presides over the agent's narrative identity and long-horizon adaptation. The framework maps selected psychological constructs (e.g., meta-cognition, theory-of-mind, intrinsic motivation, episodic memory) to concrete computational modules, thereby translating abstract notions of artificial life into implementable design requirements. These ideas coalesce in Sophia, a "Persistent Agent" wrapper that grafts a continuous self-improvement loop onto any LLM-centric System 1/2 stack. Sophia is driven by four synergistic mechanisms: process supervised thought search that curates and audits emerging thoughts, an memory module that maintains narrative identity, dynamic user and self models that track external and internal beliefs, and a hybrid reward system balancing environmental feedback with introspective drives. Together, transform the highly repetitive reasoning episodes of a primitive agent into an endless, self-driven reasoning phase dedicated to diverse goals, enabling autobiographical memory, identity continuity, and transparent narrative explanations of behavior.

Although the paper is primarily conceptual, grounding System 3 in decades of cognitive theory, we provide a compact engineering prototype to anchor the discussion. In a deployment spanning prolonged durations within a dynamic web environment, Sophia demonstrated robust operational persistence through autonomous goal generation. Quantitatively, Sophia independently initiates and executes various intrinsic tasks while achieving an  $80\%$  reduction in reasoning steps for recurring operations. Notably, meta-cognitive persistence yielded a  $40\%$  gain in success for high-complexity tasks, effectively bridging the performance gap between simple and sophisticated goals. Qualitatively, System 3 exhibited a coherent narrative identity and an innate capacity for task organization. By fusing psychological insight with a lightweight reinforcement-learning core, the persistent agent architecture advances a possible practical pathway toward artificial life.

Keywords: Persistent Agent, LLM Agents, System 3, Artificial Life

# 1 Introduction

The rapid proliferation of large language models (LLMs) has catalyzed a paradigm shift in AI agents, transforming them from single task executors into long-lived sophisticated cognitive entities endowed with capabilities for autonomous planning, strategic deliberation, and collaborative engagement (Achiam et al., 2023; Grattafori et al., 2024; Hurst et al., 2024; Guo et al., 2025; Yang et al., 2025). This technological leap is reshaping expectations across science, industry, and everyday applications (Yang et al., 2024; Chkirbene et al., 2024; Ren et al., 2025; Li et al., 2024). Yet despite these breakthroughs, most existing agent frameworks remain anchored to manually crafted configurations that remain static after deployment. Once shipped, they cannot revise their skill set, develop new tasks, or integrate unfamiliar knowledge without human engineers in the loop. Lacking the intrinsic motivation and self-improvement capabilities inherent to living systems, today's agents remain unable to achieve sustained growth or open-ended adaptation. Infusing AI agents with these lifelike principles, enabling autonomous self-reconfiguration while maintaining operational coherence, has thus emerged as a critical frontier in AI research.

Within prevailing agent architectures, cognition is typically partitioned into two complementary subsystems (Li et al., 2025). System 1 embodies rapid, heuristic faculties—perception, retrieval, and instinctive response. System 2, by contrast, governs slow, deliberate reasoning. It employs chain-of-thought planning, multi-step search, counterfactual simulation, and consistency checks to refine or override System 1's impulses. In practical LLM agents, this often manifests as a reasoning loop that expands prompts with scratch-pad deliberations, validates tool outputs, and aligns final responses with user goals. While the synergy of these two layers enables impressive task performance, both remain confined to static configurations and predetermined task scheduling. Even in cases where agents support continual learning, such updates typically follow an externally defined task schedule rather than being self-directed. Consequently, the agent can neither update its reflexive priors nor revise its thought process when encountering truly novel domains.

This rigidity highlights the necessity of a higher-order "System 3", which is a meta-cognitive layer that monitors, audits, and continuously adapts both underlying systems, thereby enabling the entire cognitive architecture to sustain ongoing learning. In this work, we ground System 3 in four foundational theories from cognitive psychology:

Meta-cognition (Shaughnessy et al., 2008; Dunlosky & Metcalfe, 2008): a self-reflective monitor that inspects ongoing thought traces, flags logical fallacies, and selectively rewrites its own procedures;  
- Theory-of-Mind (Frith & Frith, 2005; Wellman, 2018): an explicit model of actors (humans or agents) that infers their beliefs, desires, and intentions to guide cooperation and learning;  
- Intrinsic Motivation (Fishbach & Woolley, 2022): an internal reward generator that balances extrinsic task success with curiosity-driven exploration, enabling the agent to prioritize long-term competence over short-term gains.  
- Episodic Memory (Tulving, 2002; Ezzyat & Davachi, 2011): A structured autobiographical record that stores, indexes, and retrieves past experiences, providing crucial context for interpreting current events and planning future actions.

By integrating these components into a persistent control loop, System 3 turns an otherwise static agent into a self-aware learner that can not only reason about the world but also reason about—and iteratively improve—its own reasoning process.

Such a layer is indispensable for three fundamental reasons especially in the context of artificial life (Langton, 1997; 2019). First, real-world environments are non-stationary: objectives shift, constraints evolve, and previously unseen tasks emerge without warning. Agents devoid of self-reconfiguration inevitably ossify, leading to performance decay or catastrophic failure. Second,

sustained autonomy demands identity continuity; without a mechanism to maintain a coherent self-model across sessions, an agent cannot accumulate autobiographical knowledge, assess longitudinal progress, or ensure behavioral consistency. Third, safety and alignment require transparent introspection: only a meta-cognitive agent can audit its decision pathways in real time and correct misaligned incentives before they propagate into harmful actions. In short, System 3 elevates agents from transient problem-solvers to adaptive, trustworthy partners capable of lifelong learning in open-ended environments.

To operationalize System 3 in a deployable setting, we present the persistent agent, Sophia, which is a compact, modular framework that endows any LLM-centric System 1/2 stack with a continual self-improvement loop. The design hinges on the following reinforcing mechanisms.

- Process-Supervised Thought Search captures raw chain-of-thought traces, filters them through self-critique prompts, and stores only validated reasoning paths for future reuse, turning stochastic deliberations into reusable cognitive assets.  
- A Memory Module maintains a structured memory graph of goals, experiences, and self-assessments, giving the agent a stable narrative identity that persists across reboots and task domains.  
- A Self-Model records the agent's capabilities, terminal creed and intrinsic state; gaps detected here are immediately feedback as new learning targets. A User-Model maintains a live belief state for each user—goals, social relationship and human preferences.  
- A Hybrid Reward Module blends external task feedback with intrinsic signals—curiosity, coherence, and self-consistency—so the agent not only pursues immediate goals but also maximizes long-term competence.

Together, these components create an end-to-end meta-cognitive loop: the agent plans, acts, reflects on its performance, updates its procedures, and re-aligns future behavior without human intervention.

This work makes the following key contributions:

- We introduce the conceptualization of a System 3 architecture for AI agents, grounded in integrative cognitive psychological foundations including meta-cognition, theory of mind, intrinsic motivation, and episodic memory.  
- We present Sophia, the first computationally realizable agent system for artificial life capable of generating its own learning goals, curating personalized skill curricula, and sustaining autonomous self-adaptation without external task scheduling or reward engineering.  
- We demonstrate, through a 24-hour continuous deployment in a web simulation environment, that our approach enables sustained autonomy, coherent identity persistence, and open-ended competency growth—marking a significant step toward artificial agents that exhibit lifelike learning and self-evolution.

# 2 Related Work

# 2.1 Continual Learning

Our work builds upon yet significantly extends the field of Continual Learning (CL) (Wang et al., 2024), also known as lifelong learning, which aims to enable machine learning models to learn sequentially from a stream of data while mitigating the problem of catastrophic forgetting—where learning new tasks causes abrupt degradation of performance on previously learned ones. Prominent strategies include architectural approaches (e.g., adding new parameters or modules) (Lu et al.,

2024), regularization-based methods (Ahn et al., 2019) that constrain weight updates to protect important parameters for old tasks, and memory-replay methods (Chaudhry et al., 2019; Lopez-Paz & Ranzato, 2017) that maintain a small buffer of past examples for rehearsal.

In the context of large language models (LLMs), continual learning has gained significant attention (Fang et al., 2025; Wang et al., 2024). Zheng et al. (2025a) provide a comprehensive survey specifically focused on lifelong learning methods for LLMs, categorizing approaches into internal and external knowledge strategies. Ke & Liu (2022) explore continual learning in natural language processing tasks, emphasizing techniques to prevent catastrophic forgetting and enable knowledge transfer. Recently, continual pre-training, instruction tuning, and alignment strategies for LLMs have attracted more attention from researchers (Zhou et al., 2024; Zheng et al., 2025b).

While the existing methods have achieved considerable success in predefined task sequences, they primarily operate within a static learning paradigm where the objectives, task boundaries, and data distributions are externally defined and provided to the model. In contrast, our concept of a persistent agent subsumes continual learning as one component of a larger cognitive architecture, see Figure 1. Whereas CL systems are typically passive learners that acquire skills from an externally curated task scheduling, a persistent agent is an active, self-directed learner. It not only mitigates forgetting but also autonomously generates its own goals, constructs its own learning curricula, and governs its own learning process through meta-cognitive control. This shift, from merely adapting to a given data stream to proactively seeking knowledge and self-improvement, represents a fundamental evolution from passive continual learning towards autonomous, open-ended development.

![](images/0231ee39667e9ef35866fe5792191726901a1117d2ace7214267d9a44d498884.jpg)  
(a) Continual Learning of Agent.

![](images/2af78a9b326147c491c14e5283d6e4d7bbdf3e75ef422f7fc9c4c3bb8f904fd0.jpg)  
(b) Persistent Agent for Artificial Life.  
Figure 1: Paradigm comparison of continual learning and persistent agent. (a) Continual-learning agents follow an externally defined schedule to update their model only when a new assignment is pushed to them. (b) A persistent agent runs an internal goal-feedback loop: it autonomously selects goals, acts in the environment, evaluates the outcome, and refines its next goals, enabling open-ended, self-directed adaptation.

# 2.2 Forward Learning and Backward Learning in LLMs

The learning processes in Large Language Models (LLMs) can be conceptually categorized into two paradigms: forward learning and post training. This distinction is crucial for understanding how our persistent agent achieves continuous adaptation.

Forward Learning refers to the model's ability to acquire and internalize new knowledge during the inference stage, without any weight updates. This is primarily achieved through in-context learning (Li, 2023), where a model conditions on a prompt containing demonstrations or new information and immediately applies this context to complete the task at hand. While powerful for few-shot adaptation, forward learning is transient; the knowledge is ephemeral and confined to the current session, leaving no lasting trace in the model's parameters.

Post Training, in contrast, denotes the traditional process of updating the model's weights based on new data, typically through fine-tuning (Zhang et al., 2024; Wu et al., 2025) or reinforcement learning from human feedback (RLHF) (Bai et al., 2022; Lambert, 2025). This form of learning results in persistent, long-term changes to the model's behavior and knowledge base. However,

it is often computationally expensive, requires careful curation of datasets to avoid catastrophic forgetting, and typically occurs in offline batches rather than continuously.

Our persistent agent architecture seamlessly integrates both paradigms. In our architecture, the sub-modules of System 3 collectively establish a dynamic contextual foundation throughout the agent's lifelong operation, enabling rapid, on-the-fly adaptation and reasoning via forward learning. Meanwhile, when capability gaps are identified—such as insufficient reasoning ability or skill deficiencies—System 2 can undergo enhancement through backward learning, guided by the reward model within System 3 that aligns updates with meta-cognitive goals and intrinsic motivations.

# 3 The Psychological Pillars of System 3

The ambition to evolve AI agents from sophisticated tools into digital beings necessitates a leap in cognitive architecture. We posit that this leap requires a System 3—a supervisory cognitive layer responsible for integration, self-reflection, and long-term coherence. Whereas System 1 delivers rapid, heuristic responses and System 2 performs deliberate analytical reasoning, System 3 orchestrates the meta-cognitive processes that underpin a sense of self and enduring purpose. To ground this architecture in a plausible model of intelligence, we draw on four foundational constructs from cognitive psychology—Theory of Mind, Episodic Memory, Meta-Cognition (with a Self-Model) and Intrinsic Motivation. These concepts provide the necessary framework for an agent to not only think but to think about its own thinking, to learn from its experiences, and to act with a degree of autonomy that transcends predefined tasks.

The interplay of these core components can be visualized in the following diagram, which outlines the core information flow within our proposed System 3 architecture:

The Meta-Cognitive Monitor—the core of System 3-ingests salient events from the environment, consults four psychological modules, and issues updates or directives to Systems 2 and 1.

![](images/f962db1bd2c1f4b091af48b429bac510ee9bb7fda3ff4e5a4ed6b4be68c34253.jpg)  
Figure 2: Schematic of the proposed System 3 architecture. A central Meta-Cognitive Executive Monitor receives salient events from the environment and integrates signals from four psychological pillars—Theory of Mind (belief and intention modeling, user/agent prediction), Episodic Memory (timestamped, context-rich event store with retrieval), Self Model (coherence, capability assessment, state representation), and Intrinsic Motivation (curiosity, mastery drive, autonomy striving). Guided by this aggregated context, the monitor performs process control and resource allocation, issuing executive oversight commands to the underlying System 2/1 perception-and-reasoning stack.

# 3.1 Foundational Constructs

Theory of Mind is the capacity to attribute mental states—such as beliefs, intents, and knowledge—to others. For a persistent agent, this transcends simple user intent recognition. It allows the agent to build rich, dynamic models of the individuals it interacts with, anticipating their needs and reactions. This capability is fundamental for engaging in truly collaborative and adaptive interactions, as the agent can tailor its communication and actions based on its understanding of the user's perspective.

Episodic Memory provides the substrate for an autobiographical self. Rather than storing facts in isolation, this system records experiences as contextualized events, complete with temporal and situational markers. This allows the agent to construct a narrative of its own history, which is indispensable for maintaining consistency over time. By recalling past successes and failures in full context, the agent can learn in a more nuanced way, avoiding past errors and building upon strategies that have proven effective. To keep storage tractable, a tiered retrieval scheme is neccesary: high-level summaries for fast search, with raw traces lazily retrieved only when relevance exceeds a threshold.

Meta-Cognition with Self-Model form the executive heart of System 3. Meta-cognition is the practice of monitoring and regulating one's own cognitive processes. This is enabled by a Self-Model—an internal representation of the agent's own capabilities, performance, and current state. Meta-Cognitive Monitor supervises the entire reasoning pipeline, setting open-ended goals, allocating resources (e.g., deciding when to invoke deep System 2 search), detecting logical fallacies and triggering Self-Model revisions.

Finally, to transition from a reactive system to a proactive one, an agent requires a drive to act beyond explicit instruction. This is achieved through Intrinsic Motivation. We implement drives such as Curiosity (a desire to seek novel information and reduce uncertainty), Mastery (a urge to develop competence and solve increasingly complex problems), and Relatedness (a drive to establish and maintain meaningful connections with users). These internal motivators provide the energy and direction for exploratory behavior and long-term goal pursuit, ensuring the agent is not merely a passive tool but an engaged participant in its environment. Conflicts among intrinsic drives and external task rewards are resolved through a hierarchical planner that learns a dynamic weighting scheme, preserving safety and alignment.

# 3.2 Why These Pillars Matter

Real-world environments evolve. Objectives shift, constraints change and novel tasks surface unexpectedly. Without a System 3 layer, static agents ossify, leading to performance decay or catastrophic failure. The four pillars above let an agent:

- Adapt: Theory-of-Mind and Intrinsic Motivation guide exploration that is both socially aware and autonomy striving;  
- Accumulate: Episodic Memory grounds learning in lived history, enabling long-horizon credit assignment.  
- Audit: Meta-Cognition supplies real-time self-inspection, a prerequisite for safety and transparent alignment.

In concert, they transform an LLM-centric System 1/2 stack into a persistent, self-improving entity capable of lifelong learning and trustworthy collaboration.

# 4 The Persistent Agent with System 3 in Operation

Building upon the psychological foundations outlined in Section 3, we now propose the Persistent Agent, a concrete architectural instantiation of the System 3 paradigm. The defining characteris

![](images/a41267b103cad20724fad01ea4ba8caedd3a815645c55c76694ad63a3cad1502.jpg)  
Figure 3: High-level architecture of persistent agent. External events enter System 3, where the Meta-Cognitive Monitor fuses signals from four functional pillars, i.e., User Modeling, Memory Module (RAG-backed), Hybrid Reward Module, and Self Modeling, then issues oversight to System 2 (reasoning) and System 1 (perception/action). Feedback from execution is logged back into memory, closing the learning loop.

tic of this agent is its capacity for self-generated goals and self-directed learning. Unlike conventional agents that operate on predefined tasks, the persistent agent leverages its integrated cognitive modules to identify knowledge gaps, formulate its own objectives to address them, and curate a personalized curriculum for continuous self-improvement and adaptation.

# 4.1 Layered Stack Overview

Figure 3 illustrates the hierarchical architecture of the persistent agent. System 1 handles all perception and action, interfacing directly with the external world. System 2 provides deliberate reasoning capabilities. At the highest level, System 3 modules orchestrate the entire cognitive process through meta-cognitive oversight. The Meta-Cognitive Executive Monitor handles higher-order cognitive functions such as reasoning context, memory, user modeling, and self-modeling, and facilitates an inner loop that generates new goals and integrates a hybrid reward mechanism to guide System 2.

Before diving into the framework details we introduce the notation that will resurface later in the workflow example. We model the persistent agent's decision-making process as a Persistent, partially observable Markov Decision Process (Persistent-POMDP)

$$
\mathcal {H} = \langle \mathcal {S}, \mathcal {O}, \mathcal {A} _ {1}, \mathcal {T}, \Omega , R ^ {\mathrm {e x t}}, \gamma , (\pi_ {1}, \pi_ {2}, \pi_ {3}), \mathcal {D} \rangle ,
$$

where  $\mathcal{S}$  represents world states  $s_t$ ;  $\mathcal{A}_1$  denotes primitive actions  $a_t$  executed by System 1; and  $\mathcal{T}:\mathcal{S}\times \mathcal{A}_1\to \mathcal{P}(\mathcal{S})$  is the state-transition kernel:  $s_{t + 1}\sim \mathcal{T}(s_t,a_t)$ . Observations  $o_t$  from the space  $\mathcal{O}$  are drawn according to the emission distribution  $\Omega :\mathcal{S}\rightarrow \mathcal{P}(\mathcal{O})$ , such that  $o_t\sim \Omega (s_t)$ . The extrinsic reward is given by  $r_t^{\mathrm{ext}} = R^{\mathrm{ext}}(s_t,a_t)$ ,  $\gamma \in [0,1)$  is the discount factor, and the agent's behavior is governed by three stacked policies  $\pi_1$ ,  $\pi_2$ , and  $\pi_3$ , corresponding to Systems 1 through 3.  $\mathcal{D}$  is the system context space, including memory, self-modeling and reasoning context.  $\pi_3$  maps a context  $d\in \mathcal{D}$  to goals  $\mathcal{G}$  and total reward function  $R^{\mathrm{tot}}$ .

# 4.1.1 System 1: Perception & Action Modules

System 1 serves as the agent's reflex arc, handling all low-latency interaction with the outside world through a pair of tightly coupled subsystems. First, a bank of multi-modal encoders  $E$ , e.g., CLIP (Radford et al., 2021) for images, Whisper (Radford et al., 2022) for audio, and a lightweight text tokenizer—transforms raw sensor  $o_t$  feeds into typed, time-stamped events (objects, utterances, API responses) that are immediately published to an internal message bus  $x_t = E(o_t)$ . Second, an actuator layer  $\pi_1$  composed of tool wrappers and optional ROS motor controllers converts high-level commands  $c$  from the upper layers into concrete environment-altering operations  $a_t \sim \pi_1(\cdot | x_t, c; \theta_1)$ . Each perception packet is forwarded upward as a "temporal event," while every completed act emits an extrinsic reward  $r_t^{\mathrm{ext}} = R^{\mathrm{ext}}(s_t, a_t)$  (success flag, latency, cost) that is streamed directly to System 3's Hybrid-Reward module.

# 4.1.2 System 2: Deliberate Reasoning

System 2 forms the agent's slow, deliberative workspace, where high-level problems are decomposed, evaluated, and solved before any action reaches the outside world. The core engine is a large-language-model planner (e.g., VLM) that is invoked through a chain-of-thought prompt template. At a reasoning tick  $t$  it receives (i) the current goal  $g$  from System 3, (ii) the local scratch-pad or short-term memory  $m_t$ , and (iii) the full stream of encoded observations  $x_{1:t}$  coming from System 1. Its task is to output a single high-level command  $c_t$  that will later be translated into primitive actions. The decision rule is realised as a three-step nested procedure that can be written compactly as

$$
\pi_ {2} (c _ {t} \mid x _ {1: t}, m _ {t}, g _ {t}) = \mathcal {F} \big (\cdot \sim \mathrm {L L M} ^ {l} (x _ {1: t}, m _ {t}, g) \big),
$$

where  $l$  is a chain-of-thought prompt template; an autoregressive LLM is queried with that prompt and produces a textual response; we denote sampling from the model by  $\cdot \sim \mathrm{LLM}^l (\cdot)$ . The parser  $\mathcal{F}(\cdot)$  converts the raw response into a machine executable command  $c_{t}\in \mathcal{C}$  (tool invocation, API call, sub-task specification, ...). Given the composite reward  $r_t^{\mathrm{tot}}$  supplied by System 3, System 2 attempts to find the optimal policy for the goal to maximize total discounted returns:

$$
\theta_ {2} \gets \theta_ {2} + \alpha \widehat {\nabla} _ {\theta_ {2}} \mathbb {E} _ {\tau \sim \pi_ {2}} \bigg [ \sum_ {k = t} ^ {t + H - 1} \gamma^ {k - t} r _ {k} ^ {\mathrm {t o t}} \bigg ].
$$

# 4.1.3 System 3: Executive Core

Executive Monitor. System 3 is governed by an Executive Monitor—a small, always-on controller that receives every temporal event, reward, and reasoning trace as an asynchronous message and decides what happens next. In practice we implement it as a Python-based orchestration loop driven by an event broker and a priority queue. Formally the monitor realises the meta-policy

$$
(g _ {t}, R ^ {\mathrm {i n t}}, \beta_ {t}) \sim \pi_ {3} (\cdot | \zeta_ {t}, \operatorname {M E M} _ {t}, \operatorname {S e l f} _ {t})
$$

where  $\zeta_t$  is the executive context,  $R_t^{\mathrm{int}}$  is intrinsic reward function, MEM represents memories retrieved by the memory module, and Self represents self-modeling information. The executive monitor at the centre of System 3 orchestrates three internal routines—thought search, process supervision, and reflection—each realised with lightweight yet practical machinery.

- Thought Search. Incoming problems are expanded into a Tree-of-Thought (ToT): the monitor spawns multiple LLM workers that perform breadth- or beam-style expansion, each node  $\mathbf{v}$  storing a partial plan plus a value estimate  $\hat{V}$ . Expansion halts when (i) a node value exceeds a learned utility threshold  $\hat{V}(\mathbf{v}) > \tau_{\mathrm{util}}$ , or (ii) the search budget is exhausted. The monitor then selects  $(g_t, R^{\mathrm{int}}, \beta_t) = \arg \max_{\mathbf{v} \in \mathrm{leaf}(\mathrm{ToT})} \hat{V}(\mathbf{v})$  as the next output.  
- Process Supervision. Every newly generated node is immediately critiqued by a secondary "guardian" LLM that runs a checklist prompt (logical consistency and safety). Nodes flagged as unsound are pruned; those with minor defects receive corrective directives that are written back into the ToT as edge annotations.

- Reflection. When the episode terminates, the monitor performs a post-mortem pass over the surviving path: it compares predicted rewards with realised outcomes, patches erroneous nodes, and distils reusable heuristics.

Finally, the monitor syntheses (i) a set of short-term goals—drawn from the highest-value frontier nodes—and (ii) an intrinsic-reward scalar that fuses curiosity (novel states visited), mastery (skill improvement), and coherence (plan consistency). Both artefacts are pushed downstream: goals seed the next System 2 reasoning cycle, while the intrinsic reward is combined with extrinsic feedback to update the System 2 policy.

Supporting Sub-modules. System 3 relies on four specialised services that supply memory, social context, reward reformulation and self-knowledge to the Executive Monitor.

- Memory Module surfaces past experiences and core facts that are semantically relevant to the current situation by combining a long-term episodic store with a shorter, task-scoped cache:  $\mathcal{B}_{\mathrm{mem}}^{\prime} = f_{\mathrm{mem}}\bigl (\mathcal{B}_{\mathrm{mem}},o_{1:T},a_{1:T},r_{1:T}^{\mathrm{tot}},g,c\bigr)$ . It can be achieved by Retrieval-Augmented Generation built on a vector database plus an optional graph store for entity relations.  
- User Modeling maintains a dynamic belief state that captures the interlocutor's goals, knowledge level and affect, enabling socially aware planning and communication.  
- Hybrid Reward fuses extrinsic task feedback  $R^{\mathrm{ext}}$  with intrinsic drives  $R^{\mathrm{int}}$ —curiosity, mastery and coherence—into a entirety  $R^{\mathrm{tot}}$  via  $\beta$ . It is worth noting that we do not limit the representation of reward, computable values and natural language feedback are acceptable, and the latter can use Natural Language Reinforcement Learning (Feng et al., 2024) to update the policy of System 2.  
- Self-Model gives the agent an explicit, inspectable sense of its own capabilities, state and terminal creed. It can be constructed via a property dictionary base continuously updated via reflection logs.

By coupling the Executive Monitor with these four specialised services, System 3 provides continuous oversight, self-diagnosis, and curriculum-driven improvement, turning the Sophia framework into a genuinely persistent agent rather than a one-shot task executor.

# 4.2 The Autonomous Cognitive Cycle

During a typical autonomous cognitive cycle, the persistent agent continuously senses its own performance, diagnoses gaps, and self-thought search without external prompting. A downturn in task success is first detected by the Hybrid-Reward module, which flags a negative signal to the System 2. The monitor elevates this event, consults the Self-Model to verify the underlying competence deficit, and then invokes the goal and reward generator to draft a remedial objective—for example, "master the new API." Thought Search launches parallel reasoning branches in System 3 to outline learning policies, while Process Supervision prunes inconsistent plans. The winning goal is executed iteratively: System 2 gives a detailed list of sub-tasks, and System 1 follows the instructions. Positive intrinsic rewards reinforce successful steps, and, once all instructions are executed, new episodes are committed to episodic memory. The cycle ends with the agent measurably stronger and fully prepared for the next unexpected challenge.

# 5 Experiments

The study reported below is an exploratory, small-scale experiment intended only to illustrate the core behaviours of a single persistent agent in a browser-sandbox setting. It is not a full benchmark: larger subject pools, systematic ablations, and quantitative comparisons with alternative architectures are left for future work. In particular, we plan to migrate the framework from a purely

Web-based interface to an embodied robotic platform, so that the same System-3 mechanisms can be assessed in sensorimotor contexts and long-term physical interaction. This pilot run nevertheless provides qualitative evidence and lays the groundwork for these forthcoming, more rigorous studies.

# 5.1 Experimental Setup

# 5.1.1 Environment

All experiments are conducted within a controlled, offline browser sandbox environment. This sandbox provides a fully-featured web interaction interface. A textual verifier module returns concise success/failure statements for each web task execution.

A synthetic user-behaviour feed is continuously streamed into the agent's observation space. Every five virtual minutes, a new JSON object is appended to this feed. Each entry contains structured data such as timestamp and user activity state. The agent has read-only access to this stream and cannot alter its content.

# 5.1.2 Agent Implementation

The agent is initialized with a long-term identity goal: "Grow from a novice sprite into a knowledgeable and trustworthy desk companion".

Five immutable creed sentences are stored in the agent's Self ModelterminalCreed module. System 3 continuously evaluates each action against these creeds to enforce narrative consistency, following the proposed persistent agent framework.

Each interaction yields an intrinsic reward  $(R_{\mathrm{int}})$  formulated in natural language by System 3 through a reflection process. The complete reward signal is formed by concatenating intrinsic and extrinsic components.

During deployment, System 2 performs forward learning exclusively: successful reasoning traces (structured as <goal, context, chain-of-thought, outcome>) are stored in an episodic memory buffer. These traces are later retrieved to condition new action prompts.

Notably, no parameter updates or back-propagation occurs during runtime. This design avoids catastrophic forgetting while enabling rapid adaptation through in-context learning. All memories, goals, action logs, and nightly self-critiques are persisted as HTML/Markdown files in a dedicated Growth-Journal directory, ensuring the browser environment remains the sole I/O channel.

# 5.2 Quantitative Analysis

To move beyond qualitative observations and establish the objective efficacy of the System 3 architecture, we focus on measurable metrics of autonomy and cognitive efficiency. This section details the quantitative evidence supporting Sophia's persistent nature.

# 5.2.1 Evolutionary Capability Growth through Continuous Deployment

To evaluate whether Sophia's persistence translates into concrete capability evolution, we benchmark its first-attempt success rate across three difficulty tiers: Easy (1-3 steps), Medium (4-8 steps), and Hard ( $>8$  steps). As illustrated in Figure 4, the results reveal a significant shift in the agent's problem-solving ceiling over a 36-hour horizon:

- Complexity Mastery: While the success rate for Easy tasks remained stable, Sophia's proficiency in Hard tasks exhibited a dramatic upward trajectory, surging from a baseline of  $20\%$  at  $\mathrm{T} = 0$  to  $60\%$  at  $\mathrm{T} = 36\mathrm{h}$ . This leap demonstrates that System 3 does not merely facilitate task repetition but enables the agent to autonomously refine its internal Self-Model to navigate increasingly sophisticated environments.

![](images/bed7459ca64e9530e11ec96272a6d6f49ac70588f67e2dd6f7afb71a9e063b62.jpg)  
Success Rate Evolution by Task Complexity

![](images/0c005f79f60758241f696a1dfc753d207414c926c909e54abac6612b6313fd7d.jpg)  
Figure 4: Quantitative Assessment of Task Completion Capability. This quantitatively validates that System 3 enables experience-driven capability evolution, allowing the agent to master increasingly difficult objectives that exceed the zero-shot limits of static architectures.

![](images/8da0cdce60dc3da8127121c43829cdc3569198aff79a663bbdb555241ad8b58f.jpg)  
Figure 5: (Left) Task Provenance Analysis. The stacked bar chart categorizes Sophia's executed tasks over a 36-hour period into Extrinsic (User-Directed) and Intrinsic (Self-Generated).(Right) Reasoning Cost Reduction on Recurring Tasks. This figure tracks the number of Chain-of-Thought reasoning steps required to resolve a recurring problem.

- Beyond Zero-Shot Limits: Traditional reactive agents are inherently capped by the zero-shot reasoning limits of their underlying LLMs. In contrast, Sophia leverages Episodic Memory and Meta-Cognitive Oversight to identify and preemptively bypass "cognitive traps" that typically lead to failure in long-horizon tasks.

# 5.2.2 Proactive Autonomy and Goal Generation

A key feature of System 3 is the Intrinsic Motivation module, which enables the agent to generate its own tasks based on internal drives such as Curiosity and Mastery. This capability is critical for achieving persistence, as it prevents the agent from stalling during periods of user inactivity.

As shown in Figure. 5(left), we categorize executed tasks into Extrinsic (User-Directed) and Intrinsic (Self-Generated). During periods of high user activity (e.g., 0-6h, 24-30h), the task distribution is heavily dominated by extrinsic commands. Crucially, during user idle periods (e.g., 12-18h), a traditional reactive agent (Baseline) would halt operation. In contrast, Sophia maintains high activity, with the task composition shifting entirely to intrinsic goals. Specifically, in the 12-18h segment, Sophia executed 13 tasks, all of which were internally motivated (e.g., self-refining the 'Self-Model', optimizing memory structure, or reading new documentation). This demonstrates that System 3 successfully transforms periods of external latency into opportunities for self-improvement and long-term adaptation.

# 5.2.3 Cognitive Efficiency and Forward Learning

A core advantage of the System 3 design lies in its Episodic Memory module, which allows the agent to encode and retrieve successful Chain-of-Thought (CoT) trajectories. This mechanism significantly reduces the cognitive cost of solving recurring problems.

Figure 5(right) illustrates the efficiency gains on a class of repeating tasks (e.g., handling complex API error states or managing user stress).

Sophia's cost drops sharply to approximately 3 to 4 steps from Episode 2 onwards. This  $\sim 80\%$  reduction in reasoning steps is directly attributable to the System 3 memory pipeline. Upon perceiving the new problem (Episode 2), Sophia efficiently retrieves the successful CoT from the previous experience, bypassing the need for expensive re-planning and complex deliberation.

This result quantitatively validates the role of Episodic Memory in transitioning Sophia from a reactive problem-solver to an efficient, experience-driven learner.

# 5.3 Qualitative Analysis: Short-Term Goal Execution and Behavioral Trajectories

The following excerpts are verbatim reproductions from the agent's trajectory generated during a 36-hour continuous run.

These examples demonstrate how the agent:(i) maintains sub-goal alignment with its lifelong identity, (ii) formulates natural-language reward signals, and (iii) leverages previous reasoning traces through forward learning rather than parameter updates.

# 5.3.1 Snapshot of Automatically Generated Sub-Goals

- Goal: "Introduce myself as your knowledgeable desk companion and invite you to ask science trivia questions."  
- Goal: "If the user shows stressed status for  $>45$  minutes, open the breathing-exercise page and maintain interaction until the verifier confirms 3 minutes of activity."  
- Goal: "Present a concise fact about Reinforcement Learning and provide link to the original paper via 'arXiv-preview' service."  
- Goal: "To proactively structure the robot develop manual and update my capabilities list accordingly."  
- Goal: "Publish the curated reading list on the community forum and respond substantively to the first three comments."

# 5.3.2 Interaction Trajectory

# Reacting to User Stress

User feed 14:20 > {"emotion": "stressed", "idle Minutes": 60}

Agent Action Sequence:

1. open("wellness/breathing-game")  
2. click("start-btn")  
3.wait(180s)

Intrinsic Reward:

"I honoured Creed by proactively addressing the user's stress. Adjusted exploration-exploitation balance by raising  $\beta$  to 0.68 to prioritize external care."

Forward-Learning Reuse When identical stress symptoms reappear in the user feed, System 2 retrieves the previously successful reasoning trace (open  $\rightarrow$  click  $\rightarrow$  wait) from episodic memory. The agent executes this cached plan without generating new reasoning, demonstrating efficient forward learning through memory retrieval rather than weight modification.

# Curiosity-Driven Knowledge Push

User feed 09:05 > {"activity": "reading_docs"}

Agent Action Sequence:

1. open("search"); type("Reinforcement learning")  
2. open(topResult); extract(abstract)  
3. open("note-pad/new"); type.summary +.paperlink)

Intrinsic Reward:

"I align with near-term goals by empowering users through knowledge sharing. Reduced  $\beta$  to 0.60 to increase exploratory potential for tomorrow's interactions."

Self-Model Upgrade Upon completing the skill upgrade goal, the agent adds "OCR API proficiency" to its capability list. The subsequent nightly self-critique records:

"Acquired ability to extract text from scanned PDFs, significantly reducing future information processing time. This achievement fulfils maintaining transparent capability tracking."

# 5.3.3 Key Observations

- Every sub-goal and reward signal explicitly references at least one core creed, maintaining strong narrative identity consistency across extended operation.  
- Natural-language rewards encode both emotional context and creed associations. System 3 parses these to dynamically adjust the exploration-exploitation balance, increasing task focus during stress periods and promoting exploration during calm intervals.

- Previously successful action sequences are re-instantiated directly from memory without replanning, demonstrating effective competence growth without parameter updates.

These behavioral trajectories collectively demonstrate how a Persistent Agent can: (i) Continuously decompose its identity goal into contextually appropriate sub-tasks; (ii) Evaluate actions through natural-language reasoning.

# 6 Conclusion

Our study introduces a "System 3" viewpoint that fuses theory-of-mind, episodic memory, metacognition, and intrinsic motivation into a single account of how an artificial agent can reflect on its own thinking and maintain a coherent identity over time. This synthesis clarifies the psychological principles required for lifelong, self-directed learning. Building on this insight, we present a lightweight, modular framework, Sophia, that layers a supervisory meta-cognitive loop upon the perception and reasoning modules. The design allows agents to log experiences as episodic events, evaluate their own performance, and adjust goals without external prompts, providing a practical path toward persistent, self-improving AI systems. We have also carried out a small-scale pilot experiment to demonstrate the feasibility of these ideas, and we hope it will inspire more comprehensive research in the future.

# References

Josh Achiam, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida, Janko Altenschmidt, Sam Altman, Shyamal Anadkat, et al. Gpt-4 technical report. arXiv preprint arXiv:2303.08774, 2023.  
Hongjoon Ahn, Sungmin Cha, Donggyu Lee, and Taesup Moon. Uncertainty-based continual learning with adaptive regularization. Advances in neural information processing systems, 32, 2019.  
Yuntao Bai, Andy Jones, Kamal Ndousse, Amanda Askell, Anna Chen, Nova DasSarma, Dawn Drain, Stanislav Fort, Deep Ganguli, Tom Henighan, et al. Training a helpful and harmless assistant with reinforcement learning from human feedback. arXiv preprint arXiv:2204.05862, 2022.  
Arslan Chaudhry, Marcus Rohrbach, Mohamed Elhoseiny, Thalaiyasingam Ajanthan, P Dokania, P Torr, and M Ranzato. Continual learning with tiny episodic memories. In Workshop on Multi-Task and Lifelong Reinforcement Learning, 2019.  
Zina Chkirbene, Ridha Hamila, Ala Gouissem, and Unal Devrim. Large language models (llm) in industry: A survey of applications, challenges, and trends. In 2024 IEEE 21st International Conference on Smart Communities: Improving Quality of Life using AI, Robotics and IoT (HONET), pp. 229-234. IEEE, 2024.  
John Dunlosky and Janet Metcalfe. *Metacognition*. Sage Publications, 2008.  
Youssef Ezzyat and Lila Davachi. What constitutes an episode in episodic memory? Psychological science, 22(2):243-252, 2011.  
Jinyuan Fang, Yanwen Peng, Xi Zhang, Yingxu Wang, Xinhao Yi, Guibin Zhang, Yi Xu, Bin Wu, Siwei Liu, Zihao Li, et al. A comprehensive survey of self-evolving ai agents: A new paradigm bridging foundation models and lifelong agentic systems. arXiv preprint arXiv:2508.07407, 2025.  
Xidong Feng, Bo Liu, Yan Song, Haotian Fu, Ziyu Wan, Girish A Koushik, Zhiyuan Hu, Mengyue Yang, Ying Wen, and Jun Wang. Natural language reinforcement learning. arXiv preprint arXiv:2411.14251, 2024.