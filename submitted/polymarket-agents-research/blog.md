# Polymarket Agents: 3700+ Stars 的预测市场 AI Agent 开发框架深度解析

![Polymarket Agents CLI](images/cli.png)

在 GitHub 上，Polymarket 早就放出了一个叫 **Polymarket Agents** 的开源仓库。这不是一个简单的演示项目，而是一个完整的开发者框架，专门用来构建预测市场的 AI Agent。

看看这个仓库的配置：
- 3700+ Stars，823 个 Fork，35 个 Watcher
- 采用 MIT 许可证，完全免费开源
- 代码 99.6% 用 Python 写成

本文将带你深入这个项目的核心架构、模块设计与工程实现。

---

## 1. 背景与项目概览

### 什么是 Polymarket？

Polymarket 是一个去中心化预测市场平台，允许用户对各种未来事件（政治选举、体育赛事、科技趋势等）进行押注。市场价格反映了集体智慧对事件发生概率的判断。

而 **Polymarket Agents** 则是官方提供的 AI Agent 开发框架，让开发者能够构建自动化的交易智能体，利用 AI 来分析信息、预测结果并执行交易。

### 项目定位

这不是一个 "一键赚钱" 的黑盒交易机器人，而是一个**开发者框架**。它提供了：
- Polymarket API 的完整封装
- AI Agent 所需的基础组件（RAG、Prompt 管理、LLM 集成）
- 可扩展的模块化架构
- 示例策略实现

---

## 2. 架构总览

Polymarket Agents 采用清晰的分层模块化设计，各组件职责明确：

<div style="padding:20px;background:#f8f9fa;border-radius:12px;border:1px solid #e9ecef;">
<div style="text-align:center;margin-bottom:16px;font-weight:700;font-size:18px;color:#1a1d21;">Polymarket Agents 架构总览</div>

<div style="background:#4A90D9;border-radius:8px;padding:12px 16px;margin-bottom:4px;">
<div style="color:#fff;font-weight:700;font-size:15px;margin-bottom:8px;">Scripts 层 — 用户交互入口</div>
<div style="display:flex;gap:8px;">
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">cli.py</span>
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">server.py</span>
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">trade.py</span>
</div>
</div>

<div style="text-align:center;color:#999;font-size:20px;line-height:1;margin:4px 0;">↓</div>

<div style="background:#635BFF;border-radius:8px;padding:12px 16px;margin-bottom:4px;">
<div style="color:#fff;font-weight:700;font-size:15px;margin-bottom:8px;">Application 层 — 核心业务逻辑</div>
<div style="display:flex;gap:8px;">
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">Trader<br/><span style="font-size:11px;color:#888;">交易逻辑</span></span>
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">Executor<br/><span style="font-size:11px;color:#888;">Agent 核心</span></span>
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">Prompter<br/><span style="font-size:11px;color:#888;">Prompt 管理</span></span>
</div>
</div>

<div style="text-align:center;color:#999;font-size:20px;line-height:1;margin:4px 0;">↓</div>

<div style="background:#00B886;border-radius:8px;padding:12px 16px;margin-bottom:4px;">
<div style="color:#fff;font-weight:700;font-size:15px;margin-bottom:8px;">Connectors 层 — 数据连接器</div>
<div style="display:flex;gap:8px;">
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">Chroma<br/><span style="font-size:11px;color:#888;">向量 DB</span></span>
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">News<br/><span style="font-size:11px;color:#888;">新闻源</span></span>
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">Search<br/><span style="font-size:11px;color:#888;">搜索</span></span>
</div>
</div>

<div style="text-align:center;color:#999;font-size:20px;line-height:1;margin:4px 0;">↓</div>

<div style="background:#F59E0B;border-radius:8px;padding:12px 16px;">
<div style="color:#fff;font-weight:700;font-size:15px;margin-bottom:8px;">APIs 层 — 底层接口</div>
<div style="display:flex;gap:8px;">
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">Polymarket<br/><span style="font-size:11px;color:#888;">API 客户端</span></span>
<span style="flex:1;background:#fff;border-radius:6px;padding:8px;text-align:center;font-size:13px;color:#333;">Gamma<br/><span style="font-size:11px;color:#888;">市场数据</span></span>
</div>
</div>

