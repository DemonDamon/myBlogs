# AI 拒了你的贷款，却说不出为什么？我装了 Semantica，把这个问题跑通了

上周看到 GitHub 趋势榜上有个项目叫 Semantica，定位很狂——"开源版 Palantir for AI Agents"，两周冲到 8800+ star。

Palantir 是干嘛的？给美国情报机构和大企业做数据分析的那家公司，核心本事是把散落各处的数据连成一张关系网，回答"谁连着谁、为什么"。Semantica 想把这套本事，给到每一个 AI Agent。

听着很美。我把它源码拉下来、装好、跑了六个 case，还顺手读了一部分代码。这篇文章讲三件事：它到底解决什么问题、实际用起来什么体验、代码里有哪些值得注意的细节。

## 一、它解决的是一个"答不上来"的问题

先做个思想实验。

你做一个信贷 Agent，某天它拒绝了张三的贷款。监管来了，问三个问题：这个决策依据是什么？和历史上哪些决策相关？两个数据源说的事实打架时你怎么处理的？

现在主流技术栈，三个都答不好：

**向量库（RAG 那套）**，本质是本通讯录。你问"贷款"，它找出"信贷"，因为向量距离近。但它只知道"谁和谁长得像"，不知道"谁导致了什么"。监管要的是因果关系，它给的是余弦相似度。

**大模型自己的记忆**，更像一个个孤岛。Agent A 记了一套，Agent B 记了另一套，互相对不了账。更麻烦的是两个数据源矛盾时，后写入的会把先写入的悄悄盖掉，没有任何告警。

**应用日志**，写了一堆"decision made"，但那是给程序员看排错用的，不是给审计用的结构化档案。

![三种方案对比](./images/comparison_small.png)

Semantica 的思路：把这些全变成**一张图**。公司、人、合同是节点，关系是边，每次 AI 决策也是一个节点，决策之间用"导致/影响"连起来。任何时刻你能顺着图问：这事为什么发生、牵连了谁、证据从哪来。

一句话：向量库回答"什么和你问的像"，图谱回答"这件事怎么来的"。高风险场景里，监管要的是后者。

## 二、架构：垫在你现有技术栈下面

看架构图之前先说一个关键认知：**Semantica 不是用来替换什么的**。

你的 LLM 照用，向量库照用，LangChain/CrewAI 照用。它在底下垫一层，管三件事：关系怎么存（上下文图谱）、决策怎么记（决策智能）、证据怎么留（PROV-O 溯源）。

![系统架构](./images/architecture_small.png)

从下往上看：

- **数据管线**：文件、网页、数据库、代码仓库进来，走 解析 → 归一 → 切分 → 实体关系抽取，变成图谱节点。Databricks 和 Snowflake 有官方连接器，数仓里的表直接变成带溯源的节点，不用先导出去再导回来——对金融医疗这种数据不能出库的行业，这点是刚需。
- **核心引擎**：上下文图谱 + 决策智能 + 确定性推理 + 溯源。注意"确定性"三个字：前向链、Rete、Datalog、SPARQL 四种推理引擎，全部是规则驱动，跑一万遍结果一样，不碰大模型。监管场景里"可复现"比"聪明"重要。
- **冲突检测**：五类矛盾（值、类型、关系、时序、逻辑）主动报警，多源打架不再悄悄覆盖。
- **服务层**：MCP Server、REST、CLI、可视化面板四条路出去，接哪个都行。

## 三、上手：安装比想象的重，但能跑

官方说一行搞定：`pip install semantica`。

实际呢？核心依赖里躺着 torch、transformers、spacy、faiss、opencv、librosa……我在 Mac 上用干净 venv 装，下了 700 多 MB。一行是没错，就是这一行比较沉。建议直接上 uv，并行下载能省一半时间。

装完先跑自检：

```bash
semantica doctor
# 0 error(s)  4 warning(s)
```

