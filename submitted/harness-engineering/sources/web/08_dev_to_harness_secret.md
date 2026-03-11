# The secret isn't the model. It's the harness. - DEV Community

**URL**: https://dev.to/n_asuy/the-secret-isnt-the-model-its-the-harness-587a

---

## 核心观点

Getting AI agents to write code is not new anymore. The real problem is not how smart the model is. The real problem is that **agents do not have good environments to work in for a long time**.

**Harness Engineering** is the field that works on this problem.

## 行业里程碑

- **Nov 2025**: Anthropic 发布 "Effective harnesses for long-running agents"
- **Feb 2026**: OpenAI 发布 "Harness engineering: leveraging Codex in an agent-first world"
  - 7人团队，5个月，100万行代码，1500个PR
  - 零手工编写源码

> The engineer's job is changing. From "writing code" to **"building environments where agents write good code."**

## Harness Engineering 的两个部分

### 1. Agent Harness（执行端）

The setup that lets agents work well over long sessions:
- Automates environment setup
- Passes progress between sessions using progress files and Git
- Builds one feature at a time
- Runs E2E tests automatically

### 2. Evaluation Harness（质量端）

How you score AI output with numbers, not feelings:
- EleutherAI: 60+ benchmarks
- Inspect AI: 100+ pre-built evaluations
- LLM-as-a-judge: lets AI grade AI
- CI/CD gates and safety testing (MLCommons AILuminate: 59,624 test prompts)

## Anthropic 方法：会话交接

Two-step system:
1. **Setup agent**: makes init.sh and feature list (JSON)
2. **Coding agent**: builds one feature at a time — code, test, commit, repeat

Between sessions: `claude-progress.txt` and Git history carry the work forward.

## OpenAI 方法：仓库级环境

- **AGENTS.md** (~100 lines): sets the rules for the whole repo
- Custom linters and CI enforce rules automatically
- Instead of asking the AI nicely in a prompt, make the tools force the rules

## 共同结论

Both companies reached the same conclusion:
1. Put knowledge in the repo
2. Enforce rules with tools
3. Break work into small steps
4. Leave a trail

## 限制

- Anthropic's method: optimized for full-stack web development, not tested on scientific research or financial modeling
- OpenAI's environment: highly customized for one repo, cannot be copied directly to other projects

## 结论

Models will keep getting smarter. But **even the smartest model cannot sustain long-running development without a well-designed environment**. The difference is not which model you pick. It is **how you build the harness**.

---
**Source**: https://dev.to/n_asuy/the-secret-isnt-the-model-its-the-harness-587a