</div>

---

## 3. 核心模块深度解析

### 3.1 Trader 类：交易策略编排者

文件位置: `agents/application/trade.py`

Trader 类是策略的入口点，它编排整个交易流程。核心是 `one_best_trade()` 方法：

```python
def one_best_trade(self) -> None:
    """
    one_best_trade 策略评估所有事件、市场和订单簿
    利用自治智能体可访问的所有信息源
    然后无需人工干预执行交易
    """
    try:
        self.pre_trade_logic()  # 清理本地数据库

        # 步骤 1: 获取所有可交易事件
        events = self.polymarket.get_all_tradeable_events()
        print(f"1. FOUND {len(events)} EVENTS")

        # 步骤 2: 用 RAG 筛选事件
        filtered_events = self.agent.filter_events_with_rag(events)
        print(f"2. FILTERED {len(filtered_events)} EVENTS")

        # 步骤 3: 映射到市场
        markets = self.agent.map_filtered_events_to_markets(filtered_events)
        print(f"3. FOUND {len(markets)} MARKETS")

        # 步骤 4: 筛选市场
        filtered_markets = self.agent.filter_markets(markets)
        print(f"4. FILTERED {len(filtered_markets)} MARKETS")

        # 步骤 5: 计算最佳交易
        market = filtered_markets[0]
        best_trade = self.agent.source_best_trade(market)
        print(f"5. CALCULATED TRADE {best_trade}")

        # 步骤 6: 执行交易（默认注释掉，参考 TOS）
        amount = self.agent.format_trade_prompt_for_execution(best_trade)
        # trade = self.polymarket.execute_market_order(market, amount)

    except Exception as e:
        print(f"Error {e} \n \n Retrying")
        self.one_best_trade()
```

这个方法展示了典型的 Agent 交易流程：**数据获取 → 智能筛选 → 预测分析 → 交易执行**。

---

### 3.2 Executor 类：Agent 智能体的核心

文件位置: `agents/application/executor.py`

Executor 是整个框架的核心，它封装了 LLM 交互、RAG 检索、预测逻辑等。

#### 初始化与 LLM 集成

```python
class Executor:
    def __init__(self, default_model='gpt-3.5-turbo-16k') -> None:
        load_dotenv()
        max_token_model = {
            'gpt-3.5-turbo-16k': 15000,
            'gpt-4-1106-preview': 95000
        }
        self.token_limit = max_token_model.get(default_model)
        self.prompter = Prompter()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(
            model=default_model,
            temperature=0,  # 温度设为 0，确保输出确定性
        )
        self.gamma = Gamma()
        self.chroma = Chroma()
        self.polymarket = Polymarket()
```

注意 `temperature=0` 的设置，这对于需要一致性输出的交易场景非常重要。

#### 亮点：Token 分块处理策略

当市场数据量超过 LLM 上下文限制时，Executor 实现了智能的分块处理：

```python
def get_polymarket_llm(self, user_input: str) -> str:
    data1 = self.gamma.get_current_events()
    data2 = self.gamma.get_current_markets()

    combined_data = str(self.prompter.prompts_polymarket(data1=data1, data2=data2))

    # 估算 token 数
    total_tokens = self.estimate_tokens(combined_data)

    token_limit = self.token_limit
    if total_tokens <= token_limit:
        # 在限制内，正常处理
        return self.process_data_chunk(data1, data2, user_input)
    else:
        # 超出限制，分块处理
        group_size = (total_tokens // token_limit) + 1

        # 先过滤掉无意义的键，减少数据量
        keys_no_meaning = ['image', 'pagerDutyNotificationEnabled', ...]
        useful_keys = ['id', 'questionID', 'description', 'liquidity', ...]
        data1 = retain_keys(data1, useful_keys)

        # 切分数据
        cut_1 = self.divide_list(data1, group_size)
        cut_2 = self.divide_list(data2, group_size)

        # 逐块处理
        results = []
        for cut_data in zip(cut_1, cut_2):
            result = self.process_data_chunk(cut_data[0], cut_data[1], user_input)
            results.append(result)

        return " ".join(results)
```

