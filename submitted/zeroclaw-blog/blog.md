# ZeroClaw：5MB 内存跑起来的全自主 AI 助手

> **零开销 · 零妥协 · 100% Rust**

OpenClaw 大家已经很熟了，但你有没有想过：同样的 AI 助手能力，能不能跑在一块 $10 的树莓派上？ZeroClaw 用 Rust 重写了整个故事。

![ZeroClaw vs OpenClaw](images/zeroclaw_vs_openclaw.png)

## 一句话理解 ZeroClaw

用 Rust 从零实现的 OpenClaw 替代品——**不到 1% 的内存、200 倍的启动速度**，功能不缩水。

| 指标 | ZeroClaw | OpenClaw | 差距 |
|------|----------|----------|------|
| **内存占用** | ~7.8 MB RSS | 1.52 GB RSS | **200x** |
| **启动时间** | < 10 ms | 3.31 s | **330x** |
| **二进制大小** | 3.4 MB | 28 MB dist | **8x** |
| **运行硬件** | $10 树莓派 | Mac Mini $599+ | **60x 成本** |
| **1,050 测试** | ✅ | — | — |

## 三个最与众不同的设计

### 1. 零外部依赖的混合搜索记忆

这是 ZeroClaw 最硬核的创新。**没有 Pinecone、没有 Elasticsearch、没有 LangChain**，纯 SQLite 实现完整 RAG：

| 搜索层 | 实现 | 说明 |
|--------|------|------|
| **向量搜索** | SQLite BLOB + 余弦相似度 | 支持 OpenAI/Cohere 等嵌入 API |
| **关键词搜索** | FTS5 虚拟表 + BM25 | 倒排索引，高亮片段提取 |
| **混合融合** | 向量 × 0.7 + BM25 × 0.3 | 自定义权重，兼顾语义和精确匹配 |

附带 Markdown-aware chunking、embedding 缓存（LRU 淘汰）、安全重建索引（原子 Upsert/Delete/Reindex）。整个记忆系统就是一个 `.db` 文件——备份就是复制一个文件。

### 2. 8 个 Trait 驱动的全热插拔架构

不是"支持插件"，而是**一切皆可替换**。ZeroClaw 用 Rust trait 系统把整个框架拆成 8 个正交维度：

```
Provider  → 22+ AI 供应商（OpenRouter/Anthropic/Ollama/DeepSeek...）
Channel   → Telegram/Discord/Slack/iMessage/Matrix/Webhook/CLI
Memory    → SQLite 混合搜索 / Lucid / Markdown
Tool      → Shell/文件/浏览器/Composio 1000+ OAuth
Security  → 配对码/白名单/沙箱/速率限制
Runtime   → Native / Docker 沙箱
Tunnel    → Cloudflare/Tailscale/ngrok/自定义
Observer  → noop/log/multi
```

想换 AI 模型？改一行 TOML。想接 Discord？实现一个 trait。**技术选型从一次性决策变成了持续演进。**

### 3. 默认拒绝的多层安全体系

不是事后加安全，而是**安全是第一层**。请求进来的第一件事不是处理业务，而是过五关：

1. **Gateway Pairing** — 6 位 OTP + bearer token，常量时间比较防时序攻击
2. **Auth Gate** — 通道白名单 + webhook secret
3. **Rate Limiter** — 滑动窗口 + 每日成本上限
4. **Filesystem Sandbox** — path jail + null byte 拦截 + symlink 逃逸检测 + 系统目录屏蔽
5. **Encrypted Secrets** — XOR + 本地密钥文件（0600 权限）

沙箱三级权限：`ReadOnly` → `Supervised` → `Full`，默认 `Supervised + workspace-only`。

## 完整架构一览

![ZeroClaw 架构图](images/zeroclaw架构图.png)

从上到下：
- **顶层**：Chat Apps → Security Layer → Agnostic Tunnel → 22+ AI Providers
- **核心**：Agent Loop（Message In → Memory Recall → LLM → Tools → Memory Save → Response Out）
- **底层**：自研 Memory Search Engine、Sandbox 沙箱、Heartbeat & Cron 定时任务
- **引导**：7 步 Setup Wizard，60 秒内完成配置

## 快速上手

```bash
git clone https://github.com/nichochar/zeroclaw.git && cd zeroclaw
cargo build --release --locked

# 交互式引导（推荐）
zeroclaw onboard --interactive

# 开聊
zeroclaw agent -m "Hello, ZeroClaw!"

# 全自主守护进程
zeroclaw daemon
```

## 谁适合用？

| ✅ 适合 | ❌ 不适合 |
|---------|----------|
| 个人开发者 / AI 爱好者 | 企业级多租户 SaaS |
| 树莓派 / 边缘设备 / 低配 VPS | 10GB+ 历史数据的大规模 RAG |
| 数据隐私敏感，不愿上云 | 需要原生 GUI 的场景 |
| 多模型对比切换 | 复杂 ERP/CRM 系统集成 |
| 学习 Rust + AI Agent 架构 | 高并发写入（SQLite 写锁瓶颈） |

## 一句话总结

ZeroClaw 不是"砍了功能的 OpenClaw"，而是用 Rust 证明了一件事：**真正的技术突破不是堆资源，是把资源需求降到极致**。3.4MB 二进制、7.8MB 内存、10ms 启动——在 $10 的硬件上跑一个功能完整的 AI 助手，这就是 ZeroClaw 的答案。

**参考资源**：[GitHub 仓库](https://github.com/nichochar/zeroclaw) · [CLAUDE.md 工程协议](https://github.com/nichochar/zeroclaw/blob/main/CLAUDE.md) · [SECURITY.md](https://github.com/nichochar/zeroclaw/blob/main/SECURITY.md)

**标签**：`#AI` `#Rust` `#ZeroDependency` `#Performance` `#EdgeComputing` `#OpenClaw替代`
