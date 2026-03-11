# Terminal Bench 2.0 Leaderboard

**URL**: https://www.tbench.ai/leaderboard/terminal-bench/2.0

---

## 关键发现

### Deep Agents 性能数据

| 指标 | 数值 |
|------|------|
| **排名** | 第14名 |
| **Agent** | Deep Agents |
| **模型** | GPT-5.2-Codex |
| **准确率** | 66.5% ± 3.1 |
| **组织** | LangChain |
| **日期** | 2026-02-12 |

### LangChain Harness 优化历程

| 阶段 | 得分 | 排名 | 说明 |
|------|------|------|------|
| 基线 | 52.8% | 30+ | 默认 harness |
| 优化后 | 66.5% | Top 5 | 仅调整 harness |
| 提升 | +13.7 | - | 纯 harness 工程 |

### 排行榜前20（节选）

| 排名 | Agent | 模型 | 准确率 | 组织 |
|------|-------|------|--------|------|
| 1 | Forge Code | Gemini 3.1 Pro | 78.4% ± 1.8 | Forge Code |
| 2 | Droid | GPT-5.3-Codex | 77.3% ± 2.2 | Factory |
| 3 | Simple Codex | GPT-5.3-Codex | 75.1% ± 2.4 | OpenAI |
| 4 | Terminus-KIRA | Gemini 3.1 Pro | 74.8% ± 2.6 | KRAFTON AI |
| 5 | Terminus-KIRA | Claude Opus 4.6 | 74.7% ± 2.6 | KRAFTON AI |
| ... | ... | ... | ... | ... |
| 14 | **Deep Agents** | **GPT-5.2-Codex** | **66.5% ± 3.1** | **LangChain** |
| ... | ... | ... | ... | ... |
| 38 | Claude Code | Claude Opus 4.6 | 54.0% ± 2.9 | Anthropic |

### Benchmark 说明

Terminal Bench 2.0 包含 **89 个任务**，跨域：
- Software engineering
- Machine learning
- Debugging
- Biology

使用 Harbor 框架在容器化环境（Daytona/E2B）中运行评估。

---
**Source**: https://www.tbench.ai/leaderboard/terminal-bench/2.0