这是一个非常实用的工程设计：先做键过滤精简数据，再做切分，最后合并结果。

#### Superforecaster 预测流程

Executor 实现了基于 "超级预测者" 方法论的预测：

```python
def source_best_trade(self, market_object) -> str:
    market_document = market_object[0].dict()
    market = market_document["metadata"]
    outcome_prices = ast.literal_eval(market["outcome_prices"])
    outcomes = ast.literal_eval(market["outcomes"])
    question = market["question"]
    description = market_document["page_content"]

    # 第一轮：Superforecaster 预测概率
    prompt = self.prompter.superforecaster(question, description, outcomes)
    result = self.llm.invoke(prompt)
    content = result.content

    # 第二轮：根据预测生成交易
    prompt = self.prompter.one_best_trade(content, outcomes, outcome_prices)
    result = self.llm.invoke(prompt)
    content = result.content

    return content
```

---

### 3.3 Prompter 类：Prompt 工程的艺术

文件位置: `agents/application/prompts.py`

Prompter 类集中管理所有的提示词模板，这是一个很好的设计实践。

#### Superforecaster 提示词

最精彩的是 `superforecaster()` 方法，它实现了系统的预测分析流程：

```python
def superforecaster(self, question: str, description: str, outcome: str) -> str:
    return f"""
    You are a Superforecaster tasked with correctly predicting the likelihood of events.
    Use the following systematic process to develop an accurate prediction for the following
    question=`{question}` and description=`{description}` combination.

    Here are the key steps to use in your analysis:

    1. Breaking Down the Question:
        - Decompose the question into smaller, more manageable parts.
        - Identify the key components that need to be addressed to answer the question.
    2. Gathering Information:
        - Seek out diverse sources of information.
        - Look for both quantitative data and qualitative insights.
        - Stay updated on relevant news and expert analyses.
    3. Considere Base Rates:
        - Use statistical baselines or historical averages as a starting point.
        - Compare the current situation to similar past events to establish a benchmark probability.
    4. Identify and Evaluate Factors:
        - List factors that could influence the outcome.
        - Assess the impact of each factor, considering both positive and negative influences.
        - Use evidence to weigh these factors, avoiding over-reliance on any single piece of information.
    5. Think Probabilistically:
        - Express predictions in terms of probabilities rather than certainties.
        - Assign likelihoods to different outcomes and avoid binary thinking.
        - Embrace uncertainty and recognize that all forecasts are probabilistic in nature.

    Given these steps produce a statement on the probability of outcome=`{outcome}` occuring.

    Give your response in the following format:

    I believe {question} has a likelihood `{float}` for outcome of `{str}`.
    """
```

这个提示词融入了 Superforecasting 书中的方法论：问题分解、信息搜集、基准率考虑、因素评估、概率思维。

#### 交易生成提示词

另一个有趣的提示词用了 "顶尖交易者" 的人设：

```python
def one_best_trade(self, prediction: str, outcomes: List[str], outcome_prices: str) -> str:
    return self.polymarket_analyst_api() + f"""
        Imagine yourself as the top trader on Polymarket,
        dominating the world of information markets with your keen insights and strategic acumen.
        You have an extraordinary ability to analyze and interpret data from diverse sources,
        turning complex information into profitable trading opportunities.
        You excel in predicting the outcomes of global events,
        from political elections to economic developments,
        using a combination of data analysis and intuition.
        Your deep understanding of probability and statistics allows you to assess market sentiment
        and make informed decisions quickly.
        ...
    """ + f"""
        You made the following prediction for a market: {prediction}
        The current outcomes ${outcomes} prices are: ${outcome_prices}
        Given your prediction, respond with a genius trade in the format:
        `
            price:'price_on_the_orderbook',
            size:'percentage_of_total_funds',
            side: BUY or SELL,
        `
    """
```

