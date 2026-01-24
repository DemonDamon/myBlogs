# 极速开发出一个高质量 Claude Agent Skills 最佳实践

原文链接: https://mp.weixin.qq.com/s/5hFHlItI3XQUWekejC_kiw
作者: 悟鸣 | 阿里云开发者 | 2026年1月16日

---

## 一、快速认识 Skill

**Skill 定义**：技能即技能，一般放在 `skills` 文件夹内，一个技能一个文件夹。

**文件结构**：
- `SKILL.md` - 主文件，包含 YAML 头和 Markdown 描述
- 相关文档、脚本、数据等资源

**SKILL.md 格式**：
```yaml
name: skill-name
description: 技能描述
```

**加载机制**：
- YAML 元信息：始终在上下文中
- Body 部分：触发时加载，需 < 5K
- 其他文件：无限制，按需加载

**支持平台**：Claude 桌面、Claude Code、API、Antigravity、Qwen Code

**OpenSkills**：开源项目，可将 Skills 安装到其他 AI Coding 工具（Cursor、Windsurf、Aider）

---

## 二、Skill VS MCP

| 维度 | Skill | MCP |
|------|-------|-----|
| **本质** | 怎么做（经验/流程封装） | 有什么工具/功能 |
| **内容** | Markdown + 脚本 | 客户端-服务端架构 |
| **加载** | 渐进式加载 | 启动时加载全部 |
| **资源** | 无需服务器 | 需要服务器 |
| **Token** | 消耗较低 | 消耗较高 |
| **复杂度** | 简单 | 复杂 |

两者是**互补关系**：Agent 通过 Skills 获取知识，通过 MCP 拓展功能。

---

## 三、快速开发 Skill 的最佳实践

### 核心思想转变
1. **默认让 AI 来写 Skill** - 不要手写
2. **把任务拆解到模型能力以内** - 描述清楚 + 提供充足上下文

### 开发流程
1. 拉取官方 Skills 仓库：`https://github.com/anthropics/skills`
2. 用 Qoder 等工具生成仓库 Wiki，快速学习
3. 准备资料：
   - 官方优质案例
   - Skill 规约
   - 仓库 Wiki
4. 清晰描述需求 + 提供所需资源
5. 让顶尖模型生成 Skill

### 实战案例：提示词优化专家 Skill

**逻辑**：
1. 用户给出原始提示词
2. 匹配最专业的提示词框架
3. 判断是否存在歧义/遗漏
4. 按最佳框架撰写专业提示词

**素材准备**：57个专业提示词框架（通过 MCP 爬取）

**优化**：先读摘要匹配框架，再针对性读详情（节省 Token）

### 其他方法
- **Skill 模板法**：将官方仓库压缩成模板，作为项目 Rule 让 AI 生成
- **官方 skill-creator**：Claude 提供的创建 Skill 的 Skill

---

## 四、Claude Skill 自身的最佳实践

### 1. 核心设计哲学
- 上下文是公共品 - 与系统提示词、对话历史共享
- 假设 Claude 聪明 - 不解释显而易见的概念
- 黄金法则：保持精简，500 行以内

### 2. 自由度控制
| 自由度 | 适用场景 | 做法 |
|--------|----------|------|
| 低 | 数据库迁移等高风险 | 精确脚本 + 严格步骤 |
| 中 | 有首选模式但可微调 | 伪代码 + 参数化脚本 |
| 高 | 代码审查、创意写作 | 大致方向 + 信任判断 |

### 3. 结构与文件组织（渐进式披露）
- 像"洋葱"一样层层剥开
- 三种模式：概览+引用、领域隔离、按需加载
- 引用层级不超过 1 层
- 路径统一使用正斜杠 `/`

### 4. 命名规范
- **Name**：动名词形式（如 `processing-pdfs`），小写字母+数字+连字符
- **Description**：第三人称写法，包含触发词，说明何时使用

### 5. 迭代开发流（用 Claude 训练 Claude）
1. Claude A（架构师）：编写优化 Skill
2. Claude B（测试员）：实战测试
3. 观察失败点，反馈修正
4. 在 Haiku/Sonnet/Opus 多模型测试

### 6. 进阶：可执行 Skills
- 代码脚本 > 纯文本指令
- Plan-Validate-Execute 模式
- 错误处理要显式具体
- MCP 工具调用使用全限定名 `ServerName:tool_name`

### 7. 避坑速查表
| - |
|---|
| - 拒绝时间敏感信息 |
| - 拒绝术语不一致 |
| - 拒绝 Windows 反斜杠路径 |
| - 必须：100+ 行参考文件加目录 |
| - 必须：发布前至少 3 个测试用例 |

---

## 五、总结

当模型足够强大时，工作方式会发生变化：
1. 把想法表达清楚
2. 把 AI 所需信息给充足

研发 Skill 时应关注：
- 逻辑是什么
- 资料准备充足

具体怎么写，交给最强大的模型完成。

---

## 参考资料

1. [OpenSkills](https://github.com/numman-ali/openskills)
2. [Anthropic Skills](https://github.com/anthropics/skills)
3. [Agent Skills 官方介绍](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
4. [Claude Code Skills 文档](https://code.claude.com/docs/en/skills)
5. [Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
