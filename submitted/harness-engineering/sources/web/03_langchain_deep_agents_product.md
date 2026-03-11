# LangChain Deep Agents: Build Agents for Complex, Multi-Step Tasks

**URL**: https://www.langchain.com/deep-agents

---

Deep Agents is an open source agent harness built for long-running tasks. It handles planning, context management, and multi-agent orchestration for complex work like research and coding.

## Why use Deep Agents?

### Designed for autonomous agents

Agents are taking on increasingly complex work over long time horizons, like research, coding, and multi-step workflows. Deep Agents provides the primitives for these patterns:

- **Persist knowledge across sessions**: Virtual filesystem stores system prompts, skills, and long-term memory
- **Delegate work in parallel**: Spawn subagents for independent subtasks, each with isolated context
- **Break down complex objectives**: Planning tools let agents decompose tasks, track progress, and adapt as they learn

### Native context management

Context management is critical for long-running agents, and hard to get right. Deep Agents includes middleware that helps agents:
- Compress conversation history
- Offload large tool results
- Isolate context with subagents
- Use prompt caching to reduce latency and cost

### Model neutral with maximum configurability

Deep Agents is a batteries-included, general purpose agent harness. Use any model provider, manage state, and add human-in-the-loop when you need it. Tracing and deployment work natively with LangSmith.

### Code with Deep Agents CLI

Deep Agents is available as an SDK and CLI, so you can use it in your codebase or run it directly in your terminal.

## FAQs for Deep Agents

### What is an agent harness?

Agent harnesses are opinionated agent frameworks with that come batteries included with built-in tools and capabilities that make building sophisticated, long-running agents easier.

### When should I use Deep Agents vs other LangChain frameworks?

- **Use Deep Agents** when you want to build an autonomous agent to handle complex, non-deterministic, and long running tasks.
- **Choose LangGraph** when you want low-level control for building stateful, long-running workflows and agents.
- **Choose LangChain** when you want a quick way to get started and to standardize how teams build agent patterns.

### How does Deep Agents compare to other agent harnesses?

Visit docs for a detailed comparison of features across Deep Agents, OpenCode, and Claude SDK.

---
**Source**: https://www.langchain.com/deep-agents
