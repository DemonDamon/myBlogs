# CoPaw — Works for you, grows with you.

原文链接: http://copaw.agentscope.io/docs/quickstart

# 快速开始

本节介绍两种方式运行 CoPAW：

* **方式一 — 本地安装**：在本地用三条命令启动（需 Python ≥ 3.10, ≤ 3.13）。
* **方式二 — 魔搭创空间**：一键配置，部署到创空间云端运行，无需安装 Python。

> 📖 阅读前请先了解 [项目介绍](/docs/intro)，完成安装与启动后可查看 [控制台](/docs/console)。

> 💡 **安装并启动后**：在配置频道之前，可先打开 [控制台](/docs/console)（浏览器访问 `http://127.0.0.1:8088/`）与 CoPAW 对话、配置 Agent；要在钉钉、飞书、QQ 等 app 里对话时，再前往 [频道配置](/docs/channels) 接入频道。

---

## 方式一：本地安装

**环境要求**：Python >= 3.10, <= 3.13。

### 步骤一：安装

```

pip install copaw

```

可选：先创建并激活虚拟环境再安装（`python -m venv .venv`，Linux/macOS 下
`source .venv/bin/activate`）。安装后会提供 `copaw` 命令。

### 步骤二：初始化

在工作目录（默认 `~/.copaw`）下生成 `config.json` 与 `HEARTBEAT.md`。两种方式：

* **快速用默认配置**（不交互，适合先跑起来再改配置）：

  ```

  copaw init --defaults
  ```

* **交互式初始化**（按提示填写心跳间隔、投递目标、活跃时段，并可顺带配置频道与 Skills）：

  ```

  copaw init
  ```

  详见 [CLI - 快速上手](/docs/cli#%E5%BF%AB%E9%80%9F%E4%B8%8A%E6%89%8B)。

若已有配置想覆盖，可使用 `copaw init --force`（会提示确认）。
初始化后若尚未启用频道，接入钉钉、飞书、QQ 等需在 [频道配置](/docs/channels) 中按文档填写。

### 步骤三：启动服务

```

copaw app

```

服务默认监听 `127.0.0.1:8088`。若已配置频道，CoPaw 会在对应 app 内回复；若尚未配置，也可先完成本节再前往频道配置。

---

## 方式二：魔搭创空间一键配置（无需安装）

若不想在本地安装 Python，可通过魔搭创空间将 CoPaw 部署到云端运行：

1. 先前往 [魔搭](https://modelscope.cn/register?back=%2Fhome) 注册并登录；
2. 打开 [CoPaw 创空间](https://modelscope.cn/studios/fork?target=AgentScope/CoPaw)，一键配置即可使用。

**重要**：使用创空间请将空间设为 **非公开**，否则你的 CoPaw 可能被他人操纵。

---

## 验证安装（可选）

服务启动后，可通过 HTTP 调用 Agent 接口以确认环境正常。接口为 **POST** `/agent/process`，请求体为 JSON，支持 SSE 流式响应。单轮请求示例：

```

curl -N -X POST "http://localhost:8088/agent/process" \
  -H "Content-Type: application/json" \
  -d '{"input":[{"role":"user","content":[{"type":"text","text":"你好"}]}],"session_id":"session123"}'

```

同一 `session_id` 可进行多轮对话。

---

## 接下来做什么？

* **想和 CoPAW 对话** → 去 [频道配置](/docs/channels) 接一个频道（推荐先接钉钉或飞书），按文档申请应用、填 config，保存后即可在对应 app 里发消息试。
* **想定时自动跑一套「自检/摘要」** → 看 [心跳](/docs/heartbeat)，编辑 HEARTBEAT.md 并在 config 里设间隔和 target。
* **想用更多命令** → [CLI](/docs/cli)（交互式 init、定时任务、清空工作目录）、[Skills](/docs/skills)。
* **想改工作目录或配置文件路径** → [配置与工作目录](/docs/config)。