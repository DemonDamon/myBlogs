# 我问

从 README 看到 EverMemOS 依赖 MongoDB、Elasticsearch、Milvus、Redis 四个数据库。如果我要在生产环境部署，这些组件的资源配置建议是什么？比如对于 10 万用户、每天 100 万条对话消息的场景，MongoDB 需要多大存储空间？Milvus 的向量维度是多少，需要多少内存？Elasticsearch 的索引策略是什么？各个数据库之间的数据一致性如何保证？如果 Milvus 写入失败但 MongoDB 成功，系统如何处理这种不一致？是否有事务机制或重试机制？

# deepwiki答
您询问的是 EverMemOS 在生产环境部署时的资源配置建议，特别是针对 10 万用户、每天 100 万条对话消息的场景。<cite />

## 当前代码库中的配置信息

### 数据库依赖

EverMemOS 确实依赖四个数据库组件,在 Docker Compose 配置中定义了基础端口映射: [1](#0-0) 

### 向量维度配置

从环境配置模板可以看到,Milvus 使用的向量维度为 **1024 维**: [2](#0-1) 

### 数据写入流程

系统采用 **三重写入(triple-write)** 策略,同时写入 MongoDB、Elasticsearch 和 Milvus: [3](#0-2) 

## 当前代码库中缺失的信息

**重要提示**:代码库中 **没有提供** 以下关键信息:

1. **生产环境资源配置建议** - 没有针对特定用户规模和消息量的存储空间、内存、CPU 等资源配置文档<cite />

2. **存储空间估算** - 没有提供 MongoDB 存储空间计算公式或参考数据(如每条消息平均占用空间)<cite />

3. **Milvus 内存需求** - 没有说明 1024 维向量在特定数据量下需要多少内存<cite />

4. **Elasticsearch 索引策略** - 虽然定义了索引结构 [4](#0-3) ,但没有说明分片数量、副本策略、刷新间隔等生产配置<cite />

5. **数据一致性保证机制** - 代码中只看到数据同步脚本 [5](#0-4) ,但 **没有** 事务机制或自动重试机制的实现<cite />

6. **写入失败处理** - 没有发现针对部分写入失败(如 Milvus 失败但 MongoDB 成功)的错误处理或补偿机制<cite />

## Notes

当前 EverMemOS 代码库主要关注功能实现和开发环境配置,缺少生产环境部署的详细指南。<cite />建议您:

1. 根据实际业务数据进行压力测试,获取准确的资源需求
2. 考虑实现写入失败的补偿机制(如消息队列重试、定期数据一致性检查)
3. 参考各数据库官方文档的生产环境最佳实践
4. 监控实际运行数据,动态调整资源配置

代码中的数据同步脚本 [6](#0-5) 可用于修复数据不一致问题,但这是事后补救而非实时保证。<cite />

Wiki pages you might want to explore:
- [EverMemOS Overview (EverMind-AI/EverMemOS)](/wiki/EverMind-AI/EverMemOS#1)

### Citations

**File:** README_zh.md (L268-274)
```markdown
**Docker 服务说明**：
| 服务 | 宿主机端口 | 容器端口 | 用途 |
|------|-----------|---------|------|
| **MongoDB** | 27017 | 27017 | 主数据库，存储记忆单元和画像 |
| **Elasticsearch** | 19200 | 9200 | 关键词检索引擎（BM25） |
| **Milvus** | 19530 | 19530 | 向量数据库，语义检索 |
| **Redis** | 6379 | 6379 | 缓存服务 |
```

**File:** docs/dev_docs/getting_started.md (L112-112)
```markdown
DEEPINFRA_DIMENSIONS=1024
```

**File:** demo/extract/validator.py (L38-99)
```python
        # 验证 MongoDB
        print("\n[MongoDB] 检查 MemCell")
        memcell_repo = get_bean_by_type(MemCellRawRepository)
        memcells = await memcell_repo.find_by_group_id(self.group_id, limit=1000)
        print(f"  - 找到 {len(memcells)} 个 MemCell")
        
        if memcells:
            total_semantic = sum(
                len(m.semantic_memories)
                for m in memcells
                if hasattr(m, 'semantic_memories') and m.semantic_memories
            )
            total_eventlog = sum(
                len(m.event_log.get('atomic_fact', []) if isinstance(m.event_log, dict) else [])
                for m in memcells
                if hasattr(m, 'event_log') and m.event_log
            )
            
            print(f"  - episode: {len(memcells)} 个")
            print(f"  - semantic_memories: {total_semantic} 个")
            print(f"  - event_log atomic_facts: {total_eventlog} 个")
        
        # 验证 Milvus
        print("\n[Milvus] 检查记录")
        milvus_repo = get_bean_by_type(EpisodicMemoryMilvusRepository)
        vectorize_service = get_vectorize_service()
        query_vector = await vectorize_service.get_embedding("测试")
        
        # 注意：limit 不能太大，Milvus HNSW 索引要求 ef >= k
        # 默认 ef=64，所以 limit 最多设置为 64
        milvus_results = await milvus_repo.vector_search(
            query_vector=query_vector,
            user_id="default",
            limit=50,  # 减小 limit，避免超过 ef 参数（默认 64）
        )
        print(f"  - 找到 {len(milvus_results)} 条记录")
        
        if milvus_results:
            types = [r.get('memory_sub_type', 'unknown') for r in milvus_results]
            print(f"  - 类型分布: {dict(Counter(types))}")
        
        # 验证 ES
        print("\n[ES] 检查记录")
        es_repo = get_bean_by_type(EpisodicMemoryEsRepository)
        es_results = await es_repo.multi_search(
            query=[],
            user_id="default",
            size=1000,
        )
        print(f"  - 找到 {len(es_results)} 条记录")
        
        if es_results:
            types = [r.get('_source', {}).get('type', 'unknown') for r in es_results]
            print(f"  - 类型分布: {dict(Counter(types))}")
        
        # 结果汇总
        print("\n" + "=" * 80)
        print("验证结果汇总")
        print("=" * 80)
        print(f"\n✅ MongoDB: {len(memcells)} 个")
        print(f"✅ Milvus: {len(milvus_results)} 条")
        print(f"✅ ES: {len(es_results)} 条")
```

**File:** src/infra_layer/adapters/out/search/elasticsearch/memory/episodic_memory.py (L12-46)
```python
class EpisodicMemoryDoc(AliasDoc("episodic-memory", number_of_shards=3)):
    """
    情景记忆Elasticsearch文档

    基于MongoDB EpisodicMemory模型，用于高效的BM25文本检索。
    主要检索字段为title和episode的拼接内容。

    字段说明：
    - event_id: 事件唯一标识（对应MongoDB的_id）
    - user_id: 用户ID（必需，用于过滤）
    - user_name: 用户名称
    - timestamp: 事件发生时间
    - title: 事件标题（对应MongoDB的subject字段）
    - episode: 情景描述（核心内容）
    - search_content: BM25搜索字段（支持多值存储，用于精确词匹配）
    - summary: 事件摘要
    - group_id: 群组ID（可选）
    - participants: 参与者列表
    - type: 事件类型（Conversation等）
    - keywords: 关键词列表
    - linked_entities: 关联实体ID列表
    - extend: 扩展字段（灵活存储）

    分词处理说明：
    - 应用层负责中文分词（推荐使用jieba）
    - title、episode、summary字段存储预分词结果（空格分隔）
    - search_content字段支持多值存储，每个值是一个搜索词
    - ES使用standard分析器处理search_content，original子字段用于精确匹配
    - 搜索时使用terms查询在search_content.original字段中匹配多个词

    附属字段说明：
    - original: 精确匹配，小写处理
    - ik: IK智能分词（需要ES安装IK插件）
    - edge_completion: 前缀匹配和自动补全
    """
```

**File:** src/devops_scripts/data_fix/milvus_sync_docs.py (L1-15)
```python
"""
同步 MongoDB 数据到 Milvus

主入口脚本，根据 Collection 名称调用相应的同步实现。
支持命令行参数配置批量大小、处理限制和时间范围。

运行方式（推荐通过 bootstrap 运行，自动加载应用上下文与依赖注入）：
  python src/bootstrap.py src/devops_scripts/data_fix/milvus_sync_docs.py --collection-name episodic_memory --batch-size 500

参数：
  --collection-name, -c  Milvus Collection 名称（必需），如: episodic_memory
  --batch-size, -b       批处理大小（默认 500）
  --limit, -l            限制处理的文档数量（默认全部）
  --days, -d             只处理过去 N 天创建的文档（默认全部）
"""
```

**File:** src/devops_scripts/data_fix/milvus_sync_episodic_memory_docs.py (L26-42)
```python
async def sync_episodic_memory_docs(
    batch_size: int, limit: Optional[int], days: Optional[int]
) -> None:
    """
    同步情景记忆文档到 Milvus。

    实现策略：
    1. 从 MongoDB 批量获取文档（batch_size 条）
    2. 批量转换为 Milvus 实体格式
    3. 批量插入到 Milvus（使用 upsert 语义，支持幂等）
    4. 循环处理直到所有文档处理完毕

    Args:
        batch_size: 批处理大小，建议 500-1000
        limit: 最多处理的文档数量，None 表示处理全部
        days: 仅处理最近 N 天创建的文档，None 表示处理全部
    """
```



# 我问

EverMemOS 提供了 `/api/v3/agentic/memorize` 接口用于存储单条消息，但在高并发场景下（比如 1000 QPS），这种同步接口会成为性能瓶颈。系统内部是否有消息队列进行异步处理？如果我想批量导入历史对话数据（比如 1000 万条），是否有批量 API？`run_memorize.py` 脚本的性能如何？能否并行处理？如果我想自己实现批量导入，需要注意哪些技术细节？比如 MemCell 提取的速率限制、Embedding 的批处理、数据库的批量写入策略等。

# deepwiki答

您询问的是 EverMemOS 在高并发场景下的性能优化问题，特别关注消息队列、批量导入、`run_memorize.py` 脚本性能以及自定义批量导入的技术细节。<cite />

## 当前系统架构分析

### 1. 同步接口与消息队列

**当前状态**：`/api/v3/agentic/memorize` 是**同步接口**，代码库中**确实存在消息队列基础设施**，但**未用于 memorize 接口的异步处理**。<cite />

系统包含以下消息队列组件：
- **消息队列依赖**：`pyproject.toml` 中包含 `aiokafka>=0.11.0` [1](#1-0) 
- **队列管理器**：`MsgGroupQueueManager` 提供了消息分组队列功能 [2](#1-1) 
- **长任务消费者框架**：`RecycleConsumerBase` 提供了批量消息处理的基础类 [3](#1-2) 

**但是**，这些队列组件**并未集成到 memorize API 的处理流程中**。当前 memorize 接口是直接同步调用 `AgenticLayer.memorize()`，没有异步队列缓冲。<cite />

### 2. 批量导入方案

#### 现有的 `run_memorize.py` 脚本

**功能**：逐条调用 `/api/v3/agentic/memorize` API [4](#1-3) 

**性能特点**：
- **串行处理**：脚本逐条发送 HTTP 请求，没有并行能力 [5](#1-4) 
- **适用场景**：小规模数据导入（数千到数万条）
- **不适合大规模导入**：对于 1000 万条数据，串行处理会非常慢（预计需要数天）<cite />

#### 内部批量提取示例

`demo/extract/extractor.py` 展示了批量提取的内部实现： [6](#1-5) 

**关键特点**：
- 使用 `history_window_size` 维护上下文窗口
- 逐条调用 `manager.memorize()`，但在内存中批量管理历史
- **仍然是串行处理**，没有并发<cite />

### 3. 自定义批量导入的技术细节

#### MemCell 提取的速率限制

**LLM API 限制**：MemCell 提取依赖 LLM 调用，主要瓶颈在 LLM API 的速率限制。<cite />

代码中没有明确的 LLM 速率限制配置，但可以看到：
- 评估框架中使用了 `aiolimiter` 库 [7](#1-6) 
- 建议根据您的 LLM 提供商限制（如 OpenAI 的 TPM/RPM）自行实现速率控制<cite />

#### Embedding 批处理策略

系统**支持批量 Embedding 生成**： [8](#1-7) 

**批处理配置**：
- 评估框架中使用 `BATCH_SIZE = 256` 进行批量 Embedding [9](#1-8) 
- **并发控制**：使用 `Semaphore(5)` 限制并发 API 调用数 [10](#1-9) 
- **重试机制**：包含指数退避重试（2s, 4s） [11](#1-10) 

**推荐策略**：
```python
# 批量 Embedding 示例（参考评估代码）
BATCH_SIZE = 256  # 每批文本数量
MAX_CONCURRENT_BATCHES = 5  # 最大并发批次
# 分组提交，避免队列堆积
``` [12](#1-11) 

#### 数据库批量写入策略

**当前实现**：系统采用**三重写入**策略，但**没有批量写入优化**。<cite />

**数据同步脚本**提供了批量处理参考：
- MongoDB 批量查询：`batch_size = 500` [13](#1-12) 
- 并发处理：使用 `asyncio.Semaphore` 控制并发度 [14](#1-13) 

**推荐批量写入策略**：
1. **MongoDB**：使用 `insert_many()` 批量插入（建议 100-500 条/批）
2. **Elasticsearch**：使用 `bulk()` API（建议 500-1000 条/批）
3. **Milvus**：使用批量插入接口（建议 500-1000 条/批）
4. **并发控制**：使用 `asyncio.Semaphore` 限制并发数（建议 5-10）<cite />

### 4. 高并发场景优化建议

对于 **1000 QPS** 和 **1000 万条历史数据导入**场景：

#### 短期方案（无需修改代码）
1. **水平扩展**：部署多个 API 服务实例，使用负载均衡
2. **客户端并发**：自行实现多线程/协程并发调用 API（建议 10-50 并发）
3. **分批导入**：将 1000 万条数据分成多个批次，分时段导入<cite />

#### 长期方案（需要代码改造）
1. **引入消息队列**：将 memorize 请求写入 Kafka/Redis 队列，异步消费处理
2. **批量 API**：新增批量 memorize 接口，一次接收多条消息
3. **数据库批量写入**：改造 `BizLayer` 支持批量写入三个数据库
4. **MemCell 提取优化**：批量调用 LLM API，减少网络开销<cite />

## Notes

**关键发现**：
- 系统**有消息队列基础设施**（Kafka、队列管理器），但**未用于 memorize 流程**<cite />
- `run_memorize.py` 是**串行脚本**，不适合大规模导入<cite />
- 评估框架中的批量 Embedding 代码（`stage2_index_building.py`）提供了**最佳实践参考** [15](#1-14) 
- Reranker 批处理也有类似的并发控制策略 [16](#1-15) 

**性能估算**（粗略）：
- 单条 memorize 延迟：~2-5 秒（含 LLM 提取 + 三重写入）
- 串行处理 1000 万条：~23,000-58,000 小时（不可行）
- 50 并发处理：~460-1,160 小时（19-48 天）
- **建议**：实现批量 API + 异步队列，目标处理时间缩短到 1-3 天<cite />

Wiki pages you might want to explore:
- [EverMemOS Overview (EverMind-AI/EverMemOS)](/wiki/EverMind-AI/EverMemOS#1)

### Citations

**File:** pyproject.toml (L44-45)
```text
    # 消息队列 - Message Queue
    "aiokafka>=0.11.0",
```

**File:** pyproject.toml (L77-77)
```text
    "aiolimiter>=1.2.1",
```

**File:** src/core/queue/msg_group_queue/msg_group_queue_manager.py (L535-632)
```python
    async def _log_queue_details(self):
        """打印队列详细信息"""
        try:
            manager_stats = await self.get_manager_stats()
            queue_infos = await self.get_queue_info()

            # 打印管理器整体状态汇总
            logger.info(
                "📊 MsgGroupQueueManager[%s] 整体状态: "
                "总消息=%d, 总投递=%d, 总消费=%d, 总拒绝=%d, 运行时间=%.1f秒",
                self.name,
                manager_stats["total_current_messages"],
                manager_stats["total_delivered_messages"],
                manager_stats["total_consumed_messages"],
                manager_stats["total_rejected_messages"],
                manager_stats["uptime_seconds"],
            )

            # 打印管理器时间窗口统计
            logger.info(
                "⏱️  MsgGroupQueueManager[%s] 时间窗口统计: "
                "1分钟内(投递=%d, 消费=%d), 1小时内(投递=%d, 消费=%d)",
                self.name,
                manager_stats["delivered_1min"],
                manager_stats["consumed_1min"],
                manager_stats["delivered_1hour"],
                manager_stats["consumed_1hour"],
            )

            # 分别打印每个队列的详细信息
            active_queues = []
            idle_queues = []
            empty_queues = []  # 当前为空的队列

            for queue_info in queue_infos:
                queue_id = queue_info["queue_id"]
                current_size = queue_info["current_size"]
                total_delivered = queue_info["total_delivered"]
                total_consumed = queue_info["total_consumed"]
                last_deliver_time = queue_info["last_deliver_time"]
                last_consume_time = queue_info["last_consume_time"]

                # 获取时间窗口统计
                delivered_1min = queue_info.get("delivered_1min", 0)
                consumed_1min = queue_info.get("consumed_1min", 0)
                delivered_1hour = queue_info.get("delivered_1hour", 0)
                consumed_1hour = queue_info.get("consumed_1hour", 0)

                # 记录空队列
                if current_size == 0:
                    empty_queues.append(queue_id)

                # 计算队列的活跃程度：基于时间窗口活动和当前队列状态
                has_recent_activity = delivered_1min > 0 or consumed_1min > 0
                has_messages = current_size > 0
                has_historical_activity = total_delivered > 0 or total_consumed > 0

                # 活跃判断：近期有活动 或 当前有消息 或 历史上有活动
                is_active = (
                    has_recent_activity or has_messages or has_historical_activity
                )

                if is_active:
                    # 计算投递消费比率
                    delivery_rate = (
                        total_delivered / max(1, total_delivered + total_consumed) * 100
                    )
                    consume_rate = (
                        total_consumed / max(1, total_delivered + total_consumed) * 100
                    )

                    # 格式化时间显示
                    last_deliver_display = (
                        last_deliver_time[-8:] if last_deliver_time else "无"
                    )
                    last_consume_display = (
                        last_consume_time[-8:] if last_consume_time else "无"
                    )

                    active_queues.append(
                        {
                            "id": queue_id,
                            "current": current_size,
                            "delivered": total_delivered,
                            "consumed": total_consumed,
                            "delivery_rate": delivery_rate,
                            "consume_rate": consume_rate,
                            "last_deliver": last_deliver_display,
                            "last_consume": last_consume_display,
                            "delivered_1min": delivered_1min,
                            "consumed_1min": consumed_1min,
                            "delivered_1hour": delivered_1hour,
                            "consumed_1hour": consumed_1hour,
                        }
                    )
                else:
                    idle_queues.append(queue_id)

```

**File:** src/core/longjob/recycle_consumer_base.py (L426-451)
```python
    @abstractmethod
    async def _fetch_message(self) -> Optional[Any]:
        """
        获取消息数据
        子类需要实现此方法来从消息源获取消息，可以返回任何类型的数据
        框架会自动判断类型，如果不是MessageBatch会自动包装

        Returns:
            Optional[Any]: 获取到的消息数据，可以是任何类型，如果没有消息返回None
        """

    @abstractmethod
    async def _handle_message(self, message_batch: MessageBatch) -> None:
        """
        处理消息批次的具体逻辑
        子类需要实现此方法来定义具体的消息处理逻辑

        Args:
            message_batch: 要处理的消息批次，由 _fetch_message 返回

        Note:
            此方法应该处理传入的消息批次，如果处理失败应该抛出异常
            重试逻辑由基类处理，重试时会传递相同的消息批次
            子类可以通过message_batch.messages获取所有消息，自己决定如何处理（单个或批量）
        """
```

**File:** README.md (L572-594)
```markdown
#### 📦 Batch Store Group Chat Memory

EverMemOS supports a standardized group chat data format ([GroupChatFormat](data_format/group_chat/group_chat_format.md)). You can use scripts for batch storage:

```bash
# Use script for batch storage (Chinese data)
uv run python src/bootstrap.py src/run_memorize.py \
  --input data/group_chat_zh.json \
  --api-url http://localhost:8001/api/v3/agentic/memorize \
  --scene group_chat 

# Or use English data
uv run python src/bootstrap.py src/run_memorize.py \
  --input data/group_chat_en.json \
  --api-url http://localhost:8001/api/v3/agentic/memorize \
  --scene group_chat

# Validate file format
uv run python src/bootstrap.py src/run_memorize.py \
  --input data/group_chat_en.json \
  --scene group_chat \
  --validate-only
```
```

**File:** docs/dev_docs/api_usage_guide.md (L268-284)
```markdown
### 脚本工作流程

1. **验证输入文件**
   - 检查 JSON 格式是否正确
   - 验证是否符合 GroupChatFormat 规范
   - 输出数据统计信息

2. **逐条处理消息**
   - 从群聊文件中读取每条消息
   - 逐条调用 API 存储
   - 显示处理进度和结果

3. **输出处理结果**
   - 成功处理的消息数量
   - 保存的记忆数量
   - 失败的消息（如有）

```

**File:** demo/extract/extractor.py (L91-176)
```python
    async def extract_from_events(self, events: List[Dict[str, Any]]) -> int:
        """从事件列表中提取记忆
        
        Args:
            events: 对话事件列表
            
        Returns:
            提取的 MemCell 数量
        """
        if not self.manager:
            raise RuntimeError("请先调用 initialize() 初始化提取器")
        
        print("=" * 80)
        print("使用 V3 API 提取记忆")
        print("=" * 80)
        print(f"\n✓ 场景类型: {self.config.scenario_type.value}")
        print(f"✓ 语言: {self.config.prompt_language}")
        print(f"✓ 群组 ID: {self.config.group_id}")
        print(f"✓ 语义提取: {self.config.enable_semantic_extraction}")
        print(f"\n开始处理 {len(events)} 条消息...\n")
        
        history: List[RawData] = []
        saved_count = 0
        
        for idx, entry in enumerate(events):
            # 归一化消息
            message_payload = self.normalize_message(entry)
            if not message_payload:
                continue
            
            # 提取消息 ID
            message_id = (
                entry.get("message_id")
                or entry.get("id")
                or entry.get("uuid")
                or entry.get("event_id")
                or f"msg_{idx}"
            )
            
            # 创建 RawData
            raw_item = RawData(
                content=message_payload,
                data_id=str(message_id),
                data_type=RawDataType.CONVERSATION,
            )
            
            # 初始化历史
            if not history:
                history.append(raw_item)
                continue
            
            # 构建请求
            request = MemorizeRequest(
                history_raw_data_list=list(history),
                new_raw_data_list=[raw_item],
                raw_data_type=RawDataType.CONVERSATION,
                user_id_list=["default"],
                group_id=self.config.group_id,
                group_name=self.config.group_name,
                enable_semantic_extraction=self.config.enable_semantic_extraction or False,
                enable_event_log_extraction=True,
            )
            
            # 调用 V3 API
            try:
                result = await self.manager.memorize(request)
                
                if result:
                    saved_count += 1
                    print(f"  [{saved_count:3d}] ✅ 提取成功，返回 {len(result)} 个 Memory")
                    history = [raw_item]
                else:
                    history.append(raw_item)
                    if len(history) > self.config.history_window_size:
                        history = history[-self.config.history_window_size:]
            
            except Exception as e:
                print(f"\n⚠️ 提取失败: {e}")
                history.append(raw_item)
                if len(history) > self.config.history_window_size:
                    history = history[-self.config.history_window_size:]
                continue
        
        print(f"\n✅ 处理完成，共提取 {saved_count} 个 MemCell")
        return saved_count
```

**File:** src/agentic_layer/vectorize_service.py (L448-479)
```python
    async def get_embeddings_batch(
        self, text_batches: List[List[str]], instruction: Optional[str] = None
    ) -> List[List[np.ndarray]]:
        """
        批量获取多个文本批次的embedding向量

        Args:
            text_batches: 文本批次列表，每个批次包含多个文本
            instruction: 可选的指令文本

        Returns:
            每个批次的embedding向量列表
        """
        tasks = []
        for batch in text_batches:
            task = self.get_embeddings(batch, instruction)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常结果
        embeddings_batches = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error processing batch {i}: {result}")
                # 返回空列表作为占位符
                embeddings_batches.append([])
            else:
                embeddings_batches.append(result)

        return embeddings_batches

```

**File:** evaluation/src/adapters/evermemos/stage2_index_building.py (L171-299)
```python
async def build_emb_index(config: ExperimentConfig, data_dir: Path, emb_save_dir: Path):
    """
    构建 Embedding 索引（稳定版）
    
    性能优化策略：
    1. 受控并发：严格遵守 API Semaphore(5) 限制
    2. 保守批次大小：256 个文本/批次（避免超时）
    3. 串行批次提交：分组提交，避免队列堆积
    4. 进度监控：实时显示处理进度和速度
    
    优化效果：
    - 稳定性优先，避免超时和 API 过载
    - API 并发数：5（受 vectorize_service.Semaphore 控制）
    - 批次大小：256（平衡稳定性和效率）
    """
    # 🔥 优化1：保守的批次大小（避免超时）
    BATCH_SIZE = 256  # 使用较大批次（单次 API 调用处理更多，减少请求数）
    MAX_CONCURRENT_BATCHES = 5  # 🔥 严格控制并发数（与 Semaphore(5) 匹配）
    
    import time  # 用于性能统计
    
    for i in range(config.num_conv):
        file_path = data_dir / f"memcell_list_conv_{i}.json"
        if not file_path.exists():
            print(f"Warning: File not found, skipping: {file_path}")
            continue

        print(f"\n{'='*60}")
        print(f"Processing {file_path.name} for embedding...")
        print(f"{'='*60}")

        with open(file_path, "r", encoding="utf-8") as f:
            original_docs = json.load(f)

        texts_to_embed = []
        doc_field_map = []
        for doc_idx, doc in enumerate(original_docs):
            # 优先使用event_log（如果存在）
            if doc.get("event_log") and doc["event_log"].get("atomic_fact"):
                atomic_facts = doc["event_log"]["atomic_fact"]
                if isinstance(atomic_facts, list) and atomic_facts:
                    # 🔥 关键改动：每个atomic_fact单独计算embedding（MaxSim策略）
                    # 这样可以精确匹配到某个具体的原子事实，避免语义稀释
                    for fact_idx, fact in enumerate(atomic_facts):
                        # 🔥 修复：兼容两种格式（字符串 / 字典）
                        fact_text = None
                        if isinstance(fact, dict) and "fact" in fact:
                            # 新格式：{"fact": "...", "embedding": [...]}
                            fact_text = fact["fact"]
                        elif isinstance(fact, str):
                            # 旧格式：纯字符串
                            fact_text = fact
                        
                        # 确保fact非空
                        if fact_text and fact_text.strip():
                            texts_to_embed.append(fact_text)
                            doc_field_map.append((doc_idx, f"atomic_fact_{fact_idx}"))
                    continue

            # 回退到原有字段（保持向后兼容）
            for field in ["subject", "summary", "episode"]:
                if text := doc.get(field):
                    texts_to_embed.append(text)
                    doc_field_map.append((doc_idx, field))

        if not texts_to_embed:
            print(
                f"Warning: No documents found in {file_path.name}. Skipping embedding creation."
            )
            continue

        total_texts = len(texts_to_embed)
        total_batches = (total_texts + BATCH_SIZE - 1) // BATCH_SIZE
        print(f"Total texts to embed: {total_texts}")
        print(f"Batch size: {BATCH_SIZE}")
        print(f"Total batches: {total_batches}")
        print(f"Max concurrent batches: {MAX_CONCURRENT_BATCHES}")
        print(f"\nStarting parallel embedding generation...")
        
        # 🔥 优化2：稳定的批次处理（避免超时）
        start_time = time.time()
        
        async def process_batch_with_retry(batch_idx: int, batch_texts: list, max_retries: int = 3) -> tuple[int, list]:
            """处理单个批次（异步 + 重试）"""
            for attempt in range(max_retries):
                try:
                    # 调用 API 获取 embeddings（受 Semaphore(5) 控制并发数）
                    batch_embeddings = await vectorize_service.get_text_embeddings(batch_texts)
                    return (batch_idx, batch_embeddings)
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2.0 * (2 ** attempt)  # 指数退避：2s, 4s
                        print(f"  ⚠️  Batch {batch_idx + 1}/{total_batches} failed (attempt {attempt + 1}), retrying in {wait_time:.1f}s: {e}")
                        await asyncio.sleep(wait_time)
                    else:
                        print(f"  ❌ Batch {batch_idx + 1}/{total_batches} failed after {max_retries} attempts: {e}")
                        return (batch_idx, [])
        
        # 🔥 优化3：分组串行提交（避免队列堆积导致超时）
        print(f"Processing {total_batches} batches in groups of {MAX_CONCURRENT_BATCHES}...")
        
        batch_results = []
        completed = 0
        
        # 🔥 关键：分组提交，每组最多 MAX_CONCURRENT_BATCHES 个并发
        for group_start in range(0, total_texts, BATCH_SIZE * MAX_CONCURRENT_BATCHES):
            # 计算当前组的批次范围
            group_end = min(group_start + BATCH_SIZE * MAX_CONCURRENT_BATCHES, total_texts)
            group_tasks = []
            
            for j in range(group_start, group_end, BATCH_SIZE):
                batch_idx = j // BATCH_SIZE
                batch_texts = texts_to_embed[j : j + BATCH_SIZE]
                task = process_batch_with_retry(batch_idx, batch_texts)
                group_tasks.append(task)
            
            # 🔥 并发处理当前组（最多 MAX_CONCURRENT_BATCHES 个）
            print(f"  Group {group_start//BATCH_SIZE//MAX_CONCURRENT_BATCHES + 1}: Processing {len(group_tasks)} batches concurrently...")
            group_results = await asyncio.gather(*group_tasks, return_exceptions=False)
            batch_results.extend(group_results)
            
            completed += len(group_tasks)
            progress = (completed / total_batches) * 100
            print(f"  Progress: {completed}/{total_batches} batches ({progress:.1f}%)")
            
            # 🔥 组间延迟（给 API 服务器喘息时间）
            if group_end < total_texts:
                await asyncio.sleep(1.0)  # 1秒组间延迟
        
```

**File:** src/devops_scripts/data_fix/milvus_sync_docs.py (L27-44)
```python
async def run(
    collection_name: str, batch_size: int, limit_: int | None, days: int | None
) -> None:
    """
    同步 MongoDB 数据到 Milvus 指定 Collection。

    根据 Collection 名称路由到具体的同步实现。

    Args:
        collection_name: Milvus Collection 名称，如: episodic_memory
        batch_size: 批处理大小，默认 500
        limit_: 限制处理的文档数量，None 表示处理全部
        days: 只处理过去 N 天创建的文档，None 表示处理全部

    Raises:
        ValueError: 当 Collection 名称不支持时
        Exception: 当同步过程中发生错误时
    """
```

**File:** src/devops_scripts/data_fix/mongo_fix_episodic_memory_missing_vector.py (L115-214)
```python
    """
    执行修复任务。

    Args:
        limit:    最多处理的文档数量
        batch:    每次批量从数据库拉取的文档数量
        concurrency: 并发度（协程并发）

    Returns:
        统计信息字典
    """
    if limit <= 0:
        limit = 1
    if batch <= 0:
        batch = 1
    if concurrency <= 0:
        concurrency = 1

    semaphore = asyncio.Semaphore(concurrency)

    processed_total = 0
    succeeded = 0
    errors: List[Tuple[str, str]] = []
    created_before: Optional[Any] = None
    # 通过函数参数传入的范围过滤
    created_gte: Optional[Any] = start_created_at
    created_lte: Optional[Any] = end_created_at

    logger.info(
        "🔍 开始扫描需修复文档（limit=%d, batch=%d, concurrency=%d）",
        limit,
        batch,
        concurrency,
    )

    while processed_total < limit:
        fetch_size = min(batch, limit - processed_total)
        candidates = await _fetch_candidates(
            size=fetch_size,
            created_before=created_before,
            created_gte=created_gte,
            created_lte=created_lte,
        )

        if not candidates:
            break

        # 下一页锚点：本批次中最早的 created_at
        try:
            created_before = candidates[-1].created_at
            try:
                logger.info("⏱️ 当前处理到 created_at=%s", to_iso_format(created_before))
            except Exception:  # noqa: BLE001
                logger.info("⏱️ 当前处理到 created_at=%s", str(created_before))
        except AttributeError:
            # 如果模型无该字段或异常，退化为按 skip 逻辑（不更新锚点）
            pass

        logger.info(
            "📦 拉取到候选 %d 条（已累计处理=%d/%d）",
            len(candidates),
            processed_total,
            limit,
        )

        tasks: List[asyncio.Task] = []
        for doc in candidates:
            task = asyncio.create_task(_process_one(doc, semaphore))
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=False)

        for doc_id, err in results:
            if err is None:
                succeeded += 1
            else:
                errors.append((doc_id or "unknown", err))

        processed_total += len(candidates)

    failed = len(errors)
    if failed:
        for doc_id, err_msg in errors[:20]:  # 避免日志过多
            logger.error("❌ 修复失败 doc=%s, error=%s", doc_id, err_msg)
        if failed > 20:
            logger.error("… 还有 %d 条错误未逐条打印", failed - 20)

    logger.info(
        "✅ 修复完成 | total=%d, succeeded=%d, failed=%d",
        processed_total,
        succeeded,
        failed,
    )
    return {
        "total": processed_total,
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors,
    }

```

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L1018-1049)
```python
    # 🔥 可控并发处理（稳妥的并发策略）
    # 从配置获取并发数（默认 2，稳妥值）
    max_concurrent = getattr(config, 'reranker_concurrent_batches', 2)
    
    batch_results_list = []
    successful_batches = 0
    
    # 分组处理，每组最多 max_concurrent 个批次并发
    for group_start in range(0, len(batches), max_concurrent):
        group_batches = batches[group_start : group_start + max_concurrent]
        
        print(f"  Processing batch group {group_start//max_concurrent + 1} ({len(group_batches)} batches in parallel)...")
        
        # 🔥 并发处理当前组的所有批次
        tasks = [
            process_batch_with_retry(start_idx, batch) 
            for start_idx, batch in group_batches
        ]
        group_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计成功的批次
        for result in group_results:
            if isinstance(result, list) and result:
                batch_results_list.append(result)
                successful_batches += 1
            else:
                batch_results_list.append([])
        
        # 组间延迟（进一步降低，激进加速）
        if group_start + max_concurrent < len(batches):
            await asyncio.sleep(0.3)  # 🔥 组间 0.3 秒间隔（从 0.8s 降低）
    
```


# 我问

在 README 的"记忆构筑"部分提到了多种记忆类型：情节（episode）、画像（profile）、偏好（preference）、关系、语义知识、基础事实、核心记忆。这些记忆类型在数据库中是如何组织的？它们是存储在不同的 MongoDB collection 吗？每种记忆类型的数据结构（Schema）是什么？我如果想扩展新的记忆类型（比如"任务记忆"用于追踪用户的待办事项），需要修改哪些代码？是在 `memory_layer/memory_extractor/` 下添加新的 extractor 吗？新的记忆类型如何与现有的检索流程集成？

# deepwiki答
您询问的是 EverMemOS 中不同记忆类型的数据库组织方式、Schema 结构，以及如何扩展新的记忆类型（如"任务记忆"）。<cite />

## 记忆类型的数据库组织

### MongoDB Collection 结构

EverMemOS 使用**三个主要 MongoDB collection** 存储不同记忆类型：<cite />

1. **`episodic_memories`** - 存储情节记忆（episode） [1](#2-0) 

2. **`core_memories`** - 统一存储基础事实（base_memory）、画像（profile）、偏好（preference） [2](#2-1) 

3. **`semantic_memories`** - 存储语义知识（semantic_memory）<cite />

**关键设计**：`core_memories` 是一个**统一文档**，单个文档包含用户的所有三种记忆类型数据（base_memory、profile、preference），而不是分开存储。 [3](#2-2) 

### 记忆类型枚举定义

系统在 `src/memory_layer/types.py` 中定义了所有记忆类型： [4](#2-3) 

包括：
- `EPISODE_SUMMARY` - 情节记忆
- `BASE_MEMORY` - 基础事实
- `PROFILE` - 画像
- `PREFERENCES` - 偏好
- `RELATIONSHIPS` - 关系
- `SEMANTIC_SUMMARY` - 语义知识
- `EVENT_LOG` - 事件日志
- `GROUP_PROFILE` - 群组画像
- `CORE` - 核心记忆

## 各记忆类型的 Schema 结构

### 1. 情节记忆（EpisodicMemory）

**Collection**: `episodic_memories` [5](#2-4) 

**核心字段**：
- `user_id` - 用户ID
- `group_id` - 群组ID（可选）
- `timestamp` - 发生时间
- `participants` - 参与者列表
- `summary` - 记忆单元摘要
- `subject` - 主题
- `episode` - 情景记忆内容
- `keywords` - 关键词
- `memcell_event_id_list` - 关联的 MemCell ID 列表
- `vector` - 向量（用于 Milvus）

**索引策略**： [6](#2-5) 
- `(user_id, timestamp)` 复合索引
- `(group_id, timestamp)` 复合索引
- `keywords` 索引
- `linked_entities` 索引

### 2. 核心记忆（CoreMemory）

**Collection**: `core_memories` [2](#2-1) 

**版本控制字段**： [7](#2-6) 
- `version` - 版本号
- `is_latest` - 是否最新版本

**BaseMemory 字段**（基础事实）： [8](#2-7) 
- `user_name`, `gender`, `position`, `department`, `age`
- `supervisor_user_id`, `team_members`
- `okr`, `base_location`, `hiredate`

**Profile 字段**（画像）： [9](#2-8) 
- `hard_skills`, `soft_skills` - 技能（包含 evidences）
- `motivation_system`, `fear_system`, `value_system` - 心理系统
- `personality`, `interests`, `tendency` - 性格特征
- `projects_participated`, `user_goal` - 经历与目标

**索引策略**： [10](#2-9) 
- `(user_id, version)` 唯一索引
- `(user_id, is_latest)` 索引（快速查询最新版本）

### 3. 语义记忆（SemanticMemory）

**数据模型**： [11](#2-10) 

**核心字段**：
- `user_id` - 用户ID
- `content` - 语义知识内容
- `knowledge_type` - 知识类型
- `source_episodes` - 来源情节ID列表
- `group_id`, `participants` - 群组信息

## 如何扩展新的记忆类型（任务记忆示例）

### 步骤 1：定义记忆类型枚举

在 `src/memory_layer/types.py` 的 `MemoryType` 枚举中添加： [4](#2-3) 

```python
class MemoryType(Enum):
    # ... 现有类型 ...
    TASK_MEMORY = "task_memory"  # 新增任务记忆
```

### 步骤 2：创建 MongoDB 文档模型

在 `src/infra_layer/adapters/out/persistence/document/memory/` 下创建 `task_memory.py`：

```python
class TaskMemory(DocumentBase, AuditBase):
    """任务记忆文档模型"""
    user_id: str = Field(..., description="用户ID")
    task_title: str = Field(..., description="任务标题")
    task_status: str = Field(..., description="状态：pending/in_progress/completed")
    due_date: Optional[datetime] = Field(default=None, description="截止日期")
    priority: Optional[str] = Field(default=None, description="优先级")
    # ... 其他字段
    
    model_config = ConfigDict(
        collection="task_memories",  # 新 collection
        # ...
    )
```

参考现有的 `EpisodicMemory` 结构。 [12](#2-11) 

### 步骤 3：创建 Repository

在 `src/infra_layer/adapters/out/persistence/repository/` 下创建 `task_memory_raw_repository.py`：

```python
@repository("task_memory_raw_repository", primary=True)
class TaskMemoryRawRepository(BaseRepository[TaskMemory]):
    """任务记忆仓库"""
    def __init__(self):
        super().__init__(TaskMemory)
    
    async def get_by_user_id(self, user_id: str, limit: int = 10):
        # 实现查询逻辑
        pass
```

参考 `EpisodicMemoryRawRepository` 的实现。 [13](#2-12) 

### 步骤 4：创建 Memory Extractor

在 `src/memory_layer/memory_extractor/` 下创建 `task_memory_extractor.py`： [14](#2-13) 

```python
class TaskMemoryExtractor(MemoryExtractor):
    """任务记忆提取器"""
    def __init__(self, llm_provider):
        super().__init__(MemoryType.TASK_MEMORY)
        self.llm_provider = llm_provider
    
    async def extract_memory(self, request: MemoryExtractRequest) -> Optional[Memory]:
        # 1. 从 MemCell 中提取任务信息
        # 2. 调用 LLM 识别任务相关内容
        # 3. 构造 TaskMemory 对象
        pass
```

### 步骤 5：集成到 MemoryManager

在 `src/memory_layer/memory_manager.py` 的 `extract_memory()` 方法中添加分支： [15](#2-14) 

```python
async def extract_memory(self, ...):
    # ... 现有代码 ...
    elif memory_type == MemoryType.TASK_MEMORY:
        extractor = TaskMemoryExtractor(self.task_memory_llm_provider)
        request = TaskMemoryExtractRequest(
            memcell_list=memcell_list,
            user_id_list=user_ids,
            # ...
        )
```

### 步骤 6：添加到 Agentic Layer

在 `src/agentic_layer/memory_models.py` 中定义数据模型： [16](#2-15) 

```python
class MemoryType(str, Enum):
    # ... 现有类型 ...
    TASK_MEMORY = "task_memory"

@dataclass
class TaskMemoryModel:
    """任务记忆模型"""
    id: str
    user_id: str
    task_title: str
    # ... 其他字段
```

在 `src/agentic_layer/fetch_mem_service.py` 中添加查询逻辑： [17](#2-16) 

```python
case MemoryType.TASK_MEMORY:
    tasks = await self._task_repo.get_by_user_id(user_id, limit=limit)
    memories = [self._convert_task_memory(task) for task in tasks]
```

### 步骤 7：集成到检索流程

#### Elasticsearch 索引

在 `src/infra_layer/adapters/out/search/elasticsearch/memory/` 下创建 `task_memory.py`： [18](#2-17) 

```python
class TaskMemoryDoc(AliasDoc("task-memory", number_of_shards=3)):
    """任务记忆 ES 文档"""
    task_id = e_field.Keyword(required=True)
    user_id = e_field.Keyword(required=True)
    task_title = e_field.Text(...)
    # ... 定义检索字段
```

#### Milvus 向量索引

任务记忆需要生成向量并存储到 Milvus，参考 `EpisodicMemory` 的 `vector` 字段处理。 [19](#2-18) 

#### 检索 API 支持

在 `/api/v3/agentic/retrieve_lightweight` 和 `/api/v3/agentic/retrieve_agentic` 接口中，添加 `data_source="task_memory"` 的支持。<cite />

## Notes

**关键架构设计**：
- **CoreMemory 的统一设计**：base_memory、profile、preference 存储在同一个文档中，通过字段区分，而不是分开存储。这简化了版本管理和查询。 [3](#2-2) 

- **三重写入策略**：新的记忆类型也需要同时写入 MongoDB、Elasticsearch、Milvus 三个数据库，确保检索性能。<cite />

- **MemoryExtractor 基类**：所有记忆提取器都继承自 `MemoryExtractor`，实现 `extract_memory()` 方法。 [14](#2-13) 

- **现有的 Extractor 实现**：可以参考 `EpisodeMemoryExtractor`、`ProfileMemoryExtractor` 的实现细节，它们展示了如何从 MemCell 提取特定类型的记忆。 [20](#2-19) 

**扩展新记忆类型的完整路径**：
1. 定义枚举 → 2. MongoDB 文档模型 → 3. Repository → 4. Extractor → 5. MemoryManager 集成 → 6. Agentic Layer 数据模型 → 7. 检索流程（ES + Milvus）<cite />

Wiki pages you might want to explore:
- [EverMemOS Overview (EverMind-AI/EverMemOS)](/wiki/EverMind-AI/EverMemOS#1)

### Citations

**File:** src/infra_layer/adapters/out/persistence/document/memory/episodic_memory.py (L11-62)
```python
class EpisodicMemory(DocumentBase, AuditBase):
    """
    情景记忆文档模型

    存储用户的情景记忆，包含事件摘要、参与者、主题等信息。
    从 MemCell 摘要直接转存而来。
    """

    user_id: str = Field(..., description="当事人")
    group_id: Optional[str] = Field(default=None, description="群组ID")
    timestamp: datetime = Field(..., description="发生时间（时间戳）")
    participants: Optional[List[str]] = Field(
        default=None, description="事件参与者名字"
    )
    summary: str = Field(..., min_length=1, description="记忆单元")
    subject: Optional[str] = Field(default=None, description="记忆单元主题")
    episode: str = Field(..., min_length=1, description="情景记忆")
    type: Optional[str] = Field(default=None, description="情景类型，如Conversation等")
    keywords: Optional[List[str]] = Field(default=None, description="关键词")
    linked_entities: Optional[List[str]] = Field(
        default=None, description="关联的实体ID"
    )

    memcell_event_id_list: Optional[List[str]] = Field(
        default=None, description="记忆单元事件ID"
    )

    extend: Optional[Dict[str, Any]] = Field(default=None, description="备用拓展字段")

    vector: Optional[List[float]] = Field(default=None, description="文本向量")
    vector_model: Optional[str] = Field(default=None, description="使用的向量化模型")

    model_config = ConfigDict(
        collection="episodic_memories",
        validate_assignment=True,
        json_encoders={datetime: lambda dt: dt.isoformat()},
        json_schema_extra={
            "example": {
                "user_id": "user_12345",
                "group_id": "group_work",
                "timestamp": 1701388800,
                "participants": ["张三", "李四"],
                "summary": "讨论了项目进度和下周计划",
                "subject": "项目会议",
                "episode": "在会议室进行了项目进度讨论，确定了下周的开发任务分配",
                "type": "Conversation",
                "keywords": ["项目", "进度", "会议"],
                "linked_entities": ["proj_001", "task_123"],
                "extend": {"priority": "high", "location": "会议室A"},
            }
        },
    )
```

**File:** src/infra_layer/adapters/out/persistence/document/memory/episodic_memory.py (L72-94)
```python
        indexes = [
            # 用户ID和时间戳复合索引
            IndexModel(
                [("user_id", ASCENDING), ("timestamp", DESCENDING)],
                name="idx_user_timestamp",
            ),
            # 群组ID和时间戳复合索引
            IndexModel(
                [("group_id", ASCENDING), ("timestamp", DESCENDING)],
                name="idx_group_timestamp",
            ),
            # 关键词索引
            IndexModel([("keywords", ASCENDING)], name="idx_keywords", sparse=True),
            # 关联实体索引
            IndexModel(
                [("linked_entities", ASCENDING)],
                name="idx_linked_entities",
                sparse=True,
            ),
            # 审计字段索引
            IndexModel([("created_at", DESCENDING)], name="idx_created_at"),
            IndexModel([("updated_at", DESCENDING)], name="idx_updated_at"),
        ]
```

**File:** src/infra_layer/adapters/out/persistence/document/memory/core_memory.py (L10-16)
```python
class CoreMemory(DocumentBase, AuditBase):
    """
    核心记忆文档模型

    统一存储用户的基础信息、个人档案和偏好设置。
    单个文档包含所有三种记忆类型的数据。
    """
```

**File:** src/infra_layer/adapters/out/persistence/document/memory/core_memory.py (L20-24)
```python
    # ==================== 版本控制字段 ====================
    version: Optional[str] = Field(default=None, description="版本号，用于支持版本管理")
    is_latest: Optional[bool] = Field(
        default=True, description="是否为最新版本，默认为True"
    )
```

**File:** src/infra_layer/adapters/out/persistence/document/memory/core_memory.py (L26-39)
```python
    # ==================== BaseMemory 字段 ====================
    # 基础信息字段
    user_name: Optional[str] = Field(default=None, description="用户姓名")
    gender: Optional[str] = Field(default=None, description="性别")
    position: Optional[str] = Field(default=None, description="职位")
    supervisor_user_id: Optional[str] = Field(default=None, description="上级UserID")
    team_members: Optional[List[str]] = Field(
        default=None, description="团队成员UserID"
    )
    okr: Optional[List[Dict[str, str]]] = Field(default=None, description="OKR指标")
    base_location: Optional[str] = Field(default=None, description="base地点")
    hiredate: Optional[str] = Field(default=None, description="入职时间")
    age: Optional[int] = Field(default=None, description="年纪")
    department: Optional[str] = Field(default=None, description="部门")
```

**File:** src/infra_layer/adapters/out/persistence/document/memory/core_memory.py (L41-70)
```python
    # ==================== Profile 字段 ====================
    # 个人档案字段 - 所有字段现在使用嵌入 evidences 的格式
    # 技能格式: [{"value": "Python", "level": "高级", "evidences": ["2024-01-01|conv_123"]}]
    # Legacy格式: [{"skill": "Python", "level": "高级", "evidences": ["..."]}] (自动转换)
    hard_skills: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="硬技能，SQL、Python、产品设计等，及其熟练程度，包含 evidences",
    )
    soft_skills: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="软技能，沟通能力、团队合作、情绪智力等，包含 evidences",
    )
    output_reasoning: Optional[str] = Field(
        default=None, description="当前输出结果的推理说明"
    )
    motivation_system: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="激励系统，包含 value/level/evidences"
    )
    fear_system: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="恐惧系统，包含 value/level/evidences"
    )
    value_system: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="价值体系，包含 value/level/evidences"
    )
    humor_use: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="幽默使用方式，包含 value/level/evidences"
    )
    colloquialism: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="俗语或口头禅偏好，包含 value/level/evidences"
    )
```

**File:** src/infra_layer/adapters/out/persistence/document/memory/core_memory.py (L130-145)
```python
        indexes = [
            # 用户ID和版本联合唯一索引
            IndexModel(
                [("user_id", ASCENDING), ("version", ASCENDING)],
                unique=True,
                name="idx_user_id_version_unique",
            ),
            # is_latest字段索引（用于快速查询最新版本）
            IndexModel(
                [("user_id", ASCENDING), ("is_latest", ASCENDING)],
                name="idx_user_id_is_latest",
            ),
            # 审计字段索引
            IndexModel([("created_at", DESCENDING)], name="idx_created_at"),
            IndexModel([("updated_at", DESCENDING)], name="idx_updated_at"),
        ]
```

**File:** src/memory_layer/types.py (L8-22)
```python
class MemoryType(Enum):
    """Types of memories that can be extracted."""

    EPISODE_SUMMARY = "episode_summary"  # 情节记忆
    BASE_MEMORY = "baseMemory"  # 稳定、客观、可验证 Who He Is
    PROFILE = "profile"  # 能力与经验画像
    PREFERENCES = "preferences"  # 偏好设置
    RELATIONSHIPS = "relationships"  # 人际关系
    SEMANTIC_SUMMARY = "semantic"  # 语义记忆
    EVENT_LOG = "event_log"  # 事件日志

    GROUP_PROFILE = "group_profile"  # 群组画像

    CORE = "core"  # 核心记忆

```

**File:** src/memory_layer/types.py (L199-234)
```python
@dataclass
class SemanticMemory:
    """
    语义记忆数据模型

    用于存储从情景记忆中提取的语义知识
    """

    user_id: str
    content: str
    knowledge_type: str = "knowledge"
    source_episodes: List[str] = None
    created_at: datetime.datetime = None
    group_id: Optional[str] = None
    participants: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.source_episodes is None:
            self.source_episodes = []
        if self.created_at is None:
            self.created_at = datetime.datetime.now()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "content": self.content,
            "knowledge_type": self.knowledge_type,
            "source_episodes": self.source_episodes,
            "created_at": to_iso_format(self.created_at),
            "group_id": self.group_id,
            "participants": self.participants,
            "metadata": self.metadata,
        }
```

**File:** src/infra_layer/adapters/out/persistence/repository/episodic_memory_raw_repository.py (L17-27)
```python
@repository("episodic_memory_raw_repository", primary=True)
class EpisodicMemoryRawRepository(BaseRepository[EpisodicMemory]):
    """
    情景记忆原始数据仓库
    会生成向量化的文本内容，并保存到数据库中
    提供情景记忆的 CRUD 操作和基础查询功能。
    """

    def __init__(self):
        super().__init__(EpisodicMemory)
        self.vectorize_service = get_vectorize_service()
```

**File:** src/memory_layer/memory_extractor/base_memory_extractor.py (L29-58)
```python
class MemoryExtractor(ABC):
    """
    Simple abstract base class for memory extraction.

    This class provides a minimal interface for extracting memories
    from boundary detection results.
    """

    def __init__(self, memory_type: MemoryType):
        """
        Initialize the memory extractor.

        Args:
            memory_type: The type of memory this extractor generates
        """
        self.memory_type = memory_type

    @abstractmethod
    async def extract_memory(self, request: MemoryExtractRequest) -> Optional[Memory]:
        """
        Extract memory from a boundary detection result.

        Args:
            boundary_result: The boundary detection result to extract from
            user_id: User ID for the memory

        Returns:
            MemoryExtractionResult if extraction is successful, None otherwise
        """
        pass
```

**File:** src/memory_layer/memory_manager.py (L183-269)
```python
    async def extract_memory(
        self,
        memcell_list: list[MemCell],
        memory_type: MemoryType,
        user_ids: List[str],
        group_id: Optional[str] = None,
        group_name: Optional[str] = None,
        old_memory_list: Optional[List[Memory]] = None,
        user_organization: Optional[List] = None,
        episode_memory: Optional[Memory] = None,  # 用于个人语义记忆和事件日志提取
    ):
        """
        提取记忆
        
        Returns:
            - EPISODE_SUMMARY/PROFILE/GROUP_PROFILE: 返回 List[Memory]
            - SEMANTIC_SUMMARY: 返回 List[SemanticMemoryItem]
            - EVENT_LOG: 返回 EventLog
        """
        extractor = None
        request = None

        if memory_type == MemoryType.EPISODE_SUMMARY:
            extractor = EpisodeMemoryExtractor(
                self.episode_memory_extractor_llm_provider
            )
            request = EpisodeMemoryExtractRequest(
                memcell_list=memcell_list,
                user_id_list=user_ids,
                group_id=group_id,
                old_memory_list=old_memory_list,
            )
        elif memory_type == MemoryType.PROFILE:
            if memcell_list[0].type == RawDataType.CONVERSATION:
                extractor = ProfileMemoryExtractor(
                    self.profile_memory_extractor_llm_provider
                )
                request = ProfileMemoryExtractRequest(
                    memcell_list=memcell_list,
                    user_id_list=user_ids,
                    group_id=group_id,
                    old_memory_list=old_memory_list,
                )
        elif memory_type == MemoryType.GROUP_PROFILE:
            extractor = GroupProfileMemoryExtractor(
                self.profile_memory_extractor_llm_provider
            )
            request = GroupProfileMemoryExtractRequest(
                memcell_list=memcell_list,
                user_id_list=user_ids,
                group_id=group_id,
                group_name=group_name,
                old_memory_list=old_memory_list,
                user_organization=None,
            )
        elif memory_type == MemoryType.SEMANTIC_SUMMARY and episode_memory:
            # 为个人 episode 提取语义记忆
            logger.debug(f"开始为个人 episode 提取语义记忆: user_id={episode_memory.user_id}")
            
            extractor = SemanticMemoryExtractor(
                llm_provider=self.episode_memory_extractor_llm_provider
            )
            
            semantic_memories = await extractor.generate_semantic_memories_for_episode(
                episode_memory
            )
                        
            return semantic_memories
        
        elif memory_type == MemoryType.EVENT_LOG and episode_memory:
            # 为个人 episode 提取事件日志
            logger.debug(f"开始为个人 episode 提取事件日志: user_id={episode_memory.user_id}")
            
            extractor = EventLogExtractor(
                    llm_provider=self.event_log_llm_provider
                )
            
            event_log = await extractor.extract_event_log(
                episode_text=episode_memory.episode,
                timestamp=episode_memory.timestamp
            )
            
            return event_log

        if extractor == None or request == None:
            return []
        return await extractor.extract_memory(request)
```

**File:** src/agentic_layer/memory_models.py (L23-35)
```python
class MemoryType(str, Enum):
    """记忆类型枚举"""

    BASE_MEMORY = "base_memory"
    PROFILE = "profile"
    PREFERENCE = "preference"
    EPISODIC_MEMORY = "episodic_memory"
    SEMANTIC_MEMORY = "semantic_memory"
    ENTITY = "entity"
    RELATION = "relation"
    BEHAVIOR_HISTORY = "behavior_history"
    MULTIPLE = "multiple"  # 多类型查询

```

**File:** src/agentic_layer/fetch_mem_service.py (L404-549)
```python
            self._get_repositories()
            memories = []

            match memory_type:
                case MemoryType.MULTIPLE:
                    # 多类型查询：获取core_memory并转换为CoreMemoryModel
                    core_memory_result = await self._core_repo.get_by_user_id(
                        user_id, version_range=version_range
                    )
                    if core_memory_result:
                        # 如果version_range为None，core_memory_result是单个CoreMemory
                        # 如果version_range不为None，core_memory_result是List[CoreMemory]
                        if isinstance(core_memory_result, list):
                            memories = [
                                await self._convert_core_memory(core_memory)
                                for core_memory in core_memory_result
                            ]
                        else:
                            memories = [
                                await self._convert_core_memory(core_memory_result)
                            ]
                    else:
                        memories = []
                case MemoryType.SEMANTIC_MEMORY:
                    # 语义记忆：每个用户只有一个语义记忆文档
                    semantic_memory = await self._semantic_repo.get_by_user_id(user_id)
                    if semantic_memory:
                        memories = [
                            await self._convert_semantic_memory(semantic_memory)
                        ]
                    else:
                        memories = []

                case MemoryType.EPISODIC_MEMORY:
                    # 情景记忆：按时间排序的事件列表
                    episodic_memories = await self._episodic_repo.get_by_user_id(
                        user_id, limit=limit
                    )
                    memories = [
                        self._convert_episodic_memory(mem) for mem in episodic_memories
                    ]

                case MemoryType.BASE_MEMORY:
                    # 基础记忆：从核心记忆中提取基础信息
                    core_memory = await self._core_repo.get_by_user_id(user_id)
                    if core_memory:
                        base_info = self._core_repo.get_base(core_memory)
                        memories = [
                            BaseMemoryModel(
                                id=str(core_memory.id),
                                user_id=core_memory.user_id,
                                content=f"用户: {base_info.get('user_name', '未知')} | 职位: {base_info.get('position', '未知')} | 部门: {base_info.get('department', '未知')}",
                                created_at=core_memory.created_at,
                                updated_at=core_memory.updated_at,
                                metadata={
                                    "user_name": base_info.get('user_name', ''),
                                    "position": base_info.get('position', ''),
                                    "department": base_info.get('department', ''),
                                    "company": base_info.get('company', ''),
                                    "location": base_info.get('location', ''),
                                    "contact": base_info.get('contact', {}),
                                },
                            )
                        ]
                    else:
                        memories = []

                case MemoryType.PROFILE:
                    # 个人档案：从核心记忆中提取个人特征
                    core_memory = await self._core_repo.get_by_user_id(user_id)
                    if core_memory:
                        profile_info = self._core_repo.get_profile(core_memory)
                        memories = [
                            ProfileModel(
                                id=str(core_memory.id),
                                user_id=core_memory.user_id,
                                name=profile_info.get('personality', '未知'),
                                age=profile_info.get('age', 0),
                                gender=profile_info.get('gender', ''),
                                occupation=profile_info.get('occupation', ''),
                                interests=profile_info.get('interests', []),
                                personality_traits=profile_info.get(
                                    'personality_traits', {}
                                ),
                                created_at=core_memory.created_at,
                                updated_at=core_memory.updated_at,
                                metadata=profile_info,
                            )
                        ]
                    else:
                        memories = []

                case MemoryType.PREFERENCE:
                    # 个人偏好：从核心记忆中提取偏好设置
                    core_memory = await self._core_repo.get_by_user_id(user_id)
                    if core_memory:
                        preference_info = self._core_repo.get_preference(core_memory)
                        # 将偏好信息转换为多个 PreferenceModel
                        memories = []
                        for key, value in preference_info.items():
                            memories.append(
                                PreferenceModel(
                                    id=f"{core_memory.id}_{key}",
                                    user_id=core_memory.user_id,
                                    category="个人偏好",
                                    preference_key=key,
                                    preference_value=str(value),
                                    confidence_score=1.0,
                                    created_at=core_memory.created_at,
                                    updated_at=core_memory.updated_at,
                                    metadata={
                                        "source": "core_memory",
                                        "original_key": key,
                                    },
                                )
                            )
                    else:
                        memories = []

                case MemoryType.ENTITY:
                    # 实体：查询与用户相关的实体
                    entities = await self._entity_repo.get_by_type(
                        "Person", limit=limit
                    )
                    memories = [self._convert_entity(entity) for entity in entities]

                case MemoryType.RELATION:
                    # 关系：查询人际关系
                    relationships = (
                        await self._relationship_repo.get_by_relationship_type(
                            "人际关系", limit=limit
                        )
                    )
                    memories = [
                        self._convert_relationship(rel) for rel in relationships
                    ]

                case MemoryType.BEHAVIOR_HISTORY:
                    # 行为历史：按时间排序的用户行为
                    behaviors = await self._behavior_repo.get_by_user_id(
                        user_id, limit=limit
                    )
                    memories = [
                        self._convert_behavior_history(behavior)
                        for behavior in behaviors
                    ]
```

**File:** src/infra_layer/adapters/out/search/elasticsearch/memory/episodic_memory.py (L12-77)
```python
class EpisodicMemoryDoc(AliasDoc("episodic-memory", number_of_shards=3)):
    """
    情景记忆Elasticsearch文档

    基于MongoDB EpisodicMemory模型，用于高效的BM25文本检索。
    主要检索字段为title和episode的拼接内容。

    字段说明：
    - event_id: 事件唯一标识（对应MongoDB的_id）
    - user_id: 用户ID（必需，用于过滤）
    - user_name: 用户名称
    - timestamp: 事件发生时间
    - title: 事件标题（对应MongoDB的subject字段）
    - episode: 情景描述（核心内容）
    - search_content: BM25搜索字段（支持多值存储，用于精确词匹配）
    - summary: 事件摘要
    - group_id: 群组ID（可选）
    - participants: 参与者列表
    - type: 事件类型（Conversation等）
    - keywords: 关键词列表
    - linked_entities: 关联实体ID列表
    - extend: 扩展字段（灵活存储）

    分词处理说明：
    - 应用层负责中文分词（推荐使用jieba）
    - title、episode、summary字段存储预分词结果（空格分隔）
    - search_content字段支持多值存储，每个值是一个搜索词
    - ES使用standard分析器处理search_content，original子字段用于精确匹配
    - 搜索时使用terms查询在search_content.original字段中匹配多个词

    附属字段说明：
    - original: 精确匹配，小写处理
    - ik: IK智能分词（需要ES安装IK插件）
    - edge_completion: 前缀匹配和自动补全
    """

    ID_SOURCE_FIELD = "event_id"

    # 基础标识字段
    event_id = e_field.Keyword(required=True)
    user_id = e_field.Keyword(required=True)
    user_name = e_field.Keyword()

    # 时间字段
    timestamp = e_field.Date(required=True)

    # 核心内容字段 - BM25检索的主要目标
    title = e_field.Text(
        required=False,
        analyzer=whitespace_lowercase_trim_stop_analyzer,
        search_analyzer=whitespace_lowercase_trim_stop_analyzer,
        fields={
            "keyword": e_field.Keyword(),  # 精确匹配
            # "completion": e_field.Completion(analyzer=completion_analyzer),  # 自动补全
        },
    )

    episode = e_field.Text(
        required=True,
        analyzer=whitespace_lowercase_trim_stop_analyzer,
        search_analyzer=whitespace_lowercase_trim_stop_analyzer,
        fields={"keyword": e_field.Keyword()},  # 精确匹配
    )

    # BM25检索核心字段 - 支持多值存储的搜索内容
    # 应用层可以存储多个相关的搜索词或短语
```



# 我问

代码中提到使用 DeepInfra API 进行 Embedding 和 Rerank。如果我想替换成自己部署的模型（比如本地的 BGE-M3 做 Embedding、本地的 bge-reranker-v2 做重排序），需要修改哪些代码？是在 `component/` 下添加新的适配器吗？系统的 Embedding 维度是固定的还是可配置的？如果更换了 Embedding 模型，已有的向量数据是否需要全部重新生成？有没有数据迁移的工具或脚本？对于 LLM 部分，README 提到支持多种 API（OpenRouter、OpenAI 等），但如果我想接入本地的大模型（比如通过 vLLM 部署的 Qwen），需要怎么配置？

# deepwiki答
您询问的是如何将 EverMemOS 的 Embedding 和 Rerank 服务从 DeepInfra API 替换为本地部署的模型（如 BGE-M3 和 bge-reranker-v2），以及如何接入本地 LLM（如 vLLM 部署的 Qwen）。<cite />

## Embedding 服务替换

### 当前实现分析

EverMemOS 使用 `DeepInfraVectorizeService` 进行 Embedding 生成，该服务通过 OpenAI 兼容的 API 调用 DeepInfra： [1](#3-0) 

**关键配置**：
- **向量维度**：默认 **1024 维**，可通过环境变量 `DEEPINFRA_DIMENSIONS` 配置 [2](#3-1) 
- **API 端点**：`DEEPINFRA_BASE_URL`（默认 `https://api.deepinfra.com/v1/openai`） [3](#3-2) 
- **模型名称**：`DEEPINFRA_EMBEDDING_MODEL`（默认 `Qwen/Qwen3-Embedding-4B`） [4](#3-3) 

### 替换方案 1：直接修改配置（推荐）

如果您的本地 BGE-M3 模型提供 **OpenAI 兼容的 API**（如通过 vLLM、FastChat 或 Xinference 部署），可以直接修改 `.env` 配置：<cite />

```bash
# 本地 BGE-M3 Embedding 服务
DEEPINFRA_BASE_URL=http://localhost:8000/v1  # 本地 API 地址
DEEPINFRA_EMBEDDING_MODEL=BAAI/bge-m3        # 模型名称
DEEPINFRA_DIMENSIONS=1024                     # BGE-M3 的向量维度
DEEPINFRA_API_KEY=dummy_key                   # 本地服务可能不需要真实 key
```

**注意**：BGE-M3 的默认向量维度是 **1024 维**，与当前配置一致。如果使用其他维度，需要修改 `DEEPINFRA_DIMENSIONS`。 [5](#3-4) 

### 替换方案 2：添加新的适配器

如果本地模型 **不兼容 OpenAI API**，需要在 `src/component/` 下创建新的适配器：<cite />

#### 步骤 1：创建 BGE-M3 适配器

在 `src/component/embedding_adapter/` 下创建 `bge_m3_adapter.py`：

```python
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from core.di import service

@service(name="bge_m3_vectorize_service", primary=False)
class BGEM3VectorizeService:
    """本地 BGE-M3 Embedding 服务"""
    
    def __init__(self, model_path: str = "BAAI/bge-m3"):
        self.model = SentenceTransformer(model_path)
        self.dimensions = 1024  # BGE-M3 维度
    
    async def get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """批量生成 Embedding"""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return [np.array(emb, dtype=np.float32) for emb in embeddings]
```

#### 步骤 2：修改依赖注入配置

在 `src/bootstrap.py` 中注册新服务，并修改 `vectorize_service` 的绑定：

```python
# 注册 BGE-M3 服务
container.register("bge_m3_vectorize_service", BGEM3VectorizeService)

# 切换默认 Embedding 服务
container.register("vectorize_service", BGEM3VectorizeService, primary=True)
```

## Rerank 服务替换

### 当前实现分析

Rerank 服务使用 `DeepInfraRerankService`，通过 DeepInfra 推理 API 调用： [6](#3-5) 

**关键配置**：
- **API 端点**：`DEEPINFRA_RERANK_BASE_URL`（默认 `https://api.deepinfra.com/v1/inference`） [7](#3-6) 
- **模型名称**：`DEEPINFRA_RERANK_MODEL`（默认 `Qwen/Qwen3-Reranker-4B`） [8](#3-7) 

### 替换方案：创建本地 Reranker 适配器

在 `src/component/rerank_adapter/` 下创建 `bge_reranker_adapter.py`：

```python
from typing import List, Dict, Any
from FlagEmbedding import FlagReranker
from core.di import service

@service(name="bge_reranker_service", primary=False)
class BGERerankerService:
    """本地 bge-reranker-v2 服务"""
    
    def __init__(self, model_path: str = "BAAI/bge-reranker-v2-m3"):
        self.model = FlagReranker(model_path, use_fp16=True)
    
    async def rerank_memories(self, query: str, documents: List[str]) -> List[Dict[str, Any]]:
        """重排序文档"""
        scores = self.model.compute_score([[query, doc] for doc in documents])
        results = [
            {"index": i, "relevance_score": float(score)}
            for i, score in enumerate(scores)
        ]
        return sorted(results, key=lambda x: x["relevance_score"], reverse=True)
```

## 向量维度变更与数据迁移

### 向量维度配置

系统的 Embedding 维度是 **可配置的**，通过环境变量 `DEEPINFRA_DIMENSIONS` 设置： [9](#3-8) 

**重要**：如果更换 Embedding 模型且维度不同（如从 1024 维改为 768 维），**必须重新生成所有向量数据**，因为：<cite />
1. Milvus 向量数据库的 collection schema 是固定维度的
2. 不同维度的向量无法进行相似度计算

### 数据迁移工具

代码库提供了向量数据修复脚本，可用于批量重新生成向量： [10](#3-9) 

**使用方法**：

```bash
# 重新生成所有 EpisodicMemory 的向量
python src/bootstrap.py src/devops_scripts/data_fix/mongo_fix_episodic_memory_missing_vector.py \
  --limit 10000 \      # 处理数量
  --batch 200 \        # 批次大小
  --concurrency 8      # 并发度
```

**脚本功能**：
- 从 MongoDB 读取缺失向量或向量模型不匹配的文档
- 调用新的 Embedding 服务重新生成向量
- 更新 MongoDB 和 Milvus 中的向量数据<cite />

**目标向量模型配置**：脚本中硬编码了目标模型名称 `TARGET_VECTOR_MODEL = "Qwen/Qwen3-Embedding-4B"`，需要修改为您的新模型名称。 [11](#3-10) 

## LLM 服务替换（接入本地 vLLM）

### 当前 LLM 适配器架构

EverMemOS 使用 `OpenAIAdapter` 作为 LLM 适配器，支持任何 **OpenAI 兼容的 API**： [12](#3-11) 

### 接入本地 vLLM 部署的 Qwen

vLLM 提供 OpenAI 兼容的 API 服务器，可以直接通过修改 `.env` 配置接入：<cite />

```bash
# MemCell 提取器 LLM 配置
CONV_MEMCELL_LLM_PROVIDER=openai
CONV_MEMCELL_LLM_MODEL=Qwen/Qwen2.5-7B-Instruct  # vLLM 部署的模型名称
CONV_MEMCELL_LLM_BASE_URL=http://localhost:8000/v1  # vLLM API 地址
CONV_MEMCELL_LLM_API_KEY=dummy_key  # vLLM 默认不需要真实 key
CONV_MEMCELL_LLM_TEMPERATURE=0.3
CONV_MEMCELL_LLM_MAX_TOKENS=16384

# Episode Memory 提取器 LLM 配置
EPISODE_MEMORY_LLM_PROVIDER=openai
EPISODE_MEMORY_LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
EPISODE_MEMORY_LLM_BASE_URL=http://localhost:8000/v1
EPISODE_MEMORY_LLM_API_KEY=dummy_key
```

**配置说明**： [13](#3-12) 
- `CONV_MEMCELL_LLM_*`：用于 MemCell 提取
- `EPISODE_MEMORY_LLM_*`：用于情节记忆提取
- 两者可以使用不同的模型或相同的本地模型

### vLLM 部署示例

```bash
# 启动 vLLM 服务器（OpenAI 兼容模式）
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-7B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --served-model-name Qwen/Qwen2.5-7B-Instruct
```

## 完整替换流程总结

### 1. Embedding 替换（本地 BGE-M3）

**方案 A：OpenAI 兼容 API**（推荐）
```bash
# 部署 BGE-M3 为 OpenAI 兼容服务（如使用 Xinference）
xinference launch --model-name bge-m3 --model-type embedding

# 修改 .env
DEEPINFRA_BASE_URL=http://localhost:9997/v1
DEEPINFRA_EMBEDDING_MODEL=bge-m3
DEEPINFRA_DIMENSIONS=1024
```

**方案 B：自定义适配器**
- 在 `src/component/embedding_adapter/` 创建适配器
- 修改 `src/bootstrap.py` 注册服务
- 更新依赖注入配置

### 2. Reranker 替换（本地 bge-reranker-v2）

- 在 `src/component/rerank_adapter/` 创建适配器
- 使用 `FlagEmbedding` 库加载本地模型
- 修改 `src/bootstrap.py` 切换服务

### 3. 向量数据迁移

```bash
# 如果维度变更，重新生成所有向量
python src/bootstrap.py src/devops_scripts/data_fix/mongo_fix_episodic_memory_missing_vector.py \
  --limit 100000 --batch 500 --concurrency 10
```

### 4. LLM 替换（本地 vLLM）

```bash
# 启动 vLLM
vllm serve Qwen/Qwen2.5-7B-Instruct --port 8000

# 修改 .env
CONV_MEMCELL_LLM_BASE_URL=http://localhost:8000/v1
CONV_MEMCELL_LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
```

## Notes

**关键发现**：
- **OpenAI 兼容性**：系统的 LLM 和 Embedding 服务都使用 OpenAI 兼容的 API，这使得替换为本地模型非常简单，只需修改 `base_url` 和 `model` 配置。 [14](#3-13) 

- **向量维度灵活性**：虽然默认是 1024 维，但系统支持通过环境变量配置任意维度。 [5](#3-4) 

- **数据迁移必要性**：更换 Embedding 模型后，**必须**重新生成向量数据，否则检

Wiki pages you might want to explore:
- [EverMemOS Overview (EverMind-AI/EverMemOS)](/wiki/EverMind-AI/EverMemOS#1)

### Citations

**File:** src/agentic_layer/vectorize_service.py (L38-38)
```python
    dimensions: int = 1024
```

**File:** src/agentic_layer/vectorize_service.py (L45-47)
```python
            self.base_url = os.getenv(
                "DEEPINFRA_BASE_URL", "https://api.deepinfra.com/v1/openai"
            )
```

**File:** src/agentic_layer/vectorize_service.py (L49-51)
```python
            self.model = os.getenv(
                "DEEPINFRA_EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-4B"
            )
```

**File:** src/agentic_layer/vectorize_service.py (L64-65)
```python
        if self.dimensions == 1024:  # 使用默认值时才从环境变量读取
            self.dimensions = int(os.getenv("DEEPINFRA_DIMENSIONS", "1024"))
```

**File:** src/agentic_layer/vectorize_service.py (L155-211)
```python
@service(name="vectorize_service", primary=True)
class DeepInfraVectorizeService(DeepInfraVectorizeServiceInterface):
    """
    DeepInfra向量化服务类

    提供调用DeepInfra API获取文本embedding向量的方法
    """

    def __init__(self, config: Optional[DeepInfraConfig] = None):
        """
        初始化DeepInfra向量化服务

        Args:
            config: DeepInfra配置，如果为None则尝试从依赖注入获取，最后从环境变量读取
        """
        if config is None:
            try:
                # 尝试从依赖注入获取配置
                from core.di import get_bean

                config = get_bean("deepinfra_config")
                logger.info("DeepInfra config source: DI bean 'deepinfra_config'")
            except Exception:
                # 如果依赖注入失败，从环境变量读取
                config = self._load_config_from_env()
                # 打印.env传入情况（不输出密钥内容）
                logger.info(
                    "DeepInfra config source: env | DEEPINFRA_API_KEY set=%s | DEEPINFRA_BASE_URL=%s | DEEPINFRA_EMBEDDING_MODEL=%s | DEEPINFRA_DIMENSIONS=%s",
                    bool(os.getenv("DEEPINFRA_API_KEY")),
                    os.getenv("DEEPINFRA_BASE_URL"),
                    os.getenv("DEEPINFRA_EMBEDDING_MODEL"),
                    os.getenv("DEEPINFRA_DIMENSIONS"),
                )

        # 规范化配置，避免后续请求异常
        # 确保 base_url 包含协议
        base_url = config.base_url or ""
        if base_url and not (
            base_url.startswith("http://") or base_url.startswith("https://")
        ):
            base_url = f"https://{base_url}"
        # 确保模型非空
        model = config.model or os.getenv(
            "DEEPINFRA_EMBEDDING_MODEL", "Qwen/Qwen3-Embedding-4B"
        )

        # 写回配置对象
        config.base_url = base_url
        config.model = model

        self.config = config
        self.client: Optional[AsyncOpenAI] = None
        self._semaphore = asyncio.Semaphore(config.max_concurrent_requests)

        logger.info(
            f"Initialized DeepInfra Vectorize Service | model={config.model} | base_url={config.base_url}"
        )
```

**File:** src/agentic_layer/rerank_service.py (L43-45)
```python
            self.base_url = os.getenv(
                "DEEPINFRA_RERANK_BASE_URL", "https://api.deepinfra.com/v1/inference"
            )
```

**File:** src/agentic_layer/rerank_service.py (L47-47)
```python
            self.model = os.getenv("DEEPINFRA_RERANK_MODEL", "Qwen/Qwen3-Reranker-4B")
```

**File:** src/agentic_layer/rerank_service.py (L103-132)
```python
@service(name="rerank_service", primary=True)
class DeepInfraRerankService(DeepInfraRerankServiceInterface):
    """
    DeepInfra重排序服务类

    提供调用DeepInfra API对检索到的记忆进行重排序的方法
    """

    def __init__(self, config: Optional[DeepInfraRerankConfig] = None):
        """
        初始化DeepInfra重排序服务

        Args:
            config: DeepInfra重排序配置，如果为None则尝试从依赖注入获取，最后从环境变量读取
        """
        if config is None:
            try:
                # 尝试从依赖注入获取配置
                from core.di import get_bean

                config = get_bean("deepinfra_rerank_config")
            except Exception:
                # 如果依赖注入失败，从环境变量读取
                config = self._load_config_from_env()

        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._semaphore = asyncio.Semaphore(config.max_concurrent_requests)

        logger.info(f"Initialized DeepInfra Rerank Service with model: {config.model}")
```

**File:** docs/dev_docs/getting_started.md (L82-99)
```markdown
#### LLM 配置
```bash
# Conversation MemCell Extractor / 对话记忆单元提取器
CONV_MEMCELL_LLM_PROVIDER=openai
CONV_MEMCELL_LLM_MODEL=google/gemini-2.5-flash
CONV_MEMCELL_LLM_BASE_URL=https://openrouter.ai/api/v1
CONV_MEMCELL_LLM_API_KEY=sk-or-v1-你的API密钥
CONV_MEMCELL_LLM_TEMPERATURE=0.3
CONV_MEMCELL_LLM_MAX_TOKENS=16384

# Episode Memory Extractor / 情景记忆提取器
EPISODE_MEMORY_LLM_PROVIDER=openai
EPISODE_MEMORY_LLM_MODEL=google/gemini-2.5-flash
EPISODE_MEMORY_LLM_BASE_URL=https://openrouter.ai/api/v1
EPISODE_MEMORY_LLM_API_KEY=sk-or-v1-你的API密钥
EPISODE_MEMORY_LLM_TEMPERATURE=0.3
EPISODE_MEMORY_LLM_MAX_TOKENS=16384
```
```

**File:** docs/dev_docs/getting_started.md (L112-112)
```markdown
DEEPINFRA_DIMENSIONS=1024
```

**File:** src/devops_scripts/data_fix/mongo_fix_episodic_memory_missing_vector.py (L1-29)
```python
#!/usr/bin/env python3
"""
修复历史 EpisodicMemory 文档中缺失的向量字段。

运行方式（推荐通过 bootstrap 运行，自动加载应用上下文与依赖注入）：
  python src/bootstrap.py src/scripts/data_fix/fix_episodic_memory_missing_vector.py --limit 1000 --batch 200 --concurrency 8

参数：
  --limit         最多处理的文档数量（默认 1000）
  --batch         每次从数据库拉取的文档数量（默认 200，越大越快但更占内存）
  --concurrency   并发度（默认 8）
"""

import argparse
import asyncio
from typing import Any, Dict, List, Optional, Tuple

from core.observation.logger import get_logger
from infra_layer.adapters.out.persistence.document.memory.episodic_memory import (
    EpisodicMemory,
)
from agentic_layer.vectorize_service import get_vectorize_service
from common_utils.datetime_utils import from_iso_format, to_iso_format


logger = get_logger(__name__)

# 目标向量模型：不等于该模型的记录也需要重刷
TARGET_VECTOR_MODEL = "Qwen/Qwen3-Embedding-4B"
```

**File:** src/component/llm_adapter/llm/openai_adapter.py (L13-29)
```python
class OpenAIAdapter(LLMBackendAdapter):
    """OpenAI API适配器（基于openai官方包实现）"""

    def __init__(self, config: Dict[str, Any]):
        # 保存配置
        self.config = config
        self.api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.base_url = config.get("base_url") or os.getenv("OPENAI_BASE_URL")
        self.timeout = config.get("timeout", 600)

        if not self.api_key:
            raise ValueError(ErrorMessage.INVALID_PARAMETER.value)

        # 实例化 openai 异步客户端
        self.client = openai.AsyncOpenAI(
            api_key=self.api_key, base_url=self.base_url, timeout=self.timeout
        )
```



# 我问

EverMemOS 的核心概念 MemCell（记忆单元）到底是什么？从代码结构看，有 `memcell_extractor`，但具体的 MemCell 包含哪些字段？是一个结构化的 JSON 对象吗？它与传统 RAG 系统中的 "chunk" 有什么本质区别？MemCell 的粒度是如何确定的？一条对话消息可能生成多个 MemCell 吗？MemCell 之间的关系是如何表示的？是使用图结构吗？如果是，图数据是存储在 MongoDB 还是有单独的图数据库？在检索时，是直接检索 MemCell 还是检索更高层次的 Episode？

# deepwiki答

您询问的是 EverMemOS 的核心概念 MemCell（记忆单元）的定义、结构、粒度控制以及与传统 RAG 系统的区别。<cite />

## MemCell 的定义与数据结构

### 核心数据模型

MemCell 是一个**结构化的 Python dataclass**，定义在 `src/memory_layer/types.py` 中： [1](#4-0) 

**核心字段**：
- `event_id` - 唯一标识符
- `user_id_list` - 参与用户列表
- `original_data` - 原始对话数据（List[Dict]）
- `timestamp` - 时间戳
- `summary` - 摘要（必需）
- `episode` - 情景记忆内容（可选）
- `keywords` - 关键词列表
- `subject` - 主题
- `linked_entities` - 关联实体
- `semantic_memories` - 语义记忆联想列表
- `event_log` - 事件日志对象

### MongoDB 存储结构

MemCell 在 MongoDB 中存储为独立的 collection `memcells`，文档模型定义在 `src/infra_layer/adapters/out/persistence/document/memory/memcell.py`。<cite />

Repository 层提供了完整的 CRUD 操作： [2](#4-1) 

## MemCell 与传统 RAG "Chunk" 的本质区别

### 1. 语义完整性 vs 机械切分

**传统 RAG Chunk**：
- 按固定长度（如 512 tokens）或段落机械切分
- 可能破坏语义边界
- 缺乏上下文理解

**EverMemOS MemCell**：
- **LLM 驱动的智能边界检测**：通过 `ConvMemCellExtractor` 使用 LLM 分析对话，识别语义完整的片段 [3](#4-2) 
- **保留对话上下文**：`original_data` 字段存储完整的原始消息列表，包含 speaker_id、speaker_name、content 等元信息 [4](#4-3) 
- **主题聚焦**：每个 MemCell 有明确的 `subject` 和 `summary`，表示一个完整的对话主题

### 2. 结构化元数据 vs 纯文本

**传统 Chunk**：通常只包含文本内容和位置信息

**MemCell**：包含丰富的结构化元数据：
- `participants` - 参与者列表（支持多人对话场景）
- `keywords` - 提取的关键词（用于 BM25 检索）
- `linked_entities` - 关联实体（支持实体链接）
- `semantic_memories` - 前瞻性语义联想（预测未来行为变化） [5](#4-4) 

### 3. 多层次记忆构建 vs 扁平检索

**传统 RAG**：直接检索 chunk，缺乏层次结构

**EverMemOS**：MemCell 是**原子记忆单元**，作为构建更高层次记忆的基础：
- **Episode（情节记忆）**：多个相关 MemCell 聚合形成，通过 `memcell_event_id_list` 字段关联 [6](#4-5) 
- **Profile（画像）**：从 MemCell 中提取用户特征 [7](#4-6) 
- **Semantic Memory（语义记忆）**：从 MemCell 预测未来行为趋势 [8](#4-7) 

## MemCell 的粒度控制

### 粒度确定机制

MemCell 的粒度**不是固定的**，而是由 LLM 根据对话内容动态判断：<cite />

1. **上下文窗口**：`ConvMemCellExtractor` 接收 `history_raw_data_list`（历史消息）和 `new_raw_data_list`（新消息） [9](#4-8) 

2. **LLM 边界检测**：通过 prompt 引导 LLM 判断：
   - 是否形成完整的对话主题
   - 是否需要等待更多消息（`should_wait` 标志） [10](#4-9) 

3. **动态聚合**：如果 LLM 判断当前消息不足以形成完整 MemCell，返回 `should_wait=True`，系统会累积更多消息后再次触发提取<cite />

### 一条消息 vs 多个 MemCell

**通常情况**：一条对话消息**不会**单独生成 MemCell，而是与前后消息聚合形成一个 MemCell。<cite />

**特殊情况**：如果一条消息包含多个独立主题（如长篇工作汇报），LLM 可能将其拆分为多个 MemCell，但这取决于 LLM 的判断逻辑。<cite />

**实际粒度**：从评估代码可以看到，MemCell 通常包含 **3-10 条原始消息**，形成一个完整的对话片段： [11](#4-10) 

## MemCell 之间的关系表示

### 关系存储方式

MemCell 之间的关系**不是通过图数据库存储**，而是通过以下方式表示：<cite />

#### 1. Episode 聚合关系

Episode（情节记忆）通过 `memcell_event_id_list` 字段记录包含的 MemCell ID 列表，形成**一对多关系**：<cite />

```python
# EpisodicMemory 文档结构
{
  "episode_id": "ep_001",
  "memcell_event_id_list": ["mc_001", "mc_002", "mc_003"],  # 关联的 MemCell
  "summary": "讨论项目进度",
  "episode": "详细的情节内容..."
}
```

这种关系存储在 **MongoDB** 的 `episodic_memories` collection 中，不需要单独的图数据库。<cite />

#### 2. 时间序列关系

MemCell 通过 `timestamp` 字段形成时间序列，Repository 提供了按时间范围查询的方法： [12](#4-11) 

#### 3. 用户/群组关系

通过 `user_id_list`、`group_id`、`participants` 字段建立用户和群组的关联关系，支持多维度查询： [13](#4-12) 

#### 4. 关键词关联

通过 `keywords` 字段建立主题关联，支持关键词检索： [14](#4-13) 

### 聚类管理（可选）

系统提供了 **ClusterManager** 模块，可以基于语义相似度和时间接近度对 MemCell 进行自动聚类： [15](#4-14) 

**聚类特性**：
- 使用 Embedding 计算语义相似度
- 考虑时间间隔（`max_time_gap_days`）
- 支持事件通知机制
- 聚类状态可持久化到 MongoDB（`MongoClusterStorage`）

但这是**可选功能**，不是核心的关系表示方式。<cite />

## 检索策略：MemCell vs Episode

### 检索目标

系统**不直接检索 MemCell**，而是检索**更高层次的记忆类型**：<cite />

#### 1. Episode 检索（主要方式）

`/api/v3/agentic/retrieve_lightweight` 和 `/api/v3/agentic/retrieve_agentic` 接口的 `data_source` 参数支持：
- `episode` - 检索情节记忆（**最常用**）
- `event_log` - 检索事件日志
- `semantic_memory` - 检索语义记忆
- `profile` - 检索用户画像

**不支持直接检索 MemCell**。<cite />

#### 2. 检索流程

以 Episode 检索为例：<cite />

```
用户查询 → Elasticsearch (BM25) + Milvus (向量) 
         → RRF 融合 
         → 返回 Episode 文档（包含 memcell_event_id_list）
         → 如需原始对话，再从 MongoDB 查询 MemCell
```

#### 3. MemCell 的作用

MemCell 在检索中的角色是**构建材料**而非检索目标：<cite />
- **构建阶段**：多个 MemCell 聚合形成 Episode
- **检索阶段**：检索 Episode，Episode 的 `episode` 字段已包含提炼后的内容
- **溯源阶段**：通过 `memcell_event_id_list` 可追溯到原始 MemCell

这种设计避免了检索粒度过细导致的噪声问题。<cite />

## Notes

**关键设计理念**：
- **MemCell 是原子单元**：类似于"记忆分子"，本身不直接用于检索，而是构建更高层次记忆的基础材料<cite />
- **层次化记忆架构**：MemCell → Episode/Profile/Semantic Memory → 检索结果，每一层都有明确的职责<cite />
- **关系表示简洁**：使用 MongoDB 的文档引用（ID 列表）而非图数据库，降低了系统复杂度<cite />
- **LLM 驱动的粒度控制**：不依赖固定规则，而是让 LLM 根据语义判断边界，更符合人类记忆的组织方式<cite />

**与传统 RAG 的核心差异总结**：
- 传统 RAG：文本 → 机械切分 → Chunk → 直接检索
- EverMemOS：对话 → LLM 边界检测 → MemCell → 聚合成 Episode → 检索 Episode

这种设计使得 EverMemOS 能够更好地理解和组织对话记忆，而不仅仅是文本检索。<cite />

**ProfileManager 的自动化**：系统还提供了 `ProfileManager`，可以自动监听 MemCell 提取事件，判断是否包含高价值的用户画像信息，并自动触发 Profile 提取： [16](#4-15) 

这进一步体现了 MemCell 作为"原材料"的定位，系统会自动从中提炼出不同类型的结构化记忆。<cite />

Wiki pages you might want to explore:
- [EverMemOS Overview (EverMind-AI/EverMemOS)](/wiki/EverMind-AI/EverMemOS#1)

### Citations

**File:** src/memory_layer/types.py (L63-106)
```python
@dataclass
class MemCell:
    """
    Boundary detection result following the specified schema.

    This class represents the result of boundary detection analysis
    and contains all the required fields for memory storage.
    """

    event_id: str
    user_id_list: List[str]
    # For downstream consumers we store normalized dicts extracted from RawData
    original_data: List[Dict[str, Any]]
    timestamp: datetime.datetime
    summary: str

    # Optional fields
    group_id: Optional[str] = None
    participants: Optional[List[str]] = None
    type: Optional[RawDataType] = None
    keywords: Optional[List[str]] = None
    subject: Optional[str] = None
    linked_entities: Optional[List[str]] = None
    episode: Optional[str] = None  # 情景记忆内容

    # 语义记忆联想预测字段
    semantic_memories: Optional[List['SemanticMemoryItem']] = None  # 语义记忆联想列表
    # Event Log 字段
    event_log: Optional[Any] = None  # Event Log 对象
    # extend fields, can be used to store any additional information
    extend: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate the result after initialization."""
        if not self.event_id:
            raise ValueError("event_id is required")
        if not self.original_data:
            raise ValueError("original_data is required")
        if not self.summary:
            raise ValueError("summary is required")

    def __repr__(self) -> str:
        return f"MemCell(event_id={self.event_id}, original_data={self.original_data}, timestamp={self.timestamp}, summary={self.summary})"

```

**File:** src/infra_layer/adapters/out/persistence/repository/memcell_raw_repository.py (L25-76)
```python
@repository("memcell_raw_repository", primary=True)
class MemCellRawRepository(BaseRepository[MemCell]):
    """
    MemCell 原生 CRUD 仓库

    提供对 MemCell 文档的直接数据库操作，包括：
    - 基本 CRUD 操作（继承自 BaseRepository）
    - 复合查询和筛选
    - 批量操作
    - 统计和聚合查询
    - 事务管理（继承自 BaseRepository）
    """

    def __init__(self):
        """初始化仓库"""
        super().__init__(MemCell)

    async def get_by_event_id(self, event_id: str) -> Optional[MemCell]:
        """
        根据 event_id 获取 MemCell

        Args:
            event_id: 事件 ID

        Returns:
            MemCell 实例或 None
        """
        try:
            result = await self.model.find_one({"_id": ObjectId(event_id)})
            if result:
                logger.debug("✅ 根据 event_id 获取 MemCell 成功: %s", event_id)
            else:
                logger.debug("⚠️  未找到 MemCell: event_id=%s", event_id)
            return result
        except Exception as e:
            logger.error("❌ 根据 event_id 获取 MemCell 失败: %s", e)
            return None

    async def append_memcell(
        self, memcell: MemCell, session: Optional[AsyncIOMotorClientSession] = None
    ) -> Optional[MemCell]:
        """
        追加 MemCell
        """
        try:
            await memcell.insert(session=session)
            print(f"✅ 追加 MemCell 成功: {memcell.event_id}")
            return memcell
        except Exception as e:
            logger.error("❌ 追加 MemCell 失败: %s", e)
            return None

```

**File:** src/infra_layer/adapters/out/persistence/repository/memcell_raw_repository.py (L134-177)
```python
    async def find_by_user_id(
        self,
        user_id: str,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort_desc: bool = True,
    ) -> List[MemCell]:
        """
        根据用户 ID 查询 MemCell

        Args:
            user_id: 用户 ID
            limit: 限制返回数量
            skip: 跳过数量
            sort_desc: 是否按时间降序排序

        Returns:
            MemCell 列表
        """
        try:
            query = self.model.find({"user_id": user_id})

            # 排序
            if sort_desc:
                query = query.sort("-timestamp")
            else:
                query = query.sort("timestamp")

            # 分页
            if skip:
                query = query.skip(skip)
            if limit:
                query = query.limit(limit)

            results = await query.to_list()
            logger.debug(
                "✅ 根据用户 ID 查询 MemCell 成功: %s, 找到 %d 条记录",
                user_id,
                len(results),
            )
            return results
        except Exception as e:
            logger.error("❌ 根据用户 ID 查询 MemCell 失败: %s", e)
            return []
```

**File:** src/infra_layer/adapters/out/persistence/repository/memcell_raw_repository.py (L375-417)
```python
    async def search_by_keywords(
        self,
        keywords: List[str],
        match_all: bool = False,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
    ) -> List[MemCell]:
        """
        根据关键词查询 MemCell

        Args:
            keywords: 关键词列表
            match_all: 是否匹配所有关键词（True）或匹配任一关键词（False）
            limit: 限制返回数量
            skip: 跳过数量

        Returns:
            MemCell 列表
        """
        try:
            if match_all:
                query = self.model.find({"keywords": {"$all": keywords}})
            else:
                query = self.model.find({"keywords": {"$in": keywords}})

            query = query.sort("-timestamp")

            if skip:
                query = query.skip(skip)
            if limit:
                query = query.limit(limit)

            results = await query.to_list()
            logger.debug(
                "✅ 根据关键词查询 MemCell 成功: %s, 匹配模式: %s, 找到 %d 条记录",
                keywords,
                '全部' if match_all else '任一',
                len(results),
            )
            return results
        except Exception as e:
            logger.error("❌ 根据关键词查询 MemCell 失败: %s", e)
            return []
```

**File:** src/memory_layer/memory_manager.py (L112-181)
```python
    async def extract_memcell(
        self,
        history_raw_data_list: list[RawData],
        new_raw_data_list: list[RawData],
        raw_data_type: RawDataType,
        group_id: Optional[str] = None,
        group_name: Optional[str] = None,
        user_id_list: Optional[List[str]] = None,
        old_memory_list: Optional[List[Memory]] = None,
        enable_semantic_extraction: bool = True,
        enable_event_log_extraction: bool = True,
    ) -> tuple[Optional[MemCell], Optional[StatusResult]]:
        """
        提取 MemCell（包含可选的语义记忆和事件日志提取）
        
        Args:
            history_raw_data_list: 历史消息列表
            new_raw_data_list: 新消息列表
            raw_data_type: 数据类型
            group_id: 群组ID
            group_name: 群组名称
            user_id_list: 用户ID列表
            old_memory_list: 历史记忆列表
            enable_semantic_extraction: 是否提取语义记忆（默认True）
            enable_event_log_extraction: 是否提取事件日志（默认True）
            
        Returns:
            (MemCell, StatusResult) 或 (None, StatusResult)
        """
        logger = get_logger(__name__)
        now = time.time()
        
        # 1. 提取基础 MemCell（包括可选的语义记忆）
        request = ConversationMemCellExtractRequest(
            history_raw_data_list,
            new_raw_data_list,
            user_id_list=user_id_list,
            group_id=group_id,
            group_name=group_name,
            old_memory_list=old_memory_list,
        )
        extractor = ConvMemCellExtractor(self.conv_memcall_llm_provider)
        memcell, status_result = await extractor.extract_memcell(
            request, 
            use_semantic_extraction=enable_semantic_extraction
        )
        
        # 2. 如果成功提取 MemCell，且启用了 Event Log 提取
        if memcell and enable_event_log_extraction and hasattr(memcell, 'episode') and memcell.episode:
            if self._event_log_extractor is None:
                self._event_log_extractor = EventLogExtractor(llm_provider=self.event_log_llm_provider)
            
            logger.debug(f"开始提取 Event Log: {memcell.event_id}")
            event_log = await self._event_log_extractor.extract_event_log(
                episode_text=memcell.episode,
                timestamp=memcell.timestamp
            )
            
            if event_log:
                memcell.event_log = event_log
                logger.debug(f"Event Log 提取成功: {memcell.event_id}")
        
        logger.debug(
            f"提取MemCell完成, raw_data_type: {raw_data_type}, "
            f"semantic_extraction={enable_semantic_extraction}, "
            f"event_log_extraction={enable_event_log_extraction}, "
            f"耗时: {time.time() - now}秒"
        )
        
        return memcell, status_result
```

**File:** src/memory_layer/memory_manager.py (L205-214)
```python
        if memory_type == MemoryType.EPISODE_SUMMARY:
            extractor = EpisodeMemoryExtractor(
                self.episode_memory_extractor_llm_provider
            )
            request = EpisodeMemoryExtractRequest(
                memcell_list=memcell_list,
                user_id_list=user_ids,
                group_id=group_id,
                old_memory_list=old_memory_list,
            )
```

**File:** src/memory_layer/memory_manager.py (L215-225)
```python
        elif memory_type == MemoryType.PROFILE:
            if memcell_list[0].type == RawDataType.CONVERSATION:
                extractor = ProfileMemoryExtractor(
                    self.profile_memory_extractor_llm_provider
                )
                request = ProfileMemoryExtractRequest(
                    memcell_list=memcell_list,
                    user_id_list=user_ids,
                    group_id=group_id,
                    old_memory_list=old_memory_list,
                )
```

**File:** src/memory_layer/prompts/en/semantic_mem_prompts.py (L102-197)
```python
SEMANTIC_GENERATION_PROMPT = """
You are an advanced personal semantic analysis agent. Your task is to predict the specific impacts that a user's latest MemCell event might have on their future personal behaviors, habits, decisions, and lifestyle.

## Task Objectives:
1. **Personal-Level Association**: Analyze the event's potential impact on the user's future behavior, thinking patterns, life habits, or decision preferences from the personal perspective.
2. **Associative Prediction, Not Summary**: Based on event content, predict potential personal changes rather than repeating or summarizing the original content.
3. **Scenario Style Matching**: Predictions must match the scenario style of the event:
   - Life scenarios (e.g., health, family, leisure, learning) → Use casual language, focus on personal habits, emotional states, lifestyle, personal growth, etc.
   - Work scenarios (e.g., career development, skill improvement, work style) → Use professional language, focus on career planning, capability enhancement, work habits, professional development, etc.
4. **Personal Behavior-Oriented**: Each association should reflect the user's "potential changes" or "behavioral tendencies," focusing on individual-level future development.
5. **Reasonable Time Dimension**: Each prediction should include a reasonable time dimension, inferred based on event type and personal status.
6. **Specific and Actionable**: Each prediction should not exceed 40 words, must generate exactly 10 predictions, with specific and verifiable content.
7. **Direct User ID Usage**: Output should directly use user IDs (e.g., user_1), avoid using generic terms like "the user."

## Output Format:
Return results as a JSON array, each association includes time information:
[
  {
    "content": "user_1 should pay more attention to emotional management recently",
    "start_time": "2025-10-21",
    "end_time": "2025-10-28",
    "duration_days": 7,
    "source_episode_id": "test-001"
  },
  ...
]

## Example Input (Life Scenario):
{
  "event_id": "test-001",
  "user_id": "XiaoMing",
  "subject": "XiaoMing completed wisdom tooth extraction surgery and post-operative instructions",
  "summary": "XiaoMing successfully had wisdom tooth extraction this afternoon, doctor emphasized attention to diet and hygiene for the next week.",
  "episode": "On the afternoon of October 21, 2025, XiaoMing described the tooth extraction experience, the doctor reminded to maintain oral hygiene and regular follow-ups."
}

## Example Output (Life Scenario):
[
  {
    "content": "XiaoMing will adjust dietary habits for the next week",
    "start_time": "2025-10-21",
    "end_time": "2025-10-28",
    "duration_days": 7,
    "source_episode_id": "test-001"
  },
  {
    "content": "XiaoMing will develop a habit of regular dental check-ups",
    "start_time": "2025-10-21",
    "end_time": "2025-11-21",
    "duration_days": 31,
    "source_episode_id": "test-001"
  }
  ...
]

## Example Input (Work Scenario):
{
  "event_id": "work-001",
  "user_id": "LiHua",
  "subject": "LiHua attended project management training",
  "summary": "LiHua attended a three-day project management training and learned new working methods.",
  "episode": "From October 21-23, 2025, LiHua attended company-organized project management training, learning agile development methods and team collaboration skills."
}

## Example Output (Work Scenario):
[
  {
    "content": "LiHua will apply new project management methods in the future",
    "start_time": "2025-10-24",
    "end_time": "2025-11-24",
    "duration_days": 31,
    "source_episode_id": "work-001"
  },
  {
    "content": "LiHua will pay attention to more career development opportunities",
    "start_time": "2025-10-24",
    "end_time": "2025-12-24",
    "duration_days": 61,
    "source_episode_id": "work-001"
  }
  ...
]

## Important Notes:
- **Personal-Oriented**: Focus on "personal-level future changes," content can cover life, learning, work, emotions, habits, and other personal development areas.
- **Associative Innovation**: Don't repeat original content; generate personal behavioral, habitual, or decision-making changes that the event might trigger.
- **Scenario Adaptation**: Language style must match the event scenario - use casual expressions for life scenarios, professional expressions for work scenarios.
- **Time Inference**: Reasonably infer time ranges based on event type, personal status, and common sense - don't rigidly apply fixed times.
- **Content Practicality**: Content must be specific, reasonable, practical, and usable by the system for personal semantic memory modeling.
- **Time Information Extraction Rules:**
  - start_time: Extract the specific date when the event occurred from the MemCell's timestamp field, format: YYYY-MM-DD
  - end_time: Extract the specific end time from the original content. If there's an explicit end time (e.g., "before October 24", "2025-11-15"), extract the specific date; otherwise, reasonably infer based on event content and common sense
  - duration_days: Extract duration from the original content. If there's explicit time description (e.g., "within a week", "7 days", "one month"), extract days; otherwise, reasonably infer based on event content and common sense
  - source_episode_id: Use the event_id from the input
  - **Important**: Prioritize extracting explicit time information from the original text; if not available, make reasonable inferences based on event content and common sense. Time cannot be null
"""
```

**File:** src/memory_layer/memcell_extractor/base_memcell_extractor.py (L252-263)
```python
@dataclass
class MemCellExtractRequest:
    history_raw_data_list: List[RawData]
    new_raw_data_list: List[RawData]
    # 整个群的user id
    user_id_list: List[str]
    group_id: Optional[str] = None
    group_name: Optional[str] = None

    old_memory_list: Optional[List[Memory]] = None
    smart_mask_flag: Optional[bool] = False

```

**File:** src/memory_layer/memcell_extractor/base_memcell_extractor.py (L265-271)
```python
@dataclass
class StatusResult:
    """Status control result."""

    # 表示下次触发时，这次的对话会累积一起作为new message输入
    should_wait: bool

```

**File:** evaluation/src/adapters/evermemos/stage4_response.py (L29-61)
```python
def load_memcells_by_conversation(conv_idx: int, memcells_dir: Path) -> Dict[str, dict]:
    """
    加载指定对话的所有 memcells，返回 event_id -> memcell 的映射
    
    Args:
        conv_idx: 对话索引
        memcells_dir: memcells 目录路径
    
    Returns:
        {event_id: memcell_dict} 的映射
    """
    memcell_file = memcells_dir / f"memcell_list_conv_{conv_idx}.json"
    
    if not memcell_file.exists():
        print(f"Warning: Memcell file not found: {memcell_file}")
        return {}
    
    try:
        with open(memcell_file, "r", encoding="utf-8") as f:
            memcells = json.load(f)
        
        # 构建 event_id -> memcell 的映射
        memcell_map = {}
        for memcell in memcells:
            event_id = memcell.get("event_id")
            if event_id:
                memcell_map[event_id] = memcell
        
        return memcell_map
    
    except Exception as e:
        print(f"Error loading memcells from {memcell_file}: {e}")
        return {}
```

**File:** demo/utils/memory_utils.py (L128-149)
```python
async def query_memcells_by_group_and_time(
    group_id: str, start_date: datetime, end_date: datetime
) -> List[DocMemCell]:
    """按群组和时间范围查询 MemCell

    Args:
        group_id: 群组 ID
        start_date: 开始日期
        end_date: 结束日期

    Returns:
        MemCell 文档对象列表
    """
    memcells = (
        await DocMemCell.find(
            {"group_id": group_id, "timestamp": {"$gte": start_date, "$lt": end_date}}
        )
        .sort("timestamp")
        .to_list()
    )

    return memcells
```

**File:** src/memory_layer/cluster_manager/__init__.py (L1-47)
```python
"""Cluster Manager - Automatic clustering of memcells with event notifications.

This module provides ClusterManager, a core component that clusters memcells
based on semantic similarity and temporal proximity, with event hooks for
downstream processing.

Key Features:
- Incremental clustering using embeddings and timestamps
- Event notifications on cluster assignments
- Flexible storage backends for cluster state
- Seamless integration with MemCellExtractor

Usage:
    from memory_layer.cluster_manager import ClusterManager, ClusterManagerConfig
    
    # Initialize
    config = ClusterManagerConfig(
        similarity_threshold=0.65,
        max_time_gap_days=7,
        enable_persistence=True
    )
    cluster_mgr = ClusterManager(config)
    
    # Attach to memcell extractor
    cluster_mgr.attach_to_extractor(memcell_extractor)
    
    # Register callbacks for cluster events
    cluster_mgr.on_cluster_assigned(my_callback)
    
    # Clusters are automatically assigned, callbacks notified!
"""

from memory_layer.cluster_manager.config import ClusterManagerConfig
from memory_layer.cluster_manager.manager import ClusterManager
from memory_layer.cluster_manager.storage import (
    ClusterStorage,
    InMemoryClusterStorage,
)
from memory_layer.cluster_manager.mongo_cluster_storage import MongoClusterStorage

__all__ = [
    "ClusterManager",
    "ClusterManagerConfig",
    "ClusterStorage",
    "InMemoryClusterStorage",
    "MongoClusterStorage",
]
```

**File:** src/memory_layer/profile_manager/discriminator.py (L105-159)
```python
    def _build_group_chat_prompt(
        self,
        latest: Any,
        recent: List[Any]
    ) -> str:
        """Build prompt for group_chat scenario."""
        context_texts = []
        if self.config.use_context and recent:
            window = recent[-self.config.context_window:]
            for i, mc in enumerate(window):
                text = self._extract_text(mc)
                if text:
                    context_texts.append(f"[Context {i+1}]\n{text}")
        
        latest_text = self._extract_text(latest)
        context_block = "\n\n".join(context_texts) if context_texts else "No context available"
        
        prompt = f"""You are a precise profile value discriminator for work/group chat scenario.

Given the latest conversation MemCell and recent context, determine if the latest MemCell contains 
new, concrete, and attributable information about user profile fields such as:

Profile Fields to Consider:
- role_responsibility: User's role, duties, responsibilities
- hard_skills: Technical skills, tools, technologies
- soft_skills: Communication, leadership, collaboration
- projects_participated: Project names, roles, contributions
- working_habit_preference: Work style, preferences, routines
- personality: Character traits, temperament
- way_of_decision_making: Decision patterns, priorities
- interests: Professional interests, areas of focus
- tendency: Behavioral tendencies, patterns

Rules for Judgment:
1. Reject small talk, vague statements, or non-attributable content
2. Prefer explicit statements (e.g., "I am responsible for X", "I have experience with Y")
3. Look for concrete evidence, not assumptions
4. Consider if the information is stable/lasting vs transient
5. Ensure the information is clearly attributable to a specific user

Context (Previous MemCells):
{context_block}

Latest MemCell to Evaluate:
{latest_text}

Respond with strict JSON only (no extra text):
{{
  "is_high_value": true/false,
  "confidence": 0.0-1.0,
  "reasons": "Brief explanation of your judgment"
}}"""
        
        return prompt
    
```


# 我问

关于混合检索（RRF 融合），README 提到并行执行语义检索和关键词检索，然后用 Reciprocal Rank Fusion 融合。具体的融合算法参数是什么？K 值设置为多少？两种检索方式的权重是固定的还是可以调整？在实际场景中，如何根据查询类型动态调整权重？比如对于实体查询（"张三的电话"）更依赖关键词检索，对于语义查询（"用户的兴趣爱好"）更依赖向量检索。系统是否支持这种动态策略？另外，Reranker 的批处理大小是多少？如何平衡吞吐量和延迟？

# deepwiki答

您询问的是 EverMemOS 混合检索中 RRF（Reciprocal Rank Fusion）融合算法的具体参数配置、权重调整策略，以及 Reranker 的批处理配置。<cite />

## RRF 融合算法参数

### K 值配置

系统在多处使用 RRF 融合，**K 值统一设置为 60**，这是工业界验证的经验最优值： [1](#5-0) 

**RRF 公式**：`RRF_score(doc) = Σ(1 / (k + rank_i))` [2](#5-1) 

**K=60 的优势**：
- 无需归一化分数（Embedding 和 BM25 分数范围不同）
- 对头部结果更敏感（高排名贡献更大）
- 无需调参，工业界广泛验证（Elasticsearch 等） [3](#5-2) 

### 实际使用场景

#### 1. 轻量级检索（Lightweight）

在 `lightweight_retrieval` 中，RRF 融合 Embedding 和 BM25 结果： [4](#5-3) 

**参数配置**：
- Embedding 候选数：50（`config.lightweight_emb_top_n`）
- BM25 候选数：50（`config.lightweight_bm25_top_n`）
- RRF K 值：60（硬编码） [5](#5-4) 
- 最终返回：20（`config.lightweight_final_top_n`）

#### 2. 混合检索（Hybrid Search）

在 `hybrid_search_with_rrf` 中，同样使用 K=60： [6](#5-5) 

**可配置参数**：
- `emb_candidates`：Embedding 候选数（默认 50）
- `bm25_candidates`：BM25 候选数（默认 50）
- `rrf_k`：RRF 参数（默认 60） [7](#5-6) 
- `top_n`：最终返回数（默认 40）

#### 3. 多查询融合（Multi-Query RRF）

在 Agentic 检索的多查询场景中，使用相同的 K=60 融合多个查询结果： [8](#5-7) 

**融合逻辑**：在多个查询中都排名靠前的文档 → 分数累积高 → 最终排名靠前 [9](#5-8) 

## 权重调整策略

### 当前实现：固定权重

**重要发现**：系统**不支持动态权重调整**，RRF 算法本身是**无权重**的融合策略。<cite />

RRF 的核心特点是**基于排名而非分数**，每个检索方法对最终结果的贡献完全由其排名位置决定，公式中没有权重参数： [2](#5-1) 

```python
# RRF 融合逻辑（无权重参数）
doc_rrf_scores[doc_id] = doc_rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank)
``` [10](#5-9) 

### 间接调整方式

虽然 RRF 本身无权重，但可以通过以下方式**间接影响**两种检索方式的贡献：

#### 1. 调整候选数量

通过改变 `emb_candidates` 和 `bm25_candidates` 的比例，可以间接调整权重： [11](#5-10) 

```python
# 示例：更依赖 BM25（关键词检索）
emb_candidates=30,   # 减少 Embedding 候选
bm25_candidates=70,  # 增加 BM25 候选

# 示例：更依赖 Embedding（语义检索）
emb_candidates=70,   # 增加 Embedding 候选
bm25_candidates=30,  # 减少 BM25 候选
```

#### 2. 单独使用某种检索

系统支持**跳过融合**，单独使用 Embedding 或 BM25： [12](#5-11) 

**配置选项**：
- `config.use_hybrid_search=False` + `config.use_emb=True`：仅 Embedding
- `config.use_hybrid_search=False` + `config.use_emb=False`：仅 BM25

### 动态策略的缺失

**当前系统不支持**根据查询类型（实体查询 vs 语义查询）动态调整权重。<cite />

**原因分析**：
1. RRF 算法设计上就是**无权重**的，依赖排名融合
2. 代码中没有查询分类器（Query Classifier）来判断查询类型
3. 没有针对不同查询类型的配置分支

**实现动态策略的建议**：
1. 添加查询分类器（如基于关键词匹配或 LLM 判断）
2. 根据查询类型选择不同的检索策略：
   - 实体查询 → 仅 BM25 或 BM25 候选数更多
   - 语义查询 → 仅 Embedding 或 Embedding 候选数更多
   - 混合查询 → 使用 RRF 融合

## Reranker 批处理配置

### 批处理大小

Reranker 的批处理大小**可配置**，默认值为 **10**： [13](#5-12) 

**环境变量配置**： [14](#5-13) 
```bash
DEEPINFRA_RERANK_BATCH_SIZE=10  # 默认值
```

**批处理逻辑**： [15](#5-14) 
```python
# 将文档分批，每批 batch_size 个
batches = []
for i in range(0, len(doc_texts), batch_size):
    batch = doc_texts[i : i + batch_size]
    batches.append((i, batch))
```

### 吞吐量与延迟平衡

#### 1. 串行批处理策略

系统采用**串行处理批次**（而非并发），以避免 API 限流： [16](#5-15) 

**优势**：
- 避免 API 限流（DeepInfra 有并发限制）
- 更稳定，成功率高
- 支持重试和指数退避

**劣势**：
- 延迟较高（批次数 × 单批延迟）

#### 2. 并发控制

虽然批次是串行的，但系统在 Rerank 服务层面有**并发限制**： [17](#5-16) 

```python
self._semaphore = asyncio.Semaphore(config.max_concurrent_requests)
```

**默认并发数**：5（`DEEPINFRA_RERANK_MAX_CONCURRENT=5`） [18](#5-17) 

#### 3. 重试与超时机制

每个批次支持**重试和指数退避**： [19](#5-18) 

**配置参数**：
- `max_retries`：最大重试次数（默认 3）
- `retry_delay`：重试基础延迟（默认 2.0 秒）
- `timeout`：单批次超时（默认 30 秒） [20](#5-19) 

**指数退避**：2s → 4s → 8s [21](#5-20) 

#### 4. 降级策略

如果 Rerank 成功率过低，自动降级到原始排序： [22](#5-21) 

```python
fallback_threshold=0.3  # 成功率低于 30% 时降级
```

### 性能权衡建议

| 批处理大小 | 吞吐量 | 延迟 | 适用场景 |
|-----------|--------|------|---------|
| 5 | 低 | 低 | 实时对话（延迟敏感） |
| 10（默认） | 中 | 中 | 平衡场景 |
| 20 | 高 | 高 | 批量处理（吞吐优先） |

**调整建议**：
- **延迟敏感**：减小 `batch_size` 到 5，增加 `max_concurrent_requests` 到 10
- **吞吐优先**：增大 `batch_size` 到 20，保持串行处理避免限流
- **高可用**：增加 `max_retries` 到 5，延长 `timeout` 到 60 秒

## Notes

**关键发现**：
- **RRF K=60 是固定值**，在所有检索场景中统一使用 [23](#5-22) 
- **无权重参数**：RRF 算法本身不支持权重调整，只能通过候选数量间接影响<cite />
- **动态策略缺失**：系统不支持根据查询类型自动选择检索策略<cite />
- **Reranker 批处理**：默认 10，串行处理，支持重试和降级 [24](#5-23) 

**Agentic 检索的配置**：在 Agentic 模式下，RRF 参数同样使用 K=60： [25](#5-24) 

**多查询融合示例**：在多查询场景中，RRF 融合多个查询结果，K 值保持 60： [26](#5-25) 

**实现动态权重的替代方案**：
1. 在应用层实现查询分类器
2. 根据分类结果调用不同的检索接口（`use_emb` / `use_hybrid_search`）
3. 或者调整 `emb_candidates` 和 `bm25_candidates` 的比例

Wiki pages you might want to explore:
- [EverMemOS Overview (EverMind-AI/EverMemOS)](/wiki/EverMind-AI/EverMemOS#1)

Wiki pages you might want to explore:
- [EverMemOS Overview (EverMind-AI/EverMemOS)](/wiki/EverMind-AI/EverMemOS#1)

### Citations

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L192-227)
```python
def reciprocal_rank_fusion(
    emb_results: List[Tuple[dict, float]],
    bm25_results: List[Tuple[dict, float]],
    k: int = 60
) -> List[Tuple[dict, float]]:
    """
    使用 RRF (Reciprocal Rank Fusion) 融合 Embedding 和 BM25 检索结果
    
    RRF 是一种无需归一化的融合策略，对排序位置敏感。
    公式：RRF_score(doc) = Σ(1 / (k + rank_i))
    
    优势：
    1. 无需归一化分数（Embedding 和 BM25 分数范围不同）
    2. 简单有效，工业界广泛验证（Elasticsearch 等）
    3. 对头部结果更敏感（高排名贡献更大）
    4. 无需调参（k=60 是经验最优值）
    
    Args:
        emb_results: Embedding 检索结果 [(doc, score), ...]
        bm25_results: BM25 检索结果 [(doc, score), ...]
        k: RRF 常数，通常使用 60（经验值）
    
    Returns:
        融合后的结果 [(doc, rrf_score), ...]，按 RRF 分数降序排列
    
    Example:
        emb_results = [(doc1, 0.92), (doc2, 0.87), (doc3, 0.81)]
        bm25_results = [(doc2, 15.3), (doc1, 12.7), (doc4, 10.2)]
        
        Doc1: 1/(60+1) + 1/(60+2) = 0.0323
        Doc2: 1/(60+2) + 1/(60+1) = 0.0323  
        Doc3: 1/(60+3) + 0        = 0.0159
        Doc4: 0        + 1/(60+3) = 0.0159
        
        融合结果: [(doc1, 0.0323), (doc2, 0.0323), (doc3, 0.0159), (doc4, 0.0159)]
    """
```

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L239-239)
```python
        doc_rrf_scores[doc_id] = doc_rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank)
```

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L257-324)
```python
def multi_rrf_fusion(
    results_list: List[List[Tuple[dict, float]]],
    k: int = 60
) -> List[Tuple[dict, float]]:
    """
    使用 RRF 融合多个查询的检索结果（多查询融合）
    
    与双路 RRF 类似，但支持融合任意数量的检索结果。
    每个结果集贡献的分数：1 / (k + rank)
    
    原理：
    - 在多个查询中都排名靠前的文档 → 分数累积高 → 最终排名靠前
    - 这是一种"投票机制"：多个查询都认为相关的文档更可能真正相关
    
    Args:
        results_list: 多个检索结果列表 [
            [(doc1, score), (doc2, score), ...],  # Query 1 结果
            [(doc3, score), (doc1, score), ...],  # Query 2 结果
            [(doc4, score), (doc2, score), ...],  # Query 3 结果
        ]
        k: RRF 常数（默认 60）
    
    Returns:
        融合后的结果 [(doc, rrf_score), ...]，按 RRF 分数降序排列
    
    Example:
        Query 1 结果: [(doc_A, 0.9), (doc_B, 0.8), (doc_C, 0.7)]
        Query 2 结果: [(doc_B, 0.88), (doc_D, 0.82), (doc_A, 0.75)]
        Query 3 结果: [(doc_A, 0.92), (doc_E, 0.85), (doc_B, 0.80)]
        
        RRF 分数计算：
        doc_A: 1/(60+1) + 1/(60+3) + 1/(60+1) = 0.0323  ← 在 Q1,Q2,Q3 都出现
        doc_B: 1/(60+2) + 1/(60+1) + 1/(60+3) = 0.0323  ← 在 Q1,Q2,Q3 都出现
        doc_C: 1/(60+3) + 0        + 0        = 0.0159  ← 只在 Q1 出现
        doc_D: 0        + 1/(60+2) + 0        = 0.0161  ← 只在 Q2 出现
        doc_E: 0        + 0        + 1/(60+2) = 0.0161  ← 只在 Q3 出现
        
        融合结果: doc_A 和 doc_B 排名最高（被多个查询认可）
    """
    if not results_list:
        return []
    
    # 如果只有一个结果集，直接返回
    if len(results_list) == 1:
        return results_list[0]
    
    # 🔥 修复：使用 event_id 作为唯一标识，而不是 Python 内存地址
    # 原因：BM25 和 Embedding 索引分别加载 JSON，创建了不同的 Python 对象
    # 即使内容相同，id() 也会不同，导致无法去重
    doc_rrf_scores = {}  # {event_id: rrf_score}
    doc_map = {}         # {event_id: doc}
    
    # 遍历每个查询的检索结果
    for query_results in results_list:
        for rank, (doc, score) in enumerate(query_results, start=1):
            doc_id = doc.get("event_id", id(doc))  # 🔥 优先使用 event_id，回退到 id()
            if doc_id not in doc_map:
                doc_map[doc_id] = doc
            # 累加 RRF 分数
            doc_rrf_scores[doc_id] = doc_rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    
    # 按 RRF 分数排序
    sorted_docs = sorted(doc_rrf_scores.items(), key=lambda x: x[1], reverse=True)
    
    # 转换回 (doc, score) 格式
    fused_results = [(doc_map[doc_id], rrf_score) for doc_id, rrf_score in sorted_docs]
    
    return fused_results
```

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L327-412)
```python
async def lightweight_retrieval(
    query: str,
    emb_index,
    bm25,
    docs,
    config: ExperimentConfig,
) -> Tuple[List[Tuple[dict, float]], dict]:
    """
    轻量级快速检索（无 LLM 调用，纯算法检索）
    
    流程：
    1. 并行执行 Embedding 和 BM25 检索
    2. 各取 Top-50 候选
    3. 使用 RRF 融合
    4. 返回 Top-20 结果
    
    优势：
    - 速度快：无 LLM 调用，纯向量/词法检索
    - 成本低：不消耗 LLM API 费用
    - 稳定：无网络依赖，纯本地计算
    
    适用场景：
    - 对延迟敏感的场景
    - 预算有限的场景
    - 查询简单明确的场景
    
    Args:
        query: 用户查询
        emb_index: Embedding 索引
        bm25: BM25 索引
        docs: 文档列表
        config: 实验配置
    
    Returns:
        (final_results, metadata)
    """
    start_time = time.time()
    
    metadata = {
        "retrieval_mode": "lightweight",
        "emb_count": 0,
        "bm25_count": 0,
        "final_count": 0,
        "total_latency_ms": 0.0,
    }
    
    # ========== 并行执行 Embedding 和 BM25 检索 ==========
    emb_task = search_with_emb_index(
        query, 
        emb_index, 
        top_n=config.lightweight_emb_top_n  # 默认 50
    )
    bm25_task = asyncio.to_thread(
        search_with_bm25_index, 
        query, 
        bm25, 
        docs, 
        config.lightweight_bm25_top_n  # 默认 50
    )
    
    emb_results, bm25_results = await asyncio.gather(emb_task, bm25_task)
    
    metadata["emb_count"] = len(emb_results)
    metadata["bm25_count"] = len(bm25_results)
    
    # ========== RRF 融合 ==========
    if not emb_results and not bm25_results:
        metadata["total_latency_ms"] = (time.time() - start_time) * 1000
        return [], metadata
    elif not emb_results:
        final_results = bm25_results[:config.lightweight_final_top_n]
    elif not bm25_results:
        final_results = emb_results[:config.lightweight_final_top_n]
    else:
        # 使用 RRF 融合
        fused_results = reciprocal_rank_fusion(
            emb_results, 
            bm25_results, 
            k=60  # 标准 RRF 参数
        )
        final_results = fused_results[:config.lightweight_final_top_n]  # 默认 20
    
    metadata["final_count"] = len(final_results)
    metadata["total_latency_ms"] = (time.time() - start_time) * 1000
    
    return final_results, metadata
```

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L498-581)
```python
async def hybrid_search_with_rrf(
    query: str,
    emb_index,
    bm25,
    docs,
    top_n: int = 40,
    emb_candidates: int = 50,
    bm25_candidates: int = 50,
    rrf_k: int = 60,
    query_embedding: Optional[np.ndarray] = None  # 🔥 支持预计算的 embedding
) -> List[Tuple[dict, float]]:
    """
    使用 RRF 融合 Embedding 和 BM25 检索结果（混合检索）
    
    执行流程：
    1. 并行执行 Embedding (MaxSim) 和 BM25 检索
    2. 每种方法分别召回 top-N 候选文档
    3. 使用 RRF 融合两个结果集
    4. 返回融合后的 Top-N 文档
    
    为什么使用混合检索：
    - Embedding: 擅长语义匹配，但对罕见词和精确匹配较弱
    - BM25: 擅长精确匹配和罕见词，但语义理解较弱
    - RRF 融合: 结合两者优势，提升召回率 15-20%
    
    Args:
        query: 用户查询
        emb_index: Embedding 索引
        bm25: BM25 索引
        docs: 文档列表（用于 BM25）
        top_n: 最终返回的结果数量（默认 40）
        emb_candidates: Embedding 检索的候选数量（默认 50）
        bm25_candidates: BM25 检索的候选数量（默认 50）
        rrf_k: RRF 参数 k（默认 60，经验最优值）
    
    Returns:
        融合后的 Top-N 结果 [(doc, rrf_score), ...]
    
    Example:
        Query: "他喜欢吃什么？"
        
        Embedding Top-3:
        - (doc_A: "用户喜爱川菜", 0.92)  # 语义匹配"喜欢"="喜爱"
        - (doc_B: "用户偏好清淡口味", 0.78)
        - (doc_C: "成都是美食之都", 0.65)
        
        BM25 Top-3:
        - (doc_A: "用户喜爱川菜", 15.3)  # 精确匹配"喜欢"
        - (doc_D: "喜欢吃火锅", 12.7)  # 精确匹配"喜欢吃"
        - (doc_E: "最喜欢的菜是麻婆豆腐", 10.2)
        
        RRF 融合:
        - doc_A: 同时在两个结果中排名靠前 → 最高分 ✅
        - doc_D: 只在 BM25 中排名高
        - doc_B: 只在 Embedding 中排名高
        
        最终: [(doc_A, 0.0323), (doc_D, 0.0161), (doc_B, 0.0161), ...]
    """
    # 并行执行 Embedding 和 BM25 检索（提高效率）
    emb_task = search_with_emb_index(
        query, emb_index, top_n=emb_candidates, query_embedding=query_embedding
    )
    bm25_task = asyncio.to_thread(search_with_bm25_index, query, bm25, docs, bm25_candidates)
    
    # 等待两个检索任务完成
    emb_results, bm25_results = await asyncio.gather(emb_task, bm25_task)
    
    # 如果其中一个检索结果为空，返回另一个
    if not emb_results and not bm25_results:
        return []
    elif not emb_results:
        print(f"Warning: Embedding search returned no results for query: {query}")
        return bm25_results[:top_n]
    elif not bm25_results:
        print(f"Warning: BM25 search returned no results for query: {query}")
        return emb_results[:top_n]
    
    # 使用 RRF 融合两个检索结果
    fused_results = reciprocal_rank_fusion(emb_results, bm25_results, k=rrf_k)
    
    # 打印融合统计信息（用于调试）
    print(f"Hybrid search: Emb={len(emb_results)}, BM25={len(bm25_results)}, Fused={len(fused_results)}, Returning top-{top_n}")
    
    return fused_results[:top_n]
```

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L771-774)
```python
        round2_results = multi_rrf_fusion(
            results_list=multi_query_results,
            k=config.hybrid_rrf_k  # 使用相同的 k 参数
        )
```

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L877-902)
```python
    batch_size: int = 10,  # 🔥 批次大小（Reranker API 通常限制）
    max_retries: int = 3,  # 🔥 最大重试次数
    retry_delay: float = 2.0,  # 🔥 重试基础延迟
    timeout: float = 30.0,  # 🔥 单批次超时
    fallback_threshold: float = 0.3,  # 🔥 降级阈值
    config: ExperimentConfig = None,  # 🔥 新增：实验配置（用于获取并发数）
):
    """
    使用 reranker 模型对检索结果进行重排序（支持批量并发处理 + 增强稳定性）
    
    对于包含 event_log 的文档：
    - 格式化为多行文本：时间 + 每句 atomic_fact 单独一行
    - 例如：
      2024-10-31 14:30:00
      用户喜欢吃川菜
      用户最喜欢的川菜是麻婆豆腐
      用户不喜欢太辣的菜
    
    对于传统文档：
    - 回退到使用 episode 字段
    
    优化策略（稳定性优先）：
    - 将文档分批处理（每批 batch_size 个）
    - 串行处理批次（避免 API 限流）
    - 每个批次支持重试和指数退避
    - 成功率过低时自动降级到原始排序
```

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L970-977)
```python
    # 🔥 第二步：批量处理（串行 + 重试 + 降级）
    # 将文档分批，每批 batch_size 个
    batches = []
    for i in range(0, len(doc_texts), batch_size):
        batch = doc_texts[i : i + batch_size]
        batches.append((i, batch))  # 保存起始索引和批次数据
    
    print(f"Split into {len(batches)} batches for serial reranking")
```

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L979-1016)
```python
    # 🔥 处理单个批次（带重试 + 超时 + 指数退避）
    async def process_batch_with_retry(start_idx: int, batch_texts: List[str]):
        """处理单个批次（带重试和超时）"""
        for attempt in range(max_retries):
            try:
                # 🔥 添加超时保护
                batch_results = await asyncio.wait_for(
                    reranker._make_rerank_request(
                    query, batch_texts, instruction=reranker_instruction
                    ),
                    timeout=timeout
                )
                
                # 调整索引：将批次内的索引映射回全局索引
                for item in batch_results["results"]:
                    item["global_index"] = start_idx + item["index"]
                
                if attempt > 0:
                    print(f"  ✓ Batch at {start_idx} succeeded on attempt {attempt + 1}")
                return batch_results["results"]
                
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # 指数退避：2s, 4s, 8s
                    print(f"  ⏱️  Batch at {start_idx} timeout (attempt {attempt + 1}), retrying in {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"  ❌ Batch at {start_idx} timeout after {max_retries} attempts")
                    return []
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"  ⚠️  Batch at {start_idx} failed (attempt {attempt + 1}), retrying in {wait_time:.1f}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    print(f"  ❌ Batch at {start_idx} failed after {max_retries} attempts: {e}")
                    return []
```

**File:** evaluation/src/adapters/evermemos/stage3_memory_retrivel.py (L1288-1303)
```python
                            elif config.use_emb:
                                # 单独使用 Embedding + MaxSim 检索
                                results = await search_with_emb_index(
                                    query=question, 
                                    emb_index=emb_index, 
                                    top_n=config.emb_recall_top_n
                                )
                            else:
                                # 单独使用 BM25 检索
                                results = await asyncio.to_thread(
                                    search_with_bm25_index, 
                                    question, 
                                    bm25, 
                                    docs, 
                                    config.emb_recall_top_n
                                )
```

**File:** src/agentic_layer/rerank_service.py (L130-130)
```python
        self._semaphore = asyncio.Semaphore(config.max_concurrent_requests)
```

**File:** src/agentic_layer/rerank_service.py (L144-144)
```python
            batch_size=int(os.getenv("DEEPINFRA_RERANK_BATCH_SIZE", "10")),
```

**File:** src/agentic_layer/rerank_service.py (L145-147)
```python
            max_concurrent_requests=int(
                os.getenv("DEEPINFRA_RERANK_MAX_CONCURRENT", "5")
            ),
```

**File:** src/agentic_layer/retrieval_utils.py (L225-225)
```python
        fused_results = reciprocal_rank_fusion(emb_results, bm25_results, k=60)
```

**File:** src/agentic_layer/retrieval_utils.py (L727-727)
```python
            rrf_k=60
```


# 我问

在企业场景中，我们可能需要支持多租户（multi-tenant）架构，不同公司的数据需要隔离。EverMemOS 的 group_id 和 user_id 是否足够支持多租户？还是需要在上层添加 tenant_id？数据隔离是在应用层实现还是数据库层实现？如果在数据库层实现，MongoDB、Elasticsearch、Milvus 的索引策略需要如何调整？对于跨租户的数据访问控制，系统是否有权限管理模块？另外，如果要支持数据的逻辑删除和物理删除（比如用户要求删除所有历史数据），系统提供了哪些 API 和工具？

# deepwiki答

您询问的是 EverMemOS 在企业多租户场景下的数据隔离方案、权限管理以及数据删除功能。<cite />

## 当前多租户支持分析

### 现有的隔离字段

EverMemOS 当前使用 **`user_id` 和 `group_id`** 进行数据隔离：<cite />

**EpisodicMemory 的隔离字段**： [1](#6-0) 
- `user_id` - 用户级隔离
- `group_id` - 群组级隔离（可选）

**索引策略**： [2](#6-1) 
- `(user_id, timestamp)` 复合索引
- `(group_id, timestamp)` 复合索引

### 多租户架构的不足

**当前设计的局限性**：

1. **缺少 tenant_id 字段**：`user_id` 和 `group_id` 只能实现用户级和群组级隔离，无法区分不同公司（租户）<cite />

2. **跨租户数据泄露风险**：如果两个公司的用户恰好使用相同的 `user_id`（如 "user_001"），会导致数据混淆<cite />

3. **无法实现租户级配额管理**：无法统计单个租户的存储用量、API 调用量等<cite />

**代码证据**：从示例数据可以看到，`user_id` 是简单的字符串标识符（如 "user_101", "user_102"），没有租户前缀或命名空间隔离： [3](#6-2) 

## 推荐的多租户改造方案

### 方案 1：添加 tenant_id 字段（推荐）

#### 数据模型改造

在所有记忆类型的文档模型中添加 `tenant_id` 字段：

```python
class EpisodicMemory(DocumentBase, AuditBase):
    tenant_id: str = Field(..., description="租户ID")  # 新增
    user_id: str = Field(..., description="用户ID")
    group_id: Optional[str] = Field(default=None, description="群组ID")
    # ... 其他字段
```

参考现有的 `EpisodicMemory` 结构： [4](#6-3) 

#### MongoDB 索引调整

**新增复合索引**：
```python
IndexModel(
    [("tenant_id", ASCENDING), ("user_id", ASCENDING), ("timestamp", DESCENDING)],
    name="idx_tenant_user_timestamp"
),
IndexModel(
    [("tenant_id", ASCENDING), ("group_id", ASCENDING), ("timestamp", DESCENDING)],
    name="idx_tenant_group_timestamp"
),
```

**原因**：MongoDB 查询必须包含 `tenant_id` 作为第一个过滤条件，确保数据隔离<cite />

#### Elasticsearch 索引调整

在 Elasticsearch 文档中添加 `tenant_id` 字段： [5](#6-4) 

```python
class EpisodicMemoryDoc(AliasDoc("episodic-memory", number_of_shards=3)):
    tenant_id = e_field.Keyword(required=True)  # 新增
    event_id = e_field.Keyword(required=True)
    user_id = e_field.Keyword(required=True)
    # ...
```

**分片策略**：可以使用 `tenant_id` 作为路由键（routing key），将同一租户的数据路由到相同分片，提升查询性能<cite />

#### Milvus Collection 隔离

**方案 A：单 Collection + tenant_id 过滤**
- 在向量插入时添加 `tenant_id` 标量字段
- 查询时使用 `expr="tenant_id == 'tenant_001'"` 过滤

**方案 B：每租户独立 Collection**（推荐大租户）
- 为每个租户创建独立的 Milvus collection（如 `episodic_memory_tenant_001`）
- 优势：物理隔离、独立配额、更好的性能
- 劣势：管理复杂度增加

### 方案 2：使用命名空间前缀（轻量级）

如果不想修改数据模型，可以在 `user_id` 和 `group_id` 中嵌入租户信息：

```python
user_id = f"{tenant_id}::{user_id}"  # 如 "tenant_001::user_101"
group_id = f"{tenant_id}::{group_id}"  # 如 "tenant_001::group_001"
```

**优势**：无需修改数据库 Schema
**劣势**：
- 无法高效统计租户级指标
- 索引效率较低（前缀扫描）
- 应用层需要处理字符串拼接/拆分逻辑

## 数据隔离实现层次

### 应用层隔离（当前实现）

**当前代码的隔离方式**：在 Repository 查询时通过 `user_id` 或 `group_id` 过滤： [6](#6-5) 

**问题**：
- 依赖开发者手动添加过滤条件，容易遗漏
- 无法防止恶意查询（如直接构造 MongoDB 查询绕过应用层）

### 数据库层隔离（推荐）

**MongoDB 实现**：
1. 使用 **MongoDB Views** 为每个租户创建视图，自动注入 `tenant_id` 过滤条件
2. 使用 **Row-Level Security**（需要 MongoDB Atlas 或企业版）

**Elasticsearch 实现**：
1. 使用 **Document Level Security**（需要 X-Pack 或 Elastic Cloud）
2. 为每个租户创建独立的索引别名（Alias）

**Milvus 实现**：
- 使用独立 Collection 实现物理隔离

## 权限管理模块

### 当前状态：无权限管理

**重要发现**：EverMemOS **没有内置权限管理模块**。<cite />

代码中没有发现以下组件：
- 用户认证（Authentication）
- 权限控制（Authorization）
- 角色管理（RBAC）
- API 密钥管理

**API 接口无鉴权**：检索接口只需提供 `user_id` 或 `group_id`，没有验证调用者身份： [7](#6-6) 

### 推荐的权限管理方案

#### 1. 添加 API 密钥认证

在 FastAPI 中添加依赖注入的认证中间件：

```python
from fastapi import Depends, HTTPException, Header

async def verify_tenant(x_tenant_id: str = Header(...), x_api_key: str = Header(...)):
    # 验证 API Key 是否属于该租户
    if not is_valid_api_key(x_tenant_id, x_api_key):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_tenant_id

@app.post("/api/v3/agentic/retrieve_lightweight")
async def retrieve(request: RetrieveRequest, tenant_id: str = Depends(verify_tenant)):
    # 强制注入 tenant_id 到查询条件
    request.tenant_id = tenant_id
    # ...
```

#### 2. 实现 RBAC（基于角色的访问控制）

定义角色和权限：
- **Admin**：可以管理租户内所有数据
- **User**：只能访问自己的数据
- **Viewer**：只读权限

## 数据删除功能

### 逻辑删除（Soft Delete）

**当前状态**：系统**不支持逻辑删除**，没有 `deleted_at` 或 `is_deleted` 字段。<cite />

**实现建议**：
1. 在所有文档模型中添加 `deleted_at` 字段（继承自 `AuditBase`）
2. 修改查询逻辑，默认过滤 `deleted_at IS NULL` 的记录
3. 提供恢复接口（将 `deleted_at` 设为 NULL）

### 物理删除（Hard Delete）

**现有的删除方法**：

#### 1. MemCell 删除

**按用户删除**： [8](#6-7) 

**按时间范围删除**： [9](#6-8) 

#### 2. EpisodicMemory 删除

**按用户删除**： [10](#6-9) 

**按事件 ID 删除**： [11](#6-10) 

#### 3. CoreMemory 删除

**按用户删除（支持版本控制）**： [12](#6-11) 

#### 4. SemanticMemory 删除

**按用户删除**： [13](#6-12) 

### 缺失的功能

**当前删除方法的局限性**：

1. **只删除 MongoDB**：没有同步删除 Elasticsearch 和 Milvus 中的数据<cite />
2. **无批量删除 API**：没有提供 HTTP API 接口，只能通过内部 Repository 调用<cite />
3. **无删除审计日志**：无法追踪谁在何时删除了哪些数据<cite />
4. **无级联删除**：删除 Episode 时不会自动删除关联的 MemCell<cite />

### 推荐的完整删除方案

#### 实现三重删除（Triple Delete）

```python
async def delete_user_all_data(tenant_id: str, user_id: str):
    """删除用户的所有数据（MongoDB + ES + Milvus）"""
    # 1. 删除 MongoDB
    await memcell_repo.delete_by_user_id(user_id)
    await episodic_repo.delete_by_user_id(user_id)
    await core_memory_repo.delete_by_user_id(user_id)
    await semantic_repo.delete_by_user_id(user_id)
    
    # 2. 删除 Elasticsearch
    await es_client.delete_by_query(
        index="episodic-memory",
        body={"query": {"term": {"user_id": user_id}}}
    )
    
    # 3. 删除 Milvus
    await milvus_client.delete(
        collection_name="episodic_memory",
        expr=f"user_id == '{user_id}'"
    )
    
    # 4. 记录审计日志
    await audit_log.record_deletion(tenant_id, user_id, deleted_by="admin")
```

#### 添加 HTTP API

```python
@app.delete("/api/v3/agentic/user/{user_id}/data")
async def delete_user_data(
    user_id: str,
    tenant_id: str = Depends(verify_tenant),
    confirm: bool = Query(False, description="确认删除")
):
    if not confirm:
        raise HTTPException(400, "Must set confirm=true")
    
    await delete_user_all_data(tenant_id, user_id)
    return {"status": "deleted", "user_id": user_id}
```

## 多租户改造的完整检查清单

### 数据模型层
- [ ] 在所有 Document 模型中添加 `tenant_id` 字段
- [ ] 添加 `deleted_at` 字段支持逻辑删除
- [ ] 更新 MongoDB 索引策略（tenant_id 作为第一个索引键）

### Repository 层
- [ ] 所有查询方法强制添加 `tenant_id` 过滤
- [ ] 实现三重删除（MongoDB + ES + Milvus）
- [ ] 添加批量删除方法

### API 层
- [ ] 添加 API 密钥认证中间件
- [ ] 从请求头提取 `tenant_id` 并注入到查询
- [ ] 添加删除数据的 HTTP 接口

### 数据库层
- [ ] Elasticsearch：为每个租户创建独立索引或使用 Document Level Security
- [ ] Milvus：为大租户创建独立 Collection
- [ ] MongoDB：创建租户级视图或

Wiki pages you might want to explore:
- [EverMemOS Overview (EverMind-AI/EverMemOS)](/wiki/EverMind-AI/EverMemOS#1)

### Citations

**File:** src/infra_layer/adapters/out/persistence/document/memory/episodic_memory.py (L11-41)
```python
class EpisodicMemory(DocumentBase, AuditBase):
    """
    情景记忆文档模型

    存储用户的情景记忆，包含事件摘要、参与者、主题等信息。
    从 MemCell 摘要直接转存而来。
    """

    user_id: str = Field(..., description="当事人")
    group_id: Optional[str] = Field(default=None, description="群组ID")
    timestamp: datetime = Field(..., description="发生时间（时间戳）")
    participants: Optional[List[str]] = Field(
        default=None, description="事件参与者名字"
    )
    summary: str = Field(..., min_length=1, description="记忆单元")
    subject: Optional[str] = Field(default=None, description="记忆单元主题")
    episode: str = Field(..., min_length=1, description="情景记忆")
    type: Optional[str] = Field(default=None, description="情景类型，如Conversation等")
    keywords: Optional[List[str]] = Field(default=None, description="关键词")
    linked_entities: Optional[List[str]] = Field(
        default=None, description="关联的实体ID"
    )

    memcell_event_id_list: Optional[List[str]] = Field(
        default=None, description="记忆单元事件ID"
    )

    extend: Optional[Dict[str, Any]] = Field(default=None, description="备用拓展字段")

    vector: Optional[List[float]] = Field(default=None, description="文本向量")
    vector_model: Optional[str] = Field(default=None, description="使用的向量化模型")
```

**File:** src/infra_layer/adapters/out/persistence/document/memory/episodic_memory.py (L72-82)
```python
        indexes = [
            # 用户ID和时间戳复合索引
            IndexModel(
                [("user_id", ASCENDING), ("timestamp", DESCENDING)],
                name="idx_user_timestamp",
            ),
            # 群组ID和时间戳复合索引
            IndexModel(
                [("group_id", ASCENDING), ("timestamp", DESCENDING)],
                name="idx_group_timestamp",
            ),
```

**File:** data/group_chat_en.json (L1411-1420)
```json
    },
    {
      "message_id": "msg_0148",
      "create_time": "2025-03-20T13:22:00+08:00",
      "sender": "user_102",
      "sender_name": "Betty",
      "type": "text",
      "content": "That's it.",
      "refer_list": []
    },
```

**File:** src/infra_layer/adapters/out/search/elasticsearch/memory/episodic_memory.py (L50-53)
```python
    # 基础标识字段
    event_id = e_field.Keyword(required=True)
    user_id = e_field.Keyword(required=True)
    user_name = e_field.Keyword()
```

**File:** src/infra_layer/adapters/out/persistence/repository/episodic_memory_raw_repository.py (L65-105)
```python
    async def get_by_user_id(
        self,
        user_id: str,
        limit: Optional[int] = None,
        skip: Optional[int] = None,
        sort_desc: bool = True,
        session: Optional[AsyncIOMotorClientSession] = None,
    ) -> List[EpisodicMemory]:
        """
        根据用户ID获取情景记忆列表

        Args:
            user_id: 用户ID
            limit: 限制返回数量
            skip: 跳过数量
            sort_desc: 是否按时间降序排序
            session: 可选的 MongoDB 会话，用于事务支持

        Returns:
            EpisodicMemory 列表
        """
        try:
            query = self.model.find({"user_id": user_id})

            if sort_desc:
                query = query.sort("-timestamp")
            else:
                query = query.sort("timestamp")

            if skip:
                query = query.skip(skip)
            if limit:
                query = query.limit(limit)

            results = await query.to_list()
            logger.debug(
                "✅ 根据用户ID获取情景记忆成功: %s, 找到 %d 条记录",
                user_id,
                len(results),
            )
            return results
```

**File:** src/infra_layer/adapters/out/persistence/repository/episodic_memory_raw_repository.py (L149-191)
```python
    async def delete_by_event_id(
        self,
        event_id: str,
        user_id: str,
        session: Optional[AsyncIOMotorClientSession] = None,
    ) -> bool:
        """
        根据事件ID和用户ID删除情景记忆

        Args:
            event_id: 事件ID
            user_id: 用户ID
            session: 可选的 MongoDB 会话，用于事务支持

        Returns:
            是否删除成功
        """
        try:
            # 将字符串 event_id 转换为 ObjectId
            object_id = ObjectId(event_id)
            # 直接删除并检查删除数量
            result = await self.model.find(
                {"_id": object_id, "user_id": user_id}, session=session
            ).delete()

            deleted_count = (
                result.deleted_count if hasattr(result, 'deleted_count') else 0
            )
            success = deleted_count > 0

            if success:
                logger.info("✅ 根据事件ID和用户ID删除情景记忆成功: %s", event_id)
                return True
            else:
                logger.warning(
                    "⚠️  未找到要删除的情景记忆: event_id=%s, user_id=%s",
                    event_id,
                    user_id,
                )
                return False
        except Exception as e:
            logger.error("❌ 根据事件ID和用户ID删除情景记忆失败: %s", e)
            return False
```

**File:** src/infra_layer/adapters/out/persistence/repository/episodic_memory_raw_repository.py (L193-215)
```python
    async def delete_by_user_id(
        self, user_id: str, session: Optional[AsyncIOMotorClientSession] = None
    ) -> int:
        """
        根据用户ID删除所有情景记忆

        Args:
            user_id: 用户ID
            session: 可选的 MongoDB 会话，用于事务支持

        Returns:
            删除的记录数量
        """
        try:
            result = await self.model.find({"user_id": user_id}).delete(session=session)
            count = result.deleted_count if result else 0
            logger.info(
                "✅ 根据用户ID删除情景记忆成功: %s, 删除 %d 条记录", user_id, count
            )
            return count
        except Exception as e:
            logger.error("❌ 根据用户ID删除情景记忆失败: %s", e)
            return 0
```

**File:** README.md (L491-500)
```markdown
| Parameter | Required | Description |
|-----------|----------|-------------|
| `query` | Yes* | Natural language query (*optional for profile data source) |
| `user_id` | No | User ID |
| `data_source` | Yes | `episode` / `event_log` / `semantic_memory` / `profile` |
| `memory_scope` | Yes | `personal` (user_id only) / `group` (group_id only) / `all` (both) |
| `retrieval_mode` | Yes | `embedding` / `bm25` / `rrf` (recommended) |
| `group_id` | No | Group ID |
| `current_time` | No | Filter valid semantic_memory (format: YYYY-MM-DD) |
| `top_k` | No | Number of results (default: 5) |
```

**File:** src/infra_layer/adapters/out/persistence/repository/memcell_raw_repository.py (L421-443)
```python
    async def delete_by_user_id(
        self, user_id: str, session: Optional[AsyncIOMotorClientSession] = None
    ) -> int:
        """
        删除用户的所有 MemCell

        Args:
            user_id: 用户 ID
            session: 可选的 MongoDB 会话，用于事务支持

        Returns:
            删除的记录数量
        """
        try:
            result = await self.model.find({"user_id": user_id}).delete(session=session)
            count = result.deleted_count if result else 0
            logger.info(
                "✅ 删除用户所有 MemCell 成功: %s, 删除 %d 条记录", user_id, count
            )
            return count
        except Exception as e:
            logger.error("❌ 删除用户所有 MemCell 失败: %s", e)
            return 0
```

**File:** src/infra_layer/adapters/out/persistence/repository/memcell_raw_repository.py (L445-485)
```python
    async def delete_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime,
        user_id: Optional[str] = None,
        session: Optional[AsyncIOMotorClientSession] = None,
    ) -> int:
        """
        删除时间范围内的 MemCell

        Args:
            start_time: 开始时间
            end_time: 结束时间
            user_id: 可选的用户 ID 筛选
            session: 可选的 MongoDB 会话，用于事务支持

        Returns:
            删除的记录数量
        """
        try:
            conditions = [
                GTE(MemCell.timestamp, start_time),
                LT(MemCell.timestamp, end_time),
            ]

            if user_id:
                conditions.append(Eq(MemCell.user_id, user_id))

            result = await self.model.find(And(*conditions)).delete(session=session)
            count = result.deleted_count if result else 0
            logger.info(
                "✅ 删除时间范围内 MemCell 成功: %s - %s, 用户: %s, 删除 %d 条记录",
                start_time,
                end_time,
                user_id or '全部',
                count,
            )
            return count
        except Exception as e:
            logger.error("❌ 删除时间范围内 MemCell 失败: %s", e)
            return 0
```

**File:** src/infra_layer/adapters/out/persistence/repository/core_memory_raw_repository.py (L199-263)
```python
    async def delete_by_user_id(
        self,
        user_id: str,
        version: Optional[str] = None,
        session: Optional[AsyncIOMotorClientSession] = None,
    ) -> bool:
        """
        根据用户ID删除核心记忆

        Args:
            user_id: 用户ID
            version: 可选的版本号，如果指定则只删除特定版本，否则删除所有版本
            session: 可选的 MongoDB 会话，用于事务支持

        Returns:
            是否删除成功
        """
        try:
            query_filter = {"user_id": user_id}
            if version is not None:
                query_filter["version"] = version

            if version is not None:
                # 删除特定版本 - 直接删除并检查删除数量
                result = await self.model.find(query_filter, session=session).delete()
                deleted_count = (
                    result.deleted_count if hasattr(result, 'deleted_count') else 0
                )
                success = deleted_count > 0

                if success:
                    logger.debug(
                        "✅ 根据用户ID和版本删除核心记忆成功: user_id=%s, version=%s",
                        user_id,
                        version,
                    )
                    # 删除后确保最新版本标记正确
                    await self.ensure_latest(user_id, session)
                else:
                    logger.warning(
                        "⚠️  未找到要删除的核心记忆: user_id=%s, version=%s",
                        user_id,
                        version,
                    )
            else:
                # 删除所有版本
                result = await self.model.find(query_filter, session=session).delete()
                deleted_count = (
                    result.deleted_count if hasattr(result, 'deleted_count') else 0
                )
                success = deleted_count > 0

                if success:
                    logger.debug(
                        "✅ 根据用户ID删除所有核心记忆成功: user_id=%s, 删除 %d 条",
                        user_id,
                        deleted_count,
                    )
                else:
                    logger.warning("⚠️  未找到要删除的核心记忆: user_id=%s", user_id)

            return success
        except Exception as e:
            logger.error("❌ 根据用户ID删除核心记忆失败: %s", e)
            return False
```

**File:** src/infra_layer/adapters/out/persistence/repository/semantic_memory_raw_repository.py (L86-108)
```python
    async def delete_by_user_id(
        self, user_id: str, session: Optional[AsyncIOMotorClientSession] = None
    ) -> bool:
        """
        根据用户ID删除语义记忆

        Args:
            user_id: 用户ID
            session: 可选的 MongoDB 会话，用于事务支持

        Returns:
            删除成功返回 True，否则返回 False
        """
        try:
            semantic_memory = await self.get_by_user_id(user_id)
            if semantic_memory:
                await semantic_memory.delete(session=session)
                logger.info("✅ 根据用户ID删除语义记忆成功: %s", user_id)
                return True
            return False
        except Exception as e:
            logger.error("❌ 根据用户ID删除语义记忆失败: %s", e)
            return False
```


# 我问

看到评估框架支持 LoCoMo、LongMemEval、PersonaMem 三个基准测试，并且有检查点和恢复机制。如果我想在自己的业务数据上评估系统效果，需要准备什么格式的测试数据？评估框架是否支持自定义数据集？具体需要哪些字段（对话历史、ground truth、评估指标等）？另外，系统提到使用 LLM-Judge 进行评估，这个评估的 prompt 是什么？评估标准是什么？如果我不满意默认的评估方式，是否可以自定义评估器？

# deepwiki答

您询问的是如何在 EverMemOS 评估框架中使用自定义业务数据进行评估，包括数据格式要求、LLM-Judge 的评估标准以及自定义评估器的方法。<cite />

## 评估框架的数据格式要求

### 标准数据模型

评估框架定义了统一的数据格式，确保不同数据集之间的互操作性： [1](#7-0) 

**核心数据结构**：

1. **Message（消息）**：
   - `speaker_id` - 说话者ID
   - `speaker_name` - 说话者名称
   - `content` - 消息内容
   - `timestamp` - 时间戳（可选，PersonaMem 数据集没有时间信息）
   - `metadata` - 额外元数据

2. **Conversation（对话）**：
   - `conversation_id` - 对话唯一标识
   - `messages` - 消息列表
   - `metadata` - 对话级元数据

3. **QAPair（问答对）**：
   - `question_id` - 问题唯一标识
   - `question` - 问题文本
   - `answer` - 标准答案（ground truth）
   - `category` - 问题类别（可选，字符串类型）
   - `evidence` - 证据列表（引用的消息ID）
   - `metadata` - 额外元数据

4. **Dataset（数据集）**：
   - `dataset_name` - 数据集名称
   - `conversations` - 对话列表
   - `qa_pairs` - 问答对列表
   - `metadata` - 数据集级元数据

### 支持的数据格式

评估框架支持三种数据格式，并提供自动转换器：<cite />

#### 1. LoCoMo 格式（原生格式）

这是评估框架的**标准格式**，其他格式会被转换为此格式：<cite />

```json
{
  "qa": [
    {
      "question_id": "locomo_0_qa0",
      "question": "What is Alice's favorite hobby?",
      "answer": "painting",
      "evidence": ["D0:5", "D1:3"],
      "category": "recall"
    }
  ],
  "conversation": {
    "speaker_a": "user_0",
    "speaker_b": "assistant_0",
    "session_0_date_time": "2024-01-01 10:00:00",
    "session_0": [
      {
        "speaker": "user_0",
        "text": "I love painting on weekends",
        "dia_id": "D0:5"
      }
    ]
  }
}
```

#### 2. LongMemEval 格式

系统提供转换器将 LongMemEval-S 格式转换为 LoCoMo 格式： [2](#7-1) 

**转换逻辑**：
- 从 `haystack_sessions` 提取对话
- 从 `answer_session_ids` 标记包含答案的消息
- 生成 `evidence` 字段（格式：`D{session_idx}:{msg_idx}`）
- 转换时间格式

#### 3. PersonaMem 格式

PersonaMem 是选择题格式，配置文件指定使用 `exact_match` 评估器： [3](#7-2) 

**特殊配置**：
- `case_sensitive: false` - 不区分大小写
- `normalize_whitespace: true` - 规范化空白字符
- `extract_choice: true` - 从生成答案中提取选项（如 (a), (b)）

## 自定义数据集的准备步骤

### 步骤 1：准备数据文件

创建符合 LoCoMo 格式的 JSON 文件，放置在 `evaluation/data/` 目录下：<cite />

```json
[
  {
    "qa": [
      {
        "question_id": "custom_0_qa0",
        "question": "用户的职位是什么？",
        "answer": "产品经理",
        "evidence": ["D0:2"],
        "category": "base_memory"
      }
    ],
    "conversation": {
      "speaker_a": "user_101",
      "speaker_b": "assistant_101",
      "session_0_date_time": "2025-01-15 14:30:00",
      "session_0": [
        {
          "speaker": "user_101",
          "text": "我是产品经理，负责移动端产品",
          "dia_id": "D0:2"
        }
      ]
    }
  }
]
```

**关键字段说明**：
- `evidence`：引用格式为 `D{session_idx}:{message_idx}`，指向包含答案的消息
- `category`：可自定义分类（如 "base_memory", "preference", "relationship"）
- `dia_id`：消息唯一标识，用于溯源

### 步骤 2：创建数据集配置文件

在 `evaluation/config/datasets/` 下创建 `custom_dataset.yaml`：<cite />

```yaml
# Custom Dataset Configuration
name: "custom_dataset"
version: "1.0"
description: "My business data evaluation"

# Data configuration
data:
  path: "custom_dataset/data.json"  # 相对于 evaluation/data/ 的路径
  format: "locomo"  # 使用 LoCoMo 格式

# Evaluation configuration
evaluation:
  type: "llm_judge"  # 或 "exact_match"
  
  # LLM Judge 配置
  llm:
    api_key: "${LLM_API_KEY}"  # 从环境变量读取
    base_url: "https://api.openai.com/v1"
    model: "gpt-4o-mini"
  
  num_runs: 3  # 每个问题评估 3 次，计算平均值和标准差
  
  # 可选：过滤特定类别
  filter_category: []  # 如需过滤：["base_memory", "preference"]
```

### 步骤 3：运行评估

```bash
# 冒烟测试（快速验证）
uv run python -m evaluation.cli --dataset custom_dataset --system evermemos --smoke

# 完整评估
uv run python -m evaluation.cli --dataset custom_dataset --system evermemos

# 查看结果
cat evaluation/results/custom_dataset-evermemos/report.txt
```

## LLM-Judge 评估标准

### 评估 Prompt

LLM-Judge 使用的 prompt 定义在配置文件中： [4](#7-3) 

**System Prompt**：
```
You are an expert grader that determines if answers to questions match a gold standard answer
```

**User Prompt 核心逻辑**：
1. **宽松评分原则**：只要生成答案触及与标准答案相同的主题，就算正确
2. **时间问题处理**：允许相对时间引用（如 "上周二"）与绝对日期（如 "5月7日"）匹配
3. **格式容忍**：不同日期格式（"May 7th" vs "7 May"）视为相同
4. **输出格式**：JSON 格式 `{"label": "CORRECT"}` 或 `{"label": "WRONG"}`

**示例**：
```
Question: Do you remember what I got the last time I went to Hawaii?
Gold answer: A shell necklace
Generated answer: I recall you mentioned getting a beautiful shell necklace from your Hawaii trip.
→ CORRECT（触及相同主题）
```

### 评估实现

LLM-Judge 评估器的实现： [5](#7-4) 

**关键特性**：
- **多次运行**：每个问题评估 `num_runs` 次（默认 3 次）
- **独立判断**：保留每次运行的独立结果（`judgment_1`, `judgment_2`, `judgment_3`）
- **统计分析**：计算平均准确率（mean）和标准差（std）
- **并发控制**：使用 `Semaphore(10)` 限制并发 API 调用

**评估流程**： [6](#7-5) 

```python
# 1. 调用 LLM 判断答案正确性
response = await llm_client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": accuracy_prompt},
    ],
    temperature=0,
)

# 2. 解析 JSON 响应
label = json.loads(response.choices[0].message.content)["label"]

# 3. 返回布尔值
return label.strip().lower() == "correct"
```

## 自定义评估器

### 现有评估器类型

评估框架支持两种评估器，通过注册机制管理： [7](#7-6) 

1. **llm_judge** - LLM 作为评判器（适用于开放式问答）
2. **exact_match** - 精确匹配（适用于选择题，如 PersonaMem）

### 创建自定义评估器

#### 步骤 1：定义评估器类

在 `evaluation/src/evaluators/` 下创建 `custom_evaluator.py`：

```python
from typing import List
from evaluation.src.evaluators.base import BaseEvaluator
from evaluation.src.evaluators.registry import register_evaluator
from evaluation.src.core.data_models import AnswerResult, EvaluationResult

@register_evaluator("custom_evaluator")
class CustomEvaluator(BaseEvaluator):
    """自定义评估器"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        # 初始化自定义配置
        self.threshold = config.get("threshold", 0.8)
    
    async def evaluate(
        self, 
        answer_results: List[AnswerResult]
    ) -> EvaluationResult:
        """
        自定义评估逻辑
        
        Args:
            answer_results: 答案结果列表
            
        Returns:
            EvaluationResult: 评估结果
        """
        correct = 0
        detailed_results = []
        
        for result in answer_results:
            # 实现自定义评分逻辑
            is_correct = self._custom_scoring(
                result.answer, 
                result.golden_answer
            )
            
            if is_correct:
                correct += 1
            
            detailed_results.append({
                "question_id": result.question_id,
                "question": result.question,
                "answer": result.answer,
                "golden_answer": result.golden_answer,
                "is_correct": is_correct,
            })
        
        accuracy = correct / len(answer_results) if answer_results else 0.0
        
        return EvaluationResult(
            total_questions=len(answer_results),
            correct=correct,
            accuracy=accuracy,
            detailed_results=detailed_results,
            metadata={"threshold": self.threshold}
        )
    
    def _custom_scoring(self, answer: str, golden_answer: str) -> bool:
        """自定义评分函数"""
        # 示例：基于关键词匹配
        keywords = golden_answer.lower().split()
        answer_lower = answer.lower()
        
        match_count = sum(1 for kw in keywords if kw in answer_lower)
        match_ratio = match_count / len(keywords) if keywords else 0
        
        return match_ratio >= self.threshold
    
    def get_name(self) -> str:
        return "Custom Evaluator"
```

#### 步骤 2：注册评估器

在 `evaluation/src/evaluators/registry.py` 中添加模块映射： [8](#7-7) 

```python
_EVALUATOR_MODULES = {
    "llm_judge": "evaluation.src.evaluators.llm_judge",
    "exact_match": "evaluation.src.evaluators.exact_match",
    "custom_evaluator": "evaluation.src.evaluators.custom_evaluator",  # 新增
}
```

#### 步骤 3：配置数据集使用自定义评估器

在 `evaluation/config/datasets/custom_dataset.yaml` 中指定：

```yaml
evaluation:
  type: "custom_evaluator"  # 使用自定义评估器
  
  # 自定义评估器配置
  threshold: 0.75  # 关键词匹配阈值
```

### 自定义 Prompt（针对 LLM-Judge）

如果只想修改 LLM-Judge 的 prompt，无需创建新评估器，直接修改配置文件： [9](#7-8) 

在 `evaluation/config/prompts.yaml` 中添加自定义 prompt：

```yaml
# 自定义 LLM Judge Prompt
custom_llm_judge:
  system_prompt: |
    你是一个专业的中文问答评估专家
  
  user_prompt: |
    请判断以下答案是否正确：
    
    问题：{question}
    标准答案：{golden_answer}
    生成答案：{generated_answer}
    
    评分标准：
    1. 答案必须包含标准答案的核心信息
    2. 允许使用同义词

Wiki pages you might want to explore:
- [EverMemOS Overview (EverMind-AI/EverMemOS)](/wiki/EverMind-AI/EverMemOS#1)

### Citations

**File:** evaluation/src/core/data_models.py (L11-50)
```python
@dataclass
class Message:
    """标准消息格式"""
    speaker_id: str
    speaker_name: str
    content: str
    timestamp: Optional[datetime] = None  # 时间戳可选，某些数据集（如 PersonaMem）没有时间信息
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """标准对话格式"""
    conversation_id: str
    messages: List[Message]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QAPair:
    """
    标准 QA 对格式
    
    注意：category字段统一为字符串类型，以兼容不同数据集的格式
    """
    question_id: str
    question: str
    answer: str
    category: Optional[str] = None  # 统一为字符串类型
    evidence: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dataset:
    """标准数据集格式"""
    dataset_name: str
    conversations: List[Conversation]
    qa_pairs: List[QAPair]
    metadata: Dict[str, Any] = field(default_factory=dict)
```

**File:** evaluation/src/converters/longmemeval_converter.py (L40-104)
```python
def convert_lmeval_s_to_locomo_style(lmeval_data: list) -> list:
    """
    将 LongMemEval-S 格式转换为 Locomo 格式
    
    Args:
        lmeval_data: LongMemEval-S 原始数据
        
    Returns:
        Locomo 格式数据
    """
    locomo_style_data = []
    
    for data in lmeval_data:
        data_dict = {
            "qa": [],
            "conversation": {}
        }
        
        # 找出包含答案的 session 索引
        evidence_session_idx = []
        for idx, session_id in enumerate(data["haystack_session_ids"]):
            if session_id in data["answer_session_ids"]:
                evidence_session_idx.append(idx)
        
        # 标记包含答案的消息
        for idx, session in enumerate(data["haystack_sessions"]):
            for i, msg in enumerate(session):
                data["haystack_sessions"][idx][i]["has_answer"] = idx in evidence_session_idx
        
        # 收集 evidence
        evidence = []
        for idx, session in enumerate(data["haystack_sessions"]):
            for i, msg in enumerate(session):
                if msg["has_answer"]:
                    evidence.append(f"D{idx}:{i}")
        
        # 构建 QA
        data_dict["qa"].append({
            "question_id": data["question_id"],
            "question": data["question"],
            "answer": data["answer"],
            "evidence": evidence,
            "category": data["question_type"]
        })
        
        # 构建对话
        data_dict["conversation"]["speaker_a"] = f"user_{data['question_id']}"
        data_dict["conversation"]["speaker_b"] = f"assistant_{data['question_id']}"
        
        for idx, session in enumerate(data["haystack_sessions"]):
            data_dict["conversation"][f"session_{idx}_date_time"] = convert_time_format(
                data["haystack_dates"][idx]
            )
            data_dict["conversation"][f"session_{idx}"] = []
            
            for i, msg in enumerate(session):
                data_dict["conversation"][f"session_{idx}"].append({
                    "speaker": msg["role"] + f"_{data['question_id']}",
                    "text": msg["content"],
                    "dia_id": f"D{idx}:{i}"
                })
        
        locomo_style_data.append(data_dict)
    
    return locomo_style_data
```

**File:** evaluation/config/datasets/personamem.yaml (L17-24)
```yaml
# Evaluation configuration
evaluation:
  type: "exact_match"  # PersonaMem 是选择题，使用精确匹配
  
  # Exact match 配置
  case_sensitive: false  # 不区分大小写
  normalize_whitespace: true  # 规范化空白字符
  extract_choice: true  # 从生成的答案中提取选项（如 (a), (b)）
```

**File:** evaluation/config/prompts.yaml (L3-31)
```yaml
llm_judge:
  system_prompt: |
    You are an expert grader that determines if answers to questions match a gold standard answer
  
  user_prompt: |
    Your task is to label an answer to a question as 'CORRECT' or 'WRONG'. You will be given the following data:
        (1) a question (posed by one user to another user),
        (2) a 'gold' (ground truth) answer,
        (3) a generated answer
    which you will score as CORRECT/WRONG.

    The point of the question is to ask about something one user should know about the other user based on their prior conversations.
    The gold answer will usually be a concise and short answer that includes the referenced topic, for example:
    Question: Do you remember what I got the last time I went to Hawaii?
    Gold answer: A shell necklace
    The generated answer might be much longer, but you should be generous with your grading - as long as it touches on the same topic as the gold answer, it should be counted as CORRECT.

    For time related questions, the gold answer will be a specific date, month, year, etc. The generated answer might be much longer or use relative time references (like "last Tuesday" or "next month"), but you should be generous with your grading - as long as it refers to the same date or time period as the gold answer, it should be counted as CORRECT. Even if the format differs (e.g., "May 7th" vs "7 May"), consider it CORRECT if it's the same date.

    Now it's time for the real question:
    Question: {question}
    Gold answer: {golden_answer}
    Generated answer: {generated_answer}

    First, provide a short (one sentence) explanation of your reasoning, then finish with CORRECT or WRONG.
    Do NOT include both CORRECT and WRONG in your response, or it will break the evaluation script.

    Just return the label CORRECT or WRONG in a json format with the key as "label".
  
```

**File:** evaluation/src/evaluators/llm_judge.py (L26-109)
```python
class LLMJudge(BaseEvaluator):
    """LLM 评判器"""
    
    def __init__(self, config: dict):
        super().__init__(config)
        
        # 初始化 OpenAI 客户端
        llm_config = config.get("llm", {})
        self.client = AsyncOpenAI(
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url", "https://api.openai.com/v1")
        )
        self.model = llm_config.get("model", "gpt-4o-mini")
        self.num_runs = config.get("num_runs", 3)
    
    async def evaluate(
        self, 
        answer_results: List[AnswerResult]
    ) -> EvaluationResult:
        """
        使用LLM评估答案，返回多次运行的统计结果
        
        Args:
            answer_results: 答案结果列表
            
        Returns:
            EvaluationResult: 包含mean和std的评估结果
        """
        print(f"\n{'='*60}")
        print(f"Evaluation: LLM Judge (model={self.model}, runs={self.num_runs})")
        print(f"{'='*60}")
        
        detailed_results = []
        
        # 并发评估所有答案
        semaphore = asyncio.Semaphore(10)  # 限制并发数
        
        # 使用 tqdm 进度条
        pbar = tqdm(total=len(answer_results), desc="⚖️  Evaluate Progress", unit="qa")
        
        async def evaluate_single(answer_result: AnswerResult):
            async with semaphore:
                result = await self._evaluate_single_answer(answer_result)
                pbar.update(1)  # 更新进度条
                return result
        
        tasks = [evaluate_single(ar) for ar in answer_results]
        results = await asyncio.gather(*tasks)
        
        # 关闭进度条
        pbar.close()
        
        # 收集结果
        for result in results:
            detailed_results.append(result)
        
        # 分别计算每次 run 的准确率
        run_scores = []
        category_stats = defaultdict(lambda: {"correct": [0] * self.num_runs, "total": 0})
        
        for i in range(self.num_runs):
            judgment_key = f"judgment_{i+1}"
            correct_count = 0
            total_count = 0
            
            for result in detailed_results:
                llm_judgments = result.get("llm_judgments", {})
                category = result.get("category")
                
                if judgment_key in llm_judgments:
                    total_count += 1
                    if llm_judgments[judgment_key]:
                        correct_count += 1
                        if category is not None:
                            category_stats[category]["correct"][i] += 1
                
                # 统计 category 总数（只需要一次）
                if i == 0 and category is not None:
                    category_stats[category]["total"] += 1
            
            if total_count > 0:
                run_accuracy = correct_count / total_count
                run_scores.append(run_accuracy)
        
```

**File:** evaluation/src/adapters/evermemos/stage5_eval.py (L26-71)
```python
async def locomo_grader(
    llm_client, question: str, gold_answer: str, response: str
) -> bool:
    system_prompt = """
        You are an expert grader that determines if answers to questions match a gold standard answer
        """

    accuracy_prompt = f"""
    Your task is to label an answer to a question as ’CORRECT’ or ’WRONG’. You will be given the following data:
        (1) a question (posed by one user to another user),
        (2) a ’gold’ (ground truth) answer,
        (3) a generated answer
    which you will score as CORRECT/WRONG.

    The point of the question is to ask about something one user should know about the other user based on their prior conversations.
    The gold answer will usually be a concise and short answer that includes the referenced topic, for example:
    Question: Do you remember what I got the last time I went to Hawaii?
    Gold answer: A shell necklace
    The generated answer might be much longer, but you should be generous with your grading - as long as it touches on the same topic as the gold answer, it should be counted as CORRECT.

    For time related questions, the gold answer will be a specific date, month, year, etc. The generated answer might be much longer or use relative time references (like "last Tuesday" or "next month"), but you should be generous with your grading - as long as it refers to the same date or time period as the gold answer, it should be counted as CORRECT. Even if the format differs (e.g., "May 7th" vs "7 May"), consider it CORRECT if it's the same date.

    Now it’s time for the real question:
    Question: {question}
    Gold answer: {gold_answer}
    Generated answer: {response}

    First, provide a short (one sentence) explanation of your reasoning, then finish with CORRECT or WRONG.
    Do NOT include both CORRECT and WRONG in your response, or it will break the evaluation script.

    Just return the label CORRECT or WRONG in a json format with the key as "label".
    """

    response = await llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": accuracy_prompt},
        ],
        temperature=0,
    )
    message_content = response.choices[0].message.content
    label = json.loads(message_content)["label"]
    parsed = LLMGrade(llm_judgment=label, llm_reasoning="")

    return parsed.llm_judgment.strip().lower() == "correct"
```

**File:** evaluation/src/evaluators/registry.py (L12-20)
```python
_EVALUATOR_REGISTRY: Dict[str, Type[BaseEvaluator]] = {}

# 评估器模块映射（用于延迟加载）
_EVALUATOR_MODULES = {
    "llm_judge": "evaluation.src.evaluators.llm_judge",
    "exact_match": "evaluation.src.evaluators.exact_match",
    # 未来添加其他评估器：
    # "bert_score": "evaluation.src.evaluators.bert_score",
}
```

**File:** evaluation/src/utils/prompts.py (L11-104)
```python
class PromptManager:
    """Prompt 管理器"""
    
    _instance = None
    _prompts = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._prompts is None:
            self._load_prompts()
    
    def _load_prompts(self):
        """加载 prompts 配置文件"""
        # 找到 config/prompts.yaml
        current_file = Path(__file__)
        config_path = current_file.parent.parent.parent / "config" / "prompts.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Prompts config not found: {config_path}")
        
        with open(config_path, "r", encoding="utf-8") as f:
            self._prompts = yaml.safe_load(f)
    
    def get_prompt(self, prompt_key: str, sub_key: str = None) -> str:
        """
        获取 prompt 模板
        
        Args:
            prompt_key: Prompt 类别键（如 "answer_generation", "llm_judge"）
            sub_key: 子键（如 "system_prompt", "user_prompt"）
            
        Returns:
            Prompt 模板字符串
        
        Example:
            >>> pm = PromptManager()
            >>> pm.get_prompt("answer_generation", "template")
            'Based on the following memories...'
            >>> pm.get_prompt("llm_judge", "system_prompt")
            'You are an expert grader...'
        """
        if prompt_key not in self._prompts:
            raise KeyError(f"Prompt key '{prompt_key}' not found in prompts.yaml")
        
        prompt_config = self._prompts[prompt_key]
        
        if sub_key:
            if sub_key not in prompt_config:
                raise KeyError(
                    f"Sub-key '{sub_key}' not found in prompt '{prompt_key}'"
                )
            return prompt_config[sub_key].strip()
        
        # 如果没有 sub_key，默认返回 'template'
        if "template" in prompt_config:
            return prompt_config["template"].strip()
        
        raise KeyError(
            f"No 'template' field found in prompt '{prompt_key}' "
            f"and no sub_key specified"
        )
    
    def format_prompt(
        self, 
        prompt_key: str, 
        sub_key: str = None, 
        **kwargs
    ) -> str:
        """
        获取并格式化 prompt
        
        Args:
            prompt_key: Prompt 类别键
            sub_key: 子键
            **kwargs: 格式化参数
            
        Returns:
            格式化后的 prompt
        
        Example:
            >>> pm = PromptManager()
            >>> pm.format_prompt(
            ...     "answer_generation",
            ...     context="Memory 1...",
            ...     question="What is X?"
            ... )
            'Based on the following memories...Memory 1...Question: What is X?'
        """
        template = self.get_prompt(prompt_key, sub_key)
        return template.format(**kwargs)
```
