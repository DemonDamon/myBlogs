# CoPaw vs OpenClaw：个人 AI 助理的两条技术路线

2026 年 2 月 14 日，阿里云通义团队推出 CoPaw，直接对标年初火了一把的 OpenClaw。两款产品定位一致——不是聊天框里的问答机器人，而是**跑在你自己环境里、连着日常软件、能按节奏主动干活**的 AI 助理。

有意思的是，CoPaw 并非"从零造轮子"。官方文档里明确写着：**记忆架构受 OpenClaw 启发，Prompt 系统设计也受 OpenClaw 启发**，甚至部分内置技能直接来自 OpenClaw 和 Anthropic 的开源仓库。这让两者的关系更像"站在巨人肩膀上的迭代"，而非简单的竞品对抗。

本文基于 CoPaw 官方文档（9 篇）和 OpenClaw 项目源码，做一次技术层面的拆解。

![OpenClaw vs CoPaw 技术对比](images/OpenClaw%20vs%20CoPaw%20技术对比信息图-lovartai.png)
*OpenClaw 与 CoPaw 核心技术对比一览*

---

## 先看结论

| 你的需求 | 推荐 | 一句话理由 |
|----------|------|-----------|
| 数据必须自控、预算有限 | **OpenClaw** | 完全开源、本地优先、MIT 协议 |
| 不想折腾环境、三条命令跑起来 | **CoPaw** | `pip install copaw` → `copaw init` → `copaw app` |
| 海外渠道（WhatsApp / Telegram / Slack） | **OpenClaw** | 12+ 渠道官方支持 |
| 国内办公（钉钉 / 飞书 / QQ） | **CoPaw** | 官方原生支持，多模态收发全覆盖 |
| 要上云、弹性扩容、企业合规 | **CoPaw** | 魔搭一键云端，阿里云生态打通 |
| 高度定制、爱折腾 | **OpenClaw** | 技能可编程、ClawHub 生态 |

---

## 一、技术栈对比

两者底层路线完全不同：

| 维度 | CoPaw | OpenClaw |
|------|-------|----------|
| **语言** | Python（≥ 3.10, ≤ 3.13） | Node.js（≥ 22.12.0） |
| **智能体框架** | AgentScope + AgentScope Runtime | Pi 系列库（@mariozechner/pi-*） |
| **记忆引擎** | ReMe（向量 + BM25 混合检索） | SQLite + 本地文件 |
| **向量数据库** | Chroma（默认后端） | 内嵌向量检索 |
| **模型支持** | ModelScope / DashScope / 自定义 | Anthropic / OpenAI / Ollama 等 |
| **配置热加载** | ✅ 每 2 秒自动检测 config.json 变更 | 需手动重启 |