---

### 3.4 PolymarketRAG：向量检索增强

文件位置: `agents/connectors/chroma.py`

RAG 模块用于将事件和市场向量化，然后通过相似度搜索筛选最相关的标的：

```python
class PolymarketRAG:
    def events(self, events: "list[SimpleEvent]", prompt: str) -> "list[tuple]":
        # 步骤 1: 创建本地 JSON 文件
        local_events_directory: str = "./local_db_events"
        if not os.path.isdir(local_events_directory):
            os.mkdir(local_events_directory)
        local_file_path = f"{local_events_directory}/events.json"
        dict_events = [x.dict() for x in events]
        with open(local_file_path, "w+") as output_file:
            json.dump(dict_events, output_file)

        # 步骤 2: 定义 metadata 提取函数
        def metadata_func(record: dict, metadata: dict) -> dict:
            metadata["id"] = record.get("id")
            metadata["markets"] = record.get("markets")
            return metadata

        # 步骤 3: 加载文档并创建向量库
        loader = JSONLoader(
            file_path=local_file_path,
            jq_schema=".[]",
            content_key="description",
            text_content=False,
            metadata_func=metadata_func,
        )
        loaded_docs = loader.load()
        embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_db_directory = f"{local_events_directory}/chroma"
        local_db = Chroma.from_documents(
            loaded_docs, embedding_function, persist_directory=vector_db_directory
        )

        # 步骤 4: 相似度检索
        return local_db.similarity_search_with_score(query=prompt)
```

这里的设计模式是：
1. 数据写入临时 JSON
2. 用 LangChain 的 JSONLoader 加载（支持 metadata 提取）
3. 创建 Chroma 向量库
4. 执行相似度搜索

---

### 3.5 Polymarket API：区块链交互

文件位置: `agents/polymarket/polymarket.py`

这个模块封装了与 Polymarket 区块链和 API 的交互，包括 Web3 集成、订单构建与签名等。

#### 初始化与钱包配置

```python
class Polymarket:
    def __init__(self) -> None:
        self.gamma_url = "https://gamma-api.polymarket.com"
        self.clob_url = "https://clob.polymarket.com"
        self.chain_id = 137  # POLYGON 主网
        self.private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY")
        self.polygon_rpc = "https://polygon-rpc.com"
        self.w3 = Web3(Web3.HTTPProvider(self.polygon_rpc))

        # 合约地址
        self.exchange_address = "0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e"
        self.usdc_address = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

        self._init_api_keys()
        self._init_approvals(False)
```

#### 市场订单执行

```python
def execute_market_order(self, market, amount) -> str:
    token_id = ast.literal_eval(market[0].dict()["metadata"]["clob_token_ids"])[1]
    order_args = MarketOrderArgs(
        token_id=token_id,
        amount=amount,
    )
    signed_order = self.client.create_market_order(order_args)
    print("Execute market order... signed_order ", signed_order)
    resp = self.client.post_order(signed_order, orderType=OrderType.FOK)
    print(resp)
    print("Done!")
    return resp
```

这里使用了 FOK（Fill-or-Kill）订单类型，即要么完全成交，要么全部撤销。

---

## 4. 核心工作流详解

让我们通过 `one_best_trade()` 看完整的执行链路：

<div style="padding:20px;background:#f8f9fa;border-radius:12px;border:1px solid #e9ecef;">
<div style="text-align:center;margin-bottom:16px;font-weight:700;font-size:18px;color:#1a1d21;">one_best_trade() 完整执行链路</div>

<div style="background:#4A90D9;border-radius:8px;padding:12px 16px;text-align:center;">
<span style="color:#fff;font-weight:700;font-size:15px;">开始 one_best_trade()</span>
</div>

<div style="text-align:center;color:#999;font-size:20px;line-height:1;margin:4px 0;">↓</div>