四个警告都是缺 LLM API key 之类的可选项——记住这个细节，**它的核心能力不依赖任何大模型**，缺 key 照样跑。

## 四、跑 case：一条能交给监管的证据链

推文里的例子是医疗场景，我原样复现了一遍，顺手加了步随访。背景：患者 P-4821 同时开了华法林和胺碘酮，这两种药联用会增强抗凝效果，需要干预。

**第一步，把三个决策记下来：**

```python
from semantica.context import ContextGraph

graph = ContextGraph(advanced_analytics=True)

d1 = graph.record_decision(
    category="drug_interaction_check",
    scenario="Patient P-4821: warfarin + amiodarone co-prescribed",
    reasoning="Amiodarone potentiates warfarin's anticoagulant effect",
    outcome="flag_for_review", confidence=0.91,
)
d2 = graph.record_decision(
    category="dosage_adjustment",
    scenario="INR monitoring plan for P-4821",
    reasoning="Reduce warfarin dose per interaction severity; recheck INR in 5 days",
    outcome="dose_reduced_30pct", confidence=0.87,
)
d3 = graph.record_decision(
    category="followup_schedule",
    scenario="Follow-up visit for P-4821 after dose change",
    outcome="scheduled_day5", confidence=0.95,
)
```

**第二步，连因果边：**

```python
graph.add_causal_relationship(d1, d2, relationship_type="CAUSED")
graph.add_causal_relationship(d2, d3, relationship_type="INFLUENCED")
```

边类型只允许三种：CAUSED（导致）、INFLUENCED（影响）、PRECEDENT_FOR（先例）。克制是对的——因果语义乱用，审计链就废了。

**第三步，一条命令拉全链：**

```python
chain = graph.trace_decision_chain(d3)
```

返回的东西比我想的细。它不只给你一条链，而是给你每一跳的证据：`hop_count`（隔了几跳）、`confidence_decay`（置信度沿链衰减多少）、`weakest_link`（整条链上最弱的一环是哪条边）、`distance_band`（直接/间接），甚至还有一句现成的 `interpretation`："Direct influence with confidence 1.00"。

![决策因果链](./images/decision-chain_small.png)

**第四步，导出证据：**

```python
pm = ProvenanceManager()
pm.track_entity(d1, source="ehr_p4821.xml", metadata={...})
prov_out = pm.export_prov(format="turtle")
```

导出来的是标准 W3C PROV-O 格式（Turtle），每条记录是一个 `prov:Entity`，带 `prov:wasAttributedTo`（谁做的）、`prov:qualifiedGeneration`（什么时候、什么活动产生的）。这是国际标准格式，审计系统能直接吃。

除了因果链，我还试了两个查询，都一次跑通：

- `find_similar_decisions("warfarin interaction review")` 找历史先例——有意思的是它的相似度是**两路混合**的：内容相似度（文本向量）+ 结构相似度（图结构），我这个 case 里结构相似度 1.0、内容相似度 0.125，加权后 0.39。同一个病人的决策，文本长得不像但结构一样，照样能捞出来。
- `analyze_decision_impact(d2)` 看影响面——直接影响了谁、间接影响了谁、各带影响分。

另外把 MCP Server 也点着了，12 个工具（record_decision、get_causal_chain、find_precedents……）全在，Claude Desktop、Cline、VS Code 里配上就能用。

## 五、读代码：几个值得说的细节

趁装依赖的空档翻了下源码，说三个架构师视角的观察。

**1. 图是自己写的，不是 networkx。**

`ContextGraph` 那个类 4100 多行，底层就是 dict 存节点、list 存边，加自建的邻接表和类型索引，读写上了一把线程锁。整个包 18 万行 Python，networkx 只在可选的分析算法里出现。为什么自己写？双时间模型是个线索：每个节点带 `valid_from/valid_until`，"撤销"和"删除"是两码事（撤销是关掉有效期窗口，历史还在；删除才进墓碑）。`state_at("2024-06-01")` 能拿到任意历史时刻的图快照——这个"时间旅行"能力，networkx 给不了，审计场景却是刚需。

