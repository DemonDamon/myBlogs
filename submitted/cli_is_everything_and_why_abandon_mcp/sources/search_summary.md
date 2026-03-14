# 搜索结果汇总

## 搜索信息
- 主题：MCP vs CLI——AI Agent 工具接口的辩证分析
- 搜索时间：2026-03-14
- 搜索 Query 列表：
  1. "MCP已死 CLI 当立 Perplexity 放弃 MCP"
  2. "MCP vs CLI AI agent enterprise production trade-offs 2026"
  3. "CLI-Anything HKUDS Making ALL Software Agent-Native 2026"
  4. "Perplexity abandon MCP CLI API Denis Yarats Ask 2026"
  5. "MCP协议 CLI 比较 AI Agent 企业落地 生产环境 2026"
  6. "Eric Holmes MCP is dead long live the CLI"
  7. "Scalekit MCP vs CLI benchmark AI agent cost reliability"
  8. "CircleCI MCP vs CLI inner loop outer loop"

## 高价值页面（已爬取）
| # | 标题 | URL | 来源类型 | 价值评估 |
|---|------|-----|---------|---------|
| 1 | MCP is dead. Long live the CLI — Eric Holmes | ejholmes.github.io | 技术博客(原始出处) | 极高 |
| 2 | MCP已死，CLI当立！Perplexity首先放弃使用MCP | aitntnews.com | 中文新闻 | 高 |
| 3 | Perplexity CTO Moves Away from MCP Toward APIs and CLIs | awesomeagents.ai | 新闻报道 | 高 |
| 4 | MCP vs. CLI for AI-native development — CircleCI | circleci.com/blog | 技术博客 | 极高(inner/outer loop框架) |
| 5 | MCP is up to 32× more expensive than CLI — Scalekit | scalekit.com/blog | 技术博客+Benchmark | 极高(含B2B分析) |
| 6 | MCP vs CLI Tools: Which is best for production — Runlayer | runlayer.com/blog | 技术博客 | 高(single-tool MCP方案) |
| 7 | Bye-Bye MCP: Says Perplexity and Cloudflare — Medium | medium.com | 技术博客 | 中(付费墙) |
| 8 | GitHub - HKUDS/CLI-Anything README | github.com | 项目文档 | 极高 |

## 补充搜索结果（WebSearch）
| # | 标题 | URL | 关键摘要 |
|---|------|-----|---------|
| 1 | CLI-Based Agents vs MCP: The 2026 Showdown | Medium | CLI ~200 token/交互 vs MCP schema bloat |
| 2 | Why CLI Tools Are Beating MCP for AI Agents | jannikreinhard.com | 50 设备查询 CLI 4,150 tokens vs MCP 145,000 tokens |
| 3 | MCP Token Cost Problem: Why AI Teams Switch to CLI | buildmvpfast.com | MCP schema 每请求 $0.27，万次/日 = $2,700/天 |
| 4 | MCP vs CLI AI Agents: The Answer Is Both | aiproductivity.ai | Skills 抽象层：lazy-loading ~300 tokens |
| 5 | 港大开源了CLI-Anything！ | news.qq.com | 中文报道，11.7k stars |

## 关键数据点摘录
- **Scalekit Benchmark**: CLI 1,365 tokens vs MCP 44,026 tokens (32×) 最简任务；MCP 28% 失败率
- **月度成本**: CLI ~$3.20 vs MCP ~$55.20（10,000次操作）
- **CircleCI 框架**: Inner Loop = CLI，Outer Loop = MCP
- **Scalekit B2B 分析**: CLI 无法提供 per-user OAuth / tenant isolation / audit trail
- **MCP Gateway**: Schema filtering 可减少 ~90% token 开销，接近 CLI 效率
- **CLI-Anything**: 11 个软件，1,508 个测试，100% 通过率，11.7k stars
