# Improving Deep Agents with harness engineering - LangChain

**URL**: https://blog.langchain.com/improving-deep-agents-with-harness-engineering/  
**Published**: 2026

---

## TLDR

Our coding agent went from Top 30 to Top 5 on Terminal Bench 2.0. We only changed the harness. Here's our approach to harness engineering (teaser: self-verification & tracing help a lot).

## The Goal of Harness Engineering

The goal of a harness is to **mold the inherently spiky intelligence of a model for tasks we care about**. Harness Engineering is about systems, you're building tooling around the model to optimize goals like task performance, token efficiency, latency, etc. Design decisions include the system prompt, tool choice, and execution flow.

At LangChain, we use Traces to understand agent failure modes at scale.

## 实验设置与 Harness 的可调参数

We used Terminal Bench 2.0, a now standard benchmark to evaluate agentic coding. It has 89 tasks across domains like machine learning, debugging, and biology.

### The Knobs we can Turn

An agent harness has a lot of knobs:
- System prompts
- Tools
- Hooks/middleware
- Skills
- Sub-agent delegation
- Memory systems

We deliberately compress the optimization space and focus on three: **System Prompt, Tools, and Middleware** (our term for hooks around model and tool calls).

## 性能提升结果

| 阶段 | 得分 | 排名 | 说明 |
|------|------|------|------|
| 基线 | 52.8% | 30+ | 默认 harness + GPT-5.2-Codex |
| 优化后 | 66.5% | Top 5 | 仅调整 harness，模型不变 |
| 提升 | +13.7 | - | 纯 harness 工程带来的改进 |

## Trace Analyzer Skill

We wanted trace analysis to be repeatable so we made it into an Agent Skill. This serves as our recipe to analyze errors across runs and make improvements to the harness. The flow is:

1. **Aggregate feedback** and make targeted changes to the harness.
2. **Spawn parallel error analysis agents** → main agent synthesizes findings + suggestions
3. **Fetch experiment traces** from LangSmith

This works similarly to boosting which focuses on mistakes from previous runs.

## 实际有效的改进措施

### Build & Self-Verify

Today’s models are exceptional self-improvement machines. Self-verification allows agents to self-improve via feedback within a run.

The most common failure pattern was that the agent wrote a solution, re-read its own code, confirmed it looks ok, and stopped. Testing is a key part of autonomous agentic coding.

We added guidance to the system prompt on how to approach problem solving:

1. **Fix**: Analyze any errors, revisit the original spec, and fix issues.
2. **Verify**: Run tests, read the full output, compare against what was asked (not against your own code).
3. **Build**: Implement the plan with verification in mind. Build tests, if they don't exist and test both happy paths and edge cases.
4. **Planning & Discovery**: Read the task, scan the codebase, and build an initial plan based on the task specification and how to verify the solution.

We use a **PreCompletionChecklistMiddleware** that intercepts the agent before it exits and reminds it to run a verification pass against the Task spec.

### Giving Agents Context about their Environment

1. **Time Budgeting**: We inject time budget warnings to nudge the agent to finish work and shift to verification. Agents are famously bad at time estimation so this heuristic helps.

2. **Teaching Agents to Write Testable Code**: We add prompting say their work will be measured against programatic tests, similar to when committing code.

3. **Directory Context & Tooling**: A LocalContextMiddleware runs on agent start to map the cwd and other parent+children directories.

### Encouraging Agents to Step Back & Reconsider Plans

Agents can be myopic once they've decided on a plan which results in "doom loops" that make small variations to the same broken approach (10+ times in some traces).

We use a **LoopDetectionMiddleware** that tracks per-file edit counts via tool call hooks. It adds context like "...consider reconsidering your approach" after N edits to the same file.

### Choosing How Much Compute to Spend on Reasoning

We found that reasoning helps with planning to fully understand the problem. As a heuristic, we choose a **xhigh-high-xhigh "reasoning sandwich"** as a baseline:
- Planning: xhigh reasoning
- Implementation: high reasoning
- Verification: xhigh reasoning

Running only at xhigh scored poorly at 53.9% due to agent timeouts compared to 63.6% at high.

## Practical Takeaways for Building Agent Harnesses

1. **Tailor Harnesses to Models**: Codex and Claude prompting guides show that models require different prompting. Running a few rounds of harness iterations for your task helps maximize agent performance.

2. **Detect and fix bad patterns in the short term**: The job of the harness designer is to design around today's shortcomings while planning for smarter models in the future.

3. **Tracing as a feedback signal**: Traces allow agents to self-evaluate and debug themselves.

4. **Help agents self-verify their work**: Models are biased towards their first plausible solution. Prompt them aggressively to verify their work by running tests.

5. **Context Engineering on Behalf of Agents**: Onboarding models with context like directory structures, available tools, coding best practices, and problem solving strategies helps reduce the error surface.

---
**Source**: https://blog.langchain.com/improving-deep-agents-with-harness-engineering/