<div style="background:#635BFF;border-radius:8px;padding:12px 16px;">
<span style="color:#fff;font-weight:700;font-size:14px;">1. 获取所有可交易事件</span>
<span style="color:rgba(255,255,255,0.8);font-size:12px;display:block;margin-top:4px;">get_all_tradeable_events → Polymarket API → Gamma API</span>
</div>

<div style="text-align:center;color:#999;font-size:20px;line-height:1;margin:4px 0;">↓</div>

<div style="background:#00B886;border-radius:8px;padding:12px 16px;">
<span style="color:#fff;font-weight:700;font-size:14px;">2. RAG 筛选事件</span>
<span style="color:rgba(255,255,255,0.8);font-size:12px;display:block;margin-top:4px;">filter_events_with_rag → 事件向量化 → Chroma DB → 相似度检索</span>
</div>

<div style="text-align:center;color:#999;font-size:20px;line-height:1;margin:4px 0;">↓</div>

<div style="background:#00B886;border-radius:8px;padding:12px 16px;">
<span style="color:#fff;font-weight:700;font-size:14px;">3. 映射到市场</span>
<span style="color:rgba(255,255,255,0.8);font-size:12px;display:block;margin-top:4px;">map_filtered_events_to_markets → 为每个事件获取对应的市场数据</span>
</div>

<div style="text-align:center;color:#999;font-size:20px;line-height:1;margin:4px 0;">↓</div>

<div style="background:#00B886;border-radius:8px;padding:12px 16px;">
<span style="color:#fff;font-weight:700;font-size:14px;">4. RAG 筛选市场</span>
<span style="color:rgba(255,255,255,0.8);font-size:12px;display:block;margin-top:4px;">filter_markets → 市场向量化 → Chroma DB → 相似度检索</span>
</div>

<div style="text-align:center;color:#999;font-size:20px;line-height:1;margin:4px 0;">↓</div>

<div style="background:#F59E0B;border-radius:8px;padding:12px 16px;">
<span style="color:#fff;font-weight:700;font-size:14px;">5. 计算最佳交易</span>
<span style="color:rgba(255,255,255,0.9);font-size:12px;display:block;margin-top:6px;padding-left:12px;border-left:2px solid rgba(255,255,255,0.4);">第一轮: Superforecaster 预测概率<br/><span style="color:rgba(255,255,255,0.7);">↳ LLM + superforecaster prompt</span></span>
<span style="color:rgba(255,255,255,0.9);font-size:12px;display:block;margin-top:6px;padding-left:12px;border-left:2px solid rgba(255,255,255,0.4);">第二轮: 生成交易建议<br/><span style="color:rgba(255,255,255,0.7);">↳ LLM + one_best_trade prompt</span></span>
</div>

<div style="text-align:center;color:#999;font-size:20px;line-height:1;margin:4px 0;">↓</div>

<div style="background:#EF4444;border-radius:8px;padding:12px 16px;">
<span style="color:#fff;font-weight:700;font-size:14px;">6. 执行交易 [默认注释]</span>
<span style="color:rgba(255,255,255,0.8);font-size:12px;display:block;margin-top:4px;">execute_market_order → 构建订单 → 签名 → 上链</span>
</div>

</div>

---

## 5. 工程要点与创新点

### 5.1 Token 分块处理策略

当市场数据量大时，直接丢给 LLM 会超出上下文限制。Polymarket Agents 的解决方案很优雅：

1. **先过滤字段**：保留 `id`、`description`、`liquidity` 等有用字段，丢弃 `image`、`pagerDutyNotificationEnabled` 等噪声
2. **再切分数据**：根据 token 估算将数据切分成多块
3. **最后合并**：对每块调用 LLM，最后合并结果

### 5.2 RAG + Superforecasting 组合

这个框架的一个亮点是将 **检索增强** 与 **超级预测者方法论** 结合：
- RAG 用于从大量市场中筛选相关标的
- Superforecaster prompt 用于深度分析单个市场的概率

### 5.3 Prompt 工程的层次化

Prompter 类将提示词集中管理，并且有清晰的层次：
- `polymarket_analyst_api()`: 基础人设
- `superforecaster()`: 预测方法论
- `one_best_trade()`: 交易决策

