# 大纲：MCP 已死？全面拥抱 CLI？—— 一份给 toB 团队的辩证指南

## 核心立意
不做"MCP 已死"的跟风党，也不做 MCP 的盲目拥护者。以 Benchmark 数据和 CLI-Anything 项目为证据，给出 toB 场景下"CLI 为主 + MCP Gateway 兜底"的务实技术选型路径。

---

## 1. 引言：一场 AI Agent 接口之争正在上演（~400字）
- 新闻钩子：Perplexity CTO Denis Yarats 在 Ask 2026 宣布放弃 MCP → 转向 API+CLI
- Y Combinator CEO Garry Tan 也直言"MCP sucks"
- 引出核心问题：MCP 真的该死吗？CLI 能一统天下吗？toB 团队该怎么选？
- **配图**: images/decision_tree_cli_vs_mcp.png（自绘决策树）

## 2. MCP 的原罪：不可承受之"重"（~700字）
### 2.1 线性上下文成本——最致命的问题
- Schema bloat：GitHub MCP Server 43 个工具 schema 全量注入
- Scalekit 实测数据：CLI 1,365 tokens vs MCP 44,026 tokens（32×），最简任务
- 月度成本：CLI ~$3.20 vs MCP ~$55.20（10K ops）
- **配图**: images/24ce739d19b6fc29ea1a6841b8c85afd.png（Scalekit token benchmark）

### 2.2 可靠性之痛
- MCP 28% 失败率（TCP 超时） vs CLI 100%
- 初始化不稳定，MCP server 进程管理噩梦
- 认证摩擦：多工具多次 re-auth
- **配图**: images/4b31692e9583d62c8369b38e9a4a708d.png（MCP 失败率图）

### 2.3 Eric Holmes 的一线观察
- CLI 可组合（pipe/jq/grep） vs MCP 只能靠上下文或服务端自定义
- 可调试性：出错时 run 同一命令 vs 翻 JSON transport log
- Auth 已有成熟体系（aws sso / gh auth / kubeconfig）

## 3. CLI 的文艺复兴：港科大 CLI-Anything 的启示（~900字）
### 3.1 项目定位与核心理念
- "一条命令把任意 GUI 软件变成 Agent 可控的 CLI 工具"
- Prompt 驱动的方法论框架（不是可执行的 pipeline 引擎）
- **配图**: images/6d311563391e3cd575b90b4390d42664.png（CLI-Anything Teaser）

### 3.2 7-Phase Pipeline：从源码到可用 CLI
- Analyze → Design → Implement → Plan Tests → Write Tests → Document → Publish
- 关键创新：HARNESS.md 作为 SOP，由 Agent 自主执行
- 已覆盖 11 个专业软件（GIMP/Blender/LibreOffice/OBS/Audacity 等），1,508 测试 100% 通过
- **配图**: images/b98e5b2a94fa9d89fee50b69c32651cc.png（CLI-Anything Architecture）

### 3.3 关键设计细节（引用源码分析）
- Click CLI + REPL 双模式（`invoke_without_command=True`）
- `--json` flag：Agent 消费 JSON，人类看表格
- PEP 420 命名空间包：多 CLI 无冲突共存
- Backend Wrapper：调用真实软件引擎，非"重实现"
- ReplSkin：统一 REPL 体验

### 3.4 CLI-Anything 证明了什么？
- CLI 是 LLM 的"母语"——训练数据中 man pages、Stack Overflow、GitHub repos 的海量 shell 用法
- 零 schema 开销，Agent 直接 `--help` 自发现
- 生成的 CLI 可组合、可调试、pip install 即用

## 4. 且慢——MCP 真的一无是处吗？（~800字）
### 4.1 Inner Loop vs Outer Loop（CircleCI 框架）
- Inner Loop（本地开发迭代）→ CLI 完胜：速度、token 效率、训练数据熟悉度
- Outer Loop（CI/CD、外部系统协调）→ MCP 有价值：认证、结构化响应、发现、会话状态
- **配图**: images/f296730b5e1c27260aab86557dd029ea.png（CircleCI 内外循环图）

