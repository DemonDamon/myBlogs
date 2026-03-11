# 用 ZeroClaw 结合 SNS 打造每日新闻邮件推送助手 - zhaojie10 - 博客园

原文链接: https://www.cnblogs.com/peacemaple/p/19620712

[![返回主页](/skins/custom/images/logo.gif)](zeroclaw-blog/images/a8f0edf3afb8df92d9a17312c18d1ef5.jpg)

# [zhaojiew10学习记录](https://www.cnblogs.com/peacemaple)

##

* [博客园](https://www.cnblogs.com/)
* [首页](https://www.cnblogs.com/peacemaple/)
* [新随笔](https://i.cnblogs.com/EditPosts.aspx?opt=1)
* [联系](https://msg.cnblogs.com/send/zhaojie10)
* [订阅](javascript:void(0))
* [管理](https://i.cnblogs.com/)

# [用 ZeroClaw 结合 SNS 打造每日新闻邮件推送助手](https://www.cnblogs.com/peacemaple/p/19620712 "发布于 2026-02-17 01:03")

参考资料

* <https://github.com/zeroclaw-labs/zeroclaw>
* <https://github.com/vikiboss/60s?tab=readme-ov-file>
* <https://skills.sh/vikiboss/60s-skills/daily-news-60s>
* <https://skills.sh/vikiboss/60s-skills/hot-topics>

ZeroClaw 是 OpenClaw 的 Rust 重写版本，定位是轻量级 AI Agent 基础设施。吸引我的几个点：二进制只有 3.4MB，冷启动不到 10ms，支持 22+ AI 提供商，内置 Telegram/Discord/Slack 等消息通道。跟 OpenClaw 相比，ZeroClaw 用 Rust 的 trait 系统做了插件化架构，Provider、Channel、Memory、Tool 都是可替换的 trait 实现。内存安全由编译器保证，没有运行时开销。对于想**在服务器上长期跑一个 AI 助手**的场景来说，这些特性很实用。

这里的数据源用的是 vikiboss 做的 60s API，每天提供 15 条精选新闻加一句每日微语，每 30 分钟更新一次。除了每日新闻，还覆盖了微博、知乎、百度、抖音、B站等主流平台的热搜榜单。接口免费、无需认证、全球 CDN 加速，响应速度很快。60s API 同时在 skills.sh 上发布了两个 Agent Skill：daily-news-60s 和 hot-topics。

## 安装ZeroClaw

安装Rust 环境后，克隆仓库后直接 cargo build：

```

git clone https://github.com/zeroclaw-labs/zeroclaw.git
cd zeroclaw
cargo build --release
cargo install --path .

```

编译时遇到了一个小 bug：`src/main.rs` 里 `ModelCommands` 枚举被定义了两次，导致编译报 `E0428` 重复定义错误，需要删掉重复的那份。

ZeroClaw 提供了 onboard 命令做初始化，支持交互式和快速模式：

```

zeroclaw onboard --provider openai --api-key "YOUR_KEY" --memory sqlite

```

这会在 `~/.zeroclaw/` 下生成完整的工作空间结构，包括配置文件、sessions、memory、skills 目录，以及一系列 Agent 人格文件（IDENTITY.md、SOUL.md 等）。

![image]()

由于我用的是本地 LiteLLM 代理转发到 qwen3-coder 模型，endpoint 在 `localhost:4000`。onboard 时选了 openai provider，配置里也加了 `base_url`，结果 agent 启动后卡住不动。

排查发现，ZeroClaw 的 OpenAI Provider 实现里，API 地址是硬编码的，请求直接发到了 OpenAI 官方地址导致超时

```

let response = self.client
    .post("https://api.openai.com/v1/chat/completions")
    .header("Authorization", format!("Bearer {api_key}"))
    .json(&request)
    .send()
    .await?;

```

需要使用 `custom:` 前缀的 provider，它走的是 OpenAI Compatible 通道支持自定义 URL：

```

[ec2-user@ip-172-31-14-46 workspace]$ cat ~/.zeroclaw/config.toml
api_key = "sk-D6TQa6a-echLxddGr52kXQ"
default_provider = "custom:http://localhost:4000/v1"
default_model = "qwen3-coder"
default_temperature = 0.7

```

ZeroClaw 的 provider 工厂方法会识别 `custom:` 前缀，解析后面的 URL，创建一个通用的 OpenAI 兼容 Provider 实例。

## 配置 Skills

Skills 是 Vercel 推出的 Agent 技能生态，本质上是一份 SKILL.md 文件，用 YAML frontmatter 描述元数据，用 Markdown 写使用说明。Agent 启动时扫描 skills 目录，把这些知识加载到上下文中，就"学会"了如何调用对应的 API。

Skills CLI 是 Vercel 做的包管理器，用 `npx skills add` 安装。但它安装到 `~/.skills/` 目录，ZeroClaw 扫描的是 `~/.zeroclaw/workspace/skills/`，所以需要手动复制过去。ZeroClaw 的 skills 加载优先级是：项目 workspace/skills > 用户 ~/.zeroclaw/workspace/skills > 内置 skills。跟 OpenClaw 的机制一致。

```

npx skills add vikiboss/60s-skills@daily-news-60s -g -y
npx skills add vikiboss/60s-skills@hot-topics -g -y

cp -r ~/.skills/daily-news-60s ~/.zeroclaw/workspace/skills/
cp -r ~/.skills/hot-topics ~/.zeroclaw/workspace/skills/

```

ZeroClaw 默认的安全策略比较严格，这是好事，但也意味着 Agent 刚装好的时候几乎什么都做不了。我调了这几个地方：

* `allowed_commands` 里加入 `curl`、`mkdir`、`aws`，让 Agent 能执行 shell 命令调 API 和操作文件。
* `http_request` 工具默认是关闭的，需要手动开启并配置允许的域名。注意 `max_response_size` 和 `timeout_secs` 不能留 0，否则会用默认值或者行为异常。

```

[http_request]
enabled = true
allowed_domains = ["60s.viki.moe"]
max_response_size = 1000000
timeout_secs = 30

```

* `workspace_only = false`。默认开启时 Agent 只能访问 workspace 目录内的文件，读不了 skills 目录也写不了外部路径。
* 源码里 `MAX_TOOL_ITERATIONS` 默认是 10。Agent 在复杂任务中经常需要多轮工具调用（读 skill、调 API、写文件、发 SNS），修改到了 20并重新编译。

## 接入SNS 邮件推送测试运行效果

比起把新闻存成文件等着自己去看，推送到邮箱更实用。在AWS SNS 创建一个 Topic，订阅邮箱地址，然后用一条 CLI 命令就能发。在 ZeroClaw 的 `allowed_commands` 里加上 `aws` 就行。

让 Agent 在获取新闻后自己调这个命令发邮件。Agent 读了 skill 里的 API 文档，知道怎么调 60s 接口；在 prompt 里告诉它 SNS 的 ARN 和 region，它就能把整个流程串起来。最终的一条命令如下

```

zeroclaw agent -m "请调用 60s API 获取今日新闻和微博热搜，\
整理成中文摘要，通过 aws sns publish 发送到 SNS topic，\
同时保存到 news/ 目录"

```

Agent 的执行过程如下

1. 调用 `https://60s.viki.moe/v2/60s` 获取每日新闻（http\_request 工具）
2. 调用 `https://60s.viki.moe/v2/weibo` 获取微博热搜（http\_request 工具）
3. 整理成结构化的 Markdown 摘要（LLM 推理）
4. 写入 `news/2026-02-16.md`（file\_write 工具）
5. 执行 `aws sns publish` 发送邮件（shell 工具）

全程大约 30 秒完成，邮箱里收到了格式清晰的新闻早报。

![image]()

如果要做成每天自动执行，ZeroClaw 内置了 cron 系统：

```

zeroclaw cron add \
  --name "每日新闻早报" \
  --cron "0 7 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "获取今日新闻和热搜，整理后通过 SNS 发送邮件" \
  --deliver

```

cron 任务持久化在 `~/.zeroclaw/cron/` 下，重启不丢失。isolated session 意味着每次执行都是独立上下文，不会被之前的对话历史干扰。

![image]()

cron 任务注册好了，但是到点却没执行。后来发现是 `zeroclaw cron add` 只是把任务写入了配置文件，真正负责调度执行的是 daemon 进程。ZeroClaw 的 daemon 是一个长驻后台服务，包含四个组件：

* Gateway：HTTP/WebSocket 服务，监听在 `127.0.0.1:8080`，提供 webhook 接口供外部系统（Telegram、Discord 等）推送消息，也支持 WebSocket 实时通信
* Channels：消息通道管理，负责连接各个聊天平台
* Heartbeat：心跳检查，定期执行后台感知任务
* Scheduler：定时任务调度器，按 cron 表达式触发注册的任务

没有 daemon 在跑，scheduler 就不工作，cron 任务自然不会触发。启动方式：

```

zeroclaw daemon

```

Gateway 启动时会生成一个一次性配对码，用于客户端认证。如果只是跑 cron 任务，不需要关心配对流程，让它默认监听 127.0.0.1 就行。

daemon 需要持续运行，手动在终端跑不现实。可以用如下命令注册为服务，开机自启、崩溃自动重启：

```

zeroclaw service start

zeroclaw service status

Service state: active
Unit: /home/ec2-user/.config/systemd/user/zeroclaw.service

$ cat /home/ec2-user/.config/systemd/user/zeroclaw.service
[Unit]
Description=ZeroClaw daemon
After=network.target

[Service]
Type=simple
ExecStart=/home/ec2-user/.cargo/bin/zeroclaw daemon
Restart=always
RestartSec=3

[Install]
WantedBy=default.target

```

之后用 `systemctl --user status zeroclaw.service` 查看运行状态，`journalctl --user -u zeroclaw.service` 看执行日志。

posted @
2026-02-17 01:03
[zhaojie10](https://www.cnblogs.com/peacemaple)
阅读(151)
评论(0)

[收藏](javascript:void(0))
[举报](javascript:void(0))

[刷新页面](#)[返回顶部](#top)

[![](https://img2024.cnblogs.com/blog/35695/202512/35695-20251205182619157-1150461542.webp)](https://ais.cn/u/3Qf22e)

### 公告

[博客园](https://www.cnblogs.com/)
  ©  2004-2026

[![](zeroclaw-blog/images/9cc3128655f9ed3b7637356f49069fc5.png)浙公网安备 33010602011771号](zeroclaw-blog/images/4082a8cb1e24bb41648ee3e764134e54.jpg)
[浙ICP备2021040463号-3](https://beian.miit.gov.cn)