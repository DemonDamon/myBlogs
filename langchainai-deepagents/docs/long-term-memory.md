# Long-term memory

> Learn how to extend deep agents with persistent memory across threads

Deep agents come with a local filesystem to offload memory. This filesystem is stored in state and is therefore **transient to a single thread**—files are lost when the conversation ends.

You can extend deep agents with **long-term memory** by providing a LangGraph `Store` and setting `use_longterm_memory=True`. This enables persistent storage that survives across threads and conversations.

## Setup

```python  theme={null}
from deepagents import create_deep_agent
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()  # Or any other Store object
agent = create_deep_agent(
    store=store,
    use_longterm_memory=True
)
```

## How it works

When long-term memory is enabled, deep agents maintain **two separate filesystems**:

### 1. Short-term (transient) filesystem

* Stored in the agent's state
* Persists only within a single thread
* Files are lost when the thread ends
* Accessed through standard paths: `/notes.txt`

### 2. Long-term (persistent) filesystem

* Stored in a LangGraph Store
* Persists across all threads and conversations
* Files survive indefinitely
* Accessed through the special prefix: `/memories/notes.txt`

## The /memories/ path convention

**The key to long-term memory is the `/memories/` path prefix:**

* Files with paths starting with `/memories/` are stored in the Store (persistent)
* Files without this prefix remain in transient state
* All filesystem tools (`ls`, `read_file`, `write_file`, `edit_file`) work with both

```python  theme={null}
# Transient file (lost after thread ends)
agent.invoke({
    "messages": [{"role": "user", "content": "Write draft to /draft.txt"}]
})

# Persistent file (survives across threads)
agent.invoke({
    "messages": [{"role": "user", "content": "Save final report to /memories/report.txt"}]
})
```

## Cross-thread persistence

Files in `/memories/` can be accessed from any thread:

```python  theme={null}
import uuid

# Thread 1: Write to long-term memory
config1 = {"configurable": {"thread_id": str(uuid.uuid4())}}
agent.invoke({
    "messages": [{"role": "user", "content": "Save my preferences to /memories/preferences.txt"}]
}, config=config1)

# Thread 2: Read from long-term memory (different conversation!)
config2 = {"configurable": {"thread_id": str(uuid.uuid4())}}
agent.invoke({
    "messages": [{"role": "user", "content": "What are my preferences?"}]
}, config=config2)
# Agent can read /memories/preferences.txt from the first thread
```

## Use cases

### User preferences

Store user preferences that persist across sessions:

```python  theme={null}
agent = create_deep_agent(
    store=store,
    use_longterm_memory=True,
    system_prompt="""When users tell you their preferences, save them to
    /memories/user_preferences.txt so you remember them in future conversations."""
)
```

### Self-improving instructions

An agent can update its own instructions based on feedback:

```python  theme={null}
agent = create_deep_agent(
    store=store,
    use_longterm_memory=True,
    system_prompt="""You have a file at /memories/instructions.txt with additional
    instructions and preferences.

    Read this file at the start of conversations to understand user preferences.

    When users provide feedback like "please always do X" or "I prefer Y",
    update /memories/instructions.txt using the edit_file tool."""
)
```

Over time, the instructions file accumulates user preferences, helping the agent improve.

### Knowledge base

Build up knowledge over multiple conversations:

```python  theme={null}
# Conversation 1: Learn about a project
agent.invoke({
    "messages": [{"role": "user", "content": "We're building a web app with React. Save project notes."}]
})

# Conversation 2: Use that knowledge
agent.invoke({
    "messages": [{"role": "user", "content": "What framework are we using?"}]
})
# Agent reads /memories/project_notes.txt from previous conversation
```

### Research projects

Maintain research state across sessions:

```python  theme={null}
research_agent = create_deep_agent(
    store=store,
    use_longterm_memory=True,
    system_prompt="""You are a research assistant.

    Save your research progress to /memories/research/:
    - /memories/research/sources.txt - List of sources found
    - /memories/research/notes.txt - Key findings and notes
    - /memories/research/report.md - Final report draft

    This allows research to continue across multiple sessions."""
)
```

## Store implementations

Any LangGraph `BaseStore` implementation works:

### InMemoryStore (development)

Good for testing and development, but data is lost on restart:

```python  theme={null}
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()
agent = create_deep_agent(store=store, use_longterm_memory=True)
```

### PostgresStore (production)

For production, use a persistent store:

```python  theme={null}
from langgraph.store.postgres import PostgresStore
import os

store = PostgresStore(connection_string=os.environ["DATABASE_URL"])
agent = create_deep_agent(store=store, use_longterm_memory=True)
```

## Best practices

### Use descriptive paths

Organize long-term files with clear, hierarchical paths:

```python  theme={null}
# ✅ Good: Organized and descriptive
/memories/user_preferences/language.txt
/memories/projects/project_alpha/status.txt
/memories/research/quantum_computing/sources.txt

# ❌ Bad: Generic and unorganized
/memories/temp.txt
/memories/data.txt
/memories/file1.txt
```

### Document what gets persisted

In system prompts, clarify when to use long-term vs short-term storage:

```python  theme={null}
system_prompt="""You have access to two types of storage:

SHORT-TERM (paths without /memories/):
- Current conversation notes
- Temporary scratch work
- Draft documents

LONG-TERM (paths starting with /memories/):
- User preferences and settings
- Completed reports and documents
- Knowledge that should persist across conversations
- Project state and progress

Always use /memories/ for information that should survive beyond this conversation."""
```

### Isolate storage by assistant ID

For multi-tenant applications, provide an `assistant_id` to isolate storage:

```python  theme={null}
config = {
    "configurable": {
        "thread_id": "thread-123",
    },
    "metadata": {
        "assistant_id": "user-456"  # Namespace isolation
    }
}

agent.invoke({"messages": [...]}, config=config)
```

Each assistant gets its own namespace in the Store, preventing cross-contamination.

### Use persistent stores in production

```python  theme={null}
# ❌ Development only - data lost on restart
store = InMemoryStore()

# ✅ Production - data persists
from langgraph.store.postgres import PostgresStore
store = PostgresStore(connection_string=os.environ["DATABASE_URL"])
```

## Listing files

The `ls` tool shows files from both filesystems:

```python  theme={null}
agent.invoke({
    "messages": [{"role": "user", "content": "List all files"}]
})

# Example output:
# Transient files:
# - /draft.txt
# - /temp_notes.txt
#
# Long-term files:
# - /memories/user_preferences.txt
# - /memories/project_status.txt
```

Files from the Store are prefixed with `/memories/` in listings.

## Limitations

### Store is required

You must provide a Store when enabling long-term memory:

```python  theme={null}
# ❌ This will error
agent = create_deep_agent(use_longterm_memory=True)  # Missing store!

# ✅ Correct
agent = create_deep_agent(
    use_longterm_memory=True,
    store=InMemoryStore()
)
```

### Agents must use correct paths

The agent must learn to use the `/memories/` prefix for persistence. The system prompt teaches this, but the agent must follow the instructions.

### No automatic cleanup

Long-term files persist indefinitely. There's no built-in TTL or automatic cleanup. You'll need to implement cleanup strategies if needed.

***

<Callout icon="pen-to-square" iconType="regular">
  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/deepagents/long-term-memory.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for    real-time answers.
</Tip>
