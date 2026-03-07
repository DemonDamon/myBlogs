# Claude Agent Skills 深度解析：从"会用AI"到"可复制工程能力"

> 一文读懂 Skills 架构原理、创建方法与团队落地实践

## 一、背景：通用 Agent 的经验瓶颈

想象一个场景：你有一项复杂的报税工作，你愿意把它交给一个数学满分的天才，还是交给一个做了上千次报税的老会计？

大多数人会选老会计。原因很简单：**会计的核心优势不是智商，而是经验**——流程熟悉、边界清晰、验收口径明确、常见坑早就踩过了。

今天的大语言模型也面临同样的问题。Claude 很聪明，但每次对话都是从零开始。你在上次对话里花了两小时"调教"出来的代码审查流程，下次打开新对话时消失得一干二净。同类任务反复做，输出漂移，质量靠人盯，SOP 散落在一条条历史对话里——这是团队使用 AI 时共同的痛点。

Anthropic 在 2025 年 10 月推出了 **Agent Skills**，试图系统性地解决这个问题。它的核心思路很直接：**把"怎么做"从对话里拿出来，沉淀为可版本化、可复用、可审计的文件资产**。

Skills 不是让模型更聪明，而是让它在特定领域**更像一个训练有素的老手**。

## 二、Skills 是什么：一句话说清楚

一个 Skill 的最小定义极其简洁：

> **一个目录 + 一个 `SKILL.md` 文件 = 一个可复用的 AI 能力模块**

就这样。没有复杂配置，没有特殊运行时，没有需要上传到云端的模型权重。一个名为 `code-review` 的文件夹，里面放一个 `SKILL.md`，就构成了一个可以自动触发的 Skills。

你可以把它理解成**给新员工写的"培训手册 + 工具箱"**：手册告诉他什么情况下做什么，工具箱提供他做事要用的脚本和模板。只要这套材料写清楚了，换谁来执行都能得到一致的结果。

**与传统 Prompt 工程的关键区别**在于持久化：

- **Prompt**：每次对话都要重写，一次性消耗，无法积累
- **Skills**：写一次，永久复用；可以版本控制，可以团队共享，可以跨平台移植

