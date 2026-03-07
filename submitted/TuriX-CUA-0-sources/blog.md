# TuriX-CUA：开源AI桌面智能体深度解析

## 目录

- [什么是 TuriX-CUA](#什么是-turix-cua)
- [核心概念：Computer-Using Agent (CUA)](#核心概念computer-using-agent-cua)
- [架构设计：多智能体分工协作](#架构设计多智能体分工协作)
- [核心特性深度解析](#核心特性深度解析)
- [性能表现](#性能表现)
- [实测体验：国产模型接入实战](#实测体验国产模型接入实战)
- [快速上手指南](#快速上手指南)
- [最佳实践与使用建议](#最佳实践与使用建议)
- [生态集成：MCP协议与OpenClaw](#生态集成mcp协议与openclaw)
- [发展路线图](#发展路线图)
- [总结与展望](#总结与展望)

## 什么是 TuriX-CUA

TuriX-CUA 是 TurixAI 团队开源的一个 **计算机使用智能体（Computer-use Agent）** 项目，它能让AI模型直接在你的桌面上进行真实的物理操作。通过自然语言指令，TuriX 就能帮你完成各种复杂的桌面任务，从预订机票酒店到编辑文档图表，真正实现"对话计算机，看它工作"。

> "Talk to your computer, watch it work."

![TuriX-CUA 基础演示](sources/manual_images/TuriX-CUA_image_4.gif)

项目的主要特点：

- ✅ **100% 开源**：个人和研究使用完全免费
- ✅ **state-of-the-art 性能**：在内部 OSWorld 风格测试集上通过率超过 **68%**
- ✅ **热插拔模型**：可以轻松更换不同的视觉语言模型（VLM）
- ✅ **跨平台支持**：原生支持 macOS 和 Windows
- ✅ **MCP 就绪**：支持通过 Model Context Protocol 与 Claude for Desktop 等外部Agent集成
- ✅ **Skills 机制**：支持可复用的 markdown 技能手册，提升复杂任务规划能力

## 核心概念：Computer-Using Agent (CUA)

### CUA 是什么？

**Computer-Using Agent (CUA)** 是一种新兴的AI范式，它让AI能够像人一样通过图形用户界面（GUI）与计算机交互。传统的自动化工具依赖特定应用的API或DOM选择器，而CUA通过视觉感知来理解屏幕内容，然后模拟鼠标和键盘操作来完成任务。

**CUA vs 传统自动化：**

| 特性 | 传统RPA自动化 | CUA智能体 |
|------|--------------|-----------|
| 依赖 | 需要特定API/选择器 | 只需要视觉可见，人类能点就能点 |
| 适应性 | 难以应对界面变化 | 通过视觉理解，鲁棒性强 |
| 通用性 | 通常绑定特定应用 | 任意桌面应用均可操作 |
| 智能程度 | 预设脚本，僵硬 | 能理解复杂指令，自适应调整 |

### 工作原理

CUA 的核心工作循环非常简单但有效：

1. **观察**：截取当前屏幕截图
2. **理解**：使用多模态大模型分析界面状态
3. **决策**：决定下一步该做什么（点击哪里、输入什么）
4. **执行**：控制系统完成实际操作
5. **重复**：直到任务完成

![TuriX-CUA 预订演示](sources/manual_images/TuriX-CUA_image_3.gif)

## 架构设计：多智能体分工协作

TuriX-CUA 采用了**多模型架构设计**，将原来单模型承担的所有任务分解给不同的专业模型，每个模型专注于自己擅长的部分，从而缓解了单个模型的压力，提升了整体性能。

### 整体架构

TuriX-CUA 的架构分为四个核心模块：

**四个核心模块：**

| 模块 | 职责 | 说明 |
|------|------|------|
| **Planner** | 任务规划 | 将高层自然语言目标分解为可执行的步骤 |
| **Brain** | 状态理解与决策 | 分析屏幕截图，理解当前界面，决策下一步操作 |
| **Actor** | 动作执行 | 精准计算点击坐标，输出具体操作参数 |
| **Memory** | 记忆管理 | 维护对话历史和任务上下文，支持可恢复压缩 |

### 架构优势

1. **职责分离**：不同模型专注不同任务，专业的人做专业的事
2. **灵活配置**：可以根据任务复杂度和成本选择不同规模的模型
3. **可扩展性**：新功能可以通过新增模块实现，不影响现有架构
4. **热插拔**：可以随时切换不同的后端模型提供商

![TuriX-CUA macOS 复杂任务演示](sources/manual_images/TuriX-CUA_image_5.gif)

### 执行流程

TuriX-CUA 的完整执行流程如下：

流程说明：

1. **用户输入**：用户用自然语言描述想要完成的任务
2. **任务分解**：Planner 将高层目标分解为多个步骤
3. **感知循环**：进入循环执行过程：
   - 截取当前屏幕截图
   - Memory 整合历史上下文
   - Brain 分析界面状态并决策
   - Actor 计算精准坐标
   - 系统执行操作（点击/输入/滚动等）
   - 等待界面更新
   - 判断任务是否完成，未完成则继续循环
4. **任务结束**：输出执行结果给用户

## 核心特性深度解析

### 1. 热插拔"大脑"机制

TuriX-CUA 设计了非常灵活的模型切换机制，你不需要修改代码，只需要在 `config.json` 中配置即可切换不同的模型提供商：

**支持的提供商：**
- TuriX API 官方服务
- OpenAI (ChatOpenAI)
- Google Gemini (ChatGoogleGenerativeAI)
- Anthropic Claude (ChatAnthropic)
- Ollama 本地部署
- 自定义扩展

**配置示例（Ollama 本地）：**

```json
{
  "brain_llm": {
    "provider": "ollama",
    "model_name": "llama3.2-vision",
    "base_url": "http://localhost:11434"
  },
  "actor_llm": {
    "provider": "ollama",
    "model_name": "llama3.2-vision",
    "base_url": "http://localhost:11434"
  },
  "memory_llm": {
    "provider": "ollama",
    "model_name": "llama3.2-vision",
    "base_url": "http://localhost:11434"
  },
  "planner_llm": {
    "provider": "ollama",
    "model_name": "llama3.2-vision",
    "base_url": "http://localhost:11434"
  }
}
```

**自定义模型扩展：**

如果你想使用项目中未预置的模型，只需要在 `main.py` 中添加几行代码：

```python
if provider == "name_you_want":
        return ChatOpenAI(
            model="gpt-4.1-mini", api_key=api_key, temperature=0.3
        )
```

根据你的需要，可以切换 ChatOpenAI、ChatGoogleGenerativeAI、ChatAnthropic 或 ChatOllama。

### 2. Skills：markdown 可复用技能手册

Skills 是 TuriX-CUA v0.3 引入的一个重要特性，它允许你将常用操作流程编写为 markdown 手册，Planner 会自动选择相关技能来指导执行。

**Skill 文件格式示例：**

```markdown
---
name: github-web-actions
description: Use when navigating GitHub in a browser (searching repos, starring, etc.).
---
# GitHub Web Actions
- Open GitHub, use the site search, and navigate to the repo page.
- If login is required, ask the user before proceeding.
- Confirm the Star button state before moving on.
```

**工作机制：**
- Planner 只看到技能的 `name` 和 `description`，用于相关性筛选
- Brain 实际执行时会获得完整的技能内容
- 技能可以不断积累，形成个人知识库

**启用 Skills：**

```json
{
  "agent": {
    "use_plan": true,
    "use_skills": true,
    "skills_dir": "skills",
    "skills_max_chars": 4000
  }
}
```

### 3. 可恢复记忆压缩

Recoverable Memory Compression 是 TuriX-CUA 的一个高级特性，它解决了长任务上下文窗口溢出的问题：

- 自动压缩历史记忆，节省上下文空间
- 支持任务中断后恢复执行
- 保持记忆的可访问性同时控制token消耗

### 4. 任务中断恢复

TuriX-CUA 支持从终止的任务中恢复：

```json
{
  "agent": {
    "resume": true,
    "agent_id": "my-task-001"
  }
}
```

使用说明：
- 使用与之前运行相同的 `agent_id`
- 保持相同的 `task` 描述
- 仅在先前记忆文件存在于 `src/agent/temp_files/<agent_id>/memory.jsonl` 时有效
- 若要重新开始，设置 `resume: false`，更改 `agent_id`，或删除 `src/agent/temp_files/<agent_id>` 目录

## 性能表现

根据项目官方数据，TuriX-CUA 在桌面自动化任务上达到了业内领先水平：

- 在内部 OSWorld 风格测试集上 **通过率 > 68%**
- 在复杂UI交互任务上，相比之前的开源智能体（如 UI-TARS），**成功率和速度都有优势**
- 集成 Qwen3-VL 后，复杂UI交互任务成功率**提升高达 15%**（内部基准测试）

![TuriX-CUA 性能对比](sources/manual_images/TuriX-CUA_image_8.jpg)

### 为什么性能更好？

1. **多模型分工**：每个模块专注自己擅长的任务，比单模型整体处理更精准
2. **专业的动作模型**：TuriX 官方训练的 `turix-actor` 模型在坐标预测上更精准
3. **技能引导**：Skills 机制提供结构化指导，减少规划错误
4. **稳定记忆管理**：可恢复压缩保证长任务不迷路

## 实测体验：国产模型接入实战

TuriX-CUA 的 `provider: "turix"` 本质上是一个 **OpenAI 兼容客户端**，这意味着我们可以接入任何支持 OpenAI 格式的 API，包括阿里云百炼（DashScope）和火山引擎方舟。我们实际测试了这两个平台，以下是完整的体验报告。

### 测试任务

```
open Chrome, go to github, and search for turix-cua in the github webpage. 
Enter the TuriX-CUA repository, and star it.
```

这是一个典型的多步骤桌面自动化任务，涉及：打开应用 → 导航网页 → 搜索 → 点击交互。

### 方案一：阿里云 DashScope（qwen3-vl-plus）

**配置（四个模块全部使用 qwen3-vl-plus）：**

```json
{
  "brain_llm": {
    "provider": "turix",
    "model_name": "qwen3-vl-plus",
    "api_key": "YOUR_DASHSCOPE_KEY",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  },
  "actor_llm": {
    "provider": "turix",
    "model_name": "qwen3-vl-plus",
    "api_key": "YOUR_DASHSCOPE_KEY",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  },
  "planner_llm": {
    "provider": "turix",
    "model_name": "qwen3-vl-plus",
    "api_key": "YOUR_DASHSCOPE_KEY",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  },
  "memory_llm": {
    "provider": "turix",
    "model_name": "qwen3-vl-plus",
    "api_key": "YOUR_DASHSCOPE_KEY",
    "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"
  }
}
```

> **踩坑提示**：早期测试中，将 Brain/Actor 设为 qwen3-vl-plus、Planner/Memory 设为 qwen3.5-plus 的混合方案曾出现视觉 API 超时的情况。全部换为 qwen3-vl-plus 后恢复正常，具体原因未确定（可能与 API 限流或网络波动有关）。

**测试结果：**

| 指标 | 结果 |
|------|------|
| 任务完成 | ✅ 成功（20步完成 Star 操作） |
| Brain 耗时范围 | **7-17 秒/步** |
| Actor 耗时范围 | **2-6 秒/步** |
| 稳定性 | ✅ 无超时，利用了 prompt cache |

**亮点：单步速度极快。** qwen3-vl-plus 的 Brain 推理仅需 7-17 秒，Actor 仅需 2-6 秒，远快于 Doubao-Seed-1.8。DashScope 还支持 prompt cache（日志中可见 `cached_tokens: 640`），进一步加速了重复请求。

**问题：坐标精度较低，导致大量重试。** 整个任务虽然完成，但经历了 20 个步骤（其中多步失败）：

- GitHub 搜索时自动加了 `owner:DemonDamon` 前缀，多次清除失败（Step 3-6）
- 搜索结果中反复点击错误的文件路径而非仓库链接（Step 7-13）
- 最终通过手动编辑 URL 将搜索类型改为 `type=repository` 才定位到正确仓库（Step 16）

**总耗时：约 5.5 分钟**（20 个循环，但单步快）

### 方案二：火山引擎方舟（Doubao-Seed-1.8）

**配置（四个模块全部使用 doubao-seed-1-8）：**

```json
{
  "brain_llm": {
    "provider": "turix",
    "model_name": "doubao-seed-1-8-251228",
    "api_key": "YOUR_VOLCENGINE_KEY",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3"
  },
  "actor_llm": {
    "provider": "turix",
    "model_name": "doubao-seed-1-8-251228",
    "api_key": "YOUR_VOLCENGINE_KEY",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3"
  },
  "planner_llm": {
    "provider": "turix",
    "model_name": "doubao-seed-1-8-251228",
    "api_key": "YOUR_VOLCENGINE_KEY",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3"
  },
  "memory_llm": {
    "provider": "turix",
    "model_name": "doubao-seed-1-8-251228",
    "api_key": "YOUR_VOLCENGINE_KEY",
    "base_url": "https://ark.cn-beijing.volces.com/api/v3"
  }
}
```

**测试结果（两轮）：**

| 指标 | 第一轮 | 第二轮 |
|------|-------|-------|
| 任务完成 | ✅ 成功（6步） | ✅ 成功（7步） |
| Brain 耗时范围 | 14-66 秒/步 | 16-75 秒/步 |
| Actor 耗时范围 | 7-22 秒/步 | 5-43 秒/步 |
| 稳定性 | ✅ 无超时 | ✅ 无超时 |

**亮点：步骤少，决策更精准。** Doubao-Seed-1.8 只用 6-7 步就完成了任务，中间仅有少量修正步骤。

**问题：单步耗时较长。** Brain 模型推理需要 16-75 秒/步，部分步骤的 reasoning_tokens 高达 1400+（深度思考模式），导致整体速度偏慢。

**第二轮详细执行日志：**

| 步骤 | 操作 | Brain | Actor | 结果 |
|------|------|-------|-------|------|
| Step 1 | 点击 Dock 上的 Chrome 图标 | 17s | 6s | ✅ 成功 |
| Step 2 | 新建标签页，输入 github.com | 16s | 17s | ✅ 成功 |
| Step 3 | 在 GitHub 搜索 turix-cua | 47s | 15s | ⚠️ 搜索范围错误（org:openclaw 前缀） |
| Step 4 | 修正搜索查询（Cmd+A 全选重输入） | 42s | 43s | ✅ 成功 |
| Step 5 | 筛选 Repositories，点击目标仓库 | 21s | 43s | ✅ 成功 |
| Step 6 | 点击进入 TuriX-CUA 仓库 | 75s | 8s | ✅ 成功 |
| Step 7 | 点击 Star 按钮 | 28s | 7s | ✅ 成功 |

**总耗时：约 6.5 分钟**（7 个循环，但单步慢）

### 对比总结

| 指标 | qwen3-vl-plus (DashScope) | Doubao-Seed-1.8 (火山) |
|------|--------------------------|----------------------|
| 任务完成 | ✅ 成功 | ✅ 成功 |
| 总步数 | 20 步（含大量重试） | 7 步（少量修正） |
| Brain 单步耗时 | **7-17s** ⚡ | 16-75s |
| Actor 单步耗时 | **2-6s** ⚡ | 5-43s |
| 总耗时 | **~5.5 分钟** | ~6.5 分钟 |
| 坐标精度 | ⚠️ 较低（多次点错链接） | ✅ 较高 |
| 推理深度 | 轻量推理，无 reasoning tokens | 深度推理（reasoning tokens 高达 1400+） |
| 特色 | 快思快动，依靠重试纠错 | 慢思精动，一步到位 |
| 推荐度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

> **结论**：两个平台总耗时相近（~5-7分钟），但思路截然不同。**qwen3-vl-plus 胜在速度**（单步快 3-5 倍），**Doubao-Seed-1.8 胜在精度**（步数少 2/3）。TuriX 官方 API 的 `turix-actor` 专门针对坐标精度优化，理论上可以兼得两者优势。

### 踩坑记录

#### 1. macOS 权限问题

首次运行会遇到多个权限弹窗，需要逐一授权：

| 权限 | 位置 | 用途 |
|------|------|------|
| **屏幕录制** | 系统设置 → 隐私与安全性 → 屏幕录制 | 截取屏幕截图 |
| **辅助功能** | 系统设置 → 隐私与安全性 → 辅助功能 | 模拟鼠标点击 |
| **输入监控** | 系统设置 → 隐私与安全性 → 输入监控 | 监听热键（强制停止） |

> ⚠️ **关键**：每次添加权限后，必须**退出并重启终端**才能生效。

#### 2. Safari JavaScript 执行权限

如果需要操作 Safari，还需要：
1. Safari → 设置 → 高级 → 启用「在菜单栏中显示"开发"菜单」
2. 开发 → 勾选「允许 Apple 事件中的 JavaScript」

#### 3. 辅助功能权限是核心

没有辅助功能权限时，TuriX 能"看"（截屏成功），但不能"动"（点击无效）。日志中会显示：

```
WARNING  [pynput.keyboard.GlobalHotKeys] This process is not trusted! 
Input event monitoring will not be possible until it is added to accessibility clients.
```

如果看到这个警告，说明终端还没有辅助功能权限。

### 为什么 CUA 这么慢？

这是 **CUA 类应用的本质特性**，每一步都需要完整的感知-决策-执行循环：

1. **截屏**：捕获当前桌面状态
2. **编码**：将截图转为 base64（Retina 屏幕下一张截图可达数 MB）
3. **上传**：发送到云端 API
4. **推理**：多模态大模型分析图像 + 生成决策
5. **返回**：接收 JSON 格式的操作指令
6. **执行**：模拟鼠标/键盘操作
7. **等待**：等待界面响应后再进入下一步

整个流程决定了 CUA 不会像普通 API 调用那么快。**每步 30-60 秒是正常水平**，复杂任务需要几分钟完成。

### 优化建议

| 策略 | 说明 | 效果 |
|------|------|------|
| 使用 TuriX 官方 API | `turix-actor` 专门针对坐标精度优化 | 更快更准 |
| 本地 Ollama 部署 | 无网络延迟，完全离线 | 需要强 GPU |
| 降低截图分辨率 | 修改源码减小图片尺寸 | 牺牲精度换速度 |
| 开启 Skills | 提供结构化指导减少试错 | 减少重复步骤 |

### 小结

经过实测，**两个国产视觉模型平台都成功完成了任务**，但风格迥异：

- ✅ **qwen3-vl-plus**：单步速度极快（Brain 7-17s），但坐标精度较低，需要多次重试（20步），像一个"手速快但容易手滑"的操作者
- ✅ **Doubao-Seed-1.8**：单步较慢（Brain 16-75s），但决策精准，步骤紧凑（7步），像一个"深思熟虑后精准操作"的操作者
- ⚠️ 两者总耗时相近（5-7分钟），CUA 的感知-决策-执行循环是核心瓶颈

**选择建议**：如果你的任务界面简单、操作目标明确，qwen3-vl-plus 的速度优势更明显；如果界面复杂、需要精准点击小元素，Doubao-Seed-1.8 的精度更可靠。追求最佳体验，建议使用 TuriX 官方 API（新用户 $20 免费额度）。如果看重隐私和离线能力，可以尝试 Ollama 本地部署。

## 快速上手指南

### 环境要求

- **macOS**：15+（Sequoia），支持完整功能
- **Windows**：切换到 `multi-agent-windows` 分支

![TuriX-CUA Windows 演示](sources/manual_images/TuriX-CUA_image_6.gif)
- **Python**：3.12 推荐
- **依赖**：详见 `requirements.txt`

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/TurixAI/TuriX-CUA.git
cd TuriX-CUA
```

#### 2. 创建 Python 环境

```bash
conda create -n turix_env python=3.12
conda activate turix_env
# requires conda >= 22.9
pip install -r requirements.txt
```

#### 3. 授权权限（macOS）

**辅助功能授权：**
```
系统设置 → 隐私与安全性 → 辅助功能
点击 +，添加 Terminal 和 Visual Studio Code（你使用的任意IDE）
如果代理仍然失败，也添加 /usr/bin/python3
```

**Safari 自动化授权：**
```
Safari → 设置 → 高级 → 启用 Show features for web developers
在新的 Develop 菜单中，启用 Allow Remote Automation
在新的 Develop 菜单中，启用 Allow JavaScript from Apple Events
```

触发权限对话框（每个 shell 运行一次）：

> **注意**：官方 README 中的 osascript 命令使用了 `\"` 转义，直接粘贴到终端会报语法错误。以下是经过实测修正的正确写法：

```bash
# 1. 先打开一个网页（Safari 必须有 document 才能执行 JavaScript）
open -a Safari https://www.apple.com

# 2. macOS Terminal 中执行（会弹出权限请求）
osascript -e 'tell application "Safari" to do JavaScript "alert('\''Triggering accessibility request'\'')" in document 1'

# 3. VS Code / Cursor 集成终端中重复执行（为对应终端授权）
osascript -e 'tell application "Safari" to do JavaScript "alert('\''Triggering accessibility request'\'')" in document 1'
```

点击所有弹窗的"允许"，这样代理才能驱动Safari。

#### 4. 配置任务

编辑 `examples/config.json`，设置你的任务：

```json
{
  "agent": {
    "task": "open system settings, switch to Dark Mode"
  }
}
```

> ⚠️ **重要提示**：任务指令的质量直接影响成功率。清晰、具体的prompt能带来更好的自动化结果。

#### 5. 配置 API

在 `examples/config.json` 中配置API密钥：

```json
"brain_llm": {
  "provider": "turix",
  "model_name": "turix-brain-model",
  "api_key": "YOUR_API_KEY",
  "base_url": "https://llm.turixapi.io/v1"
},
"actor_llm": {
  "provider": "turix",
  "model_name": "turix-actor-model",
  "api_key": "YOUR_API_KEY",
  "base_url": "https://llm.turixapi.io/v1"
},
"memory_llm": {
  "provider": "turix",
  "model_name": "turix-memory-model",
  "api_key": "YOUR_API_KEY",
  "base_url": "https://llm.turixapi.io/v1"
},
"planner_llm": {
  "provider": "turix",
  "model_name": "turix-planner-model",
  "api_key": "YOUR_API_KEY",
  "base_url": "https://llm.turixapi.io/v1"
}
```

我们强烈建议你将 `turix-actor` 模型设置为执行器。Brain 可以是你喜欢的任意 VLM，官方提供了 qwen3vl 在平台上。Gemini Pro 经测试是最聪明的，Gemini Flash 在大多数任务上都足够快速和智能。

> **注意**：README 中提到的 "Gemini-3-pro" / "Gemini-3-flash" 可能是对 Gemini 系列的简称，代码中实际使用的模型名为 `gemini-2.5-pro` 和 `gemini-2.5-flash`，请以代码中的 `build_llm()` 函数为准。

> 你可以在 [TuriX 官方网站](https://turix.ai/api-platform/) 获取API密钥，新用户有 $20 免费额度。

#### 6. 运行

```bash
python examples/main.py
```

然后就看着它工作吧！🍾

## 最佳实践与使用建议

### 1. 任务指令编写指南

**好的例子：**
```
"搜索最新的iPhone价格，创建一个Pages文档，把结果发送给联系人"
```

**不好的例子：**
```
"帮我做点事情"
```

**建议：**
- ✅ 清晰描述最终目标
- ✅ 指定具体应用名称
- ✅ 说明预期结果格式
- ✅ 分解大型任务为多个子任务

### 2. 模型选择建议

根据项目官方推荐：

| 场景 | 推荐模型 | 理由 |
|------|----------|------|
| 最高准确度 | Gemini-3-pro | 官方测试最聪明 |
| 平衡速度和质量 | Gemini-3-flash | 足够智能且更快 |
| 本地部署 | Ollama + Qwen3-VL / llama3.2-vision | 隐私保护，无API调用 |
| 默认推荐 | TuriX 官方模型 | 专门训练，点击精度更高 |

### 3. 性能优化建议

1. **开启规划功能**：对于复杂任务，设置 `agent.use_plan: true` 能大幅提升成功率
2. **启用Skills**：对于重复出现的任务场景，编写Skill手册能减少重复犯错
3. **合理上下文窗口**：通过 `skills_max_chars` 控制加载的技能总长度，避免上下文溢出
4. **使用恢复功能**：调试复杂任务时，合理利用 `resume` 功能节省token和时间

### 4. 隐私说明

项目官方明确承诺：**我们从不收集数据**。你可以完全离线使用（Ollama模式），安装后授权即可使用，数据不会离开你的电脑。

## 生态集成：MCP协议与OpenClaw

### MCP 协议集成

TuriX-CUA 原生支持 **Model Context Protocol (MCP)**，这意味着你可以：

- 让 Claude for Desktop 调用 TuriX 来执行实际桌面操作
- 通过 MCP 连接任何其他支持该协议的 AI 助手
- 实现"大脑+手脚"的分工：让大模型做推理，TuriX 做执行

**MCP 演示场景：**
> Claude 搜索AI新闻 → 调用 TuriX with MCP → TuriX 把研究结果写入Pages文档 → TuriX 发送文档给联系人

![TuriX-CUA MCP 集成演示](sources/manual_images/TuriX-CUA_image_7.gif)

### OpenClaw Skill

TuriX-CUA 已经发布了 OpenClaw Skill 到 [ClawHub](https://clawhub.ai/Tongyu-Yan/turix-cua)，让 OpenClaw 可以调用 TuriX 作为它的桌面智能体。

**本地安装：**
仓库中已经包含了预构建的 skill 包在 `OpenCLaw_TuriX_skill/` 目录：

1. 复制到你的 OpenClaw 本地 skills 文件夹：
   ```bash
   cp -r OpenCLaw_TuriX_skill ~/clawd/skills/local/turix-mac/
   ```

2. 按照 `OpenCLaw_TuriX_skill/README.md` 完成设置和权限配置

## 发展路线图

项目路线图更新到 2026 Q2：

| 季度 | 特性 | 状态 |
|------|------|------|
| 2025 Q3 | 终止与恢复支持 | ✅ 已完成 |
| 2025 Q3 | Windows 支持 | ✅ 已完成 |
| 2025 Q3 | 增强 MCP 集成 | ✅ 已完成 |
| 2025 Q4 | 新一代 AI 模型（提升点击精度） | ✅ 已完成 |
| 2025 Q4 | Windows 优化模型 | ✅ 已完成 |
| 2025 Q4 | 支持 Gemini Pro 模型 | ✅ 已完成 |
| 2025 Q4 | Planner 任务规划器 | ✅ 已完成 |
| 2025 Q4 | 多智能体架构 | ✅ 已完成 |
| 2025 Q4 | DuckDuckGo 搜索集成 | ✅ 已完成 |
| 2026 Q1 | Ollama 本地模型支持 | ✅ 已完成 |
| 2026 Q1 | 可恢复记忆压缩 | ✅ 已完成（Beta） |
| 2026 Q1 | Skills 技能机制 | ✅ 已完成 |
| 2026 Q1 | OpenClaw Skill 发布 | ✅ 已完成 |
| 2026 Q1 | 浏览器自动化 | 🔄 进行中 |
| 2026 Q1 | 持久化记忆 | 🔄 进行中 |
| 2026 Q2 | 示范学习（Learning by Demonstration） | 📋 计划中 |

## 总结与展望

TuriX-CUA 是目前开源 CUA 领域值得关注的项目。通过本文的深度解析和实测体验，我们可以得出以下结论：

**技术层面：**

- **多智能体架构是正确方向**：将 Planner/Brain/Actor/Memory 四个职责分离，让不同模型各司其职，确实比单模型承担所有任务更稳定
- **Skills 机制提供了务实的精度提升路径**：通过 markdown 手册引导执行，不需要重新训练模型就能改善特定场景的成功率
- **MCP 协议集成拓展了生态边界**：让 TuriX 能作为 Claude 等大模型的"手脚"，实现推理与执行的分工

**实测结论：**

- 国产视觉模型中，阿里 qwen3-vl-plus 和火山 Doubao-Seed-1.8 均能成功驱动 TuriX-CUA，前者单步快但精度低，后者单步慢但决策准
- CUA 的每步 30-60 秒耗时是当前技术阶段的固有特性，而非个别实现的问题
- macOS 权限配置（屏幕录制、辅助功能、输入监控）是首次运行的主要障碍

**展望：**

CUA 还处于早期阶段。当视觉模型推理速度进一步提升、本地部署门槛降低后，"用自然语言操控电脑"有望从技术演示走向日常工具。TuriX-CUA 作为开源项目，为这个方向提供了一个可运行、可扩展的起点。

> **项目地址**：[https://github.com/TurixAI/TuriX-CUA](https://github.com/TurixAI/TuriX-CUA)
> **官方网站**：[https://turix.ai](https://turix.ai)
> **Discord 社区**：[https://discord.gg/yaYrNAckb5](https://discord.gg/yaYrNAckb5)