**2. 决策是"一等公民"，不是日志。**

`record_decision` 一次写入五个地方：图的 decision 节点、决策主表、按类别的倒排索引、按实体的倒排索引、按时间的倒排索引。所以后面无论按病人查、按时间查、按类别查，都不用扫全图。

**3. PROV-O 是手工拿 rdflib 拼的。**

溯源导出没有用 prov 库，直接绑定 `http://www.w3.org/ns/prov#` 命名空间手工构造三元组。好处是依赖少、输出完全可控；存储层还带哈希链，防事后篡改记录。

## 六、踩的坑，也是真实体验的一部分

不吹不黑，这几个坑都值得记下来：

**坑一：嵌入模型下载。** 向量检索要下载 BAAI 的 bge-small 模型，HuggingFace 直连超时，我换 `HF_ENDPOINT=https://hf-mirror.com` 加禁用 xet 才下载成功。

**坑二：向量库写入失败后静默降级。** 最诡异的一个：AgentContext 存记忆时报 "Failed to store in vector store"，没有异常抛出，检索自动退化成纯图检索——结果还是对的，但你不知道向量那路其实没工作。做基础设施，静默降级是双刃剑：可用性上去了，可观测性下来了。

**坑三：导出 API 各写各的。** RDF 导出要的是 `{"entities": [...], "relationships": [...]}` 字典，直接把 ContextGraph 对象丢进去会报错；`track_relationship` 的第一个参数是 relationship_id 而不是源实体，容易传错。API 风格还没有统一打磨过。

**坑四：目录名陷阱。** 在克隆的仓库上层目录跑 `python -m semantica.mcp_server` 会挂——CWD 里那个叫 semantica 的仓库文件夹会被当成命名空间包，把真包遮住。换个目录跑就好，但这种问题排查起来挺费时间。

## 七、性能数字怎么看

官方 README 放了几个很猛的数字：11.8 万节点图上，节点搜索从 24ms 优化到 0.004ms（约 6000 倍）；嵌入缓存命中吞吐提升 10 倍；语义去重快 6.98 倍。

读的时候注意一句话，README 自己写的：这些是**记录在 CHANGELOG 里的历史测量，不是自动化测试断言**。官方也给了基准脚本（`pytest tests/vector_store/test_performance_benchmarks.py`），真要选型，拿自己的数据跑一遍再信。

我自己这张小图上，两跳 BFS 遍历 0.013ms，量级上没有异常。

## 八、谁该看，谁不用急

**该认真看的**：做信贷、保险、医疗、合规类 AI Agent 的团队——任何"决策要留痕、审计要过堂"的场景。它把监管最看重的东西（因果链、先例、溯源、冲突检测）做成了开箱即用的原语，自己从零造这套东西起码几个月。MIT 协议、可自托管、数据不出库，企业落地的主要顾虑都照顾到了。

**不用急的**：做闲聊机器人、通用 RAG 问答的。你的场景没有"审计"压力，加这层是给自己上强度。向量库 + 重排已经够了。

**我的整体判断**：方向真、问题真、工程完成度超出我预期（尤其决策链查询的输出设计），但 v0.6.5 还处于"能力都有、打磨未完"的阶段——API 一致性、错误处理、静默降级这些都还有毛边。适合现在开始 PoC，生产上量前把上面那几个坑验证一遍。

八千多个 star 不全是跟风。AI 可解释性从"锦上添花"变成"硬性要求"的趋势已经很明显，给系统补一条可追溯的决策链，越早越好。

---

*项目地址：github.com/semantica-agi/semantica（MIT，v0.6.5）*
*测试环境：macOS + Python 3.11 + uv，全部 case 代码在本文配套仓库可复现*