2025 年 12 月，Anthropic 将 Skills 规范发布为开放标准 [agentskills.io](https://agentskills.io)，标志着 Skills 从 Claude 私有能力演变为整个 AI 生态的公共基础设施。Cursor、GitHub Copilot 等工具也在跟进采纳这一标准。

## 三、核心原理：渐进式披露（三层加载架构）

Skills 的设计灵魂是 **渐进式披露（Progressive Disclosure）** 机制，按需加载，而不是一次性把所有内容塞进 Context。

这解决了一个工程难题：**如何让 Agent 同时"知道很多"，但又不把 Context 塞满？**

答案是分三层：

![Claude Agent Skills 渐进式披露架构](images/claude_skills_architecture.png)

### Level 1：元数据层（发现）
**何时加载**：Agent 启动时，始终在 System Prompt 里  
**Token 成本**：每个 Skill 约 100 tokens  
**内容**：YAML frontmatter 里的 `name` 和 `description` 字段

这一层相当于**能力目录**——让 Agent 知道"我有哪些技能，每个技能适用于什么场景"，但不加载具体内容。你安装 20 个 Skills，System Prompt 也只多了约 2000 tokens，完全可控。

### Level 2：指令层（激活）
**何时加载**：用户请求与某个 Skill 的 description 匹配时  
**Token 成本**：建议控制在 5000 tokens 以内  
**内容**：`SKILL.md` 的 Markdown 正文——流程、边界、验收标准

这一层才是真正的"操作手册"。只有当 Agent 判断当前任务需要某个 Skill 时，才会去读取它的完整内容。

### Level 3+：资源层（执行）
**何时加载**：执行过程中按需访问  
**Token 成本**：实际上无上限，因为不进入 Context Window  
**内容**：`scripts/`（可执行脚本）、`references/`（参考文档）、`assets/`（静态资源）

这一层是最精妙的设计：**脚本代码在执行时不进入 Context**，Agent 通过 bash 命令运行脚本，只把执行结果（stdout）带回上下文。一个 300 行的 Python 脚本，对 Context 的"消耗"等于它输出的几行结果。

**横向对比**：传统方案把所有 SOP 常驻在 Prompt 里，轻松消耗 3000+ tokens；Skills 方案在未激活状态下每个 Skill 仅 100 tokens，即便激活也控制在 5000 tokens 以内。这是数量级的差异。

## 四、解剖一个 Skill：结构与 SKILL.md 格式

### 目录结构

一个完整 Skill 的推荐目录结构如下：

```
my-skill/                    # Skill 目录（名称即技能标识）
├── SKILL.md                 # 必需：核心指令 + 元数据
├── references/              # 可选：参考资料（按需加载）
│   ├── checklist.md         
│   └── templates.md         
├── scripts/                 # 可选：可执行脚本（执行不入 Context）
│   └── process.py           
└── assets/                  # 可选：静态资源
    └── schema.json          
```

![SKILL.md 文件结构与目录组织](images/skill_md_structure.png)

### SKILL.md 格式详解

每个 `SKILL.md` 由两部分组成：YAML frontmatter（元数据）+ Markdown 正文（指令）。

```yaml
---
name: code-review
description: |
  执行代码审查，检查安全漏洞、性能问题与可维护性。
  用于 PR 审查、merge request 评估、代码质量检测。
  触发词：代码审查、review、PR、代码质量、安全漏洞
license: Apache-2.0
metadata:
  author: my-team
  version: "1.0"
allowed-tools: Read Grep Glob
# Code Review Skill

## 审查流程
1. 读取代码变更
2. 检查安全漏洞（注入、XSS、认证）
3. 分析性能问题
4. 评估可维护性与测试覆盖
5. 输出结构化报告

## 输出格式
- **严重**：必须修复才能合并
- **警告**：建议修复，但不阻塞
- **建议**：可选优化项

详细规范见 [审查清单](references/checklist.md)
```

### 必填字段

**`name`** — Skill 的唯一标识符
- 小写字母、数字和连字符，最多 64 字符
- 不能以连字符开头/结尾，不能有连续连字符（`--`）
- 必须与父目录名称匹配
- 正确示例：`pdf-processing`、`code-review`、`daily-standup`

**`description`** — **Skills 能否被正确触发的核心**
- 最多 1024 字符（agentskills.io 标准），Claude.ai 内为 200 字符
- 同时说明**做什么**和**何时用**
- 应包含用户真实会说的关键词
- 好示例：`提取和分析 PDF 文件的文本与表格数据。当用户提到 PDF、表单填写或文档提取时使用。`
- 差示例：`帮助处理 PDF。`

> **核心洞见**：`description` 不是功能简介，更像一条路由规则。它决定了 Claude 是否会在合适的时机加载你的 Skill。很多 Skills 失效的根本原因就是 description 写得太模糊。

### 可选字段

| 字段 | 用途 | 适用场景 |
|------|------|---------|
| `license` | 许可证声明 | 开源 Skill 时填写 |
| `metadata` | 作者、版本等附加信息 | 团队管理 Skills 时 |
| `allowed-tools` | 收敛执行面，指定允许的工具 | 安全敏感场景 |
| `compatibility` | 运行环境要求 | 需要特定依赖时 |
| `dependencies` | 软件包依赖 | Scripts 有第三方依赖时 |

## 五、跨平台支持：在哪里用、怎么用

Anthropic 将 Agent Skills 设计为开放标准，而不是只能在 Claude 里用的私有能力。一套 Skills，可以在多个 AI 工具里通用——这与 USB-C 成为充电标准的逻辑如出一辙。

### Claude Code
```bash
# 项目级 Skill（团队共享，可 Git 版本控制）
.claude/skills/code-review/SKILL.md

# 个人级 Skill（跨项目复用）
~/.claude/skills/code-review/SKILL.md
```
自动发现，无需注册；支持 `/skill-name` 手动触发。

### Claude.ai
在 **Settings > Features > Skills** 上传 ZIP 包，要求：
```
my-skill.zip
└── my-skill/
    ├── SKILL.md
    └── resources/
```
注意：ZIP 根目录必须是 Skill 文件夹，不能直接放文件。

### Claude API
通过 `/v1/skills` 接口上传，workspace 内所有成员共享。需要三个 beta headers：
- `files-api-2025-04-14`
- `skills-2025-10-02`  
- `code-execution-2025-08-25`

### Agent SDK
在配置中添加 `"Skill"` 到 `allowed_tools`，Skills 放置在 `.claude/skills/` 目录。

### 跨平台标准（agentskills.io）
基于 [agentskills.io](https://agentskills.io) 开放规范创建的 Skills 同样可以在 Cursor、GitHub Copilot 等支持标准的工具里运行。

**预置 Skills（官方提供，开箱即用）**：
- **PDF**：生成格式化 PDF 报告
- **Word（docx）**：创建/编辑 Word 文档
- **Excel（xlsx）**：电子表格数据分析
- **PowerPoint（pptx）**：创建和编辑演示文稿

## 六、创建你的第一个 Skill：完整步骤

### 第一步：选题原则

**两个核心信号**：
1. **可验收**：输出能被机器或人检查，不靠"感觉对"
2. **高频**：每周都在做，或每个项目都要做

**适合做成 Skill 的任务**：代码审查、故障排障、日报/周报生成、API 文档生成、数据分析报告、品牌规范应用

**不适合做成 Skill 的任务**：一次性任务、实验性探索、需要实时外部数据的任务（用 MCP 替代）

### 第二步：创建目录结构
```bash
mkdir -p ~/.claude/skills/daily-standup
cd ~/.claude/skills/daily-standup
```

### 第三步：写 SKILL.md

从最小可用版本开始，绝对不要一开始就写大而全：

```yaml
---
name: daily-standup
description: |
  从 Git 提交记录生成每日站会总结。
  用于生成工作日报、站会汇报、进度同步。
  触发词：站会、日报、昨天做了什么、今天计划、工作总结
# Daily Standup Generator

## 输出格式
1. **昨日完成**：最近24小时的 Git 提交总结
2. **今日计划**：当前 TODO 或进行中的分支
3. **阻塞项**：标注需要协作解决的问题

## 流程
1. 执行 `git log --since="24 hours ago" --oneline` 获取提交
2. 总结提交为人类可读的完成项
3. 检查当前分支和未提交改动
4. 输出站会格式报告

## 验收
- 每个完成项不超过一句话
- 必须包含三个部分（昨日/今日/阻塞）
- 不含技术细节，面向非技术受众
```

### 第四步：添加脚本（可选但推荐）

把确定性操作脚本化，让 Claude 从"操作者"变为"编排者"：

```python
# scripts/get_git_summary.py
#!/usr/bin/env python3
"""获取 Git 日志并结构化输出"""
import subprocess
import sys
from datetime import datetime, timedelta

def get_recent_commits(hours=24):
    since = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")
    result = subprocess.run(
        ["git", "log", f"--since={since}", "--oneline", "--no-merges"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()

if __name__ == "__main__":
    commits = get_recent_commits()
    if commits:
        print("## 近24小时提交\n")
        for line in commits.split('\n'):
            print(f"- {line}")
    else:
        print("近24小时无提交记录")
```

然后在 `SKILL.md` 里引用它：
```markdown
## 数据获取
运行 `scripts/get_git_summary.py` 获取结构化提交数据，
然后基于输出生成站会报告。
```

### 第五步：测试

**手动触发**（Claude Code）：
```
/daily-standup
```

**自然语言触发**：
```
帮我生成今天的站会内容
```

**调试**：检查 Claude 的 thinking 确认 Skill 是否被加载；如未触发，迭代优化 `description` 中的关键词。

## 七、工程实践：生产级 Skill 的关键设计

能跑通一个 Skill 和把 Skill 用到生产环境，之间还差几件重要的事。

### 1. 验收标准先行

最高杠杆的实践：在 `SKILL.md` 里写清**可执行的验收方式**，而不只是"输出应该包含..."。

**差的写法**：
```markdown
## 输出要求
生成一份代码审查报告，涵盖安全性、性能、可维护性
```

**好的写法**：
```markdown
## 验收标准
- [ ] 报告包含三级分类（严重/警告/建议）
- [ ] 每项问题附带具体的代码位置（文件名+行号）
- [ ] 严重问题必须有修复建议
- [ ] 最后一行明确标注 APPROVED / REJECTED / CONDITIONAL
```

让 Claude "自证正确"，而不是让人肉去验收。

### 2. 脚本化确定性部分

Anthropic 工程团队分享过一个真实观察：他们反复看到 Claude 在对话中写同一段 Python 脚本，用来把演示文稿套上 Anthropic 的模板。**与其每次都让模型"现场重写"，不如把脚本保存下来，让 Agent 直接调用**。

LLM 擅长处理"不确定"：拆解、取舍、叙事、判断。对于确定性操作，应该交给脚本：

**适合脚本化的任务**：
- 批量文件处理、格式转换
- 数据提取和统计
- 输出结构校验（JSON Schema、Markdown 格式）
- 模板套用（报告骨架、幻灯片模板）
- 跑测试、构建命令

**脚本化带来的工程收益**：
- 脚本本体不进 Context，只带回结果（一个 300 行脚本，对 Context 的消耗 = 它输出的几行结果）
- 失败模式可分类（权限不足 / 依赖缺失 / 格式错误），而不是模糊的"Claude 输出了不对的东西"
- 可单独测试，可 code review，可版本迭代

### 3. 收敛执行面

`allowed-tools` 字段让你能明确限制 Skill 能使用哪些工具：

```yaml
# 只读审计类 Skill：严格限制写操作
allowed-tools: Read Grep Glob

# 代码审查：允许执行构建命令
allowed-tools: Read Grep Glob Bash(npm:*) Bash(git:*)

# 完全开放（谨慎使用）
allowed-tools: Bash Read Write
```

最小权限原则不只是安全规范，更能提高执行确定性——让 Claude 聚焦在允许的操作范围内，减少"漫游"风险。

### 4. 入口文件只放三件事

很多 Skills 失效是因为 `SKILL.md` 写成了文档站，关键约束被淹没了。

**SKILL.md 的正确用法**：
1. **验收**：怎样算完成（可验证的）
2. **边界**：缺什么先问，什么情况不做
3. **流程**：按顺序做什么

细节、案例、模板、清单——全部拆进 `references/`，在 `SKILL.md` 里用链接引用。

**Skill 结构的层次感**：
```
SKILL.md（入口）
├── 流程 + 验收 + 边界（核心，<500行）
├── references/checklist.md（详细审查清单，按需加载）
├── references/templates.md（输出模板，按需加载）
└── scripts/validate.py（格式校验，执行不入Context）
```

### 5. 团队落地与治理

当 Skills 数量增长到 10+ 时，治理是硬需求：

- **定期盘点**：合并重复 Skill，删除不再使用的，补齐验收标准
- **description 设计**：关键词不重叠，避免 Skills 相互抢夺触发
- **标注 owner**：每个 Skill 在 metadata 里记录负责人
- **可量化验收**：首轮命中率（第一次输出可交付的比例）、输出一致性（同类任务格式漂移程度）

## 八、Skills 与 MCP、Hooks、CLAUDE.md 的分工

初学者经常困惑：我什么时候该用 Skills？什么时候用 MCP？什么时候用 CLAUDE.md？答案是：这四个组件不是竞争关系，而是分工合作。Claude Code 的配置体系包含多个组件，各有各的位置：

| 组件 | 本质 | 解决什么 | 典型误用 |
|------|------|---------|---------|
| **Skills** | 方法论/流程封装 | 同类任务重复执行 | 把项目全局规范放进去 |
| **MCP** | 外部工具/数据连接 | 需要访问第三方服务 | 试图在 MCP 里写流程 |
| **Hooks** | 事件驱动自动化 | 必须保证执行的操作 | 用来替代 Skills |
| **CLAUDE.md** | 静态项目上下文 | 全局规范与项目背景 | 把 SOP 都塞进来 |
| **Prompt** | 单次任务指令 | 本次具体要做什么 | 每次重写相同的 SOP |

一句话总结：**Skills 负责"怎么做才稳定"，MCP 负责"连到外部世界"，Hooks 负责"不得不做的护栏"，CLAUDE.md 负责"项目记忆"**。

四个组件配合使用，比任何单一工具都更强大、更可靠。

## 九、常见陷阱与避坑指南

### 陷阱 1：Skill 变成"百科全书"
**症状**：Skill 覆盖范围太广，什么都能触发，但执行时步骤混乱  
**修复**：一个 Skill 只解决一类问题，宁可拆成三个精准的 Skill，也不要塞进一个大而全的 Skill

### 陷阱 2：description 太模糊
**症状**：用户明确要做代码审查，但 Claude 没有加载 Skill  
**修复**：描述里加入用户真实会说的关键词；用 `/skill-name` 手动触发测试；检查 thinking 确认触发链路

### 陷阱 3：没有验收标准
**症状**：每次执行结果格式不一样，靠人肉比对  
**修复**：用 Checklist 格式写验收条件；加入脚本做结构校验

### 陷阱 4：全靠模型推理，不脚本化
**症状**：相同任务执行结果不一致，调试困难  
**修复**：识别确定性部分（文件处理、格式转换、数据统计）并脚本化

### 陷阱 5：入口文件太长
**症状**：SKILL.md 超过 500 行，Claude 执行时"跳步"或遗漏关键约束  
**修复**：入口只保留流程骨架，细节迁入 references/

## 十、安全注意事项

Skills 可以执行代码，这让它非常强大，也意味着安全边界不可忽视。

**核心原则**：

1. **只安装可信源的 Skills**：来自 Anthropic 官方仓库（[github.com/anthropics/skills](https://github.com/anthropics/skills)）或自己团队编写的 Skills 是最安全的
2. **使用前审计 bundled 文件**：检查 scripts/ 里的脚本，注意不寻常的网络调用、文件读写范围
3. **不要硬编码敏感信息**：API 密钥、密码、令牌绝对不要出现在 SKILL.md 或 scripts/ 里
4. **防范 Prompt Injection**：如果 Skill 会处理外部来源的内容（网页、文件、邮件），流程上先"提取事实"，再"执行动作"
5. **最小权限**：用 `allowed-tools` 严格限制 Skill 的工具访问范围

## 十一、总结与展望

Claude Agent Skills 代表了一种新的 AI 使用范式转变：**从"用 AI 做事"到"把做事方式教给 AI"**。

核心价值链：

```
个人经验 → SKILL.md → 团队资产 → 生态公共品
```

**立即可以做的三件事**：

1. **选一个高频任务**（PR 审查、日报生成、故障排障……），写你的第一个 Skill
2. **参考官方示例**：[github.com/anthropics/skills](https://github.com/anthropics/skills) 里有涵盖文档处理、代码开发、企业流程的 86.1k star 开源库
3. **关注 agentskills.io 标准**：随着更多 AI 工具采纳这一开放标准，你今天写的 Skills 将在更多平台上运行

Anthropic 在工程博客里透露了未来方向：让 Agent **自主创建和评估 Skills**——在工作过程中发现好的模式，自动沉淀为可复用的 Skill。Skills 的生命周期管理（创建→测试→迭代→分享→废弃）正在进一步自动化。

当 Agent 能为自己积累经验、迭代工作方式时，"AI 加速复利"才真正开始。而这一切，从你今天写下第一个 `SKILL.md` 开始。

## 参考资料

1. **Anthropic 官方帮助文档** — How to create custom Skills  
   https://support.claude.com/en/articles/12512198-how-to-create-custom-skills

2. **Anthropic 工程博客** — Equipping agents for the real world with Agent Skills  
   https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

3. **官方 GitHub 仓库** — anthropics/skills（86.1k stars）  
   https://github.com/anthropics/skills

4. **Agent Skills 开放规范** — agentskills.io  
   https://agentskills.io/specification

5. **Claude 官方技术文档** — Agent Skills Overview  
   https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview

6. **Claude.ai 博客** — Introducing Agent Skills  
   https://claude.com/blog/skills

7. **第三方深度解析** — Claude Code Skills Guide  
   https://www.heyuan110.com/posts/ai/2026-02-28-claude-code-skills-guide/

8. **Claude CN 中文社区** — Skills 专业入门  
   https://claudecn.com/blog/claude-skills-professional-intro/
