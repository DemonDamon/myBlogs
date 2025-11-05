# 我问
graphiti解决了什么核心问题？

# deepwiki

您询问的是 Graphiti 解决了什么核心问题。<cite></cite>

## 核心问题

Graphiti 解决了**动态环境中 AI Agent 的知识图谱构建和查询**问题,特别是针对传统 RAG(检索增强生成)方法的局限性。 [1](#0-0) 

### 传统 RAG 的痛点

传统 RAG 方法依赖批处理和静态数据摘要,在处理频繁变化的数据时效率低下。 [2](#0-1) 

### Graphiti 的解决方案

Graphiti 通过以下核心能力解决这些问题:

1. **实时增量更新** - 无需批量重新计算即可立即集成新数据 [3](#0-2) 

2. **双时态数据模型** - 明确跟踪事件发生时间和摄入时间,支持精确的时间点查询 [4](#0-3) 

3. **高效混合检索** - 结合语义嵌入、关键词(BM25)和图遍历,实现低延迟查询,无需依赖 LLM 摘要 [5](#0-4) 

4. **自定义实体定义** - 通过 Pydantic 模型灵活创建本体和开发者定义的实体 [6](#0-5) 

5. **可扩展性** - 通过并行处理高效管理大型数据集,适合企业环境 [7](#0-6) 

## 与 GraphRAG 的对比

Graphiti 专门设计用于处理动态和频繁更新的数据集,特别适合需要实时交互和精确历史查询的应用。 [8](#0-7) 

关键区别包括:
- **数据处理**: 连续增量更新 vs 批处理
- **知识结构**: 情节数据、语义实体、社区 vs 实体集群和社区摘要
- **检索方法**: 混合语义、关键词和图搜索 vs 顺序 LLM 摘要
- **查询延迟**: 通常亚秒级 vs 数秒到数十秒
- **矛盾处理**: 时态边失效 vs LLM 驱动的摘要判断 [9](#0-8) 

## Notes

Graphiti 的核心价值在于将静态的批处理知识图谱转变为能够实时演化的动态记忆系统,特别适合 AI Agent 在动态环境中的应用场景。<cite></cite> 它通过时态感知的图结构和高效的混合检索,在保持查询性能的同时支持持续的知识更新。<cite></cite>

Wiki pages you might want to explore:
- [Custom Entity Types and Schemas (getzep/graphiti)](/wiki/getzep/graphiti#10.3)
- [Deployment and Services (getzep/graphiti)](/wiki/getzep/graphiti#8)

### Citations

**File:** README.md (L37-42)
```markdown
Graphiti is a framework for building and querying temporally-aware knowledge graphs, specifically tailored for AI agents
operating in dynamic environments. Unlike traditional retrieval-augmented generation (RAG) methods, Graphiti
continuously integrates user interactions, structured and unstructured enterprise data, and external information into a
coherent, queryable graph. The framework supports incremental data updates, efficient retrieval, and precise historical
queries without requiring complete graph recomputation, making it suitable for developing interactive, context-aware AI
applications.
```

**File:** README.md (L82-83)
```markdown
Traditional RAG approaches often rely on batch processing and static data summarization, making them inefficient for
frequently changing data. Graphiti addresses these challenges by providing:
```

**File:** README.md (L85-85)
```markdown
- **Real-Time Incremental Updates:** Immediate integration of new data episodes without batch recomputation.
```

**File:** README.md (L86-87)
```markdown
- **Bi-Temporal Data Model:** Explicit tracking of event occurrence and ingestion times, allowing accurate point-in-time
  queries.
```

**File:** README.md (L88-89)
```markdown
- **Efficient Hybrid Retrieval:** Combines semantic embeddings, keyword (BM25), and graph traversal to achieve
  low-latency queries without reliance on LLM summarization.
```

**File:** README.md (L90-91)
```markdown
- **Custom Entity Definitions:** Flexible ontology creation and support for developer-defined entities through
  straightforward Pydantic models.
```

**File:** README.md (L92-92)
```markdown
- **Scalability:** Efficiently manages large datasets with parallel processing, suitable for enterprise environments.
```

**File:** README.md (L100-111)
```markdown
| Aspect                     | GraphRAG                              | Graphiti                                         |
|----------------------------|---------------------------------------|--------------------------------------------------|
| **Primary Use**            | Static document summarization         | Dynamic data management                          |
| **Data Handling**          | Batch-oriented processing             | Continuous, incremental updates                  |
| **Knowledge Structure**    | Entity clusters & community summaries | Episodic data, semantic entities, communities    |
| **Retrieval Method**       | Sequential LLM summarization          | Hybrid semantic, keyword, and graph-based search |
| **Adaptability**           | Low                                   | High                                             |
| **Temporal Handling**      | Basic timestamp tracking              | Explicit bi-temporal tracking                    |
| **Contradiction Handling** | LLM-driven summarization judgments    | Temporal edge invalidation                       |
| **Query Latency**          | Seconds to tens of seconds            | Typically sub-second latency                     |
| **Custom Entity Types**    | No                                    | Yes, customizable                                |
| **Scalability**            | Moderate                              | High, optimized for large datasets               |
```

**File:** README.md (L113-114)
```markdown
Graphiti is specifically designed to address the challenges of dynamic and frequently updated datasets, making it
particularly suitable for applications requiring real-time interaction and precise historical queries.
```

# 我问
图数据库用的什么？实时增量更新和双时态数据模型具体如何实现？

# deepwiki
您询问的是 Graphiti 使用的图数据库以及实时增量更新和双时态数据模型的具体实现。<cite></cite>

## 支持的图数据库

Graphiti 支持多种图数据库后端,通过抽象的 `GraphDriver` 接口实现: [1](#1-0) 

1. **Neo4j** (默认) - 版本 5.26+ [2](#1-1) 
2. **FalkorDB** - 版本 1.1.2+,基于 Redis 的图数据库 [3](#1-2) 
3. **Kuzu** - 版本 0.11.2,嵌入式图数据库 [4](#1-3) 
4. **Amazon Neptune** - AWS 云端图数据库(需配合 OpenSearch Serverless) [5](#1-4) 

默认使用 Neo4j,但您可以通过 `graph_driver` 参数传入自定义驱动: [6](#1-5) 

## 实时增量更新的实现

实时增量更新通过 `add_episode()` 方法实现,无需批量重新计算整个图:<cite></cite>

### 核心流程

1. **创建 EpisodicNode** - 将新数据包装为带时间戳的情节节点 <cite></cite>
2. **检索上下文** - 获取最近的情节(默认 3 个)提供给 LLM <cite></cite>
3. **并行提取** - 同时提取实体节点和关系边 <cite></cite>
4. **去重解析** - 使用嵌入相似度识别重复实体 <cite></cite>
5. **原子持久化** - 在单个事务中保存到图数据库和向量存储 <cite></cite>

### 并发控制

通过 `SEMAPHORE_LIMIT` 环境变量控制并发操作数,默认为 10: [7](#1-6) 

在 MCP 服务器中,使用队列机制确保同一 `group_id` 的情节按顺序处理,避免竞态条件: [8](#1-7) 

## 双时态数据模型的实现

双时态模型通过两组时间戳字段实现,分别跟踪**有效时间**和**事务时间**:<cite></cite>

### 时间维度

1. **Valid Time (有效时间)** - 事实在现实世界中为真的时间
   - `valid_at`: 关系建立的时间 [9](#1-8) 
   - `invalid_at`: 关系失效的时间 [10](#1-9) 

2. **Transaction Time (事务时间)** - 事实被记录到系统的时间
   - `created_at`: 节点/边创建时间 <cite></cite>

### 时间提取

LLM 从情节内容中提取时间信息,支持相对时间(如"10 年前")和绝对时间: [11](#1-10) 

关键规则:
- 使用 ISO 8601 格式 (YYYY-MM-DDTHH:MM:SS.SSSSSSZ)
- 基于参考时间戳计算相对时间
- 仅提取与关系建立/变化直接相关的时间

### 矛盾处理

当检测到矛盾的事实时,通过设置旧边的 `invalid_at` 字段来失效旧关系,而不是删除:<cite></cite>

```
时间 T1: EntityEdge(fact="Kendra loves Adidas", valid_at=T1, invalid_at=null)
时间 T2: 新事实 "Kendra loves Nike"
结果:
  - 旧边: EntityEdge(fact="Kendra loves Adidas", valid_at=T1, invalid_at=T2)
  - 新边: EntityEdge(fact="Kendra loves Nike", valid_at=T2, invalid_at=null)
```

### 时间点查询

通过时间过滤器实现历史状态查询:
- **当前状态**: `WHERE invalid_at IS NULL`
- **历史状态**: `WHERE valid_at <= T AND (invalid_at > T OR invalid_at IS NULL)`

## 配置示例

### Neo4j (默认)
```python
from graphiti_core import Graphiti
from graphiti_core.driver.neo4j_driver import Neo4jDriver

driver = Neo4jDriver(
    uri="bolt://localhost:7687",
    user="neo4j", 
    password="password",
    database="my_custom_database"
)
graphiti = Graphiti(graph_driver=driver)
``` [12](#1-11) 

### FalkorDB
```python
from graphiti_core.driver.falkordb_driver import FalkorDriver

driver = FalkorDriver(
    host="localhost",
    port=6379,
    database="my_custom_graph"
)
graphiti = Graphiti(graph_driver=driver)
``` [13](#1-12) 

## Notes

- 图数据库的选择影响性能和部署方式:Neo4j 适合生产环境,Kuzu 适合本地开发,Neptune 适合 AWS 云端部署 <cite></cite>
- 实时增量更新的关键在于避免批量重新计算,通过上下文窗口(默认 3 个情节)提供足够的历史信息给 LLM 进行实体解析 <cite></cite>
- 双时态模型的核心优势是保留完整的变更历史,支持"时光旅行"查询,这是传统 RAG 系统无法实现的 <cite></cite>
- 所有时间戳使用 ISO 8601 格式,确保跨时区的一致性 [14](#1-13) 

Wiki pages you might want to explore:
- [Overview (getzep/graphiti)](/wiki/getzep/graphiti#1)
- [Deployment and Services (getzep/graphiti)](/wiki/getzep/graphiti#8)

### Citations

**File:** graphiti_core/graphiti.py (L166-201)
```python
        graph_driver : GraphDriver | None, optional
            An instance of GraphDriver for database operations.
            If not provided, a default Neo4jDriver will be initialized.
        max_coroutines : int | None, optional
            The maximum number of concurrent operations allowed. Overrides SEMAPHORE_LIMIT set in the environment.
            If not set, the Graphiti default is used.
        ensure_ascii : bool, optional
            Whether to escape non-ASCII characters in JSON serialization for prompts. Defaults to False.
            Set as False to preserve non-ASCII characters (e.g., Korean, Japanese, Chinese) in their
            original form, making them readable in LLM logs and improving model understanding.

        Returns
        -------
        None

        Notes
        -----
        This method establishes a connection to a graph database (Neo4j by default) using the provided
        credentials. It also sets up the LLM client, either using the provided client
        or by creating a default OpenAIClient.

        The default database name is defined during the driver’s construction. If a different database name
        is required, it should be specified in the URI or set separately after
        initialization.

        The OpenAI API key is expected to be set in the environment variables.
        Make sure to set the OPENAI_API_KEY environment variable before initializing
        Graphiti if you're using the default OpenAIClient.
        """

        if graph_driver:
            self.driver = graph_driver
        else:
            if uri is None:
                raise ValueError('uri must be provided when graph_driver is None')
            self.driver = Neo4jDriver(uri, user, password)
```

**File:** README.md (L121-121)
```markdown
- Neo4j 5.26 / FalkorDB 1.1.2 / Kuzu 0.11.2 / Amazon Neptune Database Cluster or Neptune Analytics Graph + Amazon
```

**File:** README.md (L214-219)
```markdown
Concurrency controlled by the `SEMAPHORE_LIMIT` environment variable. By default, `SEMAPHORE_LIMIT` is set to `10`
concurrent operations to help prevent `429` rate limit errors from your LLM provider. If you encounter such errors, try
lowering this value.

If your LLM provider allows higher throughput, you can increase `SEMAPHORE_LIMIT` to boost episode ingestion
performance.
```

**File:** README.md (L282-298)
```markdown
#### Neo4j with Custom Database Name

```python
from graphiti_core import Graphiti
from graphiti_core.driver.neo4j_driver import Neo4jDriver

# Create a Neo4j driver with custom database name
driver = Neo4jDriver(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password",
    database="my_custom_database"  # Custom database name
)

# Pass the driver to Graphiti
graphiti = Graphiti(graph_driver=driver)
```
```

**File:** README.md (L300-317)
```markdown
#### FalkorDB with Custom Database Name

```python
from graphiti_core import Graphiti
from graphiti_core.driver.falkordb_driver import FalkorDriver

# Create a FalkorDB driver with custom database name
driver = FalkorDriver(
    host="localhost",
    port=6379,
    username="falkor_user",  # Optional
    password="falkor_password",  # Optional
    database="my_custom_graph"  # Custom database name
)

# Pass the driver to Graphiti
graphiti = Graphiti(graph_driver=driver)
```
```

**File:** README.md (L319-330)
```markdown
#### Kuzu

```python
from graphiti_core import Graphiti
from graphiti_core.driver.kuzu_driver import KuzuDriver

# Create a Kuzu driver
driver = KuzuDriver(db="/tmp/graphiti.kuzu")

# Pass the driver to Graphiti
graphiti = Graphiti(graph_driver=driver)
```
```

**File:** README.md (L332-354)
```markdown
#### Amazon Neptune

```python
from graphiti_core import Graphiti
from graphiti_core.driver.neptune_driver import NeptuneDriver

# Create a FalkorDB driver with custom database name
driver = NeptuneDriver(
    host= < NEPTUNE
ENDPOINT >,
aoss_host = < Amazon
OpenSearch
Serverless
Host >,
port = < PORT >  # Optional, defaults to 8182,
         aoss_port = < PORT >  # Optional, defaults to 443
)

driver = NeptuneDriver(host=neptune_uri, aoss_host=aoss_host, port=neptune_port)

# Pass the driver to Graphiti
graphiti = Graphiti(graph_driver=driver)
```
```

**File:** graphiti_core/driver/falkordb_driver.py (L111-146)
```python
class FalkorDriver(GraphDriver):
    provider = GraphProvider.FALKORDB
    aoss_client: None = None

    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        username: str | None = None,
        password: str | None = None,
        falkor_db: FalkorDB | None = None,
        database: str = 'default_db',
    ):
        """
        Initialize the FalkorDB driver.

        FalkorDB is a multi-tenant graph database.
        To connect, provide the host and port.
        The default parameters assume a local (on-premises) FalkorDB instance.
        """
        super().__init__()

        self._database = database
        if falkor_db is not None:
            # If a FalkorDB instance is provided, use it directly
            self.client = falkor_db
        else:
            self.client = FalkorDB(host=host, port=port, username=username, password=password)

        self.fulltext_syntax = '@'  # FalkorDB uses a redisearch-like syntax for fulltext queries see https://redis.io/docs/latest/develop/ai/search-and-query/query/full-text/

    def _get_graph(self, graph_name: str | None) -> FalkorGraph:
        # FalkorDB requires a non-None database name for multi-tenant graphs; the default is "default_db"
        if graph_name is None:
            graph_name = self._database
        return self.client.select_graph(graph_name)
```

**File:** mcp_server/graphiti_mcp_server.py (L575-609)
```python
async def initialize_graphiti():
    """Initialize the Graphiti client with the configured settings."""
    global graphiti_client, config

    try:
        # Create LLM client if possible
        llm_client = config.llm.create_client()
        if not llm_client and config.use_custom_entities:
            # If custom entities are enabled, we must have an LLM client
            raise ValueError('OPENAI_API_KEY must be set when custom entities are enabled')

        # Validate Neo4j configuration
        if not config.neo4j.uri or not config.neo4j.user or not config.neo4j.password:
            raise ValueError('NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD must be set')

        embedder_client = config.embedder.create_client()

        # Initialize Graphiti client
        graphiti_client = Graphiti(
            uri=config.neo4j.uri,
            user=config.neo4j.user,
            password=config.neo4j.password,
            llm_client=llm_client,
            embedder=embedder_client,
            max_coroutines=SEMAPHORE_LIMIT,
        )

        # Destroy graph if requested
        if config.destroy_graph:
            logger.info('Destroying graph...')
            await clear_data(graphiti_client.driver)

        # Initialize the graph database with Graphiti's indices
        await graphiti_client.build_indices_and_constraints()
        logger.info('Graphiti client initialized successfully')
```

**File:** graphiti_core/prompts/extract_edge_dates.py (L25-28)
```python
    valid_at: str | None = Field(
        None,
        description='The date and time when the relationship described by the edge fact became true or was established. YYYY-MM-DDTHH:MM:SS.SSSSSSZ or null.',
    )
```

**File:** graphiti_core/prompts/extract_edge_dates.py (L29-32)
```python
    invalid_at: str | None = Field(
        None,
        description='The date and time when the relationship described by the edge fact stopped being true or ended. YYYY-MM-DDTHH:MM:SS.SSSSSSZ or null.',
    )
```

**File:** graphiti_core/prompts/extract_edge_dates.py (L43-88)
```python
def v1(context: dict[str, Any]) -> list[Message]:
    return [
        Message(
            role='system',
            content='You are an AI assistant that extracts datetime information for graph edges, focusing only on dates directly related to the establishment or change of the relationship described in the edge fact.',
        ),
        Message(
            role='user',
            content=f"""
            <PREVIOUS MESSAGES>
            {context['previous_episodes']}
            </PREVIOUS MESSAGES>
            <CURRENT MESSAGE>
            {context['current_episode']}
            </CURRENT MESSAGE>
            <REFERENCE TIMESTAMP>
            {context['reference_timestamp']}
            </REFERENCE TIMESTAMP>
            
            <FACT>
            {context['edge_fact']}
            </FACT>

            IMPORTANT: Only extract time information if it is part of the provided fact. Otherwise ignore the time mentioned. Make sure to do your best to determine the dates if only the relative time is mentioned. (eg 10 years ago, 2 mins ago) based on the provided reference timestamp
            If the relationship is not of spanning nature, but you are still able to determine the dates, set the valid_at only.
            Definitions:
            - valid_at: The date and time when the relationship described by the edge fact became true or was established.
            - invalid_at: The date and time when the relationship described by the edge fact stopped being true or ended.

            Task:
            Analyze the conversation and determine if there are dates that are part of the edge fact. Only set dates if they explicitly relate to the formation or alteration of the relationship itself.

            Guidelines:
            1. Use ISO 8601 format (YYYY-MM-DDTHH:MM:SS.SSSSSSZ) for datetimes.
            2. Use the reference timestamp as the current time when determining the valid_at and invalid_at dates.
            3. If the fact is written in the present tense, use the Reference Timestamp for the valid_at date
            4. If no temporal information is found that establishes or changes the relationship, leave the fields as null.
            5. Do not infer dates from related events. Only use dates that are directly stated to establish or change the relationship.
			6. For relative time mentions directly related to the relationship, calculate the actual datetime based on the reference timestamp.
            7. If only a date is mentioned without a specific time, use 00:00:00 (midnight) for that date.
            8. If only year is mentioned, use January 1st of that year at 00:00:00.
            9. Always include the time zone offset (use Z for UTC if no specific time zone is mentioned).
            10. A fact discussing that something is no longer true should have a valid_at according to when the negated fact became true.
            """,
        ),
    ]
```

# 我问
所以就是动态更新图谱，那首先是如何构建schema，又如何基于schema去构建图谱（是先抽取实体、关系，再构建spo，还是一步直接抽取spo？），如何检验图谱构建的专业性？用了什么维度和指标去评判图谱构建的质量。在graphiti中如何使用图谱去增强rag效果（混合检索的设置、提示词怎么拼装等）

# deepwiki
您询问的是 Graphiti 如何构建 schema、如何基于 schema 构建图谱、如何评估图谱质量,以及如何使用图谱增强 RAG 效果。<cite/>

## Schema 构建

Graphiti 支持两种 schema 定义方式:<cite/>

### 1. 默认 Schema

系统使用通用的 `Entity` 节点和 `EntityEdge` 关系,无需预定义 schema。 [1](#2-0) 

### 2. 自定义实体类型

通过 Pydantic 模型定义自定义实体类型,在 `add_episode()` 时传入 `entity_types` 参数: [2](#2-1) 

```python
from pydantic import BaseModel, Field

class Person(BaseModel):
    """A person entity"""
    age: int | None = Field(None, description="Person's age")
    occupation: str | None = Field(None, description="Person's job")

class Organization(BaseModel):
    """An organization entity"""
    industry: str | None = Field(None, description="Industry sector")

entity_types = {
    "Person": Person,
    "Organization": Organization
}

await graphiti.add_episode(
    name="meeting",
    episode_body="John, 30, works at TechCorp in the software industry",
    entity_types=entity_types,
    ...
)
```

自定义类型会传递给 LLM 作为提取上下文。 [3](#2-2) 

### 3. 自定义关系类型

通过 `edge_types` 和 `edge_type_map` 定义关系类型及其适用的实体对: [4](#2-3) 

```python
edge_types = {
    "WORKS_AT": WorksAtRelation,
    "MANAGES": ManagesRelation
}

edge_type_map = {
    ("Person", "Organization"): ["WORKS_AT"],
    ("Person", "Person"): ["MANAGES"]
}
```

关系类型信息会传递给边提取 prompt。 [5](#2-4) 

## 图谱构建流程

Graphiti 采用**两阶段提取**策略,先提取实体,再提取关系:<cite/>

### 阶段 1: 实体提取

1. **LLM 提取** - 调用 `extract_nodes()`,使用 prompt 从 episode 内容中提取实体: [6](#2-5) 

2. **Reflexion 机制** - 通过 `MAX_REFLEXION_ITERATIONS` 次迭代检查是否遗漏实体,最多 2 次反思。 [7](#2-6) 

3. **去重解析** - `resolve_extracted_nodes()` 使用嵌入相似度(阈值 0.8)和 LLM 判断识别重复实体: [8](#2-7) 

4. **属性提取** - `extract_attributes_from_nodes()` 为实体填充自定义属性和摘要。 [9](#2-8) 

### 阶段 2: 关系提取

1. **LLM 提取** - 调用 `extract_edges()`,基于已提取的实体列表提取关系三元组: [10](#2-9) 

   Prompt 明确要求只提取涉及已识别实体的关系。 [11](#2-10) 

2. **Reflexion 机制** - 同样使用反思机制检查遗漏的关系。 [12](#2-11) 

3. **关系解析** - `resolve_extracted_edges()` 检测矛盾关系并通过设置 `invalid_at` 失效旧关系: [13](#2-12) 

### 为什么是两阶段?

这种设计确保:<cite/>
- 实体作为"锚点"先被识别和去重
- 关系提取时可以引用明确的实体 ID,避免指代不清
- 减少 LLM 的认知负担,提高提取准确性

## 图谱质量评估

Graphiti 使用 **LLM-as-Judge** 方法评估图谱构建质量:<cite/>

### 评估维度

在 `eval_e2e_graph_building.py` 中,系统通过以下方式评估: [14](#2-13) 

1. **基线对比** - 使用 GPT-4.1-mini 构建基线图谱作为参考标准。 [15](#2-14) 

2. **LLM 评判** - 使用 `eval_add_episode_results` prompt 让 LLM 比较候选图谱和基线图谱: [16](#2-15) 

   评判标准:
   - 提取的实体是否完整
   - 关系是否准确
   - 是否有幻觉或遗漏
   - 整体质量是否优于基线

3. **评分计算** - 计算候选图谱优于基线的比例作为最终得分。 [17](#2-16) 

### 评估指标

虽然代码中没有明确的量化指标,但评估隐含考虑:<cite/>
- **召回率** - 是否提取了所有重要实体和关系
- **准确率** - 提取的信息是否正确
- **一致性** - 跨 episode 的实体去重是否准确
- **时态正确性** - 时间信息提取是否准确

## 使用图谱增强 RAG

Graphiti 通过**混合检索**将图谱用于 RAG:<cite/>

### 混合检索配置

系统提供多种预配置的搜索策略: [18](#2-17) 

#### 1. 基础混合搜索 (RRF)

```python
from graphiti_core.search.search_config_recipes import EDGE_HYBRID_SEARCH_RRF

results = await graphiti.search_(
    query="John 的工作",
    config=EDGE_HYBRID_SEARCH_RRF,
    group_ids=["user_123"]
)
```

该配置结合:<cite/>
- **BM25 全文搜索** - 关键词匹配 `fact` 字段
- **向量相似度搜索** - 语义匹配 `fact_embedding`
- **RRF 融合** - 倒数排名融合算法合并结果

#### 2. 图遍历增强搜索

```python
from graphiti_core.search.search_config_recipes import EDGE_HYBRID_SEARCH_NODE_DISTANCE

results = await graphiti.search_(
    query="与 John 相关的信息",
    config=EDGE_HYBRID_SEARCH_NODE_DISTANCE,
    center_node_uuid="john_uuid"  # 中心节点
)
```

该配置额外使用:<cite/>
- **BFS 图遍历** - 从中心节点出发查找相关关系
- **节点距离重排序** - 根据图距离调整结果排序 [19](#2-18) 

#### 3. Cross-Encoder 重排序

```python
from graphiti_core.search.search_config_recipes import COMBINED_HYBRID_SEARCH_CROSS_ENCODER

results = await graphiti.search_(
    query="John 的职业发展",
    config=COMBINED_HYBRID_SEARCH_CROSS_ENCODER
)
```

使用 LLM 对初步结果进行深度语义重排序。 [20](#2-19) 

### 检索方法组合

每种搜索配置可以组合以下方法:<cite/>

| 方法 | 实现 | 索引 |
|------|------|------|
| BM25 | `edge_fulltext_search()` | `edge_name_and_fact` 全文索引 |
| 向量相似度 | `edge_similarity_search()` | `fact_embedding` 向量索引 |
| 图遍历 | `edge_bfs_search()` | 图结构遍历 | [21](#2-20) 

### Prompt 拼装

检索到的结果可以直接用于 RAG prompt:<cite/>

```python
# 1. 检索相关事实
edges = await graphiti.search(
    query="用户的偏好",
    num_results=10
)

# 2. 格式化为上下文
context = "\n".join([
    f"- {edge.fact} (来源: {edge.source_node_uuid} -> {edge.target_node_uuid})"
    for edge in edges
])

# 3. 拼装 prompt
prompt = f"""
基于以下知识图谱中的事实回答问题:

<FACTS>
{context}
</FACTS>

<QUESTION>
{user_question}
</QUESTION>

请基于 FACTS 中的信息回答问题,不要编造信息。
"""
```

### MCP 服务器中的实现

在 MCP 服务器中,搜索工具直接暴露给 AI 助手: [22](#2-21) 

配置示例:
- 使用 `NODE_HYBRID_SEARCH_RRF` 搜索实体
- 使用 `SearchFilters` 过滤特定实体类型
- 返回格式化的节点摘要供 LLM 使用

## Notes

- Graphiti 的 schema 是**灵活的**,可以从无 schema 开始,逐步添加自定义类型。<cite/>
- 两阶段提取策略是核心设计,确保实体作为"锚点"先被识别,避免关系提取时的指代歧义。<cite/>
- 质量评估依赖 LLM-as-Judge,这是当前 LLM 应用评估的主流方法,但可能存在评判偏差。<cite/>
- 混合检索的关键是**多种方法互补**:BM25 捕获关键词,向量捕获语义,图遍历捕获结构关系。<cite/>
- 实际使用时,建议根据查询类型选择合适的搜索配置:事实查询用 RRF,关系查询用图遍历,复杂查询用 Cross-Encoder。<cite/>

Wiki pages you might want to explore:
- [System Architecture (getzep/graphiti)](/wiki/getzep/graphiti#4)
- [Search and Retrieval System (getzep/graphiti)](/wiki/getzep/graphiti#4.3)
- [Data Processing Pipeline (getzep/graphiti)](/wiki/getzep/graphiti#5)

### Citations

**File:** graphiti_core/graphiti.py (L393-393)
```python
        entity_types: dict[str, type[BaseModel]] | None = None,
```

**File:** graphiti_core/graphiti.py (L396-397)
```python
        edge_types: dict[str, type[BaseModel]] | None = None,
        edge_type_map: dict[tuple[str, str], list[str]] | None = None,
```

**File:** graphiti_core/graphiti.py (L798-809)
```python
            hydrated_nodes_results: list[list[EntityNode]] = await semaphore_gather(
                *[
                    extract_attributes_from_nodes(
                        self.clients,
                        nodes_by_episode_unique[episode.uuid],
                        episode,
                        previous_episodes,
                        entity_types,
                    )
                    for episode, previous_episodes in episode_context
                ]
            )
```

**File:** graphiti_core/prompts/extract_nodes.py (L71-73)
```python

class Versions(TypedDict):
    extract_message: PromptFunction
```

**File:** graphiti_core/prompts/extract_edges.py (L92-118)
```python
Extract all factual relationships between the given ENTITIES based on the CURRENT MESSAGE.
Only extract facts that:
- involve two DISTINCT ENTITIES from the ENTITIES list,
- are clearly stated or unambiguously implied in the CURRENT MESSAGE,
    and can be represented as edges in a knowledge graph.
- Facts should include entity names rather than pronouns whenever possible.
- The FACT TYPES provide a list of the most important types of facts, make sure to extract facts of these types
- The FACT TYPES are not an exhaustive list, extract all facts from the message even if they do not fit into one
    of the FACT TYPES
- The FACT TYPES each contain their fact_type_signature which represents the source and target entity types.

You may use information from the PREVIOUS MESSAGES only to disambiguate references or support continuity.


{context['custom_prompt']}

# EXTRACTION RULES

1. Only emit facts where both the subject and object match IDs in ENTITIES.
2. Each fact must involve two **distinct** entities.
3. Use a SCREAMING_SNAKE_CASE string as the `relation_type` (e.g., FOUNDED, WORKS_AT).
4. Do not emit duplicate or semantically redundant facts.
5. The `fact_text` should quote or closely paraphrase the original source sentence(s).
6. Use `REFERENCE_TIME` to resolve vague or relative temporal expressions (e.g., "last week").
7. Do **not** hallucinate or infer temporal bounds from unrelated events.

# DATETIME RULES
```

**File:** graphiti_core/utils/maintenance/edge_operations.py (L87-163)
```python
async def extract_edges(
    clients: GraphitiClients,
    episode: EpisodicNode,
    nodes: list[EntityNode],
    previous_episodes: list[EpisodicNode],
    edge_type_map: dict[tuple[str, str], list[str]],
    group_id: str = '',
    edge_types: dict[str, type[BaseModel]] | None = None,
) -> list[EntityEdge]:
    start = time()

    extract_edges_max_tokens = 16384
    llm_client = clients.llm_client

    edge_type_signature_map: dict[str, tuple[str, str]] = {
        edge_type: signature
        for signature, edge_types in edge_type_map.items()
        for edge_type in edge_types
    }

    edge_types_context = (
        [
            {
                'fact_type_name': type_name,
                'fact_type_signature': edge_type_signature_map.get(type_name, ('Entity', 'Entity')),
                'fact_type_description': type_model.__doc__,
            }
            for type_name, type_model in edge_types.items()
        ]
        if edge_types is not None
        else []
    )

    # Prepare context for LLM
    context = {
        'episode_content': episode.content,
        'nodes': [
            {'id': idx, 'name': node.name, 'entity_types': node.labels}
            for idx, node in enumerate(nodes)
        ],
        'previous_episodes': [ep.content for ep in previous_episodes],
        'reference_time': episode.valid_at,
        'edge_types': edge_types_context,
        'custom_prompt': '',
        'ensure_ascii': clients.ensure_ascii,
    }

    facts_missed = True
    reflexion_iterations = 0
    while facts_missed and reflexion_iterations <= MAX_REFLEXION_ITERATIONS:
        llm_response = await llm_client.generate_response(
            prompt_library.extract_edges.edge(context),
            response_model=ExtractedEdges,
            max_tokens=extract_edges_max_tokens,
        )
        edges_data = ExtractedEdges(**llm_response).edges

        context['extracted_facts'] = [edge_data.fact for edge_data in edges_data]

        reflexion_iterations += 1
        if reflexion_iterations < MAX_REFLEXION_ITERATIONS:
            reflexion_response = await llm_client.generate_response(
                prompt_library.extract_edges.reflexion(context),
                response_model=MissingFacts,
                max_tokens=extract_edges_max_tokens,
            )

            missing_facts = reflexion_response.get('missing_facts', [])

            custom_prompt = 'The following facts were missed in a previous extraction: '
            for fact in missing_facts:
                custom_prompt += f'\n{fact},'

            context['custom_prompt'] = custom_prompt

            facts_missed = len(missing_facts) != 0

```

**File:** graphiti_core/utils/maintenance/edge_operations.py (L225-312)
```python
async def resolve_extracted_edges(
    clients: GraphitiClients,
    extracted_edges: list[EntityEdge],
    episode: EpisodicNode,
    entities: list[EntityNode],
    edge_types: dict[str, type[BaseModel]],
    edge_type_map: dict[tuple[str, str], list[str]],
) -> tuple[list[EntityEdge], list[EntityEdge]]:
    driver = clients.driver
    llm_client = clients.llm_client
    embedder = clients.embedder
    await create_entity_edge_embeddings(embedder, extracted_edges)

    valid_edges_list: list[list[EntityEdge]] = await semaphore_gather(
        *[
            EntityEdge.get_between_nodes(driver, edge.source_node_uuid, edge.target_node_uuid)
            for edge in extracted_edges
        ]
    )

    related_edges_results: list[SearchResults] = await semaphore_gather(
        *[
            search(
                clients,
                extracted_edge.fact,
                group_ids=[extracted_edge.group_id],
                config=EDGE_HYBRID_SEARCH_RRF,
                search_filter=SearchFilters(edge_uuids=[edge.uuid for edge in valid_edges]),
            )
            for extracted_edge, valid_edges in zip(extracted_edges, valid_edges_list, strict=True)
        ]
    )

    related_edges_lists: list[list[EntityEdge]] = [result.edges for result in related_edges_results]

    edge_invalidation_candidate_results: list[SearchResults] = await semaphore_gather(
        *[
            search(
                clients,
                extracted_edge.fact,
                group_ids=[extracted_edge.group_id],
                config=EDGE_HYBRID_SEARCH_RRF,
                search_filter=SearchFilters(),
            )
            for extracted_edge in extracted_edges
        ]
    )

    edge_invalidation_candidates: list[list[EntityEdge]] = [
        result.edges for result in edge_invalidation_candidate_results
    ]

    logger.debug(
        f'Related edges lists: {[(e.name, e.uuid) for edges_lst in related_edges_lists for e in edges_lst]}'
    )

    # Build entity hash table
    uuid_entity_map: dict[str, EntityNode] = {entity.uuid: entity for entity in entities}

    # Determine which edge types are relevant for each edge
    edge_types_lst: list[dict[str, type[BaseModel]]] = []
    for extracted_edge in extracted_edges:
        source_node = uuid_entity_map.get(extracted_edge.source_node_uuid)
        target_node = uuid_entity_map.get(extracted_edge.target_node_uuid)
        source_node_labels = (
            source_node.labels + ['Entity'] if source_node is not None else ['Entity']
        )
        target_node_labels = (
            target_node.labels + ['Entity'] if target_node is not None else ['Entity']
        )
        label_tuples = [
            (source_label, target_label)
            for source_label in source_node_labels
            for target_label in target_node_labels
        ]

        extracted_edge_types = {}
        for label_tuple in label_tuples:
            type_names = edge_type_map.get(label_tuple, [])
            for type_name in type_names:
                type_model = edge_types.get(type_name)
                if type_model is None:
                    continue

                extracted_edge_types[type_name] = type_model

        edge_types_lst.append(extracted_edge_types)

```

**File:** tests/evals/eval_e2e_graph_building.py (L105-123)
```python
async def build_baseline_graph(multi_session_count: int, session_length: int):
    # Use gpt-4.1-mini for graph building baseline
    llm_client = OpenAIClient(config=LLMConfig(model='gpt-4.1-mini'))
    graphiti = Graphiti(NEO4J_URI, NEO4j_USER, NEO4j_PASSWORD, llm_client=llm_client)

    add_episode_results, _ = await build_graph(
        'baseline', multi_session_count, session_length, graphiti
    )

    filename = 'baseline_graph_results.json'

    serializable_baseline_graph_results = {
        key: [item.model_dump(mode='json') for item in value]
        for key, value in add_episode_results.items()
    }

    with open(filename, 'w') as file:
        json.dump(serializable_baseline_graph_results, file, indent=4, default=str)

```

**File:** tests/evals/eval_e2e_graph_building.py (L125-180)
```python
async def eval_graph(multi_session_count: int, session_length: int, llm_client=None) -> float:
    if llm_client is None:
        llm_client = OpenAIClient(config=LLMConfig(model='gpt-4.1-mini'))
    graphiti = Graphiti(NEO4J_URI, NEO4j_USER, NEO4j_PASSWORD, llm_client=llm_client)
    with open('baseline_graph_results.json') as file:
        baseline_results_raw = json.load(file)

        baseline_results: dict[str, list[AddEpisodeResults]] = {
            key: [AddEpisodeResults(**item) for item in value]
            for key, value in baseline_results_raw.items()
        }
    add_episode_results, add_episode_context = await build_graph(
        'candidate', multi_session_count, session_length, graphiti
    )

    filename = 'candidate_graph_results.json'

    candidate_baseline_graph_results = {
        key: [item.model_dump(mode='json') for item in value]
        for key, value in add_episode_results.items()
    }

    with open(filename, 'w') as file:
        json.dump(candidate_baseline_graph_results, file, indent=4, default=str)

    raw_score = 0
    user_count = 0
    for user_id in add_episode_results:
        user_count += 1
        user_raw_score = 0
        for baseline_result, add_episode_result, episodes in zip(
            baseline_results[user_id],
            add_episode_results[user_id],
            add_episode_context[user_id],
            strict=False,
        ):
            context = {
                'baseline': baseline_result,
                'candidate': add_episode_result,
                'message': episodes[0],
                'previous_messages': episodes[1:],
            }

            llm_response = await llm_client.generate_response(
                prompt_library.eval.eval_add_episode_results(context),
                response_model=EvalAddEpisodeResults,
            )

            candidate_is_worse = llm_response.get('candidate_is_worse', False)
            user_raw_score += 0 if candidate_is_worse else 1
            print('llm_response:', llm_response)
        user_score = user_raw_score / len(add_episode_results[user_id])
        raw_score += user_score
    score = raw_score / user_count

    return score
```

**File:** graphiti_core/prompts/eval.py (L127-156)
```python
def eval_add_episode_results(context: dict[str, Any]) -> list[Message]:
    sys_prompt = """You are a judge that determines whether a baseline graph building result from a list of messages is better
        than a candidate graph building result based on the same messages."""

    user_prompt = f"""
    Given the following PREVIOUS MESSAGES and MESSAGE, determine if the BASELINE graph data extracted from the 
    conversation is higher quality than the CANDIDATE graph data extracted from the conversation.
    
    Return False if the BASELINE extraction is better, and True otherwise. If the CANDIDATE extraction and
    BASELINE extraction are nearly identical in quality, return True. Add your reasoning for your decision to the reasoning field
    
    <PREVIOUS MESSAGES>
    {context['previous_messages']}
    </PREVIOUS MESSAGES>
    <MESSAGE>
    {context['message']}
    </MESSAGE>
    
    <BASELINE>
    {context['baseline']}
    </BASELINE>
    
    <CANDIDATE>
    {context['candidate']}
    </CANDIDATE>
    """
    return [
        Message(role='system', content=sys_prompt),
        Message(role='user', content=user_prompt),
    ]
```

**File:** graphiti_core/search/search_utils.py (L168-538)
```python
    )

    communities = [get_community_node_from_record(record) for record in records]

    return communities


async def edge_fulltext_search(
    driver: GraphDriver,
    query: str,
    search_filter: SearchFilters,
    group_ids: list[str] | None = None,
    limit=RELEVANT_SCHEMA_LIMIT,
) -> list[EntityEdge]:
    # fulltext search over facts
    fuzzy_query = fulltext_query(query, group_ids, driver)

    if fuzzy_query == '':
        return []

    match_query = """
    YIELD relationship AS rel, score
    MATCH (n:Entity)-[e:RELATES_TO {uuid: rel.uuid}]->(m:Entity)
    """
    if driver.provider == GraphProvider.KUZU:
        match_query = """
        YIELD node, score
        MATCH (n:Entity)-[:RELATES_TO]->(e:RelatesToNode_ {uuid: node.uuid})-[:RELATES_TO]->(m:Entity)
        """

    filter_queries, filter_params = edge_search_filter_query_constructor(
        search_filter, driver.provider
    )

    if group_ids is not None:
        filter_queries.append('e.group_id IN $group_ids')
        filter_params['group_ids'] = group_ids

    filter_query = ''
    if filter_queries:
        filter_query = ' WHERE ' + (' AND '.join(filter_queries))

    if driver.provider == GraphProvider.NEPTUNE:
        res = driver.run_aoss_query('edge_name_and_fact', query)  # pyright: ignore reportAttributeAccessIssue
        if res['hits']['total']['value'] > 0:
            input_ids = []
            for r in res['hits']['hits']:
                input_ids.append({'id': r['_source']['uuid'], 'score': r['_score']})

            # Match the edge ids and return the values
            query = (
                """
                                                                                                                                        UNWIND $ids as id
                                                                                                                                        MATCH (n:Entity)-[e:RELATES_TO]->(m:Entity)
                                                                                                                                        WHERE e.group_id IN $group_ids 
                                                                                                                                        AND id(e)=id 
                                                                                                                                        """
                + filter_query
                + """
                AND id(e)=id
                WITH e, id.score as score, startNode(e) AS n, endNode(e) AS m
                RETURN
                    e.uuid AS uuid,
                    e.group_id AS group_id,
                    n.uuid AS source_node_uuid,
                    m.uuid AS target_node_uuid,
                    e.created_at AS created_at,
                    e.name AS name,
                    e.fact AS fact,
                    split(e.episodes, ",") AS episodes,
                    e.expired_at AS expired_at,
                    e.valid_at AS valid_at,
                    e.invalid_at AS invalid_at,
                    properties(e) AS attributes
                ORDER BY score DESC LIMIT $limit
                            """
            )

            records, _, _ = await driver.execute_query(
                query,
                query=fuzzy_query,
                ids=input_ids,
                limit=limit,
                routing_='r',
                **filter_params,
            )
        else:
            return []
    elif driver.aoss_client:
        route = group_ids[0] if group_ids else None
        filters = build_aoss_edge_filters(group_ids or [], search_filter)
        res = await driver.aoss_client.search(
            index=ENTITY_EDGE_INDEX_NAME,
            params={'routing': route},
            body={
                'size': limit,
                '_source': ['uuid'],
                'query': {
                    'bool': {
                        'filter': filters,
                        'must': [{'match': {'fact': {'query': query, 'operator': 'or'}}}],
                    }
                },
            },
        )

        if res['hits']['total']['value'] > 0:
            input_uuids = {}
            for r in res['hits']['hits']:
                input_uuids[r['_source']['uuid']] = r['_score']

            # Get edges
            entity_edges = await EntityEdge.get_by_uuids(driver, list(input_uuids.keys()))
            entity_edges.sort(key=lambda e: input_uuids.get(e.uuid, 0), reverse=True)
            return entity_edges
        else:
            return []
    else:
        query = (
            get_relationships_query('edge_name_and_fact', limit=limit, provider=driver.provider)
            + match_query
            + filter_query
            + """
            WITH e, score, n, m
            RETURN
            """
            + get_entity_edge_return_query(driver.provider)
            + """
            ORDER BY score DESC
            LIMIT $limit
            """
        )

        records, _, _ = await driver.execute_query(
            query,
            query=fuzzy_query,
            limit=limit,
            routing_='r',
            **filter_params,
        )

    edges = [get_entity_edge_from_record(record, driver.provider) for record in records]

    return edges


async def edge_similarity_search(
    driver: GraphDriver,
    search_vector: list[float],
    source_node_uuid: str | None,
    target_node_uuid: str | None,
    search_filter: SearchFilters,
    group_ids: list[str] | None = None,
    limit: int = RELEVANT_SCHEMA_LIMIT,
    min_score: float = DEFAULT_MIN_SCORE,
) -> list[EntityEdge]:
    match_query = """
        MATCH (n:Entity)-[e:RELATES_TO]->(m:Entity)
    """
    if driver.provider == GraphProvider.KUZU:
        match_query = """
            MATCH (n:Entity)-[:RELATES_TO]->(e:RelatesToNode_)-[:RELATES_TO]->(m:Entity)
        """

    filter_queries, filter_params = edge_search_filter_query_constructor(
        search_filter, driver.provider
    )

    if group_ids is not None:
        filter_queries.append('e.group_id IN $group_ids')
        filter_params['group_ids'] = group_ids

        if source_node_uuid is not None:
            filter_params['source_uuid'] = source_node_uuid
            filter_queries.append('n.uuid = $source_uuid')

        if target_node_uuid is not None:
            filter_params['target_uuid'] = target_node_uuid
            filter_queries.append('m.uuid = $target_uuid')

    filter_query = ''
    if filter_queries:
        filter_query = ' WHERE ' + (' AND '.join(filter_queries))

    search_vector_var = '$search_vector'
    if driver.provider == GraphProvider.KUZU:
        search_vector_var = f'CAST($search_vector AS FLOAT[{len(search_vector)}])'

    if driver.provider == GraphProvider.NEPTUNE:
        query = (
            """
                                                                                                                MATCH (n:Entity)-[e:RELATES_TO]->(m:Entity)
                                                                                                                """
            + filter_query
            + """
            RETURN DISTINCT id(e) as id, e.fact_embedding as embedding
            """
        )
        resp, header, _ = await driver.execute_query(
            query,
            search_vector=search_vector,
            limit=limit,
            min_score=min_score,
            routing_='r',
            **filter_params,
        )

        if len(resp) > 0:
            # Calculate Cosine similarity then return the edge ids
            input_ids = []
            for r in resp:
                if r['embedding']:
                    score = calculate_cosine_similarity(
                        search_vector, list(map(float, r['embedding'].split(',')))
                    )
                    if score > min_score:
                        input_ids.append({'id': r['id'], 'score': score})

            # Match the edge ides and return the values
            query = """
                UNWIND $ids as i
                MATCH ()-[r]->()
                WHERE id(r) = i.id
                RETURN
                    r.uuid AS uuid,
                    r.group_id AS group_id,
                    startNode(r).uuid AS source_node_uuid,
                    endNode(r).uuid AS target_node_uuid,
                    r.created_at AS created_at,
                    r.name AS name,
                    r.fact AS fact,
                    split(r.episodes, ",") AS episodes,
                    r.expired_at AS expired_at,
                    r.valid_at AS valid_at,
                    r.invalid_at AS invalid_at,
                    properties(r) AS attributes
                ORDER BY i.score DESC
                LIMIT $limit
                    """
            records, _, _ = await driver.execute_query(
                query,
                ids=input_ids,
                search_vector=search_vector,
                limit=limit,
                min_score=min_score,
                routing_='r',
                **filter_params,
            )
        else:
            return []
    elif driver.aoss_client:
        route = group_ids[0] if group_ids else None
        filters = build_aoss_edge_filters(group_ids or [], search_filter)
        res = await driver.aoss_client.search(
            index=ENTITY_EDGE_INDEX_NAME,
            params={'routing': route},
            body={
                'size': limit,
                '_source': ['uuid'],
                'query': {
                    'knn': {
                        'fact_embedding': {
                            'vector': list(map(float, search_vector)),
                            'k': limit,
                            'filter': {'bool': {'filter': filters}},
                        }
                    }
                },
            },
        )

        if res['hits']['total']['value'] > 0:
            input_uuids = {}
            for r in res['hits']['hits']:
                input_uuids[r['_source']['uuid']] = r['_score']

            # Get edges
            entity_edges = await EntityEdge.get_by_uuids(driver, list(input_uuids.keys()))
            entity_edges.sort(key=lambda e: input_uuids.get(e.uuid, 0), reverse=True)
            return entity_edges
        return []

    else:
        query = (
            match_query
            + filter_query
            + """
            WITH DISTINCT e, n, m, """
            + get_vector_cosine_func_query('e.fact_embedding', search_vector_var, driver.provider)
            + """ AS score
            WHERE score > $min_score
            RETURN
            """
            + get_entity_edge_return_query(driver.provider)
            + """
            ORDER BY score DESC
            LIMIT $limit
            """
        )

        records, _, _ = await driver.execute_query(
            query,
            search_vector=search_vector,
            limit=limit,
            min_score=min_score,
            routing_='r',
            **filter_params,
        )

    edges = [get_entity_edge_from_record(record, driver.provider) for record in records]

    return edges


async def edge_bfs_search(
    driver: GraphDriver,
    bfs_origin_node_uuids: list[str] | None,
    bfs_max_depth: int,
    search_filter: SearchFilters,
    group_ids: list[str] | None = None,
    limit: int = RELEVANT_SCHEMA_LIMIT,
) -> list[EntityEdge]:
    # vector similarity search over embedded facts
    if bfs_origin_node_uuids is None or len(bfs_origin_node_uuids) == 0:
        return []

    filter_queries, filter_params = edge_search_filter_query_constructor(
        search_filter, driver.provider
    )

    if group_ids is not None:
        filter_queries.append('e.group_id IN $group_ids')
        filter_params['group_ids'] = group_ids

    filter_query = ''
    if filter_queries:
        filter_query = ' WHERE ' + (' AND '.join(filter_queries))

    if driver.provider == GraphProvider.KUZU:
        # Kuzu stores entity edges twice with an intermediate node, so we need to match them
        # separately for the correct BFS depth.
        depth = bfs_max_depth * 2 - 1
        match_queries = [
            f"""
            UNWIND $bfs_origin_node_uuids AS origin_uuid
            MATCH path = (origin:Entity {{uuid: origin_uuid}})-[:RELATES_TO*1..{depth}]->(:RelatesToNode_)
            UNWIND nodes(path) AS relNode
            MATCH (n:Entity)-[:RELATES_TO]->(e:RelatesToNode_ {{uuid: relNode.uuid}})-[:RELATES_TO]->(m:Entity)
            """,
        ]
        if bfs_max_depth > 1:
            depth = (bfs_max_depth - 1) * 2 - 1
            match_queries.append(f"""
                UNWIND $bfs_origin_node_uuids AS origin_uuid
                MATCH path = (origin:Episodic {{uuid: origin_uuid}})-[:MENTIONS]->(:Entity)-[:RELATES_TO*1..{depth}]->(:RelatesToNode_)
                UNWIND nodes(path) AS relNode
                MATCH (n:Entity)-[:RELATES_TO]->(e:RelatesToNode_ {{uuid: relNode.uuid}})-[:RELATES_TO]->(m:Entity)
            """)

        records = []
        for match_query in match_queries:
            sub_records, _, _ = await driver.execute_query(
                match_query
                + filter_query
                + """
                RETURN DISTINCT
                """
                + get_entity_edge_return_query(driver.provider)
                + """
                LIMIT $limit
                """,
```

**File:** graphiti_core/search/search_utils.py (L1416-1471)
```python
                attributes: x.attributes
            }) AS matches

            RETURN
            node.uuid AS search_node_uuid, matches
            """
        )
    else:
        query = (
            """
                                                                                                                UNWIND $nodes AS node
                                                                                                                MATCH (n:Entity {group_id: $group_id})
                                                                                                                """
            + filter_query
            + """
            WITH node, n, """
            + get_vector_cosine_func_query(
                'n.name_embedding', 'node.name_embedding', driver.provider
            )
            + """ AS score
            WHERE score > $min_score
            WITH node, collect(n)[..$limit] AS top_vector_nodes, collect(n.uuid) AS vector_node_uuids
            """
            + get_nodes_query(
                'node_name_and_summary',
                'node.fulltext_query',
                limit=limit,
                provider=driver.provider,
            )
            + """
            YIELD node AS m
            WHERE m.group_id = $group_id
            WITH node, top_vector_nodes, vector_node_uuids, collect(m) AS fulltext_nodes

            WITH node,
                top_vector_nodes,
                [m IN fulltext_nodes WHERE NOT m.uuid IN vector_node_uuids] AS filtered_fulltext_nodes

            WITH node, top_vector_nodes + filtered_fulltext_nodes AS combined_nodes

            UNWIND combined_nodes AS combined_node
            WITH node, collect(DISTINCT combined_node) AS deduped_nodes

            RETURN
            node.uuid AS search_node_uuid,
            [x IN deduped_nodes | {
                uuid: x.uuid,
                name: x.name,
                name_embedding: x.name_embedding,
                group_id: x.group_id,
                created_at: x.created_at,
                summary: x.summary,
                labels: labels(x),
                attributes: properties(x)
            }] AS matches
            """
```

**File:** graphiti_core/search/search.py (L268-275)
```python
    elif config.reranker == EdgeReranker.cross_encoder:
        fact_to_uuid_map = {edge.fact: edge.uuid for edge in list(edge_uuid_map.values())[:limit]}
        reranked_facts = await cross_encoder.rank(query, list(fact_to_uuid_map.keys()))
        reranked_uuids = [
            fact_to_uuid_map[fact] for fact, score in reranked_facts if score >= reranker_min_score
        ]
        edge_scores = [score for _, score in reranked_facts if score >= reranker_min_score]
    elif config.reranker == EdgeReranker.node_distance:
```

**File:** mcp_server/graphiti_mcp_server.py (L829-907)
```python
@mcp.tool()
async def search_memory_nodes(
    query: str,
    group_ids: list[str] | None = None,
    max_nodes: int = 10,
    center_node_uuid: str | None = None,
    entity: str = '',  # cursor seems to break with None
) -> NodeSearchResponse | ErrorResponse:
    """Search the graph memory for relevant node summaries.
    These contain a summary of all of a node's relationships with other nodes.

    Note: entity is a single entity type to filter results (permitted: "Preference", "Procedure").

    Args:
        query: The search query
        group_ids: Optional list of group IDs to filter results
        max_nodes: Maximum number of nodes to return (default: 10)
        center_node_uuid: Optional UUID of a node to center the search around
        entity: Optional single entity type to filter results (permitted: "Preference", "Procedure")
    """
    global graphiti_client

    if graphiti_client is None:
        return ErrorResponse(error='Graphiti client not initialized')

    try:
        # Use the provided group_ids or fall back to the default from config if none provided
        effective_group_ids = (
            group_ids if group_ids is not None else [config.group_id] if config.group_id else []
        )

        # Configure the search
        if center_node_uuid is not None:
            search_config = NODE_HYBRID_SEARCH_NODE_DISTANCE.model_copy(deep=True)
        else:
            search_config = NODE_HYBRID_SEARCH_RRF.model_copy(deep=True)
        search_config.limit = max_nodes

        filters = SearchFilters()
        if entity != '':
            filters.node_labels = [entity]

        # We've already checked that graphiti_client is not None above
        assert graphiti_client is not None

        # Use cast to help the type checker understand that graphiti_client is not None
        client = cast(Graphiti, graphiti_client)

        # Perform the search using the _search method
        search_results = await client._search(
            query=query,
            config=search_config,
            group_ids=effective_group_ids,
            center_node_uuid=center_node_uuid,
            search_filter=filters,
        )

        if not search_results.nodes:
            return NodeSearchResponse(message='No relevant nodes found', nodes=[])

        # Format the node results
        formatted_nodes: list[NodeResult] = [
            {
                'uuid': node.uuid,
                'name': node.name,
                'summary': node.summary if hasattr(node, 'summary') else '',
                'labels': node.labels if hasattr(node, 'labels') else [],
                'group_id': node.group_id,
                'created_at': node.created_at.isoformat(),
                'attributes': node.attributes if hasattr(node, 'attributes') else {},
            }
            for node in search_results.nodes
        ]

        return NodeSearchResponse(message='Nodes retrieved successfully', nodes=formatted_nodes)
    except Exception as e:
        error_msg = str(e)
        logger.error(f'Error searching nodes: {error_msg}')
        return ErrorResponse(error=f'Error searching nodes: {error_msg}')
```