CoPaw 基于阿里的 [AgentScope](https://github.com/agentscope-ai/agentscope) 框架构建，同时引入 [ReMe](https://github.com/agentscope-ai/ReMe) 做记忆管理。值得注意的是，CoPaw 虽然支持云端部署，但**数据默认全在本地**（`~/.copaw` 目录），不依赖第三方托管。

![CoPaw 系统架构图](images/CoPaw%20系统架构图-lovartai.png)
*CoPaw 完整系统架构：从用户渠道到 AgentScope 核心引擎到数据存储层*

---

## 二、记忆系统：混合检索 vs 纯本地存储

这是两者技术差异最大的地方。

### CoPaw 的记忆架构

CoPaw 的记忆系统分两层：

- **上下文管理**：对话超过 token 阈值时，自动压缩为摘要写入日志
- **长期记忆**：通过文件工具将关键信息写入 Markdown，配合语义检索召回

文件结构很直观：

```
~/.copaw/
├── MEMORY.md              # 长期记忆（决策、偏好、持久事实）
└── memory/
    ├── 2026-02-14.md      # 每日日志（自动追加）
    └── 2026-02-15.md
```

**技术亮点在检索**。CoPaw 采用 **向量 + BM25 混合检索**，两路信号加权融合：

| 检索方式 | 权重 | 擅长 | 弱点 |
|---------|------|------|------|
| 向量语义搜索 | 0.7 | 意义相近但措辞不同的内容 | 精确 token 匹配 |
| BM25 全文检索 | 0.3 | 函数名、错误码等精确命中 | 同义词改写 |

融合逻辑：两路各自扩大 3 倍候选池 → 独立打分 → 按 `path + start_line + end_line` 去重 → 加权求和 → 取 top-N。

举个例子，查询 `"handleWebSocketReconnect 断线重连"`：

| 记忆片段 | 向量分 | BM25 分 | 融合分 |
|---------|--------|---------|-------|
| "handleWebSocketReconnect 函数负责断线重连" | 0.85 | 1.0 | **0.895** |
| "网络断开后自动重试连接" | 0.78 | 0.0 | **0.546** |

> 单独用任何一种检索都有盲区。混合检索让"自然语言提问"和"精确查找"都能命中。

### OpenClaw 的记忆方案

OpenClaw 走的是更轻量的路线：SQLite 存储 + 本地文件（AGENTS.md、SOUL.md 等），支持向量检索但实现更简洁。两者思路相似——CoPaw 官方也承认记忆设计受 OpenClaw 启发——但 CoPaw 在检索精度上做了更多工程化打磨。

---

## 三、人设系统：6 个 Markdown 文件定义一个 AI

CoPaw 用 6 个 Markdown 文件构建 Agent 的完整人格，这套设计同样受 OpenClaw 启发：

| 文件 | 职责 | 读写 |
|------|------|------|
| **SOUL.md** | 价值观与行为准则（"真心帮忙不敷衍、有自己的观点不盲从"） | 只读 |
| **PROFILE.md** | Agent 身份 + 用户画像 | 读写 |
| **BOOTSTRAP.md** | 首次运行引导（自我介绍 → 了解用户 → 写 PROFILE → 自我删除） | 一次性 |
| **AGENTS.md** | 完整工作规范（记忆读写、安全权限、工具调用） | 只读 |
| **MEMORY.md** | 工具设置与经验教训 | 读写 |
| **HEARTBEAT.md** | 后台巡检任务清单 | 读写 |

文件协作关系：

```
BOOTSTRAP.md (🐣 一次性)
    ├── 生成 → PROFILE.md
    ├── 引导阅读 → SOUL.md
    └── 完成后自我删除 ✂️

AGENTS.md (📋 日常规范)
    ├── 读写 → MEMORY.md
    ├── 参考 → HEARTBEAT.md
    └── 参考 → PROFILE.md
```

这意味着 CoPaw 有一个**自举过程**：首次启动时通过 BOOTSTRAP.md 引导 Agent "出生"，了解用户后生成 PROFILE，然后 BOOTSTRAP 自我删除。之后 Agent 的行为完全由剩下的 5 个文件驱动。

---

## 四、技能系统：开源生态的交叉授粉

CoPaw 的内置技能来源很有意思——并非全部自研：

| 技能 | 能力 | 来源 |
|------|------|------|
| cron | 定时任务管理 | CoPaw 自建 |
| file_reader | 文本文件读取与摘要 | CoPaw 自建 |
| news | 新闻查询与摘要 | CoPaw 自建 |
| browser_visible | 可见模式浏览器（调试/验证码） | CoPaw 自建 |
| **himalaya** | **CLI 邮件管理（IMAP/SMTP）** | **来自 OpenClaw** |
| **pdf / docx / pptx / xlsx** | **Office 文档全家桶** | **来自 Anthropic** |

这是一个典型的**开源生态交叉授粉**：CoPaw 从 OpenClaw 借了邮件管理，从 Anthropic 借了文档处理，自己补了定时任务和浏览器能力。

自定义技能的方式也很简洁：在 `~/.copaw/customized_skills/` 下建目录，放一个 `SKILL.md` 即可，应用启动时自动加载。也可以在控制台 UI 里直接创建，不用碰文件系统。

![CoPaw 控制台 - 技能管理](https://img.alicdn.com/imgextra/i2/O1CN01ovyeE126g4rr18aGy_!!6000000007690-2-tps-4066-2118.png)
*CoPaw 控制台技能管理界面*

---

## 五、渠道与多模态：不只是"能连"

渠道支持不能只看数量，还得看**多模态能力**。CoPaw 官方文档给出了完整的支持矩阵：

| 频道 | 收文本 | 收图片 | 收视频 | 收音频 | 收文件 | 发文本 | 发图片 | 发视频 | 发音频 | 发文件 |
|------|--------|--------|--------|--------|--------|--------|--------|--------|--------|--------|
| **钉钉** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **飞书** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Discord** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🚧 | 🚧 | 🚧 | 🚧 |
| **QQ** | ✅ | 🚧 | 🚧 | 🚧 | 🚧 | ✅ | 🚧 | 🚧 | 🚧 | 🚧 |
| **iMessage** | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |

（✅ = 已支持，🚧 = 施工中，❌ = 平台限制无法支持）

**钉钉和飞书是一等公民**——全模态收发都支持。飞书走 WebSocket 长连接收消息、Open API 发送，群聊时还会在 metadata 中带 `chat_id` 和 `message_id` 做去重。Discord 和 QQ 的多模态发送还在施工中，当前以链接形式附在文本里。iMessage 受平台限制，只支持纯文本。

OpenClaw 在渠道**数量**上更多（WhatsApp、Telegram、Slack、Signal 等 12+ 渠道），但多模态深度不如 CoPaw 在钉钉/飞书上的表现。

---

## 六、心跳与定时任务

CoPaw 有一个区分于 OpenClaw 的设计：把**心跳**和**定时任务**明确拆成两个机制。

**心跳**是全局唯一的后台巡检——你在 `HEARTBEAT.md` 里写一套检查清单，系统按间隔（如 30 分钟）自动执行，结果可以发到你上次对话的频道：

```markdown
# Heartbeat checklist
- 扫描收件箱紧急邮件
- 查看未来 2h 的日历
- 检查待办是否卡住
- 若安静超过 8h，轻量 check-in
```

**定时任务**（Cron）则是多条独立任务，每条单独配时间、内容和投递频道：

```bash
# 每天 9 点发早安到钉钉
copaw cron create --type text --name "每日早安" \
  --cron "0 9 * * *" --channel dingtalk --text "早上好！"

# 每 2 小时让 AI 检查待办并转发
copaw cron create --type agent --name "检查待办" \
  --cron "0 */2 * * *" --channel dingtalk --text "我有什么待办？"
```

两者的区别一目了然：

| | 心跳 | 定时任务 |
|---|------|---------|
| **数量** | 只有一份 | 可以建很多个 |
| **间隔** | 一个全局间隔 | 每个独立设定 |
| **投递** | 发到"上次频道"或不发 | 每个独立指定频道和用户 |
| **适用** | 固定一套自检/摘要 | 多条不同时间、不同内容 |

![CoPaw 控制台 - 定时任务](https://img.alicdn.com/imgextra/i2/O1CN01JTEIm61U1MFz3kDn2_!!6000000002457-2-tps-4066-2118.png)
*CoPaw 控制台定时任务管理*

---

## 七、部署体验

### 本地部署

两边都做到了三条命令上手：

```bash
# CoPaw
pip install copaw
copaw init --defaults    # 生成 ~/.copaw/config.json + HEARTBEAT.md
copaw app                # 默认 http://127.0.0.1:8088

# OpenClaw
npm install -g openclaw
openclaw onboard         # 交互式引导
openclaw gateway
```

CoPaw 的 `copaw init` 如果不加 `--defaults`，会走一个完整的交互式引导：心跳配置 → 语言选择 → 频道配置 → LLM 提供商 → 技能选择 → 环境变量。

### 云端部署

CoPaw 支持 [魔搭创空间](https://modelscope.cn/studios/fork?target=AgentScope/CoPaw) 一键部署——不用装 Python，浏览器打开就能用。**注意要把空间设为非公开**，否则你的 AI 助理可能被他人操纵。

OpenClaw 目前没有官方的一键云端方案，需要自行部署到服务器。

### 控制台

CoPaw 内置了一个 Web 管理界面，功能覆盖聊天、频道管理、会话管理、定时任务、工作区（编辑人设文件）、技能开关、模型配置、环境变量——基本上所有配置都能在浏览器里完成。

![CoPaw 控制台 - 聊天界面](https://img.alicdn.com/imgextra/i1/O1CN01kFaEFI1CrQCDRI0Oo_!!6000000000134-2-tps-4066-2118.png)
*CoPaw 控制台聊天界面*

---

## 总结

把两者放在一起看，更准确的定位是：

- **OpenClaw** = 本地优先、轻量、完全开源、海外渠道多、可编程定制，适合开发者和隐私敏感用户
- **CoPaw** = 站在 OpenClaw 肩膀上的云原生迭代，极简安装、国内办公友好、混合检索记忆更精、控制台体验更完整，适合不想折腾的人和企业场景

技术上没有绝对优劣。CoPaw 在记忆检索、多模态深度、部署便捷性上更进一步；OpenClaw 在开放性、渠道广度、社区生态上占优。选型时结合你的部署环境、渠道需求和技术栈来定。

---

**相关链接**

- **CoPaw**：[官方文档](http://copaw.agentscope.io/) · [魔搭创空间](https://modelscope.cn/studios/fork?target=AgentScope/CoPaw) · [AgentScope](https://github.com/agentscope-ai/agentscope) · [ReMe](https://github.com/agentscope-ai/ReMe)
- **OpenClaw**：[官网](https://openclaw.ai/) · [GitHub](https://github.com/openclaw/openclaw) · [文档](https://docs.openclaw.ai/)

*本文基于 2026 年 2 月 CoPaw 官方文档（v1）和 OpenClaw 公开资料整理，技术细节以各自官方文档为准。*