这种分层设计使得 prompt 可以复用和组合。

### 5.4 区块链安全设计

在 `_init_approvals()` 中我们看到，合约授权默认是关闭的（`run=False`），交易执行代码也是默认注释的。这是负责任的设计：
- 用户需要显式启用才会执行真实交易
- README 中明确提醒参考 TOS（服务条款）

---

## 6. 快速上手实战

### 环境配置

```bash
# 1. 克隆仓库
git clone https://github.com/Polymarket/agents.git
cd polymarket-agents

# 2. 创建虚拟环境（Python 3.9）
virtualenv --python=python3.9 .venv
source .venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入：
# - POLYGON_WALLET_PRIVATE_KEY
# - OPENAI_API_KEY

# 5. 设置 PYTHONPATH
export PYTHONPATH="."
```

### 运行示例策略

```bash
# 运行 CLI
python scripts/python/cli.py get-all-markets --limit 5

# 运行交易策略（不会真正执行，因为交易代码被注释了）
python agents/application/trade.py
```

### 自定义策略开发

要开发自己的策略，可以参考 `Trader` 类的结构：

```python
from agents.application.executor import Executor as Agent
from agents.polymarket.polymarket import Polymarket

class MyStrategy:
    def __init__(self):
        self.polymarket = Polymarket()
        self.agent = Agent()

    def my_custom_trade(self):
        # 你的自定义逻辑
        events = self.polymarket.get_all_tradeable_events()
        # ... 你的筛选、分析、交易逻辑 ...
```

---

## 7. 局限与展望

### 当前版本的限制

1. **示例性质**：`one_best_trade` 更多是概念验证，离实盘盈利还有距离
2. **缺少回测框架**：没有提供历史数据回测能力
3. **风控简单**：没有仓位管理、止损等风控模块
4. **新闻源有限**：当前新闻和搜索连接器还比较基础

### 可扩展方向

1. **多策略组合**：可以扩展为支持多个策略并行运行
2. **实时数据流**：接入 WebSocket 实时市场数据
3. **更丰富的数据源**：集成更多新闻源、另类数据
4. **性能监控 Dashboard**：添加策略表现监控和可视化
5. **策略回测引擎**：添加历史回测模块

### 社区贡献机会

作为一个 3700+ Stars 的开源项目，虽然仓库已于 2024 年 11 月停止更新并在 2026 年 5 月正式归档（Public Archive），但其架构设计和工程思路仍然值得学习。社区可以通过 Fork 方式继续发展：
- 改进数据连接器
- 添加新的策略模板
- 完善文档和示例
- 基于 Fork 修复 Issues 中的 bug

---

## 总结

Polymarket Agents 是一个设计精良的 AI Agent 开发框架，它的价值不在于提供"即插即用"的盈利策略，而在于：

1. **完整的架构参考**：展示了如何将 LLM、RAG、区块链 API 组合成一个 Agent
2. **模块化设计**：各组件解耦，易于扩展和修改
3. **工程实践**：Token 分块、Prompt 管理、安全设计等都值得学习
4. **入门门槛低**：代码简洁，注释清晰，适合学习

如果你对 AI Agent、预测市场、DeFi 感兴趣，这个项目是一个很好的学习起点。当然，真正用于实盘交易时，请务必做好充分的测试和风险控制。

> **注意**：该仓库已于 2026 年 5 月归档（Public Archive），不再维护。本文基于归档前的代码进行分析，建议读者参考学习其架构设计，但实际使用时请注意代码可能未及时更新。

---

## 参考资料

- GitHub 仓库: [https://github.com/Polymarket/agents](https://github.com/Polymarket/agents)
- Polymarket 官网: [https://polymarket.com](https://polymarket.com)
- Superforecasting: [HBR 文章](https://hbr.org/2016/05/superforecasting-how-to-upgrade-your-companys-judgment)
- Vitalik Buterin 关于 Crypto + AI: [The promise and challenges of crypto + AI applications](https://vitalik.eth.limo/general/2024/01/30/cryptoai.html)