### 4.2 Scalekit 的灵魂拷问：你的 Agent 为谁服务？
- 核心区分：**开发者自用** vs **代客户操作**
- CLI 的致命短板——当 Agent 跨越"服务自己"到"服务客户"的边界：
  - 无 per-user OAuth（一个 token 对应一个人）
  - 无租户隔离（Acme 的数据泄漏到 Globex）
  - 无审计日志（企业安全审计无法交差）
  - 无同意流（用户无法授权/撤销）
- OpenClaw 的前车之鉴：10,000+ 暴露实例、12% 恶意社区 skills、770,000 个可被劫持的 agent
- **配图**: images/536c754b664dc680c147c48b93360364.png（多租户身份层示意图）

### 4.3 Runlayer 的 Single-Tool MCP 思路
- 不暴露 40 个工具，只暴露 1 个 Python/JS 编程接口
- Agent 用训练数据中的编程语言"说话"，避免 CLI 的语法猜测
- Context 小、安全可控、可审计

## 5. toB 落地的务实解法：CLI 为矛，MCP Gateway 为盾（~800字）
### 5.1 分层架构决策
- **个人/团队内部工具** → CLI + Skills（800 token 的 tips 文件）
  - 最高效、最可靠、最低成本
- **SaaS 产品（代客户操作）** → MCP 的 OAuth 模型不可避免
  - 但不要直连 43-tool MCP Server
- **多租户企业级** → MCP Gateway 是正解
  - Schema 过滤：43 tools → 2-3 相关工具，减 90% token
  - 连接池：28% 失败率 → ~1%
  - 集中认证：一处管理 token 刷新、scope 执行、审计日志
- **配图**: images/a63ac20fc788477931f5ecd356a3d712.png（MCP Gateway 架构图）

### 5.2 具体建议矩阵
| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 开发者自用/内部工具 | CLI + Skills | 效率最高，$3/月 |
| SaaS 产品 | MCP + Gateway | 需 OAuth/隔离/审计 |
| 已有 CLI 的系统 | CLI-Anything + Gateway 桥接 | 两全其美 |
- **配图**: images/6fe5500b842df9d06f92ca609e25be66.png（决策框架图）

### 5.3 CLI-Anything 在 toB 中的落地路径
- 用 CLI-Anything 为内部专业软件生成 CLI harness
- 在 CI/CD 等内循环中直接使用 CLI
- 在面向客户的外循环中，通过 MCP Gateway 包装 CLI
- 关键：不要二选一，而是在正确的层选正确的工具

## 6. 总结：不要站队，要解题（~400字）
- "MCP 已死"是情绪，"CLI 一统天下"是幻想
- 真正的问题是：**谁在用你的 Agent？用在哪个环节？**
- CLI-Anything 证明了 CLI 路线的可行性和优越性（尤其在内循环）
- MCP 的价值在于治理（尤其在多租户外循环）
- toB 团队的正确姿势：CLI 为 default，MCP Gateway 为桥梁
- 最后引用 Eric Holmes："最好的工具是人类和机器都好用的工具。CLI 经历了几十年的设计迭代，已经是一个足够好的抽象层。"

---

## 图文配对汇总

| 章节 | 图片 | 类型 | 用途 |
|------|------|------|------|
| 1-引言 | decision_tree_cli_vs_mcp.png | 自绘 | 决策树总览 |
| 2.1 | 24ce739d19b6fc29ea1a6841b8c85afd.png | Scalekit 原图 | Token benchmark |
| 2.2 | 4b31692e9583d62c8369b38e9a4a708d.png | Scalekit 原图 | 失败率对比 |
| 3.1 | 6d311563391e3cd575b90b4390d42664.png | CLI-Anything 原图 | 项目 Teaser |
| 3.2 | b98e5b2a94fa9d89fee50b69c32651cc.png | CLI-Anything 原图 | 架构图 |
| 4.1 | f296730b5e1c27260aab86557dd029ea.png | CircleCI 原图 | 内外循环 |
| 4.2 | 536c754b664dc680c147c48b93360364.png | Scalekit 原图 | 多租户身份 |
| 5.1 | a63ac20fc788477931f5ecd356a3d712.png | Scalekit 原图 | Gateway 架构 |
| 5.2 | 6fe5500b842df9d06f92ca609e25be66.png | Scalekit 原图 | 决策框架 |
