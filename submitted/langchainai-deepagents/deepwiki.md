# 我问
首先，解释下deepagents和langraph的区别以及如何结合使用？

# deepwiki答
# Answer

## DeepAgents 和 LangGraph 的关系

**DeepAgents 是基于 LangGraph 构建的高级框架** [1](#0-0) 。它们的关系是：

### DeepAgents 是什么
DeepAgents 是一个 Python 包，提供了开箱即用的"深度智能体"功能，包括：
- 规划工具（planning tool）
- 子智能体系统（sub-agents）
- 虚拟文件系统（file system）
- 详细的系统提示词（detailed prompt） [2](#0-1) 

### LangGraph 是什么
LangGraph 是底层的智能体图框架，DeepAgents 依赖它作为核心基础设施 [3](#0-2) 。

## 如何结合使用

### 1. DeepAgents 返回 LangGraph 图对象

当你调用 `create_deep_agent()` 时，它返回的就是一个 LangGraph 的 `CompiledStateGraph` 对象 [4](#0-3) ：

```python
from deepagents import create_deep_agent

agent = create_deep_agent([internet_search], research_instructions)
# agent 是一个 LangGraph 图对象
``` [5](#0-4) 

### 2. 使用 LangGraph 的调用模式

因为返回的是 LangGraph 图，你可以使用所有标准的 LangGraph 调用方式：

```python
# 同步调用
result = agent.invoke({"messages": [...]})

# 流式输出
for event in agent.stream({"messages": [...]}):
    print(event)

# 异步流式输出
async for event in agent.astream({"messages": [...]}):
    print(event)
``` [6](#0-5) 

### 3. 内部实现：通过 LangChain 的 create_agent

DeepAgents 内部通过调用 `langchain.agents.create_agent` 来构建 LangGraph 图 [7](#0-6) 。这个函数接收：
- 模型（model）
- 系统提示词（system_prompt）
- 工具列表（tools）
- 中间件栈（middleware）
- 检查点器（checkpointer） [8](#0-7) 

### 4. 中间件系统扩展 LangGraph

DeepAgents 通过 LangGraph 的中间件机制添加功能 [9](#0-8) ：
- `PlanningMiddleware` - 添加 `write_todos` 工具
- `FilesystemMiddleware` - 添加文件系统工具
- `SubAgentMiddleware` - 添加 `task` 工具用于子智能体委托
- `SummarizationMiddleware` - 对话摘要
- `AnthropicPromptCachingMiddleware` - 提示词缓存

<cite />

## 实际使用示例

```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import MemorySaver

# 创建 DeepAgent（返回 LangGraph 图）
agent = create_deep_agent(
    tools=[your_tools],
    instructions="你的指令",
    checkpointer=MemorySaver()  # LangGraph 的检查点器
)

# 使用 LangGraph 的配置和调用模式
config = {"configurable": {"thread_id": "1"}}
result = agent.invoke({"messages": [...]}, config=config)
``` [10](#0-9) 

# Notes

DeepAgents 本质上是 LangGraph 的一个预配置封装，它不是替代 LangGraph，而是在 LangGraph 之上提供了一套针对"深度任务"优化的默认配置和工具集。你可以把 DeepAgents 看作是 LangGraph 的一个高级应用模板，专门用于需要规划、文件管理和子任务委托的复杂智能体场景 [11](#0-10) 。

Wiki pages you might want to explore:
- [Getting Started (langchain-ai/deepagents)](/wiki/langchain-ai/deepagents#1.1)
- [Agent Creation and Configuration (langchain-ai/deepagents)](/wiki/langchain-ai/deepagents#2.1)

### Citations

**File:** README.md (L3-10)
```markdown
Using an LLM to call tools in a loop is the simplest form of an agent. 
This architecture, however, can yield agents that are “shallow” and fail to plan and act over longer, more complex tasks. 
Applications like “Deep Research”, "Manus", and “Claude Code” have gotten around this limitation by implementing a combination of four things:
a **planning tool**, **sub agents**, access to a **file system**, and a **detailed prompt**.

<img src="deep_agents.png" alt="deep agent" width="600"/>

`deepagents` is a Python package that implements these in a general purpose way so that you can easily create a Deep Agent for your application.
```

**File:** README.md (L59-62)
```markdown
agent = create_deep_agent(
    [internet_search],
    research_instructions,
)
```

**File:** README.md (L65-66)
```markdown
result = agent.invoke({"messages": [{"role": "user", "content": "what is langgraph?"}]})
```
```

**File:** README.md (L70-71)
```markdown
The agent created with `create_deep_agent` is just a LangGraph graph - so you can interact with it (streaming, human-in-the-loop, memory, studio)
in the same way you would any LangGraph agent.
```

**File:** README.md (L314-336)
```markdown
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

# Create agent with file operations requiring approval
agent = create_deep_agent(
    tools=[your_tools],
    instructions="Your instructions here",
    tool_configs={
        # You can specify a dictionary for fine grained control over what interrupt options exist
        "tool_1": {
            "allow_respond": True,
            "allow_edit": True,
            "allow_accept":True,
        },
        # You can specify a boolean for shortcut
        # This is a shortcut for the same functionality as above
        "tool_2": True,
    }
)

checkpointer= InMemorySaver()
agent.checkpointer = checkpointer
```
```

**File:** pyproject.toml (L4-4)
```text
description = "General purpose 'deep agent' with sub-agent spawning, todo list capabilities, and mock file system. Built on LangGraph."
```

**File:** pyproject.toml (L9-9)
```text
    "langgraph>=1.0.0a3",
```

**File:** src/deepagents/graph.py (L5-5)
```python
from langchain.agents import create_agent
```

**File:** src/deepagents/graph.py (L28-42)
```python
    deepagent_middleware = [
        PlanningMiddleware(),
        FilesystemMiddleware(),
        SubAgentMiddleware(
            default_subagent_tools=tools,   # NOTE: These tools are piped to the general-purpose subagent.
            subagents=subagents if subagents is not None else [],
            model=model,
            is_async=is_async,
        ),
        SummarizationMiddleware(
            model=model,
            max_tokens_before_summary=120000,
            messages_to_keep=20,
        ),
        AnthropicPromptCachingMiddleware(ttl="5m", unsupported_model_behavior="ignore")
```

**File:** src/deepagents/graph.py (L51-58)
```python
    return create_agent(
        model,
        system_prompt=instructions + "\n\n" + BASE_AGENT_PROMPT,
        tools=tools,
        middleware=deepagent_middleware,
        context_schema=context_schema,
        checkpointer=checkpointer,
    )
```


# 我追问
你说「你可以把 DeepAgents 看作是 LangGraph 的一个高级应用模板，专门用于需要规划、文件管理和子任务委托的复杂智能体场景」能不能再具体举例子描述下，就是什么情况用langchain够了，什么情况是langchain+langgraph，什么情况是得用deepagents，这样我才能更加清晰的区分使用场景，不然我听得很模糊

# deepwiki答
让我用三层递进的方式来说明 LangChain、LangGraph 和 DeepAgents 的使用场景区别。<cite/>

## 第一层：只用 LangChain

**适用场景**：单次工具调用或简单的工具链 [1](#2-0) 

### 例子 1：简单问答
```python
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

@tool
def search(query: str):
    """搜索信息"""
    return "搜索结果..."

# 直接用 LLM + 工具，不需要图结构
llm = ChatOpenAI()
llm_with_tools = llm.bind_tools([search])
response = llm_with_tools.invoke("今天天气如何?")
```

**特点**：
- 1-2 次工具调用就能完成
- 不需要状态管理
- 不需要循环执行
- 例如：简单查询、单次翻译、格式转换 [2](#2-1) 

## 第二层：LangChain + LangGraph

**适用场景**：需要多轮工具调用循环，但任务相对简单（≤3 步） [3](#2-2) 

### 例子 2：多次搜索后总结
```python
from langchain.agents import create_agent

agent = create_agent(
    model="claude-3-5-sonnet",
    tools=[search_tool, calculator],
    system_prompt="你是一个助手"
)

# 用户："搜索 Python 和 Java 的区别，然后总结"
# 执行流程：
# 1. 调用 search_tool("Python") 
# 2. 调用 search_tool("Java")
# 3. LLM 总结两者区别
# 4. 返回答案
```

**特点**：
- 需要 agent 循环（LangGraph 提供）
- 但不需要显式规划
- 不需要保存中间文件
- 不需要拆分子任务
- 例如：连续搜索、简单数据处理、基础对话 [4](#2-3) 

### 例子 3：并行简单任务
```python
# 用户："订一份披萨、一个汉堡、一份沙拉"
# 执行流程：
# 1. 并行调用 order_pizza()、order_burger()、order_salad()
# 2. 返回确认
```

这种场景虽然是多个工具调用，但每个都是独立的简单操作，不需要 DeepAgents 的规划和状态管理能力 [5](#2-4) 。

## 第三层：必须用 DeepAgents

**适用场景**：复杂多步任务（>3 步），需要以下任一能力 [6](#2-5) ：

### 判断标准

| 能力需求 | 是否需要 DeepAgents |
|---------|-------------------|
| 显式任务规划和进度追踪 | ✅ 需要 |
| 保存中间文件/工件 | ✅ 需要 |
| 拆分独立子任务（上下文隔离） | ✅ 需要 |
| 任务步骤 > 3 步 | ✅ 需要 |
| 需要迭代改进（如写作→审阅→修改） | ✅ 需要 |

### 例子 4：研究报告（需要 DeepAgents）

**用户请求**："研究三位篮球明星并写对比报告" [7](#2-6) 

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    tools=[search_tool],
    instructions="你是研究专家"
)

# 执行流程：
# 1. write_todos() - 创建任务清单
#    - 研究 LeBron James ✓
#    - 研究 Michael Jordan ✓  
#    - 研究 Kobe Bryant ✓
#    - 撰写对比报告 ✓

# 2. 并行启动 3 个子智能体（上下文隔离）
#    task("研究 LeBron", subagent_type="general-purpose")
#    task("研究 Jordan", subagent_type="general-purpose")
#    task("研究 Kobe", subagent_type="general-purpose")

# 3. 每个子智能体独立工作：
#    - 多次搜索
#    - write_file("lebron_research.txt", "详细成就...")
#    - 返回精炼摘要

# 4. 主智能体整合：
#    - read_file("lebron_research.txt")
#    - read_file("jordan_research.txt")
#    - read_file("kobe_research.txt")
#    - 对比分析
#    - write_file("final_report.txt", "对比报告...")
#    - 更新 todos 为 completed
```

**为什么需要 DeepAgents**：
- **规划**：4 个主要步骤，需要 `write_todos` 追踪进度 [8](#2-7) 
- **文件系统**：保存每个球员的研究结果，避免上下文过长 [9](#2-8) 
- **子智能体**：每个球员的研究是独立的深度任务，用子智能体隔离上下文 [10](#2-9) 

### 例子 5：代码重构（需要 DeepAgents）

**用户请求**："将项目中所有 `getCwd` 重命名为 `getCurrentWorkingDirectory`" [11](#2-10) 

```python
agent = create_deep_agent(
    tools=[search_codebase, ls, read_file, edit_file],
    instructions="你是代码重构专家"
)

# 执行流程：
# 1. write_todos() - 创建任务清单
#    - 搜索所有包含 getCwd 的文件
#    - 修改 file1.ts
#    - 修改 file2.ts
#    - ...（假设找到 15 个文件）

# 2. search_codebase("getCwd") - 找到 15 个文件

# 3. 对每个文件：
#    - read_file("file1.ts")
#    - edit_file("file1.ts", "getCwd", "getCurrentWorkingDirectory")
#    - 更新 todo 状态为 completed

# 4. 所有文件修改完成后，标记整体任务完成
```

**为什么需要 DeepAgents**：
- **规划**：15+ 个文件需要修改，需要 todo 列表追踪 [12](#2-11) 
- **文件系统**：使用 `edit_file` 工具进行精确替换 [13](#2-12) 
- **进度管理**：每完成一个文件就更新状态，用户可见进度

### 例子 6：迭代写作（需要 DeepAgents）

**用户请求**："写一篇技术博客，然后让审阅智能体提意见，再修改"

```python
subagents = [{
    "name": "content-reviewer",
    "description": "审阅内容并提供改进建议",
    "prompt": "你是严格的编辑"
}]

agent = create_deep_agent(
    tools=[write_file, read_file],
    instructions="你是技术作家",
    subagents=subagents
)

# 执行流程：
# 1. write_file("draft.md", "初稿内容...")
# 2. task("审阅 draft.md", subagent_type="content-reviewer")
#    - 子智能体返回改进建议
# 3. read_file("draft.md")
# 4. edit_file("draft.md", "旧内容", "改进后内容")
# 5. write_file("final.md", "最终版本")
```

**为什么需要 DeepAgents**：
- **文件系统**：保存草稿、最终版本 [14](#2-13) 
- **子智能体**：专门的审阅智能体，隔离审阅逻辑 [15](#2-14) 
- **迭代流程**：写作→审阅→修改，多个步骤需要状态管理

## 决策树总结

```mermaid
graph TD
    START["需要 LLM 智能体"]
    
    Q1{"需要多轮<br/>工具调用?"}
    Q2{"任务步骤<br/>> 3 步?"}
    Q3{"需要以下任一:<br/>1. 显式规划<br/>2. 保存文件<br/>3. 子任务委托<br/>4. 上下文隔离"}
    
    LANGCHAIN["只用 LangChain<br/>llm.bind_tools()"]
    LANGGRAPH["LangChain + LangGraph<br/>create_agent()"]
    DEEPAGENTS["DeepAgents<br/>create_deep_agent()"]
    
    START --> Q1
    Q1 -->|"否<br/>(1-2次调用)"| LANGCHAIN
    Q1 -->|"是"| Q2
    Q2 -->|"否<br/>(≤3步)"| Q3
    Q2 -->|"是<br/>(>3步)"| DEEPAGENTS
    Q3 -->|"否"| LANGGRAPH
    Q3 -->|"是"| DEEPAGENTS
```

<cite/>

# Notes

核心区别在于**任务复杂度**：<cite/>

- **LangChain**：单次或简单工具调用（如天气查询） [1](#2-0) 
- **LangGraph**：需要循环但简单的任务（如连续搜索后总结） [4](#2-3) 
- **DeepAgents**：复杂多步任务，需要规划、文件管理或子任务委托（如研究报告、代码重构） [6](#2-5) 

DeepAgents 通过预配置的中间件栈 [16](#2-15) ，自动提供了这些高级能力，而不需要你手动实现。

Wiki pages you might want to explore:
- [Overview (langchain-ai/deepagents)](/wiki/langchain-ai/deepagents#1)
- [Built-in Tools (langchain-ai/deepagents)](/wiki/langchain-ai/deepagents#2.5)

### Citations

**File:** src/deepagents/prompts.py (L61-66)
```python
<reasoning>
The assistant used the todo list because:
1. Marketing campaign planning involves multiple distinct channels and activities
2. Each component requires careful coordination and planning
3. The systematic approach ensures all aspects of the launch are covered
</reasoning>
```

**File:** src/deepagents/prompts.py (L69-82)
```python
<example>
User: Help me rename the function getCwd to getCurrentWorkingDirectory across my project
Assistant: Let me first search through your codebase to find all occurrences of 'getCwd'.
*Uses search tools to locate all instances of getCwd in the codebase*
Assistant: I've found 15 instances of 'getCwd' across 8 different files. Let me create a todo list to track these changes.
*Creates todo list with specific items for each file that needs updating*

<reasoning>
The assistant used the todo list because:
1. The assistant searched to understand the scope of the task
2. Upon finding multiple occurrences across different files, it determined this was a complex task with multiple steps (>3)
3. The todo list helps ensure every instance is tracked and updated systematically
4. This approach prevents missing any occurrences and maintains consistency.
</reasoning>
```

**File:** src/deepagents/prompts.py (L102-113)
```python
<example>
User: How do I print 'Hello World' in Python?
Assistant: In Python, you can print "Hello World" with this simple code:

python
print("Hello World")

This will output the text "Hello World" to the console when executed.</assistant>

<reasoning>
The assistant did not use the todo list because this is a single, trivial task that can be completed in one step. There's no need to track multiple tasks or steps for such a straightforward request.
</reasoning>
```

**File:** src/deepagents/prompts.py (L116-130)
```python
<example>
User: What's the best way to water houseplants?
Assistant: The best way to water houseplants depends on the specific plant type, but here are some general guidelines:

- Check soil moisture by inserting your finger about 1-2 inches into the soil
- Water thoroughly when the top inch feels dry, allowing water to drain from the bottom
- Use room temperature water and water in the morning when possible
- Avoid overwatering, which is more harmful than underwatering for most plants

Different plants have different needs, so it's important to research your specific varieties for optimal care.

<reasoning>
The assistant did not use the todo list because this is an informational request with no actual tasks to complete. The user is simply asking for advice and explanation, not for the assistant to perform multiple steps or activities.
</reasoning>
</example>
```

**File:** src/deepagents/prompts.py (L156-164)
```python
User: I need to write a function that checks if a number is prime and then test it out.
Assistant: I'll help you write a function that checks if a number is prime and then test it out.
*Writes function that checks if a number is prime*
*Tests the function*

<reasoning>
Even though this is a multi-step task, it is very straightforward and can be completed in two trivial steps (which is less than 3 steps!). Using the todo list here is overkill and wastes time and tokens.
</reasoning>
</example>
```

**File:** src/deepagents/prompts.py (L166-177)
```python
<example>
User: I want you to order a pizza from Dominos, order a burger from McDonald's, and order a salad from Subway.
Assistant: I'll help you order a pizza from Dominos, order a burger from McDonald's, and order a salad from Subway.
*Orders a pizza from Dominos*
*Orders a burger from McDonald's*
*Orders a salad from Subway*

<reasoning>
Even though this is a multi-step task, assuming the assistant has the ability to order from these restaurants, it is very straightforward and can be completed in three trivial tool calls. 
Using the todo list here is overkill and wastes time and tokens. These three tool calls should be made in parallel, in fact.
</reasoning>
</example>
```

**File:** src/deepagents/prompts.py (L238-248)
```python
<example>
User: "I want to conduct research on the accomplishments of Lebron James, Michael Jordan, and Kobe Bryant, and then compare them."
Assistant: *Uses the task tool in parallel to conduct isolated research on each of the three players*
Assistant: *Synthesizes the results of the three isolated research tasks and responds to the User*
<commentary>
Research is a complex, multi-step task in it of itself.
The research of each individual player is not dependent on the research of the other players.
The assistant uses the task tool to break down the complex objective into three isolated tasks.
Each research task only needs to worry about context and tokens about one player, then returns synthesized information about each player as the Tool Result.
This means each research task can dive deep and spend tokens and context deeply researching each player, but the final result is synthesized information, and saves us tokens in the long run when comparing the players to each other.
</commentary>
```

**File:** src/deepagents/prompts.py (L272-278)
```python
User: "I want to order a pizza from Dominos, order a burger from McDonald's, and order a salad from Subway."
Assistant: *Calls tools directly in parallel to order a pizza from Dominos, a burger from McDonald's, and a salad from Subway*
<commentary>
The assistant did not use the task tool because the objective is super simple and clear and only requires a few trivial tool calls.
It is better to just complete the task directly and NOT use the `task`tool.
</commentary>
</example>
```

**File:** src/deepagents/prompts.py (L282-307)
```python
<example_agent_descriptions>
"content-reviewer": use this agent after you are done creating significant content or documents
"greeting-responder": use this agent when to respond to user greetings with a friendly joke
"research-analyst": use this agent to conduct thorough research on complex topics
</example_agent_description>

<example>
user: "Please write a function that checks if a number is prime"
assistant: Sure let me write a function that checks if a number is prime
assistant: First let me use the Write tool to write a function that checks if a number is prime
assistant: I'm going to use the Write tool to write the following code:
<code>
function isPrime(n) {{
  if (n <= 1) return false
  for (let i = 2; i * i <= n; i++) {{
    if (n % i === 0) return false
  }}
  return true
}}
</code>
<commentary>
Since significant content was created and the task was completed, now use the content-reviewer agent to review the work
</commentary>
assistant: Now let me use the content-reviewer agent to review the code
assistant: Uses the Task tool to launch with the content-reviewer agent 
</example>
```

**File:** README.md (L3-6)
```markdown
Using an LLM to call tools in a loop is the simplest form of an agent. 
This architecture, however, can yield agents that are “shallow” and fail to plan and act over longer, more complex tasks. 
Applications like “Deep Research”, "Manus", and “Claude Code” have gotten around this limitation by implementing a combination of four things:
a **planning tool**, **sub agents**, access to a **file system**, and a **detailed prompt**.
```

**File:** README.md (L253-257)
```markdown
`deepagents` comes with four built-in file system tools: `ls`, `edit_file`, `read_file`, `write_file`.
These do not actually use a file system - rather, they mock out a file system using LangGraph's State object.
This means you can easily run many of these agents on the same machine without worrying that they will edit the same underlying files.

Right now the "file system" will only be one level deep (no sub directories).
```

**File:** README.md (L284-292)
```markdown

By default, deep agents come with five built-in tools:

- `write_todos`: Tool for writing todos
- `write_file`: Tool for writing to a file in the virtual filesystem
- `read_file`: Tool for reading from a file in the virtual filesystem
- `ls`: Tool for listing files in the virtual filesystem
- `edit_file`: Tool for editing a file in the virtual filesystem

```

**File:** src/deepagents/graph.py (L28-43)
```python
    deepagent_middleware = [
        PlanningMiddleware(),
        FilesystemMiddleware(),
        SubAgentMiddleware(
            default_subagent_tools=tools,   # NOTE: These tools are piped to the general-purpose subagent.
            subagents=subagents if subagents is not None else [],
            model=model,
            is_async=is_async,
        ),
        SummarizationMiddleware(
            model=model,
            max_tokens_before_summary=120000,
            messages_to_keep=20,
        ),
        AnthropicPromptCachingMiddleware(ttl="5m", unsupported_model_behavior="ignore")
    ]
```


# 我追问
我想知道这种python框架，在落地时候，后台是java建设的，怎么和后台集成？就是假设我算法层，用这些框架搭建了微服务，后台通过Nginx转发各种请求到指定的微服务，那我怎么基于deepagents去搭建这些微服务？


# deepwiki答
## 将 DeepAgents 部署为微服务的架构方案

你的问题是关于如何将基于 DeepAgents 的 Python 服务集成到 Java 后台架构中，通过 Nginx 进行请求转发。<cite/>

DeepAgents 本身是一个 Python 框架，返回的是 LangGraph 图对象 [1](#3-0) 。要将其部署为微服务，你需要在 DeepAgents 之上封装 HTTP 服务层。<cite/>

## 推荐架构方案

```mermaid
graph LR
    Client["客户端/Java后台"]
    Nginx["Nginx"]
    
    subgraph "Python 微服务层"
        FastAPI["FastAPI/Flask<br/>HTTP 服务"]
        DeepAgent["DeepAgents<br/>create_deep_agent()"]
        Checkpointer["Checkpointer<br/>状态持久化"]
    end
    
    Database["数据库<br/>PostgreSQL/Redis"]
    
    Client -->|HTTP Request| Nginx
    Nginx -->|转发| FastAPI
    FastAPI -->|调用| DeepAgent
    DeepAgent -->|状态保存| Checkpointer
    Checkpointer -->|持久化| Database
    FastAPI -->|HTTP Response| Nginx
    Nginx -->|返回| Client
```

<cite/>

## 具体实现方案

### 1. 使用 FastAPI 封装 DeepAgents

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from deepagents import create_deep_agent
from langgraph.checkpoint.postgres import PostgresSaver
import asyncio

app = FastAPI()

# 初始化 DeepAgent（启动时创建）
agent = create_deep_agent(
    tools=[your_tools],
    instructions="你的指令",
    checkpointer=PostgresSaver.from_conn_string("postgresql://...")
)

class AgentRequest(BaseModel):
    thread_id: str
    message: str

class AgentResponse(BaseModel):
    response: str
    todos: list
    files: dict

@app.post("/agent/invoke")
async def invoke_agent(request: AgentRequest):
    """同步调用智能体"""
    try:
        config = {"configurable": {"thread_id": request.thread_id}}
        result = agent.invoke(
            {"messages": [{"role": "user", "content": request.message}]},
            config=config
        )
        return AgentResponse(
            response=result["messages"][-1].content,
            todos=result.get("todos", []),
            files=result.get("files", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/stream")
async def stream_agent(request: AgentRequest):
    """流式调用智能体"""
    from fastapi.responses import StreamingResponse
    
    async def event_generator():
        config = {"configurable": {"thread_id": request.thread_id}}
        async for event in agent.astream(
            {"messages": [{"role": "user", "content": request.message}]},
            config=config
        ):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

<cite/>

### 2. 状态持久化配置

DeepAgents 支持 checkpointer 参数用于状态持久化 [2](#3-1) 。你需要配置持久化存储：

```python
from langgraph.checkpoint.postgres import PostgresSaver

# 使用 PostgreSQL 持久化
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:password@host:5432/dbname"
)

agent = create_deep_agent(
    tools=[your_tools],
    instructions="你的指令",
    checkpointer=checkpointer  # 关键：状态持久化
)
```

<cite/>

这样可以实现：
- 多次请求之间保持对话状态
- `todos` 和 `files` 状态跨请求持久化
- 支持分布式部署（多个微服务实例共享状态）

### 3. Nginx 配置示例

```nginx
upstream deepagent_service {
    server 127.0.0.1:8000;  # Python 微服务地址
    server 127.0.0.1:8001;  # 可以配置多个实例
}

server {
    listen 80;
    
    # 转发到 DeepAgents 微服务
    location /api/agent/ {
        proxy_pass http://deepagent_service/agent/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # 流式响应配置
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }
    
    # 其他 Java 服务
    location /api/java/ {
        proxy_pass http://java_backend:8080/;
    }
}
```

<cite/>

### 4. Java 后台调用示例

```java
// Java 后台通过 HTTP 调用 Python 微服务
@Service
public class DeepAgentService {
    
    @Autowired
    private RestTemplate restTemplate;
    
    public AgentResponse invokeAgent(String threadId, String message) {
        String url = "http://nginx-host/api/agent/invoke";
        
        Map<String, String> request = new HashMap<>();
        request.put("thread_id", threadId);
        request.put("message", message);
        
        ResponseEntity<AgentResponse> response = restTemplate.postForEntity(
            url, 
            request, 
            AgentResponse.class
        );
        
        return response.getBody();
    }
}
```

<cite/>

## 关键注意事项

### 1. 异步工具支持

如果你的工具是异步的（如 MCP 工具），需要使用 `async_create_deep_agent` [3](#3-2) ：

```python
from deepagents import async_create_deep_agent

agent = async_create_deep_agent(
    tools=[async_tool1, async_tool2],
    instructions="你的指令"
)
```

<cite/>

### 2. 会话管理

使用 `thread_id` 来区分不同用户的会话：<cite/>

```python
# 每个用户/会话使用唯一的 thread_id
config = {"configurable": {"thread_id": user_session_id}}
result = agent.invoke({"messages": [...]}, config=config)
```

这样 DeepAgents 会自动管理每个会话的 `todos` 和 `files` 状态。<cite/>

### 3. 人工审核集成

如果需要人工审核工具调用，可以配置 `tool_configs` [4](#3-3) ：

```python
agent = create_deep_agent(
    tools=[your_tools],
    instructions="你的指令",
    tool_configs={
        "sensitive_tool": True,  # 需要人工审核
    },
    checkpointer=checkpointer  # 必须配置 checkpointer
)

# 审核流程
result = agent.invoke({"messages": [...]}, config=config)
# 如果触发审核，返回中断状态
# Java 后台展示给用户，用户批准后：
agent.invoke(Command(resume=[{"type": "accept"}]), config=config)
```

<cite/>

## 部署建议

1. **容器化部署**：使用 Docker 打包 Python 微服务
2. **负载均衡**：Nginx 配置多个 Python 实例
3. **状态共享**：使用 PostgreSQL/Redis 作为 checkpointer 后端
4. **监控告警**：集成 Prometheus + Grafana 监控服务状态
5. **日志收集**：使用 ELK 收集 Python 服务日志

<cite/>

# Notes

DeepAgents 本身不提供 HTTP 服务能力，你需要自己封装 REST API 层。<cite/>推荐使用 FastAPI 因为它原生支持异步，与 DeepAgents 的异步模式兼容 [5](#3-4) 。

关键是要配置 `checkpointer` 参数实现状态持久化 [6](#3-5) ，否则每次请求都是独立的，无法保持对话上下文和 todos/files 状态。

Wiki pages you might want to explore:
- [Overview (langchain-ai/deepagents)](/wiki/langchain-ai/deepagents#1)

### Citations

**File:** README.md (L70-71)
```markdown
The agent created with `create_deep_agent` is just a LangGraph graph - so you can interact with it (streaming, human-in-the-loop, memory, studio)
in the same way you would any LangGraph agent.
```

**File:** README.md (L313-336)
```markdown
```python
from deepagents import create_deep_agent
from langgraph.checkpoint.memory import InMemorySaver

# Create agent with file operations requiring approval
agent = create_deep_agent(
    tools=[your_tools],
    instructions="Your instructions here",
    tool_configs={
        # You can specify a dictionary for fine grained control over what interrupt options exist
        "tool_1": {
            "allow_respond": True,
            "allow_edit": True,
            "allow_accept":True,
        },
        # You can specify a boolean for shortcut
        # This is a shortcut for the same functionality as above
        "tool_2": True,
    }
)

checkpointer= InMemorySaver()
agent.checkpointer = checkpointer
```
```

**File:** README.md (L394-427)
```markdown
## Async

If you are passing async tools to your agent, you will want to use `from deepagents import async_create_deep_agent`
## MCP

The `deepagents` library can be ran with MCP tools. This can be achieved by using the [Langchain MCP Adapter library](https://github.com/langchain-ai/langchain-mcp-adapters).

**NOTE:** You will want to use `from deepagents import async_create_deep_agent` to use the async version of `deepagents`, since MCP tools are async

(To run the example below, will need to `pip install langchain-mcp-adapters`)

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent

async def main():
    # Collect MCP tools
    mcp_client = MultiServerMCPClient(...)
    mcp_tools = await mcp_client.get_tools()

    # Create agent
    agent = async_create_deep_agent(tools=mcp_tools, ....)

    # Stream the agent
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": "what is langgraph?"}]},
        stream_mode="values"
    ):
        if "messages" in chunk:
            chunk["messages"][-1].pretty_print()

asyncio.run(main())
```
```

**File:** src/deepagents/graph.py (L67-68)
```python
    checkpointer: Optional[Checkpointer] = None,
    tool_configs: Optional[dict[str, bool | ToolConfig]] = None,
```

**File:** src/deepagents/graph.py (L87-88)
```python
        checkpointer: Optional checkpointer for persisting agent state between runs.
        tool_configs: Optional Dict[str, HumanInTheLoopConfig] mapping tool names to interrupt configs.
```