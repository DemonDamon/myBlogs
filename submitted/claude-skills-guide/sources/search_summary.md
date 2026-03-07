# Claude Agent Skills 调研摘要

## 核心资料来源

### 官方文档
1. **Anthropic官方帮助文档** - How to create custom Skills
   - https://support.claude.com/en/articles/12512198-how-to-create-custom-skills
   - 核心内容：SKILL.md文件结构、必填字段（name/description）、打包方式、测试方法、最佳实践

2. **Anthropic工程博客** - Equipping agents for the real world with Agent Skills
   - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
   - 发布时间：2025年10月16日
   - 核心内容：Skills的设计理念、渐进式披露机制、PDF Skill实例、开发评估指南

3. **官方技术文档** - Agent Skills Overview
   - https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview
   - 核心内容：三层加载架构详解、跨平台支持、API/SDK/Claude.ai使用方式、安全注意事项

4. **GitHub官方仓库** - anthropics/skills (86.1k stars)
   - https://github.com/anthropics/skills
   - 核心内容：示例Skills集合（文档、创意、技术、企业），Skills规范文件

5. **agentskills.io官方标准规范**
   - https://agentskills.io/specification
   - 核心内容：SKILL.md完整格式规范、字段约束、目录结构、验证工具

6. **Claude官方博客** - How to create Skills
   - https://claude.com/blog/how-to-create-skills-key-steps-limitations-and-examples

### 社区资料
7. **Claude CN中文社区** - 专业入门文章
   - https://claudecn.com/blog/claude-skills-professional-intro/
   - 核心内容：渐进式披露原理，SKILL.md设计，脚本化价值，团队落地方案

8. **Claude CN中文社区** - 新范式文章
   - https://claudecn.com/blog/claude-skills-new-paradigm-code-is-all-you-need/
   - 核心内容：code is all you need理念，Skills vs专用Agent，团队扩展方案

9. **heyuan110博客** - Claude Code Skills Guide
   - https://www.heyuan110.com/posts/ai/2026-02-28-claude-code-skills-guide/
   - 核心内容：Skills vs Slash Commands对比，三个可复制模板，进阶frontmatter字段

10. **80aj.com** - 生产级Skills工程化实践
    - https://www.80aj.com/2025/10/20/claude-skills实战教程（三）-生产级skills的工程化实践/

## 核心要点总结

### Skills的本质
- 一个目录 + 一个SKILL.md文件 = 一个可复用的AI能力模块
- 本质上是"程序化知识（procedural knowledge）的封装"
- 相当于给新员工写的"培训手册 + 工具箱"

### 三层加载架构（渐进式披露）
| 层级 | 何时加载 | Token成本 | 内容 |
|------|---------|---------|------|
| Level 1: 元数据 | 启动时（始终） | ~100 tokens | name + description |
| Level 2: 指令 | 触发时 | < 5000 tokens | SKILL.md正文 |
| Level 3: 资源 | 按需 | 无上限 | scripts/ references/ assets/ |

### SKILL.md结构
```yaml
---
name: skill-name        # 必填，小写字母+连字符，max 64字符
description: ...        # 必填，明确何时使用+产出什么，max 1024字符
license: Apache-2.0     # 可选
metadata:               # 可选
  author: xxx
  version: "1.0"
allowed-tools: Read, Bash  # 可选，实验性
compatibility: ...      # 可选
---

# 正文（Markdown）
```

### 跨平台支持
- Claude Code：本地文件系统，`.claude/skills/`
- Claude.ai：上传ZIP文件
- Claude API：通过API上传，workspace共享
- Agent SDK：配置`allowed_tools: ["Skill"]`
- 还支持：Cursor、GitHub Copilot等（通过agentskills.io标准）

### 预置Skills（官方提供）
- PDF - 生成和处理PDF文档
- Word (docx) - 创建/编辑Word文档
- Excel (xlsx) - 创建电子表格、数据分析
- PowerPoint (pptx) - 创建和编辑演示文稿

