# ZeroClaw GitHub 代码分析

## 仓库信息
- **仓库**: https://github.com/zeroclaw-labs/zeroclaw
- **组织**: zeroclaw-labs
- **最新提交**: cd0dd1347691fee528854160d646d8452d0b4f9c
- **主语言**: Rust

## 目录结构

```
zeroclaw/
├── src/
│   ├── agent/           # Agent 核心逻辑
│   ├── approval/       # 操作员批准流程
│   ├── channels/       # 消息通道（Telegram、Discord 等）
│   ├── config/         # 配置管理
│   ├── cron/           # 定时任务
│   ├── daemon/          # 守护进程
│   ├── doctor/         # 诊断工具
│   ├── gateway/        # Webhook 网关服务器
│   ├── hardware/       # 硬件外设（STM32、树莓派 GPIO）
│   ├── health/         # 健康检查
│   ├── heartbeat/       # 心跳机制
│   ├── identity/        # 身份系统（OpenClaw、AIEOS）
│   ├── integrations/    # 50+ 集成服务
│   ├── memory/         # 记忆系统（SQLite、Lucid、Markdown）
│   ├── migration/       # 数据迁移
│   ├── observability/   # 可观测性（日志、指标）
│   ├── onboard/        # 快速配置向导
│   ├── peripherals/      # 外设管理
│   ├── providers/       # 23+ AI 提供商
│   ├── rag/            # RAG 检索增强
│   ├── runtime/         # 运行时适配器
│   ├── security/        # 安全策略
│   ├── service/         # 系统服务管理
│   ├── skills/          # 技能加载器
│   ├── tools/           # 工具执行（shell、文件、浏览器等）
│   └── tunnel/          # 隧道服务（Cloudflare、Tailscale 等）
├── Cargo.toml          # Rust 项目配置
├── Cargo.lock           # 依赖锁定
├── Dockerfile           # Docker 容器配置
├── docker-compose.yml   # Docker Compose 配置
└── ...
```

## 核心架构设计

### 1. Trait 驱动架构（8 个核心 Trait）

| Trait | 路径 | 功能 | 说明 |
|-------|--------|------|------|
| `Provider` | `src/providers/traits.rs` | AI 模型提供方 | 支持 23+ 提供商（OpenRouter、Anthropic、OpenAI、DeepSeek 等）|
| `Channel` | `src/channels/traits.rs` | 消息通道 | CLI、Telegram、Discord、Slack、iMessage、Matrix、WhatsApp、Webhook |
| `Tool` | `src/tools/traits.rs` | 工具执行能力 | shell、file_read、file_write、memory_store、browser_open 等 |
| `Memory` | `src/memory/traits.rs` | 记忆后端 | SQLite（向量 + 混合搜索）、Lucid、Markdown、None |
| `Observer` | `src/observability/traits.rs` | 可观测性 | Noop、日志、Prometheus |
| `Runtime` | `src/runtime/traits.rs` | 运行时适配器 | Native（默认）、Docker（沙箱）、WASM（计划中）|
| `Security` | - | 安全策略 | 配对码、白名单、沙箱、访问控制 |
| `Identity` | - | 身份系统 | OpenClaw（Markdown）、AIEOS（JSON） |
| `Tunnel` | `src/tunnel/traits.rs` | 隧道服务 | Cloudflare、Tailscale、ngrok、自定义 |

### 2. 记忆系统实现

ZeroClaw 的记忆系统实现**零外部依赖**的混合搜索：

| 组件 | 实现 | 特性 |
|------|------|------|
| 向量存储 | SQLite BLOB 列 | 存储嵌入向量 |
| 全文搜索 | SQLite FTS5 虚拟表 | BM25 评分 |
| 混合搜索 | 自定义权重函数 `vector.rs` | 向量相似度 × 0.7 + 关键词 × 0.3 |
| 嵌入提供 | `EmbeddingProvider` trait | OpenAI、自定义 URL、noop |
| 响应缓存 | 可选 | LRU 缓存，减少重复计算 |

### 3. 安全设计

| 层级 | 机制 | 说明 |
|------|------|------|
| 网关层 | `src/gateway/` | 默认绑定 127.0.0.1，需配对码或隧道才能公开 |
| 配对码 | 6 位一次性代码 | `/pair` 端点交换 bearer token |
| 文件沙箱 | `workspace_only` | 文件操作限制在工作区，屏蔽系统目录 |
| 命令白名单 | 14+ 目录被硬编码屏蔽 | `/etc`、`/root`、`/proc` 等 |
| 敏感文件 | 4 个敏感文件被屏蔽 | `.env`、`config.toml` 等 |
| 默认策略 | 拒绝一切 | 空白名单 = 拒绝，必须显式允许 |

