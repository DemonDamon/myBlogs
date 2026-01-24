# DeepWiki Research - anthropics/skills

> 本文档记录了通过 DeepWiki 获取的关于 Agent Skills 的深度问答。

## Q1: 核心架构与数据流：系统的加载和执行流程是怎样的？
**A1:**
系统遵循三级渐进式披露（Progressive Disclosure）加载系统：
1. **Metadata (Always In)**：`name` 和 `description` 始终在上下文中（~100词），用于匹配和触发。
2. **SKILL.md Body (On Trigger)**：技能匹配成功后加载，包含核心指令（<5k词）。
3. **Bundled Resources (As Needed)**：脚本、参考文档按需加载或执行。脚本可以在不进入上下文的情况下执行，极大节省 Token。

## Q2: 扩展与集成机制：如何动态发现并加载新的 Skill？隔离性如何保证？
**A2:**
- **发现**：通过 `/plugin marketplace add <repo>` 注册，解析 `.claude-plugin/marketplace.json`。
- **加载**：根据 `marketplace.json` 定义的路径解析 `SKILL.md`。
- **隔离**：物理文件夹隔离 + 唯一 `name` 标识符 + 按需加载。

## Q3: 脚本执行可靠性：执行环境、超时、权限如何处理？
**A3:**
- **环境**：脚本作为可执行文件处理（0o755 权限）。
- **执行**：暗示在一个独立的宿主执行环境中运行。
- **注意**：文档中未明确给出详细的沙箱隔离和资源配额（如超时）细节，这可能是宿主程序（如 Claude Code）实现的细节。

## Q4: 性能与成本优化：如何平衡详细度与 Token？
**A4:**
- **分层加载**：三级系统最大化初始 Context 利用率。
- **精简规范**：建议 `SKILL.md` 保持在 500 行以下。
- **脚本优势**：脚本执行结果进入上下文，而脚本本身代码不必全部进入。

## Q5: 设计权衡：为什么选 Markdown 而非 JSON/YAML？
**A5:**
- **人类/AI 友好**：Markdown 表达力强，易于编写工作流指南。
- **局限性**：对结构化数据的自动化解析和严格 Schema 校验弱于 JSON。

## Q6: 与 MCP 的关系？
**A6:**
**互补关系**。Skills 定义了如何“打包和加载”专业知识和工具，而 MCP 定义了“如何调用外部服务”的技术细节。Skills 可以包含如何构建/使用 MCP 服务器的指令。

---
**源码校验备注：**
- `marketplace.json` 的结构在 `.claude-plugin/marketplace.json` 中得到证实。
- `SKILL.md` 的 Frontmatter 结构在 `template/SKILL.md` 中得到证实。
- `scripts/` 的可执行属性在 `skill-creator/SKILL.md` 的指令中被反复强调。