### 与其他机制对比
| 维度 | Skills | MCP | Slash Commands | CLAUDE.md |
|------|--------|-----|----------------|-----------|
| 本质 | 方法论/流程封装 | 外部工具连接 | 手动触发命令 | 静态上下文 |
| 触发 | 自动+手动 | 工具调用 | 手动 | 始终加载 |
| 适合 | 重复性流程 | 第三方服务 | 固定命令 | 项目全局规范 |

### 安全注意事项
- 只安装来自可信源的Skills
- Skills可能执行代码，审查bundled脚本
- 不要在SKILL.md中硬编码API密钥或密码
- 外部URL内容有prompt injection风险

## 工程10问分析

### 1. 性能问题：Skills在大规模场景下的Token效率如何优化？
渐进式披露是核心优化机制：启动时每个Skill只消耗~100 tokens（仅name+description），激活时加载<5000 tokens正文，资源文件按需加载不占Context。优化建议：SKILL.md控制在500行以内，复杂内容拆分到references/，避免把百科全书塞入SKILL.md。

### 2. 容错问题：当Skills触发不准确（误触发/漏触发）时如何处理？
描述（description）是触发路由的核心，需要：（1）包含目标任务的关键词，（2）说清何时使用和产出什么，（3）避免过于模糊。官方推荐：测试时Review Claude的thinking确认是否加载了Skill；用`/skill-name`手动触发作为fallback；iteratively优化description。

### 3. 成本问题：Skills的维护和迭代成本如何控制？
单一聚焦原则降低维护成本；Skills模块化设计避免耦合；通过Git版本控制管理Skills库；团队共享Skills减少重复工作；渐进式测试（每次只改一处）。

### 4. 边界问题：Skills和Prompt、Projects、MCP的边界如何划分？
- Skills = 怎么做（流程+验收+工具入口）
- MCP = 连到哪里（外部服务连接层）
- Projects = 背景是什么（静态项目上下文）
- Prompt = 本次做什么（单次任务指令）
- Hooks = 必须做（保证执行，不可跳过）

### 5. 集成问题：Skills如何与CI/CD和团队工作流集成？
项目级Skills放.claude/skills/可以通过Git版本控制；团队成员共享同一套Skills库；结合Hooks做自动触发；Claude API Skills可通过workspace分发给团队；Claude.ai暂时不支持org-wide管理。

### 6. 安全问题：如何防范恶意Skills和prompt injection？
只安装可信源Skills；审计所有bundled文件（包括图片和脚本）；关注外部URL调用；关键动作用allowed-tools收敛执行面；流程上"先提取事实，后执行动作"防注入；Skills不要有过宽的文件访问权限。

### 7. 维护问题：随着Skills数量增长，如何治理？
（1）定期盘点：合并重复、删除不用、补齐验收标准；（2）description设计避免重叠；（3）每个Skill标注owner；（4）可量化验收指标：触发率、命中率、输出一致性。

### 8. 竞品问题：Skills vs 传统prompt工程 vs OpenAI专属Agent？
Skills优势：可版本化、可复用、按需加载、跨平台（agentskills.io标准）；传统prompt每次都要重写，无法持久化；专用Agent需要独立训练/部署，维护成本高。Skills更接近"可复用的最佳实践包"。

### 9. 依赖问题：Scripts的依赖管理如何处理？
Claude Code：需要预安装依赖，不支持运行时安装；Claude.ai：可安装来自PyPI/npm的标准库；dependencies字段声明所需包版本；建议脚本自我检测依赖并输出友好错误信息。

### 10. 陷阱问题：开发者最常见的Skills设计错误有哪些？
（1）Skill变成"百科全书"：过于宽泛，难以触发；（2）description太模糊：触发率低；（3）没有验收标准：输出漂移；（4）全靠模型推理：确定性差；（5）入口文件太长：关键约束被淹没；（6）把Skills当Prompt用：每次任务都要创建新Skill；（7）不测试就上线：自动触发场景可能出错。