### 4. 命令系统

| 层级 | 组件 | 说明 |
|------|------|------|
| 只读模式 | [default] | Agent 只能读，不能执行 shell 或写入文件 |
| 监督模式 | [default] | Agent 在白名单内执行 |
| 完全模式 | [configurable] | Agent 有完全访问权限 |
| 命令列表 | 默认 | `["git", "npm", "cargo", "ls", "cat", "grep"]` |

### 5. 性能优化策略

| 策略 | 说明 |
|------|------|
| `codegen-units=1` | 编译时减少代码大小 | 针对 Raspberry Pi 等低内存设备 |
| `lto = "fat"` | 链接时优化 | 移除未使用代码和符号 |
| 依赖选择 | 最小化 | 避免臃肿依赖，优先使用标准库 |

## 关键代码片段

### 主入口 (src/main.rs)

```rust
#[tokio::main]
async fn main() -> Result<()> {
    // 初始化日志系统
    // 解析命令行参数
    // 加载配置
    // 根据命令路由到相应子模块
    // 支持：onboard、agent、gateway、daemon、doctor、status 等
}
```

### 记忆工厂 (src/memory/mod.rs)

```rust
pub fn create_memory(
    config: &MemoryConfig,
    workspace_dir: &Path,
    api_key: Option<&str>,
) -> anyhow::Result<Box<dyn Memory>>
```

支持三种后端：
1. **SQLite** - 向量数据库 + FTS5 全文搜索 + 混合查询
2. **Lucid** - 本地向量引擎，适合大规模数据
3. **Markdown** - 简单文件存储，无持久化

### 模块导出 (src/lib.rs)

```rust
pub mod agent;
pub mod approval;
pub mod channels;
pub mod config;
pub mod cost;
pub mod cron;
pub mod daemon;
pub mod doctor;
pub mod gateway;
pub mod hardware;
pub mod health;
pub mod heartbeat;
pub mod identity;
pub mod integrations;
pub mod memory;
pub mod migration;
pub mod observability;
pub mod onboard;
pub mod peripherals;
pub mod providers;
pub mod rag;
pub mod runtime;
pub mod security;
pub mod service;
pub mod skills;
pub mod tools;
pub mod tunnel;
pub mod util;
```

## 编译产物

- **二进制大小**: 3.4 MB
- **启动时间**: < 10ms
- **内存占用**: < 5MB

## 工程协议要点（CLAUDE.md）

### KISS 原则
- **Keep It Simple, Stupid** - 优先简单控制流，避免元编程
- **YAGNI (You Ain't Gonna Need It)** - 不添加没有实际用例的功能
- **DRY + Rule of Three** - 避免重复，仅在三次使用后提取

### 安全原则
- **Secure by Default + Least Privilege** - 默认拒绝，显式允许
- **所有路径必须通过安全检查**
- **禁止记录敏感信息**

### 架构边界
- **模块职责单一** - 每个模块专注一个关注点
- **依赖方向向内** - 具体集成依赖 trait/配置层
- **避免跨子系统耦合** - 提供商不应直接导入 channel 内部

## 安全要点（SECURITY.md）

### 漏洞报告
- **请勿公开 GitHub issue** - 通过私有渠道或官方报告流程

### 受保护资产
| 类型 | 示例 |
|------|------|
| API 密钥 | `ZEROCLAW_API_KEY` |
| 配对码 | `ZEROCLAW_PAIR_CODE` |
| 敏感文件 | `.env`、`config.toml`、密钥存储 |

### 攻击场景
- 路径遍历 (`../../etc/passwd`)
- 命令注入 (`rm -rf /`)
- 工作区逃逸（通过 symlinks 或绝对路径）

## 依赖分析

根据 `Cargo.lock`，主要依赖包括：

- **HTTP 客户端**: `reqwest` / `hyper`
- **异步运行时**: `tokio`
- **序列化**: `serde` / `toml`
- **加密**: `rustls` (用于密码加密)
- **SQLite**: `rusqlite`
- **日志**: `tracing` / `tracing-subscriber`
- **CLI**: `clap`

## 待深入研究的文件

1. `src/providers/mod.rs` - 提供商实现细节
2. `src/channels/mod.rs` - 通道集成逻辑
3. `src/tools/mod.rs` - 工具执行和安全
4. `src/memory/sqlite.rs` - SQLite 记忆实现
5. `src/agent/loop.rs` - Agent 主循环逻辑
